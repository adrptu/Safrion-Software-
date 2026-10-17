#!/bin/bash
# rev95 · reteste 74f13a6: cada execução só com o portão (≤ 1 Chrome principal). Brutos em $S/rt_*.log
S=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/rev95
G=/tmp/claude-0/rev95/tools/prototipo/v37/gen37
porta() { until [ "$(ps -eo args | grep -E '/chrome-linux/chrome ' | grep -v -- '--type=' | grep -v grep | wc -l)" -le 1 ]; do sleep 2; done; }
cd $G
run() { n=$1; shift; porta; echo "== $n · início $(date -u +%T) · chrome principais: $(ps -eo args | grep -E '/chrome-linux/chrome ' | grep -v -- '--type=' | grep -v grep | wc -l)" > $S/rt_$n.log
  env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 1500 python3 -B "$@" >> $S/rt_$n.log 2>&1; echo "exit=$?" >> $S/rt_$n.log
  echo "$n: $(grep -E 'RESULTADO|^exit=' $S/rt_$n.log | tr '\n' ' ' | cut -c1-260)"; }
run reteste_74f13a6 $S/rev95_reteste.py $G/_render 1440,390
run reteste_a10656a $S/rev95_reteste.py $S/render_a10656a 1440,390
run sonda_74f13a6 $S/rev95_sonda.py $G/_render 1440,390
run solo_ag02_desktop solo_ag02_test.py desktop
run solo_ag02_celular solo_ag02_test.py celular
