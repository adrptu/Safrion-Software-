# SAF-LOTE na composição `adca8ba` (recibo da bateria)

- **Árvore testada:** `4151aec` = SAF-LOTE `d0b6279` (com a correção do slPlano `abea501`, aceita pelo Codex em 6229456485) + merge da composição `adca8ba` (PR #89 e PR #95).
- **Bateria:** dados sintéticos, navegador com no máximo 1 Chrome. Os brutos estão nesta pasta e o resumo em `resumo.txt`.

| Teste | Resultado |
|---|---|
| saf_lote_unit_test | 54/54 |
| kanban_raias_test | 9/9 |
| saf_lote_test | 45/45 |
| saf_c01_test | 68 ok · 0 falhas |
| tabelas_saf_test | 24/24 |
| cartoes_test | 70/70 |
| ds_1510_test | 17 ok · 0 falhas |
| solo_ag02_test | 32/32 |
| paginas_scan_test | 5 ok · 0 falhas (148 páginas) |

**Próximo passo:** incorporar a composição seguinte (PRs #94, #93 e #99) e repetir os testes pelo impacto (ver `composicao-<sha>/`).
