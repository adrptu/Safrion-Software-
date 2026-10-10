# Integração BEN, rodada 2 · a falta de caixas não tira as caixas de outra ordem (BEN-D32)

S2 da reverificação BEN-c1-B (sonda `p10_cadeia.py`): a recuperação da falta de caixas apontava a custódia de qualquer outra ordem como "sobra". Correção no commit `f048862` (código, testes e BEN-D32 em `docs/beneficiamento/DECISOES.md`). Dados sintéticos. "Antes" = `ben.js` do HEAD `58fb55b` com os testes novos; "depois" = `f048862`.

| Prova | Comando (em `tools/prototipo/v37/gen37`, `SAFRION_DADOS=sintetico`) | Antes (58fb55b) | Depois (f048862) |
|---|---|---|---|
| Unidade | `python3 ben_unit_test.py` | `ben_unit_test_antes_58fb55b.log`: FALHOU 163/168 (U46a-e) | `bateria/ben_unit_test.py.log`: OK 168/168 |
| Mutantes | `python3 ben_mutantes.py` | — | OK 76/76 (M73-M76 novos) |
| Tela, a cadeia da reverificação | `python3 ben_fluxo_test.py cadeia` (1440, clique real) e `cadeia390` (390, toque real) | `ben_fluxo_test_cadeia_antes_58fb55b.log`: FALHOU 4/8 (K1-K4) | OK 16/16 |
| Sondas da lente B | `GEN=<gen37> python3 p10_cadeia.py 1440` e `p9_sobra.py 1440` | o atalho "Receber a devolução da OB-0113" existia | param no passo 2: "NÃO ACHEI: Receber a devolução da OB-0113" (`sonda_*_depois.log`) |
| Harness do Codex (BEN-REV-20261009-03) | `python3 docs/integracao/BEN/rev03/run_harness.py` (na raiz) | — | OK 4/4 |
| Bateria do BEN | `bateria/resumo.txt` (um teste de navegador por vez, lock I) | — | todos rc=0 |

Navegador: `env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpI.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 <teste>`. O modo `fluxo erros celular revisao` rodou antes do commit, sobre o mesmo `ben.js` e o mesmo teste (`bateria/ben_fluxo_test.py_fluxo_erros_celular_revisao.log`, OK 64/64).
