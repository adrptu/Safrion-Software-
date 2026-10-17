#!/bin/bash
# retomada após o reinício do contêiner: só o que não terminou (config_test_cf01 terminou: 38/39)
E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/r2; RES=$E/resumo.txt; X=$E/resumo-extra.txt; export CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
lit(){ ps -eo args | grep -cE '^/tmp/cloudchrome/chrome .*remote-debugging-port'; }   # comando do coordenador (o wrapper faz exec: tende a 0)
ativos(){ ps -eo etimes=,args= | awk '/chrome-linux\/chrome/ && /--remote-debugging-port/ && !/--type=/ && $1<7200' | wc -l; }   # navegadores reais < 2 h
espera(){ while [ "$(lit)" -gt 1 ] || [ "$(ativos)" -gt 1 ]; do sleep 5; done; echo "$(date +%T) literal=$(lit) ativos<2h=$(ativos)" >> $E/logs/gate.txt; }
roda(){ dir=$1; out=$2; nome=$3; shift 3; espera; t0=$(date +%s); ( cd $dir && timeout 1200 "$@" ) > $E/logs/$nome.log 2>&1; rc=$?
  echo "$nome exit=$rc secs=$(( $(date +%s)-t0 )) | $(grep -v agent-proxy $E/logs/$nome.log | grep -v '^\s*$' | tail -1 | cut -c1-170)" >> $out; }
C=/tmp/claude-0/pr88b/tools/prototipo/v37/gen37; B=/tmp/claude-0/c9base/tools/prototipo/v37/gen37
roda $C $RES ds_modulos_catraca env DS_MOD_JSON=$E/ds-modulos.json python3 -B ds_modulos.py --catraca
roda $C $RES paginas_scan_test python3 -B paginas_scan_test.py
echo FIM >> $RES
roda $C $X origem_grupo_cand env GEN37=$C RENDER_DIR=$C/_render python3 -B $E/origem_grupo_test.py
roda $B $X config_test_cf01-base python3 -B config_test.py cf01
roda $B $X carencia_test-base python3 -B carencia_test.py
if grep -q "^ds_modulos_catraca exit=[^0]" $RES; then roda $B $X ds_modulos_catraca-base env DS_MOD_JSON=$E/ds-modulos-base.json python3 -B ds_modulos.py --catraca; fi
if grep -q "^paginas_scan_test exit=[^0]" $RES; then roda $B $X paginas_scan_test-base python3 -B paginas_scan_test.py; fi
echo FIM >> $X
