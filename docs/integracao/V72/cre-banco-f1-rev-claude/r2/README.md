# PR #90 · revisão do Claude, rodada 2 (HEAD b35cd0c)

- **Revisado:** `b35cd0c91139e98c665b2fe8086212282adf16e4` (refs/pull/90/head), sobre `7860b81`.
- **Composição:** `claude/v44-v69-mapa` em `c9ffa08`. O delta 5511cf3..c9ffa08 só mexe em `docs/integracao/V71/mapa-frota/`, e `git merge-tree c9ffa08 b35cd0c` não dá conflito.
- **Render:** montado em worktree nova, 156 páginas, dados sintéticos.
- **Data:** 16/10/2026. Tudo aqui foi executado.

## Achados da rodada 1, um por um

| # | Achado | Em b35cd0c | Prova |
|---|---|---|---|
| 1 | rótulo do botão do painel | `EXTRA[i]` com `{{cre_ficha_salvar_rotulo}}` e asserção no `credito_ficha_build.py` | N1 e C1b ok a 1440 e 390 |
| 2 | "Incluir documento" à vista | botão antes do `ilink`; "Bens e avaliações" no ⋯ | R1 ok |
| 3 | links_ocultos L2b | par GE-08→PT-04 retirado, com motivo | 16/16 |
| 4 | estado do CRE-0102 no cabeçalho | `status=` restaurado e asserção no build | R2 ok; ver a captura `ficha-vazia-1440.png` |
| 5 | estado vazio | mensagem própria (com e sem papel); a do motor fica para filtro sem resultado; nada no erro de leitura | F4 ok; 4 testes novos no motor |
| 6 | erro de papel na inclusão | `{[isNovo?'nome':'oper']:…}` | S4 ok (Ana e Rui) |
| 7 | formato ao reabrir | `credFichaDinheiro(...).slice(3)`: "850.000,50" e "12.500.000,00"; valor salvo igual | P7 (oráculo r2: formato canônico), P8, P9 e P10 ok |

**Oráculos:**
- As expectativas do motor que mudaram de "850000,50" para "850.000,50" acompanham o formato novo. O valor continua exato, e o rascunho em erro ou quota mantém o texto digitado.
- Os testes novos do motor reprovam o script de 7860b81: 9/17 em `contraprova-motor-novo-no-7860b81.log`.
- P9 e P10 são novos nesta rodada: reabrir e salvar sem mudar nada não cria versão.

## Testes (executados em b35cd0c)

| Teste | Resultado |
|---|---|
| `credito_ficha_build.py` | ok (asserções novas passam) |
| `node credito_ficha_unit.js` | 18/18 |
| `node credito_ficha_motor_unit.js` (gerado e render) | 17/17 e 17/17 |
| `rev_ficha_nav_r2.py`, 1440 e 390 | 111 ok · 0 falhas |
| `credito_menu_test.py` | 16/16 |
| `cadastros_rev1_test.py` | 19/19 |
| `cad_gravacao_falha_test.py` | 7/7 |
| `cadastros_padrao_test.py` | 44/44 |
| `links_ocultos_test.py` | 16/16 |
| `ds_modulos.py --catraca` | catraca ok |
| `ds_inventario.py --catraca` | catraca ok |
| `paginas_scan_test.py` | 5 ok · 0 falhas (148 páginas) |

Chrome: um por vez. O teste espera até haver no máximo 1 Chrome rodando, contado com `ps -eo args | grep -cE '^/tmp/cloudchrome/chrome .*remote-debugging-port'`. O `pgrep -f` também casa a linha de comando do próprio shell e infla a contagem.

## Pendências S4 (não bloqueiam)

- **Achado 8:** o parágrafo repete o título, e o vocabulário ainda difere da spec ("Completar ficha", "completo/falta", "usado em N dossiês"). Está registrado pelo Codex.
- **Mensagem de vazio:** fica no pé do bloco, longe do cabeçalho da tabela, porque o bloco único estica a grade. Está legível; dá para aproximar depois.
