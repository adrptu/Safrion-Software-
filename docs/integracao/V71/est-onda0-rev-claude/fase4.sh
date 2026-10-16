#!/bin/bash
# Fase 4: BEN na base (fluxo, lotes, cadeia) e prova do ajuste proposto para o modo sobra no PR. Um por vez, timeout 900.
O=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude; PR=/tmp/claude-0/pr81/tools/prototipo/v37/gen37; BA=/tmp/claude-0/pr81base/tools/prototipo/v37/gen37
mkdir -p $O/fase4; R=$O/fase4/_resumo.txt
roda(){ rot="$1"; dir="$2"; shift 2; ini=$(date +%s)
  ( cd "$dir" && timeout 900 env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico GEN="$dir" python3 -B "$@" ) > "$O/fase4/$rot.log" 2>&1; rc=$?
  res=$(grep -a "RESULTADO" "$O/fase4/$rot.log" | tail -n 1); [ -z "$res" ] && res="(sem RESULTADO) $(tail -n 1 "$O/fase4/$rot.log" | cut -c1-200)"
  echo "$rot | rc=$rc | $(( $(date +%s)-ini ))s | $res" | tee -a $R; }
until grep -q FIM $O/fase3/_resumo.txt 2>/dev/null; do sleep 20; done
roda pr_ben_sobra_ajuste $PR $O/ben_fluxo_test_ajuste_sobra.py sobra
roda pr_ben_sobra390_ajuste $PR $O/ben_fluxo_test_ajuste_sobra.py sobra390
for m in fluxo lotes cadeia; do roda base_ben_$m $BA ben_fluxo_test.py $m; done
echo FIM >> $R
