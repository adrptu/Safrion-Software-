# -*- coding: utf-8 -*-
"""Motor (node) das mesmas entradas dos dois S2 da CTL-4, em qualquer versão. GEN = pasta gen37 da versão.
Baseado em ctl4rv/v1-estado/hlib2.py, t3/t4/t9/t10 (853a6a8). Somente leitura do repositório."""
import sys, os, json, subprocess, tempfile, inspect
G=os.environ['GEN']; sys.path.insert(0,G); os.chdir(G)
import dados2 as D2, cenario
import areas.processo_os as PO
CAL=open(os.path.join(G,'cal01.js'),encoding='utf-8').read()
CENJS=open(os.path.join(G,'cenario.js'),encoding='utf-8').read()
print('versão:',os.environ.get('VER'),'GEN=',G)
TEM={f:(('function '+f+'(') in (CENJS+CAL)) for f in ('cenOsDem','cenEstDem','cenDemEntradas','demFazenda','demSolSit','demSolRevisar','cenEntregar','cenDevolver','cenReceber','cenLiberarQuarentena')}
print('funções presentes (cenario.js + cal01.js):',json.dumps(TEM))
print('assinatura dados2.demanda:',str(inspect.signature(D2.demanda)))
def dem_seed(s,prods):
    m=D2.demanda(s); out={}
    for k,d in (m.items() if isinstance(m,dict) else []):
        nome=d.get('nome',k) if isinstance(d,dict) else k
        if any(p==nome or p==k for p in prods): out[nome]={kk:d.get(kk) for kk in ('liq','est','res','rec','bruta','plano','valor') if isinstance(d,dict) and kk in d}
    return out
PRODS=['NPK 20-05-20','MAP 11-52','Semente de soja 58 W','Fungicida A']
try: print('dados2.demanda("S2627") (build, sem cenário):',json.dumps(dem_seed('S2627',PRODS),ensure_ascii=False))
except Exception as e: print('dados2.demanda erro:',repr(e))
if not (TEM['demFazenda'] and TEM['cenOsDem']):
    print('MOTOR DA DEMANDA VIVA AUSENTE nesta versão: Planejar safra/Compra não recebem o cenário (cenGet) como entrada da demanda; a reprodução é só pela tela.')
    sys.exit(0)
PRE=cenario.js_prefixo(); PERF=cenario.perfis_js()
SRC=PO.JS_NUCLEO+PO.JS
def fn(name):
    i=SRC.index('function '+name+'(')
    j=SRC.index('{',i); d=0; k=j
    while True:
        ch=SRC[k]
        if ch=='{': d+=1
        elif ch=='}':
            d-=1
            if d==0: return SRC[i:k+1]
        k+=1
OSC='\n'.join(fn(n) for n in ('osc_o','osc_txt','osCargasVivas','osc_cancTxt','osc_cancCust','osc_cancelar','osc_conferencia','osc_encerrar','osApPend','cortaPrev','nd','nf'))+"\nconst LIM_DISP=0.20;\n"+fn('osc_dispensar')
SAFS=('S2627','S27SF','LG2627')
GX={s:D2.dem_entradas(s) for s in SAFS}
GB=D2.os_base(); GE=D2.est_base() if hasattr(D2,'est_base') else {}
HEAD=PERF+PRE+'\n'+CAL+'\n'+OSC+'\n'
EX="""function estRecX(c,d){ const n0=c.movs.length; if(d.apto>0) cenReceber(c,d.item,d.lote,d.apto,d.un,d.local,d.val,d.nf,true,PAULA);
 if(d.quar>0) cenReceber(c,d.item,d.lote,d.quar,d.un,d.local,d.val,d.nf,false,PAULA); c.movs[n0].estRec=d; }"""
def runjs(code):
    f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8'); f.write(code); f.close()
    try:
        p=subprocess.run(['node',f.name],capture_output=True,text=True,timeout=180)
        if p.returncode: raise RuntimeError(p.stderr[-1500:])
        return json.loads(p.stdout.strip().splitlines()[-1])
    finally: os.unlink(f.name)
PREAMB=f"""
const XS={json.dumps(GX,ensure_ascii=False)}, B={json.dumps(GB,ensure_ascii=False)}, EB={json.dumps(GE,ensure_ascii=False)};
const ENT=(c,x)=>typeof cenDemEntradas==='function'?cenDemEntradas(c,x,{{osb:B,est:EB}}):Object.assign({{}},x,{{osd:cenOsDem(c,B)}});
const DM=(c,s)=>{{ const m=demFazenda(ENT(c,XS[s||'S2627'])); const o={{}}; Object.values(m).forEach(d=>o[d.nome]=d); return o; }};
const snap=(c)=>{{ const R={{}}; Object.keys(XS).forEach(s=>{{ const m=demFazenda(ENT(c,XS[s]));
  R[s]={{tot:Math.round(Object.values(m).reduce((a,d)=>a+d.valor,0)*100)/100,liq:Object.fromEntries(Object.values(m).map(d=>[d.nome,d.liq]))}}; }}); return R; }};
let c=JSON.parse(JSON.stringify(CEN0)); const OUT=[]; const ERR=[];
const PAULA={{k:'Paula'}}, ANA={{k:'Ana'}}, RUI={{k:'Rui'}};
{EX}
"""
def viva(steps):
    js=HEAD+PREAMB
    for lab,code in steps:
        js+=f"try{{ (function(){{ {code} }})(); }}catch(e){{ ERR.push({json.dumps(lab)}+': '+e.message); }}\nOUT.push([{json.dumps(lab)},snap(c)]);\n"
    js+="console.log(JSON.stringify({OUT,ERR}));"
    return runjs(js)
def dif(a,b,tol=0.005):
    out={}
    for s in SAFS:
        la,lb=a[s]['liq'],b[s]['liq']
        d={n:(la.get(n),lb.get(n)) for n in set(la)|set(lb) if abs((la.get(n) or 0)-(lb.get(n) or 0))>tol}
        if d or abs(a[s]['tot']-b[s]['tot'])>tol: out[s]=dict(d=d,tot=(a[s]['tot'],b[s]['tot']))
    return out
def run(nome,steps):
    r=viva([('seed','')]+steps); print('==',nome)
    if r['ERR']: print('  ERROS:',r['ERR'])
    prev=r['OUT'][0][1]
    for lab,s in r['OUT'][1:]:
        d=dif(prev,s); print('  passo',lab,'→',json.dumps(d,ensure_ascii=False) if d else 'sem mudança na demanda'); prev=s
CANC=lambda o: f"osc_cancelar(c,'{o}','teste revisão',['','',''],ANA);"
AP=lambda ha,cons,d='26/09',ch='W-T1': f"cenApontar(c,{{os:'OS-0421',d:'{d}',ha:{ha},cons:{{'Fungicida A':{cons},'Adjuvante espalhante':0}},est:[],origem:'web',chave:'{ch}'}});"
NF=lambda q,qa,qq: f"estRecX(c,{{id:'r4533',nf:'NF 4533',ped:'PC-090 · Semente de soja 58 W · Coop. Vale',item:'Semente de soja 58 W',un:'kg',lote:'S58-0926',local:'Câmara fria',val:'06/2027',conf:{q},apto:{qa},quar:{qq}}});"
print('######## S2-1 custódia fora do pendente')
run('D1 devolver 500 kg MAP 11-52 da REQ-031 (OS-0417 em conferência)',[('dev500',"cenDevolver(c,'REQ-031','MAP 11-52',500,true,PAULA);")])
run('C4 entregar 8.000 kg NPK (REQ-040/OS-0425), cancelar a OS-0425, devolver 8.000',[('ent8000',"cenEntregar(c,'REQ-040','NPK 20-05-20',8000,'Carlos',PAULA);"),('cancel',CANC('OS-0425')),('dev8000',"cenDevolver(c,'REQ-040','NPK 20-05-20',8000,true,PAULA);")])
run('A11 OS-0421 aponta 150 ha usando 20 L, devolve 40 L',[('ap',AP(150,20)),('dev40',"cenDevolver(c,'REQ-035','Fungicida A',40,true,PAULA);")])
js=HEAD+PREAMB+"""
const L=[]; let sol={}; Object.entries(DM(c)).forEach(([n,d])=>{ if(d.liq>0.001) sol[n]=d.liq; }); L.push(['SOL-2026-07 enviada (semente) NPK',sol['NPK 20-05-20']]);
cenEntregar(c,'REQ-040','NPK 20-05-20',8000,'Carlos',PAULA); let R=demSolRevisar(sol,DM(c),false); L.push(['entrega 8.000 kg: novos/menos',R.novos,R.menos]);
osc_cancelar(c,'OS-0425','replanejado',['','',''],ANA); R=demSolRevisar(sol,DM(c),false); sol=R.it; L.push(['OS-0425 cancelada → Atualizar SOL: novos/menos/SOL NPK',R.novos,R.menos,sol['NPK 20-05-20']]);
cenDevolver(c,'REQ-040','NPK 20-05-20',8000,true,PAULA); R=demSolRevisar(sol,DM(c),true); const d=DM(c)['NPK 20-05-20'];
L.push(['devolução 8.000 kg com pedido emitido: novos/menos/SOL NPK/liq/situação',R.novos,R.menos,R.it['NPK 20-05-20'],d.liq,demSolSit(d,sol['NPK 20-05-20'],true,true)]);
console.log(JSON.stringify(L));"""
print('== T10 SOL com complemento e pedido emitido antes da devolução')
try:
    for l in runjs(js): print(' ',json.dumps(l,ensure_ascii=False))
except Exception as e: print('  erro:',repr(e)[:400])
print('######## S2-2 quarentena virando falta firme')
r=viva([('seed',''),('nfq',NF(20000,0,20000)),('laudo',"cenLiberarQuarentena(c,'Semente de soja 58 W|S58-0926','LAB-1',ANA);")])
print('== G5 NF 4533 20.000 kg em quarentena, depois laudo (S2627 Semente: liq, total)')
for lab,s in r['OUT']: print('  ',lab,(s['S2627']['liq'].get('Semente de soja 58 W'),s['S2627']['tot']))
if r['ERR']: print('  ERROS:',r['ERR'])
js=HEAD+PREAMB+"""
const L=[]; let sol={}; Object.entries(DM(c)).forEach(([n,d])=>{ if(d.liq>0.001) sol[n]=d.liq; });
"""+NF(20000,0,20000)+"""
const d=DM(c)['Semente de soja 58 W']; L.push(['após NF em quarentena: liq, situação (SOL enviada sem a semente)',d.liq,demSolSit(d,sol['Semente de soja 58 W'],true,false)]);
const R=demSolRevisar(sol,DM(c),false); L.push(['Atualizar SOL: novos',R.novos,R.it['Semente de soja 58 W']]);
console.log(JSON.stringify(L));"""
print('== G5b situação e revisão da SOL com a quarentena')
try:
    for l in runjs(js): print(' ',json.dumps(l,ensure_ascii=False))
except Exception as e: print('  erro:',repr(e)[:400])
run('D3 devolver 30 L Fungicida A da REQ-035 bloqueado',[('dev30q',"cenDevolver(c,'REQ-035','Fungicida A',30,false,PAULA);")])
