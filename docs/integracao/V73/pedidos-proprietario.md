# Pedidos do proprietário desde 16/10/2026, 12h: situação conferida em 18/10, 15h UTC

**Fonte dos pedidos:** a transcrição da sessão do Claude.
**Fonte da situação:** a composição `claude/v44-v69-mapa` e o artefato publicado, com estado completo na v132 (versão 138, `1792329558-1f0c`).

**Conferência do artefato (executada):**
- v132: 59 páginas que mudaram enviadas em 2 lotes (versões 137 e 138); as outras 89 e os arquivos de apoio são iguais aos da v131;
- 4 páginas lidas de volta e conferidas por sha256 (`artefato-v132/LEIAME.md`);
- origem: `f6a9374a` (v131 + Q5-AMB).

| Quando | Pedido | Situação | Onde conferir no artefato |
|---|---|---|---|
| 16/10 12:01 | Barra de ícones do mapa longe da barra lateral dos módulos | **Publicado** (v98/v99): barra horizontal no alto do mapa | Mapa |
| 16/10 14:06 | Planejar safra no mapa, clicando nos talhões, com aplicar a todos | **Não implantado** (SAF-MAPA só especificado) | — |
| 16/10 14:27 | Planos agronômicos por operação, uma coisa bem feita por vez | **Não implantado** (PA-OPER: especificação R3 com parecer favorável do Codex) | — |
| 16/10 16:18 | Correlação de variáveis no mapa: causa, efeito e alavancas da produtividade | **Não implantado** (MAPA-MIP-PROD só especificado) | — |
| 16/10 17:17 e 23:35 | Raio-X do alvo e pragas no tempo | **Não implantado** (RAIOX-ALVO: contrato RX-0 em discussão) | — |
| 16/10 19:34 e 19:36 | Máquinas em execução andando no mapa, com 1 clique e ícones; telemetria na mesma filosofia | **Não implantado** (MAPA-FROTA: especificação integrada, F1 não começou) | — |
| 16/10 21:29 | Seta do drill down mais amigável, como padrão em tudo | **Publicado** (v116, TAB-11) | Qualquer tabela: a seta fica à esquerda |
| 16/10 21:42 | Editar todos os talhões de uma fazenda numa tela só; entradas mais rápidas | **Publicado** (v116, SAF-LOTE/INP) | Planejar safra › Talhões e cultivos › "Editar talhões…" |
| 16/10 22:52 | Manutenção: vincular ativos a planos, de forma intuitiva | **Publicado** (v117; PR #101 integrado pelo Codex em acf65e1) | Manutenção › Planos: "4 ativos sem plano · Criar plano" e "Vincular a plano" |
| 16/10 23:38 | Mapa com UX/UI de excelência (hover, clique, detalhe) | **Publicado na v129** (MUX-F0/F1/F2: hover, clique e painel; mapa_mux 17/48/29 sem falha) | Mapa |
| 16/10 23:40 | Resolver em 1 clique | **Não implantado** (só a crítica do Claude) | — |
| 17/10 00:03 | Excelência EX-01..48, entrada e ações (varredura e robô) | **Em parte:** os achados de entrada e ações viraram PRs do Codex, já publicados na v113 a v116; o restante está validado, mas não implantado | O.S., CA-01det, Kanban |
| 17/10 08:40 | Agrupar por fazenda também com uma só | **Publicado na v129** (artefato versão 133): o Planejar safra agrupa por fazenda mesmo com uma só, recolhida ao abrir | Planejar safra › Talhões e cultivos |
| 17/10 (manhã) | Cartões e tabelas com drill down recolhido por padrão | **Publicado na v129**: tabelas e cartões abrem recolhidos; busca e endereço de um registro abrem só o caminho dele; Expandir/Recolher tudo | Qualquer tabela com seta (O.S., Estoque, Produção, Qualidade) |
| 17/10 09:00 | Design system do Agrícola nos demais módulos; "⋯" no topo das telas | **Publicado na v128** (artefato versão 130): desvios do padrão 175 → 13 nas 148 telas; no topo, só a ação principal e o ⋯; as ações da linha no ⋯; telas fora do menu com "‹ Módulo" e Fazenda/Safra na faixa "Trabalhando em"; sem cartões de resumo soltos sobre as listas. Os 13 que restam estão em telas da frente aberta do Codex (CA-02, GE-*) ou na ficha impressa | Qualquer módulo: Compras, Estoque, Manutenção, Comercial |
| 17/10 (noite) | Manutenção ainda fora do padrão do Agrícola | **Publicado na v131** (versão 136): título da visão, abas com número só do que pede ação, lista num bloco com título, linhas de até 2 linhas e entrada em blocos Cadastro, Execução e Resultados, como o Agrícola; mantida a linha "N ativos sem plano · Vincular ›" (um toque). Medida automática `ds_man_test` 99/0 (na v129 eram 56 falhas) | Manutenção |
| 17/10 09:18 | Hover e UX dentro do mapa | **Publicado na v129** (MAPA-UX F1): realce e dica no hover do talhão, clique abre o painel do talhão | Mapa |
| 17/10 09:40 | Cartões da O.S. fora do padrão | **Publicado na v128**: cartões compactos em grade (4 por fileira a 1440), selo da fase no título, até 4 campos; também no Agrupar por e a 390 px | Ordens de serviço › Cartões |
| 17/10 09:42 | Seta de drill down só onde há detalhamento | **Publicado na v129**: a seta só aparece em linha com filhos | Qualquer tabela |
| 17/10 09:55 | Agrupar O.S. de vários talhões com a mesma calda ou entrada, para aprovar uma a uma, liberar as aprovadas, separar os insumos de uma vez e seguir uma sequência contínua; modal fora do design system | **Publicado e integrado** (v121; PR #105 em 461e296): grupo proposto por calda, aprovação uma a uma, liberar as aprovadas, separação e sequência | O.S. › "Agrupar operações compatíveis" › Sulfato de magnésio 2 kg/ha |
| 17/10 10:35 | Agrupar O.S.: mostrar insumos e datas de cada O.S./talhão logo ao abrir, para conferir e agrupar | **Publicado e integrado** (v121): insumos e datas visíveis ao abrir | O.S. › "Agrupar operações compatíveis" |
| 17/10 10:40 | EX-49: padrão único para listas, cartões, pai e filho, botões e ⋯ com ícone | **Combinado com o Codex:** Claude implanta no motor logo depois do DRILL; medida pelo robô v4 antes e depois | — |
| 17/10 10:40 | EX-50: telas ocultas, levar o que tem valor e excluir o resto | **Decisões tomadas** (exclusão aceita; financeiro no ERP; portal mínimo; implantação assistida). Classificação dos 123 IDs versionada (`ex50-classificacao-codex.md`). **SU-01 publicado na v122** (PR #106 do Codex em `2249b84`): a falta da OM-0234 vem da manutenção viva e o rolamento e a COT-113 fictícios saíram. **SU-02 publicado na v123** (PR #107 em `c31d9c4`): propor, aprovar e publicar política com recibo, sem tocar na vigente até publicar; selo do cabeçalho pelo estado. **SU-08 publicado na v125** (PR #108 em `df887d9`): perda vira ajuste pendente e só baixa o saldo na aprovação AL-09; transferência e estorno genérico só em prévia, sem efeito fictício. **CA-02 publicado na v126** (PR #109 em `7c5723a`): a fila vem dos apontamentos reais, conferir e divergência usam a conferência diária oficial (AL-12) sem mexer em área, horas ou consumo, e o botão principal abre o próximo a revisar. **LO-02det publicado na v127** (PR #110 em `687d5a7`): a conferência lê a carga programada oficial (RM), a pesagem confirma a saída com baixa única do estoque (só Ana ou Rui), e saem as etapas, a viagem e o frete fictícios do T2. Telas com contrato de Suprimentos e Logística concluídas. Próximo: levar Aprovações e Meu dia para o Mapa, depois das frentes de design e do Mapa; exclusão só depois de migrar as funções e os links | Logística › Expedição: programe a carga do PV-030 e abra Conferir carga |
| 17/10 17:58 | EX-51 fluxo conectado: unir Claude e Codex e implantar da melhor forma | **N-1/B-3 publicado na v130** (versão 134): a decisão do AG-01 emite o receituário com autor, chave e versão; O.S. com receituário divergente mostra o selo e não aprova nem libera até reemitir; a coleta do MB-06 grava. **C-3/C-4 publicado na v131** (versão 136): a compra aprovada vira pedido por linha no Estoque, o recebimento parcial baixa a linha certa e a Compra mostra Recebido, Em quarentena e A entregar por linha. O teste de navegador achou 3 S2, corrigidos: NF com vários itens, Planejar safra sem ver os pedidos emitidos (risco de reduzir insumo já comprado) e nota antiga sem unidade contando em dobro. **v132** (versão 138): o Codex achou um S2 na última correção (nota antiga baixava duas linhas do mesmo item); agora só baixa a linha única em que cabe e, na dúvida, a previsão sai do suprimento com aviso. F1 a F5 seguem depois | Pragas e doenças › decisão; Ordens de serviço (selo "Receituário divergente") |

## Por que quase nada da noite chegou ao artefato

Os pedidos grandes da noite seguiram o rito de avaliar, confrontar Claude × Codex, consultar o Gemini, registrar e só então implantar. A noite foi gasta em especificação e confronto, e quase nada virou tela.

A partir de 17/10, a regra muda. No protótipo, a implantação começa logo, com testes, e a revisão do Codex vem depois, sem bloquear (AGENTS §3.5). A especificação só é escrita quando a decisão é material.

## Ordem de implantação a partir de agora

- **Claude:** N-1/B-3 (v130), C-3/C-4 e DS-MAN (v131) publicados → base verde 2 (vermelhos antigos de Estoque, demanda e Crédito) → EX-51 F1 → MAPA-FROTA F1 (máquinas no mapa) → SAF-MAPA (planejar safra no mapa) → MAPA-MIP-PROD (correlação) → PA-OPER F1.
- **Proposto ao Codex:** RESOLVE-1-CLIQUE e RAIOX-ALVO RX-0.

O artefato é republicado a cada frente integrada. Esta tabela é atualizada na mesma entrega.
