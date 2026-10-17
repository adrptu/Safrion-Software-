# TAB-11 na composição fa4413a

Brutos da junção da TAB-11 (`claude/v44-v73-seta-comp`) com a composição fa4413a = f7b8c8e + PR #96 + PR #97 (já com #93 EX-47a, #94 AGRO-02/06, #99). Tudo **executado**, dados sintéticos, render montado da árvore limpa de cada commit, um Chrome por vez e só com 0 rodando.

## Commits

- `b3f2b2e`: merge da fa4413a.
  - Conflito em `engine.py` `grid()`: ficou o `hsel` da TAB-11 (`SETA_VAZIO`) e o `hdel` do #93 (cabeçalho "Ações" só com `_acoes` quando `menu_linha`; com `dele`, o de sempre).
  - Conflito em `g2lib.js` `g2vals`: ficou o bloco EX47 A1 inteiro (`_acoes`, coluna retirada sem ação, `_ncols`), antes do comentário TAB-09 da TAB-11.
  - Lógica do Codex não reescrita.
- `359a00a`: vermelho novo do merge, no produto. Três `summary` novos com o marcador nativo (o triângulo preto):
  - "Conferir caminho de liberação" no PL-04 e no CA-01 (#97);
  - "Método e limites" no Registrar laudo do AG-02 (#94).
  - Correção: `E.seta()` como 1º filho e o `SETA_CSS` põe todo summary com seta em linha (sem classe nova no markup do Codex).
  - O `agro01_previa_test` ganhou o engine no ambiente da expressão; as asserções não mudaram.
  - O `seta_padrao_test` ganhou os estados `AG-02#registrar` e `CA-01|sel1`.

## Resultados

| Teste | Commit | Resultado |
|---|---|---|
| rmenu_unit.js | b3f2b2e | OK |
| rmenu_generator_test.py | b3f2b2e | OK |
| rmenu_alignment_test.js × base 6631d58 | b3f2b2e | 557 OK, 4 falhas (A6 "caminho antigo idêntico à base") |
| rmenu_alignment_test.js × base 2bbe0d5 (TAB-11 sem o #93) | b3f2b2e | 561 OK, 0 falhas |
| contraprova: 2bbe0d5 × 6631d58 | — | 57 falhas, entre elas as mesmas 4 A6: a diferença do caminho antigo vem da TAB-11 (sai `caretSym`, "Expandir"→"Abrir", `g2csel`), não do merge; a sonda continua vendo a falta do #93 (A1) |
| rev93_reteste_navegador.py | b3f2b2e | 44 OK, 0 falhas |
| seta_padrao_test | b3f2b2e | 12/14 (B no PL-04) |
| contraprova summary (PL-04, AG-02 registrar, CA-01 sel1) | b3f2b2e | reprova B nos três |
| seta_padrao_test | 359a00a | 14/14 (148 telas + 12 estados; 420 controles a 1440; 1.777 setas, 1 desenho) |
| kanban_raias 9/9 · tabelas_saf 24/24 · saf_tab 14/14 · cartoes 70/70 · tabelas_os 40/40 · os_cenario 22/22 · visoes2_formas 23/23 · pa_lista 24/24 · ma_unica 23/23 · ma_rastreio 58/58 · solo_os 18/18 | b3f2b2e | verdes (não tocam os 3 summary) |
| tab_drill_cab 6/6 · ds_1510 17/17 · ds_1610 14/14 · paginas_scan 5/5 | b3f2b2e e 359a00a | verdes |
| solo_ag02 32/32 · mapa9 13/13 · solo_saf 36/36 · solo_rev 22/22 | 359a00a | verdes |
| agro10_estado_test · agro01_previa_test · mip_unit_test 34/34 · quantidade_test 15/15 | b3f2b2e | verdes |
| agro01_previa_test · agro06_analitos_unit · agro02_selecao_unit 7/7 | 359a00a | verdes |

Fotos olhadas (359a00a): `../fotos/pl04_previa_*_depois.jpg` e `../fotos/ag02_registrar_*_depois.jpg`.
