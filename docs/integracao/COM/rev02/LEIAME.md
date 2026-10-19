# COM-IDEM-01 · entrega repetida com outra origem da devolução (S3)

Achado do Codex em 6091943041 (COM-REV-20261010-02): `comEntregar` montava a impressão sem o lote de origem da devolução. A mesma chave com outro lote (L10-031 em vez de L39-133) voltava `repetido:true`.

- Candidata: `3fcf47c7fae9fc55c7071c592cc01e39315d2d1d` (branch local `claude/v44-comercial`), filho de `29cdc6e`. Para reproduzir: depois do `com.bundle`, `git am rev02/0001-*.patch` sobre `29cdc6e`, ou `git apply rev02/diff-29cdc6e-3fcf47c.patch`.
- Mudança (2 arquivos, +24 −1):
  - `comercial.js`, `comEntregar`: na repetição com a mesma chave e a mesma impressão, o lote pedido confere com a **origem efetiva gravada** (`de`) da devolução daquele recibo (`rm.devs` com a chave `<chave>-DEV`).
    - Outro lote é conflito.
    - Sem lote (seleção automática) vale a origem gravada, sem conflito falso.
    - Sem a devolução do recibo não há como provar a igualdade, e é conflito.
  - A impressão e os recibos antigos **não mudam de formato**, e a história fica preservada.
  - `comercial_unit.js`: caso RV-IDEM (a–e).
    - (a) A mesma chave e o mesmo conteúdo repetem sem gravar.
    - (b) Outro lote é conflito, sem gravar.
    - (c) Sem lote, vale a origem gravada.
    - (d) No recibo antigo, a origem comprovada repete e outro lote é conflito.
    - (e) Sem a devolução do recibo, pedir o lote é conflito.

| Prova (executada pelo Claude, Node local, dados sintéticos) | Código | Resultado | Bruto |
|---|---|---|---|
| `python3 comercial_unit_test.py` | `29cdc6e` com os casos novos | FALHOU 107/110 (RV-IDEMb, d, e) | `brutos/comercial_unit_antes_29cdc6e.log` |
| `python3 comercial_unit_test.py` | `3fcf47c` | OK 110/110 (com e sem o núcleo da carência) | `brutos/comercial_unit_depois.log` |
| Harness do Codex 6091943041, sem mudança: prefixo `comercial_unit_test.fonte(True).split('const R = [];')[0]` + `harness_codex.js` | `29cdc6e` | 6/7; falha `delivery-different-lot-conflict` | `brutos/harness_codex_antes_29cdc6e.json` |
| o mesmo | `3fcf47c` | 7/7 | `brutos/harness_codex_depois.json` |

O motor, a precisão e as telas não mudaram. A bateria de navegador não foi repetida: só o caminho da repetição mudou, e ele não tem tela própria.
