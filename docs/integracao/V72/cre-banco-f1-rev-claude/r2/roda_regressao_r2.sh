#!/bin/bash
# Revisão Claude PR #90 (rodada 2; contagem por ps porque pgrep -f casa a própria linha de comando do shell): bateria de regressão em sequência, um Chrome por vez; espera os Chrome de outros revisores caírem para no máximo 1.
# Uso: roda_regressao.sh <dir gen37> <dir saída> <teste...>
G="$1"; O="$2"; shift 2
cd "$G" || exit 2
for t in "$@"; do
  until [ "$(ps -eo args | grep -cE '^/tmp/cloudchrome/chrome .*remote-debugging-port')" -le 1 ]; do sleep 5; done
  nome=$(basename "$t" .py | tr ' ' '_')
  extra=''
  t0=$(date +%s)
  case "$t" in
    "ds_modulos.py --catraca") env DS_MOD_JSON="$O/ds-modulos-pr.json" CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B ds_modulos.py --catraca > "$O/reg-ds_modulos.log" 2>&1; rc=$?; nome=ds_modulos;;
    *) env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B $t > "$O/reg-$nome.log" 2>&1; rc=$?;;
  esac
  echo "$nome rc=$rc $(( $(date +%s) - t0 ))s · $(grep -E 'RESULTADO' "$O/reg-$nome.log" | tail -n 1)" >> "$O/regressao-resumo.txt"
done
echo FIM >> "$O/regressao-resumo.txt"
