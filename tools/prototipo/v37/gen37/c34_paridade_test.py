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
# Q5 (revisão do Codex 6249640248; patch do integrador, Claude): nota antiga sem unidade ou linha só baixa a linha única do PC e item em que cabe.
leg=dict(id='ANTIGA',nf='7001',ped='PC-X',item='A',apto=20,quar=0)
c3=copy.deepcopy(empty);c3['movs']=[dict(tipo='recebimento-nf',estRec=leg)]
um=[dict(ref='PC-X',item='A',un='kg',q=100,faz='F')]
dois=[dict(ref='PC-X',item='A',un='kg',linha=1,q=100,faz='F'),dict(ref='PC-X',item='A',un='L',linha=2,q=50,faz='F')]
mesmo=[dict(ref='PC-X',item='A',un='kg',linha=1,q=100,faz='F'),dict(ref='PC-X',item='A',un='kg',linha=2,q=50,faz='F')]
out=check(c3,dict(b,rec=um),'F');assert [x['q'] for x in out['recebDt']]==[80] and not out['recebNaoApuravel'],out      # legado único continua abatendo
c4=copy.deepcopy(c3);c4['movs'][0]['estRec']['un']='L'
out=check(c4,dict(b,rec=um),'F');assert [x['q'] for x in out['recebDt']]==[100],out                                   # unidade divergente não abate
out=check(c3,dict(b,rec=dois),'F')                                                                                      # contraexemplo do Codex: 100 kg e 50 L
assert not out['recebDt'] and len(out['recebNaoApuravel'])==2 and all('7001' in x['motivo'] for x in out['recebNaoApuravel']),out
c5=copy.deepcopy(c3);c5['movs'][0]['estRec']['un']='kg'
out=check(c5,dict(b,rec=mesmo),'F');assert not out['recebDt'] and len(out['recebNaoApuravel'])==2,out                  # mesma unidade, sem linha: ambígua
out=check(c5,dict(b,rec=dois),'F');assert [x['q'] for x in out['recebDt']]==[80,50] and not out['recebNaoApuravel'],out # unidade única entre as linhas: baixa só a sua
c6=copy.deepcopy(c5);c6['movs'][0]['estRec']['linha']=2
out=check(c6,dict(b,rec=mesmo),'F');assert [x['q'] for x in out['recebDt']]==[100,30],out                              # com linha: baixa só a sua
print('PASS 6 paridades Q5: legado único abate, unidade divergente não, legado ambíguo (unidades distintas ou mesma unidade sem linha) fora do suprimento com aviso, unidade ou linha única baixa só a sua.')
# Fronteira do Q5 (revisão do Codex 6250436415; patch do integrador, Claude): cada outra previsão do mesmo PC e item é outra ocorrência,
# mesmo sem linha ou com a mesma chave. A nota que cabe em duas não baixa nenhuma; não se inventa linha nem se deduplica quantidade.
semlinha=[dict(ref='PC-X',item='A',un='kg',q=100,faz='F'),dict(ref='PC-X',item='A',un='kg',q=50,faz='F')]
out=check(c3,dict(b,rec=semlinha),'F')                                                                                  # contraexemplo do Codex: 100 e 50 kg, ambas sem linha
assert not out['recebDt'] and len(out['recebNaoApuravel'])==2 and all('7001' in x['motivo'] for x in out['recebNaoApuravel']),out
parcelas=[dict(ref='PC-X',item='A',un='kg',linha=1,q=100,faz='F'),dict(ref='PC-X',item='A',un='kg',linha=1,q=50,faz='F')]
out=check(c6,dict(b,rec=parcelas),'F');assert [x['q'] for x in out['recebDt']]==[100,50] and not out['recebNaoApuravel'],out   # nota da linha 2 não cabe em nenhuma
c7=copy.deepcopy(c6);c7['movs'][0]['estRec']['linha']=1
out=check(c7,dict(b,rec=parcelas),'F');assert not out['recebDt'] and len(out['recebNaoApuravel'])==2,out                # duas parcelas da mesma linha: não baixa 20 duas vezes
out=check(c3,dict(b,rec=semlinha[:1]),'F');assert [x['q'] for x in out['recebDt']]==[80],out                            # uma só previsão sem linha continua abatendo
print('PASS 4 paridades da fronteira Q5: duas previsões sem linha, duas parcelas da mesma linha (com e sem nota delas) e previsão única sem linha.')
