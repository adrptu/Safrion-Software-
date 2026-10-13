#!/bin/bash
/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/bin/nav.sh /home/user/sp-verde/tools/prototipo/v37/gen37 /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/fix10 /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera/fix10/lista.txt
REF=$(ls -d $HOME/.cache/safrion-gen37-ref/*-sintetico/tools/prototipo/v37/gen37/_render | head -1)
cd /tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/acelera
for i in 1 2 3; do ANTES_DIR=$REF python3 bin/mutar.py e15_abas_controle_$i _render/OS.dc.html ".etp-sr{position:absolute!important;" ".etp-sr{position:absolute!important;" -- etapas_celular_test.py desktop 100 115; done
ANTES_DIR=$REF python3 bin/mutar.py e15_abas_muda _render/CMP.dc.html ".etp-sr{position:absolute!important;" "main{padding-top:30px!important}.etp-sr{position:absolute!important;" -- etapas_celular_test.py desktop 30 45
ANTES_DIR=$REF python3 bin/mutar.py e15_abas_muda_recolhido _render/OS.dc.html ".etp-sr{position:absolute!important;" ".menu-lat.rec{width:80px!important}.etp-sr{position:absolute!important;" -- etapas_celular_test.py desktop 95 110
echo FIM
