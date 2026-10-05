#!/bin/bash
# Python (espelho dados2.repartir), em sequência, um processo por vez; 1 execução instrumentada + 1 cronometrada por caso
W=$1; cd $W/scripts
run(){ (echo "# loadavg antes: $(cat /proc/loadavg)"; timeout 1800 python3 run_py.py $W/$1 $W/entradas/$3.json 1; echo "# saída $? · loadavg depois: $(cat /proc/loadavg)") > $W/brutos/prop_py_${2}_$3.txt 2>&1; }
for v in src/c2e3:P0 var/p2:P2 var/p2u:P2u; do r=${v%%:*}; n=${v##*:}; for e in casos_principais casos_extras contraexemplo; do run $r $n $e; done; done
for v in var/p1_2e18:P1_2e18 var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22; do r=${v%%:*}; n=${v##*:}; for e in casos_principais casos_extras_py contraexemplo; do run $r $n $e; done; done
run var/p1_2e18 P1_2e18 casos_extras_so_js
echo fim
