# Hospedagem de baixo custo — Homologação (HML) e piloto de produção

Data de referência e de acesso a todas as fontes: **27/09/2026**. Só leitura: nenhuma conta criada, nenhum cadastro aberto, nenhum dado informado.

**Rótulos.** *verificado* = número lido na página oficial do provedor nesta data. *especificado* = conta ou suposição minha feita a partir de números verificados (uso, tamanho, horas). *não verificado* = sem fonte oficial lida.

**Cotação.** PTAX venda de 25/09/2026 (último dia útil antes de 27/09, um domingo): **R$ 5,1991 por US$** (verificado, API PTAX do Banco Central, fonte F1). Cartão internacional paga IOF de **3,5%** (especificado pela Fazenda em maio/2025, fonte F2; vigência em set/2026 e spread do banco não verificados). Fator usado: 5,1991 × 1,035 = **R$ 5,3811 por US$** com IOF.

**O que o PRD já decidiu (lido no repositório, só leitura).** §28.1 dá como topologia de referência *Google Cloud Run + Cloud SQL PostgreSQL/PostGIS com HA regional + Cloud Storage + Secret Manager + Cloud Tasks/Jobs*, via Terraform, com região escolhida em ADR. §27.4 exige HML com estrutura equivalente à produção, projeto e banco próprios e **a mesma imagem por digest** promovida para produção. §30.5 pede backup diário com retenção de 35 dias e PITR de pelo menos 7 dias. NFR-11 pede RPO ≤ 15 min e RTO ≤ 4 h. Isso pesa na recomendação.

## Recomendação curta

| Ambiente | Escolha | US$/mês | R$/mês (PTAX) | R$/mês com IOF |
|---|---|---|---|---|
| **HML** | Google Cloud `southamerica-east1`: Cloud Run (web, mínimo 0) + Cloud Run Job (worker) + Cloud SQL `db-f1-micro` com PostGIS, sem HA, com backup | **≈ 16,32** | ≈ 84,87 | ≈ 87,84 |
| **Piloto (conforme PRD)** | Mesmo desenho em projeto separado; Cloud SQL Enterprise **HA** 1 vCPU/3,75 GiB; web com 1 instância mínima | **≈ 183,13** | ≈ 952,12 | ≈ 985,44 |
| Piloto econômico (exige aceite de risco) | Igual, mas Cloud SQL **HA `db-g1-small`** (núcleo compartilhado, fora do SLA do Cloud SQL) | ≈ 111,85 | ≈ 581,50 | ≈ 601,86 |

Por quê: é a topologia de referência do PRD (§28.1); tem região em São Paulo (LGPD); PostGIS suportado; backup gerenciado; roda contêiner comum, então a mesma imagem por digest vai de HML para produção sem migrar de provedor. A conta nova tem crédito de US$ 300 por 90 dias (verificado, F13), mas a elegibilidade da conta do proprietário não foi verificada.

Plano B só para HML, se o proprietário preferir o menor custo e aceitar registrar em ADR o desvio da §28.1: **Fly.io `gru` (web + worker) + Neon `aws-sa-east-1` Free** ≈ **US$ 7,85/mês** (R$ 40,82; R$ 42,25 com IOF). Tudo em São Paulo, com PostGIS.

## Tabela comparativa (US$ por mês; detalhes das contas na seção seguinte)

| Opção | Região no Brasil | HML mínima | Piloto | Camada grátis e limites reais | PostGIS | Backup e restauração | Operação | Lock-in | Cartão |
|---|---|---|---|---|---|---|---|---|---|
| **Google Cloud Run + Cloud SQL** | Sim, `southamerica-east1` (F12, F13b) | ≈ 16,32 (esp.) | ≈ 183,13 com HA dedicado; ≈ 111,85 com HA compartilhado (esp.) | Cloud Run: 180 mil vCPU-s, 360 mil GiB-s e 2 milhões de requisições por mês; crédito de US$ 300/90 dias; Cloud SQL tem instância de teste de 30 dias; depois paga (ver.) | Sim, todas as versões (F14) | Automático, retenção de 1 dia a 10 anos conforme opção (ver., F15); PITR em dias: não verificado | Média: IAM, projetos, Terraform | Baixo no app (contêiner); médio no banco (Postgres padrão) | Sim (ver., F13) |
| **Fly.io + Fly Managed Postgres** | Sim, `gru`, e o MPG roda em `gru` (F4) | ≈ 46,13 (esp.) | ≈ 53,38 com HA incluso (esp.) | Só teste: 2 h de máquina ou 7 dias (ver., F5) | Sim, ao criar o cluster (F3b) | "Backups automáticos e recuperação"; frequência e retenção não verificadas | Baixa | Baixo (contêiner + Postgres) | Sim, toda organização (ver., F3) |
| **Fly.io + Neon** | Sim, `gru` + `aws-sa-east-1` (F4, F7) | ≈ 7,85 (esp.) | ≈ 22,82 a 32,63 (esp.) | Neon Free: 0,5 GB, 100 CU-h por projeto, dorme após 5 min, restauração de 6 h, sem cartão (ver., F6) | Sim (F8) | Neon Launch: restauração até 7 dias (ver.) | Baixa | Baixo | Fly sim; Neon não |
| **Vercel + Neon ou Supabase** | Sim: Vercel `gru1`, Neon e Supabase `sa-east-1` (F9, F7, F11) | ≈ 0 + worker fora (esp.) | ≈ 45 + worker fora (Vercel Pro 20 + Supabase Pro 25) | Vercel Hobby só uso pessoal, não comercial, cron no máximo 1 vez por dia; Supabase Free pausa após 1 semana sem uso, sem backup (ver.) | Sim (Neon F8, Supabase F11b) | Supabase Pro: backup diário por 7 dias; PITR US$ 100/mês por 7 dias (ver.) | Média: worker precisa de outro lugar | Médio a alto (Vercel não publica imagem por digest) | Não verificado |
| **Render** | Não: EUA, Frankfurt, Singapura (F16) | ≈ 20,30 (esp.) | ≈ 36 (esp.) | Web grátis dorme após 15 min, 750 h; Postgres grátis expira em 30 dias, sem backup; worker não tem grátis (ver., F17) | Sim (F18) | PITR 3 dias no Hobby, 7 no Pro de US$ 25 (ver., F19) | Baixa | Baixo | Não verificado |
| **Railway** | Não: EUA, Amsterdã, Singapura (F21) | ≈ 8,15 (esp.) | ≈ 15 a 25 (esp., uso) | Teste de US$ 5 por 30 dias, sem cartão; plano grátis com US$ 1/mês (ver., F20) | Só por modelo da comunidade, não gerenciado (F22) | Backup de volume: diário por 6 dias, semanal por 27, mensal por 89 (ver., F23) | Baixa a média | Baixo | Teste não |
| **AWS Lightsail** | Sim, São Paulo, com metade da franquia de tráfego (F24) | ≈ 13 (esp.): VPS de 2 GB com tudo em Docker | ≈ 28 (esp.) se o banco gerenciado aceitar PostGIS | "Comece grátis" pelo Free Tier; prazo e planos não verificados | Banco gerenciado: não verificado; na VPS, sim (autogerido) | Snapshot automático diário, guarda os 7 últimos (ver., F25) | Alta na VPS (atualização, TLS, backup do banco) | Baixo | Não verificado |
| **DigitalOcean** | Não: América do Norte, Europa, Ásia, Austrália (F28) | ≈ 17 (esp.) | ≈ 25,15 (esp.) | Só 3 sites estáticos grátis (ver., F27) | Sim no banco gerenciado (F29); no banco de dev, não verificado | Detalhes de backup não verificados | Baixa | Baixo | Não verificado |
| **Hetzner (VPS + Docker)** | Não: Alemanha, Finlândia, EUA, Singapura (F30) | ≈ 8,39 (esp.) | ≈ 16,78 (esp.) | Não há | Sim, autogerido | Backup do servidor: +20% do preço (ver., F31) | Alta | Baixo | Não verificado |

Leitura da tabela: "esp." quer dizer que o total é uma conta minha feita com preços verificados; os preços unitários estão abaixo e nas fontes. Mês = 730 h = 2.628.000 s.

## Contas (preços unitários verificados; quantidades especificadas)

**HML recomendada — Google Cloud, São Paulo** (preços lidos em F12 e F13b com o seletor de região em *Sao Paulo (southamerica-east1)*)
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
- Versão econômica: trocar o banco por HA `db-g1-small` (US$ 0,105/h × 730 = 76,65) e a reserva por 10 → **≈ US$ 111,85** (R$ 601,86 com IOF). Sem HA (`db-g1-small` a 0,0525/h = 38,33) → ≈ US$ 68,42 (R$ 368,18 com IOF), mas contraria a §28.1 do PRD.

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

1. **Crédito e franquia não são teto.** Crédito de 90 dias acaba e a conta passa a cobrar. Alerta de orçamento do Google avisa, mas não confirmei se bloqueia o gasto (não verificado). Por isso o teto precisa ser vigiado.
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
3. **Gasto máximo mensal da HML:** teto de **US$ 25/mês (≈ R$ 135 com IOF)**, com alertas em 50%, 90% e 100%. Isso dá folga de cerca de 50% sobre os US$ 16,32 estimados.
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
