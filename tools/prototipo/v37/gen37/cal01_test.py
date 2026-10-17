# -*- coding: utf-8 -*-
"""Testes unitários do CAL-01 (PRD v3.9 · necessidade líquida por data): cal01.js executado no JavaScriptCore (jsc) ou Node,
espelho Python de dados2.cal01 com os mesmos casos, e paridade JS × Python nos dados reais (Safra 2026/27, Safrinha 2027, Mamão 2026/27).
Uso: python3 cal01_test.py            → testa cal01.js e dados2.cal01 (deste diretório)
     python3 cal01_test.py --antes D  → roda os mesmos casos na demanda() agregada de D/safra.js (contraprova do cálculo anterior)"""
import sys, os, json, subprocess, shutil, tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
def runjs(code):
    node=shutil.which('node'); f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8')
    f.write(code.replace('__OUT__','console.log' if node else 'print')); f.close()
    try: return subprocess.run([node or JSC,f.name],capture_output=True,text=True,timeout=60).stdout
    finally: os.unlink(f.name)
D=lambda dt,q,own=True,**k: dict(dict(dt=dt,q=q,tipo='dem',own=own,ord=k.pop('ord',0)),**k)
REC=lambda dt,q,**k: dict(dt=dt,q=q,tipo='rec',own=False,ord=0,**k)
RES=lambda dt,q,chave=None: dict(dt=dt,q=q,tipo='res',own=False,ord=0,chave=chave,t='Reserva')
# casos: (nome, físico apto, eventos, esperado {liq, falta, ...}, entrada da demanda agregada anterior {est (livre), rec, dem:[(dt,q)]})
CASOS=[
 ('AC-13 · demanda 80, físico 60 com 40 reservados à MESMA demanda → compra 20',60,[D('2026-10-03',80,chave='c1|a1'),RES('2026-09-30',40,'c1|a1')],dict(liq=20,falta='2026-10-03'),
   dict(est=20,rec=0,dem=[('2026-10-03',80)])),
 ('Entrega depois do uso · demanda 80 hoje, estoque 20, chegam 60 amanhã → falta 60 hoje',20,[D('2026-10-03',80),REC('2026-10-04',60)],dict(liq=60,falta='2026-10-03',tarde=60),
   dict(est=20,rec=60,dem=[('2026-10-03',80)])),
 ('Entrega no dia do uso cobre: estoque 20 + 60 hoje, demanda 80 hoje → 0',20,[D('2026-10-03',80),REC('2026-10-03',60)],dict(liq=0,falta=None),
   dict(est=20,rec=60,dem=[('2026-10-03',80)])),
 ('Reserva para OUTRO destino entra uma vez como demanda: físico 60, reserva 40 hoje, demanda 80 amanhã → 60',60,[D('2026-10-04',80),RES('2026-10-03',40)],dict(liq=60,falta='2026-10-04',antes=40),
   dict(est=20,rec=0,dem=[('2026-10-04',80)])),
 ('Reposição entra no saldo: sem estoque, 10 em d1 e 10 em d2 → 20 (não 30)',0,[D('2026-10-03',10),D('2026-10-05',10)],dict(liq=20,falta='2026-10-03'),
   dict(est=0,rec=0,dem=[('2026-10-03',10),('2026-10-05',10)])),
 ('Entrega entre dois usos: estoque 50, uso 60 em d1, chegam 40 em d2, uso 40 em d3 → 10',50,[D('2026-10-03',60),REC('2026-10-04',40),D('2026-10-05',40)],dict(liq=10,falta='2026-10-03'),
   dict(est=50,rec=40,dem=[('2026-10-03',60),('2026-10-05',40)])),
 ('Outra safra usa antes o mesmo estoque: físico 100, outra 100 em d1, esta 50 em d2 → 50',100,[D('2026-10-05',50,ord=1),D('2026-10-03',100,own=False,ord=0)],dict(liq=50,falta='2026-10-05',antes=100),
   dict(est=100,rec=0,dem=[('2026-10-05',50)])),
 ('Mesma projeção vista pela outra safra: a falta não é atribuída duas vezes → 0',100,[D('2026-10-03',100,ord=0),D('2026-10-05',50,own=False,ord=1)],dict(liq=0,falta=None),
   dict(est=100,rec=0,dem=[('2026-10-03',100)])),
 ('Mesmo dia, duas safras: a de ordem menor usa primeiro (A 0, B 50; soma 50)',50,[D('2026-10-03',50,ord=1),D('2026-10-03',50,own=False,ord=0)],dict(liq=50,falta='2026-10-03'),
   dict(est=50,rec=0,dem=[('2026-10-03',50)])),
 ('Estoque de segurança 5: físico 10, demanda 10 → 5',10,[D('2026-10-03',10)],dict(liq=5,falta='2026-10-03',seg=5),
   dict(est=10,rec=0,dem=[('2026-10-03',10)])),
 # opt {hoje, viavel}: consumo realizado e chegada viável de compra nova (PRD CAL-01: "Consumo já realizado sai tanto do físico quanto da necessidade
 # residual"; saldo_final = saldo_antes + reposicao_proposta_com_chegada_viavel)
 ('Consumo realizado sai da demanda: hoje 03/10, usos 30 em 01/10 (realizado) e 50 em 05/10, físico 40 → 10',40,[D('2026-10-01',30),D('2026-10-05',50)],
   dict(liq=10,falta='2026-10-05',real=30,opt=dict(hoje='2026-10-03')),dict(est=40,rec=0,dem=[('2026-10-01',30),('2026-10-05',50)])),
 ('Ruptura antes da chegada viável (30/09) coberta pelo recebimento de 30/09: físico 60, uso 110 em 25/09, chegam 50 → 0 · ruptura 50 de 25/09 a 30/09',60,
   [D('2026-09-25',110),REC('2026-09-30',50)],dict(liq=0,falta='2026-09-25',rupRec=50,cob='2026-09-30',opt=dict(hoje='2026-09-23',viavel='2026-09-30')),
   dict(est=60,rec=50,dem=[('2026-09-25',110)])),
 ('Ruptura sem recebimento até a chegada viável vira reposição nela: físico 0, uso 20 em 25/09 → 20 a partir de 25/09',0,[D('2026-09-25',20)],
   dict(liq=20,falta='2026-09-25',cob='2026-09-30',opt=dict(hoje='2026-09-23',viavel='2026-09-30')),dict(est=0,rec=0,dem=[('2026-09-25',20)])),
 ('Recebimento depois da chegada viável não cobre a ruptura: físico 60, uso 110 em 25/09, chegam 50 em 02/10 → 50',60,[D('2026-09-25',110),REC('2026-10-02',50)],
   dict(liq=50,falta='2026-09-25',tarde=50,opt=dict(hoje='2026-09-23',viavel='2026-09-30')),dict(est=60,rec=50,dem=[('2026-09-25',110)])),
 ('Falta depois da chegada viável: reposição na data do uso (entrega tardia não cobre) → 60',20,[D('2026-10-03',80),REC('2026-10-04',60)],
   dict(liq=60,falta='2026-10-03',tarde=60,opt=dict(hoje='2026-09-23',viavel='2026-09-30')),dict(est=20,rec=60,dem=[('2026-10-03',80)])),
]
SKIP=('seg','opt')
OK=[]; FAIL=[]
def chk(nome,cond,det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ')+nome+('' if cond else f' · {det}'))
def perto(a,b): return (a is None and b is None) or (a is not None and b is not None and abs(float(a)-float(b))<1e-6)
if '--antes' in sys.argv:
    # contraprova: os mesmos casos na demanda() agregada anterior (liq = máx(0, bruta − estoque livre − todos os recebimentos))
    src=open(os.path.join(sys.argv[sys.argv.index('--antes')+1],'safra.js'),encoding='utf-8').read()
    f=src[src.index('function demanda('):src.index('// produtividade da colheita')]
    js=['const nf=(x)=>String(x), br=(x)=>x; let D2={}, OC=[]; function ocorr(){ return OC; }',f,'const R=[];']
    for nome,fis,evs,esp,a in CASOS:
        js.append(f"D2={{estoque:{{X:{a['est']}}},receb:{{X:{a['rec']}}}}}; OC={json.dumps([dict(dt=dt,c=dict(v=dict(local='T')),a=dict(nome='Atv'),area=q,prods=[dict(nome='X',grupo='G',un='L',preco=1,dose=1,q=q)]) for dt,q in a['dem']])};"
                  f" R.push(demanda(null,'s').X.liq);")
    js.append('__OUT__(JSON.stringify(R));')
    res=json.loads(runjs('\n'.join(js)).strip())
    for (nome,fis,evs,esp,a),liq in zip(CASOS,res): chk('[cálculo anterior] '+nome,perto(liq,esp['liq']),f'devolve {liq}, CAL-01 pede {esp["liq"]}')
    print(f'\nRESULTADO (cálculo anterior): {len(OK)} ok · {len(FAIL)} falhas'); sys.exit(0)
# 1 · cal01.js
cal=open(os.path.join(HERE,'cal01.js'),encoding='utf-8').read()
js=cal+'\nconst R=[];\n'+''.join(f"R.push(cal01({fis},{json.dumps(evs)},{esp.get('seg',0)},{json.dumps(esp.get('opt',{}))}));\n" for _,fis,evs,esp,_a in CASOS)+'__OUT__(JSON.stringify(R));'
out=runjs(js).strip(); rj=json.loads(out) if out else []
import dados2 as D2
for (nome,fis,evs,esp,_a),r in zip(CASOS,rj):
    ok=all(perto(r[k],v) if k in ('liq','tarde','antes','real','rupRec') else (r[k]==v) for k,v in esp.items() if k not in SKIP)
    chk('[cal01.js] '+nome,ok,{k:r[k] for k in esp if k not in SKIP})
    o=esp.get('opt',{}); p=D2.cal01(fis,evs,esp.get('seg',0),o.get('hoje',''),o.get('viavel',''))
    chk('[dados2.cal01 = cal01.js] '+nome,all(perto(p[k],r[k]) for k in ('liq','antes','tarde','real','rupRec')) and p['falta']==r['falta'] and p['cob']==r['cob'],(p['liq'],p['falta'],p['cob'],r['liq'],r['falta'],r['cob']))
chk('jsc/Node executou todos os casos',len(rj)==len(CASOS),out[:200])
# 2 · memória: as linhas citam reserva da mesma demanda, recebimento tardio e o resultado
mem=json.loads(runjs(cal+f"\n__OUT__(JSON.stringify([cal01Memo(cal01(60,{json.dumps(CASOS[0][2])}),{{un:'L',res:40}}),cal01Memo(cal01(20,{json.dumps(CASOS[1][2])}),{{un:'L'}})]));").strip())
chk('memória AC-13: físico com reservas, reserva contada uma vez, compra 20',mem[0][0]=='Estoque apto hoje: 60 L (inclui 40 L reservados)' and any('da mesma demanda, contados uma vez' in l for l in mem[0]) and mem[0][-1].startswith('Necessidade líquida = soma das faltas desta safra = 20 L'),mem[0])
chk('memória entrega tardia: falta 60 na data de uso; a entrega de 04/10 fica depois do último uso',any('falta 60 L' in l and l.startswith('03/10/2026 · ') for l in mem[1]) and mem[1][-1].endswith('falta a partir de 03/10/2026'),mem[1])
OP=json.dumps(dict(hoje='2026-09-23',viavel='2026-09-30'))
mem2=json.loads(runjs(cal+f"\n__OUT__(JSON.stringify([cal01Memo(cal01(60,{json.dumps([D('2026-01-09',500),D('2026-09-25',110),REC('2026-09-30',50,t='Recebimento previsto')])},0,{OP}),{{un:'kg'}})]));").strip())[0]
chk('memória com uso antes de hoje sem O.S. e ruptura coberta: fora da demanda (histórico do plano, DEM-06), ruptura na data de uso, recebimento cobre, sem compra nova',
    mem2[1]=='Antes de 23/09/2026 sem O.S. · 1 uso · 500 kg · fora da demanda (histórico do plano; se ainda vai acontecer, emita a O.S.)' and any(l.startswith('25/09/2026 · ') and l.endswith('ruptura 50.000 kg'.replace('50.000','50')) for l in mem2)
    and any(l.startswith('30/09/2026 · Recebimento previsto · +50,0 kg') and l.endswith('cobre a ruptura') for l in mem2)
    and mem2[-1]=='Sem compra nova · ruptura de 50 kg de 25/09/2026 a 30/09/2026, coberta pelo recebimento',mem2)
# 3 · paridade nos dados reais: cal01.js sobre as mesmas entradas de dados2.demanda() dá a mesma necessidade e a mesma data de falta
OPT=json.dumps(dict(hoje=D2.HOJE_ISO,viavel=D2.VIAVEL))
# CTL-4 (demanda única): as O.S. entram na demanda e o estoque é o da fazenda da safra (demanda_unica_test.py reproduz os números).
# Revisão do 853a6a8 (achado 1): a custódia sem uso nas O.S. entra no saldo (os 500 kg de MAP da OS-0417, em conferência): S2627 R$ 428.305,00
for saf,(n_esp,v_esp) in {'S2627':(14,428305.00),'S27SF':(8,1094947.10),'LG2627':(13,1614360.34)}.items():
    dm=D2.demanda(saf); its=sorted(dm)
    rr=json.loads(runjs(cal+'\nconst R=[];\n'+''.join(f"R.push(cal01({dm[n]['estoque']+dm[n].get('cust',0)+dm[n].get('quarC',0)},{json.dumps(dm[n]['evs'],ensure_ascii=False)},0,{OPT}));\n" for n in its)+'__OUT__(JSON.stringify(R.map(r=>[calR2(r.liq),r.falta])));').strip())   # a demanda leva a quantidade a comprar com 0,01 da unidade (calR2)
    dif=[(n,dm[n]['liq'],dm[n]['falta'],r) for n,r in zip(its,rr) if not (perto(r[0],dm[n]['liq']) and r[1]==dm[n]['falta'])]
    tot=sum(o['valor'] for o in dm.values()); n=sum(1 for o in dm.values() if o['liq']>0.001)
    chk(f'paridade {saf}: {len(its)} insumos, JS = Python (necessidade e data da falta)',not dif,dif[:3])
    chk(f'{saf}: {n} insumos a comprar · R$ {tot:,.2f}',n==n_esp and abs(tot-v_esp)<0.005,(n,tot))
s1=D2.demanda('S2627'); fa=s1['Fungicida A']
chk('Safra 2026/27 · Fungicida A: físico apto 545 L (inclui 65 da OS-0424, a mesma demanda da ordem) → 0 L: a OS-0421 já cobre a 1ª aplicação (nunca 145,2 L)',fa['estoque']==545 and fa['reservado']==65 and perto(round(fa['liq'],1),0),(fa['estoque'],fa['reservado'],fa['liq']))
s2=D2.demanda('S27SF')
chk('Safrinha 2027 · MAP 11-52: os 90 t aptos vão antes para a Safra 2026/27 → 101.440 kg a partir de 20/02/2027',perto(s2['MAP 11-52']['liq'],101440) and s2['MAP 11-52']['falta']=='2027-02-20',(s2['MAP 11-52']['liq'],s2['MAP 11-52']['falta']))
lg=D2.demanda('LG2627'); ca=lg['Calcário dolomítico filler']
chk('Mamão 2026/27 · calcário: 1.185,68 t do plano antes de hoje sem O.S. ficam fora da demanda; 96,94 t em 25/09 com 60 t aptos → ruptura de 36,94 t coberta pelo pedido de 30/09, sem compra nova',
    perto(ca['real'],1185680) and perto(ca['bruta'],96940) and perto(ca['liq'],0) and ca['falta']=='2026-09-25' and perto(ca['rup'],36940) and ca['cob']=='2026-09-30',
    {k:ca[k] for k in ('real','bruta','liq','falta','rup','cob')})
chk('Mamão 2026/27 · nenhuma falta antes de hoje',all(not o['falta'] or o['falta']>=D2.HOJE_ISO for o in lg.values()),[(n,o['falta']) for n,o in lg.items() if o['falta'] and o['falta']<D2.HOJE_ISO])
chk('reservas da demanda (est_dem, cenário da semente) fecham com o reservado dos lotes; disponível por lote fecha com ESTOQUE',not D2.checa_reservas() and not D2.checa_coerencia(),(D2.checa_reservas(),D2.checa_coerencia()))
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas'); [print('  -',f) for f in FAIL]
sys.exit(1 if FAIL else 0)
