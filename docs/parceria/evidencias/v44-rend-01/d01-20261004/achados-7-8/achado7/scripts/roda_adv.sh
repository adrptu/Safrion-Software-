#!/bin/bash
# bateria adversarial (71 casos, semente 20261004): JS em todas as variantes (1 instrumentada + 1 cronometrada), um processo por vez
W=$1; cd $W/scripts; A=$W/entradas/adversariais.json
for v in src/c2e3:P0 var/p2:P2 var/p2u:P2u var/p1_2e18:P1_2e18 var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22; do r=${v%%:*}; n=${v##*:}
  (echo "# loadavg antes: $(cat /proc/loadavg)"; node run_js.js $W/$r $A 1; echo "# saída $? · loadavg depois: $(cat /proc/loadavg)") > $W/brutos/adv_js_$n.txt 2>&1; echo "$n ok $(date +%T)"; done
echo fim
