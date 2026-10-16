#!/bin/bash
# Reconferência R3 do PR #81 (HEAD 2daee8e): só o ben_fluxo modo fluxo (único arquivo de teste mudado); render reaproveitado de 50af2ae (produto igual).
R3=/tmp/claude-0/pr81/docs/integracao/V71/est-onda0-rev-claude/r3; C=/tmp/claude-0/pr81b/tools/prototipo/v37/gen37; S=$R3/_resumo.txt
until [ "$(pgrep -f 'cloudchrome/chrome.*remote-debugging' | wc -l)" -le 1 ]; do sleep 15; done
echo "início $(date -u +%H:%M:%S) · Chrome em execução antes: $(pgrep -f 'cloudchrome/chrome.*remote-debugging' | wc -l)" >> $S
ini=$(date +%s); ( cd $C && timeout 900 env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico GEN=$C python3 -B ben_fluxo_test.py fluxo ) > $R3/cand_ben_fluxo.log 2>&1; rc=$?
echo "cand_ben_fluxo (2daee8e) | rc=$rc | $(( $(date +%s)-ini ))s | $(grep -a RESULTADO $R3/cand_ben_fluxo.log | tail -n 1) | $(grep -a '^MEDIDA' $R3/cand_ben_fluxo.log)" >> $S
echo FIM >> $S
