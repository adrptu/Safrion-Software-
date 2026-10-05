#!/bin/bash
# bateria adversarial no Python: P0, P2, P2u e P1 2^18 em todos os casos; P1 2^20 e 2^22 só nos piores (lista em entradas/adversariais_piores.json)
W=$1; cd $W/scripts; A=$W/entradas/adversariais.json
for v in src/c2e3:P0 var/p2:P2 var/p2u:P2u var/p1_2e18:P1_2e18; do r=${v%%:*}; n=${v##*:}
  (echo "# loadavg antes: $(cat /proc/loadavg)"; timeout 5400 python3 run_py.py $W/$r $A 1; echo "# saída $? · loadavg depois: $(cat /proc/loadavg)") > $W/brutos/adv_py_$n.txt 2>&1; echo "$n ok $(date +%T)"; done
for v in var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22; do r=${v%%:*}; n=${v##*:}
  (echo "# loadavg antes: $(cat /proc/loadavg)"; timeout 5400 python3 run_py.py $W/$r $W/entradas/adversariais_piores.json 0; echo "# saída $? · loadavg depois: $(cat /proc/loadavg)") > $W/brutos/adv_py_$n.txt 2>&1; echo "$n ok $(date +%T)"; done
echo fim
