#!/bin/sh
# Roda a verificação da especificação v2 e grava as saídas ao lado. Só lê gen37 (HEAD 884620c).
cd "$(dirname "$0")"
for f in 0 1 3; do python3 ocupacao_v2.py $f > saida_ocupacao_f$f.txt 2>&1; done
python3 trava_v2.py 1 > saida_trava_f1.txt 2>&1
python3 trava_v2.py 0 > saida_trava_f0.txt 2>&1
python3 estimativa_v2.py > saida_estimativa.txt 2>&1
python3 propriedades_v2.py 400 > saida_propriedades.txt 2>&1
git -C /home/user/sp-tab5/tools/prototipo/v37/gen37 log --oneline -1 > base.txt
wc -l saida_*.txt; cat saida_propriedades.txt base.txt
