# Hospedagem de baixo custo — Homologação (HML) e piloto de produção

Data de referência e de acesso às fontes: **27/09/2026**; a seção "Atualização de 28/09/2026" relê os preços do Google Cloud e a PTAX em 28/09. Só leitura: nenhuma conta criada, nenhum cadastro aberto, nenhum dado informado.

**Rótulos.** _verificado_ = número lido na página oficial do provedor nesta data. _especificado_ = conta ou suposição minha feita a partir de números verificados (uso, tamanho, horas). _não verificado_ = sem fonte oficial lida.

**Cotação.** PTAX venda de 25/09/2026 (último dia útil antes de 27/09, um domingo): **R$ 5,1991 por US$** (verificado, API PTAX do Banco Central, fonte F1). Cartão internacional paga IOF de **3,5%** (especificado pela Fazenda em maio/2025, fonte F2; vigência em set/2026 e spread do banco não verificados). Fator usado: 5,1991 × 1,035 = **R$ 5,3811 por US$** com IOF.

**O que o PRD já decidiu (lido no repositório, só leitura).** §28.1 dá como topologia de referência _Google Cloud Run + Cloud SQL PostgreSQL/PostGIS com HA regional + Cloud Storage + Secret Manager + Cloud Tasks/Jobs_, via Terraform, com região escolhida em ADR. §27.4 exige HML com estrutura equivalente à produção, projeto e banco próprios e **a mesma imagem por digest** promovida para produção. §30.5 pede backup diário com retenção de 35 dias e PITR de pelo menos 7 dias. NFR-11 pede RPO ≤ 15 min e RTO ≤ 4 h. Isso pesa na recomendação.

## Atualização de 28/09/2026: a HML do artefato real (substitui a recomendação de HML abaixo onde houver diferença)

**O que mudou desde 27/09:**

- Existe o artefato: imagem `web` distroless e alvo `preparo`, os comandos `preparar-banco`, `demo-reset` e `vincular-identidade`, login OIDC e `/saude`, verificados na CI do PR #10.
- O projeto `project-d6996034-e2ee-4e56-836` existe com faturamento vinculado e só Vertex AI habilitado. Não há servidor, banco nem orçamento criado (`conexao-google-cloud.md`, 28/09 15:58 UTC).
- **Nenhum recurso foi criado por esta atualização.**

**Corrigido depois de `622bdea` (revisão do Codex de 28/09 e checagem adversarial de segurança; só texto, nada provisionado):**
- **Backups:** 7 → **35 retidos**, alinhado ao PRD 30.5. Com 7 backups e 7 dias de log, sobravam só 6 a 7 dias de PITR.
- **PITR:** sem custo de log na Enterprise nova. A sensibilidade de "log no disco" virou (g), o crescimento do disco.
- **Franquia do Cloud Run:** é desconto sobre o gasto, da conta de faturamento. A web e os jobs passam a US$ 0, e todos os cenários foram refeitos.
- **Segredos:** `PGPASSWORD` explícito no `demo-reset`; versão fixa; rotação que desativa antes e só destrói depois de 7 dias e de um teste de recuperação.
- **Segurança:**
  - condição completa do WIF;
  - senhas geradas sem o agente ver;
  - `postgres` fora do state;
  - proteção contra exclusão nos recursos críticos;
  - sessão do dono registrada como exceção, com revogação comprovada nos dois caminhos de ADC;
  - conta própria dos agentes;
  - operador humano;
  - IAP como padrão;
  - dados só fictícios;
  - imagem provisória com `ignore_changes`;
  - faturamento só do Adrianus.

**Corrigido depois de `090caf7` (2ª revisão do Codex, 28/09):**
- principal próprio de infraestrutura (`sa-infra-github`), com acesso ao state e papel customizado de segredos sem leitura de valor. O IAM do projeto foi para o bootstrap;
- teto de gasto nativo do Cloud Run proposto em US$ 15 brutos, separado do alerta e não configurado;
- IAP direto confirmado sem organização, com a 1ª ativação pelo console e o agente de serviço do IAP;
- rotação validada sem resetar a demonstração.

**Câmbio:** PTAX de venda de 28/09/2026 = **R$ 5,2132** (boletim das 13:03). Com IOF de 3,5%, dá R$ 5,3957 (IOF não reconferido hoje). **Se a conta de faturamento for de contratação local no Brasil, os preços dos SKUs não incluem impostos (14% sobre o uso) e o IOF provavelmente não se aplica.** Só o console mostra qual caso vale para a conta do Adrianus (https://docs.cloud.google.com/billing/docs/resources/vat-overview).

### Custo mensal da HML mínima (preços de São Paulo relidos em 28/09; mês = 730 h; corrigido em 28/09 após a revisão do Codex)

| Item | Conta | US$/mês |
| --- | --- | --- |
| Cloud SQL PostgreSQL 17, `db-f1-micro`, Enterprise, zonal | 0,0158 × 730 | 11,53 |
| Disco SSD de 10 GiB (o mínimo da API), autoaumento até 20 GiB | 0,000349315 × 730 × 10 | 2,55 |
| Backup diário, **35 retidos** (PRD 30.5). Premissa: 1 completo de cerca de 1 GiB + 34 incrementais de cerca de 0,17 GiB = 6,67 GiB | 0,000164384 × 730 × 6,67 | 0,80 |
| **PITR de 7 dias** (o máximo da edição Enterprise), com os logs no Cloud Storage da mesma região | sem custo adicional por instância (F35) | 0 |
| Cloud Run web, 20 h de uso, 1 vCPU e 0,5 GiB, cobrança por requisição | bruto 72.000 × 0,0000336 + 36.000 × 0,0000035 = 2,55; **coberto pela franquia** (US$ 4,32 de CPU e US$ 0,90 de memória) | 0 |
| Cloud Run Jobs `safrion-preparo` (10 × 3 min) e `safrion-demo-reset` (4 × 2 min), cobrança por instância | bruto 2.280 × 0,0000216 + 1.140 × 0,0000024 = 0,05; coberto pela franquia | 0 |
| Artifact Registry, 2 GiB (0,5 GiB grátis; mesmo preço em repositório regional e multirregional) | 1,5 × 0,000136986 × 730 | 0,15 |
| Saída de internet para os testadores, cerca de 1 GiB | 1 × 0,19 | 0,19 |
| Secret Manager (4 versões ativas; franquia de 6 **por conta de faturamento**), Logging (< 50 GiB grátis), Monitoring, WIF, IAM, requisições (< 2 milhões) | — | 0 |
| Bucket do state do Terraform (< 10 MiB) | 0,000047945 × 730 × 0,01 | 0,00 |
| **Total** | | **≈ 15,22** (R$ 79,37 pela PTAX; **R$ 82,15 com IOF**; com imposto local de 14%, ≈ US$ 17,36) |

**Rótulos:**
- Preços unitários: _verificado_ em 28/09 nas páginas oficiais: Cloud Run (F12), Cloud SQL, inclusive o IP ocioso de São Paulo a US$ 0,015/h (F13b), Artifact Registry (F38) e Secret Manager (F39).
- Saída de internet: US$ 0,19 é o preço de saída do Cloud SQL. O Cloud Run cobra pela tabela de rede Premium, _não verificada_ nesta rodada; o efeito é menor que US$ 0,10 com 1 GiB.
- Quantidades (20 h, 38 min, 2 GiB de imagens, 1 GiB de saída, 6,67 GiB de backup) e totais: _especificado_.
- IOF e imposto local: _não verificado_.

**Franquia do Cloud Run (corrigida):**
- Ela é "a spending based discount using Tier 1 pricing" e "aggregated across projects by billing account" (F12). Ou seja, é um desconto sobre o gasto, em dólar, valorado a preço de us-central1: US$ 4,32 de CPU e US$ 0,90 de memória por mês. É abatido ao preço de São Paulo, não acumula de um mês para outro e é **da conta de faturamento, não do projeto**. Em São Paulo, cobre cerca de 35,7 h/mês de web ativa com 1 vCPU.
- A versão `622bdea` tratava a franquia como desconto por unidade e atribuía US$ 0,74 à web e aos jobs; isso foi retirado.
- _Não verificado_: se os jobs dividem o saldo com a web (a página mostra franquias de mesmo valor); se a franquia cobre o tempo ocioso de uma instância mínima; como a fatura em região Tier 2 aplica o desconto (a página só tem exemplos em Tier 1). **Conferir na 1ª fatura.**
- **Pior caso:** se outro projeto da mesma conta de faturamento (o projeto atual ou outro) consumir a franquia, a HML paga o bruto de 2,60, e o total vai a **17,82**.

**Sensibilidades (sobre a base de 15,22):**

- (a) web com 1 instância mínima, cobrança por requisição: **25,97 a 28,64**, conforme a franquia cubra ou não o tempo ocioso. Com CPU sempre alocada (cobrança por instância), **≈ 69,92**;
- (b) banco `db-g1-small`: **42,01**;
- (c) PITR de 7 dias: **+0**. A versão `622bdea` somava 2,55 porque supunha o log no disco; em instância Enterprise nova, o log fica no Cloud Storage (F35);
- (d) 100 h de uso por mês, com cerca de 5 GiB de saída: **23,76**. A faixa vai de 23,49 a 23,81: 23,49 se a franquia for um saldo único de US$ 5,22 para CPU e memória; 23,81 se os jobs dividirem o saldo com a web;
- (g) disco cresce por autoaumento de 10 para 20 GiB (dados, cerca de 1 dia de WAL local, arquivos temporários): **17,77**, acima do aviso de 70% (US$ 17,50);
- (d) + (g): **26,31** (26,04 a 26,36), acima do orçamento de alerta de US$ 25;
- (e) parar a instância quase não economiza, porque o IP ocioso custa US$ 10,95 (US$ 0,015/h em São Paulo, F13b): **14,64**. Apagar a instância exige desligar a proteção por plano específico e a confirmação do Adrianus, e os backups automáticos vão junto (retenção depois da exclusão: não verificado);
- (f) se o IPv4 fosse cobrado com a instância rodando, o que a página não indica: **26,17**. Conferir na 1ª fatura;
- (h) franquia do Cloud Run consumida por outro projeto da conta: **17,82**;
- (i) volume de backup, que é premissa: **14,54** se quase nada mudar por dia e **18,62** se cada backup regravar o banco inteiro.

**O Cloud SQL (instância, disco e backups) é cerca de 98% da conta e não tem teto automático.** O máximo de instâncias do Cloud Run também **não é teto em dinheiro**: com as 2 instâncias ocupadas o mês todo, a web passaria de US$ 180.

**Orçamento:**
- US$ 25/mês **só de alerta**, com escopo no projeto HML e avisos em **70% (US$ 17,50), 90% e 100%** do gasto real e em 100% do previsto (PRD 28.4; plano R-006 passos 11 e 12). A base usa 61%. O aviso de 70% dispara com o disco em 20 GiB ou com a franquia dividida, e isso é esperado: é aviso, não corte.
- **Orçamento não limita uso nem gasto.** O teto de gasto nativo do Google só vale para Cloud Run, Cloud Run functions, Gemini API e Vertex; **o Cloud SQL não está coberto**.
- Aumentar o orçamento **antes** de mudar a configuração:
  - US$ 30 com uso intenso;
  - US$ 35 com mínimo 1;
  - US$ 50 com `db-g1-small`;
  - US$ 75 com CPU sempre alocada.
- O valor é autorização de gasto do Adrianus, em frase literal (R-006 §3; leitura do Codex de 28/09 17:04).

**Teto de gasto nativo do Cloud Run (proposta; não configurado nem autorizado):**
- É um orçamento separado do alerta: vale para **um projeto e um serviço**, é mensal e **pausa os pedidos novos** ao Cloud Run (web e jobs) quando o custo estimado passa do valor. Não apaga recurso nem dado; os pedidos em curso terminam (F42).
- Usa **custo bruto estimado, sem franquia nem créditos**. A aplicação não é instantânea: o que passar por atraso de medição é cobrado normalmente, e o Google recomenda um valor um pouco abaixo do limite real. Avisa em 50%, 80% e 100%. Depois de liberar, o serviço pode levar até 1 h para voltar (F42).
- **Não cobre o Cloud SQL**, que é cerca de 98% da conta, mas custo fixo e previsível.
- **Valor proposto: US$ 15/mês, no Cloud Run do projeto da HML.** O bruto estimado do Cloud Run é 2,60 no uso base, 12,78 com 100 h e 16,02 com 1 instância mínima (especificado, com os preços da tabela). Os US$ 15 cobrem o uso normal e o intenso e param um abuso por ingress público ou um laço de jobs. Ligar a instância mínima exige **subir o teto antes**, como o orçamento.
- **Efeito na HML:** se o teto disparar, a HML fica fora do ar até alguém liberar. Para testes é aceitável; é melhor que um gasto sem limite.
- **Quem faz:** o Adrianus, na conta de faturamento (item da lista de execução), com autorização de gasto em frase dele. Os agentes não mexem em faturamento.

**Fontes desta atualização (acessadas em 28/09/2026):**
- F12 https://cloud.google.com/run/pricing;
- F13b https://cloud.google.com/sql/pricing (região São Paulo);
- F15 https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/backups (backups incrementais, cobrança pelo tamanho);
- F35 https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/restore#log-storage-for-pitr (instâncias Enterprise criadas depois de 09/01/2023: logs do PITR no Cloud Storage, sem custo adicional por instância);
- F36 https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/backup-options (retenção de log de 1 a 7 dias na Enterprise; 7 backups com 7 dias de log retêm só de 6 a 7 dias de log);
- F37 https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/configure-pitr (por Terraform, backup e PITR precisam ser ligados explicitamente);
- F38 https://cloud.google.com/artifact-registry/pricing;
- F39 https://cloud.google.com/secret-manager/pricing (versão desativada conta como ativa; US$ 0,06/mês por versão acima da franquia; destruída é grátis);
- F40 https://docs.cloud.google.com/run/docs/configuring/jobs/secrets (variável declarada por segredo; versão fixa recomendada; sem o segredo, a instância não sobe);
- F41 https://docs.cloud.google.com/secret-manager/docs/destroy-secret-version e https://docs.cloud.google.com/secret-manager/docs/best-practices (destruir é permanente; desativar antes e observar);
- F42 https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps (teto de gasto: serviços elegíveis, um projeto e um serviço, custo bruto estimado, pausa de pedidos novos, atraso de aplicação, avisos 50/80/100%);
- F43 https://docs.cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run (IAP direto no Cloud Run, projeto sem organização, cliente OAuth pelo console, papéis);
- F44 https://developer.hashicorp.com/terraform/language/backend/gcs (backend gcs: Storage Object Admin no bucket do state; fonte conferida pelo Codex em 28/09).

### Desenho mínimo (sem domínio próprio)

| Componente                 | Onde roda                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Configuração e segredos                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Banco                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Web (`web@sha256`)         | Cloud Run service `safrion-web`, southamerica-east1, mínimo 0 e máximo 2, concorrência 20, 1 vCPU, 512 MiB, CPU só na requisição, conta `sa-web`                                                                                                                                                                                                                                                                                                                                                                                     | `DATABASE_URL=postgresql://app_runtime@/safrion_hml?host=/cloudsql/<PROJ>:southamerica-east1:safrion-hml` **sem senha**; `PGPASSWORD` vindo do segredo `hml-db-app-runtime-senha` (o `pg` 8.23 lê `PGPASSWORD`, sem mudança de código); `SAFRION_ORIGEM=https://safrion-web-<NUM>.southamerica-east1.run.app`; `SAFRION_AMBIENTE=hml`; `SAFRION_VERSAO`/`SAFRION_COMMIT` injetados na publicação; `SAFRION_OIDC_ISSUER=https://accounts.google.com`; `SAFRION_OIDC_CLIENT_ID`; `SAFRION_OIDC_CLIENT_SECRET` do segredo `hml-oidc-client-secret` | Conexão Cloud SQL integrada do Cloud Run (socket `/cloudsql`) |
| Preparo (`preparo@sha256`) | Cloud Run Job `safrion-preparo`, 1 tarefa, `max_retries 0`, 600 s, conta `sa-preparo`, args `--ambiente hml --banco safrion_hml`                                                                                                                                                                                                                                                                                                                                                                                                     | `SAFRION_ADMIN_URL=postgresql://postgres@/postgres?host=/cloudsql/…` sem senha; `PGPASSWORD` de `hml-db-admin-senha`; `SAFRION_SENHA_MIGRATOR` e `SAFRION_SENHA_APP_RUNTIME` dos segredos próprios                                                                                                                                                                                                                                                                                                                                              | Socket `/cloudsql`                                            |
| Demonstração               | Cloud Run Job `safrion-demo-reset` com a imagem `preparo`, command `node`, args `dist/cli/demo-reset.js --confirmar hml`, conta `sa-demo`                                                                                                                                                                                                                                                                                                                                                                                            | `DATABASE_URL` do `app_runtime` sem senha (como a web), **`PGPASSWORD` declarado no job com referência ao segredo `hml-db-app-runtime-senha`, em versão fixa** (`--set-secrets PGPASSWORD=hml-db-app-runtime-senha:<N>`; no Terraform, `env` com `value_source.secret_key_ref`). O `secretAccessor` da `sa-demo` autoriza a leitura, mas não cria a variável (F40). O vínculo de IAM nasce antes do job (`depends_on`), e a versão `<N>` existe antes da 1ª execução. `SAFRION_AMBIENTE=hml` | Socket `/cloudsql`                                            |
| Vínculo de identidade      | **Na máquina do operador, não em job**: o código entra pela entrada padrão, sem eco, e um job não tem terminal. Cloud SQL Auth Proxy em 127.0.0.1 com a identidade IAM do operador (Cloud SQL Client)                                                                                                                                                                                                                                                                                                                                | `SAFRION_ADMIN_URL=postgresql://postgres@127.0.0.1:6543/postgres`; `PGPASSWORD` lido do Secret Manager sem aparecer na tela, com `unset` ao final; checkout do commit publicado; Node 24.21                                                                                                                                                                                                                                                                                                                                                     | Auth Proxy (TLS + IAM)                                        |
| Banco                      | Cloud SQL `safrion-hml`: **`database_version = POSTGRES_17`, `edition = ENTERPRISE`, `tier = db-f1-micro`, explícitos** (PG16+ nasce Enterprise Plus); zonal; SSD de 10 GB com autoaumento até 20 GB; backup automático diário standard com **35 retidos** (PRD 30.5; o Google recomenda reter mais backups que os dias de log, F36); **PITR de 7 dias**, o máximo da Enterprise (35 dias de log só na Enterprise Plus). No Terraform, tudo explícito (F37): `backup_configuration { enabled = true, point_in_time_recovery_enabled = true, transaction_log_retention_days = 7, location = "southamerica-east1", backup_retention_settings { retained_backups = 35, retention_unit = "COUNT" } }`. O campo que escolhe backup standard ou enhanced: não verificado. **Local dos backups fixado em southamerica-east1:** sem isso, eles vão para uma multirregião (asia, eu ou us), fora do Brasil, onde o preço de backup de São Paulo usado no custo não vale. A HML guarda a identidade real dos testadores; proteção contra exclusão tripla: `deletion_protection = true` (Terraform), `settings.deletion_protection_enabled = true` (API) e `lifecycle { prevent_destroy = true }`; IP público **sem redes autorizadas** (só conector com IAM); `server_ca_mode = GOOGLE_MANAGED_INTERNAL_CA` explícito; `max_connections` padrão 25 → orçamento de ≤ 18 (web 2 × pool 3 + jobs + operador) | O Terraform cria **só a instância, sem `root_password` e sem `google_sql_user` para o `postgres`**: a senha nunca entra no state nem no plan. Banco `safrion_hml`, `migrator`, `app_runtime` e `app_sessao` nascem **só pelo job de preparo**                                                                                                                                                                                                                                                                                                                                                                                     |
| Segredos                   | Secret Manager, replicação em southamerica-east1: `hml-db-admin-senha`, `hml-db-migrator-senha`, `hml-db-app-runtime-senha`, `hml-oidc-client-secret`                                                                                                                                                                                                                                                                                                                                                                                | O Terraform cria o segredo e o IAM; **os valores entram por stdin, fora do Terraform** (senão iriam para o state e o plan). Senhas alfanuméricas de 32 caracteres. `prevent_destroy` nos 4 segredos (apagar o segredo apaga todas as versões). Web e jobs referem **número de versão fixo, nunca `latest`** (F40).<br>**Rotação:**<br>(1) gravar a nova versão por stdin;<br>(2) trocar a senha no banco. A antiga deixa de valer na hora, e conexões novas falham até o passo 3;<br>(3) republicar a web e atualizar os jobs com o novo número, usando **`--update-secrets`**: `--set-secrets` apaga os outros segredos do job, e o `safrion-preparo` tem 3;<br>(4) validar **sem destruir nada**. `/saude` e o login confirmam a credencial `app_runtime`, a mesma do `demo-reset`. `gcloud run jobs describe` confirma o número de versão fixado nos 2 jobs. **Não executar `safrion-demo-reset` para validar**, porque o reset troca a geração e derruba os vínculos reais, nem o `safrion-preparo` sem migração pendente. A credencial do admin é conferida pelo operador, pelo Auth Proxy. **Atenção:** o `preparar-banco` confere a senha dos papéis que já existem e recusa com `CREDENCIAL_DIVERGENTE` se ela mudou. A troca da senha de `migrator` ou `app_runtime` é feita pelo admin (`ALTER ROLE … PASSWORD`, sem eco), e o procedimento precisa estar escrito em `OPERACAO.md` antes da 1ª troca;<br>(5) **desativar** a versão antiga. É reversível e leva algum tempo para propagar;<br>(6) destruir só depois de 7 dias de observação e de um teste de recuperação registrado, com confirmação do Adrianus. O Google recomenda desativar antes de destruir e dá como exemplo esperar uma semana (F41). Destruir é permanente.<br>**Custo:** versão desativada conta como ativa. Com as 4 em uso, até 2 desativadas cabem na franquia de 6, se nenhum outro projeto da conta a usar; acima disso, US$ 0,06/mês cada (F39). Um restore traz de volta os usuários do backup, possivelmente com a senha da época: conferir no ensaio de restauração                                                                                                                                                                                                                                                                     | —                                                             |
| Imagens                    | Artifact Registry `safrion` (Docker, southamerica-east1), tags imutáveis, limpeza: 10 versões mais recentes e sem tag por 14 dias                                                                                                                                                                                                                                                                                                                                                                                                    | Publica o **mesmo digest que o Trivy varreu**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | —                                                             |
| Publicação                 | GitHub Actions `publicar-hml.yml` (**a criar**): push em `main`, environment `hml` com revisor, `permissions: id-token: write, contents: read`, WIF                                                                                                                                                                                                                                                                                                                                                                                  | Publica as imagens → executa o preparo → publica a web por digest → testa `/saude` exigindo `ok`, `hml` e `commit = GITHUB_SHA` → grava o manifesto da publicação. Serviço e jobs nascem no Terraform com imagem provisória (`us-docker.pkg.dev/cloudrun/container/hello`) e `lifecycle { ignore_changes = [<atributo de imagem>, client, client_version] }`: a imagem real é só do pipeline, senão o próximo apply reverte a HML em silêncio                                                                                                                                                                                                                                                                                                                                                                               | —                                                             |

**Identidades de menor privilégio, sem chave JSON:**

- `sa-web`: `cloudsql.client` e `secretAccessor` só em `app-runtime` e `oidc`;
- `sa-preparo`: `cloudsql.client` e `secretAccessor` nas 3 senhas do banco;
- `sa-demo`: `cloudsql.client` e `secretAccessor` só em `app-runtime`;
- `sa-deploy-github`: `artifactregistry.writer` no repositório, `run.developer` nos 3 recursos, `iam.serviceAccountUser` nas 3 SAs de runtime. `workloadIdentityUser` só para `principalSet://…/attribute.repository_id/<ID_REPO>`. O provider do WIF tem `attribute_condition`:
  `assertion.repository_id == '<ID_REPO>' && assertion.repository_owner_id == '<ID_DONO>' && assertion.ref == 'refs/heads/main' && assertion.event_name in ['push','workflow_dispatch'] && assertion.workflow_ref.startsWith('adrptu/Safrion-Software-/.github/workflows/publicar-hml.yml@') && assertion.environment == 'hml'`.
  Sem `workflow_ref` e `event_name`, qualquer workflow com ref `main` (inclusive `pull_request_target`) receberia a SA. **Atenção:** na prática, ela soma o poder das SAs de runtime, inclusive a senha do `postgres` via `sa-preparo`. A página de segredos cita `run.admin` para configurá-los: confirmar no 1º plan se `run.developer` basta para trocar a versão do segredo, sem ampliar o papel antes de testar;
- `sa-infra-github`: aplica o `infra/terraform/hml` pela CI, com as permissões da divisão do R-006 no passo 3; `workloadIdentityUser` só para o `principalSet` do workflow `infra-hml.yml` em `main`;
- operador humano (o Adrianus, nunca um agente): `run.invoker` nos jobs, `cloudsql.client`, `secretAccessor` **só em `hml-db-admin-senha`**, `logging.viewer`. A verificar: autenticação IAM do Cloud SQL pelo Auth Proxy (`--auto-iam-authn`), com o usuário IAM dele membro de `migrator`, tira a senha do caminho;
- proprietário: `owner` só para o bootstrap e emergências. Conta de faturamento, orçamento, cartão e aceites de termos são só dele: agente não usa `gcloud billing` nem a API de orçamentos;
- agentes: `sa-agentes-leitura`, só leitura (`run.viewer`, `cloudsql.viewer`, `logging.viewer`, `monitoring.viewer`, `artifactregistry.reader`), por _impersonation_, **sem** `secretAccessor`. **Base da personificação:** uma conta Google separada para os agentes, criada pelo Adrianus (agente não cria conta), sem papel no projeto além de `roles/iam.serviceAccountTokenCreator` em `sa-agentes-leitura`. Se o Gemini continuar pelo Vertex, ela recebe o mesmo papel em `sa-vertex`, que tem `roles/aiplatform.user`. Todo comando dos agentes usa `--impersonate-service-account`;
- `allUsers` com `run.invoker` só no serviço web e só se o ingress público for a exceção aprovada (lacunas); nunca nos jobs. Com IAP, o `run.invoker` vai para o agente de serviço do IAP;
- conta padrão do Compute: depois de habilitar as APIs, ver se `<NUM>-compute@developer.gserviceaccount.com` existe. Se existir, tirar dela `roles/editor` e desativá-la. Declarar `service_account` explícito em toda revisão e todo job. Sem organização, a política que desliga a concessão automática não se aplica (não verificado).

**Sondas:** o `HEALTHCHECK` do Dockerfile não vale no Cloud Run. Usar a **sonda de inicialização HTTP em `/saude`**, que trava a revisão sem banco, e **nenhuma sonda de atividade em `/saude`**, porque ela responde 503 quando o banco cai e derrubaria instâncias sadias.

**Dados:** só fictícios na HML (PRD 27.4). É proibido carregar dump, planilha ou cadastro real. O único dado pessoal real é a identidade OIDC do testador, guardada só no vínculo e apagada ao encerrar o teste. A web não registra e-mail nem `sub` em log, só o id interno, porque os agentes leem os logs (AGT-01).

### Ordem de execução, com quem faz o quê (nada foi executado)

Em 28/09, o Adrianus delegou às 3 IAs as decisões que dependiam dele. Os **atos que exigem a identidade dele** continuam com ele: login, aceite de termos, faturamento, cartão e criação de conta.

1. **Adrianus:**
   - (a) criar o **projeto dedicado `safrion-hml-<sufixo>`** (o ID é global; PRD 27.4 e ENG-064) e vinculá-lo à conta de faturamento no console, ou usar o projeto atual, se o time decidir assim;
   - (b) ver no console **se a cobrança é em US$ com cartão ou por contratação local**;
   - (c) criar o **orçamento de alerta** no valor decidido, com 70/90/100% e escopo no projeto da HML (D4);
   - (d) criar a **conta Google dos agentes** (base da personificação).
2. **Adrianus, no console, antes de todo o resto (risco que derruba o desenho):** na Google Auth Platform do projeto HML:
   - identidade visual "Safrion HML", público Externo, status Em teste, escopo só `openid`;
   - **registrar o domínio autorizado e o URI `https://safrion-web-<NUM>.southamerica-east1.run.app/entrar/retorno`**. Se o Google **recusar** `run.app`, a HML precisa de domínio próprio com balanceador global, a partir de **US$ 18,25/mês**, e o total passa de US$ 25: decisão nova de custo;
   - com escopo só `openid`, a lista de usuários de teste talvez não barre ninguém, e aí qualquer conta Google chega ao pedido de acesso. **Não verificado:** testar com uma conta fora da lista. Se a lista barrar, ela vira a lista de permitidos, sem custo.
3. **Codex, bootstrap, uma única vez:**
   - **Estado em 28/09:** a sessão de `adrptu@gmail.com` está gravada em `/Users/adrianussanders/.config/safrion-gcloud` desde 27/09 e é compartilhada por Codex e Claude, inclusive para o Gemini via Vertex. Isso dá poder de Owner e acesso ao faturamento nesta máquina. **Exceção ENG-005 até o fim deste passo.** Escopo: leitura e Vertex no projeto atual. Compensação: nenhum comando de escrita, de segredo ou de faturamento fora do bootstrap. Aprovação pelo time, por delegação, com veto do Adrianus. Vencida sem bootstrap, a sessão é revogada, e o Adrianus entra de novo só na janela do bootstrap.
   - **Pré-requisitos:** instalar Terraform, TFLint, um scanner de configuração e o Cloud SQL Auth Proxy, conferindo o checksum oficial.
   - Com projeto dedicado, todo comando usa `--project=<id da HML>`, o provider fixa `project`, e o wrapper ganha uma variante da HML. O wrapper atual fixa o projeto do Vertex.
   - O que o bootstrap cria:
     - bucket do state com versionamento, `uniform_bucket_level_access`, `public_access_prevention = "enforced"`, `prevent_destroy` e acesso só do dono;
     - APIs (run, sqladmin, artifactregistry, secretmanager, iam, iamcredentials, sts, cloudresourcemanager, serviceusage e **iap**);
     - papel customizado `safrionInfraSegredos` e o IAM do projeto (ver a divisão abaixo);
     - pool e provider WIF, com a condição da seção de identidades e `prevent_destroy`;
     - SAs.
   - **Divisão do R-006:** localmente, só o bootstrap. O `infra/terraform/hml` é aplicado pela CI por WIF, com **principal próprio de infraestrutura**, e não com a SA de publicação (achado do Codex, 28/09):
     - **`sa-infra-github`**, usada só pelo workflow `infra-hml.yml` (plan em PR, apply em `main`, environment `hml-infra` com o Adrianus como único revisor). O WIF liga cada SA ao seu workflow pelo `principalSet` do atributo `workflow_ref`: `sa-deploy-github` ← `…/publicar-hml.yml@refs/heads/main`, `sa-infra-github` ← `…/infra-hml.yml@refs/heads/main`. A condição do provider aceita só esses dois workflows. Outra ref ou outro workflow não recebe nenhuma das duas;
     - **state:** `roles/storage.objectAdmin` **só no bucket do state** para `sa-infra-github` (backend gcs, F44). O "acesso só do dono" do bucket vira dono + `sa-infra-github`;
     - **o que ela cria na HML:**
       - `roles/cloudsql.admin`;
       - `roles/run.admin`, necessário para política de IAM do serviço e dos jobs e para `iap_enabled`;
       - `roles/artifactregistry.admin`;
       - `roles/iap.admin` (política de acesso do IAP);
       - `roles/iam.serviceAccountUser` só nas 3 SAs de runtime;
       - para segredos, **papel customizado** `safrionInfraSegredos`, com criar/ler metadados/atualizar/listar segredos e get/setIamPolicy, **sem `secretmanager.versions.access`**. O papel pronto `secretmanager.admin` lê o valor dos segredos, e por isso fica de fora;
     - **IAM do projeto fica no bootstrap:** `cloudsql.client` das SAs de runtime e do operador, `logging.viewer` e os papéis da `sa-agentes-leitura` são aplicados pelo dono, uma vez. Assim, `sa-infra-github` não precisa de `resourcemanager.projectIamAdmin`, que lhe permitiria se dar Owner;
     - **nunca Owner nem Editor para SA de CI.** Mesmo assim, `sa-infra-github` é poderosa (Cloud SQL, Run, segredos sem valor). A compensação: revisor humano no environment, plan aprovado por hash e `prevent_destroy`/`deletion_protection` nos recursos críticos;
     - **aceite futuro:** init, plan e apply autenticados com esse principal; tentativa com outra ref ou outro workflow negada; nenhuma saída de plan ou apply com valor de segredo;
     - **alternativa, se o time preferir menos privilégio parado:** aplicar também o `infra/terraform/hml` localmente, na janela de sessão do dono, sem SA de infraestrutura. O custo é abrir uma janela de sessão a cada mudança de infraestrutura.
   - **Aprovação do plan:**
     - `terraform plan -out` revisado (fmt, validate, TFLint, scanner);
     - o plan fica fora do Git; na rodada vão só o hash e a contagem add/change/destroy;
     - o time aprova o plan por esse hash, com veto do Adrianus;
     - o apply usa só esse arquivo;
     - plan com `destroy` ou `must be replaced` em Cloud SQL, bucket do state, segredos ou pool WIF é recusado e volta como plano específico (PRD 28.2).
   - **Revogação ao final, pelo wrapper `safrion-gcloud`:** `auth revoke --all` e `auth application-default revoke`.
     - Prova no canal: `safrion-gcloud auth list` sem conta e ausência dos dois arquivos ADC (`/Users/adrianussanders/.config/safrion-gcloud/application_default_credentials.json` e `~/.config/gcloud/application_default_credentials.json`).
     - Para o Terraform, preferir `GOOGLE_OAUTH_ACCESS_TOKEN` de vida curta emitido pelo wrapper, sem gravar arquivo ADC.
     - A partir daí, os agentes usam só a conta própria, por personificação.
   - **3b. Adrianus, no console, depois do bootstrap:** gerar um novo segredo no cliente OAuth e colá-lo direto no Secret Manager como versão de `hml-oidc-client-secret`. Não enviar a ninguém nem ao chat; se baixar o JSON, apagá-lo. O agente só confere que a versão existe.
4. **Senhas, pelo agente no fim do passo 3, sem ver o valor.** Cada senha nasce e é gravada num só comando, sem eco e sem argumento:
   `P=$(openssl rand -hex 16); printf %s "$P" | gcloud secrets versions add hml-db-admin-senha --data-file=- >/dev/null; printf '%s\n' "$P" | gcloud sql users set-password postgres --instance=safrion-hml --prompt-for-password; unset P`.
   - Para `migrator` e `app_runtime`, só o `versions add`, porque o job de preparo cria os papéis.
   - Proibido na sessão do agente: `gcloud secrets versions access`, `--password=`, `set -x` e eco de variável de senha. A conferência é só pelo número da versão.
   - **Não verificado:** se `--prompt-for-password` lê a entrada padrão sem terminal; ensaiar antes. Se não ler, usar `password_wo` no `google_sql_user`, com valor efêmero (Terraform ≥ 1.11; suporte do provider não verificado).
5. **GitHub (Adrianus, administrador):**
   - environment `hml` restrito a `main`, **com o Adrianus como único revisor**. Os agentes usam a mesma conta `adrptu` e nunca aprovam; a conta GitHub própria dos agentes resolve isso;
   - variáveis `GCP_PROJECT_ID`, `GCP_REGION`, `WIF_PROVIDER` e `DEPLOY_SA`;
   - **sem environment com revisor, o pipeline não publica na HML** até existir a proteção do `main` (PEND-REPO-01), com PR revisado por quem não é o autor. Nesse caso, a condição do WIF perde só `environment` e mantém `workflow_ref` e `event_name`.
6. **1ª subida, com aprovação no environment:**
   - publicar as imagens → job `safrion-preparo` → job `safrion-demo-reset` → publicar a web;
   - **provas:**
     - `/saude` com `ok`, `hml`, commit e **digest** publicados;
     - com a credencial publicada: `SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user` = f/f, a consulta A5 e o AC-04 repetido;
     - a faixa ou selo "Homologação" em todas as telas;
     - o login.
   - **Só F0 e vínculo no ar é infraestrutura pronta, não homologação:** nenhum link vai ao Adrianus como candidata antes do ensaio do Codex (R-006 passo 16).
7. **Acesso de cada testador:**
   - a pessoa entra e passa o código;
   - o **operador humano (o Adrianus, nunca um agente)** confirma quem é por canal independente e roda `vincular-identidade conceder` da máquina dele, pelo Auth Proxy;
   - **repetir depois de cada `demo-reset`**, que revoga os acessos reais à geração anterior.

### Lacunas que precisam de decisão ou código antes ou durante a 1ª subida

- **(código, autor Claude, revisor Codex; R-006 passo 11)** `infra/terraform/bootstrap` (bucket do state, APIs, WIF, SAs) e `infra/terraform/hml` (Cloud Run web e jobs, Cloud SQL, segredos sem valor, Artifact Registry), mais a ADR curta da região southamerica-east1. Aceite: fmt, validate, TFLint e scanner sem achado alto, rodados localmente. Hoje não existe nenhum arquivo `infra/` nem `.tf`.
- **Publicação e infraestrutura pela CI inexistentes.** Estão por fazer o `publicar-hml.yml`, o `infra-hml.yml` e o manifesto da publicação (ENG-060). Hoje a imagem varrida é descartada.
- **O operador não tinha como saber o `--usuario` a conceder.** Resolvido em `fd57a94` (`feat/demo-reset-ids`): o `demo:reset` imprime a organização e os ids fictícios por papel, e o `OPERACAO.md` indica o log do job.
- **Vínculo pela máquina do operador × PRD 31.7 e o passo 12 (revogar a sessão depois do bootstrap).** Cada concessão exige sessão gcloud ativa (Auth Proxy e acesso ao segredo). Opções: login e revogação a cada concessão, com roteiro de um comando; autenticação IAM do Cloud SQL, sem senha; ou exceção explícita registrada.
- **URL controlada (PRD 27.4; plano passo 11).**
  - **Padrão proposto:** IAP direto no Cloud Run com lista de permitidos, sem `allUsers`. O IAP direto **funciona em projeto sem organização** (F43, confirmado pelo Codex em 28/09).
    - Liga-se com `iap_enabled = true` no `google_cloud_run_v2_service`, mais `roles/run.invoker` para o agente de serviço do IAP (`service-<NUM>@gcp-sa-iap.iam.gserviceaccount.com`) e a API `iap.googleapis.com`.
    - Acesso de pessoas: `roles/iap.httpsResourceAccessor` no serviço, para cada testador e para a identidade do teste de `/saude`.
    - **Em projeto sem organização, a 1ª ativação é pelo console**, com cliente OAuth customizado, porque cliente OAuth não se cria por programa (F43). O redirect do cliente do IAP é `https://iap.googleapis.com/v1/oauth/clientIds/<CLIENT_ID>:handleRedirect`. É mais um ato do Adrianus na lista de execução. Só depois o Terraform mantém a configuração e a lista.
    - Com IAP, a pessoa passa por dois logins Google: o do IAP e o do Safrion, que cria o pedido de acesso. Na HML isso é aceitável. O teste de `/saude` da publicação precisa de identidade com acesso ao IAP (não verificado como obter o token na CI).
    - Custo do IAP direto: **não verificado** na página de preços.
    - Não se decide domínio nem balanceador enquanto o caminho direto não for comprovado inviável.
  - Ingress público só com exceção ENG-005 aprovada:
    - escopo: `/entrar` e o pedido de acesso;
    - risco: qualquer conta Google cria pedido e gera tráfego pago;
    - compensação: `allUsers` só na web, máximo 2 instâncias, teto nativo de gasto do Cloud Run ligado, cota de pedidos e nenhum dado exibido antes do vínculo;
    - vencimento: antes do piloto.
  - Com o máximo de 2 instâncias ocupadas o mês todo, CPU e memória dariam cerca de US$ 186/mês, antes da franquia (especificado: 2 × 2.628.000 s × US$ 0,0000336 + 2 × 0,5 × 2.628.000 × US$ 0,0000035). O orçamento só avisa.
- **Identidade para testar o login e ensaiar a tarefa.** O primeiro login real é do Adrianus. O ensaio do Codex usa uma conta de teste criada por ele, porque agente não cria conta nem digita senha.
- **Migração usa a senha do administrador do banco.** Aceitável na HML, com a `sa-preparo` isolada. Antes do piloto, um comando `migrar` só com o `migrator`.
- **Faixa HOMOLOGAÇÃO.** A casca já mostra um selo permanente do ambiente no cabeçalho (`(app)/layout.tsx`, a partir da identidade do banco). Conferir se atende "todas as telas", inclusive `/entrar` e erros (PRD:5495).
- **Rotação de senha:** o procedimento está resumido na linha Segredos; falta escrevê-lo em `OPERACAO.md` antes da 1ª troca.

### Correções ao texto de 27/09 abaixo

- os alertas passam de 50/90/100 para **70/90/100** (PRD 28.4);
- "teto" significa **orçamento de alerta, que não limita gasto**;
- o piloto econômico com reserva de 10 dá **US$ 116,85**; 111,85 é com reserva de 5;
- 16,32 × 5,1991 = R$ 84,85, não 84,87;
- o "job worker" não existe na F1: o único job de migração é o `preparo` (PRD:5470);
- a conta Google e o faturamento já existem: não há "criar conta" nem crédito de US$ 300 garantido;
- DNS e subdomínio **não são necessários na HML** (URL do Cloud Run).

## Recomendação curta

| Ambiente                                 | Escolha                                                                                                                                         | US$/mês      | R$/mês (PTAX) | R$/mês com IOF |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------- | -------------- |
| **HML**                                  | Google Cloud `southamerica-east1`: Cloud Run (web, mínimo 0) + Cloud Run Job (worker) + Cloud SQL `db-f1-micro` com PostGIS, sem HA, com backup | **≈ 16,32**  | ≈ 84,87       | ≈ 87,84        |
| **Piloto (conforme PRD)**                | Mesmo desenho em projeto separado; Cloud SQL Enterprise **HA** 1 vCPU/3,75 GiB; web com 1 instância mínima                                      | **≈ 183,13** | ≈ 952,12      | ≈ 985,44       |
| Piloto econômico (exige aceite de risco) | Igual, mas Cloud SQL **HA `db-g1-small`** (núcleo compartilhado, fora do SLA do Cloud SQL)                                                      | ≈ 111,85     | ≈ 581,50      | ≈ 601,86       |

Por quê: é a topologia de referência do PRD (§28.1); tem região em São Paulo (LGPD); PostGIS suportado; backup gerenciado; roda contêiner comum, então a mesma imagem por digest vai de HML para produção sem migrar de provedor. A conta nova tem crédito de US$ 300 por 90 dias (verificado, F13), mas a elegibilidade da conta do proprietário não foi verificada.

Plano B só para HML, se o proprietário preferir o menor custo e aceitar registrar em ADR o desvio da §28.1: **Fly.io `gru` (web + worker) + Neon `aws-sa-east-1` Free** ≈ **US$ 7,85/mês** (R$ 40,82; R$ 42,25 com IOF). Tudo em São Paulo, com PostGIS.

## Tabela comparativa (US$ por mês; detalhes das contas na seção seguinte)

| Opção                             | Região no Brasil                                              | HML mínima                                  | Piloto                                                         | Camada grátis e limites reais                                                                                                                                            | PostGIS                                                        | Backup e restauração                                                                             | Operação                                        | Lock-in                                                    | Cartão                           |
| --------------------------------- | ------------------------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------- | ---------------------------------------------------------- | -------------------------------- |
| **Google Cloud Run + Cloud SQL**  | Sim, `southamerica-east1` (F12, F13b)                         | ≈ 16,32 (esp.)                              | ≈ 183,13 com HA dedicado; ≈ 111,85 com HA compartilhado (esp.) | Cloud Run: 180 mil vCPU-s, 360 mil GiB-s e 2 milhões de requisições por mês; crédito de US$ 300/90 dias; Cloud SQL tem instância de teste de 30 dias; depois paga (ver.) | Sim, todas as versões (F14)                                    | Automático, retenção de 1 dia a 10 anos conforme opção (ver., F15); PITR em dias: não verificado | Média: IAM, projetos, Terraform                 | Baixo no app (contêiner); médio no banco (Postgres padrão) | Sim (ver., F13)                  |
| **Fly.io + Fly Managed Postgres** | Sim, `gru`, e o MPG roda em `gru` (F4)                        | ≈ 46,13 (esp.)                              | ≈ 53,38 com HA incluso (esp.)                                  | Só teste: 2 h de máquina ou 7 dias (ver., F5)                                                                                                                            | Sim, ao criar o cluster (F3b)                                  | "Backups automáticos e recuperação"; frequência e retenção não verificadas                       | Baixa                                           | Baixo (contêiner + Postgres)                               | Sim, toda organização (ver., F3) |
| **Fly.io + Neon**                 | Sim, `gru` + `aws-sa-east-1` (F4, F7)                         | ≈ 7,85 (esp.)                               | ≈ 22,82 a 32,63 (esp.)                                         | Neon Free: 0,5 GB, 100 CU-h por projeto, dorme após 5 min, restauração de 6 h, sem cartão (ver., F6)                                                                     | Sim (F8)                                                       | Neon Launch: restauração até 7 dias (ver.)                                                       | Baixa                                           | Baixo                                                      | Fly sim; Neon não                |
| **Vercel + Neon ou Supabase**     | Sim: Vercel `gru1`, Neon e Supabase `sa-east-1` (F9, F7, F11) | ≈ 0 + worker fora (esp.)                    | ≈ 45 + worker fora (Vercel Pro 20 + Supabase Pro 25)           | Vercel Hobby só uso pessoal, não comercial, cron no máximo 1 vez por dia; Supabase Free pausa após 1 semana sem uso, sem backup (ver.)                                   | Sim (Neon F8, Supabase F11b)                                   | Supabase Pro: backup diário por 7 dias; PITR US$ 100/mês por 7 dias (ver.)                       | Média: worker precisa de outro lugar            | Médio a alto (Vercel não publica imagem por digest)        | Não verificado                   |
| **Render**                        | Não: EUA, Frankfurt, Singapura (F16)                          | ≈ 20,30 (esp.)                              | ≈ 36 (esp.)                                                    | Web grátis dorme após 15 min, 750 h; Postgres grátis expira em 30 dias, sem backup; worker não tem grátis (ver., F17)                                                    | Sim (F18)                                                      | PITR 3 dias no Hobby, 7 no Pro de US$ 25 (ver., F19)                                             | Baixa                                           | Baixo                                                      | Não verificado                   |
| **Railway**                       | Não: EUA, Amsterdã, Singapura (F21)                           | ≈ 8,15 (esp.)                               | ≈ 15 a 25 (esp., uso)                                          | Teste de US$ 5 por 30 dias, sem cartão; plano grátis com US$ 1/mês (ver., F20)                                                                                           | Só por modelo da comunidade, não gerenciado (F22)              | Backup de volume: diário por 6 dias, semanal por 27, mensal por 89 (ver., F23)                   | Baixa a média                                   | Baixo                                                      | Teste não                        |
| **AWS Lightsail**                 | Sim, São Paulo, com metade da franquia de tráfego (F24)       | ≈ 13 (esp.): VPS de 2 GB com tudo em Docker | ≈ 28 (esp.) se o banco gerenciado aceitar PostGIS              | "Comece grátis" pelo Free Tier; prazo e planos não verificados                                                                                                           | Banco gerenciado: não verificado; na VPS, sim (autogerido)     | Snapshot automático diário, guarda os 7 últimos (ver., F25)                                      | Alta na VPS (atualização, TLS, backup do banco) | Baixo                                                      | Não verificado                   |
| **DigitalOcean**                  | Não: América do Norte, Europa, Ásia, Austrália (F28)          | ≈ 17 (esp.)                                 | ≈ 25,15 (esp.)                                                 | Só 3 sites estáticos grátis (ver., F27)                                                                                                                                  | Sim no banco gerenciado (F29); no banco de dev, não verificado | Detalhes de backup não verificados                                                               | Baixa                                           | Baixo                                                      | Não verificado                   |
| **Hetzner (VPS + Docker)**        | Não: Alemanha, Finlândia, EUA, Singapura (F30)                | ≈ 8,39 (esp.)                               | ≈ 16,78 (esp.)                                                 | Não há                                                                                                                                                                   | Sim, autogerido                                                | Backup do servidor: +20% do preço (ver., F31)                                                    | Alta                                            | Baixo                                                      | Não verificado                   |

Leitura da tabela: "esp." quer dizer que o total é uma conta minha feita com preços verificados; os preços unitários estão abaixo e nas fontes. Mês = 730 h = 2.628.000 s.

## Contas (preços unitários verificados; quantidades especificadas)

**HML recomendada — Google Cloud, São Paulo** (preços lidos em F12 e F13b com o seletor de região em _Sao Paulo (southamerica-east1)_)

- Cloud SQL `db-f1-micro` (0,6 GiB, núcleo compartilhado): US$ 0,0158/h × 730 = **11,53**.
- Disco SSD de 10 GiB (esp.): US$ 0,000349315 por GiB-h × 730 = 0,255 por GiB → **2,55**.
- Backup usado de 2 GiB (esp.): US$ 0,000164384 por GiB-h × 730 = 0,12 por GiB → **0,24**.
- Cloud Run web e job: tarifa de São Paulo é "Tier 2" (F12): CPU ativa US$ 0,0000336 por vCPU-s e memória US$ 0,0000035 por GiB-s; job US$ 0,0000216 por vCPU-s. Com 20 h de uso por mês (1 vCPU, 0,5 GiB) dá cerca de US$ 2,55, abaixo da franquia grátis (aplicada como desconto a preço Tier 1, cerca de US$ 5,22) → **0** (esp.).
- Reserva para Cloud Storage, registro de imagens, segredos e tráfego: **2,00** (esp.; preços não verificados).
- **Total ≈ US$ 16,32** → R$ 84,87 (PTAX) → **R$ 87,84 com IOF**.

**Piloto conforme PRD — Google Cloud, São Paulo**

- Cloud SQL Enterprise HA, 1 vCPU e 3,75 GiB: (US$ 0,1239 + 3,75 × 0,021)/h × 730 = **147,93**.
- Disco SSD HA de 20 GiB (esp.): US$ 0,00069863 por GiB-h × 730 = 0,51 por GiB → **10,20**. Backup usado de 10 GiB (esp.): **1,20**.
- Web com 1 instância sempre ligada, 1 vCPU e 0,5 GiB, cobrada como ociosa: (0,0000035 + 0,5 × 0,0000035) × 2.628.000 = **13,80**.
- Worker como job (esp.): **5,00**. Reserva de armazenamento, tráfego e monitoramento (esp.): **5,00**.
- **Total ≈ US$ 183,13** → R$ 952,12 → **R$ 985,44 com IOF**.
- Versão econômica: trocar o banco por HA `db-g1-small` (US$ 0,105/h × 730 = 76,65), mantendo a reserva em 5 → **≈ US$ 111,85** (R$ 601,86 com IOF); com reserva de 10, ≈ US$ 116,85 (correção de 28/09). Sem HA (`db-g1-small` a 0,0525/h = 38,33) → ≈ US$ 68,42 (R$ 368,18 com IOF), mas contraria a §28.1 do PRD.

**Plano B — Fly.io `gru` + Neon São Paulo** (F3, F6)

- Preço base do Fly × acréscimo de São Paulo 1,615384615: web `shared-cpu-1x` 512 MB = 2,92 × 1,615 = **4,72**; worker 256 MB = 1,94 × 1,615 = **3,13**; Neon Free = **0**. Total **≈ US$ 7,85** (R$ 42,25 com IOF).
- No piloto: web 1 GB (7,87) + worker (4,72) + Neon Launch a US$ 0,106 por CU-h, 0,25 CU por 360 a 730 h, mais 2 GB a US$ 0,35 = 10,24 a 20,04 → **≈ US$ 22,82 a 32,63**. Neon não tem HA de computação por padrão (não verificado).
- Com Fly Managed Postgres Basic (US$ 38, HA incluso) + 1 a 10 GB a US$ 0,28: HML ≈ 46,13, piloto ≈ 53,38. Se o acréscimo de São Paulo também vale para o MPG: não verificado.

**Demais (esp., com preços de F17 a F31)**

- Render (Hobby US$ 0 + uso): web Starter 7 + worker Starter 7 + Postgres 256 MB 6 + 1 GB a 0,30 = 20,30; piloto com Postgres de 1 GB (19) e 10 GB = 36,00.
- Railway Hobby (US$ 5 com US$ 5 de uso incluso): 0,6 GB de RAM a 10 + 0,1 vCPU média a 20 + 1 GB de volume a 0,15 = 8,15.
- Lightsail: VPS de US$ 12 (2 GB) + cerca de 20 GB de snapshot a 0,05 = 13; piloto + banco gerenciado de 1 GB a 15 = 28.
- DigitalOcean: app de 5 + worker de 5 + banco de dev de 7 = 17; piloto com Postgres gerenciado de 15,15 = 25,15.
- Hetzner (Alemanha): CX23 6,49 + IPv4 0,60 + backup de 20% (1,30) = 8,39; piloto com 2 servidores = 16,78.

## Riscos

1. **Crédito e franquia não são teto.** Crédito de 90 dias acaba e a conta passa a cobrar. **Verificado em 28/09:** orçamento só de alerta não limita uso nem gasto; o teto nativo de gasto só cobre Cloud Run, Cloud Run functions, Gemini API e Vertex, não o Cloud SQL (https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps). Por isso o gasto precisa ser vigiado.
2. **Núcleo compartilhado não tem SLA.** `db-f1-micro` e `db-g1-small` "não são cobertos pelo SLA do Cloud SQL" (F13b). Isso é aceitável em HML, mas é um risco no piloto econômico.
3. **Cold start.** Web com mínimo 0 (HML) e Neon Free (dorme após 5 min) atrasam o primeiro acesso. Aceitável em teste; no piloto use 1 instância mínima.
4. **Câmbio e IOF.** Custo em dólar e cobrado no cartão: cada US$ 10 a mais de uso custa cerca de R$ 54 com IOF (5,3811 por US$). O spread do banco não foi verificado.
5. **LGPD no piloto.** Render, Railway, DigitalOcean e Hetzner não têm região no Brasil: dado de cliente sairia do país (transferência internacional). As regras exatas da ANPD não foram verificadas aqui. Só GCP, Fly, Neon, Supabase, Vercel e Lightsail ficam em São Paulo.
6. **Termos de uso.** Vercel Hobby é "pessoal, não comercial" (F10). Não serve para um produto comercial, nem para a HML dele.
7. **Desvio de arquitetura.** Qualquer opção fora do GCP exige ADR que altere a §28.1 do PRD. O plano B economiza cerca de US$ 8/mês na HML, mas pode obrigar a migrar antes do piloto.
8. **Protótipo não é homologação.** Hospedagem é pré-requisito, não entrega. Pela §27.4 a HML só recebe uma candidata identificada por commit e imagem (digest), com dados fictícios. Hoje o `docs/STATUS.md` registra código de produto "Nenhum": sem backend, banco, integração nem implantação.

## O que o proprietário precisa autorizar (e fazer ele mesmo)

1. **Conta.** Criar a conta Google Cloud no nome dele, com ele como dono da conta de faturamento. Agentes não criam conta nem aceitam termos.
2. **Cartão.** Cadastrar o cartão pessoalmente. O Google exige meio de pagamento válido mesmo no teste (F13). Agentes não digitam dados de cartão.
3. **Orçamento de alerta da HML:** **US$ 25/mês (≈ R$ 135 com IOF)**, com alertas em **70%, 90% e 100%** (correção de 28/09, PRD 28.4). Orçamento avisa, não limita gasto. Estimativa atualizada: US$ 15,40 (ver a atualização de 28/09).
4. **Separação.** Um projeto `hml` agora. O projeto `prod` fica para quando o piloto for aprovado (§27.4). Nada de dado real na HML.
5. **Subdomínio.** Indicar o domínio e autorizar um registro DNS do tipo `hml.<domínio>`. Se já existe domínio: não verificado.
6. **Acesso técnico mínimo.** Autorizar uma identidade de serviço para o pipeline publicar na HML, sem acesso a produção, via OIDC do GitHub (conforme o PRD).
7. **Piloto, decisão separada e posterior:** escolher entre ≈ US$ 183/mês (HA dedicado, conforme o PRD) e ≈ US$ 112/mês (HA compartilhado, sem SLA). Teto sugerido: US$ 220 ou US$ 135/mês.

Próximo passo mínimo, sem chamar protótipo de homologação: com as autorizações 1 a 3 feitas, criar o projeto `hml` e o banco com PostGIS por Terraform. Quando a F0 tiver CI verde, publicar a primeira imagem por digest com uma página de saúde que mostre versão, commit e ambiente "HOMOLOGAÇÃO". Só a primeira fatia funcional da F1 vira candidata a teste do proprietário.

## Suposições

- Uso da HML: poucos testadores, cerca de 20 h de acesso por mês, banco abaixo de 2 GB e dados fictícios. O worker roda como job sob demanda.
- Tamanhos: 10 GiB de disco na HML e 20 GiB no piloto. O menor disco permitido pelo Cloud SQL não foi verificado.
- Nos provedores fora do GCP, preço de região = preço base, exceto o acréscimo verificado do Fly em `gru`.

## Fontes (todas acessadas em 27/09/2026)

- F1 PTAX: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='09-21-2026'&@dataFinalCotacao='09-27-2026'&$format=json (venda de 25/09/2026: 5,19910)
- F2 IOF 3,5%: https://www.gov.br/fazenda/pt-br/assuntos/noticias/2025/Maio/equipe-economica-divulga-contingenciamento-bloqueio-e-medida-para-ajuste-fiscal
- F3 Fly, preços: https://docs.fly.io/about/pricing/ (máquinas, acréscimo de `gru` de 1,615384615, volume a US$ 0,15/GB, cartão obrigatório, IPv4 dedicado a US$ 2)
- F3b Fly, Managed Postgres: https://docs.fly.io/postgres/ (Basic US$ 38, Starter US$ 72, disco a US$ 0,28/GB, PostGIS, HA)
- F4 Fly, regiões: https://docs.fly.io/reference/regions/ (`gru` marcado como região de MPG)
- F5 Fly, teste: https://docs.fly.io/about/free-trial/
- F6 Neon, preços: https://neon.com/pricing · F7 regiões: https://neon.com/docs/introduction/regions · F8 extensões: https://neon.com/docs/extensions/pg-extensions · F8b planos: https://neon.com/docs/introduction/plans
- F9 Vercel, regiões: https://vercel.com/docs/regions · F10 preços: https://vercel.com/pricing · F10b cron: https://vercel.com/docs/cron-jobs/usage-and-pricing
- F11 Supabase, regiões: https://supabase.com/docs/guides/platform/regions · F11b PostGIS: https://supabase.com/docs/guides/database/extensions/postgis · F11c preços: https://supabase.com/pricing
- F12 Cloud Run, preços: https://cloud.google.com/run/pricing (região São Paulo escolhida no seletor da página)
- F13 Google Cloud, teste e franquia: https://docs.cloud.google.com/free/docs/free-cloud-features · F13b Cloud SQL, preços: https://cloud.google.com/sql/pricing (região São Paulo escolhida no seletor)
- F14 Cloud SQL, extensões: https://docs.cloud.google.com/sql/docs/postgres/extensions · F15 backups: https://docs.cloud.google.com/sql/docs/postgres/backup-recovery/backups
- F16 Render, regiões: https://render.com/docs/regions · F17 grátis: https://render.com/docs/free · F18 extensões: https://render.com/docs/postgresql-extensions · F19 preços: https://render.com/pricing
- F20 Railway, preços: https://railway.com/pricing · F21 regiões: https://docs.railway.com/reference/deployment-regions · F22 PostGIS (modelo): https://railway.com/deploy/postgis · F23 backups: https://docs.railway.com/reference/backups
- F24 Lightsail, preços: https://aws.amazon.com/lightsail/pricing/ · F25 FAQ: https://aws.amazon.com/lightsail/faq/
- F26 DigitalOcean, banco: https://www.digitalocean.com/pricing/managed-databases · F27 App Platform: https://www.digitalocean.com/pricing/app-platform · F28 regiões: https://docs.digitalocean.com/platform/regional-availability/ · F29 extensões: https://docs.digitalocean.com/products/databases/postgresql/details/supported-extensions/
- F30 Hetzner, locais: https://www.hetzner.com/cloud/ · F31 backup a 20%: https://docs.hetzner.com/cloud/billing/faq/ · F32 preços após 15/06/2026: https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ · F33 IPv4 a € 0,50 (US$ 0,60): https://docs.hetzner.com/general/infrastructure-and-availability/ipv4-pricing/
- F34 PRD e STATUS (leitura local): `docs/PRD.md` §27.4, §28.1, §30.5, NFR-11 e NFR-24; `docs/STATUS.md`, linha 12

## Não verificado

_Em 28/09, os preços de Artifact Registry e Secret Manager e os dias de PITR foram verificados (ver "Fontes desta atualização"). O restante desta lista continua como estava em 27/09._

Se o Google Cloud bloqueia o gasto no teto · PITR do Cloud SQL em dias · menor disco do Cloud SQL · preço exato de Cloud Storage, Artifact Registry, Secret Manager e Cloud Scheduler em São Paulo · se o acréscimo de `gru` vale para o MPG do Fly · frequência e retenção de backup do MPG · diferença de preço regional do Neon e do Supabase em `sa-east-1` · cartão exigido por Render, Vercel, Supabase, AWS, DigitalOcean e Hetzner · prazo do Free Tier do Lightsail · PostGIS no banco gerenciado do Lightsail e no banco de dev da DigitalOcean · backup da DigitalOcean · regras da ANPD para transferência internacional · Magalu Cloud (a calculadora de preços em reais não carregou em https://magalu.cloud/precos/) · spread do banco no cartão.
