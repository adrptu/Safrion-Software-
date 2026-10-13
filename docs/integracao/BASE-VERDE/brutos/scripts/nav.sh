#!/bin/bash
# uso: nav.sh <dir gen37> <dir logs> <lista>   (lista: nome|VAR=v ...|comando; um teste por vez na trava /tmp/cdpB.lock)
G=$1; O=$2; L=$3; mkdir -p $O; cd $G
while IFS='|' read -r nome envs cmd; do
  [ -z "$nome" ] && continue; case "$nome" in \#*) continue;; esac
  f=${cmd%% *}; [ -f "$f" ] || { echo "$nome AUSENTE" | tee -a $O/_resumo.txt; continue; }
  ini=$(date +%s)
  env CHROME_BIN=/tmp/cloudchrome/chrome flock /tmp/cdpB.lock env CDP_GL=1 SAFRION_DADOS=sintetico $envs timeout 900 python3 $cmd > $O/$nome.log 2>&1; rc=$?
  fim=$(date +%s)
  echo "$nome rc=$rc t=$((fim-ini))s :: $(grep -E 'RESULTADO|TOTAL|páginas sem erro|^[0-9]+ ok|ok ·|falhas' $O/$nome.log | tail -2 | tr '\n' ' ' | cut -c1-240)" | tee -a $O/_resumo.txt
done < $L
echo "FIM $(date +%T)" >> $O/_resumo.txt
