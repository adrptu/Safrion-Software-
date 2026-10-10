# COM-REV-20261010-03 · ramo restante do COM-IDEM-01

O Codex achou, em 6092005836, o caso que ainda passava. A repetição trazia devolução **sem** lote, e o recibo não tinha a devolução correspondente. O motor devolvia `repetido:true` sem comprovar a origem.

- Candidata: `5efb2c4cfef27a71aeee252318bdc897f00559d8` (`claude/v44-comercial`), filho de `3fcf47c`. Para reproduzir: `git am rev03/0001-*.patch` depois do `rev02`, ou `git apply rev03/diff-3fcf47c-5efb2c4.patch`.
- Mudança (2 arquivos, +11 −3):
  - `comercial.js`, `comEntregar`. Sempre que a repetição traz devolução, exige a devolução do recibo (`<chave>-DEV`) com a origem gravada (`de`). O lote pedido só é comparado quando é informado. A entrega sem devolução continua como estava. Os recibos antigos não mudam de formato.
  - `comercial_unit.js`:
    - RV-IDEMf: sem a devolução do recibo, repetir sem lote é conflito;
    - RV-IDEMg: entrega sem devolução repete com a mesma chave.

| Prova (executada pelo Claude, Node local, dados sintéticos) | `3fcf47c` (com os testes novos) | `5efb2c4` | Brutos |
|---|---|---|---|
| `python3 comercial_unit_test.py` | FALHOU 111/112 (RV-IDEMf) | OK 112/112 | `brutos/comercial_unit_*.log` |
| Harness do Codex 6091943041 com a contraprova de 6092005836, sem mudança nas asserções | 8/9 (`missing-receipt-omitted-lot-conflict`) | 9/9 | `brutos/harness_codex_9_*.json`, `brutos/harness_codex_9.js` |
