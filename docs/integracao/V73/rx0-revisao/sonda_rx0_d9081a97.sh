#!/bin/bash
# Sonda do Claude sobre o RX-0 A4 (d9081a97): reproduz os 4 placebos fortes com o motor original e testa duas variantes só de diagnóstico.
# Uso: sonda_rx0_d9081a97.sh <pasta vazia>   (precisa do repositório com d9081a97 e 529adf7c; dados sintéticos)
set -e; D=$1; mkdir -p $D/src $D/out
git show d9081a97:tools/prototipo/v37/gen37/raiox_gabarito.py > $D/src/raiox_gabarito.py
git show d9081a97:tools/prototipo/v37/gen37/raiox_unit.js > $D/src/raiox_unit.js
git show 529adf7c:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > $D/fonte-v3.html
cd $D; node src/raiox_unit.js fonte-v3.html --export-dir out/pacote > out/unit_export.log
python3 -B src/raiox_gabarito.py out/pacote/episodios.json --entrada-motor > out/entradas.jsonl 2> out/prereg.log
python3 -I -c "import json,sys
o=[l for l in open('out/entradas.jsonl') if (lambda h:h['safra']=='1' and ((h['alvo']=='acaro' and h['semente']==53) or (h['alvo']=='mosca' and h['semente'] in (14,40,76))))(json.loads(l)[0])]
open('out/sel4.jsonl','w').writelines(o)"
# variante A: o adaptador tipa o placebo como Clima (estrutura: a covariável é comum aos 16 talhões)
sed "s/tipo:k==='placebo'?'Controle':'Clima'/tipo:'Clima'/" src/raiox_unit.js > src/raiox_unit_clima.js
# variante B: Clima só é forte com >= 5 semanas no grupo alto E no baixo
python3 -I -c "s=open('fonte-v3.html').read();s=s.replace(\"q.wkHi = new Set(hi.map(r => r.wk)).size; });\",\"q.wkHi = new Set(hi.map(r => r.wk)).size; q.wkLo = new Set(R.rows.filter((r, i) => !I[i]).map(r => r.wk)).size; });\").replace(\"(q.f.tipo !== 'Clima' || q.wkHi >= 3)\",\"(q.f.tipo !== 'Clima' || (q.wkHi >= 5 && q.wkLo >= 5))\");open('fonte-wk5.html','w').write(s)"
node src/raiox_unit.js fonte-v3.html --motor-input out/sel4.jsonl > out/motor_original.json
node src/raiox_unit_clima.js fonte-v3.html --motor-input out/sel4.jsonl > out/motor_clima.json
node src/raiox_unit_clima.js fonte-wk5.html --motor-input out/sel4.jsonl > out/motor_clima_wk5.json
for n in original clima clima_wk5; do python3 -I -c "import json;r=json.load(open('out/motor_$n.json'));print('$n',[(x['alvo'],x['semente'],[(q['fator'],q['level'],'wkHi',q['wkHi'],'pivHi',q['pivHi'],q['mates']) for q in x['reps']]) for x in r['resultados']])"; done
