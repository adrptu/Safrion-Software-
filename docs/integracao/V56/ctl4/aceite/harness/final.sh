#!/bin/bash
# bateria + aceite + roteiro + motor na candidata 7e74e6d (um teste de navegador por vez na trava cdpN)
D=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/integ/V56/ctl4; G=/home/user/sp-v56/tools/prototipo/v37/gen37
bash $D/harness/nav.sh $G $D/logs/cand-7e74e6d $D/harness/lista_cand.txt > $D/logs/bateria_7e74e6d.out 2>&1
echo BATERIA-FIM >> $D/logs/final2.out
rm -rf $D/shots/aceite2; mkdir -p $D/shots/aceite2
cd $D
env GEN=$G CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 harness/roteiro.py 7e74e6d > logs/roteiro_7e74e6d.stdout 2>&1; echo "roteiro rc=$?" >> logs/final2.out
env GEN=$G OUTD=$D/shots/aceite2 LOGF=$D/logs/aceite_7e74e6d.log OUTJ=$D/logs/aceite_7e74e6d.json CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpN.lock env CDP_GL=1 SAFRION_DADOS=sintetico timeout 1800 python3 harness/aceite.py > logs/aceite_7e74e6d.stdout 2>&1; echo "aceite rc=$?" >> logs/final2.out
env GEN=$G VER=7e74e6d SAFRION_DADOS=sintetico timeout 600 python3 harness/m_s2.py > logs/motor_7e74e6d.log 2>&1; echo "motor rc=$?" >> logs/final2.out
echo FIM >> logs/final2.out
