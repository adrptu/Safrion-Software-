# MA-VINCULO recomposto sobre a composição 595f14e (executado em 17/10/2026)

- **Candidata:** 04c88a7, o merge de 595f14e (PRs #98 e #102) sobre 96b3d60.
- **Os dois trechos em conflito foram resolvidos preservando as duas intenções:**
  - `maquinas.py`: `.pm-sv-linha` com `max(30px,var(--g2seta-alvo))`, mantendo as regras `.vl-*`;
  - `ma_rastreio_test.py`: F17/F21 do #101 e F18 do #102.

| Teste | Resultado |
|---|---|
| `ma_vinculo_test` U A B | 101/101 |
| `ma_rastreio_test` | 58/58 |
| `ma_regras_test` | 150/150 |
| `ma_correcoes_pm_test` | 12/12 |
| `ma_unica_test` | 23/23 |
| `ma_revisao_test` | 18/18 |
| `seta_padrao_test` | 14 ok · 0 falhas |
| `cartoes_test` | 70/70 |

**Nota sobre a execução:**
- A primeira bateria esperou o navegador livre e passou do tempo-limite da tarefa. A fila foi ajustada e os testes rodaram de novo.
- O `cartoes_test` rodou à parte, depois que a bateria parou no limite de tempo.

Os brutos estão nesta pasta.
