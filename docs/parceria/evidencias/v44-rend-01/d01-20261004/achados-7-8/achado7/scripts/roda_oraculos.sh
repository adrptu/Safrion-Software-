#!/bin/bash
# oráculo rend_multiconjuntos_unit.py (101 casos) em 2e31588 e em cada cópia de proposta, um por vez
W=$1; B=$W/brutos
for v in src/c2e3:P0 var/p1_2e18:P1_2e18 var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22 var/p2:P2 var/p2u:P2u; do r=${v%%:*}; n=${v##*:}
  ( echo "# loadavg antes: $(cat /proc/loadavg)"; cd $W/$r/tools/prototipo/v37/gen37 && T0=$(date +%s.%N) && python3 rend_multiconjuntos_unit.py; s=$?; echo "# saída $s · $(echo "$(date +%s.%N) - $T0" | bc) s · loadavg depois: $(cat /proc/loadavg)" ) > $B/oraculo_$n.txt 2>&1
  echo "$n $(grep RESULTADO $B/oraculo_$n.txt)"; done
