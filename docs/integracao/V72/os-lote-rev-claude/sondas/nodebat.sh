#!/bin/bash
E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/semnav; mkdir -p $E
for TREE in pr88 v72; do
 cd /tmp/claude-0/$TREE/tools/prototipo/v37/gen37 || exit 2
 for T in aprova_quem_decide_test.py assinatura_unit_test.py ben_prop_test.py ben_unit_test.py cal01_test.py cen_grava_test.py comercial_unit_test.py compras_materiais_unit_test.py conferencia_diaria_test.py config_app_unit_test.py config_regressao_test.py config_unit_test.py ds_unit_test.py est_a4_test.py est_item_divergente_test.py est_validade_conc_nav_test.py est_validade_data_test.py est_validade_entrada_test.py est_validade_quar_dem_test.py est_validade_test.py ficha_pivo_unit_test.py inicio_entrega_test.py inteligencia_nav_test.py inteligencia_unit_test.py irr_onda0_test.py links_ocultos_test.py ma_app_test.py ma_atrito_test.py ma_menu_test.py ma_regras_test.py outorga_unit_test.py pa_regras_test.py plano_referencia_comando_test.py plano_referencia_unit_test.py praga_alvo_unit_test.py producao_unit_test.py quantidade_test.py solo_regressao_test.py; do
  SAFRION_DADOS=sintetico timeout 600 python3 -B $T > $E/${T%.py}-$TREE.log 2>&1; rc=$?
  echo "$T $TREE exit=$rc | $(grep -v agent-proxy $E/${T%.py}-$TREE.log | grep -v '^\s*$' | tail -1 | cut -c1-160)" >> $E/resumo.txt
 done
done
echo FIM >> $E/resumo.txt
