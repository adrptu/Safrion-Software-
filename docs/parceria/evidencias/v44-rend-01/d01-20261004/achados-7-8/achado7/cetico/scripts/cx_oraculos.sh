#!/bin/bash
C=$(dirname $(dirname $(readlink -f $0)))
for v in P0:src/2e31588 P1_2e18:var/p1_2e18 P1_2e20:var/p1_2e20 P1_2e22:var/p1_2e22 P2:var/p2 P2u:var/p2u; do n=${v%%:*}; d=${v#*:}
  ( cd $C/$d/tools/prototipo/v37/gen37 && s=$(date +%s.%N); python3 rend_multiconjuntos_unit.py > $C/brutos/oraculo_$n.txt 2>&1; echo "rc=$? seg=$(echo "$(date +%s.%N)-$s"|bc) load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $C/brutos/oraculo_$n.txt )
done
