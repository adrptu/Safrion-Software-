# ADR 0001: Adotar a arquitetura e a stack de referência do PRD

- **Situação:** aceita
- **Data:** 2026-09-27
- **Autor:** Claude Code
- **Revisor:** Codex (pendente)
- **Requisitos do PRD afetados:** 12.1, 12.2, 23.1–23.3, 24, 28; ENG-006..020

## Contexto
O PRD já define arquitetura e stack. Esta ADR só registra a adoção no repositório, para que as mudanças futuras sejam decisões explícitas, e não deriva silenciosa.

## Decisão
- **Monólito modular por domínio**, com web/PWA, API de aplicação, workers separados e PostgreSQL/PostGIS como banco transacional e geográfico. Nada de dezenas de microsserviços sem necessidade demonstrada (PRD 12.1).
- **Stack:** TypeScript estrito, Next.js/React, Node.js LTS, Prisma, Dexie/Workbox, pnpm workspace, Vitest, Testing Library, Playwright, Testcontainers, fast-check, Docker, GitHub Actions e Terraform. Nuvem de referência: Google Cloud (PRD 23.1 e 28).
- **Na mesma transação:** fato ou documento, registro de idempotência, recibo e outbox. Consumidores deduplicam pelo efeito (PRD 12.2 e ENG-021/022; revisão v3.10, 73.3 e 73.6).
- **Estrutura de pastas do PRD 23.3.** Um pacote só é criado quando tem responsabilidade real.
- **Versões:** fixadas em `docs/architecture/versions.md` no primeiro commit executável. Nunca `latest`.

## Alternativas consideradas
| Alternativa | Por que não |
|---|---|
| Microsserviços desde o início | Sem necessidade demonstrada; aumenta falhas distribuídas e custo (PRD 12.1) |
| Event sourcing geral | O PRD exige ledger imutável e outbox, não event sourcing em todo domínio (revisão v3.10) |
| App nativo desde o início | O PRD prevê PWA e só troca por nativo se o aparelho-alvo não cumprir os requisitos offline (23.1) |

## Consequências
Para trocar qualquer escolha, é preciso uma ADR nova que demonstre o mesmo requisito (PRD 12.1). A preferência pessoal não basta.

## Verificação
Checks de fronteira de pacotes e de ciclos na CI (ENG-012), quando houver código. Revisão do Codex nos pull requests de arquitetura.
