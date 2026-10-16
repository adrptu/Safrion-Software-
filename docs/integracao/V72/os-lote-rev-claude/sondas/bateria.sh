#!/bin/bash
# uso: bateria.sh <tree> <rotulo> teste1 teste2 ...
TREE=$1; ROT=$2; shift 2
E=/tmp/claude-0/pr88/docs/integracao/V72/os-lote-rev-claude/browser
mkdir -p $E
cd /tmp/claude-0/$TREE/tools/prototipo/v37/gen37 || exit 2
for T in "$@"; do
  ARGS=""; NAME=$T
  case $T in visoes_test.py:*) ARGS=${T#*:}; T=visoes_test.py; NAME=visoes_test-$ARGS;; esac
  t0=$(date +%s)
  env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B $T $ARGS > $E/${NAME%.py}-$ROT.log 2>&1
  rc=$?
  echo "$NAME $ROT exit=$rc secs=$(( $(date +%s)-t0 )) | $(grep -v agent-proxy $E/${NAME%.py}-$ROT.log | grep -v '^\s*$' | tail -1 | cut -c1-200)" >> $E/resumo-$ROT.txt
done
echo FIM >> $E/resumo-$ROT.txt
