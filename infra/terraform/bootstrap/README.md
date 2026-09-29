# Bootstrap da HML

Aplicado **uma vez, localmente**, pelo Codex, na janela da sessão do dono (R-006 §3). Ordem geral e o que nunca vai no Terraform: [README do Terraform](../README.md).

## O que cria

- APIs: run, sqladmin, artifactregistry, secretmanager, iam, iamcredentials, sts, cloudresourcemanager, serviceusage, storage, compute, servicenetworking e, com `habilitar_iap`, iap. Nunca desligadas pelo Terraform.
- Rede privada da HML ([ADR 0006](../../../docs/adr/0006-rede-privada-hml.md), `rede.tf`), toda com `prevent_destroy`:
  - VPC `safrion-hml`, modo custom;
  - sub-rede `safrion-hml-run` /24 (`subrede_cidr`, padrão `10.10.0.0/24`) em southamerica-east1, para o Direct VPC egress do Cloud Run, com Private Google Access e sem flow logs;
  - faixa `safrion-hml-psa` /20 (`faixa_psa_cidr`, padrão `10.20.0.0/20`), com endereço explícito, para o IP privado do Cloud SQL;
  - conexão de Private Service Access com `deletion_policy = "PREVENT"`.

  As duas faixas são validadas: RFC 1918, alinhadas, e a do PSA sem conter a sub-rede. Sem NAT, conector VPC, regra de firewall, bastion ou VPN. Custo: nenhum pela conexão nem pelos IPs internos; só o tráfego (R-006, `894ef4d`).
- Bucket `<projeto>-tfstate-hml` em southamerica-east1: versionado (a versão atual e as 10 anteriores), acesso uniforme, prevenção de acesso público, `prevent_destroy`.
- WIF: pool `github-hml` e provider `github-oidc`, só para `publicar-hml.yml` no environment `hml` e `infra-hml.yml` no environment `hml-infra`, na `main`, por `push` ou `workflow_dispatch`. Ambos com `prevent_destroy`. O atributo `fluxo` (`publicar` ou `infra`) sai do `workflow_ref` e prende cada conta ao seu workflow.
- Papel customizado `safrionVinculoPedido` (R-006 §3c): só `secretmanager.versions.list`, `get`, `access`, `disable` e `destroy`, para o job `safrion-vinculo`. Não se vincula no projeto: o `hml/` o dá à `sa-preparo` só no segredo `hml-vinculo-pedido`, então o bootstrap vai antes do apply do `hml/` que cria esse vínculo. `checar_travas.py` confere o conjunto exato.
- Papel customizado `safrionInfraSegredos`: cria segredos, lê os metadados, atualiza e dá IAM, sem ler, gravar ou destruir versão. **Não isola o valor:** `setIamPolicy` e `run.admin` com `actAs` dão acesso indireto (R-006).
- Contas sem chave: `sa-web`, `sa-preparo`, `sa-demo`, `sa-deploy-github`, `sa-infra-github`, `sa-agentes-leitura` e, com `criar_sa_vertex`, `sa-vertex`.

| Conta | Papéis |
|---|---|
| `sa-web`, `sa-preparo`, `sa-demo` | `cloudsql.client` no projeto; segredos no `hml/` |
| `sa-deploy-github` | WIF só do `publicar-hml.yml`; `serviceAccountUser` nas 3 de runtime; o resto no `hml/` |
| `sa-infra-github` | WIF só do `infra-hml.yml`; `serviceAccountUser` nas 3 de runtime; `artifactregistry.admin`, `cloudsql.admin`, `run.admin`, `iap.admin` e `safrionInfraSegredos` no projeto; `storage.objectAdmin` no bucket do state |
| `sa-agentes-leitura` | `run.viewer`, `cloudsql.viewer`, `logging.viewer`, `monitoring.viewer`, `artifactregistry.reader`; **sem** `secretAccessor`; `serviceAccountTokenCreator` para a conta dos agentes |
| `sa-vertex` (opcional) | `aiplatform.user`; `serviceAccountTokenCreator` para a conta dos agentes. A API aiplatform não é ligada aqui |
| operador humano | `logging.viewer` no projeto; segredo e jobs no `hml/`. Sem `cloudsql.client`: sem IP público, o notebook não conecta ao banco ([ADR 0006](../../../docs/adr/0006-rede-privada-hml.md)) |

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

Pré-requisitos (R-006 §3): Terraform 1.16.3 (a versão fixada em `versions.tf`), TFLint e Trivy conferidos pelo checksum oficial; credencial de vida curta pelo wrapper (`GOOGLE_OAUTH_ACCESS_TOKEN`), sem gravar arquivo ADC.

```sh
cp terraform.tfvars.example terraform.tfvars   # valores reais; o arquivo fica fora do Git
terraform init
terraform fmt -check && terraform validate && tflint && trivy config --severity HIGH,CRITICAL --exit-code 1 .
terraform plan -out=bootstrap.tfplan
shasum -a 256 bootstrap.tfplan                 # hash e contagem vão para a rodada
terraform apply bootstrap.tfplan               # só depois da aprovação por esse hash
```

Saídas para o GitHub (environment `hml`): `WIF_PROVIDER` = `wif_provider`, `DEPLOY_SA` = `sa_deploy_github`, `GCP_PROJECT_ID` e `GCP_REGION`. O Terraform da HML usa também `sa_infra_github`, `bucket_state` e as saídas da rede (`TF_VAR_rede_self_link`, `TF_VAR_subrede_self_link` e `TF_VAR_faixa_psa_nome` no environment `hml-infra`).

**A rede vem antes da 1ª instância.** Aplicar o bootstrap com a rede antes de qualquer apply do `hml/` que crie o Cloud SQL: o IP privado não sai mais da instância, e a faixa só se atribui na criação. Ligar o IP privado numa instância existente a reinicia e não aceita faixa nomeada. Mudar `subrede_cidr` ou `faixa_psa_cidr` depois do apply recria o recurso, e o `prevent_destroy` recusa o plan.

## Depois do apply

**Conta padrão do Compute** (fora do Terraform, R-006): ligar a API do Compute cria a conta padrão, que pode receber o papel Editor. Depois do apply, ver se `<NUM>-compute@developer.gserviceaccount.com` existe (`gcloud iam service-accounts list --project=<id>`). Se existir:
1. `gcloud projects remove-iam-policy-binding <id> --member=serviceAccount:<NUM>-compute@developer.gserviceaccount.com --role=roles/editor`;
2. `gcloud iam service-accounts disable <NUM>-compute@developer.gserviceaccount.com --project=<id>`;
3. registrar na rodada. Web e jobs declaram `service_account` explícito no `hml/`.

**Rede `default`** (fora do Terraform): a doc descreve a criação dela em projeto novo, com regras de firewall que abrem SSH e RDP para `0.0.0.0/0`; não se sabe se nasce num projeto já existente, e o Trivy não a vê. Conferir com `gcloud compute networks list --project=<id>`. Se aparecer, apagar as regras dela (`gcloud compute firewall-rules list --project=<id> --filter="network~/default$"` e `gcloud compute firewall-rules delete <regra> --project=<id>`), depois a rede (`gcloud compute networks delete default --project=<id>`), e registrar na rodada.

**Migrar o state para o bucket** (plano R-006, passo 12): acrescentar `backend "gcs" { prefix = "bootstrap" }` em `versions.tf` e rodar `terraform init -migrate-state -backend-config="bucket=<bucket_state>"`. Antes, restringir o acesso da `sa-infra-github` ao prefixo `hml/` (condição de IAM no bucket, a ensaiar), porque o `objectAdmin` dela vale para o bucket todo.

**Revogar a sessão do dono** ao fim da janela, pelo wrapper: `auth revoke --all` e `auth application-default revoke`, com a prova pedida no R-006 §3.

**Sem environment com revisor** (R-006, passo 5): nenhum dos dois caminhos autentica. Não há variante da condição sem `environment`.
