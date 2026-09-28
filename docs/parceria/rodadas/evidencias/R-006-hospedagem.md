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

**Câmbio:** PTAX de venda de 28/09/2026 = **R$ 5,2132** (boletim das 13:03). Com IOF de 3,5%, dá R$ 5,3957 (IOF não reconferido hoje). **Se a conta de faturamento for de contratação local no Brasil, os preços dos SKUs não incluem impostos (14% sobre o uso) e o IOF provavelmente não se aplica.** Só o console mostra qual caso vale para a conta do Adrianus (https://docs.cloud.google.com/billing/docs/resources/vat-overview).

### Custo mensal da HML mínima (preços de São Paulo relidos em 28/09; mês = 730 h)

| Item                                                                                                                     | Conta                                                              | US$/mês                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Cloud SQL PostgreSQL 17, `db-f1-micro`, Enterprise, zonal                                                                | 0,0158 × 730                                                       | 11,53                                                                                         |
| Disco SSD de 10 GB (o mínimo da API), autoaumento até 20 GB                                                              | 0,000349315 × 730 × 10                                             | 2,55                                                                                          |
| Backup diário, 7 retidos, cerca de 2 GiB usados                                                                          | 0,000164384 × 730 × 2                                              | 0,24                                                                                          |
| Cloud Run web, 20 h de uso, 1 vCPU e 0,5 GiB, com a franquia (desconto a preço Tier 1)                                   | 72.000 × (0,0000336 − 0,000024) + 36.000 × (0,0000035 − 0,0000025) | 0,73                                                                                          |
| Cloud Run Jobs `safrion-preparo` (10 × 3 min) e `safrion-demo-reset` (4 × 2 min), com a franquia                         | 2.280 × (0,0000216 − 0,000018) + 1.140 × (0,0000024 − 0,000002)    | 0,01                                                                                          |
| Artifact Registry, 2 GiB (0,5 GiB grátis; preço único para todas as regiões)                                             | 1,5 × 0,000136986 × 730                                            | 0,15                                                                                          |
| Saída de internet para os testadores, cerca de 1 GiB                                                                     | 1 × 0,19                                                           | 0,19                                                                                          |
| Secret Manager (4 versões ativas ≤ 6 grátis), Logging (< 50 GiB grátis), Monitoring, WIF, IAM, requisições (< 2 milhões) | —                                                                  | 0                                                                                             |
| Bucket do state do Terraform (< 10 MiB)                                                                                  | 0,000047945 × 730 × 0,01                                           | 0,00                                                                                          |
| **Total**                                                                                                                |                                                                    | **≈ 15,40** (R$ 80,29 pela PTAX; **R$ 83,10 com IOF**; com imposto local de 14%, ≈ US$ 17,56) |

Se o Google aplicar a franquia do Cloud Run como crédito em dólar, a web e os jobs zeram e o total fica em US$ 14,67. A diferença, US$ 0,74, não muda a decisão.

**Sensibilidades:**

- (a) web com 1 instância mínima: **28,82**;
- (b) banco `db-g1-small`: **42,19**;
- (c) PITR de 7 dias ligado, no pior caso de o log ocupar o disco até 20 GB: **17,95**. É a configuração que o requisito pede (§30.5; ENG-067);
- (d) 100 h de uso por mês: **23,39**;
- (c) + (d): **25,94**;
- (e) parar a instância quase não economiza, porque o IP ocioso custa US$ 10,95: **14,82**. Só apagar a instância economiza de verdade;
- (f) se o IPv4 fosse cobrado com a instância rodando, o que a página não indica: **26,35**. Conferir na 1ª fatura.

**O Cloud SQL é cerca de 92% da conta e não tem teto automático.**

**Orçamento:** US$ 25/mês **só de alerta**, com escopo no projeto HML e avisos em **70% (US$ 17,50), 90% e 100%** do gasto real e em 100% do previsto (PRD 28.4; plano R-006 passos 11 e 12). **Orçamento não limita uso nem gasto.** O teto de gasto nativo do Google só vale para Cloud Run, Cloud Run functions, Gemini API e Vertex; **o Cloud SQL não está coberto**. Aumentar o orçamento **antes** de mudar a configuração: US$ 30 com PITR e uso intenso, US$ 35 com mínimo 1, US$ 50 com `db-g1-small`.

### Desenho mínimo (sem domínio próprio)

| Componente                 | Onde roda                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Configuração e segredos                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Banco                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Web (`web@sha256`)         | Cloud Run service `safrion-web`, southamerica-east1, mínimo 0 e máximo 2, concorrência 20, 1 vCPU, 512 MiB, CPU só na requisição, conta `sa-web`                                                                                                                                                                                                                                                                                                                                                                                     | `DATABASE_URL=postgresql://app_runtime@/safrion_hml?host=/cloudsql/<PROJ>:southamerica-east1:safrion-hml` **sem senha**; `PGPASSWORD` vindo do segredo `hml-db-app-runtime-senha` (o `pg` 8.23 lê `PGPASSWORD`, sem mudança de código); `SAFRION_ORIGEM=https://safrion-web-<NUM>.southamerica-east1.run.app`; `SAFRION_AMBIENTE=hml`; `SAFRION_VERSAO`/`SAFRION_COMMIT` injetados na publicação; `SAFRION_OIDC_ISSUER=https://accounts.google.com`; `SAFRION_OIDC_CLIENT_ID`; `SAFRION_OIDC_CLIENT_SECRET` do segredo `hml-oidc-client-secret` | Conexão Cloud SQL integrada do Cloud Run (socket `/cloudsql`) |
| Preparo (`preparo@sha256`) | Cloud Run Job `safrion-preparo`, 1 tarefa, `max_retries 0`, 600 s, conta `sa-preparo`, args `--ambiente hml --banco safrion_hml`                                                                                                                                                                                                                                                                                                                                                                                                     | `SAFRION_ADMIN_URL=postgresql://postgres@/postgres?host=/cloudsql/…` sem senha; `PGPASSWORD` de `hml-db-admin-senha`; `SAFRION_SENHA_MIGRATOR` e `SAFRION_SENHA_APP_RUNTIME` dos segredos próprios                                                                                                                                                                                                                                                                                                                                              | Socket `/cloudsql`                                            |
| Demonstração               | Cloud Run Job `safrion-demo-reset` com a imagem `preparo`, command `node`, args `dist/cli/demo-reset.js --confirmar hml`, conta `sa-demo`                                                                                                                                                                                                                                                                                                                                                                                            | `DATABASE_URL` do `app_runtime` (como a web), `SAFRION_AMBIENTE=hml`                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Socket `/cloudsql`                                            |
| Vínculo de identidade      | **Na máquina do operador, não em job**: o código entra pela entrada padrão, sem eco, e um job não tem terminal. Cloud SQL Auth Proxy em 127.0.0.1 com a identidade IAM do operador (Cloud SQL Client)                                                                                                                                                                                                                                                                                                                                | `SAFRION_ADMIN_URL=postgresql://postgres@127.0.0.1:6543/postgres`; `PGPASSWORD` lido do Secret Manager sem aparecer na tela, com `unset` ao final; checkout do commit publicado; Node 24.21                                                                                                                                                                                                                                                                                                                                                     | Auth Proxy (TLS + IAM)                                        |
| Banco                      | Cloud SQL `safrion-hml`: **`database_version = POSTGRES_17`, `edition = ENTERPRISE`, `tier = db-f1-micro`, explícitos** (PG16+ nasce Enterprise Plus); zonal; SSD de 10 GB com autoaumento até 20 GB; backup diário com 7 retidos; **PITR de 7 dias** (requisito; ligar explicitamente no Terraform); `deletion_protection`; IP público **sem redes autorizadas** (só conector com IAM); `server_ca_mode = GOOGLE_MANAGED_INTERNAL_CA` explícito; `max_connections` padrão 25 → orçamento de ≤ 18 (web 2 × pool 3 + jobs + operador) | O Terraform cria **só a instância e o usuário `postgres`**. Banco `safrion_hml`, `migrator`, `app_runtime` e `app_sessao` nascem **só pelo job de preparo**                                                                                                                                                                                                                                                                                                                                                                                     |
| Segredos                   | Secret Manager, replicação em southamerica-east1: `hml-db-admin-senha`, `hml-db-migrator-senha`, `hml-db-app-runtime-senha`, `hml-oidc-client-secret`                                                                                                                                                                                                                                                                                                                                                                                | O Terraform cria o segredo e o IAM; **os valores entram por stdin, fora do Terraform** (senão iriam para o state e o plan). Senhas alfanuméricas de 32 caracteres. Ao trocar, **destruir** a versão antiga, não só desativá-la: versões desativadas contam na franquia de 6                                                                                                                                                                                                                                                                     | —                                                             |
| Imagens                    | Artifact Registry `safrion` (Docker, southamerica-east1), tags imutáveis, limpeza: 10 versões mais recentes e sem tag por 14 dias                                                                                                                                                                                                                                                                                                                                                                                                    | Publica o **mesmo digest que o Trivy varreu**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | —                                                             |
| Publicação                 | GitHub Actions `publicar-hml.yml` (**a criar**): push em `main`, environment `hml` com revisor, `permissions: id-token: write, contents: read`, WIF                                                                                                                                                                                                                                                                                                                                                                                  | Publica as imagens → executa o preparo → publica a web por digest → testa `/saude` exigindo `ok`, `hml` e `commit = GITHUB_SHA` → grava o manifesto da publicação                                                                                                                                                                                                                                                                                                                                                                               | —                                                             |

**Identidades de menor privilégio, sem chave JSON:**

- `sa-web`: `cloudsql.client` e `secretAccessor` só em `app-runtime` e `oidc`;
- `sa-preparo`: `cloudsql.client` e `secretAccessor` nas 3 senhas do banco;
- `sa-demo`: `cloudsql.client` e `secretAccessor` só em `app-runtime`;
- `sa-deploy-github`: `artifactregistry.writer` no repositório, `run.developer` nos 3 recursos, `iam.serviceAccountUser` nas 3 SAs de runtime. Recebe `workloadIdentityUser` do principal do repositório, com a condição `repository_id` e ref `main`;
- operador humano: `run.invoker` nos jobs, `cloudsql.client`, `secretAccessor`, `logging.viewer`;
- proprietário: `owner` só para o bootstrap e emergências, e o papel de faturamento que cria o orçamento;
- agentes: `sa-agentes-leitura`, só leitura (`run.viewer`, `cloudsql.viewer`, `logging.viewer`, `monitoring.viewer`, `artifactregistry.reader`), por _impersonation_, **sem** `secretAccessor`.
- Desligar a concessão automática de Editor à conta padrão do Compute.

**Sondas:** o `HEALTHCHECK` do Dockerfile não vale no Cloud Run. Usar a **sonda de inicialização HTTP em `/saude`**, que trava a revisão sem banco, e **nenhuma sonda de atividade em `/saude`**, porque ela responde 503 quando o banco cai e derrubaria instâncias sadias.

### Ordem de execução, com quem faz o quê (nada foi executado)

1. **Adrianus:**
   - (a) decidir entre o **projeto dedicado `safrion-hml`** (recomendado pelo PRD 27.4 e ENG-064: ambientes separados de fato) e o projeto atual;
   - (b) ver no console **se a conta de faturamento é em US$ com cartão ou contratação local**;
   - (c) autorizar o **orçamento de alerta de US$ 25/mês** (D4) e criá-lo na conta de faturamento com 70/90/100%.
2. **Adrianus, no console, antes de todo o resto (risco que derruba o desenho):** na Google Auth Platform do projeto HML:
   - identidade visual "Safrion HML", público Externo, status Em teste, escopo só `openid`;
   - **registrar o domínio autorizado e o URI `https://safrion-web-<NUM>.southamerica-east1.run.app/entrar/retorno`**. Se o Google **recusar** `run.app`, a HML precisa de domínio próprio com balanceador global, a partir de **US$ 18,25/mês**, e o total passa de US$ 25: decisão nova de custo;
   - com escopo só `openid`, a lista de usuários de teste não barra ninguém, e qualquer conta Google chega ao pedido de acesso.
3. **Agente (Codex) com a sessão do dono, uma única vez (bootstrap):**
   - bucket do state com versionamento, `prevent_destroy` e acesso só do dono;
   - APIs (run, sqladmin, artifactregistry, secretmanager, iam, iamcredentials, sts, cloudresourcemanager, serviceusage, billingbudgets se o orçamento for por Terraform);
   - pool e provider WIF do GitHub;
   - SAs;
   - `terraform plan` revisado (fmt, validate, TFLint, scanner), apply do plan aprovado.
   - Depois, **revogar a sessão e a ADC** (plano R-006 passo 12).
4. **Senhas:** gerar 3 senhas, gravar as versões por stdin e definir a senha do `postgres` da instância igual à do segredo.
5. **GitHub (Adrianus, administrador):**
   - environment `hml` com revisor, restrito a `main`, e variáveis `GCP_PROJECT_ID`, `GCP_REGION`, `WIF_PROVIDER` e `DEPLOY_SA`;
   - se o plano do GitHub não oferecer environments em repositório privado, a condição do WIF fica por repositório e ref `main`.
6. **1ª subida, com aprovação no environment:**
   - publicar as imagens → job `safrion-preparo` → job `safrion-demo-reset` → publicar a web;
   - conferir `/saude` (ok, hml, commit), a **faixa ou selo "Homologação"** em todas as telas e o login.
7. **Acesso de cada testador:**
   - a pessoa entra e passa o código; o operador confirma quem é por canal independente;
   - `vincular-identidade conceder` roda na máquina do operador pelo Auth Proxy;
   - **repetir depois de cada `demo-reset`**, que revoga os acessos reais à geração anterior.

### Lacunas que precisam de decisão ou código antes ou durante a 1ª subida

- **Publicação inexistente.** O `publicar-hml.yml` e o manifesto da publicação (ENG-060) estão por fazer. Hoje a imagem varrida é descartada.
- **O operador não tem como saber o `--usuario` a conceder.** Proposta (código Claude): `vincular-identidade listar --organizacao <id>` rodando como migrator, que mostra papel e id dos usuários fictícios (não é dado pessoal), ou o `demo-reset` imprimindo esses ids.
- **Vínculo pela máquina do operador × PRD 31.7 e o passo 12 (revogar a sessão depois do bootstrap).** Cada concessão exige sessão gcloud ativa (Auth Proxy e `secrets access`). Decidir entre login e revogação a cada concessão, com um roteiro de um comando, ou uma exceção explícita registrada.
- **URL controlada (PRD 27.4; plano passo 11: IAP ou exceção ENG-005).** O IAP direto no Cloud Run é GA, custa **US$ 0** e funciona sem organização. Decidir entre IAP com lista de permitidos e ingress público com vínculo explícito como controle. Com IAP, o teste de `/saude` da publicação precisa de identidade com acesso.
- **Migração usa a senha do administrador do banco.** Aceitável na HML, com a `sa-preparo` isolada. Antes do piloto, um comando `migrar` só com o `migrator`.
- **Faixa HOMOLOGAÇÃO.** A casca já mostra um selo permanente do ambiente no cabeçalho (`(app)/layout.tsx`, a partir da identidade do banco). Conferir se atende "todas as telas", inclusive `/entrar` e erros (PRD:5495).
- **Backups:** o local padrão dos backups automáticos é a multirregião mais próxima, possivelmente fora do Brasil. Fixar `location` em southamerica-east1 se a LGPD pedir (não verificado).

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

Se o Google Cloud bloqueia o gasto no teto · PITR do Cloud SQL em dias · menor disco do Cloud SQL · preço exato de Cloud Storage, Artifact Registry, Secret Manager e Cloud Scheduler em São Paulo · se o acréscimo de `gru` vale para o MPG do Fly · frequência e retenção de backup do MPG · diferença de preço regional do Neon e do Supabase em `sa-east-1` · cartão exigido por Render, Vercel, Supabase, AWS, DigitalOcean e Hetzner · prazo do Free Tier do Lightsail · PostGIS no banco gerenciado do Lightsail e no banco de dev da DigitalOcean · backup da DigitalOcean · regras da ANPD para transferência internacional · Magalu Cloud (a calculadora de preços em reais não carregou em https://magalu.cloud/precos/) · spread do banco no cartão.
