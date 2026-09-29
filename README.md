# Do Talhão à O.S.

Plataforma de gestão agrícola integrada: planejamento da safra, planos agronômicos, ordens de serviço com aprovação agronômica, almoxarifado integrado, app de campo com operação sem internet, compras, estoque e custos.

**Estado:** fundação em construção, **sem homologação hospedada nem produção**. Já existem o domínio (decimal, unidades e saldo por lote), o banco PostgreSQL/PostGIS com RLS e isolamento entre organizações, o login OIDC com sessões, a primeira interface web de estoque e cadastros, as imagens verificadas e o Terraform da homologação (validado na CI, não aplicado). Estado detalhado e próximo passo: [`docs/STATUS.md`](docs/STATUS.md) e o checkpoint da issue #1.

## Onde está cada coisa
| O quê | Onde |
|---|---|
| Contrato do produto (PRD v3.9 vigente) | [`docs/PRD.md`](docs/PRD.md) |
| Fluxogramas com raias | [`docs/prd/fluxogramas/`](docs/prd/fluxogramas/) |
| Decisões e ADRs | [`docs/DECISIONS.md`](docs/DECISIONS.md), [`docs/adr/`](docs/adr/) |
| Design system | [`docs/design-system/`](docs/design-system/) |
| Instruções para agentes (fonte única) | [`AGENTS.md`](AGENTS.md); o `CLAUDE.md` importa esse arquivo |
| Como contribuir | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Operação e homologação | [`docs/OPERACAO.md`](docs/OPERACAO.md), [`infra/terraform/`](infra/terraform/) |
| Portões da CI e proteção da `main` | [`.github/workflows/`](.github/workflows/), [`tools/ci/`](tools/ci/), [`tools/github/`](tools/github/) |
| Parceria Claude + Codex | [`docs/parceria/`](docs/parceria/) |
| Protótipo navegável (validação) | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |

## Como rodar (3 passos)
1. Instale o Node **24.21.0** (versão em `.nvmrc`) e ative o pnpm pela versão fixada: `corepack enable`.
2. `pnpm install --frozen-lockfile`
3. `pnpm run check`: confere versões, formatação, lint e fronteiras entre pacotes, tipos, testes com cobertura e build.

## Comandos que existem hoje
| Comando | O que faz |
|---|---|
| `pnpm run check` | Os mesmos passos que a CI roda no código, na mesma ordem (a instalação fica de fora) |
| `pnpm run doctor` | Confere se o Node e o pnpm em uso são os fixados (`pnpm doctor`, sem `run`, é um comando do próprio pnpm) |
| `pnpm run lint` | ESLint e o script de fronteiras dos pacotes em `packages/`: sem dependência não declarada e sem ciclo de imports (ENG-012); `apps/web` fica fora do script |
| `pnpm run test` | Testes unitários, com cobertura mínima de 95 % por arquivo nos módulos listados em `vitest.config.ts` (ENG-032/033) |
| `pnpm run test:integration` | Banco real: papéis, RLS, isolamento entre organizações, idempotência e imutabilidade. Precisa de Docker, ou de `SAFRION_TEST_DATABASE_URL` com um PostgreSQL descartável e usuário administrador. Roda na CI depois dos testes |
| `pnpm run demo:reset -- --confirmar <dev\|hml>` | Cria uma geração nova de dados fictícios de demonstração. Só roda com o banco identificado como `dev` ou `hml`, o processo dizendo o mesmo ambiente (`SAFRION_AMBIENTE`) e o nome repetido no comando; em produção, recusa sem tocar em nada. Nada é apagado: movimento e auditoria são imutáveis |
| `pnpm run test:e2e` | Jornadas de navegador (Playwright), no desktop e no celular, com login DEV, dados fictícios e banco real. Rode depois de `pnpm run build`; precisa do Chrome e de `SAFRION_TEST_DATABASE_URL` com o administrador de um PostgreSQL/PostGIS descartável |
| `python3 tools/docs/checar_docs.py` | Confere a integridade da documentação: arquivos obrigatórios, IDs sem repetição, decisões e links |
| `python3 -m unittest discover -s tools/ci` | Regressões dos portões da CI (segredos, Trivy, Semgrep, contrato de código, jornadas e proteção da `main`) |
| `python3 -m unittest discover -s infra/terraform -p 'test_*.py'` e `python3 infra/terraform/checar_travas.py` | Guard e travas da infraestrutura da homologação, sem credencial nem nuvem |

Os comandos `pnpm dev` na raiz e `test:load` do PRD 23.4 **ainda não existem**. Os nomes `setup` e `doctor` do PRD coincidem com comandos do próprio pnpm, então se chamam com `pnpm run`.

## Para quem desenvolve
- **Editor:** VS Code, com o terminal integrado (zsh no Mac). Os comandos acima não dependem do editor. As extensões oficiais do Claude Code e do Codex são opcionais; outro editor só entra com ganho demonstrado numa tarefa real.
- **Acesso:** conta individual no GitHub, com o mínimo de permissão. Nenhum segredo ou dado real em configuração do editor, extensão ou arquivo versionado.
- **Trabalho:** um checkout ou worktree e uma branch por autor e tarefa, com os arquivos reservados antes de editar. Revisão e integração seguem o [`CONTRIBUTING.md`](CONTRIBUTING.md).
