// RX-0: paridade da transformação com rxRows real; não mede recuperação.
const fs=require('fs'), vm=require('vm'), assert=require('assert'), cp=require('child_process');
const html=fs.readFileSync(process.argv[2], 'utf8');
const ini=html.indexOf('function rxRows('), fim=html.indexOf('// controles:',ini);
assert(ini>=0&&fim>ini,'fonte rxRows ausente');
const ctx={Math,PIVOS:[{id:'T',stage:'adulta'}],PEST:{A:{T:{obs:[],apps:[]}}}};
vm.createContext(ctx);vm.runInContext(html.slice(ini,fim),ctx);
const casos=[[10,20,10,1,8,8],[10,3,10,1,6,6],[10,0,10,1,11,11],[10,20,10,1,8,7],[.5,2,10,1,8,8],[10,20,10,1,12,12]];
const esperado=casos.map(([v1,v2,nc,d1,d2,D])=>{ctx.PEST.A.T.obs=[{day:d1,v:v1},{day:d2,v:v2}];ctx.a={id:'A',nc};ctx.D=D;return vm.runInContext('rxRows(a,D)',ctx).map(x=>x.r)[0]??null;});
const py=String.raw`
import json,sys
sys.path.insert(0,sys.argv[1])
import raiox_gabarito as g
out=[]
for row in json.load(sys.stdin):
 try: out.append(g.crescimento(*row))
 except ValueError: out.append(None)
print(json.dumps(out))
r=lambda d,clip=False:[dict(delta=d,identificavel=not clip,semente=i) for i in range(20)]
assert g.classe(r(0))['classe']=='fraco'
assert g.classe(r(.3))['classe']=='forte'
assert g.classe(r(.3,True))['classe']=='nao_identificavel'
assert g.consolidar({'s1':{'ligado':r(.3),'desligado':r(-.3)},'s2':{'ligado':r(.3),'desligado':r(.3)}})['classe']=='ambiguo'
assert g.consolidar({'s1':{'ligado':r(0),'desligado':r(0)},'s2':{'ligado':r(0),'desligado':r(0)}})['classe']=='fraco'
assert g.consolidar({'s1':{'ligado':r(.3),'desligado':r(.3)},'s2':{'ligado':r(-.3),'desligado':r(-.3)}})['classe']=='ambiguo'
try: g.classe(r(.3)+r(.3)); raise AssertionError('duplicadas aceitas')
except ValueError: pass
`;
const p=cp.spawnSync('python3',['-B','-c',py,__dirname],{input:JSON.stringify(casos),encoding:'utf8'});
assert.equal(p.status,0,p.stderr);const actual=JSON.parse(p.stdout);
actual.forEach((x,i)=>{if(x===null||esperado[i]===null)assert.equal(x,esperado[i]);else assert(Math.abs(x-esperado[i])<1e-12);});
const apps=[-9,-8,1,8,9];
const expectedApps=apps.map(day=>{ctx.PEST.A.T.obs=[{day:1,v:10},{day:8,v:20}];ctx.PEST.A.T.apps=[{day}];ctx.a={id:'A',nc:10};ctx.D=8;return vm.runInContext('rxRows(a,D)',ctx).length===1;});
const pa=cp.spawnSync('python3',['-B','-c',`import sys,json;sys.path.insert(0,sys.argv[1]);import raiox_gabarito as g
out=[]
for d in json.load(sys.stdin):
 try:g.crescimento(10,20,10,1,8,8,[d]);out.append(True)
 except ValueError:out.append(False)
print(json.dumps(out))`,__dirname],{input:JSON.stringify(apps),encoding:'utf8'});
assert.equal(pa.status,0,pa.stderr);assert.deepEqual(JSON.parse(pa.stdout),expectedApps);
console.log('PASS: 5 limites de aplicação e inversão de sinal entre safras; '+'PASS: 6 janelas em paridade com rxRows real; controles zero, forte, clipping, agendas opostas, duas safras e sementes duplicadas. Recuperação pelo motor ainda não executada.');

// Duas safras sintéticas: política simplificada declarada, não recuperação do motor.
const batch = "import sys,random,math,json,pathlib,copy\nsys.path.insert(0,sys.argv[1])\nimport raiox_gabarito as g\neps=[]\nfor season in (1,2):\n for seed in range(20):\n  rng=random.Random(1000*season+seed)\n  dias=[dict(wk=1.03,clima=1+.01*math.sin((d+season*4)/6),falta=.2,n14=10+math.sin((d+season*5)/7),k14=20,imigracao=.01,chuva=12 if (d+season)%13==0 else 0,ruido_obs=.88+rng.random()*.24,eff=.6+rng.random()*.1) for d in range(43)]\n  for scenario in ('zero','ausente','positivo'):\n   ds=copy.deepcopy(dias)\n   if scenario=='ausente':\n    for d in ds:d['n14']=6.4\n   eps.append(dict(cenario=scenario,safra=str(season),semente=seed,talhao='T',alvo='sintetico',fator='n',dias=ds,observacoes=[1,8,15,22,29,36,42],nc=1,x0=2,cap=1000,fx={'def':0,'n':0 if scenario=='zero' else .03,'k':0,'lav':1},politica={'delay':2,'gatilho':8,'resid':3}))\na=g.gerar(eps);b=g.gerar(eps)\nassert g.digest(a)==g.digest(b)\nassert len(a['entrada'])==240\nassert all(c['resultado']['classe']!='forte' for c in a['oraculo']['classes'] if c['chave'][0]!='positivo')\nassert any(c['resultado']['classe']=='forte' for c in a['oraculo']['classes'] if c['chave'][0]=='positivo')\nassert all(p['resultado']['delta']==0 for p in a['oraculo']['pares'] if p['cenario'] in ('zero','ausente') and 'resultado' in p)\nassert all('resultado' not in e and 'intervencao' not in e for e in a['entrada'])\nprint(json.dumps({'episodios':len(eps),'entradas':len(a['entrada']),'pares':len(a['oraculo']['pares']),'hash_repeticao':g.digest(a),'classes':[(x['chave'][0],x['chave'][-2:],x['resultado']['classe']) for x in a['oraculo']['classes']],'exclusoes':a['oraculo']['exclusoes_por_safra']},ensure_ascii=False))";
const bp=cp.spawnSync("python3",["-B","-c",batch,__dirname],{encoding:"utf8"});
assert.equal(bp.status,0,bp.stderr);console.log(bp.stdout.trim());
