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

// Comparação com simulatePest original: mesmo ruído constante, rotação e repetição.
const simStart=html.indexOf('function simulatePest('),simEnd=html.indexOf('// ---- água e adubação ----',simStart);
assert(simStart>=0&&simEnd>simStart);
for(const repete of [false,true]) {
 const days=70,prods=[{c:'Óleo mineral',g:'O',base:.5,res:2},{c:'A',g:'A',base:.6,res:4},{c:'B',g:'B',base:.7,res:5}];
 const weather=Array.from({length:days+1},(_,d)=>({quenteSeco:d%5===0}));
 const rain=Array.from({length:days+1},(_,d)=>d%13===0?12:0);
 const prof={press:1,oleo1:true,repete,eq:'E',off:0,falha:[],gatilho:2,delay:2};
 const target={id:'A',fx:{def:0,n:.03,k:0,lav:.8},x0:[2,2],wk:[1.03,1.03],clima:()=>1,cap:1000,imm:.01,nc:1,prods};
 const sim={Math,rngFor:()=>()=>.5,PROF:{T:prof},HOT:{A:[]},WATER:{T:{suff:.95}},NUT:{T:{n14:Array(days+1).fill(10),k14:Array(days+1).fill(20)}},EQ:{E:{cov:.8}},CLIMA:weather,RAINMM:rain,APP_FX:{qs:.8,chuva:.7},DAYS:days,avOf:()=>0};
 vm.createContext(sim);vm.runInContext(html.slice(simStart,simEnd),sim);sim.p={id:'T',stage:'adulta'};sim.a=target;
 const original=vm.runInContext('simulatePest(p,a)',sim);
 const ep={x0:2,cap:1000,nc:1,fx:target.fx,observacoes:original.obs.map(o=>o.day),dias:weather.map((w,d)=>({wk:1.03,clima:1,falta:0,n14:10,k14:20,imigracao:.01,chuva:rain[d],quenteSeco:w.quenteSeco,ruido_obs:1,ruido_app:.5})),politica:{produtos:prods,oleo1:true,repete,id_tamanho:1,cobertura:.8,app_qs:.8,app_chuva:.7,gatilho:2,delay:2}};
 const pySim=`import sys,json;sys.path.insert(0,sys.argv[1]);import raiox_gabarito as g\ne=json.load(sys.stdin)\na=g.agenda_observada(e['x0'],e['dias'],e['cap'],e['fx'],e['observacoes'],e['nc'],e['politica'])\nr=g.replay(e['x0'],e['dias'],a,e['cap'],e['fx'])\nprint(json.dumps(dict(apps=a,obs=[dict(day=d,v=r[d]['v']) for d in e['observacoes']])))`;
 const result=cp.spawnSync('python3',['-B','-c',pySim,__dirname],{input:JSON.stringify(ep),encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);const actual=JSON.parse(result.stdout);
 assert(actual.apps.length>=3,'fixture sem aplicações suficientes');
 assert.deepEqual(actual.apps.map(a=>[a.day,a.produto,a.rep,a.consec]),Array.from(original.apps,a=>[a.day,a.prod.c,a.rep,a.consec]));
 actual.obs.forEach((o,i)=>assert(Math.abs(o.v-original.obs[i].v)<1e-10,`observação ${i}: ${o.v} vs ${original.obs[i].v}`));
 console.log(`PASS simulatePest real: repete=${repete}, ${actual.apps.length} aplicações, ${actual.obs.length} observações.`);
}

// Alvos reais; exógenos sintéticos por safra/semente, sem dados de clientes.
const alvoStart=html.indexOf('const ALVOS = ['),alvoEnd=html.indexOf('// efeitos plantados na eficácia',alvoStart);
const ac={};vm.createContext(ac);vm.runInContext(html.slice(alvoStart,alvoEnd)+';globalThis.alvos=ALVOS',ac);
const episodes=[];
for(const a of ac.alvos) for(const season of [1,2]) for(let seed=0;seed<20;seed++) {
 let state=1000*season+seed+1; const rand=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
 const dias=Array.from({length:43},(_,d)=>{
  const c={quenteSeco:(d+season*3)%14<5,molhado:(d+season*3)%14>=9,ur:55+25*Math.sin((d+season*7)/9)};
  return {wk:a.wk[0]+(a.wk[1]-a.wk[0])*d/42,clima:a.clima(c),clima_sem:{qs:a.clima({...c,quenteSeco:false}),molh:a.clima({...c,molhado:false}),ur:a.clima({...c,ur:65})},falta:.2,n14:10,k14:15,imigracao:a.imm,chuva:c.molhado?12:0,quenteSeco:c.quenteSeco,ruido_obs:.88+rand()*.24,ruido_app:rand()};
 });
 for(const fator of ['qs','molh','ur']) episodes.push({cenario:'alvos-v3-clima',safra:String(season),semente:seed,talhao:'T',alvo:a.id,fator,dias,observacoes:[1,8,15,22,29,36,42],x0:(a.x0[0]+a.x0[1])/2,cap:a.cap,nc:a.nc,fx:a.fx,politica:{produtos:a.prods,oleo1:true,repete:false,id_tamanho:1,cobertura:.8,app_qs:.78,app_chuva:.7,gatilho:.9,delay:2}});
}
const realPy=`import sys,json;sys.path.insert(0,sys.argv[1]);import raiox_gabarito as g\ne=json.load(sys.stdin);p=g.gerar(e)\nassert len(e)==480\nfor c in p['oraculo']['classes_por_safra'].values():\n assert c['total']==72 and sum(c['contagens'].values())==72\n assert abs(sum(c['fracoes'].values())-1)<1e-12\n# Cochonilha não tem efeito de molhamento/UR no crescimento do v3.\nneg=[q for q in p['oraculo']['pares'] if q['ligado']['alvo']=='cochon' and q['intervencao'] in ('molh','ur') and 'resultado' in q]\nassert neg and all(q['resultado']['delta']==0 for q in neg)\nassert g.digest(p)==g.digest(g.gerar(e))\nprint(json.dumps(dict(episodios=len(e),pares=len(p['oraculo']['pares']),negativos_zero=len(neg),hash=g.digest(p),exclusoes=p['oraculo']['exclusoes_por_safra'],classes=p['oraculo']['classes_por_safra'])))`;
const rp=cp.spawnSync('python3',['-B','-c',realPy,__dirname],{input:JSON.stringify(episodes),encoding:'utf8',maxBuffer:8*1024*1024});assert.equal(rp.status,0,rp.stderr);console.log('PASS alvos v3/clima: '+rp.stdout.trim());

const invalidPy=`import sys;sys.path.insert(0,sys.argv[1]);import raiox_gabarito as g
r=lambda start:[dict(delta=.3,semente=i,identificavel=True) for i in range(start,start+20)]
for bad in [float('nan'),float('inf'),float('-inf'),True]:
 q=r(0);q[0]['delta']=bad
 try:g.classe(q);raise AssertionError('Delta inválido aceito')
 except ValueError:pass
for field,value in [('semente',True),('semente',-1),('identificavel',1)]:
 q=r(0);q[0][field]=value
 try:g.classe(q);raise AssertionError('Réplica inválida aceita')
 except ValueError:pass
p={'s1':{'ligado':r(0),'desligado':r(20)},'s2':{'ligado':r(0),'desligado':r(0)}}
assert g.consolidar(p)['classe']=='ambiguo'
assert not g.consolidar(p)['safras']['s1']['sementes_pareadas']
try:g.gerar([{'qualquer':float('nan')}]);raise AssertionError('NaN aceito')
except ValueError:pass
print('PASS: 7 réplicas inválidas recusadas; sementes distintas não confirmam classe; NaN recusado antes do replay.')`;
const ip=cp.spawnSync('python3',['-B','-c',invalidPy,__dirname],{encoding:'utf8'});assert.equal(ip.status,0,ip.stderr);console.log(ip.stdout.trim());

// Exportação opcional: node raiox_unit.js fonte-v3.html --export-dir pasta-nova
const exportIndex=process.argv.indexOf('--export-dir');
if(exportIndex>=0) {
 const path=require('path'),crypto=require('crypto');
 const dir=process.argv[exportIndex+1];assert(dir,'Informe pasta nova para exportação');
 fs.mkdirSync(dir); // Recusa sobrescrever pacote anterior, mesmo parcialmente.
 const write=(name,body)=>fs.writeFileSync(path.join(dir,name),body,{flag:'wx'});
 const hash=body=>crypto.createHash('sha256').update(body).digest('hex');
 const origem=JSON.stringify(episodes);write('episodios.json',origem);
 const cli=cp.spawnSync('python3',['-B',path.join(__dirname,'raiox_gabarito.py'),path.join(dir,'episodios.json')],{encoding:'utf8',maxBuffer:32*1024*1024});
 assert.equal(cli.status,0,cli.stderr);
 const pacote=JSON.parse(cli.stdout), entrada=JSON.stringify(pacote.entrada),oraculo=JSON.stringify(pacote.oraculo);
 write('entrada.json',entrada);write('oraculo.json',oraculo);
 const manifest={estado:'rascunho_para_revisao',recuperacao_motor:'nao_executada',fonte_html_sha256:hash(html),contrato_hash:pacote.oraculo.contrato_hash,arquivos:{'episodios.json':hash(origem),'entrada.json':hash(entrada),'oraculo.json':hash(oraculo)},fontes:{'raiox_gabarito.py':hash(fs.readFileSync(path.join(__dirname,'raiox_gabarito.py'))),'raiox_unit.js':hash(fs.readFileSync(__filename))},reproduzir:'python3 -B raiox_gabarito.py episodios.json; comparar JSON canônico e entrada_hash',limites:['Dados sintéticos; não são recomendações agronômicas.','Limiar e referências climáticas aguardam revisão.','Intervenção climática restrita ao crescimento; eficácia preservada.','Sem avaliação de recuperação pelo motor.']};
 write('manifesto.json',JSON.stringify(manifest,null,2));
 const roundtrip=cp.spawnSync('python3',['-B','-c',`import sys,json;sys.path.insert(0,sys.argv[1]);import raiox_gabarito as g\nfrom pathlib import Path\np=Path(sys.argv[2]);e=json.loads((p/'entrada.json').read_text());o=json.loads((p/'oraculo.json').read_text());assert g.digest(e)==o['entrada_hash'];print('PASS: entrada exportada vinculada ao oráculo')`,__dirname,dir],{encoding:'utf8'});
 assert.equal(roundtrip.status,0,roundtrip.stderr);console.log(roundtrip.stdout.trim());
 console.log('Pacote exportado: '+path.resolve(dir));
}
