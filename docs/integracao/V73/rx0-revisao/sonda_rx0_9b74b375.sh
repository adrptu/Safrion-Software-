#!/bin/bash
# Sonda do Claude sobre o C2.2 do Codex (9b74b375): reexecuta as 640 populações no motor v3.1 e cruza a origem de cada estado.
# Uso: sonda_rx0_9b74b375.sh <pasta vazia>   (no repositório com 9b74b375 e 529adf7c; dados sintéticos)
set -e; D=$1; R=$(cd "$(dirname "$0")" && pwd); mkdir -p $D/src $D/out
git show 9b74b375:tools/prototipo/v37/gen37/raiox_unit.js > $D/src/raiox_unit.js
git show 9b74b375:tools/prototipo/v37/gen37/raiox_gabarito.py > $D/src/raiox_gabarito.py
git show 529adf7c:docs/integracao/V73/pedidos-1610/raiox-pragas-no-tempo-v3.html > $D/fonte-v3.html
python3 -I $R/motor_v31.py $D/fonte-v3.html $D/fonte-v31.html
cd $D; node src/raiox_unit.js fonte-v3.html --export-dir out/pacote > out/unit_export.log
python3 -B src/raiox_gabarito.py out/pacote/episodios.json --entrada-motor > out/entradas.jsonl 2> out/prereg.log
node src/raiox_unit.js fonte-v31.html --motor-input out/entradas.jsonl > out/m_all.json
python3 -I - <<'PY'
import json, collections
r = json.load(open('out/m_all.json'))
print('combinado', len(r['combinados']), dict(collections.Counter(x['level'] for x in r['combinados'])))
A = collections.Counter(); J = collections.defaultdict(list)
for p in r['resultados']:
    k = (p['safra'], p['alvo'], 'modelo vazio' if not p['reps'] else 'com representante'); A[k] += 1; J[k].append(p['janelas'])
print('populações por safra e alvo:'); [print(' ', k, v, 'janelas', min(J[k]), '–', max(J[k])) for k, v in sorted(A.items())]
idx = {(p['safra'], p['semente'], p['alvo']): p for p in r['resultados']}
def rep(p, f):
    for q in p['reps']:
        if q['fator'] == f: return f
        if f in q['mates']: return q['fator']
ns = [x for x in r['combinados'] if x['level'] == 'nao_selecionado']
print('não selecionado com modelo vazio em pelo menos uma safra:', sum(any(not idx[(s, x['semente'], x['alvo'])]['reps'] for s in x['safras']) for x in ns), 'de', len(ns))
C = collections.Counter()
for x in r['combinados']:
    if x['level'] in ('fraca', 'moderada'):
        C[(x['fator'], x['level'], 'próprio nas duas' if x['origens'] == ['representante', 'representante'] else 'herdado do grupo')] += 1
print('evidência (campo do harness):', dict(collections.Counter((x['level'], x.get('evidencia')) for x in r['combinados'] if x['level'] in ('fraca','moderada'))))
print('placebo por nível:', dict(collections.Counter((x['level'], x.get('evidencia')) for x in r['combinados'] if x['fator']=='placebo')))
print('fraca/moderada por origem:'); [print(' ', k, v) for k, v in sorted(C.items())]
H = collections.Counter((x['fator'], tuple(rep(idx[(s, x['semente'], x['alvo'])], x['fator']) for s in x['safras'])) for x in r['combinados'] if x['level'] == 'moderada' and 'mate' in x['origens'])
print('moderada herdada (fator, representante por safra):', dict(H))
PY
