#!/bin/bash
# fila 3 (reteste 2f0a1f0): um teste de navegador por vez, cada um atrás do portão (≤ 1 Chrome principal)
L=/tmp/claude-0/rev94_tools/r2; C=/tmp/claude-0/rev94/tools/prototipo/v37/gen37; S=/tmp/claude-0/rev94_tools/s
roda(){ nome=$1; dir=$2; shift 2; $S/rev94_gate.sh >/dev/null; t0=$(date +%s); ( cd "$dir" && env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B "$@" ) > $L/$nome.log 2>&1; rc=$?; echo "$(date +%H:%M:%S) rc=$rc $(( $(date +%s)-t0 ))s $nome :: $(grep -E 'RESULTADO|ok · ' $L/$nome.log | tail -1)" >> $L/fila3_resumo.txt; }
: > $L/fila3_resumo.txt
roda sonda $C $S/rev94_sonda.py $C $L/sonda
roda mip_fluxo $C mip_fluxo_test.py
roda mip_correcoes $C mip_correcoes_test.py
echo FIM >> $L/fila3_resumo.txt
