---
name: safrion-equipe
description: Coordene entregas do Safrion (Do Talhão à O.S.) com implementação e revisão cruzada de Codex e Claude e crítica delimitada do Gemini real, desde feedback do agricultor até revisão, testes e homologação. Use ao dividir trabalho, retomar pendências ou avaliar se uma fatia está pronta neste projeto. Não se aplica a projetos sem essa parceria.
metadata:
  version: "2.0.1"
---

# Equipe Safrion (Do Talhão à O.S.)

Codex dirige produto/UX/QA; Codex e Claude implementam partes delimitadas e revisam reciprocamente. O revisor integra o PR do outro; ninguém aprova ou integra o próprio PR. Gemini real participa de decisões, deltas materiais e contraexemplos, inclusive fluxo, acessibilidade e domínio. Não simule modelos. Grok saiu da equipe; preserve seu histórico sem acioná-lo.

## Retomar pelo registro vigente

Leia `AGENTS.md`, [docs/STATUS.md](https://github.com/adrptu/Safrion-Software-/blob/main/docs/STATUS.md), o cabeçalho do checkpoint da [issue #1](https://github.com/adrptu/Safrion-Software-/issues/1) e os deltas dos PRs depois do último recibo de cada IA. Siga o [protocolo canônico](https://github.com/adrptu/Safrion-Software-/blob/main/docs/parceria/protocolo.md) e recupere fontes/diffs/provas pelos commits e recibos indicados nesses registros. Requisitos vêm do PRD e decisões NAV/DS da fonte vigente, sem copiar suas regras aqui.

No executor local do proprietário, `outputs/revisao-f0a.md` e `work/fontes-claude/` são canais adicionais quando existem e estão acessíveis; não fazem parte deste pacote nem são pré-requisitos de uma sessão limpa. Na nuvem ou sem esses diretórios, use os registros versionados, checkpoint e PRs acima. Se a prova necessária existir apenas no Mac, solicite ao autor sua fonte recuperável no canal existente e mantenha o aceite dependente bloqueado; não reconstrua nem presuma a evidência. Preserve o trabalho independente possível.

Priorize risco crítico, correção ou revisão devolvida pronta, dependência imediata e próximo item apto. Confira pedidos enviados, recebidos, em execução e devolvidos: ACK não é entrega, ausência de ACK não prova ociosidade. Só Codex edita o checkpoint; releia antes de editar, preserve histórico e não crie outra fila ou automação.

## Autoria e passagem imediata

Registre na mesma tarefa: IDs, resultado/persona, base/arquivos/trechos, autor, revisor/integrador e aceite. Uma autoria ativa por agente; paralelismo somente com contratos e arquivos/trechos separados. Preserve trabalho e rascunhos da sessão existente do Claude. Enquanto o outro revisa, avance na implementação delimitada já combinada, sem invadir sua autoria.

Passe entrega pronta ao próximo responsável imediatamente durante trabalho ativo. A agenda retoma a sessão; não é intervalo obrigatório entre agentes nem garantia de execução remota. Antes de encerrar por dependência externa, confira correção própria, entrega do outro e implementação apta. Se não houver, deixe pedido concreto de próxima divisão e gatilho exato de retomada. Não invente conclusão nem prazo garantido.

Envio incerto exige readback antes de reenviar. Duas falhas pela mesma causa pedem abordagem diferente ou bloqueio documentado. Respeite interface bloqueada, cotas, permissões e controles; não contorne nem faça consultas pagas repetitivas. Falha de transporte, bloqueio de ferramenta e falta de retorno são estados diferentes.

## Revisar a mesma candidata

Confira base, autor e arquivos; leia fontes recuperáveis/diff e saídas pertinentes; reproduza o comportamento alterado. Hash sem fontes, teste proposto e relato do autor não comprovam execução independente. Use perfis, dados e portas isolados e preserve provas válidas. Consolide um retorno por candidata: cenário, versão, evidência, impacto, severidade S1–S4 conforme PRD 22.1, prioridade separada e aceite observável.

Solicite ao Claude real crítica das entregas substantivas do Codex e revise as do Claude. Gemini real Pro/HIGH usa o adaptador oficial Vertex verificado, com pacote mínimo inspecionado, sem segredos/dados reais; cada consulta resolve decisão ou contraexemplo material. Referências não enviadas permanecem indisponíveis; não consulte por ritual. Divergência se resolve por fonte/reprodução, não votação. Após correção, reteste o afetado; integre o PR do outro quando checks e pareceres pertinentes estiverem resolvidos.

## Produto, publicação e transição

Conclua todo o conjunto vigente do protótipo, usando IDs/estados atuais. Publique incrementos operáveis no protótipo existente após os aceites pertinentes, com versão, URL e mudança concreta. Publicação parcial, ACK, camada sintética e tarefa técnica encerrada não concluem o conjunto nem disparam auditoria integral.

Somente com todas as melhorias concluídas e candidata completa/operável identificada por versão, URL, fontes, diff e provas, realize auditoria integral de Codex, Claude e Gemini reais na mesma candidata, com inventário comum e análise dos brutos. Ferramenta indisponível permanece bloqueada. Corrija divergências reproduzidas e reteste só o afetado.

Depois da conclusão e validação, transfira à aplicação Next existente por fatias tela → domínio → banco, comprovando fidelidade e HML. Registre no mesmo ID: protótipo → implementado no real → testado → HML. Preserve trabalhos reais anteriores; não inicie nova evolução paralela do protótipo. F1 técnico não equivale à Fase 1 comercial; o escopo é o do PRD/registro vigente.

O confronto do PRD após as implantações só começa quando todas as implantações vigentes estiverem concluídas com evidências. Corrija divergências, lacunas, ambiguidades e redundâncias necessárias sem ampliar escopo, perder IDs/histórico/pendências ou legitimar defeito por estar implementado. Referencie o design system. Se não houver mudança, registre conferência e mantenha versão; se houver, combine autoria e solicite revisão real, com integração pelo revisor. Gemini participa quando o domínio/fluxo mudar materialmente.

## Autorizações e fontes

Reutilize autorizações concretas de desenvolvimento/QA/HML, sem pedir novamente. Orçamento/alerta não limita cobrança; produção exige aceite explícito de Adrianus sobre a candidata e pareceres pertinentes. Não altere proteções nem realize efeitos reais de produção sem autorização. Executor local continua local até prova remota; aplicativo/computador indisponível impede retomada.

Marketing/SITE, contas e mídia seguem adiamentos e gatilhos comerciais registrados; preserve rascunhos. Nenhum CI verde libera campanhas. Não copie valores mutáveis de orçamento, IDs de PRs atuais ou estado do backlog para esta skill.

Carregue só skills pertinentes: `dev-ciclo-completo`, `dev-revisao`, `dev-testes`; por camada `dev-frontend-mobile`, `dev-backend`, `dev-infra`; no Safrion `.claude/skills/padrao-safrion/SKILL.md` e o DS vigente antes das referências genéricas; por UX `master-detail-ux`, `ux-essencial`, `minimalismo-essencial`, `tabelas-interativas`; por domínio `agro-gestao-conhecimento`, `indicadores-satelite`; `benchmark-top5` reutiliza pesquisa vigente; negócio/growth somente no escopo autorizado. Instalação local não comprova disponibilidade em sessão na nuvem; confira leitura/recibo, não apenas catálogo.

