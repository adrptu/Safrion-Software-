#!/bin/bash
# Python nas entradas aleatórias: $2.. = raiz:nome[:amostra]
W=$1; shift; cd $W/scripts; A=$W/entradas/aleatorias_s20261004.json
for v in "$@"; do IFS=: read r n s <<< "$v"
  if [ -n "$s" ]; then timeout 7200 python3 run_lote_py.py $W/$r $A 0 0 $W/entradas/aleatorias_amostra_P1_py.json > $W/brutos/aleat_py_$n.jsonl 2> $W/brutos/aleat_py_$n.err
  else timeout 7200 python3 run_lote_py.py $W/$r $A > $W/brutos/aleat_py_$n.jsonl 2> $W/brutos/aleat_py_$n.err; fi
  echo "$n saída $? $(wc -l < $W/brutos/aleat_py_$n.jsonl) linhas · $(date +%T) · $(cat /proc/loadavg)"; done
echo fim
