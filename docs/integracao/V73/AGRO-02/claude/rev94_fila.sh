#!/bin/bash
# fila sequencial dos testes de navegador da revisão do PR #94; cada item passa pelo portão (≤ 1 Chrome principal)
L=/tmp/claude-0/rev94_tools; C=/tmp/claude-0/rev94/tools/prototipo/v37/gen37; B=/tmp/claude-0/rev94base/tools/prototipo/v37/gen37
S=/tmp/claude-0/rev94/docs/integracao/V73/AGRO-02/claude/rev94_sonda.py
roda(){ nome=$1; dir=$2; shift 2; $L/rev94_gate.sh >/dev/null; t0=$(date +%s); ( cd "$dir" && env CHROME_BIN=/tmp/cloudchrome/chrome CDP_GL=1 SAFRION_DADOS=sintetico timeout 900 python3 -B "$@" ) > $L/$nome.log 2>&1; rc=$?; echo "$(date +%H:%M:%S) rc=$rc $(( $(date +%s)-t0 ))s $nome :: $(grep -E 'RESULTADO|ok · ' $L/$nome.log | tail -1)" >> $L/fila_resumo.txt; }
: > $L/fila_resumo.txt
roda base_sonda $B $S $B $L/sonda_base
roda cand_mip_correcoes $C mip_correcoes_test.py
roda base_mip_correcoes_b $B mip_correcoes_test.py b
roda cand_agtest $C agtest.py
roda cand_agrofit $C agrofit_test.py
roda cand_agrofit_faixa $C agrofit_faixa_test.py
roda cand_paginas_scan $C paginas_scan_test.py
echo FIM >> $L/fila_resumo.txt
