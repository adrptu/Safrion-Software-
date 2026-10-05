#!/bin/bash
C=$(dirname $(dirname $(readlink -f $0))); E=$C/../entradas
run(){ n=$1; d=$2; node $C/scripts/cx_run.js $C/$d/tools/prototipo/v37/gen37/safra.js $E/aleatorias_s20261004.json 1 > $C/brutos/aleat_js_$n.jsonl 2> $C/brutos/aleat_js_$n.err; echo "$n rc=$? $(date -u +%T) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $C/brutos/_aleat_js.log; }
run P0 src/2e31588 & run P2 var/p2 & wait
run P2u var/p2u & run P1_2e18 var/p1_2e18 & wait
run P1_2e20 var/p1_2e20 & run P1_2e22 var/p1_2e22 & wait
