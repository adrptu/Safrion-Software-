# -*- coding: utf-8 -*-
"""CTL-4 (CONTROLE-01, frente C, S2) · demanda líquida única por fazenda, sem navegador: Node (cal01.js + cenario.js) e o espelho Python (dados2).
Regras DEM-01..08 (desenho FRENTE-C revisado): a parte do plano convertida em O.S. deixa de ser demanda do plano (RN-006, AC-08); a O.S. conta pelo
que ainda vai tirar do almoxarifado (CAL-01 l.4201); O.S. sem vínculo nunca some; reserva da mesma O.S. conta uma vez; estoque e recebimentos são
da fazenda da safra (RN-011); uso do plano antes de hoje sem O.S. não é "realizado" (RN-003); Planejar safra, Compra e Mapa leem a mesma conta.
Seção A reproduz o dano (falha na base ecc8b00): compra em dobro (Fungicida A 145,2 L, Adjuvante 2,5 L), compra a menos (MAP sem a OS-0420,
Ureia da OS-0418, Lagoa Grande com o estoque da Santa Rita) e Mapa com outra conta (Fungicida A "Falta 194 L", Óleo "Falta 903 L").
Uso: python3 demanda_unica_test.py   (≈ 10 s)"""
import sys, os, json, copy, subprocess, shutil, tempfile, traceback
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); os.chdir(HERE)
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {str(det)[:500]}'),flush=True)
def caso(nome,fn):   # a base não tem as funções novas: o erro vira FALHA com o motivo, sem parar o resto
    try: r=fn(); chk(nome,r[0],r[1] if len(r)>1 else '')
    except Exception as e: chk(nome,False,f'{type(e).__name__}: {e}')
def runjs(code):
    node=shutil.which('node'); f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8'); f.write(code); f.close()
    try:
        p=subprocess.run([node,f.name],capture_output=True,text=True,timeout=120)
        if p.returncode: raise RuntimeError(p.stderr[-800:])
        return json.loads(p.stdout.strip().splitlines()[-1])
    finally: os.unlink(f.name)
import dados2 as D2
L=lambda d,n: round(d[n]['liq'],2) if n in d else None
perto=lambda a,b,t=1e-6: a is not None and b is not None and abs(a-b)<t
nins=lambda d: sum(1 for o in d.values() if o['liq']>0.001)
tot=lambda d: sum(o['valor'] for o in d.values())
d=D2.demanda('S2627'); s27=D2.demanda('S27SF'); lg=D2.demanda('LG2627')
# ---------------- A · dano reproduzido (vermelho na base) ----------------
print('== A · dano (compra em dobro, compra a menos, Mapa com outra conta)')
caso('A1 compra em dobro: Fungicida A da Safra 2026/27 = 0 L (nunca 145,2 L · R$ 21.054); a OS-0421 já tem 160 L entregues e 65 L em custódia',
     lambda: (L(d,'Fungicida A')==0.0,L(d,'Fungicida A')))
caso('A2 compra em dobro: Adjuvante espalhante = 0 L (nunca 2,5 L) — a OS-0421 já leva o adjuvante',lambda: (L(d,'Adjuvante espalhante')==0.0,L(d,'Adjuvante espalhante')))
caso('A3 compra a menos: MAP 11-52 = 80.000 kg a partir de 18/10/2026 (nunca 62.500): a OS-0420 (T4, 70 ha de saldo) pede 17.500 kg',
     lambda: (L(d,'MAP 11-52')==80000.0 and d['MAP 11-52']['falta']=='2026-10-18',(L(d,'MAP 11-52'),d['MAP 11-52']['falta'])))
caso('A4 compra a menos: Ureia 45% = 1.140 kg a partir de 24/09/2026 (a OS-0418 pede e o estoque é 0)',
     lambda: ('Ureia 45%' in d and L(d,'Ureia 45%')==1140.0 and d['Ureia 45%']['falta']=='2026-09-24',(L(d,'Ureia 45%'),(d.get('Ureia 45%') or {}).get('falta'))))
caso('A5 compra a menos na Lagoa Grande: Glifosato 480 = 293,34 L a partir de 30/09/2026, estoque apto 0 (o lote G26-14 é da Santa Rita)',
     lambda: (L(lg,'Glifosato 480')==293.34 and lg['Glifosato 480']['falta']=='2026-09-30' and lg['Glifosato 480']['estoque']==0,(L(lg,'Glifosato 480'),lg['Glifosato 480']['falta'],lg['Glifosato 480']['estoque'])))
caso('A6 estoque da própria fazenda: Óleo mineral LG 630,02 L (nunca 292,81) · Nitrato de cálcio LG 25.756,8 kg e Santa Rita 680 kg',
     lambda: (L(lg,'Óleo mineral')==630.02 and L(lg,'Nitrato de cálcio')==25756.8 and L(d,'Nitrato de cálcio')==680.0,(L(lg,'Óleo mineral'),L(lg,'Nitrato de cálcio'),L(d,'Nitrato de cálcio'))))
caso('A7 totais: S2627 14 insumos · R$ 430.255,00; S27SF 8 · R$ 1.094.946,91; LG2627 13 · R$ 1.614.202,52',
     lambda: (nins(d)==14 and perto(tot(d),430255.00,0.005) and nins(s27)==8 and perto(tot(s27),1094946.91,0.005) and nins(lg)==13 and perto(tot(lg),1614202.52,0.005),
              ((nins(d),round(tot(d),2)),(nins(s27),round(tot(s27),2)),(nins(lg),round(tot(lg),2)))))
# Mapa › Insumos: a página leva as entradas da mesma conta (MDATA.dem) e calcula com demFazenda/demSituacao (cal01.js) sobre o cenário vivo
import cenario
CAL=open(os.path.join(HERE,'cal01.js'),encoding='utf-8').read(); PRE=cenario.js_prefixo()
def mapa_js(dem,extra=''):
    return runjs(PRE+'\n'+CAL+f"""\nconst X={json.dumps(dem,ensure_ascii=False)}; const R={{}};
Object.keys(X.faz).forEach(f=>{{ const F=X.faz[f]; const m=demFazenda(Object.assign({{}},F,{{osd:cenOsDem(CEN0,X.osb)}})); const tid=(t)=>X.tid[t]||demTal(t);
  R[f]={{st:{{'Safra toda':demSituacao(m,null,F.hoje,F.viavel),'Próximos 30 dias':demSituacao(m,X.lim30,F.hoje,F.viavel)}},nec:demPorLocal(m,tid,F.areaT,F.hoje),
    liq:Object.fromEntries(Object.values(m).map(x=>[x.nome,x.liq])),own:Object.fromEntries(Object.values(m).map(x=>[x.nome,x.evs.filter(e=>e.tipo==='dem'&&e.own&&e.dt>=F.hoje).reduce((a,e)=>a+e.q,0)]))}}; }});
{extra}console.log(JSON.stringify(R));""")
MP={}
def _mapa():
    import areas.inicio as I
    MP.update(mapa_js(dict(I.MDATA['dem'],lim30=I.MDATA['lim30']))); return MP
def a8():
    import areas.inicio as I
    if 'dem' in I.MDATA: m=_mapa(); sr=m['Santa Rita']['st']['Safra toda']; lgs=m['Lagoa Grande']['st']['Safra toda']
    else: sr=dict(I.FAZST['Safra toda']); lgs={}   # base ecc8b00: conta própria do Mapa (inicio._fazst), as duas fazendas juntas
    num=lambda t: float(t.split(' ')[1].replace('.','').replace(',','.'))   # "Falta 1.140 kg" → 1140 (o Mapa mostra inteiro)
    dif={p:(v[0],round(L(d,p) or 0,2)) for p,v in sr.items() if (v[1]=='red')!=((L(d,p) or 0)>0.001) or (v[1]=='red' and (not v[0].endswith(' '+d[p]['un']) or abs(num(v[0])-d[p]['liq'])>0.5+1e-9))}
    return (not dif and sr['Fungicida A'][0]=='Estoque cobre' and sr['MAP 11-52'][0]=='Falta 80.000 kg',dif)
caso('A8 Mapa › Insumos lê a mesma demanda da Compra: Santa Rita, safra toda, "Falta X" = necessidade líquida de dados2.demanda em todo insumo (na base: Fungicida A "Falta 130 L" × 145,2 L; Óleo mineral "Falta 903 L" × 210 L); Fungicida A "Estoque cobre", MAP "Falta 80.000 kg"',a8)
# ---------------- B · regras (positivos e negativos) ----------------
print('== B · regras DEM-01..07')
def osd_mod(fn,cen=None):
    o=copy.deepcopy(D2.os_dem(cen)); fn(o); return o
caso('B1 DEM-02 pendente da OS-0421 (Em execução, saldo 160 ha × 0,50 L/ha − 65 L em custódia) = 15 L, na data de hoje, com a conta escrita',
     lambda: (lambda o: ([i['q'] for i in o['itens'] if i['p']=='Fungicida A']==[15.0] and o['dt']=='2026-09-23'
                         and [i['calc'] for i in o['itens'] if i['p']=='Fungicida A']==['0,50 L/ha × 160 ha − 65 L em custódia'],o))(next(x for x in D2.os_dem() if x['id']=='OS-0421')))
def b2():
    fa=d['Fungicida A']; ate=[e for e in fa['evs'] if e['dt']<='2026-09-24']; r=D2.cal01(fa['estoque'],ate,0.0,D2.HOJE_ISO,D2.VIAVEL)
    res=[e for e in fa['evs'] if e['tipo']=='res']
    return (r['saldo']==466 and res and res[0]['chave']=='OS-0424' and any(e.get('chave')=='OS-0424' and e['tipo']=='dem' for e in fa['evs']),(r['saldo'],res))
caso('B2 DEM-04 reserva REQ-039 e OS-0424 (64 L) contadas uma vez: saldo de 466 L em 24/09 (545 − 15 − 64)',b2)
caso('B3 DEM-01 escopo: c1, c2 e c3|a6 com 0,42623 sem O.S. (OS-0421 cobre 350 de 610 ha, rateados pela área); c3|a3 0,65772 (OS-0431 102 de 298 ha); c1|a1 e c9|k1 0',
     lambda: (lambda fr: (all(abs(fr[k]['f']-(1-350/610))<1e-9 for k in ('c1|a6','c2|a6','c3|a6')) and abs(fr['c3|a3']['f']-(1-102/298))<1e-9 and fr['c1|a1']['f']==0 and fr['c9|k1']['f']==0
                          and fr['c1|a6']['txt']=='OS-0421 cobre 350 de 610 ha, rateados pela área' and fr['c3|a3']['txt']=='OS-0431 cobre 102 de 298 ha',fr))(D2.dem_restante(D2.os_dem(),D2.occ_faz('S2627'))))
caso('B4 N1 a O.S. cobre só a parte dela: com a chave inteira o MAP cairia para 31.000 kg; a regra exige 80.000',
     lambda: (lambda dx: (L(dx,'MAP 11-52')==31000.0,L(dx,'MAP 11-52')))(D2.demanda('S2627',osd=osd_mod(lambda o:[x.update(area=10**6) for x in o if x['id']=='OS-0431']))))
def b5():
    dx=D2.demanda('S2627',osd=osd_mod(lambda o:o.__setitem__(slice(None),[x for x in o if x['id']!='OS-0431'])))
    return (L(dx,'MAP 11-52')==80000.0 and any(e.get('chave')=='c3|a3' and abs(e['q']-74500)<1e-6 for e in dx['MAP 11-52']['evs']),[(e.get('chave'),e['q']) for e in dx['MAP 11-52']['evs'] if e['tipo']=='dem'])
caso('B5 N2 OS-0431 cancelada: c3|a3 volta inteira ao plano (74.500 kg) e o MAP segue 80.000 kg (o pendente dela sai junto)',b5)
def b6():
    c=copy.deepcopy(cenario.seed()); c['ordens']['OS-0421']['etapa']='Em conferência'; dx=D2.demanda('S2627',osd=D2.os_dem(c)); fa=[e for e in dx['Fungicida A']['evs'] if e['tipo']=='dem' and e.get('own')]
    return (not any(e.get('chave')=='OS-0421' for e in fa) and round(sum(e['q'] for e in fa if str(e.get('chave','')).endswith('|a6')),2)==136.48,[(e.get('chave'),round(e['q'],2)) for e in fa])
caso('B6 N3 OS-0421 Em conferência: pendente 0 (sem evento da ordem), mas as chaves a6 continuam cobertas: 136,48 L, nunca 320,2 L',b6)
def b7():
    c=copy.deepcopy(cenario.seed()); c['reqs']['REQ-035']['itens'][0]['custodia']=200; o=next(x for x in D2.os_dem(c) if x['id']=='OS-0421')
    return ([i['q'] for i in o['itens'] if i['p']=='Fungicida A']==[0.0],o['itens'])
caso('B7 N4 custódia de 200 L maior que os 80 L do saldo: pendente 0, nunca negativo (os_dem sobre o cenário alterado)',b7)
caso('B8 N6 a OS-0501 (Lagoa Grande) não entra na Santa Rita: Glifosato S2627 20 L, sem evento da OS-0501',
     lambda: (L(d,'Glifosato 480')==20.0 and not any(e.get('chave')=='OS-0501' for e in d['Glifosato 480']['evs']),L(d,'Glifosato 480')))
caso('B9 N7 chave fora do plano (T4 sem plano): sem fração e sem erro',lambda: (D2.dem_restante([dict(id='X',saf='S2627',chaves=['c4|a6'],loc=['T4'],area=50,itens=[])],[])=={},))
caso('B10 N8 400 ha de O.S. numa chave de 298 ha: fração 0, nunca negativa',
     lambda: (D2.dem_restante([dict(id='A',saf='S2627',chaves=['c3|a3'],loc=['T2'],area=200),dict(id='B',saf='S2627',chaves=['c3|a3'],loc=['T2'],area=200)],
                              [dict(saf='S2627',k='c3|a3',a='a3',local='T2',tal='T2',area=298)])['c3|a3']['f']==0.0,))
caso('B11 escopo por safra: a O.S. da Safra 2026/27 não cobre a mesma atividade de outra safra no mesmo talhão',
     lambda: (D2.dem_restante([dict(id='A',saf='S2627',chaves=['c1|a6'],loc=['T1'],area=160)],[dict(saf='S27SF',k='d1|a6',a='a6',local='T1-A',tal='T1',area=160)])=={},))
def b12():
    PX={'c4':'SOJA-AT','c5':'SOJA-AT','c6':'SOJA-AT','c7':'SOJA-AT'}; dp=D2.demanda('S2627',planos_extra=PX)
    t4=sum(e['q'] for e in dp['MAP 11-52']['evs'] if e['tipo']=='dem' and e.get('own') and 'T4' in e['t'])
    return (t4==43500 and L(dp,'MAP 11-52')==173750.0 and perto(tot(dp),1205541.91,0.01),(t4,L(dp,'MAP 11-52'),round(tot(dp),2)))
caso('B12 N12 "Aplicar plano em 4 cultivos": MAP do T4 = 26.000 (104 ha sem O.S.) + 17.500 (OS-0420, chave c4|a3) = 43.500, nunca 68.500 · MAP 173.750 kg · R$ 1.205.541,91',b12)
def b13():
    dx=D2.demanda('S2627',planos_extra={'c7':'SOJA-AT'}); ev=[e for e in dx['Fungicida A']['evs'] if e['tipo']=='dem' and e.get('chave')=='OS-0424']
    return (L(dx,'Fungicida A')==55.48 and len(ev)==1 and 'sem vínculo com o plano do talhão' in ev[0]['t'],(L(dx,'Fungicida A'),[e['t'] for e in ev]))
caso('B13 N13 P2 ganha plano e a OS-0424 (sem chave) continua contando, com aviso de vínculo: Fungicida A 55,48 L',b13)
caso('B14 aviso só com o mesmo produto: a OS-0418 (Ureia, P1) não avisa, porque P1 não tem plano com Ureia',
     lambda: (not any('sem vínculo' in e['t'] for e in d['Ureia 45%']['evs']),[e['t'] for e in d['Ureia 45%']['evs']]))
def b15():
    C0=copy.deepcopy(D2.CULTIVOS['S2627']); A0=copy.deepcopy(D2.AJUSTES); out=[]
    try:
        for c in C0:
            if c['id']!='c3': out.append(copy.deepcopy(c)); continue
            for i,(nm,ar) in enumerate((('T2-A',99.33),('T2-B',99.33),('T2-C',99.34))):
                x=copy.deepcopy(c); x['local']=nm; x['area']=ar; x['tipo']='Parcela'; x['id']='c3' if i==0 else f'n{i}'; out.append(x)
        D2.CULTIVOS['S2627']=out; b=D2.demanda('S2627')
    finally: D2.CULTIVOS['S2627']=C0; D2.AJUSTES.clear(); D2.AJUSTES.update(A0)
    return (all(abs(d[n]['liq']-b[n]['liq'])<1e-6 for n in d) and abs(tot(d)-tot(b))<0.005,(round(tot(b),2),L(b,'MAP 11-52')))
caso('B15 N14 dividir T2 em 3 parcelas com o mesmo plano: mesmo valor e mesmas líquidas (a O.S. cobre pelo talhão dela)',b15)
caso('B16 DEM-06 o uso do plano antes de hoje sem O.S. continua fora da demanda: calcário LG 1.185.680 kg fora, bruta 96.940, 0 a comprar, ruptura 36.940 kg coberta em 30/09',
     lambda: (lambda ca: (perto(ca['real'],1185680) and perto(ca['bruta'],96940) and perto(ca['liq'],0) and ca['falta']=='2026-09-25' and perto(ca['rup'],36940) and ca['cob']=='2026-09-30',
                          {k:ca[k] for k in ('real','bruta','liq','falta','rup','cob')}))(lg['Calcário dolomítico filler']))
caso('B17 OS-0420 com a chave de origem c4|a3 (processo_os: "REC-014 v2 · Plantio e adubação de base"; campo: 1ª onda de 100 ha da NEC-028)',
     lambda: (next(x for x in D2.os_dem() if x['id']=='OS-0420')['chaves']==['c4|a3'],))
def b18():
    c=copy.deepcopy(cenario.seed()); c['ordens']['OS-0418']['etapa']='Canceladas'; dx=D2.demanda('S2627',osd=D2.os_dem(c))
    return ('Ureia 45%' not in dx and nins(dx)==13 and perto(tot(dx),426721.00,0.005),(nins(dx),round(tot(dx),2)))
caso('B18 O.S. cancelada no cenário (OS-0418): a Ureia sai da demanda · 13 insumos · R$ 426.721,00',b18)
NOVA=dict(id='OS-0440',novo=True,jan='2026-10-01',keys=['c1|a7'],tipo='Pulverização · Fungicida 2ª aplicação + inseticida',talhao='T1-A',area=160,etapa='A liberar',
          faz='Santa Rita',saf='2026/27',atv=dict(nome='Fungicida 2ª aplicação + inseticida'))
def cen_nova():
    c=copy.deepcopy(cenario.seed())
    c['ordens']['OS-0440']=dict(id='OS-0440',tipo=NOVA['tipo'],talhao='T1-A',area=160,etapa='A liberar',versao='v1',realizado=0,saldo=160,resp='—',
        ins=[dict(p='Fungicida A',dose=0.5,un='L',tot=80.0),dict(p='Inseticida B',dose=0.3,un='L',tot=48.0)],req=None,selos=[],ap=[],reservado=False,osc=dict(novo=NOVA))
    return c
def b19():
    dx=D2.demanda('S2627',osd=D2.os_dem(cen_nova())); ev=[e for e in dx['Fungicida A']['evs'] if e['tipo']=='dem' and e.get('own')]
    return (not any(e.get('chave')=='c1|a7' for e in ev) and any(e.get('chave')=='OS-0440' and e['dt']=='2026-10-01' and e['q']==80 for e in ev) and perto(tot(dx),tot(d),0.005),
            [(e.get('chave'),e['dt'],e['q']) for e in ev])
caso('B19 O.S. nova emitida no cenário (OS-0440, c1|a7, janela 01/10): substitui a parte do plano (80 L de 14/12 viram 80 L em 01/10), sem somar os dois; o total não muda',b19)
# ---------------- C · paridade JS × Python (a mesma conta nos dois lados) ----------------
print('== C · paridade cal01.js/cenario.js × dados2')
def c1():
    js=runjs(PRE+'\n'+CAL+f"\nconsole.log(JSON.stringify(cenOsDem(CEN0,{json.dumps(D2.os_base(),ensure_ascii=False)})));"); py=D2.os_dem()
    return (json.loads(json.dumps(py))==js,[(a['id'],b['id']) for a,b in zip(py,js) if a!=b][:3] or (len(py),len(js)))
caso('C1 cenOsDem(CEN0) (JS) = dados2.os_dem() (Python): mesmas ordens, chaves, datas, pendentes e contas',c1)
def c1b():
    cn=cen_nova(); cn['ordens']['OS-0418']['etapa']='Canceladas'; cn['reqs']['REQ-035']['itens'][0]['custodia']=40
    js=runjs(PRE+'\n'+CAL+f"\nconsole.log(JSON.stringify(cenOsDem({json.dumps(cn,ensure_ascii=False)},{json.dumps(D2.os_base(),ensure_ascii=False)})));"); py=D2.os_dem(cn)
    return (json.loads(json.dumps(py))==js and any(o['id']=='OS-0440' for o in js) and not any(o['id']=='OS-0418' for o in js),[(a['id'],b['id']) for a,b in zip(py,js) if a!=b][:3] or (len(py),len(js)))
caso('C1b paridade num cenário alterado (ordem nova, ordem cancelada, custódia mudada): cenOsDem = os_dem',c1b)
def c2():
    dif=[]
    for saf,px in (('S2627',None),('S27SF',None),('LG2627',None),('S2627',{'c4':'SOJA-AT','c5':'SOJA-AT','c6':'SOJA-AT','c7':'SOJA-AT'})):
        x=D2.dem_entradas(saf,planos_extra=px); py=D2.demanda(saf,planos_extra=px)
        js=runjs(PRE+'\n'+CAL+f"\nconst x={json.dumps(x,ensure_ascii=False)}; x.osd=cenOsDem(CEN0,{json.dumps(D2.os_base(),ensure_ascii=False)}); const m=demFazenda(x);"
                 "console.log(JSON.stringify(Object.values(m).map(d=>[d.nome,d.liq,d.falta,d.bruta,d.real,d.est,d.rup,d.cob,d.evs.map(e=>[e.dt,Math.round(e.q*1e6)/1e6,e.tipo,e.t,e.calc||'']),cal01Memo(d.cal,{un:d.un,res:d.res})])));")
        for nm,liq,falta,bruta,real,est,rup,cob,evs,memo in js:
            o=py.get(nm)
            pe=[[e['dt'],round(e['q'],6),e['tipo'],e['t'],e.get('calc') or ''] for e in o['evs']] if o else None
            if not o or not perto(o['liq'],liq) or o['falta']!=falta or not perto(o['bruta'],bruta) or not perto(o['real'],real) or o['estoque']!=est or not perto(o['rup'],rup) or o['cob']!=cob or pe!=evs:
                dif.append((saf,nm,(o or {}).get('liq'),liq,[(a,b) for a,b in zip(pe or [],evs) if a!=b][:2]))
        if [n for n,*_ in js]!=list(py): dif.append((saf,'ordem dos insumos',list(py)[:5],[n for n,*_ in js][:5]))
    return (not dif,dif[:4])
caso('C2 demFazenda (JS) = dados2.demanda (Python) nas 3 safras abertas e com "Aplicar plano em 4 cultivos": líquida, falta, bruta, antes de hoje, estoque, ruptura e cada evento (data, quantidade, texto, conta)',c2)
def c3():
    m=runjs(CAL+"""\nconst M=cal01Memo(cal01(60,[{dt:'2026-01-09',q:500,tipo:'dem',own:true,ord:0},{dt:'2026-09-25',q:110,tipo:'dem',own:true,ord:0},{dt:'2026-09-30',q:50,tipo:'rec',own:false,ord:0,t:'Recebimento previsto'}],0,{hoje:'2026-09-23',viavel:'2026-09-30'}),{un:'kg'}); console.log(JSON.stringify(M));""")
    return (m[1]=='Antes de 23/09/2026 sem O.S. · 1 uso · 500 kg · fora da demanda (histórico do plano; se ainda vai acontecer, emita a O.S.)' and not any('Realizado' in l for l in m),m[:2])
caso('C3 DEM-06 memória: "Antes de 23/09/2026 sem O.S. · … · fora da demanda (histórico do plano; se ainda vai acontecer, emita a O.S.)", nunca "Realizado"',c3)
# ---------------- D · Compra (DEM-08) ----------------
print('== D · Compra: escolha padrão sem proposta a tempo (DEM-08)')
def d1():
    P=[dict(f='F01',nome='Fertisul',unit=3.01,chega='2026-10-05',late=True),dict(f='F06',nome='Coop. Vale',unit=3.07,chega='2026-10-08',late=True),
       dict(f='F02',nome='Casa do Adubo',unit=3.13,chega='2026-10-01',late=True),dict(f='FX',nome='Outro',unit=3.30,chega='2026-10-10',late=True)]
    r=runjs(CAL+f"\nconst P={json.dumps(P)}; const ref=cmpRef(P); console.log(JSON.stringify([ref.f,cmpJust(ref,ref,P),cmpJust(P[0],ref,P),cmpJust(P[1],ref,P),cmpJust(P[3],ref,P),cmpEscolha(ref,ref,P[0],P),cmpEscolha(P[0],ref,P[0],P),cmpEscolha(P[1],ref,P[0],P)]));")
    return (r[0]=='F02' and r[1:5]==[False,False,False,True] and r[5]['selo']=='Chega primeiro' and r[6]['selo']=='Menor custo total' and r[7]['selo']=='',r)
caso('D1 Ureia (nenhuma proposta chega até 24/09): padrão = Casa do Adubo, a que chega primeiro (01/10), selo "Chega primeiro", sem justificativa; mais barata e mais tardia dispensa; mais cara e mais tardia exige',d1)
def d2():
    P=[dict(f='F04',nome='Santa Rita Insumos',unit=29.76,chega='2026-09-30',late=True),dict(f='F03',nome='Agro Norte',unit=32.64,chega='2026-09-28',late=False)]
    r=runjs(CAL+f"\nconst P={json.dumps(P)}; const ref=cmpRef(P); console.log(JSON.stringify([ref.f,cmpJust(ref,ref,P),cmpJust(P[0],ref,P),cmpEscolha(ref,ref,P[0],P).selo]));")
    return (r==['F03',False,True,'Menor custo a tempo'],r)
caso('D2 com proposta a tempo a trava continua: 2,4-D padrão Agro Norte (menor custo a tempo); escolher a Santa Rita (chega depois da falta) exige justificativa',d2)
# ---------------- E · Mapa por talhão e por período (DEM-05) ----------------
print('== E · Mapa › Insumos')
def e1():
    m=MP or _mapa(); cnt=lambda st: [len(st),sum(v[1]=='red' for v in st.values()),sum(v[1]=='yellow' for v in st.values()),sum(v[1]=='ok' for v in st.values())]
    r={f:{p:cnt(m[f]['st'][p]) for p in ('Safra toda','Próximos 30 dias')} for f in m}
    return (r['Santa Rita']=={'Safra toda':[19,14,3,2],'Próximos 30 dias':[13,9,1,3]} and r['Lagoa Grande']['Safra toda']==[14,13,1,0],r)
caso('E1 faixa do Mapa: Santa Rita safra toda 19 produtos · 14 faltam · 3 aguardando pedido · 2 estoque cobre; 30 dias 13 · 9 · 1 · 3; Lagoa Grande safra toda 14 · 13 · 1 · 0',e1)
def e2():
    m=MP or _mapa(); bad=[]
    for f in m:
        tot_={}
        for t,its in m[f]['nec'].items():
            for x in its: tot_[x['p']]=tot_.get(x['p'],0)+x['q']
        bad+=[(f,p,q,m[f]['own'].get(p)) for p,q in tot_.items() if abs(q-m[f]['own'].get(p,0))>1e-6]
    sr=m['Santa Rita']['nec']; t4=sum(x['q'] for x in sr.get('T4',[]) if x['p']=='MAP 11-52'); pv=sum(x['q'] for x in m['Lagoa Grande']['nec'].get('PV13',[]) if x['p']=='Glifosato 480')
    return (not bad and t4==17500 and round(pv,2)==147.93 and m['Santa Rita']['st']['Próximos 30 dias']['MAP 11-52'][0]=='Falta 42.000 kg' and m['Lagoa Grande']['st']['Safra toda']['Glifosato 480'][0]=='Falta 293 L',
            (bad[:3],t4,pv,m['Santa Rita']['st']['Próximos 30 dias'].get('MAP 11-52'),m['Lagoa Grande']['st']['Safra toda'].get('Glifosato 480')))
caso('E2 por talhão: soma dos talhões = fazenda em todo insumo (O.S. de vários talhões rateada pela área); T4 MAP 17.500 kg; PV13 Glifosato 147,93 L e "Falta 293 L"; MAP nos próximos 30 dias "Falta 42.000 kg"',e2)
def e3():
    m=MP or _mapa(); st=m['Santa Rita']['st']['Safra toda']
    return (st['MAP 11-52'][2]=='precisa de 170.000 kg · estoque apto 90.000 kg · falta a partir de 18/10/2026 · Suprimentos compra na Compra de insumos'
            and st['KCl 60%'][0]=='Pedido a receber · PC-088 · 02/10',(st.get('MAP 11-52'),st.get('KCl 60%')))
caso('E3 detalhe do MAP: "precisa de 170.000 kg · estoque apto 90.000 kg · falta a partir de 18/10/2026 …"; KCl "Pedido a receber · PC-088 · 02/10"',e3)
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
