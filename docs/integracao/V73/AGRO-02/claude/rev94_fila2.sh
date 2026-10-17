#!/bin/bash
# fila 2: sonda final (candidata e base) e testes obsoletos com o patch proposto (aplicado só durante a execução, revertido no fim)
L=/tmp/claude-0/rev94_tools; C=/tmp/claude-0/rev94/tools/prototipo/v37/gen37; B=/tmp/claude-0/rev94base/tools/prototipo/v37/gen37
S=/tmp/claude-0/rev94/docs/integracao/V73/AGRO-02/claude/rev94_sonda.py; PT=/tmp/claude-0/rev94/docs/integracao/V73/AGRO-02/claude/rev94_testes_obsoletos.patch
roda(){ nome=$1; dir=$2; shift 2; $L/rev94_gate.sh >/dev/null; t0=$(date +%s); ( cd "$dir" && env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B "$@" ) > $L/$nome.log 2>&1; rc=$?; echo "$(date +%H:%M:%S) rc=$rc $(( $(date +%s)-t0 ))s $nome :: $(grep -E 'RESULTADO|ok · ' $L/$nome.log | tail -1)" >> $L/fila2_resumo.txt; }
: > $L/fila2_resumo.txt
rm -rf $L/sonda_cand $L/sonda_base
roda cand_sonda $C $S $C $L/sonda_cand
roda base_sonda $B $S $B $L/sonda_base
cd /tmp/claude-0/rev94 && git apply $PT && echo "patch aplicado: $(git diff --stat | tail -1)" >> $L/fila2_resumo.txt
roda cand_patch_mip_fluxo $C mip_fluxo_test.py
roda cand_patch_mip_correcoes $C mip_correcoes_test.py
cd /tmp/claude-0/rev94 && git apply -R $PT && echo "patch revertido: $(git status --porcelain --untracked-files=no | wc -l) arquivos versionados alterados" >> $L/fila2_resumo.txt
# contraprova do patch: os testes ajustados continuam verdes na base (a dose digitada é a mesma que a base preenchia)
cd /tmp/claude-0/rev94base && git apply $PT
roda base_patch_mip_fluxo $B mip_fluxo_test.py
roda base_patch_mip_correcoes_b $B mip_correcoes_test.py b
cd /tmp/claude-0/rev94base && git apply -R $PT
echo FIM >> $L/fila2_resumo.txt
