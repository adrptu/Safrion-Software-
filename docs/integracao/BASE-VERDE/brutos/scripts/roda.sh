#!/bin/bash
# uso: roda.sh <dir gen37> <dir logs> <lista> [trava]   lista: nome|VAR=v ...|comando e argumentos
# Mede o tempo de parede DENTRO da trava (não conta a espera pela trava). Retoma: pula o que já está no _resumo.txt.
G=$1; O=$2; L=$3; LK=${4:-/tmp/cdpA.lock}; mkdir -p $O; cd $G
while IFS='|' read -r nome envs cmd; do
  [ -z "$nome" ] && continue; case "$nome" in \#*) continue;; esac
  grep -q "^$nome rc=" $O/_resumo.txt 2>/dev/null && continue
  f=${cmd%% *}; [ -f "$f" ] || { echo "$nome AUSENTE" | tee -a $O/_resumo.txt; continue; }
  env CHROME_BIN=/tmp/cloudchrome/chrome flock $LK bash -c "t0=\$(date +%s.%N); env CDP_GL=1 SAFRION_DADOS=sintetico $envs timeout 900 python3 $cmd > $O/$nome.log 2>&1; rc=\$?; t1=\$(date +%s.%N); echo \"\$rc \$(echo \"\$t1-\$t0\"|bc)\" > $O/$nome.t" < /dev/null
  read rc t < $O/$nome.t
  echo "$nome rc=$rc t=${t}s :: $(grep -E 'RESULTADO|TOTAL|páginas sem erro|^[0-9]+ ok|ok ·|falhas' $O/$nome.log | tail -2 | tr '\n' ' ' | cut -c1-240)" | tee -a $O/_resumo.txt
done < $L
echo "FIM $(date +%T)" >> $O/_resumo.txt
