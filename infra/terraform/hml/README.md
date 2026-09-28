# HML: aplicada pela CI

Aplicada **pela CI, por WIF, com a `sa-infra-github`**, só pelo workflow `infra-hml.yml`, em duas fases. Ordem geral e o que nunca vai no Terraform: [README do Terraform](../README.md). Contas e papéis no projeto: [bootstrap](../bootstrap/README.md).

## O que cria

| Recurso | Configuração |
|---|---|
| Artifact Registry `safrion` | Docker, southamerica-east1, tags imutáveis; apaga sem tag após 14 dias e mantém as 10 versões mais recentes |
| Cloud SQL `safrion-hml` | PostgreSQL 17, Enterprise, `db-f1-micro`, zonal, SSD de 10 GB até 20 GB; 35 backups e PITR de 7 dias em São Paulo, backups mantidos se a instância for apagada; IP público sem redes autorizadas, só conector, TLS obrigatório; proteção tripla contra exclusão; sem `root_password` |
| Segredos | `hml-db-admin-senha`, `hml-db-migrator-senha`, `hml-db-app-runtime-senha`, `hml-oidc-client-secret`, réplica em São Paulo, **sem versão**, `prevent_destroy`; versão destruída só 7 dias depois do pedido |
| `safrion-web` | Mínimo 0, máximo 2, concorrência 20, 1 vCPU, 512 MiB, CPU só na requisição; sonda de inicialização em `/saude`, sem sonda de atividade; socket `/cloudsql`; conta `sa-web` |
| `safrion-preparo` | 1 tarefa, sem nova tentativa, 600 s; `--ambiente hml --banco safrion_hml`; conta `sa-preparo` |
| `safrion-demo-reset` | `node dist/cli/demo-reset.js --confirmar hml`, 1 tarefa, sem nova tentativa, 600 s; conta `sa-demo` |

Acesso aos segredos (`secretAccessor` no segredo): `sa-web` → app-runtime e oidc; `sa-preparo` → admin, migrator e app-runtime; `sa-demo` → app-runtime; operador → só admin.
`sa-deploy-github`: `artifactregistry.writer` no repositório e `run.developer` na web e nos 2 jobs. Operador: `run.invoker` nos 2 jobs.
Web e jobs referem **versão fixa** de cada segredo, nunca `latest`.

## Fases

| Fase | Variáveis | Resultado |
|---|---|---|
| 1 | `criar_cloud_run = false` | Registro, banco, segredos vazios, IAM dos segredos e do registro |
| — | fora do Terraform | Versões dos segredos (R-006, passos 3b e 4) e, com IAP, o cliente OAuth do IAP no console |
| 2 | `criar_cloud_run = true`, `versoes_segredos` | Web, jobs e o IAM deles; IAP ou exceção pública |

Sem a fase 1 antes, a web nasceria sem as versões dos segredos e a revisão não subiria.

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

Variáveis: `TF_VAR_projeto_id`, `TF_VAR_projeto_numero`, `TF_VAR_operador`, `TF_VAR_oidc_client_id`, `TF_VAR_criar_cloud_run`, `TF_VAR_versoes_segredos` e, se usados, `TF_VAR_iap_permitidos`, `TF_VAR_url_controlada` e `TF_VAR_origem`. Nenhuma é segredo. `iap_permitidos` só aceita `group:` e `serviceAccount:`: os testadores entram no grupo Google, gerido pelo Adrianus fora do Terraform, e nenhum e-mail de testador vai para o plan, o state ou o log. O `operador` fica no plan e no state, fora do Git e do log.

## URL controlada

- **`iap` (padrão):** IAP ligado no serviço; `run.invoker` só para o agente de serviço do IAP; `roles/iap.httpsResourceAccessor` para cada item de `iap_permitidos`: o grupo dos testadores e a conta que o pipeline usa no teste de `/saude`. Entrar e sair do teste é mudar o grupo, sem apply.
- **`publico`:** `allUsers` com `run.invoker` só na web. Só com a exceção ENG-005 aprovada (escopo, risco, compensação e vencimento no R-006).

## Rotação de segredo

Na HML, a versão do segredo é só do Terraform. O passo 3 do R-006 (linha Segredos) vira apply, sem `gcloud --update-secrets`: se a publicação trocasse a versão, o apply seguinte voltaria à antiga, já recusada pelo banco.

1. Gravar a nova versão por stdin.
2. Atualizar `TF_VAR_versoes_segredos` no environment `hml-infra` (o do `infra-hml.yml`), gerar o plan e aprová-lo pelo hash. Conferir no plan que só mudam as referências de versão de web e jobs.
3. Trocar a senha no banco e aplicar o plan aprovado logo em seguida. Entre os dois, conexões novas falham.
4. Validar **sem destruir nada**: `/saude` e o login confirmam a credencial `app_runtime`, a mesma do `demo-reset`; `gcloud run jobs describe` confirma a versão fixada nos 2 jobs. **Não executar `safrion-demo-reset`** para validar (o reset troca a geração e derruba os vínculos reais), nem o `safrion-preparo` sem migração pendente. A credencial do admin, o operador confere pelo Auth Proxy.
5. Desativar a versão antiga.
6. Destruir só depois de 7 dias e de um teste de recuperação, com confirmação do Adrianus, que faz a destruição. O `version_destroy_ttl` ainda segura a versão por 7 dias depois do pedido.

## Achados do scanner: decisão proposta (ainda não aprovada)

Trivy 0.74, com os checks embutidos, sobre `41dd295`: 2 achados HIGH, os dois em `google_sql_database_instance.hml` (`hml/banco.tf`). A regra do `SECURITY.md` é que alta ou crítica bloqueia e que a exceção só vale por não aplicabilidade comprovada, com prova e até 90 dias. **Até haver aprovação, o gate continua vermelho.**

| Achado | Leitura | Proposta |
|---|---|---|
| **GCP-0015** ("does not require TLS") | **Não aplicável:** `ssl_mode = "ENCRYPTED_ONLY"` recusa conexão sem TLS. O Trivy 0.74, com checks embutidos, acusa GCP-0015 com `ENCRYPTED_ONLY`, e nas fixtures só o `require_ssl` legado silenciou o achado. Não se demonstrou que o check desconhece todo `ssl_mode`. Contraprova do Codex: `candidate-41dd295/evidence/tls-counterexamples`; issue aquasecurity/trivy#9999 | Exceção em `excecoes-trivy.proposta.yaml`, só para `hml/banco.tf`, **até 28/10/2026** (30 dias). Motivo do prazo: reavaliar na próxima atualização do Trivy, depois da quarentena de 7 dias, e o estado da #9999. Não trocar pelo `require_ssl` legado só para calar o scanner |
| **GCP-0017** ("public internet address") | **Risco real, mitigado**, e não falta de aplicabilidade: o IP existe. A mitigação é nenhuma rede autorizada, `connector_enforcement = "REQUIRED"` (só Auth Proxy ou conector, com IAM) e TLS obrigatório | **Não entra no arquivo de exceção:** o `SECURITY.md` não admite. Pede uma decisão à parte (abaixo) |

**GCP-0017: opções para o time decidir**
1. **IP privado** (Private Service Access e Direct VPC egress na web e nos jobs), com a concessão de vínculo passando para um job `safrion-vinculo` sem overrides: o pedido entra por uma versão de uso único de segredo, **sem bastion nem VPN**. Fecha o GCP-0017, com custo incremental de US$ 0,00 a 0,11 por mês. Pede mudanças de Terraform, código (conector com `ipType PRIVATE`, modo arquivo no CLI) e emenda à ADR 0004 §11. Comparação completa, com fontes, no R-006 (`docs/hml-custo-infra` `894ef4d`, seção "GCP-0017: IP privado × concessão fora da máquina do operador").
2. **Categoria nova de aceite de risco mitigado no `SECURITY.md`**, com as travas verificadas por guard na CI, prazo curto (até 30 dias, renovável com nova revisão), escopo por recurso e aprovação ENG-005 registrada. Muda uma política de segurança, então não é decisão só de agente.
3. **Manter bloqueado**: o Terraform fica fora do `main` até 1 ou 2.

**Recomendação do autor (revista depois da comparação pedida pelo Codex):** a opção 1, que tira o risco em vez de aceitá-lo. A decisão é do time.

**Travas verificáveis** (valem para a exceção do GCP-0015 e para qualquer decisão sobre o GCP-0017):
- `python3 checar_travas.py [módulo]` lê o HCL com analisador léxico: comentários `#`, `//` e `/* */`, strings com `${}` e heredocs não contam como trava.
  - Exige exatamente uma `google_sql_database_instance`, a `hml`, em `banco.tf`, sem segunda instância no módulo nem no arquivo.
  - Exige `settings` e `ip_configuration` uma vez cada; `ssl_mode` e `connector_enforcement` como texto literal; nenhuma `authorized_networks`, nem `dynamic`; nenhum `ignore_changes` que cubra uma trava.
- `checar_travas.py --plano <plan.json>` faz o mesmo no plan resolvido e **recusa valor desconhecido** (`after_unknown`).
- **Subconjunto explícito, falha fechado (HML-TF-04):** nada de arquivo de override, `.tf.json` ou `.tofu`; rótulos só com `[A-Za-z0-9_-]`, sem escape `\u`; blocos de topo só `terraform`, `provider`, `resource`, `variable`, `locals` e `output`; nenhum `dynamic` na instância do Cloud SQL. Não se tenta entender todo o HCL.
- Regressões em `test_checar_travas.py`: 23 testes, incluindo os rótulos escapados do HML-TF-04 e o subconjunto; com as três contraprovas do Codex (trava em `/* */`, segunda instância no mesmo arquivo, rede desconhecida no plan) e os casos achados na revisão do autor (índice legado `settings.0.…` no `ignore_changes`, arquivo de override, `.tf.json`, fonte de dados no plan).
  - Rodar com `python3 -m unittest discover -s infra/terraform -p 'test_*.py'`.
  - Proposta ao CI estático: rodar essas regressões e o `checar_travas.py`.

## A conferir no 1º plan e na 1ª publicação

- Se `run.developer` basta para a `sa-deploy-github` trocar só a imagem de web e jobs que já declaram segredos (a página de segredos do Cloud Run cita `run.admin`).
- Se a publicação pelo `gcloud` deixa outras diferenças além de imagem, `client` e `client_version` (anotações, rótulos, nome da revisão). Só então ampliar o `ignore_changes`.
- `SAFRION_VERSAO` e `SAFRION_COMMIT` entram na imagem por build-arg, nunca como variável da revisão: o apply seguinte a apagaria.
- Se o IAP aceita `group:` de grupo Google sem organização.
- Se o provider 8.3.0 aceita `retain_backups_on_delete` e `version_destroy_ttl`. O `validate` do Codex passou com o 8.4.0, que não cumpre a quarentena; falta repetir com o 8.3.0 e o lock dele.
- Se o socket `/cloudsql` do Cloud Run conecta com `connector_enforcement = "REQUIRED"`.
- Se a identidade do teste de `/saude` passa pelo IAP e com qual audiência.
