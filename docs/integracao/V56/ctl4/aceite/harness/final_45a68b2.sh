#!/bin/bash
# candidata 45a68b2 (render idêntico ao do 3353f86): bateria + roteiro + aceite + motor (um teste de navegador por vez na trava cdpN)
L=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/integ/V56/ctl4rev/c45; H=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/integ/V56/ctl4rev/harness; G=/home/user/sp-v56/tools/prototipo/v37/gen37
echo "INICIO $(date +%T)" >> $L/final.out
bash $H/nav.sh $G $L/cand $L/lista.txt > $L/bateria.out 2>&1
echo "BATERIA-FIM $(date +%T)" >> $L/final.out
cd $L/aceite
env GEN=$G CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 $H/roteiro.py 45a68b2 > roteiro_45a68b2.stdout 2>&1; echo "roteiro rc=$? $(date +%T)" >> $L/final.out
env GEN=$G OUTD=$L/aceite/shots LOGF=$L/aceite/aceite_45a68b2.log OUTJ=$L/aceite/aceite_45a68b2.json CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 1800 python3 $H/aceite.py > aceite_45a68b2.stdout 2>&1; echo "aceite rc=$? $(date +%T)" >> $L/final.out
env GEN=$G VER=45a68b2 SAFRION_DADOS=sintetico timeout 600 python3 $H/m_s2.py > motor_45a68b2.log 2>&1; echo "motor rc=$? $(date +%T)" >> $L/final.out
echo "FIM $(date +%T)" >> $L/final.out
