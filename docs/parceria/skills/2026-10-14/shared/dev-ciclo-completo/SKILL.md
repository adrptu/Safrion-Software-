---
name: dev-ciclo-completo
description: Conduza entregas de software por fatias verificáveis, da descoberta à operação. Use ao criar produto, implementar função, corrigir bug ou preparar entrega; adapte a fundação ao estágio e ao risco.
---

# Ciclo completo de desenvolvimento

## Entrega identificada e continuidade

Antes de editar, delimite resultado, IDs vigentes, base, arquivos/trechos, autor, revisor e aceite na tarefa existente. Em colaboração, mantenha uma autoria ativa por agente e contratos separados; encaminhe entregas prontas imediatamente e avance no próximo trabalho autorizado e independente. Não confunda ausência de ACK com ociosidade nem crie outra fila para retomar.

Registre estados distintos: implementado, revisado, integrado, publicado e homologado. Uma camada sintética, CI verde ou publicação parcial não conclui o produto. Preserve o trabalho válido e os requisitos pendentes. A revisão de PRD confronta decisões aprovadas e comportamento validado, sem legitimar defeitos já implementados; reutilize referências do design system. Os gatilhos específicos do Safrion ficam em `safrion-equipe`.


**Norte:** entregar uma fatia útil, verificável e operável por vez, com controles proporcionais ao risco. O primeiro commit prepara o necessário para a próxima entrega; não antecipa todo o produto.

PRD, arquitetura e instruções do projeto prevalecem sobre os exemplos deste guia. Assets são pontos de partida: conferir versões, permissões e adequação antes de incorporá-los. Um protótipo deve permanecer identificado como protótipo.

**"Pronto" = Definition of Done ([assets/definition-of-done.md](assets/definition-of-done.md)) cumprida e verificada rodando.** Nunca dizer "funciona" sem evidência pertinente: comportamento executável pede execução; alteração documental pede leitura e validação documental. Execute os checks aplicáveis e exigidos pelo projeto.

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
- Exemplos para projeto sem stack definida; decisão vigente prevalece, sem instalar a tabela inteira:

| Camada | Padrão |
|---|---|
| Linguagem | TypeScript estrito (web/API); Python 3.12+ (dados/IA); Kotlin/Swift quando nativo for exigido |
| Web | Next.js (App Router) ou Vite + React; Tailwind + tokens M3 (`ux-essencial`) |
| API | Fastify/NestJS (TS) ou FastAPI (Py); OpenAPI gerado do código |
| Mobile | Expo (React Native) ou Flutter; nativo só por exigência de plataforma |
| Dados | PostgreSQL; Prisma/Drizzle (TS) ou SQLAlchemy (Py); Redis somente se houver necessidade de cache/filas |
| Testes | Vitest + Testing Library + Playwright; pytest; Maestro/Detox (mobile) |
| Infra | Docker; GitHub Actions; PaaS (Vercel/Fly.io/Cloud Run) → Kubernetes só quando necessário |
| Observabilidade | Sentry + OpenTelemetry + logs estruturados |

Detalhes por camada: `dev-backend`, `dev-frontend-mobile`, `dev-infra`.

## Fase 2 — Fundação do repositório (antes da primeira feature)
No produto novo, preparar a fundação necessária à primeira fatia. Em projeto existente, verificar antes de acrescentar:
1. `git init`, `.gitignore`, `.editorconfig`, `README.md` (como rodar em 3 comandos).
2. Gerenciador de pacotes com lockfile e versões fixadas; `.nvmrc`/`.python-version`.
3. **Lint + formatação + tipos estritos** (`dev-revisao`, assets prontos) — conforme a política do projeto, sem ocultar avisos para liberar a entrega.
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
- **Tratamento de erro obrigatório**: toda chamada externa (rede, disco, banco) tem timeout, erro tratado e mensagem útil; não use `catch {}` vazio nem supressão de tipos/lint para esconder defeito. Exceções estreitas só quando a política do projeto permitir, com justificativa e revisão; siga `dev-revisao`.
- **Aritmética e tempo corretos**: dinheiro e taxas com aritmética decimal e escala explícita conforme o contrato do projeto (no Safrion, ENG-013); instantes em UTC com fuso na exibição; datas civis sem conversão indevida de dia; identificadores conforme o contrato do projeto.
- Atualizar docs/ADR/README no mesmo PR que muda o comportamento.

## Fase 4 — Revisão (`dev-revisao`)
Autorrevisão → checks aplicáveis → revisão independente → integração segundo a política do projeto. O revisor integra o PR do outro quando esse for o contrato; ninguém aprova ou integra o próprio PR no Safrion. Check exigido falho ou indisponível permanece pendente.

## Fase 5 — Entrega (`dev-infra`)
Deploy automatizado; migrações versionadas com recuperação testada e compatibilidade; homologação isolada com o mesmo artefato candidato. Produção segue os gates do projeto, incluindo aceite humano quando exigido. No Safrion, o proprietário aprova explicitamente a versão após homologação.

## Fase 6 — Operação
SLOs definidos (disponibilidade, p95 de latência, taxa de erro) com alertas que acordam alguém só quando o usuário sente; dashboards; backups testados com restauração; análise sem culpa e ações proporcionais ao incidente; manutenção de dependências conforme política do projeto.

---

## Regras de conduta do agente
1. Dimensionar a fundação ao escopo: uma tela em sistema existente reutiliza a base; um protótipo explícito não implica provisionar produção.
2. Ao mexer em projeto existente: respeitar as convenções dele; se faltar lint/testes/CI, propor e adicionar de forma incremental (não reescrever tudo).
3. Antes de declarar concluído: executar os checks aplicáveis à mudança e informar resultado, versão e limitações. Comando configurado não equivale a executado; não inventar comandos ausentes.
4. Proteja os comportamentos alterados com verificações proporcionais. Para defeito, reproduza o cenário e acrescente regressão quando viável; não crie testes que só espelhem texto ou implementação.
5. Preferir remover código a adicionar. Cada abstração precisa justificar-se com uso real (≥ 2 chamadores).
6. Se algo do padrão não se aplicar (script descartável, protótipo explícito), dizer isso e o que foi omitido.
