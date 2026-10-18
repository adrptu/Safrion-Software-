"""EX57: ausência de âncora preserva planejamento sem inventar cronologia."""
import json, os, subprocess
from pathlib import Path
import dados2 as D
node=os.environ.get('NODE_BINARY','node')
ev=[dict(dt='',q=100,tipo='dem',own=True,chave='pend'),dict(dt='2026-11-01',q=3,tipo='dem',own=True,chave='datada')]
code=Path('cal01.js').read_text()+'''\nconst ev=JSON.parse(process.argv[1]);const r=cal01(5,ev,0,{hoje:'2026-10-01',viavel:'2026-10-08'}); console.log(JSON.stringify({r,memo:cal01Memo(r,{un:'kg'}),sit:demSituacao({x:{nome:'Teste',un:'kg',est:5,evs:ev}},null,'2026-10-01','2026-10-08')}));'''
x=json.loads(subprocess.check_output([node,'-e',code,json.dumps(ev)],text=True))
r=x['r'];p=D.cal01(5,ev,hoje='2026-10-01',viavel='2026-10-08')
for k,v in p.items(): assert r[k]==v,(k,r[k],v)
assert r['bruta']==103 and r['semData']==100 and r['parcial']
assert r['liq']==0 and r['saldo']==2 and r['falta'] is None
assert all(e['dt'] for e in r['linhas'])
assert any('Sem data: aguarda âncora' in s and '100' in s for s in x['memo'])
assert any('projeção parcial' in s for s in x['memo'])
assert x['sit']['Teste'][0]=='Data pendente'
assert '100 kg' in x['sit']['Teste'][2]
for dt in [None,'']:
    ev[0]['dt']=dt
    p=D.cal01(5,ev)
    assert p['bruta']==103 and p['liq']==0 and p['saldo']==2
print('OK: quantidade preservada; sem evento fictício; paridade; memória parcial; situação sem falsa cobertura; null/vazio')
