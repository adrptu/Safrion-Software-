#!/bin/bash
# Fase 3: BEN na base (modos que falharam no PR), map_decisoes ajustado, ben_unit. Um por vez, timeout 900.
O=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude; PR=/tmp/claude-0/pr81/tools/prototipo/v37/gen37; BA=/tmp/claude-0/pr81base/tools/prototipo/v37/gen37
mkdir -p $O/fase3; R=$O/fase3/_resumo.txt
roda(){ rot="$1"; dir="$2"; shift 2; ini=$(date +%s)
  ( cd "$dir" && timeout 900 env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico GEN="$dir" python3 -B "$@" ) > "$O/fase3/$rot.log" 2>&1; rc=$?
  res=$(grep -a "RESULTADO" "$O/fase3/$rot.log" | tail -n 1); [ -z "$res" ] && res="(sem RESULTADO) $(tail -n 1 "$O/fase3/$rot.log" | cut -c1-200)"
  echo "$rot | rc=$rc | $(( $(date +%s)-ini ))s | $res" | tee -a $R; }
roda pr_map_decisoes_ajuste $PR $O/map_decisoes_test_ajuste.py
roda base_map_decisoes_ajuste $BA $O/map_decisoes_test_ajuste.py
for m in sobra conferencia cadeia390 sobra390 conferencia390; do roda base_ben_$m $BA ben_fluxo_test.py $m; done
roda pr_ben_unit $PR ben_unit_test.py
echo FIM >> $R
