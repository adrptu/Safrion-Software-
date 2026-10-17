#!/bin/bash
E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/r2; X=$E/resumo-extra.txt; export CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
for T in /tmp/claude-0/pr88c /tmp/claude-0/c9base; do ( cd $T/tools/prototipo/v37/gen37 && python3 -W error::SyntaxWarning -B build.py && python3 -B montar_render.py ) > $E/logs/build-$(basename $T).log 2>&1; echo "build $(basename $T) exit=$? $(tail -1 $E/logs/build-$(basename $T).log)" >> $X; done
lit(){ ps -eo args | grep -cE '^/tmp/cloudchrome/chrome .*remote-debugging-port'; }
ativos(){ ps -eo etimes=,args= | awk '/chrome-linux\/chrome/ && /--remote-debugging-port/ && !/--type=/ && $1<7200' | wc -l; }
espera(){ while [ "$(lit)" -gt 1 ] || [ "$(ativos)" -gt 1 ]; do sleep 5; done; echo "$(date +%T) literal=$(lit) ativos<2h=$(ativos)" >> $E/logs/gate.txt; }
roda(){ dir=$1; nome=$2; shift 2; espera; t0=$(date +%s); ( cd $dir && timeout 1800 "$@" ) > $E/logs/$nome.log 2>&1; rc=$?
  echo "$nome exit=$rc secs=$(( $(date +%s)-t0 )) | $(grep -v agent-proxy $E/logs/$nome.log | grep -v '^\s*$' | tail -1 | cut -c1-170)" >> $X; }
roda /tmp/claude-0/pr88c/tools/prototipo/v37/gen37 ds_test-b989864+PR python3 -B ds_test.py
roda /tmp/claude-0/c9base/tools/prototipo/v37/gen37 ds_test-b989864-base python3 -B ds_test.py
echo FIM3 >> $X
