#!/bin/bash
# roda os testes afetados um por vez, com o lock do navegador, e guarda o log de cada um
cd <sp-saf>/tools/prototipo/v37/gen37
OUT=<scratchpad>/runs
run(){ nome="$1"; shift; echo "### $nome $(date +%H:%M:%S)" >> $OUT/resumo.txt; env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpB.lock env CDP_GL=1 timeout 900 "$@" > "$OUT/$nome.log" 2>&1; echo "exit=$? $(grep -E 'RESULTADO|resultado|falhas|FALHA' "$OUT/$nome.log" | tail -3 | tr '\n' ' ' | cut -c1-400)" >> $OUT/resumo.txt; }
: > $OUT/resumo.txt
run ocupacao_test python3 ocupacao_test.py
run saf_operacoes_test python3 saf_operacoes_test.py
run tabelas_saf_test python3 tabelas_saf_test.py
run rend_fluxo python3 rend_multiconjuntos_test.py fluxo
run rend_telas python3 rend_multiconjuntos_test.py telas
run rend_bordas python3 rend_multiconjuntos_test.py bordas
run rend_bordas2 python3 rend_multiconjuntos_test.py bordas2
run partest python3 partest.py
run saf_cmp_continuidade python3 saf_cmp_continuidade_test.py
run acao_unica_saf python3 acao_unica_test.py saf
run acao_unica_v3 python3 acao_unica_test.py v3
run acao_unica_gemini python3 acao_unica_test.py gemini
run etapas_celular python3 etapas_celular_test.py
run saftest python3 saftest.py
run cmptest python3 cmptest.py
run saf38test python3 saf38test.py
run psfix38test python3 psfix38test.py
run tabelas_os_test python3 tabelas_os_test.py
run tabelas_est_test python3 tabelas_est_test.py
run testes_pedido python3 testes_pedido.py
run varredura python3 varredura.py
run acoes_duplicadas python3 ../ferramentas/acoes_duplicadas.py . /tmp/SAF-dup.json
echo "### FIM $(date +%H:%M:%S)" >> $OUT/resumo.txt
