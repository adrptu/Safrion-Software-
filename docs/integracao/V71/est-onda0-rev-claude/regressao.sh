#!/bin/bash
# Regressão da revisão EST-ONDA0: um teste por vez, timeout 900, guarda a linha RESULTADO (ou a última linha e o código de saída).
# Uso: regressao.sh <gen37> <rotulo> [testes...]
G="$1"; ROT="$2"; shift 2
O=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude/reg_$ROT; mkdir -p "$O"
TESTES=("$@")
[ ${#TESTES[@]} -eq 0 ] && TESTES=(est_cenario_test.py est_a4_test.py est_a4_nav_test.py est_item_divergente_test.py est_item_divergente_nav.py est_validade_entrada_test.py est_validade_entrada_nav.py est_validade_test.py est_validade_data_test.py est_validade_nav.py est_validade_conc_nav_test.py est_validade_conflito_nav.py est_validade_memoria_nav.py est_validade_quar_dem_test.py est_sem_validade_nav.py est_laudo_lote_nav_test.py est_fix1_test.py est_fix2_test.py esttest.py verif_ce_est.py consumo_divergente_test.py ben_fluxo_test.py demanda_estado_nav_test.py map_aprov_test.py map_decisoes_test.py os_cenario_test.py sutest.py visoes_marcas.py config_test.py cmptest.py paginas_scan_test.py)
cd "$G" || exit 2
for t in "${TESTES[@]}"; do
  ini=$(date +%s)
  timeout 900 env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico python3 -B "$t" > "$O/${t%.py}.log" 2>&1; rc=$?
  res=$(grep -a "RESULTADO" "$O/${t%.py}.log" | tail -n 1); [ -z "$res" ] && res="(sem RESULTADO) $(tail -n 1 "$O/${t%.py}.log" | cut -c1-200)"
  echo "$t | rc=$rc | $(( $(date +%s)-ini ))s | $res" | tee -a "$O/_resumo.txt"
done
echo FIM >> "$O/_resumo.txt"
