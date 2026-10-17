#!/bin/bash
SP=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad; B=$SP/n1/int
cd /tmp/claude-0/intn1/tools/prototipo/v37/gen37 || exit 1
E="env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico RENDER_DIR=$PWD/_render"
for t in n1_adapter_test n1_emission_test n1_recipe_test n1_composicao_test; do node $t.cjs > $B/$t.log 2>&1; echo "$t rc=$? $(tail -1 $B/$t.log | cut -c1-110)"; done
for t in mip_unit_test legal_unit_test quantidade_test os_aprov_lib_test usar_os_unit_test; do $E timeout 900 python3 -B $t.py > $B/$t.log 2>&1; echo "$t rc=$? $(grep -aE 'RESULTADO|TOTAL' $B/$t.log | tail -1 | cut -c1-110)"; done
$E python3 -B ds_modulos.py --catraca > $B/ds_modulos.log 2>&1; echo "ds_modulos rc=$? $(grep -a 'RESULTADO' $B/ds_modulos.log | tail -1 | cut -c1-110)"
for t in n1_fluxo_test mip_fluxo_test mip_correcoes_test tabelas_os_test os_lote_test kanban_raias_test cartoes_test ds_test ds_1610_test acao_unica_test saf_fazenda_recolhida_test mapa_mux_f0_test mapa_mux_f1_test carencia_test solo_os_test ctl5_test mbtest textos_soltos_test links_ocultos_test paginas_scan_test drill_recolhido_test; do
  [ -f $t.py ] || { echo "$t ausente"; continue; }
  $E timeout 2700 python3 -B $t.py > $B/$t.log 2>&1; echo "$t rc=$? $(grep -aE 'RESULTADO|TOTAL' $B/$t.log | tail -1 | cut -c1-140)"; done
