# Bootstrap da HML

Aplicado **uma vez, no Cloud Shell do Google**, pelo Adrianus, com o `../cloudshell.sh` e guiado pelo Codex; o Claude responde pelo plan, e as três IAs revisam pelo hash antes do apply. Nada depende de uma máquina local (ordem do proprietário, 29/09/2026). Ordem geral e o que nunca vai no Terraform: [README do Terraform](../README.md).

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
| `run.admin` | Criar web e jobs e dar IAM neles | Pôr `allUsers` na web; executar job com a `sa-preparo` e ler as senhas do banco | Só o `infra-hml.yml`, na `main`; plan aprovado por hash, com veto do Adrianus (revisor obrigatório de environment não está disponível em repositório privado no plano atual) |
| `iap.admin` | Dar acesso pelo IAP ao grupo dos testadores e à conta do teste | Abrir o IAP a outros | Mesma compensação do `run.admin` |

Todas: só pelo `infra-hml.yml`, que roda só Terraform. Scanner com achado alto sobre esses papéis aponta para esta tabela.

## State do bootstrap

O state do bootstrap fica, desde o 1º `init`, num bucket só dele: `<projeto>-tfstate-bootstrap`. O bucket nasce fora do Terraform, porque o bootstrap não pode guardar o state num bucket que ele mesmo cria, e fica sem nenhum membro direto. **Pelo código**, a `sa-infra-github` não tem papel de Storage no projeto e só tem `objectAdmin` no `<projeto>-tfstate-hml` (`contas.tf`); o `checar_travas.py` recusa papel ou permissão de Storage no projeto, outro IAM ou ACL de bucket e qualquer recurso com `tfstate-bootstrap`. **O isolamento efetivo só vale depois da conferência do passo 3**, que lê o IAM do bucket e o do projeto, porque o IAM do bucket não mostra o acesso que vem do projeto. Nenhuma cópia do state fica em máquina local, e não há migração nem condição de IAM por prefixo.

1. Criar o bucket, uma vez, na região da HML:
   ```sh
   gcloud storage buckets create gs://<projeto>-tfstate-bootstrap --project=<projeto> --location=southamerica-east1 --uniform-bucket-level-access --public-access-prevention
   gcloud storage buckets update gs://<projeto>-tfstate-bootstrap --versioning --lifecycle-file=<arquivo>
   ```
   O `<arquivo>` repete a regra do bucket da HML (`main.tf`): apagar versões arquivadas além das 11 mais novas.
2. Tirar os vínculos de conveniência de editor e leitor do projeto que existirem, para ficar só o dono. Ler a política antes (`gcloud storage buckets get-iam-policy`) e remover **só os pares presentes**: remover um vínculo ausente é erro do `gcloud`, que não se ignora. Os pares possíveis:
   ```sh
   gcloud storage buckets remove-iam-policy-binding gs://<projeto>-tfstate-bootstrap --member=projectEditor:<projeto> --role=roles/storage.legacyBucketOwner
   gcloud storage buckets remove-iam-policy-binding gs://<projeto>-tfstate-bootstrap --member=projectEditor:<projeto> --role=roles/storage.legacyObjectOwner
   gcloud storage buckets remove-iam-policy-binding gs://<projeto>-tfstate-bootstrap --member=projectViewer:<projeto> --role=roles/storage.legacyBucketReader
   gcloud storage buckets remove-iam-policy-binding gs://<projeto>-tfstate-bootstrap --member=projectViewer:<projeto> --role=roles/storage.legacyObjectReader
   ```
3. Conferir pelo servidor, e parar se algo diferir ou não puder ser lido:
   - `gcloud storage buckets describe --raw`: o bucket é deste projeto (`projectNumber`), com acesso uniforme, prevenção de acesso público `enforced` e versionamento ligado. Nome de bucket é global: o `projectNumber` se confere **antes** de qualquer mudança dos passos 1 e 2, inclusive numa retomada. Se o `describe` falhar por outro motivo que não "não existe" (permissão, rede), não criar nem mudar nada;
   - `gcloud storage buckets get-iam-policy`: só membros `projectOwner:<projeto>`;
   - `gcloud storage managed-folders list`: nenhuma pasta gerenciada, que teria IAM próprio;
   - `gcloud projects describe`: o projeto não tem pasta nem organização acima (sem `parent`). Com pai, o acesso herdado não é conferível daqui: **parar**;
   - `gcloud projects get-iam-policy`: só o dono tem `roles/owner`. Fora o dono e os agentes de serviço que o Google cria com o número deste projeto, ninguém tem papel (básico, predefinido ou customizado, expandido com `gcloud iam roles describe`) que alcance objetos (`storage.objects.*`, `storage.managedFolders.*`, `roles/storage.*`), que permita se dar acesso (`storage.buckets.setIamPolicy`, `resourcemanager.projects.setIamPolicy`, `iam.roles.update`) ou que permita agir como conta de serviço (token, assinatura, chave, `actAs`, IAM da conta ou provider do WIF; [permissões de conta de serviço](https://docs.cloud.google.com/iam/docs/service-account-permissions)). Os vínculos de personificação que o bootstrap cria ficam em cada conta, não no projeto. Os agentes pulados aparecem na tela pelo domínio, e a conferência não cobre abuso dos próprios agentes do Google. Se a conta padrão do Compute aparecer com Editor, rodar o `depois` antes.
4. `terraform init -backend-config="bucket=<projeto>-tfstate-bootstrap"`.

O `cloudshell.sh` executa e confere estes passos: `state` cria e ajusta; `planejar` e `aplicar` repetem a conferência antes de tocar no Terraform.

## Como aplicar

**Ferramentas no Cloud Shell.** Usar o Cloud Shell no modo normal, não no efêmero: o `$HOME` (cópia do repositório e `~/.safrion`) precisa sobreviver entre sessões. Antes do 1º comando, conferir `gh --version` e `python3 --version`; sem `gh`, instalar na sessão (`sudo apt-get install -y gh`), o que some quando a sessão reinicia. Terraform e TFLint não se instalam: o `cloudshell.sh` baixa as versões do `infra.yml` e confere o SHA-256.

Numa cópia limpa da `main` (`gh auth login` pelo código de dispositivo, digitado pelo próprio Adrianus; `gh repo clone adrptu/Safrion-Software-`):

```sh
infra/terraform/cloudshell.sh conferir                 # a cópia é a main atual do GitHub, com os 10 checks obrigatórios verdes
infra/terraform/cloudshell.sh state <projeto>          # bucket do state do bootstrap, conferido no servidor (seção acima)
infra/terraform/cloudshell.sh planejar <projeto>       # Terraform e TFLint pelo SHA-256 do infra.yml, travas e plan
infra/terraform/cloudshell.sh aplicar <projeto> <hash> # só depois dos pareceres pelo hash, e sem veto do Adrianus
infra/terraform/cloudshell.sh depois <projeto>         # conta padrão do Compute e rede default (seção abaixo)
infra/terraform/cloudshell.sh variaveis <projeto>      # variáveis dos environments hml e hml-infra
infra/terraform/cloudshell.sh config-hml <projeto>     # JSON privado da fase 1: imprime a geração e o SHA-256
```

O `planejar` gera o tfvars a partir do GitHub e da conta logada, sem valores digitados, e guarda tfvars, plano, `.terraform`, binários e logs em `~/.safrion/<projeto>`, fora do checkout e só para o dono. O plano anterior é apagado no início: o hash na tela é sempre o do plano que existe. Na tela ficam só o SHA-256, a contagem e os endereços, com e-mails mascarados, inclusive nos erros do `gcloud` e do `gh`: é o que vai para a rodada. `TF_VAR_*`, `TF_CLI_ARGS*` e o `~/.terraformrc` do shell não entram no Terraform, e o `conferir` recusa `*.tfvars` ignorados pelo Git nos módulos. O Trivy não roda no Cloud Shell: vale o `ci.yml` verde do mesmo commit, que o `conferir` exige. A credencial é de vida curta (`gcloud auth print-access-token`, só no ambiente do processo), sem arquivo ADC.

O `aplicar` usa uma cópia privada do plano, conferida pelo hash, com o mesmo Terraform extraído no `planejar`. **Não fechar a aba durante o `aplicar`.** Se a sessão cair no meio, o state pode ficar travado: o `planejar` ou o `aplicar` seguinte mostra o ID do lock e o comando `cloudshell.sh destravar <projeto> <ID>`, que pede `s` antes de soltar. Depois, planejar de novo e revisar o novo hash. Um comando por vez em cada projeto: um segundo comando, noutra aba, para sem mexer em nada.

Ao encerrar a janela: `cloudshell.sh limpar <projeto>` apaga os arquivos locais (o state continua no bucket), `gh auth logout --hostname github.com` e a revogação do `gcloud` (abaixo).

Saídas para o GitHub, impressas pelo `variaveis`: no environment `hml`, `WIF_PROVIDER` = `wif_provider`, `DEPLOY_SA` = `sa_deploy_github`, `GCP_PROJECT_ID` e `GCP_REGION`; no `hml-infra`, `HML_PROJECT_NUMBER`. As saídas da rede e o operador não viram variável do GitHub: vão no JSON privado da fase 1, que o `config-hml` grava uma vez no bucket do state da HML e que o `infra-hml.yml` lê pela geração e pelo SHA-256.

**A rede vem antes da 1ª instância.** Aplicar o bootstrap com a rede antes de qualquer apply do `hml/` que crie o Cloud SQL: o IP privado não sai mais da instância, e a faixa só se atribui na criação. Ligar o IP privado numa instância existente a reinicia e não aceita faixa nomeada. Mudar `subrede_cidr` ou `faixa_psa_cidr` depois do apply recria o recurso, e o `prevent_destroy` recusa o plan.

## Depois do apply

O `cloudshell.sh depois <projeto>` faz os dois passos abaixo com pergunta `s/n` para cada um, relê o resultado no servidor e diz o que ficou; resposta diferente de `s` mantém e avisa.

**Conta padrão do Compute** (fora do Terraform, R-006): ligar a API do Compute cria a conta padrão, que pode receber o papel Editor. Depois do apply, ver se `<NUM>-compute@developer.gserviceaccount.com` existe (`gcloud iam service-accounts list --project=<id>`). Se existir:
1. `gcloud projects remove-iam-policy-binding <id> --member=serviceAccount:<NUM>-compute@developer.gserviceaccount.com --role=roles/editor`;
2. `gcloud iam service-accounts disable <NUM>-compute@developer.gserviceaccount.com --project=<id>`;
3. registrar na rodada. Web e jobs declaram `service_account` explícito no `hml/`.

**Rede `default`** (fora do Terraform): a doc descreve a criação dela em projeto novo, com regras de firewall que abrem SSH e RDP para `0.0.0.0/0`; não se sabe se nasce num projeto já existente, e o Trivy não a vê. Conferir com `gcloud compute networks list --project=<id>`. Se aparecer, apagar as regras dela (`gcloud compute firewall-rules list --project=<id> --filter="network~/default$"` e `gcloud compute firewall-rules delete <regra> --project=<id>`), depois a rede (`gcloud compute networks delete default --project=<id>`), e registrar na rodada.

**State:** já nasce no bucket próprio ([State do bootstrap](#state-do-bootstrap)); não há migração. O `objectAdmin` da `sa-infra-github` vale para o bucket do state da HML inteiro, e não alcança o do bootstrap.

**Revogar a sessão do dono** ao fim da janela, pelo wrapper: `auth revoke --all` e `auth application-default revoke`, com a prova pedida no R-006 §3.

**Sem environment com revisor** (R-006, passo 5): nenhum dos dois caminhos autentica. Não há variante da condição sem `environment`.
