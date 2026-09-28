# HML: aplicada pela CI

Aplicada **pela CI, por WIF, com a `sa-infra-github`**, só pelo workflow `infra-hml.yml`, em duas fases. Ordem geral e o que nunca vai no Terraform: [README do Terraform](../README.md). Contas, papéis e rede privada: [bootstrap](../bootstrap/README.md); desenho da rede: [ADR 0006](../../../docs/adr/0006-rede-privada-hml.md).

## O que cria

| Recurso | Configuração |
|---|---|
| Artifact Registry `safrion` | Docker, southamerica-east1, tags imutáveis; apaga sem tag após 14 dias e mantém as 10 versões mais recentes |
| Cloud SQL `safrion-hml` | PostgreSQL 17, Enterprise, `db-f1-micro`, zonal, SSD de 10 GB até 20 GB; 35 backups e PITR de 7 dias em São Paulo, backups mantidos se a instância for apagada; **só IP privado** (`ipv4_enabled = false`, rede e faixa do bootstrap), sem redes autorizadas e sem ExecuteSql (`DISALLOW_DATA_API`), só conector, TLS obrigatório; proteção tripla contra exclusão; sem `root_password` |
| Segredos | `hml-db-admin-senha`, `hml-db-migrator-senha`, `hml-db-app-runtime-senha`, `hml-oidc-client-secret`, réplica em São Paulo, **sem versão**, `prevent_destroy`; versão destruída só 7 dias depois do pedido |
| `safrion-web` | Mínimo 0, máximo 2, concorrência 20, 1 vCPU, 512 MiB, CPU só na requisição; sonda de inicialização em `/saude` (18 × 10 s), sem sonda de atividade; Direct VPC egress `PRIVATE_RANGES_ONLY`; conector `ipType PRIVATE` por `SAFRION_CLOUDSQL_INSTANCIA`; conta `sa-web` |
| `safrion-preparo` | 1 tarefa, sem nova tentativa, 600 s; `--ambiente hml --banco safrion_hml`; Direct VPC egress `PRIVATE_RANGES_ONLY`; conta `sa-preparo` |
| `safrion-demo-reset` | `node dist/cli/demo-reset.js --confirmar hml`, 1 tarefa, sem nova tentativa, 600 s; Direct VPC egress `PRIVATE_RANGES_ONLY`; conta `sa-demo` |

Web e jobs recebem `SAFRION_CLOUDSQL_INSTANCIA` (nome de conexão da instância), URLs do banco sem host (`postgresql://app_runtime@/safrion_hml` e `postgresql://postgres@/postgres`) e a senha por `PGPASSWORD`. Sem volume nem socket `/cloudsql`.

Acesso aos segredos (`secretAccessor` no segredo): `sa-web` → app-runtime e oidc; `sa-preparo` → admin, migrator e app-runtime; `sa-demo` → app-runtime; operador → só admin.
`sa-deploy-github`: `artifactregistry.writer` no repositório e `run.developer` na web e nos 2 jobs. Operador: `run.invoker` nos 2 jobs.
Web e jobs referem **versão fixa** de cada segredo, nunca `latest`.

## Fases

| Fase | Variáveis | Resultado |
|---|---|---|
| 0 | bootstrap, na sessão do dono | Rede privada: `rede_self_link`, `subrede_self_link` e `faixa_psa_nome` |
| 1 | `criar_cloud_run = false` e as 3 saídas da rede | Registro, banco, segredos vazios, IAM dos segredos e do registro |
| — | fora do Terraform | Versões dos segredos (R-006, passos 3b e 4) e, com IAP, o cliente OAuth do IAP no console |
| 2 | `criar_cloud_run = true`, `versoes_segredos` | Web, jobs e o IAM deles; IAP ou exceção pública |

Sem a fase 1 antes, a web nasceria sem as versões dos segredos e a revisão não subiria. Sem a fase 0 antes, a instância nasceria sem a faixa, que depois não se atribui mais.

## Na CI

Workflow `infra-hml.yml` (a criar): só Terraform, sem `npm` nem build, na `main`, environment `hml-infra` (o Adrianus como único revisor); em PR, só checagens estáticas sem credencial. O `publicar-hml.yml` não consegue a `sa-infra-github` (vínculos do WIF no bootstrap).

```sh
echo "::add-mask::$TF_VAR_operador"                    # se um erro citar o membro, o log mascara
terraform init -backend-config="bucket=<bucket_state do bootstrap>"
terraform fmt -check && terraform validate && tflint && trivy config --severity HIGH,CRITICAL --exit-code 1 .
terraform plan -no-color -out=hml.tfplan > /dev/null   # o diff traz membros de IAM: fora do log (ENG-062)
shasum -a 256 hml.tfplan
terraform show -json hml.tfplan | jq -r '.resource_changes[] | select(.change.actions != ["no-op"]) | "\(.change.actions | join("/")) \(.address)"'
terraform apply -no-color hml.tfplan > /dev/null        # só depois da aprovação por esse hash (ENG-063)
```

No log, só o hash e a ação por endereço, sem valores.

Variáveis: `TF_VAR_projeto_id`, `TF_VAR_projeto_numero`, `TF_VAR_operador`, `TF_VAR_oidc_client_id`, `TF_VAR_rede_self_link`, `TF_VAR_subrede_self_link`, `TF_VAR_faixa_psa_nome`, `TF_VAR_criar_cloud_run`, `TF_VAR_versoes_segredos` e, se usados, `TF_VAR_iap_permitidos`, `TF_VAR_url_controlada` e `TF_VAR_origem`. Nenhuma é segredo. `iap_permitidos` só aceita `group:` e `serviceAccount:`: os testadores entram no grupo Google, gerido pelo Adrianus fora do Terraform, e nenhum e-mail de testador vai para o plan, o state ou o log. O `operador` fica no plan e no state, fora do Git e do log.

## URL controlada

- **`iap` (padrão):** IAP ligado no serviço; `run.invoker` só para o agente de serviço do IAP; `roles/iap.httpsResourceAccessor` para cada item de `iap_permitidos`: o grupo dos testadores e a conta que o pipeline usa no teste de `/saude`. Entrar e sair do teste é mudar o grupo, sem apply.
- **`publico`:** `allUsers` com `run.invoker` só na web. Só com a exceção ENG-005 aprovada (escopo, risco, compensação e vencimento no R-006).

## Rotação de segredo

Na HML, a versão do segredo é só do Terraform. O passo 3 do R-006 (linha Segredos) vira apply, sem `gcloud --update-secrets`: se a publicação trocasse a versão, o apply seguinte voltaria à antiga, já recusada pelo banco.

1. Gravar a nova versão por stdin.
2. Atualizar `TF_VAR_versoes_segredos` no environment `hml-infra` (o do `infra-hml.yml`), gerar o plan e aprová-lo pelo hash. Conferir no plan que só mudam as referências de versão de web e jobs.
3. Trocar a senha no banco e aplicar o plan aprovado logo em seguida. Entre os dois, conexões novas falham. **A definir:** com o banco só em IP privado, o notebook não alcança mais o banco; trocar as senhas de `migrator` e `app_runtime` pede subcomando num job (R-006, `894ef4d`, seção 4, "Rotação"). Até lá, não há rotação na HML.
4. Validar **sem destruir nada**: `/saude` e o login confirmam a credencial `app_runtime`, a mesma do `demo-reset`; `gcloud run jobs describe` confirma a versão fixada nos 2 jobs. **Não executar `safrion-demo-reset`** para validar (o reset troca a geração e derruba os vínculos reais), nem o `safrion-preparo` sem migração pendente. Conferir a credencial do admin também fica para o job (a definir).
5. Desativar a versão antiga.
6. Destruir só depois de 7 dias e de um teste de recuperação, com confirmação do Adrianus, que faz a destruição. O `version_destroy_ttl` ainda segura a versão por 7 dias depois do pedido.

## Achados do scanner

Trivy 0.74, com os checks embutidos, sobre `41dd295`: 2 achados HIGH, os dois em `google_sql_database_instance.hml` (`hml/banco.tf`). A regra do `SECURITY.md` é que alta ou crítica bloqueia e que a exceção só vale por não aplicabilidade comprovada, com prova e até 90 dias. **Até haver aprovação da exceção do GCP-0015, o gate continua vermelho.**

| Achado | Situação | Proposta |
|---|---|---|
| **GCP-0017** ("public internet address") | **Fechado pelo desenho** ([ADR 0006](../../../docs/adr/0006-rede-privada-hml.md), proposta): `ipv4_enabled = false` literal e nenhuma rede autorizada. O check só acusa IP ligado ou rede autorizada pública, e o Trivy lê `ipv4_enabled` ausente ou não resolvido como `true`. **A confirmar pelo Trivy do revisor** | Nenhuma exceção |
| **GCP-0015** ("does not require TLS") | **Pendente. Não aplicável:** `ssl_mode = "ENCRYPTED_ONLY"` recusa conexão sem TLS. O Trivy 0.74, com checks embutidos, acusa GCP-0015 com `ENCRYPTED_ONLY`, e nas fixtures só o `require_ssl` legado silenciou o achado. Não se demonstrou que o check desconhece todo `ssl_mode`. Contraprova do Codex: `candidate-41dd295/evidence/tls-counterexamples`; issue aquasecurity/trivy#9999 | Exceção em `excecoes-trivy.proposta.yaml`, só para `hml/banco.tf`, **até 28/10/2026** (30 dias). Motivo do prazo: reavaliar na próxima atualização do Trivy, depois da quarentena de 7 dias, e o estado da #9999. Não trocar pelo `require_ssl` legado só para calar o scanner |
| GCP-0076 (MEDIUM), GCP-0029 e GCP-0075 (LOW) | Na rede do bootstrap (`bootstrap/rede.tf`): flow logs da sub-rede e da VPC, desligados porque custam; o GCP-0075 deve fechar com `private_ip_google_access = true` | Abaixo do gate `HIGH,CRITICAL`: não bloqueiam e não pedem exceção |

A concessão de vínculo em HML, que passava pelo Auth Proxy do notebook, fica **a definir**: depende do job `safrion-vinculo` (R-006, `894ef4d`, seção 3), entrega à parte.

**Travas verificáveis** (valem para a exceção do GCP-0015 e para o fechamento do GCP-0017):
- `python3 checar_travas.py [módulo]` lê o HCL com analisador léxico: comentários `#`, `//` e `/* */` e strings com `${}` não contam como trava.
  - Exige exatamente uma `google_sql_database_instance`, a `hml`, em `banco.tf`, sem segunda instância no módulo nem no arquivo.
  - Exige `settings` e `ip_configuration` uma vez cada; `ssl_mode` e `connector_enforcement` como texto literal; nenhuma `authorized_networks`, nem `dynamic`; nenhum `ignore_changes` que cubra uma trava.
  - Rede privada (ADR 0006): `ipv4_enabled = false` como booleano literal; `private_network` como referência (`var.x`, `local.x` ou atributo), nunca vazio nem `null`; `data_api_access` ausente ou `"DISALLOW_DATA_API"` literal; nenhum `psc_config` (Private Service Connect abriria a instância a outro projeto); `enable_private_path_for_google_cloud_services` ausente ou `false` literal.
  - Em todo `google_cloud_run_v2_service` e `google_cloud_run_v2_job` do módulo: um `vpc_access` com `egress = "PRIVATE_RANGES_ONLY"` literal e uma `network_interfaces`, sem `connector`; só `dynamic "env"`; nenhum `ignore_changes` sobre o `vpc_access` ou um bloco que o contenha. De `google_cloud_run*`, só esses dois tipos e o IAM deles.
- `checar_travas.py --plano <plan.json>` faz o mesmo no plan resolvido e **recusa valor desconhecido** (`after_unknown`): `ipv4_enabled` `false`, `private_network` não vazio, `data_api_access` nulo ou `DISALLOW_DATA_API`, `psc_config` vazio ou com `psc_enabled = false`, `enable_private_path_for_google_cloud_services` nulo ou `false` e, em web e jobs, `egress` `PRIVATE_RANGES_ONLY` com uma `network_interfaces`. Outro `google_cloud_run*` (v1, worker pool) no plan também falha, como no código. Por isso o `data_api_access` fica explícito no `banco.tf`: o provider calcula o campo, e sem valor no código ele sairia desconhecido no plan de criação.
- **Subconjunto explícito, falha fechado (HML-TF-04):** nada de arquivo de override, `.tf.json` ou `.tofu`; nenhum heredoc; dentro de `${...}`, só referência, índice e chamada simples, sem aspas, chaves, comentário nem quebra de linha; nenhuma diretiva `%{`, e `$${` e `%%{` são texto; rótulos só com `[A-Za-z0-9_-]`, sem escape `\u`; blocos de topo só `terraform`, `provider`, `resource`, `variable`, `locals` e `output`; nenhum `dynamic` na instância do Cloud SQL. Não se tenta entender todo o HCL: fora disso, o guard falha, porque leria a string ou o heredoc num lugar diferente do Terraform.
- Regressões em `test_checar_travas.py`: 44 testes, com positivo e negativo de cada trava da rede privada, os rótulos escapados do HML-TF-04 e o subconjunto; com as três contraprovas do Codex (trava em `/* */`, segunda instância no mesmo arquivo, rede desconhecida no plan), os casos achados na revisão do autor (índice legado `settings.0.…` no `ignore_changes`, arquivo de override, `.tf.json`, fonte de dados no plan) e os da revisão de 28/09 (heredoc `<<EOT-X`, escape `$${`, aspas dentro de `${}`, `psc_config`, Cloud Run v1 e worker pool no plan).
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
