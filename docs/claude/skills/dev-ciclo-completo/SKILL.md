---
name: dev-ciclo-completo
description: Conduza entregas de software por fatias verificáveis, da descoberta à operação. Use ao criar produto, implementar função, corrigir bug ou preparar entrega; adapte a fundação ao estágio e ao risco.
---

# Ciclo completo de desenvolvimento

**Norte:** entregar uma fatia útil, verificável e operável por vez, com controles proporcionais ao risco. O primeiro commit prepara o necessário para a próxima entrega; não antecipa todo o produto.

PRD, arquitetura e instruções do projeto prevalecem sobre os exemplos deste guia. Assets são pontos de partida: conferir versões, permissões e adequação antes de incorporá-los. Um protótipo deve permanecer identificado como protótipo.

**"Pronto" = Definition of Done ([assets/definition-of-done.md](assets/definition-of-done.md)) cumprida e verificada rodando.** Nunca dizer "funciona" sem ter executado lint, tipos e testes e visto a saída.

---

## Fase 0 — Descoberta (1 rodada de perguntas, não um interrogatório)
**Primeiro, conferir o benchmark** (`benchmark-top5`): reutilizar a pesquisa pertinente e atual do projeto; pesquisar cinco referências relevantes quando o módulo ainda não estiver coberto. Não repetir pesquisa em cada ajuste ou correção.

Em software de agronegócio ou gestão, ler também `agro-gestao-conhecimento` (entidades, fórmulas, indicadores e normas das disciplinas) antes de modelar dados.

Depois, descobrir só o que muda a arquitetura; o resto decide-se com padrões sensatos e informa-se a decisão:
- Quem usa e qual a tarefa principal (→ `ux-essencial`).
- Entidades do domínio, estados de cada uma, ação primária por estado e seções do detalhe (→ `master-detail-ux`; toda entidade nasce com listagem e detalhe).
- Volume esperado (usuários, registros, requisições) e crescimento.
- Restrições: stack existente, hospedagem, integrações, LGPD/dados sensíveis, prazo.
- Multi-tenant? Offline? Tempo real? Pagamentos?

## Fase 1 — Arquitetura (decidir e registrar)
- Registrar decisões em ADRs curtos ([assets/ADR-template.md](assets/ADR-template.md)) em `docs/adr/`.
- **Monólito modular primeiro** (módulos por domínio, fronteiras claras); microsserviços só com motivo concreto (times separados, escala desigual).
- **Tecnologia "chata" e comprovada**; novidade só quando resolve um problema real.
- Stack padrão quando o usuário não tem preferência:

| Camada | Padrão |
|---|---|
| Linguagem | TypeScript estrito (web/API); Python 3.12+ (dados/IA); Kotlin/Swift quando nativo for exigido |
| Web | Next.js (App Router) ou Vite + React; Tailwind + tokens M3 (`ux-essencial`) |
| API | Fastify/NestJS (TS) ou FastAPI (Py); OpenAPI gerado do código |
| Mobile | Expo (React Native) ou Flutter; nativo só por exigência de plataforma |
| Dados | PostgreSQL; Prisma/Drizzle (TS) ou SQLAlchemy (Py); Redis para cache/filas |
| Testes | Vitest + Testing Library + Playwright; pytest; Maestro/Detox (mobile) |
| Infra | Docker; GitHub Actions; PaaS (Vercel/Fly.io/Cloud Run) → Kubernetes só quando necessário |
| Observabilidade | Sentry + OpenTelemetry + logs estruturados |

Detalhes por camada: `dev-backend`, `dev-frontend-mobile`, `dev-infra`.

## Fase 2 — Fundação do repositório (antes da primeira feature)
No produto novo, preparar a fundação necessária à primeira fatia. Em projeto existente, verificar antes de acrescentar:
1. `git init`, `.gitignore`, `.editorconfig`, `README.md` (como rodar em 3 comandos).
2. Gerenciador de pacotes com lockfile e versões fixadas; `.nvmrc`/`.python-version`.
3. **Lint + formatação + tipos estritos** (`dev-revisao`, assets prontos) — zero warnings tolerados.
4. **Testes** configurados com um teste real passando (`dev-testes`).
5. **Pre-commit** (lint-staged) e **CI** rodando lint → tipos → testes → build em todo PR (`dev-infra/assets/ci.yml`).
6. `.env.example` + validação das variáveis no boot; nunca segredo no repositório.
7. Ambiente reproduzível; Docker/Compose quando forem a solução escolhida, só com serviços realmente usados.
8. Para serviços executáveis: health/readiness, logs e tratamento de erros; escolher ferramentas conforme requisitos, sem contratar serviços por padrão.
9. `AGENTS.md` com comandos, convenções e decisões; `CLAUDE.md` referencia a mesma fonte quando houver Claude Code.

Checks aplicáveis configurados e executados antes de liberar a fatia. Se a CI remota estiver bloqueada externamente, continuar o trabalho local autorizado com evidência e declarar a pendência; não marcar CI verde nem liberar uma versão que dependa dessa verificação.

## Fase 3 — Implementação
- **Fatias verticais**: cada entrega atravessa UI → API → banco e é usável sozinha. Nada de "primeiro todo o backend".
- **TDD no comportamento de produto** (`dev-testes`): teste que falha → código mínimo → refatorar. Bug reportado pede regressão que reproduza o defeito; não inventar testes para texto, instruções ou ajustes visuais triviais sem risco comportamental.
- **Commits pequenos e atômicos**, Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`), branches curtas e PRs coesos, fáceis de revisar. Tamanho e duração são sinais de revisão, não limites que fragmentam uma entrega; seguir `dev-revisao`.
- **Feature flags** para o que não pode ir ao ar de uma vez; nada de branch de meses.
- **Sem redundância**: antes de escrever, procurar se já existe (função, componente, util, pacote). Regra dos 3: na terceira repetição, extrair. Sem copiar/colar blocos.
- **Sem código morto**: sem arquivos/funções/flags não usados, sem `TODO` sem issue, sem código comentado.
- **Tratamento de erro obrigatório**: toda chamada externa (rede, disco, banco) tem timeout, erro tratado e mensagem útil; nada de `catch {}` vazio, `any`, `// eslint-disable`, `@ts-ignore`, `as unknown as`.
- **Aritmética e tempo corretos**: dinheiro e taxas com precisão definida (inteiro/decimal); instantes em UTC com fuso na exibição; datas civis sem conversão indevida de dia; identificadores conforme o contrato do projeto.
- Atualizar docs/ADR/README no mesmo PR que muda o comportamento.

## Fase 4 — Revisão (`dev-revisao`)
Self-review → automação (lint, tipos, testes, cobertura, segurança, duplicação) → revisão com checklist → squash merge. Nada entra com pipeline vermelho ou com "arrumo depois".

## Fase 5 — Entrega (`dev-infra`)
Deploy automatizado; migrações versionadas com recuperação testada e compatibilidade; homologação isolada com o mesmo artefato candidato. Produção segue os gates do projeto, incluindo aceite humano quando exigido. No Safrion, o proprietário aprova explicitamente a versão após homologação.

## Fase 6 — Operação
SLOs definidos (disponibilidade, p95 de latência, taxa de erro) com alertas que acordam alguém só quando o usuário sente; dashboards; backups testados com restauração; post-mortem sem culpa para todo incidente, gerando teste + correção; dependências atualizadas semanalmente (Renovate/Dependabot).

---

## Regras de conduta do agente
1. Dimensionar a fundação ao escopo: uma tela em sistema existente reutiliza a base; um protótipo explícito não implica provisionar produção.
2. Ao mexer em projeto existente: respeitar as convenções dele; se faltar lint/testes/CI, propor e adicionar de forma incremental (não reescrever tudo).
3. Antes de declarar concluído: executar os checks aplicáveis à mudança e informar resultado, versão e limitações. Comando configurado não equivale a executado; não inventar comandos ausentes.
4. Toda funcionalidade nova vem com testes no mesmo commit; todo bug vem com teste de regressão.
5. Preferir remover código a adicionar. Cada abstração precisa justificar-se com uso real (≥ 2 chamadores).
6. Se algo do padrão não se aplicar (script descartável, protótipo explícito), dizer isso e o que foi omitido.
