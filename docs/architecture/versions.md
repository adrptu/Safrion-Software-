# Versões fixadas (PRD 23.1)

Fixadas em 27/09/2026 no primeiro commit executável (F0-a), com versões exatas, estáveis e compatíveis entre si. Nunca `latest` nem versão experimental. Quem muda uma versão confere a fonte oficial na data, cita a fonte e roda `pnpm run check`.

**Quarentena de 7 dias** (`minimumReleaseAge: 10080` no `pnpm-workspace.yaml`): nenhuma dependência, direta ou indireta, entra com menos de 7 dias de publicada. É a proteção contra versão maliciosa recém-publicada no registro. Exceção só com motivo registrado no PR (`minimumReleaseAgeExclude`). Prova de 27/09: pedir o Vitest 5.0.2, de 2 dias, foi recusado.

## Em uso

| Componente | Versão | Publicada em | Fonte (consultada em 27/09/2026) | Suporte | Motivo | Próxima revisão |
|---|---|---|---|---|---|---|
| Node.js | 24.21.0 LTS "Krypton" | 07/09/2026 | `nodejs.org/dist/index.json`; checksum em `nodejs.org/dist/v24.21.0/SHASUMS256.txt` | Manutenção a partir de 20/10/2026; fim em 30/04/2028 (`github.com/nodejs/Release`, `schedule.json`) | LTS vigente pedido pelo PRD 23.1 | Node 26 vira LTS em 28/10/2026: avaliar a troca depois dessa data |
| pnpm | 12.5.1 | 18/09/2026 | `registry.npmjs.org/pnpm` | Linha 12 atual | Gerenciador do PRD (23.1), com lockfile e quarentena | Mensal, respeitando a quarentena |
| TypeScript | 6.0.3 | 16/04/2026 | `registry.npmjs.org/typescript` | Linha 6 | **Não é a 7.0.2** (mais recente): o typescript-eslint 8.70 declara `typescript >=4.8.4 <6.1.0` | Quando o typescript-eslint aceitar a 7 |
| typescript-eslint | 8.70.0 | 07/09/2026 | `registry.npmjs.org/typescript-eslint` (peer: eslint 8.57–10; typescript < 6.1) | Linha 8 | Regras tipadas (ENG-008, ENG-009) | Mensal |
| ESLint / @eslint/js | 10.11.0 / 10.0.1 | 18/09/2026 / 06/02/2026 | `registry.npmjs.org` | Linha 10 | Configuração flat (ENG-008) | Mensal |
| Prettier | 3.9.8 | 17/09/2026 | `registry.npmjs.org/prettier` | Linha 3 | Formatação separada da análise (ENG-010) | Mensal |
| Vitest / @vitest/coverage-v8 | 5.0.1 | 15/09/2026 | `registry.npmjs.org/vitest` (peer: vite 6.4–8) | Linha 5 | Testes e cobertura (ENG-032) | Mensal |
| Vite | 8.3.0 | 10/09/2026 | `registry.npmjs.org/vite` (node ^20.19 ou ≥22.12) | Linha 8 | Peer obrigatório do Vitest 5 | Junto com o Vitest |
| fast-check | 4.10.2 | 19/09/2026 | `registry.npmjs.org/fast-check` | Linha 4 | Testes de propriedade (PRD 23.1) | Mensal |
| @types/node | 24.13.6 | 19/09/2026 | `registry.npmjs.org/@types/node` | Linha 24, igual ao Node | Tipos do runtime | Junto com o Node |
| pg (node-postgres) / @types/pg | 8.23.0 / 8.23.1 | 08/08/2026 / 17/08/2026 | `registry.npmjs.org/pg`, `registry.npmjs.org/@types/pg` | Linha 8 | Driver do PostgreSQL com SQL explícito: transação, RLS por `set_config` e SAVEPOINT sob controle (F0-b) | Mensal |
| @testcontainers/postgresql | 12.1.0 | 04/08/2026 | `registry.npmjs.org/@testcontainers/postgresql` | Linha 12 | Banco real nos testes de integração (ENG-034); scripts de instalação nativos desligados em `allowBuilds` | Mensal |
| Imagem de teste PostgreSQL + PostGIS | `postgis/postgis:17-3.5@sha256:01a6a70e41e6c4467c8f55f6063555ed72db2d6662cd0d571040d42eadaeb6f6` | 31/08/2026 | `hub.docker.com/v2/repositories/postgis/postgis/tags/17-3.5` | PostgreSQL 17; PostGIS 3.5 é o par do PG 17 no Cloud SQL (R-006) | Mesmo motor e mesma linha da HML; a versão exata do PostGIS aparece no log da primeira execução na CI | Junto com a versão do Cloud SQL da HML |
| Zod | 4.6.5 | 13/09/2026 | `registry.npmjs.org/zod` | Linha 4 | Validação em tempo de execução dos contratos externos (ENG-014): pedido, dados, recibo e erro (`@safrion/contracts`) | Mensal |
| decimal.js | 10.6.0 | 06/07/2025 | `registry.npmjs.org/decimal.js` | Estável | Decimal com 34 algarismos significativos e ROUND_HALF_UP (PRD 10.0, ENG-013) | Anual ou em alerta de segurança |
| Semgrep CE | 1.178.0 | Consultada em 28/09/2026 | `pypi.org/pypi/semgrep/1.178.0/json` e registro oficial `semgrep/semgrep` | CE local, sem conta | Duas regras locais com fixtures positivas/negativas e inventário obrigatório; imagem fixada pelo digest no workflow, execução sem rede | Mensal ou em alerta de segurança, reexecutando fixtures e provas contra falso verde |
| Next.js / @next/eslint-plugin-next | 16.3.5 | 11/09/2026 | `registry.npmjs.org/next` (consultada em 28/09/2026) | Linha 16 | Aplicação web da F0-c (ADR 0004): App Router, rotas de servidor, `proxy.ts` com CSP por nonce; regras do Next no ESLint | Mensal |
| React / React DOM / @types/react | 19.3.0 | 09/09/2026 | `registry.npmjs.org/react` (28/09/2026) | Linha 19 | Par exigido pelo Next 16.3 | Junto com o Next |
| eslint-plugin-react-hooks | 7.1.1 | 17/04/2026 | `registry.npmjs.org/eslint-plugin-react-hooks` (28/09/2026) | Linha 7 | Regras dos hooks; o eslint-config-next não entra porque os plugins de React, import e jsx-a11y dele ainda não aceitam o ESLint 10 | Junto com o Next |
| Playwright (@playwright/test) | 1.63.0 | 04/09/2026 | `registry.npmjs.org/@playwright/test` (28/09/2026) | Linha 1 | Ponta a ponta da F0-c (B2) no Chrome do sistema (`channel: 'chrome'`), sem baixar navegador; na CI, instalar o navegador é passo da esteira | Mensal |
| @axe-core/playwright / axe-core | 4.13.0 | 11/08/2026 / 05/08/2026 | `registry.npmjs.org/@axe-core/playwright` (28/09/2026) | Linha 4 | Acessibilidade WCAG 2.2 A/AA medida em cada tela nos testes ponta a ponta (a regra jsx-a11y do ESLint fica fora pelo ESLint 10) | Mensal |

## A fixar quando entrarem (não instalados e não testados, portanto sem número aqui)
Prisma (não adotado na F0-b: SQL explícito com `pg`, ADR 0003), versão do PostgreSQL da HML no Cloud SQL, Dexie e Workbox, Terraform e provedor Google. Cada um entra no PR que o usa, com fonte e data, sob a mesma quarentena.
