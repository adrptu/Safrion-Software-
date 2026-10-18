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

sol_code=Path('cal01.js').read_text()+'''\nconst parcial={liq:0,cal:{parcial:true}};
const m={X:parcial,Y:{liq:3},Z:{liq:8,cal:{parcial:true}}};
console.log(JSON.stringify({sem:demSolSit(parcial,0,false,false),enviada:demSolSit(parcial,100,true,false),emitida:demSolSit(parcial,100,true,true),complemento:demSolSit(m.Z,5,true,false),acima:demSolAcima(m,[{nome:'X',nec:100},{nome:'Y',nec:5}]),revisao:demSolRevisar({X:100,Y:5,Z:5},m,false),resolvida:demSolRevisar({X:100},{X:{liq:3,cal:{parcial:false}}},false)}));'''
s=json.loads(subprocess.check_output([node,'-e',sol_code],text=True))
assert s['sem']['t']=='Data pendente' and not s['sem']['pend']
for k in ['enviada','emitida']:
    assert s[k]['t']=='Data pendente' and s[k]['sol'] and not s[k]['pend'],s[k]
assert s['complemento']['t']=='Complemento' and s['complemento']['dif']==3
assert 'X' not in s['acima'] and s['acima']['Y']['dif']==2
assert s['revisao']=={'it':{'X':100,'Y':3,'Z':8},'novos':['Z'],'menos':['Y']},s
assert s['resolvida']['it']=={'X':3} and s['resolvida']['menos']==['X']
print('OK: data pendente preserva solicitação; falta datada e redução após resolução preservadas')
