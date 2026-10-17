# Composição com os PRs #100 e #103 (executado em 17/10/2026)

- **Base:** composição remota 595f14e (#98 e #102 integrados pelo Codex).
- **Integrados pelo Claude, revisor:**
  - PR #100 do Codex (PAINEL-FIXO-1, HEAD d5342d4) em bec5c7c/7d65025;
  - PR #103 do Codex (CALDA-QTD, HEAD a6dedd7) em 3c67916.
- **Delta da composição sobre os arquivos do #103:** nenhum. `cenario.js` e `quantidade_test.py` são iguais em 24a632a, a base do PR, e em 7d65025.

| Prova | Resultado | Bruto |
|---|---|---|
| Sonda do #100 (CA-01det → `OS-0421:ajustar` só em A liberar; prévia nos demais) | 6/6 | `pfx_sonda.log` |
| Painéis estáticos (menu) | 11 | `paineis_estaticos.out` |
| `painel_fixo_saldo_test` | ok | `painel_fixo_saldo_test.log` |
| `agro01_previa_test` | PASS | `agro01_previa_test.log` |
| `seta_padrao_test` (1440 e 390) | 14 ok · 0 falhas | `seta_padrao_test.log` |
| `paginas_scan_test` | 5 ok · 0 falhas (148 páginas) | `resumo_nav.txt` |
| `quantidade_test` com o #103 | 16/16 | `quantidade_test_103.log` |
| `os_cenario_test` com o #103 | 22/22 | `os_cenario_test_103.log` |

Revisão do #103 na base do PR: candidata 16/16; contraprova da base 14/16.
