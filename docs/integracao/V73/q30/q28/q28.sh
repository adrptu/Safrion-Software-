#!/bin/bash
# Bateria q28: composição b989864 + PR #81 (7a6aa56), render em /tmp/claude-0/int81
O=/tmp/claude-0/q28.out; : > $O
G=/tmp/claude-0/int81/tools/prototipo/v37/gen37; cd $G || exit 1
{ SAFRION_DADOS=sintetico python3 -W error::SyntaxWarning -B build.py > /tmp/claude-0/q28_build.log 2>&1 && SAFRION_DADOS=sintetico python3 -B montar_render.py >> /tmp/claude-0/q28_build.log 2>&1; } || { echo "BUILD FALHOU" >> $O; exit 1; }
echo "render: $(ls _render/*.html | wc -l) páginas" >> $O
for t in "node est_onda0_unit.js" "python3 -B est_onda0_test.py" "python3 -B ds_modulos.py --catraca" "python3 -B ds_inventario.py --catraca" est_cenario_test.py esttest.py est_sem_validade_nav.py map_decisoes_test.py "ben_fluxo_test.py" est_a4_test.py consumo_divergente_test.py os_cenario_test.py tabelas_est_test.py demanda_estado_nav_test.py paginas_scan_test.py; do
  set -- $t; case $1 in node|python3) cmd="$t"; f=$2;; *) cmd="python3 -B $t"; f=$1;; esac
  [ -f $f ] || { echo "sem $f" >> $O; continue; }
  until [ "$(pgrep -f 'cloudchrome/chrome.*remote-debugging' | wc -l)" -le 1 ]; do sleep 15; done
  s=$(date +%s); L=/tmp/claude-0/q28_${f}.log
  env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 1500 $cmd > $L 2>&1; rc=$?
  echo "rc=$rc $(( $(date +%s)-s ))s $t :: $(grep -E 'RESULTADO|ok · |[0-9]+/[0-9]+|catraca|OK' $L | tail -1 | cut -c1-200)" >> $O
done
echo FIM >> $O
