# Do Talhão à O.S.

Plataforma de gestão agrícola integrada: planejamento da safra, planos agronômicos, ordens de serviço com aprovação agronômica, almoxarifado integrado, app de campo com operação sem internet, compras, estoque e custos.

**Estado:** documentação e CI. Ainda não há código de produto. Veja [`docs/STATUS.md`](docs/STATUS.md).

## Onde está cada coisa
| O quê | Onde |
|---|---|
| Contrato do produto (PRD v3.10 vigente; v3.9 no histórico) | [`docs/PRD.md`](docs/PRD.md) |
| Fluxogramas com raias | [`docs/prd/fluxogramas/`](docs/prd/fluxogramas/) |
| Decisões e ADRs | [`docs/DECISIONS.md`](docs/DECISIONS.md), [`docs/adr/`](docs/adr/) |
| Design system | [`docs/design-system/`](docs/design-system/) |
| Instruções para agentes (fonte única) | [`AGENTS.md`](AGENTS.md); o `CLAUDE.md` importa esse arquivo |
| Como contribuir | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Parceria Claude + Codex | [`docs/parceria/`](docs/parceria/) |
| Protótipo navegável (validação) | https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo |

## Comandos que existem hoje
| Comando | O que faz |
|---|---|
| `python3 tools/docs/checar_docs.py` | Confere a integridade da documentação: arquivos obrigatórios, IDs sem repetição, decisões e links |

Os comandos `pnpm setup`, `pnpm dev`, `pnpm check` e os demais do PRD 23.4 **ainda não existem**. Eles serão criados no primeiro incremento de código.
