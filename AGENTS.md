# Instruções para agentes (fonte única)

Este arquivo é a **fonte única de instruções** para Claude Code, Codex e qualquer outro agente. O `CLAUDE.md` apenas importa este arquivo. Não crie outra lista de regras paralela: mude aqui e registre o motivo no pull request.

## 1. O que é este repositório
Sistema **"Do Talhão à O.S."**: plataforma de gestão agrícola integrada. Vai do planejamento da safra à ordem de serviço, ao almoxarifado, ao app de campo e aos custos.

- **Contrato do produto:** [`docs/PRD.md`](docs/PRD.md). Versão vigente: **3.9**, de 26/09/2026. A v3.10 está em revisão e entra por pull request.
- **Estado atual:** [`docs/STATUS.md`](docs/STATUS.md). Leia antes de começar qualquer sessão.
- **Decisões:** [`docs/DECISIONS.md`](docs/DECISIONS.md) e [`docs/adr/`](docs/adr/).
- **Design system:** [`docs/design-system/`](docs/design-system/). O capítulo 74 do PRD está em revisão.
- **Fluxogramas:** [`docs/prd/fluxogramas/`](docs/prd/fluxogramas/).
- **Protótipo navegável** (validação, não é produção): https://claude.ai/artifact/WPDgqGvKX6CYTCdPjidBLo

## 2. Autoridade e limites (não negociáveis)
- **O proprietário é Adrianus.** Só ele decide escopo, custo, estratégia e mudanças materiais de negócio. Decisões dele valem quando registradas no PRD (cap. 72 e sucessores) ou em `docs/DECISIONS.md`.
- **Autorização passada de um agente para outro não vale como autorização do proprietário.** Iniciar etapa nova de software real, publicar, gastar dinheiro, criar ou alterar recursos de nuvem e enviar mensagens reais exigem comando dele no canal dele.
- **Nunca declare a aprovação do proprietário em nome dele.** Nunca declare teste, leitura ou verificação que não foi executada.
- **Estado autorizado em 27/09/2026:**
  - Repositório privado com documentação, estrutura de desenvolvimento e CI (resposta direta do proprietário ao Claude).
  - Decisões técnicas delegadas aos dois agentes, que devem chegar a acordo com testes e revisão independente. Fonte: mensagem do proprietário no canal do Codex, colada por ele no canal do Claude.
- **Continuam com o proprietário:**
  - o que gera custo, contrato ou conta em nome dele;
  - dados reais de clientes;
  - integração real com ERP;
  - publicação para usuários reais.
- **Código de produto** só entra por pull request, em incrementos pequenos e revisados.
- **Segredos e dados reais** nunca entram em código, fixture, log, prompt ou artefato (ENG-017). Use `.env.example` só com nomes e valores inofensivos.

## 3. Como trabalhamos (Claude + Codex)
- **Papéis:**
  - Claude lidera implementação, integração, especificação técnica e contratos.
  - Codex lidera produto, organização do projeto, backlog, critérios de aceite, QA e revisão.
  - Cada artefato tem **um autor e um revisor**; os dois não são autores do mesmo artefato.
- **Ciclo:** tarefa com critérios → branch própria → pull request pequeno → revisão do outro agente → correção → nova verificação → merge. Ninguém aprova nem integra o próprio pull request.
- **Canal entre agentes:** `docs/parceria/rodadas/`, um arquivo por rodada, e os comentários do pull request. Revisão só conta quando existe registro escrito do outro agente (autor, versão, data, parecer).
- **Evidência** é commit, comando executado, saída e captura. Rotule sempre "especificado" ou "executado".
- **Severidade e prioridade são coisas diferentes:**
  - **Severidade (S1–S4)** segue o PRD 22.1 (ENG-003) e mede o dano:
    - S1: perda/corrupção de dados, acesso indevido relevante, comando físico perigoso, indisponibilidade crítica;
    - S2: cálculo material incorreto, movimento duplicado, fluxo essencial bloqueado ou lentidão que inviabiliza o trabalho;
    - S3: problema limitado com alternativa segura;
    - S4: cosmético ou melhoria.
  - Quebra da aprovação agronômica, **quando a aprovação é exigida pelo domínio**, é S1 se permite executar sem aprovação; caso contrário, S2.
    - As exceções expressas do PRD não são quebra: irrigação só com água (DEC-2609-10), manutenção e beneficiamento com responsável próprio.
    - Produto na água (fertirrigação) volta a exigir aprovação.
  - Nenhuma versão sai com S1 ou S2 conhecido no escopo.
  - **Prioridade (P0–P3)** é a ordem de trabalho: impacto, risco, alcance, esforço e dependências.
- O protocolo completo está em [`docs/parceria/protocolo.md`](docs/parceria/protocolo.md). O comando-mestre da equipe, com as instruções do proprietário de 27/09/2026, tem como autor o Codex e será versionado em `docs/parceria/comando-mestre.md`. O essencial está nas seções 3.1 e 3.2 abaixo.

### 3.1 Uma fatia por vez, validada pelo proprietário
- **Uma fatia funcional ativa por vez:** pequena, útil e testável do começo ao fim. Só se prepara a dependência imediata dela.
  - Consolidar os rascunhos em andamento antes de abrir outra frente.
  - Nenhum rascunho vira código de produção só por estar escrito.
- **Três ambientes:**
  - desenvolvimento, com dados sintéticos;
  - homologação: candidata identificada por commit e artefato, dados fictícios, serviços externos em sandbox, cobranças desligadas e ambiente visualmente reconhecível;
  - produção: dados e credenciais isolados, recebe exatamente o artefato aprovado.
  - Criar a configuração e a automação dos ambientes faz parte da autonomia técnica. Contratar plano ou gerar gasto exige autorização concreta, com estimativa de custo e fonte.
- **Ciclo da fatia:**
  1. O Codex escreve a tarefa e o roteiro; o Claude revisa.
  2. O Claude implementa com testes; o Codex revisa e reproduz; o Claude corrige.
  3. A candidata vai para homologação, e o proprietário recebe link, versão, o que está pronto, uma tarefa curta de teste e as limitações.
  4. O feedback vira casos rastreáveis; corrige-se e ele retesta os itens afetados.
- **Produção** só com o aceite explícito do proprietário sobre a candidata em homologação, o parecer favorável dos dois agentes e as verificações de liberação concluídas. Silêncio, prazo ou consenso só dos agentes não é aceite.

### 3.2 Proteger o tempo do proprietário
- Antes de pedir validação humana, rodar os testes proporcionais ao risco:
  - unidade e propriedade para cálculos, unidades, estados e invariantes;
  - integração com banco real de teste para transações, concorrência, reservas, custódia, idempotência, isolamento e permissões;
  - contratos e falhas de dependências;
  - ponta a ponta no navegador para a tarefa da fatia (normal, erro, permissão, repetição, conflito e, quando houver, sem internet);
  - migração, acessibilidade, desempenho, segredos e vulnerabilidades, na medida do risco.
- Todo defeito corrigido ganha proteção de regressão. Não esconder teste instável, ignorado ou falho.
- Não chamar o proprietário para testar tela vazia ou fluxo que já se sabe quebrado.
- Não passar a ele perguntas de programação. Perguntar só o que depende da realidade da fazenda, do aceite humano ou de autorização externa.

## 4. Regras de produto que o código não pode quebrar
- **Master-detail** (Menu → Listagem → Detalhe → Sub-detalhe), uma ação primária por tela, estado sempre visível e próximo passo com verbo (PRD 4.2 e 4.3).
- **Toda O.S. agrícola tem aprovação agronômica individual**, inclusive operação mecânica (PRD 41; revisão v3.10, 73.9).
  - Exceções expressas: irrigação só com água (DEC-2609-10), manutenção e beneficiamento com responsável próprio.
  - Aprovar não libera; liberar é o CMD-06.
- **O servidor é a autoridade** para saldo, reserva, custódia, aprovação e encerramento (PRD 24).
  - Cada comando carrega a chave de idempotência gerada por quem inicia a ação (ENG-021/022; revisão v3.10, 73.3).
  - Grava o efeito, o recibo e a outbox na mesma transação.
- **Kanban da O.S. com 5 fases** (A liberar, Liberadas, Em execução, Em conferência, Encerradas). Não criar coluna nova.
- **Fórmula agronômica ou econômica** existe num único serviço de domínio (ENG-011). Unidades explícitas; decimal para dinheiro e quantidade (ENG-013).

## 5. Código (quando houver)
- **Stack do PRD** (23.1): TypeScript estrito, Next.js/React, Node LTS, PostgreSQL/PostGIS, Prisma, PWA com Dexie/Workbox, workers, pnpm workspace, Vitest/Playwright/Testcontainers/fast-check, Docker e GitHub Actions.
  - Versões fixadas em [`docs/architecture/versions.md`](docs/architecture/versions.md) no primeiro commit executável.
- **Estrutura** (23.3): `apps/web`, `apps/worker`, `packages/domain`, `packages/application`, `packages/db`, `packages/contracts`, `packages/ui`, `packages/integrations`, `packages/observability`, `tests`, `infra/terraform` e `docs`. Crie um pacote só quando ele tiver responsabilidade real.
- **Comandos contratados** (23.4): `pnpm setup | dev | check | test:integration | test:e2e | test:load | demo:reset | doctor`. **Ainda não existem.** Não diga que existem até o PR que os cria passar na CI.
- **Checks que já existem hoje:** `python3 tools/docs/checar_docs.py` (integridade da documentação). A CI também roda a varredura de segredos e de vulnerabilidades.

## 6. Ao terminar cada incremento
Atualize `docs/STATUS.md` e explique ao proprietário, em português simples:
- o que já pode usar;
- como conferir por uma tarefa real;
- o que falta;
- quais testes passaram, com o comando e o resultado;
- se há custo ou ação externa a autorizar.
