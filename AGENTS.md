# Instruções para agentes (fonte única)

Este arquivo é a **fonte única de instruções** para Claude Code, Codex e qualquer outro agente. O `CLAUDE.md` apenas importa este arquivo. Não crie outra lista de regras paralela: mude aqui e registre o motivo no pull request.

## 0. Missão
Fazer diferença real na melhoria, na evolução e no sucesso contínuo da agricultura brasileira, com gestão, inteligência e automação simples, intuitivas, objetivas e essenciais (pedido do proprietário, 27/09/2026).
- O valor se mede por esforço poupado, erros evitados e resultado verificado na fazenda. Nada de promessa sem evidência.
- Minimalismo e essencialismo valem para produto, PRD, código, fluxograma e mensagens (§3.4), sem remover controle necessário ao trabalho correto.

## 1. O que é este repositório
Sistema **"Do Talhão à O.S."**: plataforma de gestão agrícola integrada. Vai do planejamento da safra à ordem de serviço, ao almoxarifado, ao app de campo e aos custos.

- **Contrato do produto:** [`docs/PRD.md`](docs/PRD.md). Versão vigente: **3.11**, de 27/09/2026, que inclui a v3.10 (registro em [`docs/prd/v3_10-reconciliacao.md`](docs/prd/v3_10-reconciliacao.md)). As decisões pendentes do proprietário (73.12, 74.12 e 75.8) continuam pendentes e não valem como aprovadas.
- **Estado atual:** [`docs/STATUS.md`](docs/STATUS.md). Leia antes de começar qualquer sessão.
- **Decisões:** [`docs/DECISIONS.md`](docs/DECISIONS.md) e [`docs/adr/`](docs/adr/).
- **Design system:** [`docs/design-system/`](docs/design-system/). É o capítulo 74 do PRD; `tokens.json`, espécime e tabela de contraste ainda não estão no repositório.
- **Fluxogramas:** [`docs/prd/fluxogramas/`](docs/prd/fluxogramas/).
- **Protótipo navegável** (validação, não é produção): https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm. Segue o regime leve da seção 3.5.

## 2. Autoridade e limites (não negociáveis)
- **O proprietário é Adrianus.** Só ele decide escopo, custo, estratégia e mudanças materiais de negócio. Decisões dele valem quando registradas no PRD (cap. 72 e sucessores) ou em `docs/DECISIONS.md`.
- **Autorização passada de um agente para outro não vale como autorização do proprietário.** Iniciar etapa nova de software real, publicar, gastar dinheiro, criar ou alterar recursos de nuvem e enviar mensagens reais exigem comando dele no canal dele.
- **Nunca declare a aprovação do proprietário em nome dele.** Nunca declare teste, leitura ou verificação que não foi executada.
- **Estado autorizado em 27/09/2026:**
  - Repositório privado com documentação, estrutura de desenvolvimento e CI (resposta direta do proprietário ao Claude).
  - Decisões técnicas delegadas aos dois agentes, que devem chegar a acordo com testes e revisão independente. Fonte: mensagem do proprietário no canal do Codex, colada por ele no canal do Claude.
  - **Merge na `main` entre os agentes** (proprietário, 09/10/2026: "Faça o merge entre voce e claude, nao quero trabalho pra mim", corrigido em seguida para "entre vc e codex"). O revisor integra o PR do outro com a CI verde no HEAD e um parecer favorável escrito no PR. O proprietário não é chamado para integrar. Ninguém integra o próprio PR (DEC-0910-02).
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
  - Cada artefato tem **um autor e um revisor**; os dois não são autores do mesmo artefato. No protótipo, a revisão não bloqueia (3.5).
- **Ciclo:** tarefa com critérios → branch própria → pull request pequeno → revisão do outro agente → correção → nova verificação → merge pelo revisor (2, DEC-0910-02). Ninguém aprova nem integra o próprio pull request. PR que a `main` já absorveu é fechado com a prova (arquivo a arquivo), pelo autor ou, com aviso, pelo outro agente.
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

### 3.3 Benchmark e produtividade em cada fatia (pedido do proprietário, 27/09/2026)
- **Referências.** Cinco referências do setor por **módulo**, com fonte oficial e data, reaproveitadas pelas fatias do mesmo módulo. Decisão por prática: adotar, adaptar, adiar ou descartar. Estar no mercado não prova que a regra de domínio está correta.
- **Corte de cliques e de digitação:**
  - herdar o contexto (organização, fazenda, safra, talhão, ordem, local, unidade), visível e corrigível;
  - não pedir o mesmo dado duas vezes;
  - nada de tela intermediária sem decisão, campo calculável ou confirmação redundante.
- **Seleção rápida:**
  - lista curta: um toque;
  - catálogo: busca com sugestões;
  - número: teclado numérico com unidade;
  - data: atalhos;
  - código físico: leitura.
- **Último valor:** nunca para lote, dose, quantidade ou autorização.
- **Medição:** cliques e digitação medidos nos testes ponta a ponta do mesmo cenário, antes e depois. Reduzir cliques nunca pode custar legibilidade, segurança, acessibilidade ou rastreabilidade.
- **Detalhe:** `docs/parceria/rodadas/R-004-harness-item-a-e-produtividade.md` §3 e o design system (cap. 74).

### 3.4 Método de trabalho (protocolo v3, pedido do proprietário, 27/09/2026)
- **Acordo curto antes de editar**, no arquivo da rodada ou na tarefa. Só estes campos:
  ```text
  ID / resultado útil / persona:
  Requisitos do PRD e fora do escopo:
  Autor / revisor / integrador:
  Base (commit ou hashes) / arquivos sob responsabilidade:
  Aceite e comando de verificação:
  Estado / impedimento / próximo passo:
  ```
- **Uma solução por problema:** se o outro agente já fez, revisar ou reaproveitar. Quem integra aplica o patch; quem propõe não sobrescreve arquivo ativo do outro. Perfil de navegador, porta de teste e estado de demonstração não se compartilham sem combinar.
- **Revisão por contraexemplo:** o revisor tenta quebrar o resultado como a persona faria. Cada achado é aceito, ajustado ou recusado com fundamento; polimento não reabre entrega aceita.
- **Destravar sem repetir:** travamento não é defeito; retomar do último ponto verificado. Duas falhas pelo mesmo motivo obrigam a mudar a hipótese, reduzir a tarefa ou corrigir a ferramenta antes de tentar de novo.
- **Conferir o resultado real**, não só o código de saída. Corrigido um classificador de testes, reaproveitar os logs válidos em vez de rodar tudo de novo.
- **Corte do supérfluo** em PRD, código, fluxograma, testes e mensagens: cada trecho ajuda a entender, decidir, implementar, verificar ou operar. Regra repetida vira referência à fonte única; IDs e rastreabilidade são preservados.
- **Mensagem enviada não é trabalho integrado.** Pedido entre agentes leva caminho, versão, decisão necessária e impedimento.
- Protocolo completo: [`docs/parceria/protocolo.md`](docs/parceria/protocolo.md).

### 3.5 Protótipo: regime leve (proprietário, 05/10/2026)
O protótipo (`tools/prototipo/`) valida telas e regras; não é produto. O rigor das seções 3.1 e 3.2 vale para o software real.
- **Versionamento:** commit e push na branch única `claude/prototipo-v44`, com um único PR rascunho como janela de revisão. Sem PR por incremento, sem reserva de arquivo em commit, sem pacote de evidências com checksum.
- **Testes por mudança:** unidade das regras que vão para o produto (aprovação, dose, unidade, estoque, carência), geração e varredura das páginas e os testes do módulo mexido. Bateria completa só a cada marco.
- **Revisão:** o Codex revisa pela branch e pelo artefato quando puder, sem bloquear. Achado vira correção na mesma branch.
- **Entrega:** artefato atualizado a cada melhoria, com uma linha do que mudou.
- **Continua valendo:** dados sintéticos e sem segredo (ENG-017), nunca declarar teste não executado, proteção de regressão para defeito corrigido.
- **Branches das frentes** (`claude/v44-*`) também vão ao remoto para revisão dos commits e recuperação do trabalho. O Gitleaks roda antes de cada envio; branch com achado não sobe. Exceção exige escopo explícito, justificativa, autorização pertinente e teste dos limites.

### 3.6 Velocidade com a mesma qualidade (VEL-20261013-01, autorizado pelo proprietário no canal Codex)
- **No máximo três frentes abertas.** Uma nova só começa quando outra entra numa versão publicada. O teto não amplia a fatia funcional ativa nem uma tarefa de autoria por agente; preserve e consolide as frentes já abertas (§3.1).
- Antes da revisão, a frente incorpora a ponta publicada da branch única e verifica o delta da composição.
- **Base verde:** vermelho antigo é corrigido, distinguindo defeito do produto, teste obsoleto e falha da ferramenta. Corrigir não é afrouxar: a contraprova continua reprovando a versão com defeito. Com a base verde, a bateria roda na candidata; não se repete a base sem nova divergência.
- Testes pelo impacto a cada correção; bateria completa uma vez por versão composta. Preserve provas equivalentes e repita o afetado após correções ou mudanças de composição.
- **Montagem compartilhada:** uma por commit de árvore limpa, com as entradas que alteram a saída na chave do cache (dados/configuração, dependências e versão do gerador). Artefato pronto é imutável; cada execução mantém perfil e dados de teste isolados. Não reutilize saída de árvore suja como prova daquele commit.
- Espere a condição observável, preservando os limites contratuais de carregamento e das asserções. DOM quieto é pré-condição, não prova de conclusão do domínio. Espera fixa só quando o tempo real importa (debounce, relógio); falha no limite deve ser explícita.
- Aceite mensurável combinado com o revisor antes do código (§3.4), com unidades, estados e oráculo de cálculo pertinentes.
- Uma revisão adversarial por versão composta, com lentes pelo risco: estoque, demanda, aprovação e dinheiro com lente própria; mudança só visual com conferência proporcional. Não substitui a auditoria integral real de Codex, Claude e Gemini na mesma candidata completa, com dados/perfis isolados, inventário comum e análise dos brutos, após todo o conjunto vigente. A revisão final do PRD só começa após todas as implantações do conjunto vigente, conforme o pedido do proprietário de 09/10/2026; publicação parcial não aciona nenhum desses gatilhos.
- Fonte e brutos no repositório na mesma entrega; mensagens curtas no formato da §3.4.
- Fluxo cujo agente termina com erro sem resultado não pode registrar conclusão. Ausência de ACK não comprova perda ou ociosidade; timeout de envio exige readback antes de reenvio (§3.4). Commit a cada passo verde, preservando rascunhos em falhas.

## 4. Regras de produto que o código não pode quebrar
- **Master-detail** (Menu → Listagem → Detalhe → Sub-detalhe), uma ação primária por tela, estado sempre visível e próximo passo com verbo (PRD 4.2 e 4.3).
- **Design system único** (PRD cap. 74 e [`docs/design-system/`](docs/design-system/), padrões do proprietário de 09/10/2026): botões BOT-01 a BOT-09 (um verde por contexto; lugar, verbo, tamanho e ícone fixos; componente comum), seleção que abre detalhe (SEL-01/02), etapa futura neutra (ETP-01), separador, hover verde, retorno visual e dica (VIS-01 a VIS-04). Vale para toda tela nova e para a correção das existentes, no protótipo e no software real.
- **Toda O.S. agrícola tem aprovação agronômica individual**, inclusive operação mecânica (PRD 41 e 73.9).
  - Exceções expressas: irrigação só com água (DEC-2609-10), manutenção e beneficiamento com responsável próprio.
  - Aprovar não libera; liberar é o CMD-06.
- **O servidor é a autoridade** para saldo, reserva, custódia, aprovação e encerramento (PRD 24).
  - Cada comando carrega a chave de idempotência gerada por quem inicia a ação (ENG-021/022; PRD 73.3).
  - Grava o efeito, o recibo e a outbox na mesma transação.
- **Kanban da O.S. com 5 fases** (A liberar, Liberadas, Em execução, Em conferência, Encerradas). Não criar coluna nova.
- **Fórmula agronômica ou econômica** existe num único serviço de domínio (ENG-011). Unidades explícitas; decimal para dinheiro e quantidade (ENG-013).
- **Trava só onde protege algo concreto:** resultado técnico da lavoura (receita, produto, dose, versão), dinheiro e estoque, lei (receituário, carência, reentrada, registro e bula), segurança da informação, integridade do fato registrado ou decisão explícita do proprietário. O secundário vira aviso, alerta ou registro, só onde agregar valor (proprietário, 29/09/2026). Ao escrever regra, aceite ou tela, nomeie o dano que a trava evita.

## 5. Código
- **Stack do PRD** (23.1): TypeScript estrito, Next.js/React, Node LTS, PostgreSQL/PostGIS, Prisma, PWA com Dexie/Workbox, workers, pnpm workspace, Vitest/Playwright/Testcontainers/fast-check, Docker e GitHub Actions. Na fundação, o acesso a dados usa SQL explícito com `pg`, sem Prisma (ADR 0003).
  - Versões fixadas em [`docs/architecture/versions.md`](docs/architecture/versions.md) no primeiro commit executável.
- **Estrutura** (23.3): `apps/web`, `apps/worker`, `packages/domain`, `packages/application`, `packages/db`, `packages/contracts`, `packages/ui`, `packages/integrations`, `packages/observability`, `tests`, `infra/terraform` e `docs`. Crie um pacote só quando ele tiver responsabilidade real.
- **Comandos contratados** (23.4): `pnpm setup | dev | check | test:integration | test:e2e | test:load | demo:reset | doctor`. Existem hoje, com `pnpm run`: `check`, `test:integration`, `test:e2e`, `demo:reset` e `doctor`. **Ainda não existem** `setup`, `dev` na raiz e `test:load`: não diga que existem até o PR que os cria passar na CI.
- **Checks que existem hoje:** os 10 jobs da CI (documentação, segredos, vulnerabilidades, código, navegador, imagens, Semgrep, travas do Cloud SQL e Terraform dos dois módulos), os mesmos nomes de `tools/github/protecao-main.json`. Os comandos locais equivalentes estão no `README.md`.

## 6. Ao terminar cada incremento
Atualize `docs/STATUS.md` e explique ao proprietário, em português simples:
- o que já pode usar;
- como conferir por uma tarefa real;
- o que falta;
- quais testes passaram, com o comando e o resultado;
- se há custo ou ação externa a autorizar.
