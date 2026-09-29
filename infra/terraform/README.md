# Terraform da HML

Fonte do desenho: [R-006, atualização de 28/09/2026](../../docs/parceria/rodadas/evidencias/R-006-hospedagem.md) (commit `090caf7`). Região: [ADR 0005](../../docs/adr/0005-regiao-hml.md). Rede privada: [ADR 0006](../../docs/adr/0006-rede-privada-hml.md). Nada aqui foi aplicado.

| Pasta | O que cria | Quem aplica | State |
|---|---|---|---|
| [`bootstrap/`](bootstrap/README.md) | APIs, bucket do state, WIF do GitHub, contas de serviço, papéis no projeto e nas contas, rede privada (VPC, sub-rede, faixa e conexão PSA) | O Adrianus no Cloud Shell, uma vez, com o `cloudshell.sh`; o Claude responde pelo plan e as 3 IAs revisam pelo hash | Bucket próprio, fora do Terraform ([State do bootstrap](bootstrap/README.md#state-do-bootstrap)) |
| [`hml/`](hml/README.md) | Artifact Registry, Cloud SQL, segredos sem valor, Cloud Run web e jobs, IAM por recurso, IAP | CI por WIF, só no `infra-hml.yml`, com a `sa-infra-github` | Bucket do bootstrap, prefixo `hml/` |

## Ordem

1. **Adrianus, guiado pelas IAs:** login e consentimentos da lista abaixo, antes de tudo.
2. **`bootstrap/`**, uma vez, com a rede privada e o state no bucket próprio, criado antes do `init` ([State do bootstrap](bootstrap/README.md#state-do-bootstrap)). Logo depois do apply, desativar a conta padrão do Compute e conferir a rede `default` ([bootstrap](bootstrap/README.md#depois-do-apply)).
3. **`hml/` fase 1**, pela CI (`infra-hml.yml`, integrado: por ora só gera o plan; o apply pelo hash vem à parte), com `criar_cloud_run = false` e as 3 saídas da rede: registro, banco, segredos vazios e IAM. O `oidc_client_id` pode ficar vazio: só a fase 2 o exige.
4. **Valores fora do Terraform:** senhas por stdin, sem eco (R-006, passo 4), e segredo OAuth pelo Adrianus no console (passo 3b). Anotar só o número de cada versão.
5. **Se `url_controlada = "iap"`:** o Adrianus configura uma vez, no console, o cliente OAuth do IAP. Projeto sem organização não cria cliente OAuth por API.
6. **`hml/` fase 2**, pela CI, com `criar_cloud_run = true`, `versoes_segredos` e `oidc_client_id`.
7. **Publicação** (`publicar-hml.yml`, outro autor): imagens por digest, `safrion-preparo`, `safrion-demo-reset` e a web.

**Atenção à ordem:** o passo 3 precisa da rede do passo 2, porque a instância só aceita a faixa do IP privado na criação e o IP privado não sai mais dela. O passo 4 precisa da instância criada no passo 3. Se a sessão do dono for revogada ao fim do bootstrap (R-006 §3), as senhas exigem nova janela de login dele.

## O que depende do Adrianus

As IAs preparam cada passo e guiam na tela. Ao Adrianus ficam o login, os consentimentos e o que envolve conta, cobrança ou contrato dele.

- Criar o projeto da HML (`safrion-hml-1390827288`) e vincular a conta de faturamento, que cobra em BRL.
- Orçamento de alerta da HML: referência de US$ 30/mês, autorizada por ele em 29/09/2026 (avisos em 70, 90 e 100%). A referência não é teto, e orçamento de alerta não limita gasto.
- Criar a conta Google dos agentes (base da personificação).
- Google Auth Platform: identidade "Safrion HML", público Externo, em teste, escopo `openid`, domínio autorizado e URI `<origem>/entrar/retorno` (saída `origem` do `hml/`).
- Colar o segredo do cliente OAuth como versão de `hml-oidc-client-secret`, direto no console.
- Configurar o cliente OAuth do IAP no console (passo 5).
- Criar o grupo Google dos testadores e pôr e tirar gente dele. Só o grupo entra no Terraform (`iap_permitidos`).
- GitHub: variáveis dos environments `hml` e `hml-infra`, impressas pelo `cloudshell.sh variaveis` ([`bootstrap/README.md`](bootstrap/README.md#como-aplicar)). Revisor obrigatório de environment não está disponível em repositório privado no plano atual do GitHub: o portão humano é a aprovação do plan pelo hash, com veto dele.

## Nunca no Terraform

- Valor de segredo ou senha, `google_secret_manager_secret_version`, `root_password` ou `google_sql_user` do `postgres`.
- Chave JSON de conta de serviço (`google_service_account_key`).
- Faturamento, orçamento e conta de faturamento (`google_billing_*`).
- Projeto, cliente OAuth e tela de consentimento.
- Imagem real: só o pipeline publica, por digest.
- `terraform.tfvars`, state e plan: fora do Git (`.gitignore`).

## Antes de cada apply (ENG-063)

1. `terraform fmt -check`, `terraform init -backend=false` seguido de `terraform validate`, `tflint` e `trivy config --severity HIGH,CRITICAL --exit-code 1 .` sem achado alto não justificado, e sem supressão genérica.
2. `terraform plan -out=<arquivo>` fora do Git; na rodada, só o hash SHA-256 e a contagem add/change/destroy.
3. O time aprova o plan por esse hash, com veto do Adrianus; o apply usa só esse arquivo.
4. Plan com `destroy` ou `must be replaced` em Cloud SQL, bucket do state, segredos ou WIF é recusado e volta como plano específico (PRD 28.2).

**Achados esperados do scanner** (nada foi rodado; confirmar a severidade na 1ª execução):
- Cloud SQL: sem IP público (ADR 0006), o GCP-0017 fecha pelo desenho; o GCP-0015 segue com exceção proposta ([hml](hml/README.md#achados-do-scanner)).
- Rede do bootstrap: GCP-0076 (MEDIUM) e GCP-0029 (LOW), flow logs desligados por custo, abaixo do gate.
- Papéis `*.admin` da `sa-infra-github`: exceção ENG-005 proposta, com risco e compensação por papel no [bootstrap](bootstrap/README.md).
- Se algum sair como alto, registrar a exceção pela ENG-005 antes do apply.

## Pontos a levar ao R-006

O desenho segue o R-006 (`docs/hml-custo-infra`, até `6345d23`): `sa-infra-github`, WIF canônico por fluxo e environment, papel customizado e IAM do projeto no bootstrap. Estes quatro pontos o código resolve de um jeito que o R-006 ainda não descreve. Com o aceite do Codex, entram no R-006 e no `OPERACAO.md`:

- **Rotação de segredo na HML:** a versão fixada muda por apply do Terraform (`versoes_segredos`), não por `gcloud --update-secrets`. Assim a versão tem um dono só ([hml](hml/README.md#rotação-de-segredo)).
- **`SAFRION_VERSAO` e `SAFRION_COMMIT`:** entram por build-arg da imagem, não como variável da revisão, que o apply seguinte apagaria. O [Dockerfile](../../Dockerfile) já os recebe nos alvos web e preparo (E08); a publicação passa os dois `--build-arg`.
- **Testadores no IAP:** por grupo Google, criado pelo Adrianus, e não por e-mail no Terraform. Entrar e sair do teste não passa por apply, e nenhum e-mail vai para o plan ou para o state. Não verificado: IAP com grupo em projeto sem organização.
- **Ordem da 1ª subida:** as senhas (R-006, passo 4) precisam da instância, que nasce na fase 1 do `hml/`, pela CI. Por isso a janela da sessão do dono vai do bootstrap até as senhas, passando pela fase 1. A revogação vem depois delas.
