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

**Corrigido depois de `85d2fd2` (3ª revisão do Codex, 28/09):**
- condição canônica única do WIF, com os pares publicar/`hml` e infra/`hml-infra`, e PR sem credencial;
- risco real do principal de infraestrutura: acesso indireto aos valores, sem promessa de isolamento;
- o teto nativo derruba tarefas de job em curso e está em Preview.

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
- É um orçamento separado do alerta: vale para **um projeto e um serviço**, é mensal e **pausa todo o Cloud Run do projeto** quando o custo estimado passa do valor: o serviço passa a responder erro 5xx, **tarefas de job novas não começam e as em curso falham** (F45). Não apaga recurso nem dado (F42). O recurso está em **Preview** (termos Pre-GA), e o aceite desses termos é do Adrianus. Um `safrion-preparo` interrompido pelo teto só conta como feito com recibo confirmado; a retomada segue a idempotência do preparo e das migrações, a conferir no ensaio.
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
- F44 https://developer.hashicorp.com/terraform/language/backend/gcs (backend gcs: Storage Object Admin no bucket do state; fonte conferida pelo Codex em 28/09);
- F45 https://docs.cloud.google.com/run/docs/tips/services-cost-optimization#budget_spend_caps (teto no Cloud Run: Preview; serviço responde 5xx, tarefas de job novas não começam e as em curso falham);
- F46 https://docs.cloud.google.com/secret-manager/docs/access-control (permissões de segredo, inclusive `secrets.setIamPolicy` e `versions.access`).

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
- **Condição canônica do WIF (uma só, para os dois caminhos):**
  - mapeamento: `google.subject = assertion.sub`, `attribute.repository_id = assertion.repository_id` e `attribute.fluxo`, calculado por expressão (`'publicar'` se `workflow_ref` começa por `adrptu/Safrion-Software-/.github/workflows/publicar-hml.yml@`, `'infra'` se começa por `…/infra-hml.yml@`, senão `'outro'`);
  - `attribute_condition`: `assertion.repository_id == '<ID_REPO>' && assertion.repository_owner_id == '<ID_DONO>' && assertion.ref == 'refs/heads/main' && assertion.event_name in ['push','workflow_dispatch'] && ((attribute.fluxo == 'publicar' && assertion.environment == 'hml') || (attribute.fluxo == 'infra' && assertion.environment == 'hml-infra'))`;
  - `workloadIdentityUser`: `sa-deploy-github` ← `principalSet://…/attribute.fluxo/publicar`; `sa-infra-github` ← `principalSet://…/attribute.fluxo/infra`;
  - **aceite futuro:** os dois caminhos legítimos autenticam. Trocar a ref, o workflow ou o environment falha, inclusive `pull_request_target` e o workflow de um no environment do outro. Sem `workflow_ref` e `event_name`, qualquer workflow com ref `main` receberia a SA. O nome exato da função de expressão no mapeamento fica a conferir no 1º plan;
  - **PR não autentica:** no PR rodam só checagens estáticas sem credencial (`terraform fmt -check`, `terraform init -backend=false` seguido de `terraform validate`, TFLint, scanner). Plan e apply autenticados só em `main`, no environment revisado. A SA de aplicação nunca fica acessível a PR.
- `sa-deploy-github`: `artifactregistry.writer` no repositório, `run.developer` nos 3 recursos, `iam.serviceAccountUser` nas 3 SAs de runtime. **Atenção:** na prática, ela soma o poder das SAs de runtime, inclusive a senha do `postgres` via `sa-preparo`. A página de segredos cita `run.admin` para configurá-los: confirmar no 1º plan se `run.developer` basta para trocar a versão do segredo, sem ampliar o papel antes de testar;
- `sa-infra-github`: aplica o `infra/terraform/hml` pela CI, com as permissões da divisão do R-006 no passo 3; `workloadIdentityUser` só para `attribute.fluxo/infra` (condição canônica acima);
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
     - **`sa-infra-github`**, usada só pelo workflow `infra-hml.yml`: checagens estáticas sem credencial em PR; plan e apply autenticados só em `main`, no environment `hml-infra`, com o Adrianus como único revisor. O WIF segue a condição canônica da seção de identidades, com os pares publicar/`hml` e infra/`hml-infra`. Outra ref, outro workflow ou outro environment não recebe nenhuma das duas SAs;
     - **state:** `roles/storage.objectAdmin` **só no bucket do state** para `sa-infra-github` (backend gcs, F44). O "acesso só do dono" do bucket vira dono + `sa-infra-github`;
     - **o que ela cria na HML:**
       - `roles/cloudsql.admin`;
       - `roles/run.admin`, necessário para política de IAM do serviço e dos jobs e para `iap_enabled`;
       - `roles/artifactregistry.admin`;
       - `roles/iap.admin` (política de acesso do IAP);
       - `roles/iam.serviceAccountUser` só nas 3 SAs de runtime;
       - para segredos, **papel customizado** `safrionInfraSegredos`, com criar/ler metadados/atualizar/listar segredos e get/setIamPolicy, sem `secretmanager.versions.access` direto. **Isso não isola o valor** (F46): com `setIamPolicy`, ela pode se dar acesso ao valor; com `run.admin` e `actAs` nas SAs de runtime, pode rodar código como elas, e elas leem os segredos. O papel customizado só evita a leitura direta por engano. **Na prática, o principal de infraestrutura tem acesso efetivo aos valores**;
     - **IAM do projeto fica no bootstrap:** `cloudsql.client` das SAs de runtime e do operador, `logging.viewer` e os papéis da `sa-agentes-leitura` são aplicados pelo dono, uma vez. Assim, `sa-infra-github` não precisa de `resourcemanager.projectIamAdmin`, que lhe permitiria se dar Owner;
     - **nunca Owner nem Editor para SA de CI.** Mesmo assim, `sa-infra-github` é poderosa: Cloud SQL, Run e, por via indireta, os valores dos segredos. **Não prometemos isolamento de valores.** A compensação:
       - revisão protegida do workflow e do plan, com revisor humano no environment e plan aprovado por hash;
       - nenhuma impressão de segredo em log, plan ou saída;
       - `prevent_destroy`/`deletion_protection` nos recursos críticos;
       - trilha de auditoria do IAM;
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
   - **sem environment com revisor, nenhum dos dois caminhos autenticados é ligado** (publicar e infra). A HML espera a proteção do `main` (PEND-REPO-01) e os environments `hml` e `hml-infra`, cada um com o Adrianus como revisor. Não há condição do WIF sem `environment`.
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

### GCP-0017: IP privado × concessão fora da máquina do operador (comparação pedida pelo Codex; proposta, não aceita)

*Análise de 28/09/2026, revisada no mesmo dia por verificação adversarial. Fontes: documentação oficial e o repositório. Nenhum recurso foi provisionado e nenhum dado real foi usado. As fontes G1 a G38 estão no fim da seção, com numeração própria dela.*

#### 1) Resumo

O GCP-0017 tem duas regras: IP público ligado e rede autorizada com CIDR público [G1]. O Trivy trata o `ipv4_enabled` ausente ou não resolvido como `true` [G2]. Por isso, o achado só fecha com `ipv4_enabled = false` literal e sem `authorized_networks`. Mudar só o fluxo da concessão (job ou Studio com IP público) não fecha o achado.

Um caminho privado é obrigatório. Entre as duas formas:
- o PSA não cobra pela conexão [G6];
- o endpoint do Private Service Connect cobra US$ 0,01/h [G6], cerca de 7,30 por mês.

Sem IP público, o Auth Proxy do notebook perde o caminho até o banco [G13, G5], e a concessão passa para um job.

**Recomendação:**
- **Rede:** IP privado com PSA (faixa RFC 1918 explícita) e Direct VPC egress `PRIVATE_RANGES_ONLY` na web e nos jobs.
- **Conexão ao banco:** conector Node.js com `ipType PRIVATE`, para manter `connector_enforcement = REQUIRED` [G11, G12].
- **Concessão:** job `safrion-vinculo`, executado sem overrides. O pedido, com o código, entra por uma versão de uso único de um segredo sem destruição adiada, montada como arquivo.
- **Ordem:** a rede precisa existir antes da 1ª criação da instância. Ligar o IP privado numa instância existente a reinicia e não aceita faixa nomeada [G33]. Hoje nada está provisionado (R-006).

**Custo e esforço:** de US$ 0,00 a 0,11 por mês sobre a base de US$ 15,22. O GCP-0017 deixa de bloquear sem manutenção recorrente relevante. O gate só fica verde quando a exceção do GCP-0015, outro HIGH, também for aprovada (`hml/README.md`). O trabalho pontual é:
- cerca de 12 recursos;
- conector no `packages/db`;
- modo arquivo no CLI;
- emenda ao ADR 0004 §11;
- caminho novo para a rotação de senhas;
- o procedimento da conta padrão do Compute.

#### 2) Opções

| Opção | Resolve GCP-0017? | Desenho mínimo (recursos novos) | Custo incremental US$/mês | Permissões novas | Fluxo do operador | Manutenção extra | Riscos |
|---|---|---|---|---|---|---|---|
| **A. IP privado + job de vínculo (recomendada)** | **Sim**, com `ipv4_enabled = false` literal e sem `authorized_networks` [G1, G2]. Surgem só achados abaixo do gate `HIGH,CRITICAL` (`ci.yml`, linhas 52 e 61): GCP-0076 (MEDIUM) [G3] e GCP-0029 (LOW) [G32]. O GCP-0075 (LOW) fecha com `private_ip_google_access = true` [G31]. O GCP-0015 segue à parte | **Bootstrap:** APIs `compute` e `servicenetworking` [G4]; rede custom; sub-rede RFC 1918; faixa PSA com `address` RFC 1918 explícito; conexão PSA.<br>**hml/:** `vpc_access` na web e nos 2 jobs; job `safrion-vinculo`; segredo `hml-vinculo-pedido` sem `version_destroy_ttl`; 2 vínculos IAM no segredo (os do job vêm de `local.jobs`).<br>Cerca de 12 recursos. Sem NAT, conector VPC, regra de firewall, bastion ou VPN | **Conexão PSA:** 0 [G6]<br>**IPs internos:** 0 [G6]<br>**Direct VPC:** só tráfego [G8]. Cloud Run → Cloud SQL é cobrado como VM para VM: mesma zona 0, outra zona 0,01/GiB [G9, G6]. Cloud SQL → Cloud Run na mesma região: 0 [G25]. Com 1 a 5 GiB (volume estimado, teto), 0,00 a 0,05<br>**Job:** segundos, dentro da franquia: 0<br>**Segredo:** cobrança proporcional [G21]; a versão destruída na hora custa perto de 0; no pior caso, 1 versão esquecida acima das 6 grátis custa 0,06<br>**Rede e sub-rede:** nenhum SKU achado; não verificado<br>**Total:** 0,00 a 0,11 | **Dono:** aplica a rede no bootstrap. A CI não ganha `compute.networkAdmin` [G4]<br>**Operador:** `run.invoker` só no job, automático por `local.jobs` (basta para o gcloud [G15]); `secretVersionManager` só no segredo novo, que grava e destrói sem ler o valor [G19]<br>**`sa-preparo`:** `secretAccessor` só no segredo novo<br>**Agente do Cloud Run:** nada, porque o `run.serviceAgent` já cobre [G7]<br>**`sa-deploy-github`:** nada previsto (não verificado) | Confirmar o pedido → gravar a versão pela entrada padrão → executar o job sem overrides → ler o resultado no Logging → destruir a versão. Sem checkout, Node, Auth Proxy nem senha do admin no notebook. Ainda exige sessão autenticada por concessão (gcloud ou Cloud Shell): reduz o conflito com o PRD 31.7, não o elimina | **Pontual:** conector (dependência nova, passa pela quarentena), modo arquivo no CLI, `vpc_access`, probe, retentativa, `checar_travas.py`, textos e o procedimento da conta padrão do Compute.<br>**Recorrente:** perto de zero; 3 comandos por concessão | Conexão pode levar 1 min ou mais na subida [G7], e a subida a partir de zero fica mais lenta [G8].<br>IP privado e faixa são irreversíveis; em instância existente, ligar o IP privado reinicia e não aceita faixa [G5, G33].<br>O PSA atrapalha desmontar a rede [G27].<br>Ligar o Compute cria a conta padrão, que pode receber Editor [G37].<br>A rotação de senha fica sem caminho até ganhar subcomando no job.<br>Corrida se dois operadores gravarem ao mesmo tempo, porque o volume lê a última versão [G18] |
| **B. IP privado + Cloud SQL Studio (viável por dedução; não recomendada)** | **Formalmente sim**, pelo mesmo `ipv4_enabled = false`. Mas o Studio usa o `executeSql` [G23], que vem proibido por padrão [G22]. Ligar `ALLOW_DATA_API` abre esse acesso pela internet numa instância só de IP privado [G22], sem barreira de rede: fica só IAM mais a credencial do banco [G38]. O Trivy não olha esse campo [G2]. Contorna a política em vez de tirar o risco | A mesma rede e as mesmas mudanças de conexão da opção A: web e jobs continuam precisando do conector.<br>+ `data_api_access = ALLOW_DATA_API`.<br>+ credencial do banco: segredo regional com a senha do admin, ou usuário IAM do operador com `GRANT migrator` [G38]. Sem job | Rede igual à A. Data API: nenhum SKU achado; não verificado | **Operador:** `roles/cloudsql.studioUser` [G24], dado e retirado a cada uso, mais acesso à credencial | Colar num único script `SET ROLE migrator` e a chamada de `app.conceder_vinculo` com o SHA-256 calculado à mão. Cada execução abre uma sessão nova [G23] | Menos código: sem job e sem modo arquivo. Em troca, um ritual manual de hash e IAM a cada concessão | Código ou hash no texto SQL.<br>Um erro de sintaxe grava a consulta no `postgres.log` [G23], que os agentes leem (`logging.viewer`).<br>O script e a resposta podem passar por locais intermediários [G23].<br>Pula a normalização e as recusas do CLI.<br>Hash de código de 10 caracteres em base 32: cerca de 2^50 tentativas.<br>Não verificado se respeita `REQUIRED` |
| **C. Manter IP público + exceção (só referência)** | **Não.** O GCP-0017 continua HIGH, e a política não aceita exceção para risco real | Nenhum | 0 (base de 15,22) | Nenhuma | O atual: Auth Proxy no notebook, senha do admin local, checkout e Node 24.21 | Renovar a exceção a cada 30 dias no máximo (opção 2 do README), com aprovação ENG-005 | Endpoint público, mitigado por zero redes autorizadas, `REQUIRED` e `ENCRYPTED_ONLY`.<br>O Terraform fica fora do `main`.<br>O conflito com o PRD 31.7 (sessão gcloud por concessão) continua |

#### 3) Desenho mínimo da concessão (opção A)

**Configuração, feita uma vez:**
- **Job `safrion-vinculo`:**
  - imagem `preparo` pelo mesmo digest do pipeline; entra em `local.jobs`, o que já dá `run.developer` à CI e `run.invoker` ao operador;
  - `command node` e args fixos: `dist/cli/vincular-identidade.js --ambiente hml --banco safrion_hml`;
  - `task_count 1`, `max_retries 0`, timeout de 600 s;
  - `vpc_access` com `PRIVATE_RANGES_ONLY`;
  - conta `sa-preparo`. Ela já tem `cloudsql.client` e lê `hml-db-admin-senha`, então o raio de dano não cresce;
  - variáveis de ambiente: nome de conexão da instância, `PGPASSWORD` de `hml-db-admin-senha` em versão fixa (F40) e `SAFRION_PEDIDO_ARQUIVO=/run/segredos/vinculo/pedido`;
  - volume do segredo `hml-vinculo-pedido` na versão `latest`. É exceção registrada à F40, porque o volume lê a versão atual a cada leitura [G18]. O volume não é conferido na subida, e a leitura falha se não houver versão acessível [G18]; o CLI trata isso como recusa.
- **Segredo `hml-vinculo-pedido`:**
  - replicação em southamerica-east1;
  - **sem `version_destroy_ttl`**, diferente dos 4 segredos atuais. Com o atraso, destruir só desativaria a versão, e o pedido com o código seguiria recuperável e cobrado como ativo por 7 dias [G34, G21];
  - contém o pedido inteiro em linhas `chave=valor`: ação, organização, usuário, responsável (um identificador, não o nome) e motivo, mais o código quando a ação é conceder;
  - como nada varia por execução, não há overrides.
- **Sem overrides, por quê:** os overrides trocam args e variáveis de ambiente [G15, G16]. Num job `node`, isso vira execução de código com a conta do job. Os valores ficam na Execution [G17], que o `run.viewer` lê. Por isso o operador fica só com `run.invoker`: nunca `run.developer` nem `run.jobsExecutorWithOverrides`. A execução pelo console exige `run.developer` [G15], então o operador usa o gcloud.

**Por concessão:**
1. Confirmar por canal independente quem pediu, como hoje.
2. No terminal do operador, ou no Cloud Shell, que aqui só chama APIs (o Cloud Shell só não alcança IP privado [G14]):
   - ler o código com `read -rs`: sem eco e fora do histórico;
   - montar o pedido com o `printf` do shell, que é builtin: nenhum binário é executado com o código nos argumentos;
   - mandar por pipe para `gcloud secrets versions add hml-vinculo-pedido --data-file=-`. O Google desaconselha pôr o valor na linha de comando, porque ele aparece na lista de processos [G20];
   - `unset` na variável.
3. `gcloud run jobs execute safrion-vinculo --region southamerica-east1`, sem `--args` nem `--update-env-vars`. Override exige `run.jobs.runWithOverrides` [G16], que o `run.invoker` não tem.
4. Ler no Logging o JSON do resultado: concedido, ou recusado com o código de recusa. O CLI nunca imprime o pedido.
5. `gcloud secrets versions destroy <N> --secret hml-vinculo-pedido` na hora. Sem TTL no segredo, a destruição é imediata e definitiva [G34]. Esquecer não reabre o acesso (código consumido gera `PEDIDO_CONSUMIDO`), mas deixa o texto legível para a `sa-preparo` e para o dono, e a versão continua cobrada [G21].

**Revogar:** o mesmo fluxo, com `acao=revogar` e sem código.

**Por onde o código passa:**
- terminal sem eco → pipe → API do Secret Manager → versão do segredo → arquivo montado no job → memória do CLI → hash parametrizado na consulta.

**Por onde o código não passa:**
- argumento de processo, variável de ambiente, spec da Execution, log do CLI, histórico do shell e texto SQL.

Os agentes (`run.viewer`, `logging.viewer`, `cloudsql.viewer`, sem `secretAccessor`, conforme `bootstrap/contas.tf`) veem só o nome do segredo, a execução e o resultado.

#### 3b) Contrato do job de vínculo, versão 2 (recibo durável; responde às simulações do Codex de 28/09, 21:19 e 21:31)

**Proposta; substituída em parte pela v3 (3c).** Substitui a versão 1 (`3fadd6e`), que ainda falhava em três casos das simulações do Codex:
- revogação repetida atrasada apagava uma concessão posterior;
- o commit seguido de perda de conexão soltava a trava;
- o TTL podia chamar de atrasado um pedido já aplicado.

**Princípio:** cada pedido tem **um recibo durável e único no banco, gravado na mesma transação do efeito**. Repetir o pedido devolve o recibo, **nunca reaplica**. Ordem, trava e TTL passam a ser proteções auxiliares, não a garantia.

**Banco (migração 0006, autoria Claude):**
- **Tabela `app.vinculo_pedido_recibo`:**
  - colunas: `pedido_id uuid PRIMARY KEY`, `conteudo_hash bytea` (32 bytes), `acao` (`conceder` ou `revogar`), `organization_id`, `user_id`, `resultado`, `revogados`, `versao_segredo`, `processado_em` e `database_user DEFAULT session_user`;
  - imutável, com o mesmo gatilho `impedir_alteracao` de `identity_link_event`;
  - RLS FORCE, `SELECT` só para o `migrator` e nenhum acesso para o `app_runtime`.
- **Função `app.processar_pedido_vinculo(pedido_id, conteudo_hash, acao, codigo_hash, organizacao, usuario, responsavel, motivo, criado_em, validade)`:**
  - SECURITY DEFINER, dono `app_sessao`, EXECUTE só para o `migrator`. Numa só transação:
  1. `pg_advisory_xact_lock` pela chave do pedido;
  2. **consultar o recibo primeiro**:
     - se existe com o mesmo `conteudo_hash`, devolve o resultado gravado, marcado `repetido`;
     - se existe com outro conteúdo, devolve `PEDIDO_ID_REUTILIZADO`, sem efeito;
  3. só então o TTL: `criado_em` mais antigo que a validade grava o recibo `PEDIDO_ATRASADO`, sem aplicar;
  4. aplica `conceder_vinculo` ou `revogar_vinculos` (funções atuais, com as travas de vínculo);
  5. grava o recibo com o resultado, **na mesma transação**.
  - A recusa de negócio também grava recibo e é final. A falha de infraestrutura desfaz tudo e não deixa recibo, então repetir é seguro.
- **O que as simulações do Codex dão com recibo:**
  - A(revogar), B(conceder), A repetido: o A repetido devolve o recibo de A sem revogar de novo, e **B fica**;
  - commit seguido de perda de conexão: o recibo existe, a próxima execução repete, recebe `repetido` e só então destrói a versão;
  - TTL depois de aplicado: o recibo é consultado antes do TTL e devolve o resultado real, não `PEDIDO_ATRASADO`.

**Job (CLI `vincular-identidade` em modo fila):**
- **Conexão dedicada** (um `pg.Client`, sem pool) pelo conector PRIVATE. `error` ou `end` inesperado **para a execução com código 3**. A trava de sessão `pg_try_advisory_lock` ordena execuções e, sem ela, sai `OCUPADO`. Se cair junto com a conexão, a execução já parou.
- **Fila:** para cada versão ENABLED do `hml-vinculo-pedido`, da mais antiga para a mais nova, com `versions.list`:
  1. conferir que ainda está ENABLED;
  2. ler pelo nome exato;
  3. validar o pedido (`pedido_id` UUID e campos, com as mesmas validações e a normalização do código);
  4. calcular o `conteudo_hash`: SHA-256 da forma canônica `pedido_id|acao|organizacao|usuario|responsavel|motivo|sha256(codigo)`;
  5. chamar `processar_pedido_vinculo` com o `createTime` da versão como `criado_em`;
  6. registrar no log `{pedido_id, versao, resultado, repetido}`, sem código, subject nem hash;
  7. **destruir só essa versão, com `etag`, depois do recibo confirmado.**

  Falha ao destruir para a fila com código 3. O recibo já existe, e a próxima execução repete e destrói.
- **Sem dependência nova:** REST do Secret Manager com o token do servidor de metadados, por `fetch` (a verificar no ensaio).
- **Permissões, só neste segredo:** operador com `secretVersionAdder` e `run.invoker` no job; `sa-preparo` com `secretAccessor` e `secretVersionManager`. Papéis conferidos na página de controle de acesso do Secret Manager.

**Limites conhecidos:**
- `conteudo_hash` contém o hash do código, que tem cerca de 2^50 possibilidades. Isso fica só na tabela lida pelo `migrator`, e o pedido de acesso vence em 24 h e é consumido.
- A ordem entre pedidos diferentes vale por execução serializada. Com recibo, a perda da trava não reaplica nada, mas dois pedidos diferentes feitos em execuções simultâneas seguem a ordem em que cada um entrou na transação.

**Contribuição do Gemini, desde o desenho (protocolo de 28/09):**
- **o quê:** um conjunto determinístico de cenários com entrada e resultado esperado, cobrindo sequências de pedidos, repetição, perda de conexão depois do commit, execuções simultâneas, TTL, `pedido_id` reutilizado com outro conteúdo e destruição que falha;
- **em que arquivo:** `packages/db/test/fixtures/vinculo-fila-cenarios.json`, de autoria Gemini;
- **como entra:** o autor (Claude) transforma os cenários em testes de integração com PG real, e o executor (Codex) roda.

**Testes obrigatórios:**
- os cenários acima;
- cada caso das 3 simulações do Codex;
- log sem código;
- `processar_pedido_vinculo` sem EXECUTE para o `app_runtime`;
- recibo imutável;
- contraprova de que, sem o recibo, a sequência A, B, A repetido remove B.

#### 3c) Contrato do job de vínculo, versão 3 (correções aceitas na revisão HML-JOB-01 do Codex e na fixture de cenários)

**Proposta; implementação a seguir, na branch `feat/vinculo-fila`.** Vale a v2 (3b), exceto nos pontos abaixo. A fixture é `vinculo-fila-cenarios-revisado.json` (sha256 `e2f0ed82…`, 15 cenários, Gemini e Codex).

**1. Pedido (conteúdo de uma versão do `hml-vinculo-pedido`).**
- Um objeto JSON com exatamente estas chaves:
  - `pedido_id` (UUID);
  - `acao` (`conceder` ou `revogar`);
  - `organizacao` e `usuario` (UUID);
  - `responsavel` e `motivo`;
  - `codigo`, só em `conceder`.
- Validações: as mesmas de `validarDestino` e `normalizarCodigo`, com no máximo 4 KiB.
- Qualquer outra forma é **`PEDIDO_INVALIDO`**, sem chamar o SQL. Entram aqui:
  - JSON quebrado;
  - chave desconhecida ou faltante;
  - tipo errado;
  - UUID inválido;
  - `acao` fora das duas;
  - `codigo` em `revogar`, ou ausente ou fora do formato em `conceder`.
- O volume `latest` do §3 sai: o job lê o segredo pela API, versão a versão.

**2. Identidade do pedido.**
- `conteudo_hash` = `hashCanonico` (`canonico.ts`) do objeto `{formato: 'VINCULO-PEDIDO-1', pedido_id, acao, organizacao, usuario, responsavel, motivo, codigo_hash}`, com:
  - UUIDs em minúsculas;
  - texto como é aplicado;
  - `codigo_hash` = SHA-256 hexadecimal do código normalizado, e `null` explícito em `revogar`.
- Isso substitui a concatenação com `|`, que o Codex provou ambígua (CEN-08).

**3. Função `app.processar_pedido_vinculo`.**
- Parâmetros: `p_pedido_id uuid`, `p_conteudo_hash bytea`, `p_versao_segredo bigint`, `p_acao text`, `p_codigo_hash bytea`, `p_organizacao uuid`, `p_usuario uuid`, `p_responsavel text`, `p_motivo text`, `p_criado_em timestamptz`.
- Devolve `TABLE (resultado text, revogados integer, repetido boolean)`.
- Ordem dentro da função:
  1. `pg_advisory_xact_lock` pela chave do pedido;
  2. o recibo primeiro: mesmo `conteudo_hash` devolve o resultado gravado com `repetido = true`; outro conteúdo devolve `PEDIDO_ID_REUTILIZADO`, sem efeito e sem recibo novo;
  3. o TTL, **fixo na função em 60 min**, com `now()` do início da transação: `now() − p_criado_em > 60 min` grava o recibo `PEDIDO_ATRASADO` (60:00 exato ainda vale);
  4. o efeito, por `conceder_vinculo` ou `revogar_vinculos`;
  5. o recibo, com a `versao_segredo` da 1ª aplicação.
- Recusa de negócio grava recibo e é final (CEN-14).

**4. Permissões** (padrão do `identity_link_event` da 0005):
- `app.vinculo_pedido_recibo` com RLS FORCE e gatilho `impedir_alteracao` em UPDATE e DELETE;
- `GRANT SELECT, INSERT` ao `app_sessao`, com as políticas `recibo_sessao_select` e `recibo_sessao_insert`;
- `SELECT` com a política `leitura_auditoria` ao `migrator`;
- **nada ao `app_runtime`**;
- a função é SECURITY DEFINER, com dono `app_sessao` (NOBYPASSRLS). `REVOKE ALL FROM PUBLIC` antes do `ALTER OWNER`; depois, `SET LOCAL ROLE app_sessao` e `GRANT EXECUTE` só ao `migrator`.

**5. Transação por pedido.**
- Uma transação curta por pedido: `BEGIN`, `SET LOCAL lock_timeout = '5s'`, `SET LOCAL statement_timeout = '30s'`, a função, `COMMIT`.
- Nenhum pedido compartilha transação com outro.

**6. Fila, no CLI `vincular-identidade` em modo fila.**
- **Conexão:** dedicada, pelo conector PRIVATE. `error` ou `end` inesperado para com saída 3.
- **Trava:** `pg_try_advisory_lock` da fila antes de ler qualquer segredo. Sem ela, `OCUPADO` e saída 1 (CEN-10).
- **Listagem:** `versions.list` com `filter=state:ENABLED`, lendo **todas as páginas**. A ordem é por `createTime` crescente e, no desempate, pelo número da versão; a ordem da API não conta.
- **Para cada versão:**
  1. `versions.get` pelo nome exato. Se ela deixou de estar ENABLED, fica de fora (log `VERSAO_INATIVA`). Se está, o `etag` lido aqui é o que vale;
  2. `:access`;
  3. validar;
  4. calcular o hash;
  5. chamar a função, com o `createTime` como `criado_em`.
- **Destino da versão:**
  - `PEDIDO_INVALIDO` e `PEDIDO_ID_REUTILIZADO` **desativam** a versão (`:disable` com `etag`), o que é reversível. Destruir fica com o dono;
  - qualquer outro resultado **destrói** a versão (`:destroy` com `etag`) depois do recibo confirmado.
- **Log por pedido:** exatamente `{pedido_id, versao, resultado, repetido}`. No inválido, só `{versao, resultado}`. Nunca código, subject, hashes ou conteúdo (CEN-13).
- **Saída:**
  - **3** em falha de infraestrutura, e a fila para na hora. Isso cobre banco, API, `etag` recusado e falha ao desativar ou destruir;
  - senão, **1** se houve qualquer `OCUPADO`, inválido, reutilizado, atrasado ou recusa de negócio;
  - senão, **0**.
- **Segredo:** vem de `SAFRION_PEDIDO_SEGREDO` (`projects/<p>/secrets/hml-vinculo-pedido`). O token vem do servidor de metadados, e as chamadas são REST, por `fetch`, sem dependência nova. O cliente é injetável: os testes usam uma API falsa em memória, com semântica de `etag` e de estado.

**7. Terraform.**
- Job `safrion-vinculo` em `local.jobs`, com:
  - args fixos do modo fila;
  - `max_retries 0`;
  - `vpc_access` `PRIVATE_RANGES_ONLY`;
  - a conta `sa-preparo`.
- Segredo `hml-vinculo-pedido` **sem `version_destroy_ttl`**, com o guard recusando o campo nesse segredo.
- IAM só nesse segredo:
  - operador com `secretVersionAdder`;
  - `sa-preparo` com `secretAccessor` e `secretVersionManager`.

**8. Testes** (PG real no `vinculo-fila.int.test.ts`; unitários no restante):
- os 15 cenários da fixture, lidos do JSON em `packages/db/test/fixtures/`. O CEN-05 monta `criado_em = now() − 3600 s` na mesma transação;
- concorrência do mesmo `pedido_id` por duas conexões: um efeito, um recibo, o outro `repetido`;
- UPDATE e DELETE do recibo recusados;
- `app_runtime` recebe **erro de privilégio** em SELECT, INSERT e EXECUTE;
- paginação e ordem fora da ordem da API;
- versão desativada entre a listagem e o acesso;
- conexão perdida depois do 1º pedido;
- campo desconhecido dá inválido;
- contraprova: sem o recibo, a sequência A, B, A repetido remove B.

**Limites:**
- O `createTime` vem do relógio do Secret Manager e o `now()` vem do banco. Uma diferença de segundos é aceita para um TTL de 60 min.
- A função não recalcula o `conteudo_hash`: quem a chama é o `migrator`, e o hash só separa repetição de reutilização.
- Os papéis do Secret Manager (`versions.list`, `get`, `disable` e `destroy` no `secretVersionManager`) devem ser conferidos na página de controle de acesso antes da 1ª subida.
- Nada roda no GCP antes do ensaio.

#### 4) Mudanças necessárias (arquivos)

**Terraform**
- **`bootstrap/main.tf`:**
  - acrescentar `compute.googleapis.com` e `servicenetworking.googleapis.com` em `local.apis`;
  - criar a rede, aplicada pelo dono, **antes de qualquer apply do `hml/` que crie a instância** [G33]:
    - `google_compute_network` com `auto_create_subnetworks = false`;
    - `google_compute_subnetwork` /24 RFC 1918 em southamerica-east1. O mínimo é /26 [G7]; a /24 dá folga para os blocos de 16 IPs. Com `private_ip_google_access = true` [G31] e sem `log_config`, porque flow logs custam;
    - `google_compute_global_address` com `VPC_PEERING`/`INTERNAL`, /20, com **`address` explícito em RFC 1918**, sem sobrepor a sub-rede. Motivos: o `PRIVATE_RANGES_ONLY` só manda para a VPC destinos RFC 1918 ou RFC 6598 [G35]; o Cloud SQL autoriza automaticamente só RFC 1918 [G5]; e a escolha automática não diz a faixa [G36]. O mínimo é /24 [G5], e IP interno não custa;
    - `google_service_networking_connection` com `deletion_policy = "PREVENT"` [G27].
- **`bootstrap/README.md`, "Depois do apply":** ligar o Compute cria a conta padrão do Compute, que pode receber Editor [G37]. Rodar o procedimento já escrito (tirar o Editor e desativar) e conferir a rede `default` (seção 5).
- **`bootstrap/outputs.tf`:** exportar o self_link da rede e da sub-rede e o nome da faixa.
- **`hml/variables.tf` e `terraform.tfvars.example`:** receber os self_links por variável. Não usar `data`, que o HML-TF-04 recusa.
- **`hml/banco.tf`:**
  - `ip_configuration` com `ipv4_enabled = false` literal [G2], `private_network` e `allocated_ip_range`. A faixa só pode ser dada na criação e não muda depois [G33];
  - `ssl_mode`, `server_ca_mode` e `connector_enforcement` como hoje;
  - sem `authorized_networks` [G1] e sem `data_api_access`, cujo padrão é DISALLOW [G22];
  - o `depends_on` [G26] não funciona entre estados, então a ordem vem do procedimento: bootstrap antes do hml.
- **`hml/main.tf` e `hml/cloud_run.tf`:**
  - remover o `local.socket`, o volume `cloud_sql_instance` e o `/cloudsql`;
  - pôr `vpc_access` no `template` da web e no `template.template` do preparo e do demo-reset [G28];
  - passar por variável de ambiente o nome de conexão da instância;
  - subir o `startup_probe` da web de 6 para cerca de 18 tentativas × 10 s (valor especificado, não medido) [G7];
  - criar o job `safrion-vinculo` em `local.jobs`.
- **`hml/segredos.tf`:** criar o segredo `hml-vinculo-pedido` fora do `local.segredos`, **sem `version_destroy_ttl`**, com `secretAccessor` para a `sa-preparo` e `secretVersionManager` para o operador. Explicar num comentário por que ele não segue os outros 4.
- **`hml/README.md`:**
  - dar o GCP-0017 como fechado e manter o GCP-0015 como decisão pendente;
  - corrigir a opção 1, que ainda diz "bastion ou VPN";
  - listar GCP-0076, GCP-0029 e GCP-0075 como não bloqueantes;
  - mudar o passo da credencial admin conferida pelo Auth Proxy.
- **`checar_travas.py` e `test_checar_travas.py`:**
  - exigir `ipv4_enabled = false` literal, `private_network` presente, `data_api_access` ausente ou `DISALLOW_DATA_API` e `egress = PRIVATE_RANGES_ONLY`;
  - recusar `ignore_changes` sobre esses campos;
  - opcional: recusar `version_destroy_ttl` no `hml-vinculo-pedido`.

**Código**
- **`packages/db`:**
  - fábrica de conexão com `@google-cloud/cloud-sql-connector` (`ipType PRIVATE`, autenticação por senha) quando houver o nome de conexão da instância [G12]. A URL comum continua para o Postgres local e a CI;
  - retentativa com espera crescente, até cerca de 3 min, na primeira conexão [G7];
  - usada em `src/preparo.ts`, `src/cli/preparar-banco.ts`, `src/cli/demo-reset.ts` e `src/cli/vincular-identidade.ts`.
- **`apps/web/src/servidor/ambiente.ts`:** usar a mesma fábrica.
- **`src/cli/vincular-identidade.ts`, modo pedido:**
  - quando `SAFRION_PEDIDO_ARQUIVO` está definida e a entrada não é terminal, ler do arquivo a ação, o destino e o código, com as mesmas validações, normalização e hash;
  - `--codigo` continua recusado;
  - arquivo ausente, ilegível ou incompleto dá recusa com saída 1, sem ecoar o conteúdo. Esse é também o caso de segredo sem versão [G18];
  - testes unitários e de integração, incluindo um log sem o código.
- **Rotação:** subcomandos no job para conferir a credencial do admin e trocar a senha de `migrator` e `app_runtime` lendo de segredo em versão fixa. Precisam existir antes da 1ª rotação, não antes da 1ª subida.

**Documentos**
- **ADR 0004 §11** (`docs/adr/0004-web-sessao-e-autorizacao.md`):
  - manter "nunca por argumento";
  - acrescentar que, em HML com o banco só em IP privado, o código entra por uma versão de uso único do `hml-vinculo-pedido` (sem destruição adiada), gravada pela entrada padrão, montada como arquivo e destruída logo depois;
  - registrar a exceção à F40.
- **`OPERACAO.md`:** fluxo novo de concessão e de rotação.
- **R-006:**
  - linha "Vínculo de identidade" do desenho mínimo, permissões do operador e custo;
  - ordem de execução: rede antes da instância;
  - conta padrão do Compute.

#### 5) Não verificado e limites

**Não verificado:**
- **Socket `/cloudsql` com instância só em IP privado.** A doc descreve o socket só para IP público [G11]. O desenho usa o conector por isso. Se um ensaio provar que o socket funciona, a mudança de código encolhe. Também não foi avaliada uma alternativa sem dependência nova: o Auth Proxy como sidecar, em IP privado, mantendo o socket. A doc de sidecars não cita o Cloud SQL Auth Proxy, e nos jobs o fim do sidecar é uma dúvida.
- **Direct VPC em southamerica-east1.** Não há lista positiva de regiões; nada exclui a região.
- **Permissões de rede das contas da CI:**
  - a `sa-deploy-github` (`run.developer`) publicando com `vpc_access`;
  - a `sa-infra-github` criando a instância com `private_network` de uma rede do bootstrap.

  A doc do Direct VPC só lista permissões do agente de serviço [G7]. Conferir no 1º plan e na 1ª publicação.
- **Custo da VPC e da sub-rede em si.** Não há SKU nem frase explícita de gratuidade.
- **Se a cobrança de IPv4 ocioso [G25] vale para IP privado.** Isso afeta a sensibilidade (e).
- **Criação do job pelo Terraform com o segredo ainda sem versão.** A doc só cita a checagem de permissão na criação [G18]. Na subida e na leitura, verificado: sem checagem e com falha de leitura.
- **Se o campo de valor do console do Secret Manager esconde o que é digitado.** Por isso o fluxo usa a entrada padrão.
- **Se o corpo dos overrides e o `sqlStatement` entram na auditoria.**
- **Studio:** se respeita `REQUIRED`. A exigência de `ALLOW_DATA_API` é dedução de G22 com G23.
- **Rede `default` ao ligar o Compute.** Não se sabe se ela nasce num projeto já existente; a doc fala de projeto novo, com SSH e RDP abertos para 0.0.0.0/0 [G29, G38]. Conferir depois do apply e apagá-la; o Trivy não a vê.

**Limites:**
- Operador único.
- Tráfego estimado em 1 a 5 GiB por mês, não medido; é teto, porque a volta do Cloud SQL na mesma região não custa [G25].
- Trivy 0.74 com o `trivy-checks` atual.
- Antes da 1ª subida, recomenda-se um ensaio numa instância descartável, sem dado real, do conector `PRIVATE` com o Direct VPC.
- Risco residual: a CI (`run.developer` via `local.jobs`) pode executar os jobs com overrides como `sa-preparo`, e isso já existe hoje. No job novo, isso inclui ler um pedido pendente durante a janela curta entre gravar e destruir.
- Achado lateral: o `cloudsql.viewer` dos agentes inclui `cloudsql.instances.export` e `cloudsql.backupRuns.export` [G30]. Avaliar um papel customizado sem export (não testado).

**Fontes** (acessadas em 28/09/2026)
- G1 https://raw.githubusercontent.com/aquasecurity/trivy-checks/main/checks/cloud/google/sql/no_public_access.rego: "enableipv4.value == true"; "cidr.is_public(network.cidr.value)"
- G2 https://raw.githubusercontent.com/aquasecurity/trivy/v0.74.0/pkg/iac/adapters/terraform/google/sql/adapt.go: "AsBoolValueOrDefault(true, resource)"
- G3 https://raw.githubusercontent.com/aquasecurity/trivy-checks/main/checks/cloud/google/compute/enable_subnetwork_flow_logs.rego: "GCP-0076 … severity: MEDIUM"
- G4 https://docs.cloud.google.com/sql/docs/postgres/configure-private-services-access: "fails with SERVICE_NETWORKING_NOT_ENABLED"; "roles/compute.networkAdmin"
- G5 https://docs.cloud.google.com/sql/docs/postgres/private-ip: "can't remove the private IP capability"; "minimum size is a single /24 block"; "automatically authorized for RFC 1918"
- G6 https://cloud.google.com/vpc/network-pricing: "no hourly or data charges for the connection itself"; "no charge for static or ephemeral internal IP addresses"; "priced the same as VM-to-VM traffic"; PSC endpoint "$0.01 / 1 hour"
- G7 https://docs.cloud.google.com/run/docs/configuring/vpc-direct-vpc: "/26 or larger"; "delays of a minute or more"; "roles/run.serviceAgent) that contains the necessary permissions"
- G8 https://docs.cloud.google.com/run/docs/configuring/connecting-vpc: "you pay only for network egress"; "slower, including starting from zero"
- G9 https://cloud.google.com/run/pricing: "billed as Data transfer from a VM"
- G10 https://docs.cloud.google.com/run/docs/securing/private-networking: "public destinations continue to be routed directly to the internet"
- G11 https://docs.cloud.google.com/sql/docs/postgres/connect-run: "For public IP paths … Through Unix sockets"; "uses TCP … without using the Cloud SQL Auth Proxy"
- G12 https://docs.cloud.google.com/sql/docs/postgres/connect-connectors: "Cloud SQL rejects direct connections to the database"; "don't provide new paths to connectivity"
- G13 https://docs.cloud.google.com/sql/docs/postgres/sql-proxy: "does not provide a new connectivity path"
- G14 https://docs.cloud.google.com/sql/docs/postgres/connect-instance-cloud-shell: "Cloud Shell doesn't work with a private IP address"
- G15 https://docs.cloud.google.com/run/docs/execute/jobs: "Cloud Run Invoker (roles/run.invoker) on the Cloud Run job"; "override the arguments, environment variables"; "Cloud Run Developer"
- G16 https://docs.cloud.google.com/run/docs/reference/iam/roles: "execute and cancel Cloud Run jobs with overrides"; e https://docs.cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs/run: "run.jobs.runWithOverrides"
- G17 https://docs.cloud.google.com/run/docs/reference/rest/v2/projects.locations.jobs.executions: "template used to create tasks for this execution"
- G18 https://docs.cloud.google.com/run/docs/configuring/jobs/secrets: "fetches the secret value … with the latest version"; "doesn't perform any checks during instance startup"
- G19 https://docs.cloud.google.com/secret-manager/docs/access-control: "secretmanager.versions.add … secretmanager.versions.destroy"
- G20 https://docs.cloud.google.com/secret-manager/docs/add-secret-version: "appears as plaintext in the list of processes"
- G21 https://cloud.google.com/secret-manager/pricing: "\"active\" … Enabled and Disabled"; "billed proportional to that usage"
- G22 https://docs.cloud.google.com/sql/docs/postgres/admin-api/rest/v1/instances: "Not allowed by default"; "from the public internet using instances.executeSql API"
- G23 https://docs.cloud.google.com/sql/docs/postgres/manage-data-using-studio: "uses the executeSql API"; "every execution starts a new session"; "contain the invalid query"; "might transit through intermediate locations"
- G24 https://docs.cloud.google.com/iam/docs/roles-permissions/cloudsql: "Role allowing access to Cloud SQL Studio"
- G25 https://cloud.google.com/sql/pricing: "IPv4 addresses while idle"; "Within the same region: free"
- G26 https://raw.githubusercontent.com/hashicorp/terraform-provider-google/v8.3.0/website/docs/r/sql_database_instance.html.markdown: "explicitly add a `depends_on`"; exemplos com `psc_config` e `ipv4_enabled = false`
- G27 https://raw.githubusercontent.com/hashicorp/terraform-provider-google/v8.3.0/website/docs/r/service_networking_connection.html.markdown: "fail if this field is set to \"PREVENT\""
- G28 https://raw.githubusercontent.com/hashicorp/terraform-provider-google/v8.3.0/website/docs/r/cloud_run_v2_job.html.markdown: "only single network interface is supported"
- G29 https://docs.cloud.google.com/vpc/docs/vpc: "pre-populated IPv4 firewall rules"; "ingress rules allowing protocols such as RDP and SSH"
- G30 https://docs.cloud.google.com/iam/docs/roles-permissions/cloudsql: `roles/cloudsql.viewer` com "cloudsql.instances.export"
- G31 https://raw.githubusercontent.com/aquasecurity/trivy-checks/main/checks/cloud/google/compute/enable_subnetwork_private_google_access.rego: "id: GCP-0075"; "severity: LOW"
- G32 https://raw.githubusercontent.com/aquasecurity/trivy-checks/main/checks/cloud/google/compute/enable_vpc_flow_logs.rego: "id: GCP-0029"; "severity: LOW"
- G33 https://docs.cloud.google.com/sql/docs/postgres/configure-private-ip: "causes the instance to restart"; "can't assign an allocated range name for an existing instance"; "you can't modify the range"
- G34 https://docs.cloud.google.com/secret-manager/docs/delay-destruction-of-secret-versions: "The version is disabled, preventing its use."
- G35 https://docs.cloud.google.com/run/docs/configuring/vpc-connectors: "RFC 1918"; "RFC 6598"; "Packets to any other destination are routed"
- G36 https://docs.cloud.google.com/vpc/docs/configure-private-services-access: "automatically selects an unused address range"
- G37 https://docs.cloud.google.com/compute/docs/access/service-accounts: "when you enable the Compute Engine API"; "might automatically be granted the Editor role"
- G38 https://docs.cloud.google.com/sql/docs/postgres/admin-api/rest/v1/instances/executeSql: "passwordSecretVersion"; "autoIamAuthn"; e https://docs.cloud.google.com/firewall/docs/firewalls: "default-allow-ssh" com "0.0.0.0/0"

**Arquivos citados:**
- infra/terraform/hml/README.md (linha 74, trecho "bastion ou VPN" a corrigir; GCP-0015 pendente)
- infra/terraform/hml/cloud_run.tf (`local.jobs`, linhas 339 a 355)
- infra/terraform/hml/segredos.tf (linha 43, `version_destroy_ttl = "604800s"`, que o segredo novo não deve copiar)
- infra/terraform/bootstrap/main.tf
- infra/terraform/bootstrap/contas.tf
- infra/terraform/bootstrap/README.md (linha 52, procedimento "Conta padrão do Compute")
- .github/workflows/ci.yml (linhas 52 e 61, gate `HIGH,CRITICAL`)
- docs/parceria/rodadas/evidencias/R-006-hospedagem.md (nada provisionado; conflito com o PRD 31.7)
- (produto, 182ad2a) packages/db/src/cli/vincular-identidade.ts
- (produto, 182ad2a) apps/web/src/servidor/ambiente.ts
- (produto, 182ad2a) docs/adr/0004-web-sessao-e-autorizacao.md

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
