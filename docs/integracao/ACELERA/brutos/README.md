# Brutos da ACELERA (13/10/2026)

Executado na worktree `claude/v44-acelera` (base `302b26f`), trava `cdpA`, `CDP_GL=1`, `SAFRION_DADOS=sintetico`. Resumo e
conclusões: [`tools/prototipo/v37/ferramentas/ACELERA.md`](../../../../tools/prototipo/v37/ferramentas/ACELERA.md).

| Pasta | O que é |
|---|---|
| `bateria/` | bateria completa da V56 com as esperas finais (`8bdf790`): `nav/` (54 de navegador), `unit/` (17 + `cdp_unit_test`), listas e `_compara.txt` (71/71 iguais aos brutos da `1f83eee`) |
| `defeito/` | a versão com defeito (`2e466eb`) com as esperas finais: 5/5 iguais à cand-2e466eb (`_compara.txt`) |
| `divergencia/` | a divergência achada na primeira versão das esperas (`2f63028`): `solo_os_test` 17/18 na bateria, a repetição isolada (condição 15/16 × fixa 16/16 no modo desktop) e o diagnóstico dos timers pendentes |
| `espera/` | `cdp_espera_test` na versão final (6/6) e as contraprovas: sem crédito (`stub_head`, falha E1) e crédito sem a data do timer (`stub_semcs`, falha E2); `cdp_unit_test` na versão `2f63028` (falha o item do fio); `solo_os_test` 18/18 duas vezes |
| `afetados/` | `testes_afetados.py` nos vermelhos reais da V56 e da CTL-4 (`_resumo.txt`, `valida.sh`) |
| `medida/` | os 15 testes antes × depois: `par_alternado/` (medida principal), `antes_extra/` (outras amostras do código antigo), `tabela.md` e `medida.json` |
| `scripts/` | os scripts que rodaram tudo acima (`roda.sh` mede o tempo dentro da trava; `compara2.py` compara código de saída, resumo e rótulos das asserções que falham) |

Os `stub_*.txt` são as linhas acrescentadas às cópias antigas do `cdp.py` só para o teste poder zerar o crédito; não mudam a
espera de cada versão.
