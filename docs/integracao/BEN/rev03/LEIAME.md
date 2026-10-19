# BEN-REV-20261009-03 · complemento de caixas entre lotes (S2)

Saídas brutas da correção BEN-D31 (commit 1440889), dados sintéticos. "Antes" = código do HEAD 4373592 com os testes novos; "depois" = 1440889.

| Prova | Comando (raiz do repositório, `SAFRION_DADOS=sintetico`) | Antes | Depois |
|---|---|---|---|
| Harness do Codex | `python3 docs/integracao/BEN/rev03/run_harness.py` | `harness_antes_4373592.json`: CX26-01 0, QA-CX-02 1.540 (reserva 100), estorno no QA-CX-02 | `harness_depois_1440889.json`: CX26-01 540, QA-CX-02 1.000 (reserva 100), estorno no CX26-01; 4/4 |
| Unidade | `cd tools/prototipo/v37/gen37 && python3 ben_unit_test.py` | FALHOU 153/163 (U41e, U41g, U45a-h) | OK 163/163 |
| Mutantes | `python3 ben_mutantes.py` | — | OK 72/72 |
| Tela (1440) | `python3 ben_fluxo_test.py lotes` (Chrome headless) | FALHOU no L1 (o item da REQ-041 passava ao QA-CX-02, sem REQ-042) | OK 7/7 |
| Bateria | `bateria/resumo.txt` (um teste de navegador por vez) | — | todos rc=0 |

**Envelopes (BEN-REV-20261009-04, 6091321884).** `harness_codex.js` e os dois JSON brutos ficam sem mudança. Dentro deles, `candidate` (bbe8417) e `executor` ("solicitado pelo Gemini real") são literais do harness do Codex e não descrevem estas execuções. A versão executada, quem pediu, quem executou e a hora estão em `harness_antes_4373592.envelope.json` e `harness_depois_1440889.envelope.json`, com o SHA256 de cada bruto: execução do autor (Claude, Node local), sem o Gemini.
