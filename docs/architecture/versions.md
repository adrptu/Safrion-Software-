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
| decimal.js | 10.6.0 | 06/07/2025 | `registry.npmjs.org/decimal.js` | Estável | Decimal com 34 algarismos significativos e ROUND_HALF_UP (PRD 10.0, ENG-013) | Anual ou em alerta de segurança |

## A fixar quando entrarem (não instalados e não testados, portanto sem número aqui)
Next.js e React, Prisma, PostgreSQL e PostGIS (par oferecido pelo Cloud SQL), Playwright, Testcontainers, Zod, Dexie e Workbox, Terraform e provedor Google. Cada um entra no PR que o usa, com fonte e data, sob a mesma quarentena.
