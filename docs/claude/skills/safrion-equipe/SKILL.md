---
name: safrion-equipe
description: Coordene entregas do Safrion (Do Talhão à O.S.) entre Codex e Claude Code, desde feedback do agricultor até revisão, testes e homologação. Use ao dividir trabalho, retomar pendências ou avaliar se uma fatia está pronta neste projeto. Não se aplica a projetos sem essa parceria.
metadata:
  version: "1.0.0"
---

# Equipe Safrion (Do Talhão à O.S.)

Use os skills existentes para executar a tarefa; este skill organiza a passagem entre os dois agentes. Não muda permissões nem substitui o PRD.

## Começar pelo estado real

Localize a raiz do projeto pelo contexto e leia apenas o necessário: `AGENTS.md`, `docs/STATUS.md`, requisitos citados de `docs/PRD.md` e a rodada atual em `docs/parceria/rodadas/`. `CLAUDE.md` pode apontar para `AGENTS.md`; mantenha uma fonte de regras. Se o repositório não estiver identificado, confirme-o antes de editar; não crie outro.

Identifique a fatia ativa, base (commit ou hashes), mudanças em curso e responsável pelos arquivos. Reaproveite a solução existente. Não implemente nos mesmos arquivos do outro agente sem combinar a integração.

## Carregar somente o que a tarefa exige

Leia os skills abaixo pelo catálogo do ambiente. No uso local, confira os diretórios de skills do Codex ou do Claude; não pressuponha que a instalação local está disponível em sessões na nuvem. Se faltar uma dependência necessária, declare a ausência e preserve o trabalho possível.

| Trabalho da fatia | Skills pertinentes |
|---|---|
| Construir ou evoluir produto | `dev-ciclo-completo`; `agro-gestao-conhecimento` para regras agro |
| Definir módulo ou comparar práticas | `benchmark-top5`; reutilizar pesquisa atual pertinente |
| Criar ou revisar interface | `ux-essencial`, `master-detail-ux`, `minimalismo-essencial`; `tabelas-interativas` quando houver tabela |
| Implementar interface ou app | `dev-frontend-mobile` |
| API, dados ou integrações | `dev-backend` |
| Testar ou revisar código | `dev-testes`, `dev-revisao` |
| Ambientes, entrega ou incidentes | `dev-infra` |
| Indicadores de satélite ou drone | `indicadores-satelite` |

Não carregue todos por rotina nem instale dependências ou ferramentas só porque aparecem como exemplos. Decisões, contratos e regras de negócio ficam nos documentos do projeto, não neste skill.

## Entregar e revisar sem retrabalho

Registre na rodada existente, de forma curta: **resultado/persona e IDs do PRD; autor/revisor/integrador; base/arquivos; aceite/teste; estado/próximo passo**. Uma fatia útil por vez. Paralelismo só quando necessário e autorizado, com arquivos e saídas delimitados.

- O autor faz a menor mudança coerente, verifica o comportamento e entrega caminho/diff, versão, comandos, resultados e limites.
- O outro agente procura contraexemplos na versão entregue. Distingue defeito demonstrado, risco a investigar e preferência; cada achado tem cenário, impacto e aceite observável.
- O integrador confere a base antes de aplicar. Depois da integração, execute a regressão afetada; não repita toda a bateria sem uma mudança ou dúvida que justifique.
- Revisão do Claude significa revisão pelo Claude real, e vice-versa. Confirme envio e retorno por evidência. Sem acesso, deixe pedido preparado e revisão pendente; não simule concordância.
- Encerre quando o aceite do escopo e a revisão estiverem resolvidos. Melhorias opcionais vão para a fila, sem abrir ciclos infinitos de polimento.

## Verificação que não produz aprovação falsa

Uma saída zero com ajuda, nenhum teste executado, asserção mascarada ou resumo contraditório não comprova sucesso. Separe falha do produto, teste obsoleto, precondição ausente, artefato antigo, problema da ferramenta e bloqueio externo antes de corrigir.

Em jornadas com estado, registre a ordem e as precondições; ordem alfabética não é uma sequência funcional. Não reutilize perfil de navegador, porta ou dados de teste que outro agente esteja alterando sem coordenação. Preserve evidências válidas ao retomar; dois fracassos pela mesma causa exigem outra hipótese ou uma tarefa menor.

## Feedback e homologação desde cedo

Transforme a explicação do agricultor em tarefa curta: **o que tentou, o que aconteceu, o esperado e a evidência disponível**. Registre o que foi efetivamente visto/ouvido; não invente conteúdo inacessível de áudio ou vídeo. Aproveite o relato original e peça complemento só quando mudar a correção. Preserve o requisito de print e comentário do fluxo de feedback do produto.

Priorize acesso à primeira fatia funcional verificada. Diferencie protótipo, homologação e produção pelo que realmente está disponível. Para teste humano, entregue versão, acesso testado, dados de demonstração e roteiro curto baseado nos aceites; indique limitações materiais. Use os critérios de liberação e o aceite explícito do proprietário definidos no projeto. Não confunda aprovação do plano com aprovação de produção.

## Melhorar com evidência

Corrija o método quando uma falha real revelar lacuna; prefira corrigir a ferramenta ou o teste responsável a acrescentar regras genéricas. Revise alterações deste skill com o outro agente. Meça pelos registros existentes esforço do agricultor, defeitos escapados e retrabalho; número de skills, agentes ou testes não mede sucesso.
