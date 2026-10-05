#!/bin/bash
# roda, em sequência (um processo por vez, para o tempo não disputar CPU entre variantes), cada variante nos casos principais, extras e contraexemplo
W=$1; cd $W/scripts
for v in src/c2e3:P0 var/p1_2e18:P1_2e18 var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22 var/p2:P2 var/p2u:P2u; do r=${v%%:*}; n=${v##*:}
  for e in casos_principais casos_extras contraexemplo; do (echo "# loadavg antes: $(cat /proc/loadavg)"; node run_js.js $W/$r $W/entradas/$e.json 3; echo "# loadavg depois: $(cat /proc/loadavg)") > $W/brutos/prop_js_${n}_$e.txt 2>&1; done; done
echo fim
