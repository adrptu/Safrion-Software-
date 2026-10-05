#!/bin/bash
# 3 300 entradas aleatórias (semente 20261004) em cada variante, JS; $2 = lista de variantes raiz:nome
W=$1; shift; cd $W/scripts; A=$W/entradas/aleatorias_s20261004.json
for v in "$@"; do r=${v%%:*}; n=${v##*:}; node run_lote.js $W/$r $A > $W/brutos/aleat_js_$n.jsonl 2> $W/brutos/aleat_js_$n.err; echo "$n saída $? $(wc -l < $W/brutos/aleat_js_$n.jsonl) linhas · $(cat /proc/loadavg)"; done
echo fim
