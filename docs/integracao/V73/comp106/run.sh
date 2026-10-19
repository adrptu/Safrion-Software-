cd /tmp/claude-0/int90/tools/prototipo/v37/gen37
for t in compras_materiais_unit_test compras_materiais_test acao_unica_test componentes_test textos_soltos_test links_ocultos_test demanda_estado_nav_test quantidade_test paginas_scan_test; do
  env GEN37=/tmp/claude-0/int90/tools/prototipo/v37/gen37 SHOTS=$SP/t106/shots CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=/tmp/claude-0/int90/tools/prototipo/v37/gen37/_render timeout 900 python3 -B $t.py > $SP/t106/$t.log 2>&1; echo "$t rc=$? $(grep -Eo '[0-9]+/[0-9]+' $SP/t106/$t.log | tail -1)"
done
