#!/bin/bash
E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/r2; X=$E/resumo-extra.txt; export CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
lit(){ ps -eo args | grep -cE '^/tmp/cloudchrome/chrome .*remote-debugging-port'; }
ativos(){ ps -eo etimes=,args= | awk '/chrome-linux\/chrome/ && /--remote-debugging-port/ && !/--type=/ && $1<7200' | wc -l; }
espera(){ while [ "$(lit)" -gt 1 ] || [ "$(ativos)" -gt 1 ]; do sleep 5; done; echo "$(date +%T) literal=$(lit) ativos<2h=$(ativos)" >> $E/logs/gate.txt; }
roda(){ dir=$1; nome=$2; shift 2; espera; t0=$(date +%s); ( cd $dir && timeout 1500 "$@" ) > $E/logs/$nome.log 2>&1; rc=$?
  echo "$nome exit=$rc secs=$(( $(date +%s)-t0 )) | $(grep -v agent-proxy $E/logs/$nome.log | grep -v '^\s*$' | tail -1 | cut -c1-170)" >> $X; }
C=/tmp/claude-0/pr88b/tools/prototipo/v37/gen37; B=/tmp/claude-0/c9base/tools/prototipo/v37/gen37
roda $C config_test_resto python3 -B config_test.py cf04 cf03 cf05 rev rev2 m390
if grep -q "^config_test_resto exit=[^0]" $X; then roda $B config_test_resto-base python3 -B config_test.py cf04 cf03 cf05 rev rev2 m390; fi
echo FIM2 >> $X
