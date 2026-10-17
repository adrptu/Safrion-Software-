# Recibo da publicação do artefato v129 (17/10/2026): drill recolhido, Planejar safra agrupado por fazenda e Mapa (UX e hover)

- **Artefato:** https://claude.ai/artifact/HqspGRcrX1wcayCVMe9emm. As 148 páginas foram em 3 envios: versões 131 (`1792275487-86f6`), 132 (`1792275521-b03e`) e 133 (`1792275554-f410`). O estado completo é a versão 133.
- **Antes de enviar:** o espelho era o estado da v128 (versão 130). As 148 páginas mudaram; os 35 arquivos de apoio (JSON do Agrofit, imagens, `support.js`, `index.html`) são iguais byte a byte e não foram reenviados.
- **Leitura de volta, sha256 igual ao espelho:**

  | Página | sha256 |
  |---|---|
  | `IN-04.dc.html` | `9a23c4e2…` |
  | `SAF.dc.html` | `ff6a5860…` |
  | `OS.dc.html` | `b9de1f83…` |
  | `MB-06.dc.html` | `9e89ab70…` |

- **Origem:** `ac10d029` (worktree `intdrill`), sobre a composição `0ec3a342`:
  - DRILL-RECOLHIDO + SAF-GRUPO e MAPA-UX F1;
  - oráculos adaptados ao TAB-12 (`comp-drill-mapa/oraculos-tab12.md`);
  - correção do "Corrigir cultivos" (acao_unica 7: o foco ficava no título).
- **Montagem:** o `_render` (21:26 UTC) é anterior ao commit (21:49), mas nenhum arquivo-fonte do `gen37` é mais novo que ele, e a árvore está limpa: corresponde a `ac10d029`.
- **Provas:** `comp-drill-mapa/`. Bateria pelo impacto e reexecuções finais no mesmo render:

  | Teste | Resultado |
  |---|---|
  | drill_recolhido (reexecução, limite 2700 s) | 66/0 |
  | saf_fazenda_recolhida | 18/18 |
  | saf_lote | 47/47 |
  | acao_unica | 10/0 |
  | paginas_scan | 5/5 (148 páginas) |
  | links_ocultos | 16/16 |
  | ds_test | 72/72 |
  | ds_1610 | 16/0 |
  | mapa_mux F0 / F1 / F2 | 17 / 48 / 29, sem falha |
  | mapa_mux_unit | 28/0 |
  | carencia | 90/90 |
  | tabelas_cad | 206/206 |
  | cartoes, tabelas_os, os_lote, ma_* | verdes (`resumo_bateria.txt`) |

  - **drill_recolhido:** a 1ª execução depois da correção estourou o limite de 900 s com 44 OK e nenhuma falha; a reexecução sozinha deu 66/0.
  - **textos_soltos:** 266/267; a falha `D CA-01det` já existe na base.
  - **mip_correcoes:** 12/14 na base (`mip_correcoes_test_base.log`). As verificações 2 e 5 procuram "Programar vistoria" e "Seguir monitorando" soltos na linha do AG-01; desde a DS-MODULOS-2 essas ações ficam no menu ⋯ da linha. É oráculo obsoleto, não regressão desta versão. A adaptação entra com a próxima composição.
