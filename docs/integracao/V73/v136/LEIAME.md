# v136 · testes da composição (18/10/2026)

Fonte: `claude/v44-v135-osagrupa` @ `61cd6e4c`, com os dados sintéticos.

**O que entrou desde a v135 (`b6a7bcf4`):**
- EX-32 v2 (`e98396cc`): aprovação em lote no diálogo do grupo, com um CMD-42 por O.S. e sem liberar;
- EX-55 D2 do Codex (`64dfa20e`): a classificação do Mapa extraída para `mapa_camadas.js`, com a revisão em `docs/mapa/EX-55-D2/`;
- EX-54 agenda do Codex (PR #119, `bba3d7b1` e `61cd6e4c`): núcleo `frentes_agenda.js`. **Ainda não está em tela;** o motivo está abaixo.

## Testes executados (brutos em `logs/`)

| Grupo | Teste | Resultado |
|---|---|---|
| Unidade | `os_lote_unit` | 109/109 (L1–L5 do EX-32 v2) |
| Unidade | `os_frentes_unit` | 17/17 |
| Unidade | `visoes2_ag_unit` | 9/9 |
| Unidade | `mapa_camadas_unit` | 1251 pass |
| Unidade | `frentes_agenda_unit` | 13/13; os mutantes estão em `logs/pr119/mutantes.txt` (8/8 detectados com o teste da janela de duração zero) |
| EX-32 v2, navegador | `os_lote_test` | 44/44, nas 2 larguras |
| EX-32 v2, impacto | `os_aprov_lib` 51/51 · `aprova_quem_decide` 103/103 · `map_aprov` 5/5 · `kanban_raias` 9/9 · `os_frentes` 18/18 · `visoes2_agrupar` 3/3 · `tabelas_os` 40/40 | verdes |
| Mapa, composição | `mapa9` 13/13 · `mapa_filtros` 7/7 · `mapa_mux_f1` 43/43 · `os_frentes` 18/18 | verdes |
| Varredura | `paginas_scan` | 5 ok, 0 falhas, 146 páginas |

O render do commit limpo `61cd6e4c` é **idêntico** ao que os testes usaram: 180 arquivos por sha256, 0 diferenças.

## Fora desta versão, com o motivo

- **Agenda das Frentes na tela.** O núcleo supõe operação contínua sem limite de jornada. Com a janela da O.S. por dia, isso equivale a trabalho 24 h e diz "cabe" quando não cabe. Pedida ao Codex a versão com turnos (PR #47, 6254918538). A ligação vem depois disso.
- **PR #117 (base verde 3).** O `tabelas_irr` passou, com 106/106 no HEAD `f1ed489e`. O `filtros_cultura` F2 a 390 px ainda procura `[data-g2cd="g_tal"]`, que não existe no DOM em execução: a lista é `.pr-cards [role=listitem]`. Sondas e capturas estão em `logs/pr117/`, e a correção proposta está em 6254915626.
- **PR #118** (texto do EX-32 no AGENTS/DECISIONS): devolvido para limitar ao lote a substituição da DEC-0910-15 (6254851080).
