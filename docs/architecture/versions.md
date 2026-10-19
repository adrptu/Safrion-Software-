# Versões fixadas (PRD 23.1)

Fixadas em 27/09/2026 no primeiro commit executável (F0-a), com versões exatas, estáveis e compatíveis entre si. Nunca `latest` nem versão experimental. Quem muda uma versão confere a fonte oficial na data, cita a fonte e roda `pnpm run check`.

**Quarentena de 7 dias** (`minimumReleaseAge: 10080` no `pnpm-workspace.yaml`): nenhuma dependência, direta ou indireta, entra com menos de 7 dias de publicada. É a proteção contra versão maliciosa recém-publicada no registro. Exceção só com motivo registrado no PR (`minimumReleaseAgeExclude`). Prova de 27/09: pedir o Vitest 5.0.2, de 2 dias, foi recusado.

## Atualizações automáticas — ATUALIZA-01

O alvo é a versão estável mais recente **compatível e verificada**, incluindo mudanças de major. Uma versão nova gera candidata; não altera produção. Node deve permanecer em LTS suportada e banco precisa de migração/recuperação ensaiadas. Incompatibilidades ficam no PR existente com motivo e condição de retomada, em vez de congelar a stack sem prazo.

- Dependabot verifica **Actions diariamente**, com 7 dias de quarentena e até 2 PRs. Renovate não atualiza essas mesmas Actions.
- `renovate.json` prepara consulta diária das demais dependências, no executor remoto do bot: pacotes diretos, lockfile/transitivos, Node, pnpm, imagens/digests, inputs de ferramentas nos workflows e Terraform/provider. Até 2 PRs de versão em aberto; conjuntos acoplados atualizam juntos; manutenção de lock semanal. Não roda scripts de instalação, não faz merge, apply ou deploy.
- Mantêm-se pins exatos, SHAs/digests, `--frozen-lockfile`, scanners e testes existentes. Major também vira PR, com revisão de migração, exceto as linhas de Node/tipos e PostgreSQL/PostGIS temporariamente vinculadas ao runtime homologado abaixo. Segurança aplicável tem prioridade; redução de quarentena requer motivo revisado na própria correção.
- O bot propõe; a equipe resolve quebra de API, peers, testes e pins auxiliares. A integração requer CI e pareceres pertinentes da equipe; produção continua exigindo aceite da candidata por Adrianus.

| Cobertura | Mecanismo e limite |
|---|---|
| Next/React, bibliotecas, lint, testes, driver e pnpm | Managers npm + lock; regeneração real dos dois documentos do `pnpm-lock.yaml` e instalação frozen comprovadas localmente com Renovate44.116.1/pnpm12.5.1; ensaio hospedado/cold-cache ainda pendente. |
| Node | `.nvmrc`, engines e imagem de build; conferir a mesma versão efetiva no Docker/CI e LTS nas fontes antes de integrar; bot mantém Node24/tipos24; revisar a restrição junto da próxima LTS em 28/10/2026, conforme tabela. Não avançar tipos isoladamente para outro major. |
| Imagens de runtime, Semgrep, PostGIS | Docker + regex para pins em env/TypeScript; Semgrep inclui asserção do scanner no mesmo grupo. linha17-3.5 alinhada à HML; outra linha exige alterar a restrição no mesmo PR da migração Cloud SQL/guard. Digests das imagens base agrupados semanalmente. |
| Actions, Python e Trivy | Dependabot para SHAs das Actions; Renovate para inputs/imagens. Python minor é canal, não pin de patch. Chrome/Docker/SO herdados de `ubuntu-latest` são mantidos pelo GitHub e verificados pela CI; não são geridos como dependências do produto. |
| Gitleaks e TFLint | Versão e checksum de release via `github-release-attachments`, sem remover a conferência de hash. TFLint entra quando o workflow de infra for integrado. |
| Terraform CLI/provider | Manager Terraform atualiza constraints e lock; regex cobre CLI no workflow de infra, no mesmo grupo do required_version/provider. **O SHA do zip da CLI HashiCorp ainda precisa ser obtido/conferido pela equipe no mesmo PR**; hash antigo falha fechado. Não declarar esta etapa automática antes da prova. |
| Serviços gerenciados e modelos de IA | Mudanças de API, manutenção do banco e novos modelos exigem revisão de contrato/custo/comportamento. O bot não troca projeto, região, banco, modelo ou serviço apenas por existir versão mais nova. |

**Ativação:** esta configuração ainda não comprova executor ativo. Precisa entrar na branch padrão após revisão independente e o GitHub App Renovate precisa estar instalado somente neste repositório, com recibo real de extração, atualização do lock e primeiro PR/CI. Não usa token pessoal nem depende do Mac. Até lá, somente Dependabot já existente está configurado; o recebimento de PR confirma operação, não este texto. Erros de bot/registro/lock ficam visíveis no PR/log e no checkpoint da issue1, sem outra fila de trabalho.

**Limite da quarentena:** Renovate exige timestamp do registro; se faltar, a atualização permanece retida para investigação. Para digests, a data pode ser da tag e não do blob; revisão de origem permanece necessária. Atualização pendente, falha de consulta ou PR vermelho nunca significa stack atualizada.

Fontes oficiais conferidas em 28/09/2026: [managers Renovate](https://docs.renovatebot.com/modules/manager/), [npm/lock](https://docs.renovatebot.com/modules/manager/npm/), [Actions e inputs](https://docs.renovatebot.com/modules/manager/github-actions/), [Terraform](https://docs.renovatebot.com/modules/manager/terraform/), [idade de releases](https://docs.renovatebot.com/key-concepts/minimum-release-age/), [suporte Dependabot](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories). Dependabot documenta pnpm até10 e Terraform até1.15.x; isso não prova falha no12/1.16, mas impede prometer cobertura sem ensaio.

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
| Next.js / @next/eslint-plugin-next | 16.3.8 | 30/09/2026 | `registry.npmjs.org/next` (consultada em 09/10/2026) | Linha 16 | Aplicação web da F0-c (ADR 0004): App Router, rotas de servidor, `proxy.ts` com CSP por nonce; regras do Next no ESLint. 16.3.8 corrige CVE-2026-94483 (HIGH) acusado na imagem web | Mensal ou em alerta de segurança |
| sharp (transitiva opcional do Next) | 0.35.5 | 27/09/2026 | `registry.npmjs.org/sharp` (consultada em 09/10/2026) | Linha 0.35 | Piso por `overrides` no `pnpm-workspace.yaml`: o Next aceita ^0.35.4 e a 0.35.5 corrige GHSA-wq5f-xc86-pv6w (HIGH) acusado na imagem web; script nativo segue desligado em `allowBuilds` | Junto com o Next; o piso sai quando o Next exigir a versão corrigida |
| source-map-js (transitiva do postcss e do magicast) | 1.2.2 | 30/09/2026 | `registry.npmjs.org/source-map-js` (consultada em 09/10/2026) | Linha 1 | Piso por `overrides` no `pnpm-workspace.yaml`: os dependentes aceitam ^1.2.1 e a 1.2.2 corrige CVE-2026-93749 (HIGH) acusado pelo Trivy FS no `pnpm-lock.yaml` | O piso sai quando os dependentes exigirem a versão corrigida |
| React / React DOM / @types/react | 19.3.0 | 09/09/2026 | `registry.npmjs.org/react` (28/09/2026) | Linha 19 | Par exigido pelo Next 16.3 | Junto com o Next |
| eslint-plugin-react-hooks | 7.1.1 | 17/04/2026 | `registry.npmjs.org/eslint-plugin-react-hooks` (28/09/2026) | Linha 7 | Regras dos hooks; o eslint-config-next não entra porque os plugins de React, import e jsx-a11y dele ainda não aceitam o ESLint 10 | Junto com o Next |
| Playwright (@playwright/test) | 1.63.0 | 04/09/2026 | `registry.npmjs.org/@playwright/test` (28/09/2026) | Linha 1 | Ponta a ponta da F0-c (B2) no Chrome do sistema (`channel: 'chrome'`), sem baixar navegador; na CI, instalar o navegador é passo da esteira | Mensal |
| @axe-core/playwright / axe-core | 4.13.0 | 11/08/2026 / 05/08/2026 | `registry.npmjs.org/@axe-core/playwright` (28/09/2026) | Linha 4 | Acessibilidade WCAG 2.2 A/AA medida em cada tela nos testes ponta a ponta (a regra jsx-a11y do ESLint fica fora pelo ESLint 10) | Mensal |

| openid-client | 6.8.8 | 05/09/2026 | `registry.npmjs.org/openid-client`, `github.com/panva/openid-client` (28/09/2026) | Linha 6 | Adaptador OIDC do ADR 0004: PKCE, nonce/state e validação explícita de assinatura; não gerencia sessão nem autorização | Mensal ou em alerta de segurança |

## Infraestrutura da homologação (fixada no PR #14, validada na CI, sem provisionar)

| Ferramenta | Versão | Onde está fixada | Validação |
|---|---|---|---|
| Terraform CLI | 1.16.3, com SHA-256 do pacote | `infra/terraform/*/versions.tf` (`required_version`) e `.github/workflows/infra.yml` | Jobs "Terraform — bootstrap" e "Terraform — hml": formatação, init sem backend, validate e TFLint |
| Provider Google | 8.3.0 | `infra/terraform/*/versions.tf` e o `.terraform.lock.hcl` de cada módulo | Os mesmos jobs |
| TFLint | v0.64.0, com SHA-256 do pacote | `.github/workflows/infra.yml` | Os mesmos jobs |
| PostgreSQL da HML (Cloud SQL) | 17 (`POSTGRES_17`) | `infra/terraform/hml/banco.tf` | Job "Travas de segurança do Cloud SQL"; a instância ainda não foi criada. Integração e jornadas de navegador usam `postgis/postgis:17-3.5` por digest |

A data de publicação e a fonte oficial de cada versão entram nesta tabela na próxima atualização delas (ATUALIZA-01).

## A fixar quando entrarem (não instalados e não testados, portanto sem número aqui)
Prisma (não adotado na F0-b: SQL explícito com `pg`, ADR 0003), Dexie e Workbox. Cada um entra no PR que o usa, com fonte e data, sob a mesma quarentena.
