#!/bin/bash
# v131 final = v130 + DS-MAN + C-3/C-4 (c65df394): impacto das duas frentes no render composto; um Chrome por vez
cd /tmp/claude-0/intn1/tools/prototipo/v37/gen37
O=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/v131f
export CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico
r(){ n=$1; shift; until [ $(ps -eo args | grep -E "chrom(e|ium)-linux/chrome |/cloudchrome/chrome " | grep -v -- "--type=" | grep -v grep | wc -l) -lt 4 ]; do sleep 10; done
  timeout 1500 "$@" > $O/$n.log 2>&1; echo "$n rc=$? $(grep -E 'RESULTADO|TOTAL|FALHAS:|ok ·|PASS 6|catraca' $O/$n.log | tail -1 | cut -c1-160)"; }
r c34_test node c34_test.cjs
r c34_paridade python3 -B c34_paridade_test.py
r n1_composicao node n1_composicao_test.cjs
for t in est_onda0_test demanda_unica_test mip_unit_test legal_unit_test; do r $t python3 -B $t.py; done
for t in c34_fluxo_test n1_fluxo_test ds_man_test ma_vinculo_test ma_unica_test saf_cmp_continuidade_test compras_materiais_test d5_reserva_test est_a4_nav_test tabelas_est_test tabelas_os_test mip_fluxo_test ds_test paginas_scan_test links_ocultos_test; do r $t python3 -B $t.py; done
echo FIM
