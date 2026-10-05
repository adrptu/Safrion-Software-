# TABELAS-FOCO 2b · unidade junto do valor (decisão de 05/10/2026) — evidência executada

- Branch `claude/v44-tabelas-03`. A bateria rodou sobre `cd9cdc3` com as alterações locais de `bateria/sujos.txt`, que viraram o commit `e4727eb` sem mudança de código. Dados sintéticos.
- Decisão do proprietário (Adrianus, chat, 05/10/2026): "No caso da unidade pode ficar junto do valor, fica mais intuitivo e filtrar unidade não gera valor."
- `tabelas_saf_test.log`: `python3 tabelas_saf_test.py` → **27/27**. Meta "45 t/ha/ano" e "62,5 sc/ha" (sem arredondar); filtro Meta e Necessidade líquida pelo texto da célula ("62.500 kg"); Tipo = Parcela corta; ordem numérica da necessidade; Preço "R$ x/kg"; nenhuma coluna Unidade.
- `saf_cmp_continuidade_test.log`: 31/31 (cabeçalhos essenciais à vista sem rolar a grade). `partest.log`: 43/44, igual à base (a falha "T1-C copia ajuste do T1-B" é anterior). `saftest.log`.
- `bateria/` + `00-bateria.sh`: bateria completa, 101 passos (retomada uma vez depois do limite de tempo; passos concluídos reaproveitados). O conjunto de logs com saída ≠ 0 é o mesmo da base `v44-tabelas-03/saf246-20261005/bateria`: 13 vermelhos anteriores, nenhuma falha nova.
- `SHA256SUMS`: hash de cada arquivo deste pacote.
