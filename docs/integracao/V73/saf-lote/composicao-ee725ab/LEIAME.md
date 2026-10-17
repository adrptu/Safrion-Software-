# SAF-LOTE na composição `ee725ab` (PRs #94, #93 e #99)

- **Árvore testada:** `71ecc5e`, o merge da composição `ee725ab` no SAF-LOTE.
- **Conflito resolvido:** um só, no fim do `g2lib.js`. O SAF-LOTE acrescentou o bloco `g2inp` (INP-04/07) e o #93 uma linha em branco; ficaram os dois. Depois do merge, o `g2lib.js` difere da composição só pelas 17 linhas do `g2inp`.
- **Testes pelo impacto:** g2lib com o `g2inp` sobre o rmenu do #93, `safra.js` e `processo_safra.py`. Dados sintéticos, navegador com no máximo 1 Chrome. Os brutos estão nesta pasta.

| Teste | Resultado |
|---|---|
| saf_lote_unit_test | 54/54 |
| rmenu_unit (#93) | OK |
| rmenu_generator_test (#93) | OK |
| rmenu_alignment_test (#93; base do g2lib em 6631d58) | 561 OK, 0 falhas |
| saf_lote_test | 45/45 |
| tabelas_saf_test | 24/24 |
| saf_tab_test | 14/14 |
| saf_c01_test | 68 ok, 0 falhas |

A bateria anterior, de 9 testes, rodou em `4151aec` (composição `adca8ba`): ver `composicao-4151aec/`.
