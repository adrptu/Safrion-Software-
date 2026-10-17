#!/bin/bash
# continuação do r2bat.sh (interrompido no portão antes do ctl5): portão conta navegadores principais com menos de 2 h (órfãos de 8–11 h fora)
E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/r2; RES=$E/resumo.txt; export CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
ativos(){ ps -eo etimes=,args= | awk '/chrome-linux\/chrome/ && /--remote-debugging-port/ && !/--type=/ && $1<7200' | wc -l; }
espera(){ while [ "$(ativos)" -gt 1 ]; do sleep 5; done; echo "$(date +%T) ativos=$(ativos) (limite 2 h)" >> $E/logs/gate.txt; }
roda(){ dir=$1; out=$2; nome=$3; shift 3; espera; t0=$(date +%s); ( cd $dir && timeout 1200 "$@" ) > $E/logs/$nome.log 2>&1; rc=$?
  echo "$nome exit=$rc secs=$(( $(date +%s)-t0 )) | $(grep -v agent-proxy $E/logs/$nome.log | grep -v '^\s*$' | tail -1 | cut -c1-170)" >> $out; }
C=/tmp/claude-0/pr88b/tools/prototipo/v37/gen37; B=/tmp/claude-0/c9base/tools/prototipo/v37/gen37
roda $C $RES ctl5_test python3 -B ctl5_test.py
roda $C $RES config_test_cf01 python3 -B config_test.py cf01
roda $C $RES ds_modulos_catraca env DS_MOD_JSON=$E/ds-modulos.json python3 -B ds_modulos.py --catraca
roda $C $RES paginas_scan_test python3 -B paginas_scan_test.py
echo FIM >> $RES
X=$E/resumo-extra.txt
roda $C $X origem_grupo_cand env GEN37=$C RENDER_DIR=$C/_render python3 -B $E/origem_grupo_test.py
roda $B $X carencia_test-base python3 -B carencia_test.py
for t in $(grep -v "exit=0" $RES | grep -E "^(config_test_cf01|ds_modulos_catraca|paginas_scan_test|ctl5_test)" | cut -d' ' -f1); do
  case $t in config_test_cf01) roda $B $X config_test_cf01-base python3 -B config_test.py cf01;;
    ds_modulos_catraca) roda $B $X ds_modulos_catraca-base env DS_MOD_JSON=$E/ds-modulos-base.json python3 -B ds_modulos.py --catraca;;
    *) roda $B $X $t-base python3 -B $t.py;; esac
done
echo FIM >> $X
