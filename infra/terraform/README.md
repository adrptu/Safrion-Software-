# Terraform da HML

Fonte do desenho: [R-006, atualização de 28/09/2026](../../docs/parceria/rodadas/evidencias/R-006-hospedagem.md) (commit `090caf7`). Região: [ADR 0005](../../docs/adr/0005-regiao-hml.md). Nada aqui foi aplicado.

| Pasta | O que cria | Quem aplica | State |
|---|---|---|---|
| [`bootstrap/`](bootstrap/README.md) | APIs, bucket do state, WIF do GitHub, contas de serviço, papéis no projeto e nas contas | Codex, localmente, uma vez, na janela da sessão do dono | Local; migrável para o bucket |
| [`hml/`](hml/README.md) | Artifact Registry, Cloud SQL, segredos sem valor, Cloud Run web e jobs, IAM por recurso, IAP | CI por WIF, só no `infra-hml.yml`, com a `sa-infra-github` | Bucket do bootstrap, prefixo `hml/` |

## Ordem

1. **Adrianus, no console:** os atos da lista abaixo, antes de tudo.
2. **`bootstrap/`**, local, uma vez.
3. **`hml/` fase 1**, pela CI (`infra-hml.yml`, a criar), com `criar_cloud_run = false`: registro, banco, segredos vazios e IAM.
4. **Valores fora do Terraform:** senhas por stdin, sem eco (R-006, passo 4), e segredo OAuth pelo Adrianus no console (passo 3b). Anotar só o número de cada versão.
5. **Se `url_controlada = "iap"`:** o Adrianus configura uma vez, no console, o cliente OAuth do IAP. Projeto sem organização não cria cliente OAuth por API.
6. **`hml/` fase 2**, pela CI, com `criar_cloud_run = true` e `versoes_segredos`.
7. **Publicação** (`publicar-hml.yml`, outro autor): imagens por digest, `safrion-preparo`, `safrion-demo-reset` e a web.

**Atenção à ordem:** o passo 4 precisa da instância criada no passo 3. Se a sessão do dono for revogada ao fim do bootstrap (R-006 §3), as senhas exigem nova janela de login dele.

## O que só o Adrianus faz

- Criar o projeto da HML e vincular o faturamento; ver se a cobrança é em US$ com cartão ou por contratação local.
- Criar o orçamento de alerta (US$ 25, avisos em 70, 90 e 100%). Orçamento não limita gasto.
- Criar a conta Google dos agentes (base da personificação).
- Google Auth Platform: identidade "Safrion HML", público Externo, em teste, escopo `openid`, domínio autorizado e URI `<origem>/entrar/retorno` (saída `origem` do `hml/`).
- Colar o segredo do cliente OAuth como versão de `hml-oidc-client-secret`, direto no console.
- Configurar o cliente OAuth do IAP no console (passo 5).
- Criar o grupo Google dos testadores e pôr e tirar gente dele. Só o grupo entra no Terraform (`iap_permitidos`).
- GitHub: environment `hml` com ele como único revisor e as variáveis do [`bootstrap/README.md`](bootstrap/README.md).

## Nunca no Terraform

- Valor de segredo ou senha, `google_secret_manager_secret_version`, `root_password` ou `google_sql_user` do `postgres`.
- Chave JSON de conta de serviço (`google_service_account_key`).
- Faturamento, orçamento e conta de faturamento (`google_billing_*`).
- Projeto, cliente OAuth e tela de consentimento.
- Imagem real: só o pipeline publica, por digest.
- `terraform.tfvars`, state e plan: fora do Git (`.gitignore`).

## Antes de cada apply (ENG-063)

1. `terraform fmt -check`, `terraform validate`, `tflint` e `trivy config .` sem achado alto não justificado.
2. `terraform plan -out=<arquivo>` fora do Git; na rodada, só o hash SHA-256 e a contagem add/change/destroy.
3. O time aprova o plan por esse hash, com veto do Adrianus; o apply usa só esse arquivo.
4. Plan com `destroy` ou `must be replaced` em Cloud SQL, bucket do state, segredos ou WIF é recusado e volta como plano específico (PRD 28.2).

**Achados esperados do scanner** (nada foi rodado; confirmar a severidade na 1ª execução):
- Cloud SQL com IP público: exigido pelo desenho sem VPC. Compensação: nenhuma rede autorizada, `connector_enforcement = "REQUIRED"` e `ssl_mode = "ENCRYPTED_ONLY"`.
- Papéis `*.admin` da `sa-infra-github`: exceção ENG-005 proposta, com risco e compensação por papel no [bootstrap](bootstrap/README.md).
- Se algum sair como alto, registrar a exceção pela ENG-005 antes do apply.

## Pontos a levar ao R-006

O desenho segue o R-006 (`docs/hml-custo-infra`, até `6345d23`): `sa-infra-github`, WIF canônico por fluxo e environment, papel customizado e IAM do projeto no bootstrap. Estes quatro pontos o código resolve de um jeito que o R-006 ainda não descreve. Com o aceite do Codex, entram no R-006 e no `OPERACAO.md`:

- **Rotação de segredo na HML:** a versão fixada muda por apply do Terraform (`versoes_segredos`), não por `gcloud --update-secrets`. Assim a versão tem um dono só ([hml](hml/README.md#rotação-de-segredo)).
- **`SAFRION_VERSAO` e `SAFRION_COMMIT`:** entram por build-arg da imagem, não como variável da revisão, que o apply seguinte apagaria. Isso muda o Dockerfile na publicação.
- **Testadores no IAP:** por grupo Google, criado pelo Adrianus, e não por e-mail no Terraform. Entrar e sair do teste não passa por apply, e nenhum e-mail vai para o plan ou para o state. Não verificado: IAP com grupo em projeto sem organização.
- **Ordem da 1ª subida:** as senhas (R-006, passo 4) precisam da instância, que nasce na fase 1 do `hml/`, pela CI. Por isso a janela da sessão do dono vai do bootstrap até as senhas, passando pela fase 1. A revogação vem depois delas.
