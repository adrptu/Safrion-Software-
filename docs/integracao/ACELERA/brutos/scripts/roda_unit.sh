#!/bin/bash
# uso: roda_unit.sh <dir gen37> <dir logs> <lista>  — testes sem navegador, com o mesmo resumo do units.sh da V56
G=$1; O=$2; L=$3; mkdir -p $O; cd $G
while IFS='|' read -r nome envs cmd; do
  [ -z "$nome" ] && continue; grep -q "^$nome rc=" $O/_resumo.txt 2>/dev/null && continue
  t0=$(date +%s.%N); env SAFRION_DADOS=sintetico $envs timeout 900 python3 $cmd > $O/$nome.log 2>&1 < /dev/null; rc=$?; t1=$(date +%s.%N)
  echo "$nome rc=$rc t=$(echo "$t1-$t0"|bc)s :: $(grep -E 'RESULTADO|TOTAL|^[0-9]+/[0-9]+|ok ·|falhas' $O/$nome.log | tail -2 | tr '\n' ' ' | cut -c1-220)" | tee -a $O/_resumo.txt
done < $L
echo "FIM $(date +%T)" >> $O/_resumo.txt
