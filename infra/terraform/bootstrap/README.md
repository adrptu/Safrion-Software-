# Bootstrap da HML

Aplicado **uma vez, localmente**, pelo Codex, na janela da sessão do dono (R-006 §3). Ordem geral e o que nunca vai no Terraform: [README do Terraform](../README.md).

## O que cria

- APIs: run, sqladmin, artifactregistry, secretmanager, iam, iamcredentials, sts, cloudresourcemanager, serviceusage, storage e, com `habilitar_iap`, iap. Nunca desligadas pelo Terraform.
- Bucket `<projeto>-tfstate-hml` em southamerica-east1: versionado (a versão atual e as 10 anteriores), acesso uniforme, prevenção de acesso público, `prevent_destroy`.
- WIF: pool `github-hml` e provider `github-oidc`, só para `publicar-hml.yml` no environment `hml` e `infra-hml.yml` no environment `hml-infra`, na `main`, por `push` ou `workflow_dispatch`. Ambos com `prevent_destroy`. O atributo `fluxo` (`publicar` ou `infra`) sai do `workflow_ref` e prende cada conta ao seu workflow.
- Papel customizado `safrionInfraSegredos`: cria segredos, lê os metadados, atualiza e dá IAM, sem ler, gravar ou destruir versão. **Não isola o valor:** `setIamPolicy` e `run.admin` com `actAs` dão acesso indireto (R-006).
- Contas sem chave: `sa-web`, `sa-preparo`, `sa-demo`, `sa-deploy-github`, `sa-infra-github`, `sa-agentes-leitura` e, com `criar_sa_vertex`, `sa-vertex`.

| Conta | Papéis |
|---|---|
| `sa-web`, `sa-preparo`, `sa-demo` | `cloudsql.client` no projeto; segredos no `hml/` |
| `sa-deploy-github` | WIF só do `publicar-hml.yml`; `serviceAccountUser` nas 3 de runtime; o resto no `hml/` |
| `sa-infra-github` | WIF só do `infra-hml.yml`; `serviceAccountUser` nas 3 de runtime; `artifactregistry.admin`, `cloudsql.admin`, `run.admin`, `iap.admin` e `safrionInfraSegredos` no projeto; `storage.objectAdmin` no bucket do state |
| `sa-agentes-leitura` | `run.viewer`, `cloudsql.viewer`, `logging.viewer`, `monitoring.viewer`, `artifactregistry.reader`; **sem** `secretAccessor`; `serviceAccountTokenCreator` para a conta dos agentes |
| `sa-vertex` (opcional) | `aiplatform.user`; `serviceAccountTokenCreator` para a conta dos agentes. A API aiplatform não é ligada aqui |
| operador humano | `cloudsql.client` e `logging.viewer` no projeto; segredo e jobs no `hml/` |

**Por que existe a `sa-infra-github`:** a CI aplica o `hml/` (R-006, divisão do bootstrap), e isso exige criar banco, segredos, serviços e o IAM deles. A conta não está na lista de identidades do R-006: desvio registrado no [README do Terraform](../README.md#desvios-do-r-006). A `sa-deploy-github` fica só com o mínimo da publicação, e um passo do `publicar-hml.yml` (build, dependências) não consegue a `sa-infra-github`. Nenhuma das duas recebe IAM do projeto: os papéis no projeto nascem aqui, pelo dono.

**Exceção ENG-005 proposta para os papéis admin da `sa-infra-github`** (aprovação do time com veto do Adrianus antes do 1º plan; vence antes do piloto, que terá desenho próprio):

| Papel | Por que o apply precisa | Risco | Compensação |
|---|---|---|---|
| `artifactregistry.admin` | Criar o repositório e dar `writer` à publicação | Apagar imagens | Tags imutáveis; a imagem se reconstrói do commit publicado |
| `cloudsql.admin` | Criar e configurar a instância | Desligar a proteção, apagar a instância, trocar a senha do `postgres` | Backups mantidos ao apagar (`retain_backups_on_delete`); `prevent_destroy` |
| `run.admin` | Criar web e jobs e dar IAM neles | Pôr `allUsers` na web; executar job com a `sa-preparo` e ler as senhas do banco | Só o `infra-hml.yml`, na `main`, com o Adrianus como revisor do environment; plan aprovado por hash |
| `iap.admin` | Dar acesso pelo IAP ao grupo dos testadores e à conta do teste | Abrir o IAP a outros | Mesma compensação do `run.admin` |

Todas: só pelo `infra-hml.yml`, que roda só Terraform. Scanner com achado alto sobre esses papéis aponta para esta tabela.

## Como aplicar

Pré-requisitos (R-006 §3): Terraform ≥ 1.11, TFLint e Trivy conferidos pelo checksum oficial; credencial de vida curta pelo wrapper (`GOOGLE_OAUTH_ACCESS_TOKEN`), sem gravar arquivo ADC.

```sh
cp terraform.tfvars.example terraform.tfvars   # valores reais; o arquivo fica fora do Git
terraform init
terraform fmt -check && terraform validate && tflint && trivy config .
terraform plan -out=bootstrap.tfplan
shasum -a 256 bootstrap.tfplan                 # hash e contagem vão para a rodada
terraform apply bootstrap.tfplan               # só depois da aprovação por esse hash
```

Saídas para o GitHub (environment `hml`): `WIF_PROVIDER` = `wif_provider`, `DEPLOY_SA` = `sa_deploy_github`, `GCP_PROJECT_ID` e `GCP_REGION`. O Terraform da HML usa também `sa_infra_github` e `bucket_state`.

## Depois do apply

**Conta padrão do Compute** (fora do Terraform, R-006): com as APIs ligadas, ver se `<NUM>-compute@developer.gserviceaccount.com` existe (`gcloud iam service-accounts list --project=<id>`). Se existir:
1. `gcloud projects remove-iam-policy-binding <id> --member=serviceAccount:<NUM>-compute@developer.gserviceaccount.com --role=roles/editor`;
2. `gcloud iam service-accounts disable <NUM>-compute@developer.gserviceaccount.com --project=<id>`;
3. registrar na rodada. Web e jobs declaram `service_account` explícito no `hml/`.

**Migrar o state para o bucket** (plano R-006, passo 12): acrescentar `backend "gcs" { prefix = "bootstrap" }` em `versions.tf` e rodar `terraform init -migrate-state -backend-config="bucket=<bucket_state>"`. Antes, restringir o acesso da `sa-infra-github` ao prefixo `hml/` (condição de IAM no bucket, a ensaiar), porque o `objectAdmin` dela vale para o bucket todo.

**Revogar a sessão do dono** ao fim da janela, pelo wrapper: `auth revoke --all` e `auth application-default revoke`, com a prova pedida no R-006 §3.

**Sem environment com revisor** (R-006, passo 5): nenhum dos dois caminhos autentica. Não há variante da condição sem `environment`.
