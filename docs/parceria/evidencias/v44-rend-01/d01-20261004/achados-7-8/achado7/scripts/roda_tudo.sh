#!/bin/bash
# pipeline completo do achado 7 (rodada de 04/10/2026); cada etapa grava em brutos/; log em brutos/_roda_tudo.log
W=$1; cd $W/scripts; B=$W/brutos; E=$W/entradas
log(){ echo "$(date +%T) $* · loadavg $(cat /proc/loadavg)" >> $B/_roda_tudo.log; }
log inicio
python3 verif_autoteste.py > $B/verif_autoteste.txt 2>&1; log autoteste $?
for c in c2e3 c04b cee4; do for e in casos_principais contraexemplo M2; do
  node run_js.js $W/src/$c $E/$e.json 3 > $B/repro_js_${c}_$e.txt 2>&1; log repro js $c $e $?
  python3 run_py.py $W/src/$c $E/$e.json 1 > $B/repro_py_${c}_$e.txt 2>&1; log repro py $c $e $?
  python3 run_py.py $W/src/$c $E/$e.json 0 1 > $B/repro_pyfrac_${c}_$e.txt 2>&1; log repro pyfrac $c $e $?
  for k in js py pyfrac; do python3 verif.py $E/$e.json $B/repro_${k}_${c}_$e.txt > $B/verif_repro_${k}_${c}_$e.txt 2>&1; done
  python3 paridade.py $B/repro_js_${c}_$e.txt $B/repro_py_${c}_$e.txt > $B/paridade_repro_${c}_$e.txt 2>&1
done; done; log repro fim
node run_js.js $W/var/cliq $E/casos_principais.json 3 > $B/esperado_cliq_js.txt 2>&1
python3 run_py.py $W/var/cliq $E/casos_principais.json 0 1 > $B/esperado_cliq_pyfrac.txt 2>&1
python3 verif.py $E/casos_principais.json $B/esperado_cliq_js.txt > $B/verif_esperado_cliq_js.txt 2>&1
python3 verif.py $E/casos_principais.json $B/esperado_cliq_pyfrac.txt > $B/verif_esperado_cliq_pyfrac.txt 2>&1
log esperado fim
for v in src/c2e3:P0 var/p1_2e18:P1_2e18 var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22 var/p2:P2 var/p2u:P2u; do r=${v%%:*}; n=${v##*:}
  (cd $W/$r/tools/prototipo/v37/gen37 && /usr/bin/time -f '# tempo %e s' python3 rend_multiconjuntos_unit.py) > $B/oraculo_$n.txt 2>&1; log oraculo $n $?; done
bash roda_var_js.sh $W >> $B/_roda_tudo.log 2>&1; log props js fim
bash roda_var_py.sh $W >> $B/_roda_tudo.log 2>&1; log props py fim
for n in P0 P1_2e18 P1_2e20 P1_2e22 P2 P2u; do for e in casos_principais casos_extras contraexemplo; do
  [ -f $B/prop_js_${n}_$e.txt ] && python3 verif.py $E/$e.json $B/prop_js_${n}_$e.txt > $B/verif_prop_js_${n}_$e.txt 2>&1; done
  for e in casos_principais casos_extras casos_extras_py contraexemplo; do [ -f $B/prop_py_${n}_$e.txt ] && python3 paridade.py $B/prop_js_${n}_$( [ $e = casos_extras_py ] && echo casos_extras || echo $e ).txt $B/prop_py_${n}_$e.txt > $B/paridade_${n}_$e.txt 2>&1; done; done
log props verif fim
bash roda_adv.sh $W >> $B/_roda_tudo.log 2>&1; log adv js fim
bash roda_aleat_js.sh $W src/c2e3:P0 var/p2:P2 var/p2u:P2u var/p1_2e18:P1_2e18 var/p1_2e20:P1_2e20 var/p1_2e22:P1_2e22 >> $B/_roda_tudo.log 2>&1; log aleat js fim
python3 verif_aleat.py $W P0 P2 P2u P1_2e18 P1_2e20 P1_2e22 > $B/_verif_aleat.log 2>&1; log verif aleat fim
python3 resumo_aleat.py $W P0 P1_2e18 P1_2e20 P1_2e22 P2 P2u > $B/resumo_aleat.txt 2>&1; log resumo aleat fim
log fim
