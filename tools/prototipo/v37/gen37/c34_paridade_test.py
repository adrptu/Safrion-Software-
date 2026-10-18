"""Compara as funções reais JS/Python, sem importar o build inteiro ou executar navegador."""
import ast,copy,json,pathlib,subprocess,shutil,sys
P=pathlib.Path(__file__).parent
T=ast.parse((P/'dados2.py').read_text())
# Partes canônicas da semente necessárias à previsão; sem duplicar seus números.
ns={'iso_br':lambda d:'-'.join(reversed(d.split('/')))}
for name in ['FORNECEDORES','PEDIDOS','RECEB_DT']:
 node=next(n for n in T.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
 exec(compile(ast.Module(body=[node],type_ignores=[]),'dados2.py','exec'),ns)
assert all(r.get('un') for r in ns['RECEB_DT'])
f=next(n for n in T.body if isinstance(n,ast.FunctionDef) and n.name=='est_dem')
exec(compile(ast.Module(body=[f],type_ignores=[]),'dados2.py','exec'),ns)
ns['os_faz']=lambda c:{}
node=shutil.which('node') or '/Users/adrianussanders/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
def check(c,b,faz):
 ns['est_base']=lambda:b
 py=ns['est_dem'](c,faz,[])
 code="const fs=require('fs'),vm=require('vm');let x=JSON.parse(fs.readFileSync(0,'utf8'));x.cenLoteVencido=()=>false;vm.createContext(x);vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),x);console.log(JSON.stringify(vm.runInContext('cenEstDem(c,faz,b,[])',x)));"
 js=json.loads(subprocess.check_output([node,'-e',code,str(P/'cenario.js')],input=json.dumps(dict(c=c,b=b,faz=faz,CEN0={'diaOperacional':'2026-10-17'})).encode()))
 assert py==js,(py,js)
 return py
empty=dict(lotes={},reqs={},ordens={},movs=[])
b=dict(rec=ns['RECEB_DT'],locFaz={},faz0='Santa Rita',hoje='2026-10-17')
for faz in ['Santa Rita','Lagoa Grande']:check(empty,b,faz)
# Mesmos pedidos canônicos, conferência parcial nova e repetida.
r=ns['RECEB_DT'][0];c=copy.deepcopy(empty)
e=dict(id='PARCIAL',ped=r['ref'],item=r['item'],un=r['un'],apto=15,quar=5,conf=999)
c['movs']=[dict(tipo='recebimento-nf',estRec=e)]*2
out=check(c,b,r['faz']);assert next(x for x in out['recebDt'] if x.get('ref')==r['ref'])['q']==r['q']-20
# Contraprova multi-item e unidade ambígua sem metadado legado.
b2=dict(b,rec=[dict(ref='PC-X',item='A',un='kg',q=100,faz='F'),dict(ref='PC-X',item='B',un='L',q=50,faz='F')]);c['movs']=[dict(tipo='recebimento-nf',estRec=dict(e,ped='PC-X',item='A',un='kg'))]*2
out=check(c,b2,'F');assert [r['q'] for r in out['recebDt']]==[80,50]
del b2['rec'][0]['un'];c['movs'].append(dict(tipo='recebimento-nf',estRec=dict(e,id='OUTRO',ped='PC-X',item='A',un='L')))
out=check(c,b2,'F');assert len(out['recebNaoApuravel'])==1 and len(out['recebDt'])==1
print('PASS 5 paridades JS/Python: previsões canônicas da semente (2 fazendas), parcial deduplicado, multi-item, legado ambíguo excluído com aviso. Não é execução integral do build.')
c['movs']=c['movs'][:2]
c['lotes']={'A|kg':dict(prod='A',lote='kg',local='Sede',un='kg',fisico=20,quarentena=0),'A|L':dict(prod='A',lote='L',local='Sede',un='L',fisico=5,quarentena=0)}
b2['locFaz']={'Sede':'F'}
out=check(c,b2,'F');assert len(out['recebNaoApuravel'])==1 and not any(r['item']=='A' for r in out['recebDt'])
print('PASS 6ª paridade: dois lotes em unidades distintas e recebimento parcial, previsão ambígua excluída.')
