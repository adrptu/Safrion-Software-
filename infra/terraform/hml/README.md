# HML: aplicada pela CI

Aplicada **pela CI, por WIF, com a `sa-infra-github`**, só pelo workflow `infra-hml.yml`, em duas fases. Ordem geral e o que nunca vai no Terraform: [README do Terraform](../README.md). Contas, papéis e rede privada: [bootstrap](../bootstrap/README.md); desenho da rede: [ADR 0006](../../../docs/adr/0006-rede-privada-hml.md).

## O que cria

| Recurso | Configuração |
|---|---|
| Artifact Registry `safrion` | Docker, southamerica-east1, tags imutáveis; apaga sem tag após 14 dias e mantém as 10 versões mais recentes |
| Cloud SQL `safrion-hml` | PostgreSQL 17, Enterprise, `db-f1-micro`, zonal, SSD de 10 GB até 20 GB; 35 backups e PITR de 7 dias em São Paulo, backups mantidos se a instância for apagada; **só IP privado** (`ipv4_enabled = false`, rede e faixa do bootstrap), sem redes autorizadas e sem ExecuteSql (`DISALLOW_DATA_API`), só conector, TLS obrigatório; proteção tripla contra exclusão; sem `root_password` |
| Segredos | `hml-db-admin-senha`, `hml-db-migrator-senha`, `hml-db-app-runtime-senha`, `hml-oidc-client-secret`, réplica em São Paulo, **sem versão**, `prevent_destroy`; versão destruída só 7 dias depois do pedido |
| `hml-vinculo-pedido` | Pedidos de vínculo, uma versão por pedido (R-006 3c). Réplica em São Paulo, sem versão, `prevent_destroy` e **sem `version_destroy_ttl`**: a versão destruída pelo job some na hora |
| `safrion-web` | Mínimo 0, máximo 2, concorrência 20, 1 vCPU, 512 MiB, CPU só na requisição; sonda de inicialização em `/saude` (18 × 10 s), sem sonda de atividade; Direct VPC egress `PRIVATE_RANGES_ONLY`; conector `ipType PRIVATE` por `SAFRION_CLOUDSQL_INSTANCIA`; conta `sa-web` |
| `safrion-preparo` | 1 tarefa, sem nova tentativa, 600 s; `--ambiente hml --banco safrion_hml`; Direct VPC egress `PRIVATE_RANGES_ONLY`; conta `sa-preparo` |
| `safrion-demo-reset` | `node dist/cli/demo-reset.js --confirmar hml`, 1 tarefa, sem nova tentativa, 600 s; Direct VPC egress `PRIVATE_RANGES_ONLY`; conta `sa-demo` |
| `safrion-vinculo` | `node dist/cli/vincular-identidade.js fila --ambiente hml --banco safrion_hml`, 1 tarefa, sem nova tentativa, 600 s; Direct VPC egress `PRIVATE_RANGES_ONLY`; conta `sa-preparo`; `SAFRION_PEDIDO_SEGREDO` com o id do `hml-vinculo-pedido`, lido pela API, sem volume |

Web e jobs recebem `SAFRION_CLOUDSQL_INSTANCIA` (nome de conexão da instância), URLs do banco sem host (`postgresql://app_runtime@/safrion_hml` e `postgresql://postgres@/postgres`) e a senha por `PGPASSWORD`. Sem volume nem socket `/cloudsql`.

Acesso aos segredos (`secretAccessor` no segredo): `sa-web` → app-runtime e oidc; `sa-preparo` → admin, migrator e app-runtime; `sa-demo` → app-runtime; operador → nenhum (não conecta ao banco, ADR 0006).
No `hml-vinculo-pedido`, e só nele: operador com `secretVersionAdder` (grava, sem ler, desativar nem destruir); `sa-preparo` com o papel customizado `safrionVinculoPedido`, criado no bootstrap, só com `versions.list`, `get`, `access`, `disable` e `destroy` (revisão do Codex de `8537b81`). Sem `add`, `enable` nem `rotate`, a conta do job não grava pedido nem reativa versão desativada. Resta: ela lê pedidos ENABLED e destrói versões; o papel não isola os dois jobs que usam a `sa-preparo` nem código alterado por quem tem `run.developer`, e não amplia o poder que a conta já tem sobre o banco e os vínculos.
`sa-deploy-github`: `artifactregistry.writer` no repositório e `run.developer` na web e nos 3 jobs. Operador: `run.invoker` nos 3 jobs.
Web e jobs referem **versão fixa** de cada segredo, nunca `latest`, exceto o `hml-vinculo-pedido`, que o `safrion-vinculo` lê versão a versão pela API (exceção à F40, ADR 0004 §11).

## Fases

| Fase | Variáveis | Resultado |
|---|---|---|
| 0 | bootstrap, na sessão do dono | Rede privada: `rede_self_link`, `subrede_self_link` e `faixa_psa_nome` |
| 1 | `criar_cloud_run = false` e as 3 saídas da rede | Registro, banco, segredos vazios, IAM dos segredos e do registro |
| — | fora do Terraform | Versões dos segredos (R-006, passos 3b e 4) e, com IAP, o cliente OAuth do IAP no console |
| 2 | `criar_cloud_run = true`, `versoes_segredos` | Web, jobs e o IAM deles; IAP ou exceção pública |

Sem a fase 1 antes, a web nasceria sem as versões dos segredos e a revisão não subiria. Sem a fase 0 antes, a instância nasceria sem a faixa, que depois não se atribui mais.

## Na CI

Workflow [`infra-hml.yml`](../../../.github/workflows/infra-hml.yml): **só o plan da fase 1**, disparado à mão na `main`, no environment `hml-infra`, sem apply (o portão da aplicação vem à parte). Em PR, só as checagens estáticas do `infra.yml`, sem credencial. O `publicar-hml.yml` não consegue a `sa-infra-github` (vínculos do WIF no bootstrap). Como disparar, o que o workflow recusa e o recibo: [tools/hml](../../../tools/hml/README.md).

A configuração não vem de variáveis do GitHub. É um JSON privado, `config/hml.tfvars.json` no bucket do state da HML, gravado uma vez pelo `cloudshell.sh config-hml` ([bootstrap](../bootstrap/README.md#como-aplicar)) e conferido pelo mesmo `validar_config` do workflow. As entradas do disparo são só a geração e o SHA-256 desse arquivo. No log, só contagens e hashes; endereços, membros e valores ficam no plano privado (ENG-062), que se aprova pelo hash (ENG-063).

Chaves da configuração, com o nome das variáveis do módulo: `projeto_id`, `projeto_numero`, `operador`, `rede_self_link`, `subrede_self_link`, `faixa_psa_nome` e `criar_cloud_run` na fase 1; `versoes_segredos`, `oidc_client_id` e, se usados, `iap_permitidos`, `url_controlada` e `origem` na fase 2, que o workflow ainda recusa. Nenhuma é segredo. `iap_permitidos` só aceita `group:` e `serviceAccount:`: os testadores entram no grupo Google, gerido pelo Adrianus fora do Terraform, e nenhum e-mail de testador vai para o plan, o state ou o log. O `operador` fica no JSON privado, no plan e no state, fora do Git e do log.

## URL controlada

- **`iap` (padrão):** IAP ligado no serviço; `run.invoker` só para o agente de serviço do IAP; `roles/iap.httpsResourceAccessor` para cada item de `iap_permitidos`: o grupo dos testadores e a conta que o pipeline usa no teste de `/saude`. Entrar e sair do teste é mudar o grupo, sem apply.
- **`publico`:** `allUsers` com `run.invoker` só na web. Só com a exceção ENG-005 aprovada (escopo, risco, compensação e vencimento no R-006).

## Rotação de segredo

Na HML, a versão do segredo é só do Terraform. O passo 3 do R-006 (linha Segredos) vira apply, sem `gcloud --update-secrets`: se a publicação trocasse a versão, o apply seguinte voltaria à antiga, já recusada pelo banco.

1. Gravar a nova versão por stdin.
2. Atualizar `versoes_segredos` na configuração da fase 2 (o `infra-hml.yml` ainda só planeja a fase 1), gerar o plan e aprová-lo pelo hash. Conferir no plan que só mudam as referências de versão de web e jobs.
3. Trocar a senha no banco e aplicar o plan aprovado logo em seguida. Entre os dois, conexões novas falham. **A definir:** com o banco só em IP privado, o notebook não alcança mais o banco; trocar as senhas de `migrator` e `app_runtime` pede subcomando num job (R-006, `894ef4d`, seção 4, "Rotação"). Até lá, não há rotação na HML.
4. Validar **sem destruir nada**: `/saude` e o login confirmam a credencial `app_runtime`, a mesma do `demo-reset`; `gcloud run jobs describe` confirma a versão fixada nos 3 jobs. **Não executar `safrion-demo-reset`** para validar (o reset troca a geração e derruba os vínculos reais), nem o `safrion-preparo` sem migração pendente. Conferir a credencial do admin também fica para o job (a definir).
5. Desativar a versão antiga.
6. Destruir só depois de 7 dias e de um teste de recuperação, com confirmação do Adrianus, que faz a destruição. O `version_destroy_ttl` ainda segura a versão por 7 dias depois do pedido.

## Achados do scanner

Trivy 0.74, com os checks embutidos, sobre `41dd295`: 2 achados HIGH, os dois em `google_sql_database_instance.hml` (`hml/banco.tf`). Com a rede privada (ADR 0006), na revisão de `eb90a5f` pelo Codex (`review-eb90a5f/infra/parecer.json`): só o GCP-0015; o GCP-0017 não aparece. A regra do `SECURITY.md` é que alta ou crítica bloqueia e que a exceção só vale por não aplicabilidade comprovada, com prova e até 90 dias. **Até haver aprovação da exceção do GCP-0015, o gate continua vermelho.**

| Achado | Situação | Proposta |
|---|---|---|
| **GCP-0017** ("public internet address") | **Fechado pelo desenho** ([ADR 0006](../../../docs/adr/0006-rede-privada-hml.md), proposta): `ipv4_enabled = false` literal e nenhuma rede autorizada. O check só acusa IP ligado ou rede autorizada pública, e o Trivy lê `ipv4_enabled` ausente ou não resolvido como `true`. Confirmado pelo Trivy 0.74 do Codex na revisão de `eb90a5f` | Nenhuma exceção |
| **GCP-0015** ("does not require TLS") | **Exceção ativa** em `.trivyignore.yaml`, referenciada no passo do Trivy do `ci.yml`. **Não aplicável:** `ssl_mode = "ENCRYPTED_ONLY"` recusa conexão sem TLS. O Trivy 0.74, com checks embutidos, acusa GCP-0015 com `ENCRYPTED_ONLY`, e nas fixtures só o `require_ssl` legado silenciou o achado. Não se demonstrou que o check desconhece todo `ssl_mode`. Contraprova do Codex: `candidate-41dd295/evidence/tls-counterexamples`; issue aquasecurity/trivy#9999 | Exceção em `.trivyignore.yaml` (raiz), só para `infra/terraform/hml/banco.tf` (caminho a partir da raiz, onde o Trivy roda `fs`; `hml/banco.tf` não casa, ensaio do Codex de 29/09 em `ci/excecao-review`), **até 28/10/2026** (30 dias). **Limite:** a exceção vale por regra e arquivo, não por recurso nem por `ssl_mode`: cobre também TLS inseguro ou uma segunda instância no mesmo arquivo. Por isso só se ativa junto do `checar_travas.py` obrigatório na CI (`infra.yml`), que recusa as duas coisas, e com o `.trivyignore.yaml` referenciado explicitamente no passo do Trivy. Motivo do prazo: reavaliar na próxima atualização do Trivy, depois da quarentena de 7 dias, e o estado da #9999. Não trocar pelo `require_ssl` legado só para calar o scanner |
| GCP-0076 (MEDIUM), GCP-0029 e GCP-0075 (LOW) | Na rede do bootstrap (`bootstrap/rede.tf`): flow logs da sub-rede e da VPC, desligados porque custam; o GCP-0075 deve fechar com `private_ip_google_access = true` | Abaixo do gate `HIGH,CRITICAL`: não bloqueiam e não pedem exceção |

A concessão de vínculo em HML passa pelo job `safrion-vinculo` (R-006 3c); o fluxo do operador está no [OPERACAO.md](../../../docs/OPERACAO.md).

**Travas verificáveis** (valem para a exceção do GCP-0015 e para o fechamento do GCP-0017):
- `python3 checar_travas.py [módulo]` lê o HCL com analisador léxico: comentários `#`, `//` e `/* */` e strings com `${}` não contam como trava.
  - Exige exatamente uma `google_sql_database_instance`, a `hml`, em `banco.tf`, sem segunda instância no módulo nem no arquivo.
  - Exige `settings` e `ip_configuration` uma vez cada; `ssl_mode` e `connector_enforcement` como texto literal; nenhuma `authorized_networks`, nem `dynamic`; nenhum `ignore_changes` que cubra uma trava.
  - Rede privada (ADR 0006): `ipv4_enabled = false` como booleano literal; `private_network` como referência (`var.x`, `local.x` ou atributo), nunca vazio nem `null`; `data_api_access` ausente ou `"DISALLOW_DATA_API"` literal; nenhum `psc_config` (Private Service Connect abriria a instância a outro projeto); `enable_private_path_for_google_cloud_services` ausente ou `false` literal.
  - Em todo `google_cloud_run_v2_service` e `google_cloud_run_v2_job` do módulo: um `vpc_access` com `egress = "PRIVATE_RANGES_ONLY"` literal e uma `network_interfaces`, sem `connector`; só `dynamic "env"`; nenhum `ignore_changes` sobre o `vpc_access` ou um bloco que o contenha. De `google_cloud_run*`, só esses dois tipos e o IAM deles.
  - Pedido de vínculo (R-006 3c): exatamente um `google_secret_manager_secret` com `secret_id = "hml-vinculo-pedido"` literal, sem `count` nem `for_each`, sem `version_destroy_ttl` e sem `ignore_changes` que o cubra. O nome em nenhuma outra string do módulo; `SAFRION_PEDIDO_SEGREDO` declarado uma vez, como `<esse recurso>.id`; o IAM do pedido com `secret_id` = `<esse recurso>.secret_id` e exatamente dois vínculos `_iam_member` explícitos (operador com `secretVersionAdder`; `sa-preparo` com `safrionVinculoPedido`), sem `count`, `for_each`, `_iam_binding` ou `_iam_policy`.
  - IAM (revisão do Codex de `7d71682`; o guard **falha fechado fora das formas que reconhece**, não entende IAM em geral):
    - no hml, todo IAM de segredo é `_iam_member` com `secret_id` numa de duas formas (`google_secret_manager_secret.hml[each.value.segredo].secret_id`, com `secretAccessor`, ou o recurso do pedido); alias em `local`, parênteses ou outra expressão falham. Nenhum IAM de projeto, pasta ou organização no hml;
    - no bootstrap, o papel `safrionVinculoPedido` com as 5 permissões exatas e nenhuma referência a ele (lida por tokens, então comentário não esconde). Secret Manager só em permissões de papel customizado e no nome da API; `roles/owner` e `roles/editor` em nenhum lugar. IAM de projeto só como `google_project_iam_member`, com papel literal, `each.value` de um local só com papéis literais (referência apenas como condição) ou outro papel customizado sem `secretmanager.versions.*`. O `wif.tf`, fora do analisador, só passa sem nenhum desses assuntos no texto;
    - nos dois módulos, a lista [Nunca no Terraform](../README.md#nunca-no-terraform) (E05): `resource` ou `data` de `google_secret_manager_secret_version`, `google_sql_user`, `google_service_account_key`, `google_project` (tipo exato), `google_iap_brand`, `google_iap_client`, `google_billing_*` ou `google_iam_oauth_client*`; atributo `root_password*` em qualquer bloco; e nenhum bloco `module`, cujos recursos o guard não lê. No `wif.tf`, fora do analisador, a mesma lista vale pelo texto, comentário incluído;
    - `checar_travas.py` sem argumento confere os dois módulos.
  - **Não coberto** (fica para a revisão e para o ensaio): IAM feito fora deste Terraform (console, gcloud, outro state); personificação da `sa-preparo` (`serviceAccountTokenCreator`, `actAs`); papéis predefinidos cujo nome não diz Secret Manager e que tragam acesso a versões; condições e políticas de negação; e o IAM efetivo no GCP. Sem isso, uma isca com `count = 0` passava, com o segredo real num `for_each` com TTL. Nome ou chave montados por função (`join`, `format`) não são reconhecidos: ficam para a revisão do diff, e o plan confere o TTL de todo segredo resolvido como `hml-vinculo-pedido`.
- `checar_travas.py --plano <plan.json>` faz o mesmo no plan resolvido e **recusa valor desconhecido** (`after_unknown`). Lista "Nunca no Terraform": todo recurso ou fonte de dados que fica no plan (after não nulo) com um desses tipos, recurso dentro de módulo e `root_password*` presente ou desconhecido, sem imprimir o valor; item ou lista fora do formato também falha. Travas: `ipv4_enabled` `false`, `private_network` não vazio, `data_api_access` nulo ou `DISALLOW_DATA_API`, `psc_config` vazio ou com `psc_enabled = false`, `enable_private_path_for_google_cloud_services` nulo ou `false` e, em web e jobs, `egress` `PRIVATE_RANGES_ONLY` com uma `network_interfaces`; todo segredo resolvido como `hml-vinculo-pedido`, inclusive por `for_each`, com `version_destroy_ttl` nulo e conhecido. Outro `google_cloud_run*` (v1, worker pool) no plan também falha, como no código. Por isso o `data_api_access` fica explícito no `banco.tf`: o provider calcula o campo, e sem valor no código ele sairia desconhecido no plan de criação.
- **Subconjunto explícito, falha fechado (HML-TF-04):** nada de arquivo de override, `.tf.json` ou `.tofu`; nenhum heredoc; dentro de `${...}`, só referência, índice e chamada simples, sem aspas, chaves, comentário nem quebra de linha; nenhuma diretiva `%{`, e `$${` e `%%{` são texto; rótulos só com `[A-Za-z0-9_-]`, sem escape `\u`; blocos de topo só `terraform`, `provider`, `resource`, `variable`, `locals` e `output`; nenhum `dynamic` na instância do Cloud SQL. Não se tenta entender todo o HCL: fora disso, o guard falha, porque leria a string ou o heredoc num lugar diferente do Terraform.
- Regressões em `test_checar_travas.py`: 108 testes, com positivo e negativo de cada trava da rede privada, os rótulos escapados do HML-TF-04 e o subconjunto; com as três contraprovas do Codex (trava em `/* */`, segunda instância no mesmo arquivo, rede desconhecida no plan), os casos achados na revisão do autor (índice legado `settings.0.…` no `ignore_changes`, arquivo de override, `.tf.json`, fonte de dados no plan), os da revisão de 28/09 (heredoc `<<EOT-X`, escape `$${`, aspas dentro de `${}`, `psc_config`, Cloud Run v1 e worker pool no plan) e os do pedido de vínculo (TTL, `ignore_changes`, nome não literal ou repetido, `for_each` no plan, egress do `safrion-vinculo` e, da revisão de 28/09, a isca com `count = 0` ou `for_each` vazio, o nome em outra string e o job ou o IAM fora do recurso literal).
  - Rodar com `python3 -m unittest discover -s infra/terraform -p 'test_*.py'`.
  - Proposta ao CI estático: rodar essas regressões e o `checar_travas.py`.

## A conferir no 1º plan e na 1ª publicação

- Se `run.developer` basta para a `sa-deploy-github` trocar só a imagem de web e jobs que já declaram segredos (a página de segredos do Cloud Run cita `run.admin`).
- Se a publicação pelo `gcloud` deixa outras diferenças além de imagem, `client` e `client_version` (anotações, rótulos, nome da revisão). Só então ampliar o `ignore_changes`.
- `SAFRION_VERSAO` e `SAFRION_COMMIT` entram na imagem por build-arg, nunca como variável da revisão: o apply seguinte a apagaria.
- Se o IAP aceita `group:` de grupo Google sem organização.
- Se o provider 8.3.0 aceita `retain_backups_on_delete` e `version_destroy_ttl`. O `validate` do Codex passou com o 8.4.0, que não cumpre a quarentena; falta repetir com o 8.3.0 e o lock dele.
- Se a `sa-infra-github` cria a instância com `private_network` de uma rede do bootstrap, e se a `sa-deploy-github` (`run.developer`) publica com `vpc_access`: a doc do Direct VPC só lista as permissões do agente de serviço.
- Se o Cloud Run aceita e devolve `network` e `subnetwork` na forma `projects/…` sem diferença permanente no 2º plan.
- O Direct VPC em southamerica-east1 (não há lista positiva de regiões) e o tempo real da 1ª conexão na subida, contra os 3 min da sonda.
- Antes da 1ª subida, um ensaio numa instância descartável, sem dado real, do conector `PRIVATE` com o Direct VPC (R-006).
- Se a identidade do teste de `/saude` passa pelo IAP e com qual audiência.
- No ensaio do `safrion-vinculo`: a `sa-preparo`, só com o `safrionVinculoPedido`, lista, lê, desativa e destrói versões do `hml-vinculo-pedido` pela API REST com o token do servidor de metadados, e o operador grava versão e executa o job só com `secretVersionAdder` e `run.invoker`.
