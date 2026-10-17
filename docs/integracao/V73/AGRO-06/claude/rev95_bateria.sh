#!/bin/bash
# rev95: testes de navegador do solo e a varredura, um por vez, cada um só com o portão (≤ 1 Chrome principal). Brutos em $S/bat_*.log
S=/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/rev95
G=/tmp/claude-0/rev95/tools/prototipo/v37/gen37
porta() { until [ "$(ps -eo args | grep -E '/chrome-linux/chrome ' | grep -v -- '--type=' | grep -v grep | wc -l)" -le 1 ]; do sleep 2; done; }
cd $G
for t in "solo_ag02_test.py desktop" "solo_ag02_test.py celular" "mapa_solo_texto_test.py" "solo_rev_test.py" "solo_mapa_calor_test.py" "solo_saf_test.py" "paginas_scan_test.py"; do
  n=$(echo $t | tr ' ' '_'); porta
  echo "== $t · início $(date -u +%T) · chrome principais: $(ps -eo args | grep -E '/chrome-linux/chrome ' | grep -v -- '--type=' | grep -v grep | wc -l)" > $S/bat_$n.log
  env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 1500 python3 -B $t >> $S/bat_$n.log 2>&1; echo "exit=$?" >> $S/bat_$n.log
  echo "$t: $(grep -E 'RESULTADO|^exit=' $S/bat_$n.log | tr '\n' ' ')"
done
