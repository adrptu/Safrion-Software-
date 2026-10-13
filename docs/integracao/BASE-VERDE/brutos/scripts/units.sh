#!/bin/bash
# uso: units.sh <dir gen37> <dir logs> ; roda os testes sem navegador que existem nesse lado
G=$1; O=$2; mkdir -p $O; cd $G
while IFS='|' read -r nome cmd; do
  [ -z "$nome" ] && continue; f=${cmd%% *}; [ -f "$f" ] || { echo "$nome AUSENTE_NESTE_LADO" >> $O/_resumo_unit.txt; continue; }
  ini=$(date +%s); env SAFRION_DADOS=sintetico timeout 900 python3 $cmd > $O/$nome.log 2>&1; rc=$?; fim=$(date +%s)
  echo "$nome rc=$rc t=$((fim-ini))s :: $(grep -E 'RESULTADO|TOTAL|^[0-9]+/[0-9]+|ok ·|falhas' $O/$nome.log | tail -2 | tr '\n' ' ' | cut -c1-220)" >> $O/_resumo_unit.txt
done <<'L'
ds_unit_test|ds_unit_test.py
tabelas_cad_irr_unit|tabelas_cad_irr_unit.py
outorga_unit_test|outorga_unit_test.py
usar_os_unit_test|usar_os_unit_test.py
ficha_pivo_unit_test|ficha_pivo_unit_test.py
praga_alvo_unit_test|praga_alvo_unit_test.py
solo_unit_test|solo_unit_test.py
pa_regras_test|pa_regras_test.py
comercial_unit_test|comercial_unit_test.py
producao_unit_test|producao_unit_test.py
ben_unit_test|ben_unit_test.py
ma_regras_test|ma_regras_test.py
ma_app_test|ma_app_test.py
os_aprov_lib_test|os_aprov_lib_test.py
dose_divergente_unit|dose_divergente_test.py unit
cafe_apurar_unit|cafe_apurar_test.py unit
links_ocultos_test|links_ocultos_test.py
L
echo FIM >> $O/_resumo_unit.txt
