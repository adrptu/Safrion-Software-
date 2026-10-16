#!/bin/bash
# Uso: regressao.sh <gen37> <pasta_logs> <lista de testes...>
G="$1"; L="$2"; shift 2
cd "$G" || exit 1
for t in "$@"; do
  n=$(echo "$t" | tr ' /' '__')
  env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B $t > "$L/$n.log" 2>&1
  rc=$?
  r=$(grep -a "RESULTADO" "$L/$n.log" | tail -1)
  echo "$t | rc=$rc | ${r:-sem RESULTADO: $(tail -1 "$L/$n.log" | cut -c1-160)}" >> "$L/_resumo.txt"
done
echo FIM >> "$L/_resumo.txt"
