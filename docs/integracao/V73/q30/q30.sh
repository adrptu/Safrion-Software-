#!/bin/bash
# Bateria q30: composição b989864 + PR #81 (7a6aa56) + PRs #90/#91 (05947ad), render em /tmp/claude-0/int90
O=/tmp/claude-0/q30.out; : > $O
G=/tmp/claude-0/int90/tools/prototipo/v37/gen37; cd $G || exit 1
{ SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py > /tmp/claude-0/q30_build.log 2>&1 && SAFRION_DADOS=sintetico python3 -B montar_render.py >> /tmp/claude-0/q30_build.log 2>&1; } || { echo "BUILD FALHOU" >> $O; exit 1; }
echo "render $(git rev-parse --short HEAD): $(ls _render/*.html | wc -l) páginas" >> $O
for f in est_onda0_unit.js credito_ficha_unit.js credito_ficha_motor_unit.js; do [ -f $f ] && { node $f > /tmp/claude-0/q30_$f.log 2>&1; echo "rc=$? node $f :: $(grep -E '[0-9]+/[0-9]+|RESULTADO|ok' /tmp/claude-0/q30_$f.log | tail -1 | cut -c1-120)" >> $O; }; done
[ -f credito_ficha_build.py ] && { SAFRION_DADOS=sintetico python3 -B credito_ficha_build.py > /tmp/claude-0/q30_cfbuild.log 2>&1; echo "rc=$? credito_ficha_build.py :: $(tail -1 /tmp/claude-0/q30_cfbuild.log | cut -c1-120)" >> $O; }
for a in "ds_inventario.py --catraca"; do SAFRION_DADOS=sintetico python3 -B $a > /tmp/claude-0/q30_dsinv.log 2>&1; echo "rc=$? $a :: $(tail -1 /tmp/claude-0/q30_dsinv.log | cut -c1-120)" >> $O; done
run(){ until [ "$(ps -eo args | grep -cE '^/tmp/cloudchrome/chrome .*remote-debugging-port')" -le 1 ]; do sleep 15; done
  s=$(date +%s); L=/tmp/claude-0/q30_$(echo "$*" | tr ' /=' '___').log
  env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 2400 python3 -B "$@" > $L 2>&1; rc=$?
  echo "rc=$rc $(( $(date +%s)-s ))s $* :: OK=$(grep -c '^OK' $L) FALHA=$(grep -c '^FALHA' $L) · $(grep -E 'RESULTADO|ok · |[0-9]+/[0-9]+|catraca' $L | tail -1 | cut -c1-140)" >> $O; }
run est_onda0_test.py
run credito_menu_test.py
run links_ocultos_test.py
run cadastros_rev1_test.py
run cad_gravacao_falha_test.py
run ds_modulos.py --catraca
run est_a4_test.py
run consumo_divergente_test.py
run os_cenario_test.py
run tabelas_est_test.py
run ben_fluxo_test.py multilote multilote390 rodape
run cadastros_padrao_test.py
run demanda_estado_nav_test.py
run paginas_scan_test.py
echo FIM >> $O
