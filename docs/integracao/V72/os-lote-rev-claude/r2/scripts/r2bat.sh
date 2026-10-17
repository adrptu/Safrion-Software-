#!/bin/bash
# Revisão R2 do PR #88 · candidata /tmp/claude-0/pr88b (c9ffa08 + merge 3b38b3e). Navegador: espera até haver no máximo 1 Chrome cloudchrome.
G=/tmp/claude-0/pr88b/tools/prototipo/v37/gen37; E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/r2; mkdir -p $E/logs
RES=$E/resumo.txt; export CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
# o wrapper /tmp/cloudchrome/chrome faz exec do chromium: o processo real não tem "cloudchrome" no cmdline (o pgrep literal só conta shells);
# conta navegadores principais ativos (sem --type=, com --remote-debugging-port, iniciados há < 20 min; órfãos antigos de outras sessões fora)
ativos(){ ps -eo etimes=,args= | awk '/chrome-linux\/chrome/ && /--remote-debugging-port/ && !/--type=/ && $1<1200' | wc -l; }
espera(){ while [ "$(ativos)" -gt 1 ]; do sleep 5; done; echo "$(date +%T) ativos=$(ativos) pgrep_literal=$(pgrep -f 'cloudchrome/chrome.*remote-debugging' | wc -l)" >> $E/logs/gate.txt; }
roda(){ nome=$1; nav=$2; shift 2; [ "$nav" = nav ] && espera; t0=$(date +%s); ( cd $G && timeout 1200 "$@" ) > $E/logs/$nome.log 2>&1; rc=$?
  echo "$nome exit=$rc secs=$(( $(date +%s)-t0 )) | $(grep -v agent-proxy $E/logs/$nome.log | grep -v '^\s*$' | tail -1 | cut -c1-170)" >> $RES; }
cd $G
roda os_lote_unit sem node os_lote_unit.js
roda alocacao_unit_test sem python3 -B alocacao_unit_test.py
roda mip_unit_test sem python3 -B mip_unit_test.py
roda demanda_unica_test sem python3 -B demanda_unica_test.py
roda cal01_test sem python3 -B cal01_test.py
roda config_unit_test sem python3 -B config_unit_test.py
roda links_ocultos_test sem python3 -B links_ocultos_test.py
roda aprova_quem_decide_test sem python3 -B aprova_quem_decide_test.py
roda ds_inventario_catraca sem python3 -B ds_inventario.py --catraca
roda os_lote_test nav env RENDER_DIR=$G/_render OS_LOTE_EVIDENCIA=$E/os_lote_test python3 -B os_lote_test.py
roda ui_rev_1440 nav env GEN37=$G RENDER_DIR=$G/_render W=1440 SAIDA=$E/ui python3 -B /tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/ui_rev_test.py
roda ui_rev_390 nav env GEN37=$G RENDER_DIR=$G/_render W=390 SAIDA=$E/ui python3 -B /tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/ui_rev_test.py
for T in os_v39_liberar_test carencia_test mip_fluxo_test mip_correcoes_test os_recurso_test tabelas_os_test os_cenario_test ctl5_test; do roda $T nav python3 -B $T.py; done
roda config_test_cf01 nav python3 -B config_test.py cf01
roda ds_modulos_catraca nav env DS_MOD_JSON=$E/ds-modulos.json python3 -B ds_modulos.py --catraca
roda paginas_scan_test nav python3 -B paginas_scan_test.py
echo FIM >> $RES
