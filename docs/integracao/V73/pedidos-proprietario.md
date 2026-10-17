# Pedidos do proprietário desde 16/10/2026, 12h: situação conferida em 17/10, 09h50 UTC

**Fonte dos pedidos:** a transcrição da sessão do Claude.
**Fonte da situação:** a composição `claude/v44-v69-mapa` e o artefato publicado, com estado completo na v116 (`1792228309-802d`).

**Conferência do artefato (executada):**
- 148 de 148 páginas presentes, com o tamanho igual ao do manifesto (`artefato-v115/manifesto.tsv`);
- 4 páginas conferidas por sha256;
- origem: composição `5bb8f5e`.

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
| 16/10 23:38 | Mapa com UX/UI de excelência (hover, clique, detalhe) | **Em implantação** desde 17/10 09:20 (MUX-F0/F1/F2) | — |
| 16/10 23:40 | Resolver em 1 clique | **Não implantado** (só a crítica do Claude) | — |
| 17/10 00:03 | Excelência EX-01..48, entrada e ações (varredura e robô) | **Em parte:** os achados de entrada e ações viraram PRs do Codex, já publicados na v113 a v116; o restante está validado, mas não implantado | O.S., CA-01det, Kanban |
| 17/10 08:40 | Agrupar por fazenda também com uma só | **Em implantação** (frente DRILL) | — |
| 17/10 (manhã) | Cartões e tabelas com drill down recolhido por padrão | **Em implantação** (frente DRILL) | — |
| 17/10 09:00 | Design system do Agrícola nos demais módulos; "⋯" no topo das telas | **Em implantação** (frente DS-MODULOS-2) | — |
| 17/10 09:18 | Hover e UX dentro do mapa | **Em implantação** (MAPA-UX) | — |
| 17/10 09:40 | Cartões da O.S. fora do padrão | **Em implantação** (DS-MODULOS-2) | — |
| 17/10 09:42 | Seta de drill down só onde há detalhamento | **Em implantação** (DRILL) | — |
| 17/10 09:55 | Agrupar O.S. de vários talhões com a mesma calda ou entrada, para aprovar uma a uma, liberar as aprovadas, separar os insumos de uma vez e seguir uma sequência contínua; modal fora do design system | **Publicado e integrado** (v121; PR #105 em 461e296): grupo proposto por calda, aprovação uma a uma, liberar as aprovadas, separação e sequência | O.S. › "Agrupar operações compatíveis" › Sulfato de magnésio 2 kg/ha |
| 17/10 10:35 | Agrupar O.S.: mostrar insumos e datas de cada O.S./talhão logo ao abrir, para conferir e agrupar | **Publicado e integrado** (v121): insumos e datas visíveis ao abrir | O.S. › "Agrupar operações compatíveis" |
| 17/10 10:40 | EX-49: padrão único para listas, cartões, pai e filho, botões e ⋯ com ícone | **Combinado com o Codex:** Claude implanta no motor logo depois do DRILL; medida pelo robô v4 antes e depois | — |
| 17/10 10:40 | EX-50: telas ocultas, levar o que tem valor e excluir o resto | **Decisões tomadas** (exclusão aceita; financeiro no ERP; portal mínimo; implantação assistida). Classificação dos 123 IDs versionada (`ex50-classificacao-codex.md`). **SU-01 publicado na v122** (PR #106 do Codex em `2249b84`): a falta da OM-0234 vem da manutenção viva e o rolamento e a COT-113 fictícios saíram. **SU-02 publicado na v123** (PR #107 em `c31d9c4`): propor, aprovar e publicar política com recibo, sem tocar na vigente até publicar; selo do cabeçalho pelo estado. Próximo: SU-08 (perda pelo ajuste com aprovação AL-09; transferência e estorno genérico só em prévia), depois CA-02 e LO-02det; exclusão só depois de migrar as funções e os links | Suprimentos › Necessidades e cobertura (linhas da OM-0234) |

## Por que quase nada da noite chegou ao artefato

Os pedidos grandes da noite seguiram o rito de avaliar, confrontar Claude × Codex, consultar o Gemini, registrar e só então implantar. A noite foi gasta em especificação e confronto, e quase nada virou tela.

A partir de 17/10, a regra muda. No protótipo, a implantação começa logo, com testes, e a revisão do Codex vem depois, sem bloquear (AGENTS §3.5). A especificação só é escrita quando a decisão é material.

## Ordem de implantação a partir de agora

- **Claude:** MAPA-UX (em curso) → MAPA-FROTA F1 (máquinas no mapa) → SAF-MAPA (planejar safra no mapa) → MAPA-MIP-PROD (correlação) → PA-OPER F1.
- **Proposto ao Codex:** RESOLVE-1-CLIQUE e RAIOX-ALVO RX-0.

O artefato é republicado a cada frente integrada. Esta tabela é atualizada na mesma entrega.
