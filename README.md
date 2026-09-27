# Do Talhão à O.S.

Plataforma de gestão agrícola integrada: planejamento da safra, planos agronômicos, ordens de serviço com aprovação agronômica, almoxarifado integrado, app de campo com operação sem internet, compras, estoque e custos.

**Estado:** fundação F0-a — o pacote de domínio (`packages/domain`), com decimal, unidades e saldo por lote, ainda sem banco, API ou tela. Veja [`docs/STATUS.md`](docs/STATUS.md).

## Onde está cada coisa
| O quê | Onde |
|---|---|
| Contrato do produto (PRD v3.9 vigente) | [`docs/PRD.md`](docs/PRD.md) |
| Fluxogramas com raias | [`docs/prd/fluxogramas/`](docs/prd/fluxogramas/) |
| Decisões e ADRs | [`docs/DECISIONS.md`](docs/DECISIONS.md), [`docs/adr/`](docs/adr/) |
| Design system | [`docs/design-system/`](docs/design-system/) |
| Instruções para agentes (fonte única) | [`AGENTS.md`](AGENTS.md); o `CLAUDE.md` importa esse arquivo |
| Como contribuir | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
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
| `pnpm run lint` | ESLint e o script de fronteiras: pacote sem dependência não declarada e sem ciclo de imports (ENG-012) |
| `pnpm run test` | Testes com cobertura mínima de 95 % em cada arquivo do domínio (ENG-032/033) |
| `python3 tools/docs/checar_docs.py` | Confere a integridade da documentação: arquivos obrigatórios, IDs sem repetição, decisões e links |

Os comandos `pnpm dev`, `test:integration`, `test:e2e`, `test:load` e `demo:reset` do PRD 23.4 **ainda não existem**: entram na F0-b e na F0-c. Os nomes `setup` e `doctor` do PRD coincidem com comandos do próprio pnpm, então se chamam com `pnpm run`.
