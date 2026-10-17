# -*- coding: utf-8 -*-
"""Mundo de dados dos processos (menu vigente): Planejar safra → Compra de insumos → Estoque; Planos agronômicos; O.S.
Fonte única: telas geradas e cálculo em JS (SAF) usam estes dados; a demanda calculada aqui (Python) espelha a do JS."""
import datetime as _dt, json
HOJE='23/09/2026'
MESES=[('2026-09','set/26'),('2026-10','out/26'),('2026-11','nov/26'),('2026-12','dez/26'),('2027-01','jan/27'),('2027-02','fev/27'),
       ('2027-03','mar/27'),('2027-04','abr/27'),('2027-05','mai/27'),('2027-06','jun/27'),('2027-07','jul/27'),('2027-08','ago/27')]
DIAS_UTEIS={'2026-09':24,'2026-10':22,'2026-11':23,'2026-12':21,'2027-01':21,'2027-02':19,'2027-03':22,'2027-04':23,'2027-05':24,'2027-06':24,'2027-07':25,'2027-08':25}
# período da safra por data de início e fim (o texto curto 'set/2026 – ago/2027' sai das datas)
_MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
def periodo_txt(ini,fim):
    a,b=ini.split('-'),fim.split('-'); mi,mf=_MES[int(a[1])-1],_MES[int(b[1])-1]
    return f'{mi} – {mf}/{b[0]}' if a[0]==b[0] else f'{mi}/{a[0]} – {mf}/{b[0]}'
SAFRAS=[
 dict(id='S2627',nome='Safra 2026/27',ini='2026-09-01',fim='2027-08-31',fazenda='Santa Rita',estado='Em planejamento',ro=False),
 dict(id='S27SF',nome='Safrinha 2027',ini='2027-02-01',fim='2027-07-31',fazenda='Santa Rita',estado='Rascunho',ro=False),
 dict(id='S2526',nome='Safra 2025/26',ini='2025-09-01',fim='2026-08-31',fazenda='Santa Rita',estado='Encerrada',ro=True),
]
for _s in SAFRAS: _s['periodo']=periodo_txt(_s['ini'],_s['fim'])
# gatilho: tipo DAP (dias após o plantio) · DAPC (dias após a colheita) · DANC (dias antes da colheita) · DATA (data do calendário)
TIPOS={'DAP':'DAP · dias após o plantio','DANC':'Dias antes da colheita','DAPC':'DAC · dias após a colheita','DATA':'Data do calendário'}
def A(id,nome,op,tipo,dias=None,data=None,prods=()):
    return dict(id=id,nome=nome,op=op,g=dict(tipo=tipo,dias=dias,data=data),prods=[dict(grupo=g,prod=p,dose=d,un=u,preco=pr) for g,p,d,u,pr in prods])
PLANOS=[
 dict(id='SOJA-AT',nome='Soja alta tecnologia',cultura='Soja',versao=6,estado='Publicado',atividades=[
   A('a1','Dessecação pré-plantio','Pulverização','DAP',-20,prods=[('Herbicidas','Glifosato 480',2.0,'L',28.0),('Herbicidas','2,4-D 806',1.0,'L',32.0),('Adjuvantes','Óleo mineral',0.5,'L',18.0)]),
   A('a2','Tratamento de sementes','Tratamento de sementes','DAP',-1,prods=[('Fungicidas','Fungicida TS',0.10,'L',210.0),('Inoculantes','Inoculante líquido',0.20,'L',45.0)]),
   A('a3','Plantio e adubação de base','Plantio','DAP',0,prods=[('Sementes','Semente de soja · variedade do cultivo',52.0,'kg',9.50),('Fertilizantes','MAP 11-52',250.0,'kg',3.90)]),
   A('a4','Adubação de cobertura','Adubação a lanço','DAP',20,prods=[('Fertilizantes','KCl 60%',120.0,'kg',2.40)]),
   A('a5','Herbicida pós-emergente','Pulverização','DAP',25,prods=[('Herbicidas','Cletodim 240',0.45,'L',62.0),('Adjuvantes','Óleo mineral',0.5,'L',18.0)]),
   A('a6','Fungicida 1ª aplicação','Pulverização','DAP',45,prods=[('Fungicidas','Fungicida A',0.50,'L',145.0),('Adjuvantes','Adjuvante espalhante',0.25,'L',22.0)]),
   A('a7','Fungicida 2ª aplicação + inseticida','Pulverização','DAP',60,prods=[('Fungicidas','Fungicida A',0.50,'L',145.0),('Inseticidas','Inseticida B',0.30,'L',95.0)]),
   A('a8','Colheita','Colheita de grãos','DAP',118)]),
 dict(id='SOJA-PD',nome='Soja padrão',cultura='Soja',versao=3,estado='Publicado',atividades=[
   A('b1','Dessecação pré-plantio','Pulverização','DAP',-15,prods=[('Herbicidas','Glifosato 480',2.0,'L',28.0)]),
   A('b2','Plantio e adubação de base','Plantio','DAP',0,prods=[('Sementes','Semente de soja · variedade do cultivo',50.0,'kg',9.50),('Fertilizantes','MAP 11-52',200.0,'kg',3.90)]),
   A('b3','Fungicida 1ª aplicação','Pulverização','DAP',50,prods=[('Fungicidas','Fungicida A',0.50,'L',145.0)]),
   A('b4','Colheita','Colheita de grãos','DAP',115)]),
 dict(id='MILHO-SF',nome='Milho safrinha',cultura='Milho',versao=4,estado='Publicado',atividades=[
   A('m1','Plantio e adubação de base','Plantio','DAP',0,prods=[('Sementes','Semente de milho · híbrido do cultivo',20.0,'kg',38.0),('Fertilizantes','MAP 11-52',180.0,'kg',3.90)]),
   A('m2','Adubação de cobertura','Adubação a lanço','DAP',25,prods=[('Fertilizantes','Ureia 45%',150.0,'kg',3.10)]),
   A('m3','Herbicida pós-emergente','Pulverização','DAP',30,prods=[('Herbicidas','Atrazina 500',3.0,'L',24.0)]),
   A('m4','Inseticida','Pulverização','DAP',55,prods=[('Inseticidas','Inseticida B',0.30,'L',95.0)]),
   A('m5','Colheita','Colheita de grãos','DAP',140)]),
 dict(id='FEIJ-PV',nome='Feijão pivô',cultura='Feijão',versao=3,estado='Publicado',atividades=[
   A('f1','Plantio e adubação de base','Plantio','DAP',0,prods=[('Sementes','Semente de feijão · variedade do cultivo',70.0,'kg',12.0),('Fertilizantes','MAP 11-52',200.0,'kg',3.90)]),
   A('f2','Fungicida','Pulverização','DAP',40,prods=[('Fungicidas','Fungicida A',0.50,'L',145.0)]),
   A('f3','Dessecação pré-colheita','Pulverização','DANC',7,prods=[('Herbicidas','Diquat 200',2.0,'L',48.0)]),
   A('f4','Colheita','Colheita de grãos','DAP',90)]),
 dict(id='CAFE-AR',nome='Café arábica produção',cultura='Café',versao=2,estado='Publicado',atividades=[
   A('k1','Adubação 1ª parcela','Adubação a lanço','DATA',data='2026-10-15',prods=[('Fertilizantes','NPK 20-05-20',300.0,'kg',3.40)]),
   A('k2','Adubação 2ª parcela','Adubação a lanço','DATA',data='2026-12-15',prods=[('Fertilizantes','NPK 20-05-20',300.0,'kg',3.40)]),
   A('k3','Fungicida para ferrugem','Pulverização','DATA',data='2027-01-20',prods=[('Fungicidas','Fungicida C',0.80,'L',120.0)]),
   A('k4','Colheita','Colheita de café','DATA',data='2027-05-20'),
   A('k5','Adubação pós-colheita','Adubação a lanço','DAPC',30,prods=[('Fertilizantes','KCl 60%',150.0,'kg',2.40)]),
   A('k6','Poda de esqueletamento','Poda','DAPC',45)]),
 dict(id='MAMAO-F',nome='Mamão Formosa produção',cultura='Mamão Formosa',versao=3,estado='Publicado',atividades=[
   A('p1','Fertirrigação de nitrogênio','Fertirrigação','DATA',data='2026-10-01',prods=[('Fertilizantes','Nitrato de cálcio',40.0,'kg',4.20)]),
   A('p2','Controle de ácaro','Pulverização','DATA',data='2026-10-15',prods=[('Inseticidas','Acaricida D',0.60,'L',180.0)]),
   A('p3','Fertirrigação de potássio','Fertirrigação','DATA',data='2026-11-01',prods=[('Fertilizantes','Nitrato de potássio',35.0,'kg',6.10)])]),
]
PLANO={p['id']:p for p in PLANOS}
def C(id,local,tipo,cultura,variedade,area,plantio,meta,un_meta,plano,colheita=None,ro=False,origem=''):
    return dict(id=id,fazenda='Santa Rita',local=local,tipo=tipo,cultura=cultura,variedade=variedade,area=area,plantio=plantio,meta=meta,un_meta=un_meta,plano=plano,colheita=colheita,ro=ro,origem=origem)
CULTIVOS={
 'S2627':[C('c1','T1-A','Parcela','Soja','58 W',160,'2026-10-15',64,'sc/ha','SOJA-AT'),
          C('c2','T1-B','Parcela','Soja','62 X',152,'2026-10-25',62,'sc/ha','SOJA-AT'),
          C('c3','T2','Talhão inteiro','Soja','58 W',298,'2026-10-18',63,'sc/ha','SOJA-AT'),
          C('c4','T4','Talhão inteiro','Soja','58 W',204,'2026-10-20',60,'sc/ha',None),
          C('c5','T3','Talhão inteiro','Soja','62 X',96,'2026-10-22',62,'sc/ha',None),
          C('c6','P1','Talhão inteiro','Soja','58 W',95,'2026-11-10',66,'sc/ha',None),
          C('c7','P2','Talhão inteiro','Soja','62 X',80,'2026-11-25',66,'sc/ha',None),
          C('c8','T7','Talhão inteiro','Mamão Formosa','Formosa',42,'2025-03-10',45,'t/ha/ano','MAMAO-F'),
          C('c9','C1','Talhão inteiro','Café','Catuaí 144',38,'2019-01-15',38,'sc/ha','CAFE-AR',colheita='2027-05-20')],
 'S27SF':[C('d1','T1-A','Parcela','Milho','Híbrido AG 8700',160,'2027-02-20',180,'sc/ha','MILHO-SF'),
          C('d2','T2','Talhão inteiro','Milho','Híbrido AG 8700',298,'2027-02-25',175,'sc/ha','MILHO-SF'),
          C('d3','P1','Talhão inteiro','Feijão','Pérola',95,'2027-04-15',50,'sc/ha','FEIJ-PV')],
 'S2526':[C('e1','T1','Talhão inteiro','Soja','58 W',312,'2025-10-12',62,'sc/ha','SOJA-AT',ro=True),
          C('e2','T2','Talhão inteiro','Soja','58 W',298,'2025-10-16',61,'sc/ha','SOJA-AT',ro=True),
          C('e3','T3','Talhão inteiro','Milho','Híbrido AG 8700',96,'2025-10-20',170,'sc/ha','MILHO-SF',ro=True),
          # lavouras em campo (Mapa, MIP e irrigação as mostram): entram na safra em que foram plantadas, com a colheita prevista informada.
          # Provisório até a decisão da S2526 encerrada com lavoura em campo (DECISOES etapa 2 §4); o serviço de ocupação lê faixa e período
          C('e4','P1','Talhão inteiro','Feijão','BRS Estilo',95,'2026-07-05',48,'sc/ha',None,colheita='2026-10-10',ro=True,origem='lavoura em campo'),
          C('e5','P2','Talhão inteiro','Milho','Híbrido AG 8700',80,'2026-08-10',180,'sc/ha',None,colheita='2026-11-15',ro=True,origem='lavoura em campo')],
}
# ajuste exclusivo já existente (T1-B: dose maior de Fungicida A na 1ª aplicação por histórico de ferrugem)
AJUSTES={'c2':{'a6|0':0.60}}
# conjuntos e rendimentos (etapa 3) — por atividade/operação e conjunto/equipe
CONJ=[
 dict(id='r1',larg=36,vel=8,efic=75,op='Pulverização',conj='Trator 02 MF 7719 + Pulverizador PJ-3030 36 m',rend=21.6,maq=180,impl=95,pess=1,pess_rs=38,prod=0,rec={'trator':1,'pulv':1,'oper':1}),
 dict(id='r2',larg=12,vel=7,efic=81,op='Plantio',conj='Trator T1 JD 6M 155 + Plantadeira 24 linhas',rend=6.8,maq=180,impl=140,pess=2,pess_rs=38,prod=0,rec={'trator':1,'plant':1,'oper':2}),
 dict(id='r3',larg=24,vel=10,efic=75,op='Adubação a lanço',conj='Trator 03 + Distribuidor 3 t',rend=18.0,maq=150,impl=45,pess=1,pess_rs=38,prod=0,rec={'trator':1,'dist':1,'oper':1}),
 dict(id='r4',op='Tratamento de sementes',conj='Máquina TSI na sede · equipe de 2',rend=40.0,maq=60,impl=0,pess=2,pess_rs=38,prod=0,rec={'oper':2}),
 dict(id='r5',larg=10,vel=6.25,efic=80,op='Colheita de grãos',conj='Colhedora Axial-Flow 7250 + trator com graneleiro',rend=5.0,maq=950,impl=120,pess=2,pess_rs=38,prod=3840,rec={'colh':1,'trator':1,'oper':2}),
 dict(id='r6',op='Colheita de café',conj='Derriçadeiras portáteis · equipe de 6',rend=0.35,maq=40,impl=0,pess=6,pess_rs=32,prod=2280,rec={'oper':6}),
 dict(id='r7',op='Poda',conj='Trator 04 + esqueletadeira',rend=1.5,maq=150,impl=60,pess=1,pess_rs=38,prod=0,rec={'trator':1,'oper':1}),
 dict(id='r8',op='Fertirrigação',conj='Sistema de gotejo T7 · 1 irrigante',rend=10.0,maq=25,impl=0,pess=1,pess_rs=32,prod=0,rec={'oper':1}),
]
def custo_h(c): return c['maq']+c['impl']+c['pess']*c['pess_rs']
# recursos (etapa 5): máquinas → capacidade = unidades × dias úteis × jornada × turnos × disponibilidade (%)
#                     pessoas  → capacidade = pessoas × dias úteis × jornada × (1 − absenteísmo %) — cada pessoa trabalha um turno
# disponibilidade mecânica: parte do tempo em que a máquina fica apta (referência ≥ 90 %); a eficiência de campo já está no rendimento
# absenteísmo: horas perdidas com faltas, atestados, afastamentos e férias
RECURSOS=[
 dict(id='trator',nome='Tratores',un=4,jornada=10,turnos=1,disp=92),
 dict(id='pulv',nome='Pulverizadores',un=1,jornada=10,turnos=1,disp=90),
 dict(id='plant',nome='Plantadeiras',un=1,jornada=10,turnos=1,disp=90),
 dict(id='dist',nome='Distribuidores',un=1,jornada=10,turnos=1,disp=95),
 dict(id='colh',nome='Colhedoras',un=1,jornada=9,turnos=1,disp=88),
 dict(id='oper',nome='Operadores e equipe',un=8,jornada=9,abs=10),
]
# estoque disponível (apto) e recebimentos previstos (pedidos em aberto) por produto — espelhados em Estoque/Compras
ESTOQUE={'Glifosato 480':1200,'2,4-D 806':300,'Óleo mineral':400,'Fungicida TS':20,'Inoculante líquido':50,
 'Semente de soja 58 W':12000,'Semente de soja 62 X':0,'MAP 11-52':90000,'KCl 60%':50000,'Cletodim 240':80,'Fungicida A':480,
 'Adjuvante espalhante':150,'Inseticida B':60,'NPK 20-05-20':8000,'Fungicida C':0,'Nitrato de cálcio':1000,'Acaricida D':10,'Nitrato de potássio':600,
 'Semente de milho AG 8700':0,'Ureia 45%':0,'Atrazina 500':0,'Semente de feijão Pérola':0,'Diquat 200':0}
RECEB={'Semente de soja 58 W':20000,'Semente de soja 62 X':8000,'KCl 60%':40000,'Fungicida A':0}
def prod_nome(p,cult):
    if 'variedade do cultivo' in p or 'híbrido do cultivo' in p:
        base=p.split(' · ')[0]
        var=cult['variedade'].replace('Híbrido ','')
        return f'{base} {var}'
    return p
def ddate(s): return _dt.date.fromisoformat(s)
def data_atividade(cult,atv):
    g=atv['g']
    if g['tipo']=='DAP': return ddate(cult['plantio'])+_dt.timedelta(days=g['dias'])
    if g['tipo']=='DATA': return ddate(g['data'])
    col=ddate(cult['colheita']) if cult.get('colheita') else None
    if col is None:  # colheita prevista pela atividade de colheita do plano
        pl=PLANO[cult['plano']]; ca=next((a for a in pl['atividades'] if a['op'].startswith('Colheita')),None)
        col=ddate(cult['plantio'])+_dt.timedelta(days=ca['g']['dias']) if ca and ca['g']['tipo']=='DAP' else ddate(cult['plantio'])
    return col+_dt.timedelta(days=(g['dias'] if g['tipo']=='DAPC' else -g['dias']))
def _ocorr_py(safra,ajustes,planos_extra):
    """Ocorrências de insumo da safra na ordem do JS (cultivo → atividade → produto): (cultivo, atividade, produto, dose, quantidade)."""
    for c in CULTIVOS[safra]:
        pid=(planos_extra or {}).get(c['id'],c['plano'])
        if not pid: continue
        for a in PLANO[pid]['atividades']:
            for i,p in enumerate(a['prods']):
                dose=ajustes.get(c['id'],{}).get(f"{a['id']}|{i}",p['dose'])
                yield c,a,p,dose,dose*c['area']
def demanda(safra,ajustes=None,planos_extra=None,osd=None,cen=None):
    """Demanda por insumo e necessidade líquida por data (CAL-01) — espelho de demFazenda (cal01.js), a conta única do Planejar safra (passo=demanda)
    e do Mapa › Insumos; a Compra de insumos lê esta (CTL-4, DEM-01..07). estoque = físico apto da fazenda da safra (inclui reservas);
    receb = recebimentos previstos da fazenda; bruta = usos desta safra de hoje em diante (plano sem a parte coberta por O.S. + pendente das O.S.);
    real = uso do plano antes de hoje sem O.S. (fora da demanda, DEM-06); plano = plano sem a parte coberta, todas as datas.
    osd: ordens (os_dem); cen: o cenário inteiro (ordens e estoque, como as telas) — os testes passam um cenário alterado."""
    m=dem_fazenda(dict(dem_entradas(safra,ajustes,planos_extra,cen),osd=(os_dem(cen) if osd is None else osd)))
    for o in m.values(): o.update(estoque=o['est'],reservado=o['res'],receb=o['rec'])
    return m
# ---- Fazenda Lagoa Grande (dados_lagoa_safra.py): safra de mamão nos 23 pivôs reais, planos, conjuntos e estoque ----
import dados_lagoa_safra as _DL
_DL.SAFRA['periodo']=periodo_txt(_DL.SAFRA['ini'],_DL.SAFRA['fim']); SAFRAS.append(_DL.SAFRA); CULTIVOS[_DL.SAFRA['id']]=_DL.CULTIVOS; PLANOS.extend(_DL.PLANOS); PLANO.update({p['id']:p for p in _DL.PLANOS}); CONJ.extend(_DL.CONJ)
EST_FAZ={'Santa Rita':dict(ESTOQUE),'Lagoa Grande':dict(_DL.ESTOQUE)}   # DEM-07: o físico de cada fazenda (ESTOQUE junta os dois para as telas de estoque)
ESTOQUE.update(_DL.ESTOQUE); RECEB.update(_DL.RECEB)
# ---- REND-MULTICONJUNTOS-20261003 · configurações por atividade (etapa 3 · Defina os rendimentos) e espelho do cálculo da etapa 4 ----
# diesel por hora de conjunto (L/h, estimativa da fazenda; vazio = não informado). Só estima litros pelas horas: o custo do combustível
# já está no custo por hora da máquina e não é cobrado de novo.
DIESEL_LH={'r1':14,'r2':16,'r3':10,'r5':30,'r7':7,'r9':8,'r11':6}
for _c in CONJ: _c.setdefault('diesel',DIESEL_LH.get(_c['id'],''))
# configurações extras por safra: a mesma atividade divide a área entre conjuntos de tamanhos, rendimentos e tarifas diferentes.
# Safra 2026/27: o plantio da fazenda (plantadeira 24 linhas, 6,8 ha/h) mais um prestador com plantadeira de 12 linhas (6 m × 6,5 km/h × 75 %
# = 2,925 ha/h) a R$ 320/h com trator, operador e diesel; o prestador não usa máquinas nem pessoas da fazenda (rec vazio).
CFG_EXTRA={'S2627':[dict(id='x1',op='Plantio',conj='Prestador · plantadeira 12 linhas (6 m)',conj_id='prestador',larg=6,vel=6.5,efic=75,
                         maq=320,impl=0,pess=0,pess_rs=0,diesel='',prod=0,rec={})]}
def rend_calc(larg,vel,efic): return larg*vel/10*efic/100      # ha/h = m × km/h ÷ 10 × eficiência; sem arredondar
for _l in CFG_EXTRA.values():
    for _e in _l:
        if _e.get('larg'): _e['rend']=rend_calc(_e['larg'],_e['vel'],_e['efic'])   # informativo; a etapa 3 usa rend_efetivo
def cfgs_rend(safra,op,atv=None):
    """Configurações de uma atividade numa safra: o conjunto padrão da operação (primeiro de CONJ) + as extras da safra (todas as atividades
    da operação, ou só a atividade indicada em 'atv')."""
    base=next((c for c in CONJ if c['op']==op),None)
    return ([dict(base)] if base else [])+[dict(e) for e in CFG_EXTRA.get(safra,[]) if e['op']==op and e.get('atv') in (None,atv)]
def rend_efetivo(c):
    """Rendimento da configuração na etapa 3: pelos parâmetros (largura × velocidade × eficiência) quando há largura; senão o informado."""
    return rend_calc(c['larg'],c['vel'],c['efic']) if c.get('larg') else c.get('rend')
def cfg_in(c):
    """Configuração no formato de repartir (o mesmo de cfgIn em safra.js). O prestador traz a equipe dele: não conta horas-homem da fazenda."""
    return dict(id=c.get('id'),nome=c.get('conj'),rend=rend_efetivo(c),part=c.get('part',''),jan=c.get('jan',''),custo_h=custo_h(c),diesel=c.get('diesel',''),
                pess=0 if c.get('conj_id')=='prestador' else c.get('pess'),seq=c.get('seq')=='Em sequência: divide trator, implemento ou operador',troca=c.get('troca',''),ativos=c.get('ativos',[]),rec=c.get('rec') or {})
# >>> REPARTIR (espelho de safra.js · repartir; mesmas regras e mesma ordem; aceita Fraction para conferir sem arredondamento)
# 1) junta quem trabalha em sequência antes de dividir a área; em sequência, cada uma termina dentro da própria janela (prazo do início da
#    ocorrência; a janela maior de outra não amplia a dela, D-01); começa a de menor troca e cada outra entra com a sua troca (PRD 44.3)
# 2) % fixos primeiro; o resto às sem % na proporção do rendimento (as mesmas horas); cada uma para na própria janela e a sequência para
#    quando as horas dela com as trocas enchem a janela; o que não cabe fica sem conjunto. Pendente diz a causa.
# 3) REND-RETORNO-1818 (S5): PLANO (demanda inteira pela partilha, sem janela) → necessidade da sequência e déficit; ATENDIDO (janelas);
#    SALDO (área sem conjunto + horas que faltam pelas premissas do plano). nec = atendido + saldo em ha e em horas-conjunto.
import math as _math
def _r2(x): return _math.floor(float(x or 0)*100+0.5)/100   # espelho de calR2 (cal01.js): Math.round(x*100)/100
from fractions import Fraction as _Fr
_RP_DEC=__import__('re').compile(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')
def _rp_num(x):   # igual a safra.js rpNum: decimal simples com vírgula ou ponto; vazio (ou só espaço) = sem valor
    if x is None: return None
    if isinstance(x,bool): return _math.nan
    if isinstance(x,(int,float,_Fr)): return x if not (isinstance(x,float) and (_math.isnan(x) or _math.isinf(x))) else _math.nan
    t=str(x).strip().replace(',','.',1)
    if t=='': return None
    if not _RP_DEC.fullmatch(t): return _math.nan
    n=float(t); return n if not (_math.isnan(n) or _math.isinf(n)) else _math.nan
def _ok(n): return n is not None and not (isinstance(n,float) and _math.isnan(n))
def _rp_f(n):
    v=_math.floor(float(n)*100+0.5)/100
    return (str(int(v)) if v==int(v) else repr(v)).replace('.',',')
def repartir(Q,cfgs,pools=None):
    mot=[]; mot_s=set()
    def add(m):
        if m not in mot_s: mot_s.add(m); mot.append(m)
    Q=_rp_num(Q)
    if not _ok(Q) or Q<0: add('área inválida'); Q=0
    PV=[(k,pv or {},_rp_num((pv or {}).get('un'))) for k,pv in (pools or {}).items()]; PV=[z for z in PV if _ok(z[2]) and z[2]>=0]   # grupos com unidades válidas
    it=[]
    for i,c in enumerate(cfgs or []):
        r,p,H,ch,d,tr,pe=(_rp_num(c.get(k)) for k in ('rend','part','jan','custo_h','diesel','troca','pess'))
        x=dict(i=i,id=c.get('id'),nome=c.get('nome') or f'Configuração {i+1}',r=r if _ok(r) and r>0 else None,p=p if _ok(p) and p>=0 else None,
               H=_math.inf if (H is None or not _ok(H) or H<0) else H,ch=ch if _ok(ch) and ch>=0 else None,d=d if _ok(d) and d>=0 else None,
               troca=tr if _ok(tr) and tr>0 else 0,pess=pe if _ok(pe) and pe>0 else 0,seq=bool(c.get('seq')),ativos=[a for a in (c.get('ativos') or []) if a],
               rec=c.get('rec') or {},t=0,q=0,h=0,ht=0,custo=None,diesel=None,emSeq=False,seqEst=False,grupo=i)
        if H is not None and (not _ok(H) or H<0): add(x['nome']+': janela inválida, considerada sem limite')
        x['Hin']=x['H']; fr=next((z for z in PV if 0<(_rp_num(x['rec'].get(z[0])) or 0) and (_rp_num(x['rec'].get(z[0])) or 0)>z[2]+1e-9),None)   # sozinha precisa de mais unidades: não trabalha
        if fr: x['H']=0; x['semRec']=True; add(f"{x['nome']}: precisa de {_rp_f(_rp_num(x['rec'].get(fr[0])))} em {fr[1].get('nome') or fr[0]}, a fazenda tem {_rp_f(fr[2])}; não trabalha nesta ocorrência")
        it.append(x)
    fx=[x for x in it if x['p'] is not None]; sp=sum((x['p'] for x in fx),0); esc=100/sp if sp>100 else 1
    if sp>100+1e-9: add(f'partes fixas somam {_rp_f(sp)} %: reduzidas na proporção para fechar 100 %')
    R=Q
    for x in fx: x['t']=Q*x['p']*esc/100; R-=x['t']
    if R<=1e-9*max(1,Q): R=0   # tolerância relativa à área (PRE-REV R3)
    livres=[x for x in it if x['p'] is None]; liv_ok=len(livres)>0 and not any(x['r'] is None for x in livres)
    # no plano / recebem área; fecho de quem trabalha em sequência (decorrido); uma restrição de janela por recurso físico (PRE-REV), como no safra.js
    liv_h=[x for x in livres if x['H']>0]; plan_liv=liv_h if liv_h else livres
    cand_p=[x for x in it if x['r'] is not None and ((x['t']>1e-12) if x['p'] is not None else (liv_ok and R>0 and any(y is x for y in plan_liv)))]
    cand=[x for x in cand_p if x['H']>0]
    class _UF:
        def __init__(s): s.pai=list(range(len(it)))
        def raiz(s,i):
            while s.pai[i]!=i: s.pai[i]=s.pai[s.pai[i]]; i=s.pai[i]
            return i
        def une(s,a,b):
            a,b=s.raiz(a),s.raiz(b)
            if a!=b: s.pai[max(a,b)]=min(a,b)
    U=_UF(); UP=_UF(); raiz=U.raiz   # U: quem recebe área; UP: o plano
    for xs,V in ((cand,U),(cand_p,UP)):
        for a,x in enumerate(xs):
            for y in xs[a+1:]:
                if any(z in y['ativos'] for z in x['ativos']): V.une(x['i'],y['i'])
        sq=[x for x in xs if x['seq']]
        for x in sq: V.une(sq[0]['i'],x['i'])
    if any(any(z in y['ativos'] for z in x['ativos']) for a,x in enumerate(cand) for y in cand[a+1:]): add('configurações com a mesma máquina do cadastro trabalham em sequência')
    if len([x for x in cand if x['seq']])>1: add('sequência declarada: dividem trator, implemento ou operador')
    RS=[]; sq_p=[x for x in cand_p if x['seq']]
    if len(sq_p)>1: RS.append(('sq',sq_p,[x for x in sq_p if x['H']>0]))
    ats=[]
    for x in cand_p:
        for z in x['ativos']:
            if z not in ats: ats.append(z)
    for z in ats:
        xs=[x for x in cand_p if z in x['ativos']]
        if len(xs)>1: RS.append(('at:'+str(z),xs,[x for x in xs if x['H']>0]))
    um=[z[0] for z in PV if z[2]<=1]; SERp=[]; SERa=[]   # grupo de 1 unidade: uma máquina só; SERp/SERa: grupos de 2+ que serializam no plano / na divisão (W2)
    def junto(x,y,fora=None): return (x['seq'] and y['seq']) or any(z in y['ativos'] for z in x['ativos']) or any(k!=fora and (_rp_num(x['rec'].get(k)) or 0)>0 and (_rp_num(y['rec'].get(k)) or 0)>0 for k in um)   # fora: o grupo cujo pico se mede (B5a)
    def simul(us,k,un,pare):   # maior uso simultâneo: conjunto independente de peso máximo por componente, cota por cobertura de cliques, teto; (valor, estouro) como no safra.js (W3)
        W0=[_rp_num(x['rec'].get(k)) or 0 for x in us]; n=len(us); tot=sum(W0,0)
        if tot<=un+1e-9: return tot,False
        J=[[a!=b and junto(us[a],us[b],k) for b in range(n)] for a in range(n)]; vis=[False]*n; soma=0; est=False
        def cota(P):   # P em peso decrescente: o 1º de cada clique é o maior
            ub=0; r=list(P)
            while r:
                c=[r.pop(0)]; j=0
                while j<len(r):
                    if all(J[u][r[j]] for u in c): c.append(r.pop(j))
                    else: j+=1
                ub+=W0[c[0]]
            return ub
        for s0 in range(n):
            if vis[s0]: continue
            cp=[]; pl0=[s0]; vis[s0]=True
            while pl0:
                a=pl0.pop(); cp.append(a)
                for b in range(n):
                    if not vis[b] and J[a][b]: vis[b]=True; pl0.append(b)
            cp.sort(key=lambda i:(-W0[i],i)); st=dict(best=0,passos=0,estouro=False,passou=False)
            def vai(P,s_):
                st['passos']+=1
                if st['passos']>65536: st['estouro']=True; return
                if s_>st['best']: st['best']=s_
                if pare and soma+st['best']>un+1e-9: st['passou']=True; return
                if not P or s_+cota(P)<=st['best']: return
                v=P[0]
                vai([u for u in P if u!=v and not J[v][u]],s_+W0[v])
                if st['estouro'] or st['passou']: return
                vai(P[1:],s_)
            vai(cp,0)
            if st['estouro']: est=True; soma+=sum((W0[i] for i in cp),0)
            else: soma+=st['best']
            if pare and soma>un+1e-9: return soma,est
        return soma,est
    for k,pv in (pools or {}).items():
        un=_rp_num((pv or {}).get('un'))
        if not _ok(un) or un<0: continue
        u_p=[x for x in cand_p if not x.get('semRec') and (_rp_num(x['rec'].get(k)) or 0)>0]; u_a=[x for x in u_p if x['H']>0]   # sem recurso já tem o motivo
        s_a,e_a=simul(u_a,k,un,True) if len(u_a)>1 else (0,False); s_p,e_p=simul(u_p,k,un,True) if len(u_p)>1 else (0,False)
        ea=len(u_a)>1 and (un<=1 or s_a>un+1e-9); ep=len(u_p)>1 and (un<=1 or s_p>un+1e-9)   # 1 unidade: uma máquina só, como um ativo
        if ea:
            for x in u_a: U.une(u_a[0]['i'],x['i'])
        if ep:
            for x in u_p: UP.une(u_p[0]['i'],x['i'])
        if ea or ep:
            RS.append(('pl:'+str(k),u_p if ep else [],u_a if ea else []))
            if not un<=1:
                if ep and k not in SERp: SERp.append(k)
                if ea and k not in SERa: SERa.append(k)
            sm,es=simul(u_a if ea else u_p,k,un,False); dp=(s_a>un+1e-9 and not e_a) if ea else (s_p>un+1e-9 and not e_p)   # dp: a decisão achou mais do que un sem estourar
            nome=f"{pv.get('nome') or k}"
            if es: add(nome+(f": ao mesmo tempo precisariam de mais do que as {_rp_f(un)} da fazenda; configurações consideradas em sequência nesta estimativa" if dp else ": combinações demais para conferir quantas trabalham ao mesmo tempo; configurações consideradas em sequência nesta estimativa (conservador)"))
            else: add(nome+(f": ao mesmo tempo precisariam de {_rp_f(sm)}, a fazenda tem {_rp_f(un)}"+('; trabalham uma de cada vez' if (un<=1 or all((_rp_num(x['rec'].get(k)) or 0)+(_rp_num(y['rec'].get(k)) or 0)>un+1e-9 for i_,x in enumerate(u_a if ea else u_p) for y in (u_a if ea else u_p)[i_+1:])) else '; configurações consideradas em sequência nesta estimativa') if sm>un+1e-9 else f": a fazenda tem {_rp_f(un)}; quem a usa divide a janela dela"))
    # cortes por prazo de cada clique maximal do grafo "nunca ao mesmo tempo" (D-01); grafo não perfeito entre quem tem janela (buraco ímpar de
    # 5+ no grafo ou no complemento), cliques ou cortes demais, ou busca acima do teto: só esse componente no conservador (como no safra.js)
    def exclui(x,y,S): return junto(x,y) or any((_rp_num(x['rec'].get(k)) or 0)>0 and (_rp_num(y['rec'].get(k)) or 0)>0 for k in S)
    def buraco(cs,A):   # ciclo induzido com número ímpar (5+) de vértices: True, False ou None (passou do teto)
        st=dict(passos=0)
        def ext(c,v0):
            st['passos']+=1
            if st['passos']>65536: return None
            u=c[-1]
            for w in cs:
                if w<=v0 or not A[u][w] or w in c: continue
                if any(A[c[i]][w] for i in range(1,len(c)-1)): continue
                if len(c)>1 and A[v0][w]:
                    if len(c)>=4 and len(c)%2==0: return True
                    continue
                c.append(w); r=ext(c,v0); c.pop()
                if r is not False: return r
            return False
        for v0 in cs:
            r=ext([v0],v0)
            if r is not False: return r
        return False
    def grafo(V,pref,S):
        n=len(V)
        if n<2: return
        adj=[[a!=b and exclui(V[a],V[b],S) for b in range(n)] for a in range(n)]; cl=[]; fc=[]
        def cortes(xs,tipo,out,visto):   # cortes por prazo de um grupo (D-01, 5983640246): quem tem janela ≤ t cabe em t; sem repetir; sub: prazo menor
            for t_ in sorted({x['H'] for x in xs if x['H']!=_math.inf}):
                st=[x for x in xs if x['H']<=t_]
                if len(st)<2: continue
                k=pref+tipo+':'+','.join(str(x['i']) for x in st)+'@'+str(t_)
                if k in visto: continue
                visto.add(k); out.append((k,st,t_,len(st)<len(xs)))
        vis=[False]*n
        for s0 in range(n):
            if vis[s0]: continue
            comp=[]; pilha=[s0]; vis[s0]=True
            while pilha:
                a=pilha.pop(); comp.append(a)
                for b in range(n):
                    if adj[a][b] and not vis[b]: vis[b]=True; pilha.append(b)
            comp.sort()
            if len(comp)<2: continue
            cc=[]; st=dict(passos=0,est=False)
            def bk(R_,P,X):
                if st['est']: return
                st['passos']+=1
                if st['passos']>65536 or len(cc)>4096: st['est']=True; return
                if not P and not X:
                    if len(R_)>1: cc.append(sorted(R_))
                    return
                u=(P+X)[0]
                for v in [v for v in P if not adj[u][v]]:
                    bk(R_+[v],[w for w in P if adj[v][w]],[w for w in X if adj[v][w]])
                    if st['est']: return
                    P=[w for w in P if w!=v]; X=X+[v]
            bk([],list(comp),[]); est=st['est']
            if not est:   # teto de cortes deste componente
                nc=[]; v0=set()
                for c in cc:
                    cortes([V[i] for i in c],'cq',nc,v0)
                    if len(nc)>8192: est=True; break
            imp=est
            if not est:
                cl.extend(cc); cf0=[i for i in comp if V[i]['H']!=_math.inf]   # só quem tem janela (R2-2)
                fin=[i for i in cf0 if V[i]['H']>0]; dl=[]
                for i in fin:
                    if V[i]['H'] not in dl: dl.append(V[i]['H'])
                cliq=all(adj[a][b] for k,a in enumerate(fin) for b in fin[k+1:])
                def p4():   # P4 induzido entre quem tem prazo, como no safra.js
                    return any(c!=b and adj[b][c] and any(a!=c and adj[a][b] and not adj[a][c] and any(d!=b and d!=a and adj[c][d] and not adj[b][d] and not adj[a][d] for d in fin) for a in fin) for b in fin for c in fin)
                if not cliq and len(dl)>1 and p4():   # R3-1: prazos diferentes sem exclusão total entre quem tem prazo: conservador do componente
                    imp=True; add('prazos diferentes em recursos compartilhados: as configurações ligadas são consideradas juntas em cada janela nesta estimativa (conservador)')
                elif not cliq:
                    h=buraco(cf0,adj)
                    if h is False: h=buraco(cf0,[[a!=b and not adj[a][b] for b in range(n)] for a in range(n)])
                    if h is not False: imp=True
                    if h is None: est=True
                    elif h: add('arranjo de recursos compartilhados que esta estimativa não confere exatamente: as configurações ligadas são consideradas juntas em cada janela (conservador)')
            if est: add('combinações demais para conferir quem trabalha ao mesmo tempo: as configurações ligadas são consideradas juntas em cada janela nesta estimativa (conservador)')
            if imp: fc.append(comp)
        cl.sort()
        cc=[]; vc=set()
        for c in cl: cortes([V[i] for i in c],'cq',cc,vc)
        cf=[]; vf=set()
        for c in fc: cortes([V[i] for i in c],'fc',cf,vf)
        for k,st,t_,sub in cc+cf: RS.append((k,st if pref=='p' else [],st if pref=='a' else [],t_,sub))
    grafo([x for x in cand_p if not x.get('semRec')],'p',SERp); grafo(cand,'a',SERa)
    def troca_de(xs):
        if len(xs)<2: return 0
        return sum((x['troca'] for x in xs),0)-min(x['troca'] for x in xs)
    def troca_r(xs,P,V):   # a troca que o decorrido cobra: a de cada membro, menos a menor troca do fecho se um membro a tem
        if len(xs)<2: return 0
        g=V.raiz(xs[0]['i']); mn=min((y['troca'] for y in P if V.raiz(y['i'])==g),default=_math.inf)
        return sum((x['troca'] for x in xs),0)-(mn if any(x['troca']==mn for x in xs) else 0)
    def troca_quem(xs,P,V):   # quem tem a troca reservada: todos com troca, menos uma com a menor troca do fecho (a que começa) — regra (a)
        g=V.raiz(xs[0]['i']); mn=min((y['troca'] for y in P if V.raiz(y['i'])==g),default=_math.inf); out=[]; tirou=False
        for x in xs:
            if not tirou and x['troca']==mn: tirou=True; continue
            if x['troca']>0: out.append(x['nome'])
        return out
    # origem (sequência declarada, mesma máquina, recurso da fazenda ou mista) e estimativa (par que só se exclui por grupo de 2+ que serializa)
    def pool_nome(k): return ((pools or {}).get(k) or {}).get('nome') or k
    def _par_excede(x,y):
        for z in PV:
            a=_rp_num(x['rec'].get(z[0])) or 0; b=_rp_num(y['rec'].get(z[0])) or 0
            if a>0 and b>0 and a+b>z[2]+1e-9: return True
        return False
    JM=[[x is not y and (junto(x,y) or _par_excede(x,y)) for y in it] for x in it]   # sequência de fato (inclui par que sozinho passa das unidades)
    def est_de(k,ms):
        if k=='sq' or k.startswith('at:'): return False
        return any(not JM[x['i']][y['i']] for a,x in enumerate(ms) for y in ms[a+1:])
    def nomes(xs):
        n=[x['nome'] for x in xs]
        if len(n)>4: return ', '.join(n[:3])+' e mais '+str(len(n)-3)
        return ', '.join(n[:-1])+' e '+n[-1] if len(n)>1 else ''.join(n)
    def origens(ms):   # todas as origens comuns (R3-4)
        o=[]
        if all(x['seq'] for x in ms): o.append('sq')
        for a in ms[0]['ativos']:
            if all(a in x['ativos'] for x in ms) and 'at:'+str(a) not in o: o.append('at:'+str(a))
        for pk in (pools or {}):
            if (pk in um or pk in SERp or pk in SERa) and all((_rp_num(x['rec'].get(pk)) or 0)>0 for x in ms): o.append('pl:'+str(pk))
        return o
    W={}; jan={}; pista={}; pista_a={}; TRC={}; SUB={}; MS={}; EC={}
    def EST(k):   # só para quem vira motivo
        if k not in EC: EC[k]=est_de(k,MS[k])
        return EC[k]
    for r_ in RS:
        k,xs,xa=r_[:3]
        w=r_[3] if len(r_)>3 else max((x['H'] for x in xs+xa),default=-_math.inf)   # corte por prazo: janela t
        if w==_math.inf or w==-_math.inf: continue
        W[k]=w; MS[k]=xs if len(xs)>1 else xa; SUB[k]=bool(r_[4]) if len(r_)>4 else False
        if len(xs)>1: pista[k]=xs
        if len(xa)>1:
            pista_a[k]=xa; tr=troca_r(xa,cand,U); jan[k]=w-tr
            if tr>1e-12: TRC[k]=troca_quem(xa,cand,U)
    PL={}
    for g in jan:
        for y in pista_a[g]: PL.setdefault(y['i'],[]).append(g)
    def pl(x): return PL.get(x['i'],[])   # restrições de janela da divisão de uma configuração (indexadas, W4)
    def aloca(ad):
        q=[0]*len(it); saldo=0; cz={}; uso={}; liga={}
        for x in fx:
            t=x['t']
            if t<=1e-12: continue
            if x['r'] is None: saldo+=t; cz['rend']=1; ad(x['nome']+': sem rendimento válido (ha/h), a parte dela fica sem conjunto'); continue
            q[x['i']]=min(t,x['r']*x['H'])
            if t-q[x['i']]>1e-9:
                saldo+=t-q[x['i']]
                if x.get('semRec'): cz['rec']=1
                else: cz['jan']=1; ad(f"{x['nome']}: a parte fixa não cabe na janela de {_rp_f(x['H'])} h")
        cab=q[:]; cortes=[]   # o que cabia na própria janela; o motivo diz a fração final, depois de todas as restrições
        for g in [g for g in jan if not SUB[g]]+[g for g in jan if SUB[g]]:   # o grupo inteiro reduz primeiro; subgrupo só o que ainda passar (R2-3)
            xs=[x for x in pista_a[g] if x['p'] is not None and q[x['i']]>0]; hf=sum((q[x['i']]/x['r'] for x in xs),0); B=max(0,jan[g])
            if hf>B+1e-9:
                f=B/hf
                for x in xs: n=q[x['i']]*f; saldo+=q[x['i']]-n; q[x['i']]=n
                cz['seq']=1; cortes.append(g); liga[g]=1
        pf_g={}; pf_o=[]   # um motivo por grupo e janela: a restrição da menor fração final (R2-4)
        for g in cortes:
            fs=[q[x['i']]/cab[x['i']] for x in pista_a[g] if x['p'] is not None and cab[x['i']]>0]; mn,mx=min(fs),max(fs)
            r0=(raiz(pista_a[g][0]['i']),W[g])
            if r0 not in pf_g: pf_g[r0]=[g,mn,mx]; pf_o.append(pf_g[r0])
            elif mn<pf_g[r0][1]-1e-9: pf_g[r0][:]=[g,mn,mx]
        for g,mn,mx in pf_o:
            ad(f"as partes fixas {'consideradas em sequência nesta estimativa' if EST(g) else 'em sequência'} não cabem na janela de {_rp_f(W[g])} h: "+(f'cada uma faz {_rp_f(mn*100)} %' if mx-mn<=1e-9 else f'fazem de {_rp_f(mn*100)} % a {_rp_f(mx*100)} %')+' do que cabia na própria janela ('+nomes([x for x in pista_a[g] if x['p'] is not None and cab[x['i']]>0])+')')
        for g in jan: uso[g]=sum((q[x['i']]/x['r'] for x in pista_a[g] if x['p'] is not None),0)   # depois de todas as restrições
        if R>0:
            if not livres:
                saldo+=R
                if it: cz['part']=1
                else: cz['cfg']=1
                ad('as partes fixas não cobrem toda a área' if it else 'atividade sem conjunto')
            elif not liv_ok:
                saldo+=R; cz['rend']=1
                for x in livres:
                    if x['r'] is None: ad(x['nome']+': sem rendimento válido (ha/h); '+('a divisão pelo rendimento fica pendente' if len(livres)>1 else 'horas pendentes'))
            else:
                rest=R; at=livres[:]; bj=False; bs=False; bs_f=False; br=False; lg={}
                while at:
                    sr=sum(x['r'] for x in at); T=rest/sr; e=T
                    for x in at:
                        if x['H']<e: e=x['H']
                    na={}; tl={}
                    for x in at:
                        for g in pl(x): na[g]=na.get(g,0)+1
                    for g in na:
                        tl[g]=max(0,jan[g]-uso.get(g,0))/na[g]
                        if tl[g]<e: e=tl[g]
                    if not e<T:
                        for x in at: q[x['i']]=x['r']*T
                        rest=0; break
                    fz=[x for x in at if x['H']<=e or any(tl[g]<=e for g in pl(x))]
                    for x in fz:
                        q[x['i']]=x['r']*e; rest-=q[x['i']]
                        for g in pl(x):
                            uso[g]=uso.get(g,0)+e
                            if tl[g]<=e:
                                bs=True; lg[g]=1
                                if not bs_f and not EST(g): bs_f=True
                        if x['H']<=e:
                            if x.get('semRec'): br=True
                            else: bj=True
                    fzi={x['i'] for x in fz}; at=[x for x in at if x['i'] not in fzi]
                if rest>1e-9:   # o motivo da troca só quando sobra área (empate de ponto flutuante)
                    saldo+=rest
                    for g in lg: liga[g]=1
                    if bs: cz['seq']=1; ad(('em sequência' if bs_f else 'consideradas em sequência nesta estimativa,')+' dividem a mesma janela: a área que não cabe fica sem conjunto')
                    if bj or (not bs and not br): cz['jan']=1; ad('as janelas não comportam toda a área')
                    if br: cz['rec']=1
        tc_g={}; tc_o=[]   # regra (a): a troca reservada fica (conservadora); um motivo por grupo e janela (R2-4)
        for g in liga:
            ns=TRC.get(g)
            if not ns: continue
            if jan[g]<=1e-9: cz['troca']=1
            v=(1 if jan[g]<=1e-9 else 0,W[g]-jan[g])
            r0=(raiz(pista_a[g][0]['i']),W[g])
            if r0 not in tc_g: tc_g[r0]=[g,v]; tc_o.append(tc_g[r0])
            elif v[0]>tc_g[r0][1][0] or (v[0]==tc_g[r0][1][0] and v[1]>tc_g[r0][1][1]+1e-9): tc_g[r0][:]=[g,v]
        for g,_v in tc_o:
            ns=TRC[g]
            quem=', '.join(ns); os_=origens(pista_a[g])
            rot=lambda o: 'sequência declarada' if o=='sq' else ('mesma máquina do cadastro' if o.startswith('at:') else pool_nome(o[3:])+' da fazenda')
            rs=[]
            for o_ in os_:
                if rot(o_) not in rs: rs.append(rot(o_))
            de=' e '.join(rs); o=os_[0] if len(os_)==1 else ''
            aj=f'tire {quem} da sequência declarada' if o=='sq' else (f'use outro conjunto para {quem}' if o.startswith('at:') else (f'tenha mais {pool_nome(o[3:])} na fazenda' if o.startswith('pl:') else f'separe {quem} das outras ('+(de or 'sequência declarada, mesma máquina ou recurso da fazenda')+')'))
            ori=(de+(', em sequência nesta estimativa' if EST(g) else '')) if de else ('em sequência nesta estimativa' if EST(g) else 'em sequência')
            ad(f"{quem}: troca de {_rp_f(W[g]-jan[g])} h reservada na janela de {_rp_f(W[g])} h de {nomes(pista_a[g])} ({ori}); para liberar horas, reduza a troca ou {aj}")
        return q,saldo,cz
    q2,saldo,cz=aloca(add)
    for x in it: x['q']=q2[x['i']]
    # PLANO: demanda inteira pela partilha do usuário, sem janela (parte fixa inteira; resto pelo rendimento) → necessidade da sequência e déficit
    q1=[0]*len(it)
    for x in fx:
        if x['r'] is not None and x['t']>1e-12: q1[x['i']]=x['t']
    if R>0 and liv_ok:
        sr=sum(x['r'] for x in plan_liv)
        for x in plan_liv: q1[x['i']]=x['r']*R/sr
    # conflito (R3-2): fato e estimativa separados, como no safra.js
    st_c=dict(conflito=False,deficit=0,cf_f=False); cf_g={}; cf_o=[]
    P1=[x for x in cand_p if q1[x['i']]>1e-12]
    def viol(xs,t,est,g):
        if len(xs)<2: return
        nec=sum((q1[x['i']]/x['r'] for x in xs),0)+troca_r(xs,P1,UP)
        if not nec>t+1e-9: return
        st_c['conflito']=True; d=nec-t
        if g is not None: st_c['deficit']=max(st_c['deficit'],d)
        if not est: st_c['cf_f']=True
        r0=UP.raiz(xs[0]['i'])
        if r0 not in cf_g: cf_g[r0]=dict(f=None,e=None,n=0); cf_o.append(r0)
        c=cf_g[r0]
        if g is not None: c['n']+=1
        k='e' if est else 'f'
        if c[k] is None or d>c[k]['d']+1e-9: c[k]=dict(xs=xs,nec=nec,d=d,t=t)
    for g in pista: viol([x for x in pista[g] if q1[x['i']]>1e-12],W[g],EST(g),g)
    ns=[x for x in P1 if not x.get('semRec')]; cl_f=[]; ps=[0]
    def bk_f(R_,P,X):
        ps[0]+=1
        if ps[0]>65536 or len(cl_f)>4096: return
        if not P and not X:
            if len(R_)>1: cl_f.append(R_)
            return
        u=(P+X)[0]
        for v in [v for v in P if not JM[ns[u]['i']][ns[v]['i']]]:
            bk_f(R_+[v],[w for w in P if JM[ns[v]['i']][ns[w]['i']]],[w for w in X if JM[ns[v]['i']][ns[w]['i']]]); P=[w for w in P if w!=v]; X=X+[v]
    if len(ns)>1: bk_f([],list(range(len(ns))),[])
    for c_ in cl_f:
        xs=[ns[k] for k in c_]; ts=[]
        for x in xs:
            if x['H']!=_math.inf and x['H'] not in ts: ts.append(x['H'])
        for t in ts: viol([x for x in xs if x['H']<=t],t,False,None)
    conflito=st_c['conflito']; deficit=st_c['deficit']; cf_f=st_c['cf_f']
    for r0 in cf_o:
        c=cf_g[r0]; ms=[]
        if c['f']: ms.append((c['f'],False))
        if c['e'] and (not c['f'] or c['e']['d']>c['f']['d']+1e-9): ms.append((c['e'],True))
        mais=c['n']-len(ms)
        for k,(v,est) in enumerate(ms):
            add(nomes(v['xs'])+(': consideradas em sequência nesta estimativa, precisam de ' if est else ': em sequência precisam de ')+f"{_rp_f(v['nec'])} h para {_rp_f(sum((q1[x['i']] for x in v['xs']),0))} ha; a janela tem {_rp_f(v['t'])} h"
                +((' (e mais '+str(mais)+(' combinações que também não cabem)' if mais>1 else ' combinação que também não cabe)')) if k==len(ms)-1 and mais>0 else ''))
    grp={}
    for x in it:
        if x['q']>1e-12: grp.setdefault(raiz(x['i']),[]).append(x)
    UI=_UF()   # sequência de fato (sequência declarada, mesma máquina, grupo de 1 unidade)
    for a,x in enumerate(cand):
        for y in cand[a+1:]:
            if JM[x['i']][y['i']]: UI.une(x['i'],y['i'])
    decorrido=0; troca_t=0
    for g in sorted(grp):
        xs=grp[g]; soma=0; mn=min(x['troca'] for x in xs)
        em_r=lambda x: any(any(y is x for y in pista_a[k]) for k in jan)
        ini=next((x for x in xs if x['troca']==mn and em_r(x)),None) or next(x for x in xs if x['troca']==mn)   # no empate, a que divide janela
        for x in xs:
            x['h']=x['q']/x['r']; tr=0
            if len(xs)>1 and x is not ini: tr=x['troca']
            x['ht']=x['h']+tr; troca_t+=tr; x['emSeq']=len(xs)>1; x['seqEst']=x['emSeq'] and not any(y is not x and UI.raiz(y['i'])==UI.raiz(x['i']) for y in xs); x['grupo']=g; soma+=x['ht']
        if soma>decorrido: decorrido=soma
    for x in it:
        if x['q']<=1e-12: x['grupo']=raiz(x['i'])
    hc=0; custo=0; custo_ok=True; diesel=0; diesel_ok=True; hh=0
    for x in it:
        if x['q']<=1e-12:
            x['q']=0; x['h']=0; x['ht']=0; x['custo']=None if x['ch'] is None else 0; x['diesel']=None if x['d'] is None else 0; continue
        hc+=x['h']; hh+=x['h']*x['pess']
        if x['ch'] is None: custo_ok=False; add(x['nome']+': tarifa desconhecida (R$/h), custo não calculado')
        else: x['custo']=x['h']*x['ch']; custo+=x['custo']
        if x['d'] is None: diesel_ok=False
        else: x['diesel']=x['h']*x['d']; diesel+=x['diesel']
    alocado=sum((x['q'] for x in it),0)
    if saldo<1e-9: saldo=0
    pend=Q>1e-12 and alocado<=1e-12
    causa='' if not pend else ('sem conjunto' if cz.get('cfg') else ('sem rendimento' if cz.get('rend') else (('troca reservada ocupa a janela' if cz.get('troca') else 'sem horas na janela') if (cz.get('jan') or cz.get('seq')) else ('sem recurso na fazenda' if cz.get('rec') else 'partes fixas abaixo de 100 %'))))
    # 3) saldo em horas pelas premissas do plano; necessário = atendido + saldo (ha e horas-conjunto); decorrido necessário por sequência inteira
    sem_h=0; fq=[0]*len(it)
    for x in fx:
        if x['t']<=1e-12: continue
        if x['r'] is None: sem_h+=x['t']; continue
        u=x['t']-x['q']
        if u>1e-9: fq[x['i']]=u
    if R>0:
        if not liv_ok: sem_h+=R
        else:
            rest=R-sum((x['q'] for x in livres),0)
            if rest>1e-9:
                sr=sum(x['r'] for x in plan_liv)
                for x in plan_liv: fq[x['i']]+=x['r']*rest/sr
    nhc=0; fhc=0; nec_dec=0; pis={}
    for x in it:
        x['fq']=fq[x['i']]; x['fh']=x['fq']/x['r'] if x['fq']>0 else 0; x['nq']=x['q']+x['fq']; x['nh']=x['h']+x['fh']; nhc+=x['nh']; fhc+=x['fh']
        if x['nq']>1e-12: pis.setdefault(UP.raiz(x['i']),[]).append(x)
    for g in sorted(pis):
        xs=pis[g]; s_=sum((x['nh'] for x in xs),0)+troca_de(xs)
        if s_>nec_dec: nec_dec=s_
    sem_nada=Q>1e-12 and Q-sem_h<=1e-9
    nec=dict(area=Q,hconj=None if sem_nada else nhc,decorrido=None if sem_nada else nec_dec,semHoras=sem_h)
    falta=dict(area=saldo,hconj=None if sem_nada else fhc,decorrido=None if sem_nada else max(0,nec_dec-(0 if pend else decorrido)),semHoras=sem_h)
    return dict(Q=Q,alocado=alocado,saldo=saldo,pendente=pend,causa=causa,hconj=None if pend else hc,decorrido=None if pend else decorrido,troca=troca_t,custo=custo,custoOk=custo_ok,
                custoHa=(custo/alocado) if (custo_ok and alocado>1e-12) else None,diesel=diesel,dieselOk=diesel_ok,hh=hh,conflito=conflito,conflitoEst=conflito and not cf_f,deficit=deficit,nec=nec,falta=falta,motivos=mot,itens=it)
# <<< REPARTIR
# ---- SAF etapa única "Dimensione operações e recursos" (ESPECIFICACAO §3.3, §4.3, §7): espelhos de ocorr, capSaf e resumoCultura ----
def _cfgs_safra(safra,op,atv,cfg_override,atvs_em_uso):
    """Configurações de uma atividade com a sobrescrita do teste aplicada pelas regras do rendAfter: rendimento pelos parâmetros
    (rend_efetivo); prestador sem implemento, pessoas e recursos da fazenda; rec.oper = pessoas. Chave (op, atv, id) ou (op, '*', id) =
    todas as atividades em uso da operação (a dividida entre configurações não muda)."""
    cfs=cfgs_rend(safra,op,atv)
    if not cfg_override: return cfs
    out=[]
    for c in cfs:
        o=(cfg_override.get((op,atv,c['id'])) or (cfg_override.get((op,'*',c['id'])) if (len(cfs)==1 and atv in atvs_em_uso) else None))
        if o:
            c=dict(c); c.update(o); c['rec']=dict(c.get('rec') or {})
            if c.get('larg') and c.get('modo','Largura × velocidade')!='Informado': c['rend']=rend_calc(c['larg'],c['vel'],c['efic'])
            if c.get('conj_id')=='prestador': c.update(impl=0,pess=0,pess_rs=0); c['rec']={}
            elif c.get('pess',0)>0: c['rec']['oper']=c['pess']
            else: c['rec'].pop('oper',None)
        out.append(c)
    return out
def _mes_idx(dt):
    k=dt.isoformat()[:7]
    return next((i for i,(m,_) in enumerate(MESES) if m==k),-1)
def _pools(recursos): return {r['id']:dict(un=r['un'],nome=r['nome']) for r in (recursos or RECURSOS)}
def ocorr_op(safra,planos=None,cfg_override=None,recursos=None,ajustes=None):
    """Ocorrências (cultivo × atividade) da safra como o ocorr do safra.js: data, mês, área, repartir com os grupos de recursos da fazenda,
    custo de operação e insumos (dose × área, com os ajustes '-' e '+'). planos: {cultivo: plano} sobrescreve o plano do cultivo."""
    pools=_pools(recursos); aj=AJUSTES if ajustes is None else ajustes; out=[]
    cults=[c for c in CULTIVOS.get(safra,[])]
    usados={}
    for c in cults:
        pid=(planos or {}).get(c['id'],c['plano']); pl=PLANO.get(pid) if pid else None
        if pl and pl['cultura']==c['cultura']:
            for a in pl['atividades']: usados.setdefault(a['op'],set()).add(a['nome'])
    for c in cults:
        pid=(planos or {}).get(c['id'],c['plano']); pl=PLANO.get(pid) if pid else None
        if not pl or pl['cultura']!=c['cultura']: continue
        cc=dict(c,plano=pid)
        for a in pl['atividades']:
            dt=data_atividade(cc,a); cfs=_cfgs_safra(safra,a['op'],a['nome'],cfg_override,usados.get(a['op'],set()))
            rp=repartir(c['area'],[cfg_in(x) for x in cfs],pools); A=aj.get(c['id'],{})
            cins=0.0
            for i,pr in enumerate(a['prods']):
                k=f"{a['id']}|{i}"
                if A.get(k)=='-': continue
                dose=A[k] if (k in A and A[k]!='-') else pr['dose']; cins+=float(dose)*c['area']*pr['preco']
            for k,x in A.items():
                if k.startswith(f"{a['id']}|+") and isinstance(x,dict): cins+=float(x['dose'])*c['area']*x['preco']
            out.append(dict(c=c,a=a,dt=dt,mi=_mes_idx(dt),area=c['area'],rp=rp,cfs=[dict(rec=x.get('rec') or {}) for x in cfs],cop=rp['custo'],cins=cins,
                            horas=rp['hconj'] or 0,pend=rp['pendente'],saldo=rp['saldo'],hh=rp['hh'],diesel=rp['diesel']))
    return out
def plano_op(safra,planos=None,cfg_override=None,recursos=None):
    """Espelho dos totais do plano operacional (etapa 3 "Dimensione operações e recursos"): área, horas-conjunto, custo de operação,
    diesel, horas-homem, área sem conjunto e ocorrências pendentes; as configurações vêm de cfgs_rend (com a sobrescrita do teste) e os
    grupos de recursos de RECURSOS. REND-RETORNO-1818: também as horas-conjunto necessárias (nec_h = hconj + falta_h) e a área sem horas
    calculáveis (sem_h)."""
    t=dict(area=0,hconj=0,cop=0,diesel=0,hh=0,saldo=0,pend=0,conflito=0,ocorr=0,multi=0,nec_h=0,falta_h=0,sem_h=0)
    for o in ocorr_op(safra,planos,cfg_override,recursos):
        rp=o['rp']
        t['ocorr']+=1; t['area']+=o['area']; t['hconj']+=rp['hconj'] or 0; t['cop']+=rp['custo']; t['diesel']+=rp['diesel']; t['hh']+=rp['hh']; t['saldo']+=rp['saldo']
        t['pend']+=1 if rp['pendente'] else 0; t['conflito']+=1 if rp['conflito'] else 0; t['multi']+=1 if len(o['cfs'])>1 else 0
        t['nec_h']+=rp['nec']['hconj'] or 0; t['falta_h']+=rp['falta']['hconj'] or 0; t['sem_h']+=rp['falta']['semHoras']
    return t
def carga_itens(o):
    out=[]
    for j,x in enumerate(o['rp']['itens']):
        rc=(o['cfs'][j]['rec'] if j<len(o['cfs']) else {}) or {}
        for k,u in rc.items():
            u=float(u or 0)
            if u<=0: continue
            out.append(dict(k=k,j=j,u=u,h=float(x.get('nh') or 0)*u,ha=float(x.get('h') or 0)*u,sim=u if float(x.get('nq') or 0)>1e-12 else 0,semRec=bool(x.get('semRec'))))
    return out
def cap_rec(r,meses=None,dias=None):
    pes=r['pes'] if 'pes' in r else (r['id']=='oper' or 'abs' in r)
    pc=lambda x: min(100,max(0,float(x or 0)))/100
    un=float(r['un'] or 0); J=float(r['jornada'] or 0); T=1 if pes else float(r.get('turnos') or 0); DP=(1-pc(r.get('abs'))) if pes else pc(r.get('disp'))
    por=[(DIAS_UTEIS if dias is None else dias).get(m,0)*J*T*DP for m,_ in (MESES if meses is None else meses)]
    return dict(id=r['id'],nome=r['nome'],pes=pes,un=un,porUn=por,cap=[un*p for p in por])
def outras_safras(safra):
    me=next((s for s in SAFRAS if s['id']==safra),None)
    if not me or me['ro']: return []
    return [s['id'] for s in SAFRAS if s['id']!=safra and not s['ro'] and s['fazenda']==me['fazenda']]
def classe_oc(dt,mi,ini,fim):
    """Espelho do classeOc (safra.js): antes do início, depois do fim, fora do calendário ou no calendário ('cal')."""
    d=dt.isoformat() if hasattr(dt,'isoformat') else str(dt)
    if ini and d<ini: return 'antes'
    if fim and d>fim: return 'depois'
    if mi<0: return 'fora'
    return 'cal'
def capacidade(safra,recursos=None,planos=None,cfg_override=None):
    """Espelho do capCalc + capSaf (safra.js): ocorrências desta safra com a etiqueta do período dela e as das outras safras abertas da
    mesma fazenda com o período de cada uma (SAF-C02); a conta é a do cap_saf."""
    recs=recursos or RECURSOS; me=next((s for s in SAFRAS if s['id']==safra),{})
    oc=[dict(o,cls=classe_oc(o['dt'],o['mi'],me.get('ini'),me.get('fim'))) for o in ocorr_op(safra,planos,cfg_override,recs)]
    outras=[dict(id=s['id'],nome=s['nome'],ini=s.get('ini'),fim=s.get('fim'),oc=ocorr_op(s['id'],None,None,recs)) for sid in outras_safras(safra) for s in SAFRAS if s['id']==sid]
    return cap_saf(oc,outras,recs)
def cap_saf(oc,outras,recs,meses=None,dias=None):
    """Espelho do capSaf (safra.js · bloco CAPACIDADE): por grupo de recursos e mês, demanda desta safra e das outras safras abertas da mesma
    fazenda (x.nh × rc, inclui o necessário sem alocação), capacidade, ocupação (None = não calculável), necessárias e falta. oc = desta safra,
    com 'cls'; outras = [dict(id, nome, ini, fim, oc)]. A etiqueta de cada ocorrência sai do período da safra de ORIGEM (SAF-C02): com
    etiqueta (antes, depois, fora) conta no custo e não na capacidade, e a carga vai para g['fora'] (sid None = desta safra).
    Contrato (capContrato): 'cls' em cada ocorrência desta safra e 'ini' e 'fim' em cada outra; a célula soma as parcelas de cada safra em
    ordem crescente, com laço explícito (o sum() do Python 3.12+ compensa o arredondamento e sairia do JS)."""
    for o in oc or []:
        if 'cls' not in o: raise ValueError('cap_saf: ocorrência desta safra sem a etiqueta cls do período dela')
    for s in outras or []:
        if 'ini' not in s or 'fim' not in s: raise ValueError('cap_saf: a safra %s chegou sem o período (ini e fim)' % s.get('id'))
    meses=MESES if meses is None else meses; M=len(meses); G={}; n=[0]
    for r in recs: g=cap_rec(r,meses,dias); g.update(dThis=[0.0]*M,dThisAt=[0.0]*M,dOth=[0.0]*M,oth={},sim=[0]*M,semH=[0.0]*M,pendSR=[0]*M,fora=[]); G[r['id']]=g
    def add(o,own,s):
        sid=None if own else s['id']; ix=n[0]; n[0]+=1
        if o['mi']<0: return
        cl=o.get('cls') if own else classe_oc(o['dt'],o['mi'],s.get('ini'),s.get('fim'))
        if cl and cl!='cal':
            for c in carga_itens(o):
                if c['k'] in G and c['h']>0: G[c['k']]['fora'].append(dict(sid=sid,cls=cl,mi=o['mi'],h=c['h'],n=ix))
            return
        cs=carga_itens(o)
        for c in cs:
            g=G.get(c['k'])
            if not g: continue
            if own:
                g['dThis'][o['mi']]+=c['h']; g['dThisAt'][o['mi']]+=c['ha']
                if c['semRec']: g['pendSR'][o['mi']]+=1
            else:
                g['dOth'][o['mi']]+=c['h']; g['oth'].setdefault(sid,[0.0]*M)[o['mi']]+=c['h']
            g['sim'][o['mi']]=max(g['sim'][o['mi']],c['sim'])
        if o['rp']['falta']['semHoras']>1e-9:   # "≥" com a área sem horas de qualquer safra elegível (a mesma marca nas duas vistas)
            for k in {c['k'] for c in cs}:
                if k in G: G[k]['semH'][o['mi']]+=o['rp']['falta']['semHoras']
    for o in oc: add(o,True,None)
    for s in outras:
        for o in s['oc']: add(o,False,s)
    for g in G.values():
        cells=[]
        for mi,(m,lab) in enumerate(meses):
            d=0.0
            for x in sorted([g['dThis'][mi]]+[v[mi] for v in g['oth'].values()]): d+=x
            cap=g['cap'][mi]; pu=g['porUn'][mi]
            nc=lambda h: (max(_math.ceil(h/pu-1e-9),g['sim'][mi]) if pu>0 else -1) if h>1e-4 else 0
            nec=nc(d); nt=nc(g['dThis'][mi]); falta=lambda n: n<0 or n>g['un']; red=d>1e-4 and falta(nec)
            cells.append(dict(mi=mi,mes=lab,d=d,dThis=g['dThis'][mi],dOth=g['dOth'][mi],cap=cap,porUn=pu,ocup=(None if cap<=0 else 100*d/cap) if d>1e-4 else 0,
                              nec=nec,red=red,soma=red and not falta(nt),own=g['dThis'][mi]>1e-4,ge=g['semH'][mi]>1e-9,pendSR=g['pendSR'][mi]))
        g['cells']=cells; own=[c for c in cells if c['own']]; calc=[c for c in own if c['ocup'] is not None]
        mx=None
        for c in calc:
            if mx is None or c['ocup']>mx['ocup']+1e-12: mx=c
        g['max']=mx if calc else (own[0] if own else None)
        g['reds']=[c for c in own if c['red']]; nm=None
        for c in g['reds']:
            if nm is None or c['nec']>nm['nec'] or (nm['nec']>=0 and c['nec']<0): nm=c
        g['necMax']=nm; g['horasSafra']=sum(g['dThis']); g['horasSafraAt']=sum(g['dThisAt'])
    return G
def fmt_ocup(o):
    if o is None: return 'não calculável'
    if o<=0: return '—'
    if o<1: return '<1 %'
    return '{:,} %'.format(int(_math.floor(o+0.5))).replace(',','.')
def resumo_cultura(safra,ajustes=None,planos_extra=None,cfg_override=None):
    """Custo por cultura (§4.3): área com plano (cada cultivo uma vez), custo de operação, insumos do plano (dose × área × preço, com os
    ajustes '-' e '+'), R$/ha por ha físico com plano; parcial com ocorrência pendente ou tarifa desconhecida; parcela antes do início."""
    me=next((s for s in SAFRAS if s['id']==safra),{}); ini=me.get('ini','')
    by={}; vistos=set()
    for o in ocorr_op(safra,planos_extra,cfg_override,None,ajustes):
        cu=o['c']['cultura']; b=by.setdefault(cu,dict(cult=cu,area=0.0,cop=0.0,cins=0.0,npend=0,ntar=0,copAntes=0.0,cinsAntes=0.0))
        if o['c']['id'] not in vistos: vistos.add(o['c']['id']); b['area']+=o['area']
        b['cop']+=o['cop'] or 0; b['cins']+=o['cins']
        if o['pend']: b['npend']+=1
        elif not o['rp']['custoOk']: b['ntar']+=1
        if ini and o['dt'].isoformat()<ini: b['copAntes']+=o['cop'] or 0; b['cinsAntes']+=o['cins']
    for b in by.values():
        b['tot']=b['cop']+b['cins']; b['rha']=None if (b['npend'] or b['ntar']) else (b['tot']/b['area'] if b['area'] else None)
    return by
def js_data():
    return dict(meses=MESES,dias=DIAS_UTEIS,safras=SAFRAS,tipos=TIPOS,planos=PLANOS,cultivos=CULTIVOS,ajustes=AJUSTES,conj=CONJ,recursos=RECURSOS,estoque=ESTOQUE,receb=RECEB,
                estb=est_base(),osb=os_base())   # CTL-4: estoque (cenEstDem) e ordens (cenOsDem) do cenário vivo
# =================== Suprimentos: fornecedores, cotações, pedidos, estoque (ligam Compras ↔ Estoque ↔ Cadastros) ===================
GRUPOS=['Sementes','Fertilizantes','Herbicidas','Fungicidas','Inseticidas','Adjuvantes','Inoculantes','Combustível','Peças']
FORNECEDORES=[  # cadastro de parceiros (CD-05): grupos homologados, e-mail e WhatsApp — cotações só vão a homologados do grupo
 dict(id='F01',nome='Fertisul',cnpj='12.345.678/0001-95',grupos=['Fertilizantes'],email='cotacoes@fertisul.com.br',whats='65 99911-2233',homologado=True),
 dict(id='F02',nome='Casa do Adubo',cnpj='22.456.789/0001-22',grupos=['Fertilizantes','Inoculantes'],email='vendas@casadoadubo.com.br',whats='65 99822-3344',homologado=True),
 dict(id='F03',nome='Agro Norte',cnpj='33.567.890/0001-77',grupos=['Herbicidas','Fungicidas','Inseticidas','Adjuvantes'],email='orcamento@agronorte.com.br',whats='65 99733-4455',homologado=True),
 dict(id='F04',nome='Santa Rita Insumos',cnpj='44.678.901/0001-02',grupos=['Herbicidas','Fungicidas','Inseticidas','Adjuvantes','Inoculantes'],email='compras@santaritainsumos.com.br',whats='65 99644-5566',homologado=True),
 dict(id='F05',nome='Sementes Vale',cnpj='55.789.012/0001-39',grupos=['Sementes'],email='comercial@sementesvale.com.br',whats='65 99555-6677',homologado=True),
 dict(id='F06',nome='Coop. Vale',cnpj='66.890.123/0001-53',grupos=['Sementes','Fertilizantes','Herbicidas','Fungicidas'],email='insumos@coopvale.coop.br',whats='65 99466-7788',homologado=True),
 dict(id='F07',nome='Química Centro-Oeste',cnpj='77.901.234/0001-34',grupos=['Fungicidas','Inseticidas'],email='',whats='65 99377-8899',homologado=False),
]
SOL_INICIAL=dict(id='SOL-2026-07',safra='S2627',origem='Planejar safra · Safra 2026/27 · demanda de insumos',enviada='23/09/2026 10:40',por='Ana (gestora)')
def sol_itens():
    d=demanda('S2627'); return {n:dict(grupo=o['grupo'],un=o['un'],qtd=round(o['liq'],2),preco_ref=o['preco']) for n,o in d.items() if o['liq']>0.001}
# propostas simuladas (respostas dos convites) por grupo: preço unitário, prazo de entrega (dias), frete, validade
PROPOSTAS={
 'Fertilizantes':[dict(f='F01',fator=0.97,prazo=12,frete='CIF',validade='30/09/2026',pag='28 dias'),dict(f='F02',fator=1.01,prazo=8,frete='CIF',validade='02/10/2026',pag='30 dias'),dict(f='F06',fator=0.99,prazo=15,frete='FOB',validade='29/09/2026',pag='à vista')],
 'Herbicidas':[dict(f='F03',fator=1.02,prazo=5,frete='CIF',validade='30/09/2026',pag='30 dias'),dict(f='F04',fator=0.96,prazo=7,frete='CIF',validade='01/10/2026',pag='28 dias'),dict(f='F06',fator=1.00,prazo=10,frete='FOB',validade='29/09/2026',pag='à vista')],
 'Fungicidas':[dict(f='F03',fator=0.98,prazo=5,frete='CIF',validade='30/09/2026',pag='30 dias'),dict(f='F04',fator=1.03,prazo=6,frete='CIF',validade='01/10/2026',pag='28 dias')],
 'Inseticidas':[dict(f='F03',fator=1.00,prazo=5,frete='CIF',validade='30/09/2026',pag='30 dias'),dict(f='F04',fator=0.95,prazo=9,frete='CIF',validade='01/10/2026',pag='28 dias')],
 'Adjuvantes':[dict(f='F03',fator=1.00,prazo=5,frete='CIF',validade='30/09/2026',pag='30 dias'),dict(f='F04',fator=0.97,prazo=7,frete='CIF',validade='01/10/2026',pag='28 dias')],
 'Inoculantes':[dict(f='F02',fator=1.00,prazo=6,frete='CIF',validade='30/09/2026',pag='30 dias'),dict(f='F04',fator=1.04,prazo=4,frete='CIF',validade='01/10/2026',pag='28 dias')],
 'Sementes':[dict(f='F05',fator=1.00,prazo=10,frete='CIF',validade='30/09/2026',pag='safra'),dict(f='F06',fator=0.98,prazo=14,frete='FOB',validade='29/09/2026',pag='safra')],
}
ALCADA=[dict(ate=50000,quem='Gestor de suprimentos'),dict(ate=300000,quem='Gerente da fazenda'),dict(ate=None,quem='Direção')]
# pedidos já existentes (antes desta safra ou fora da SOL) — PC-088 é o do DEMO-02
PEDIDOS=[
 dict(id='PC-088',f='F01',item='KCl 60%',grupo='Fertilizantes',un='kg',qtd=100000,recebido=60000,apto=50000,quarentena=10000,a_entregar=40000,preco=2.33,previsao='02/10/2026',estado='Parcial'),
 dict(id='PC-090',f='F06',item='Semente de soja 58 W',grupo='Sementes',un='kg',qtd=20000,recebido=0,apto=0,quarentena=0,a_entregar=20000,preco=9.30,previsao='05/10/2026',estado='Confirmado'),
 dict(id='PC-091',f='F05',item='Semente de soja 62 X',grupo='Sementes',un='kg',qtd=8000,recebido=0,apto=0,quarentena=0,a_entregar=8000,preco=9.55,previsao='08/10/2026',estado='Confirmado'),
]
RECEBIMENTOS=[  # conferência de recebimento (Estoque · etapa 1)
 dict(id='NF 4501',pedido='PC-088',f='F01',item='KCl 60%',un='kg',qtd_nf=60000,qtd_conf=60000,apto=50000,quarentena=10000,lote='K26-11',data='19/09/2026',estado='Conferido · 10 t em quarentena'),
 dict(id='NF 4533',pedido='PC-090',f='F06',item='Semente de soja 58 W',un='kg',qtd_nf=20000,qtd_conf=None,apto=None,quarentena=None,lote='S58-0926',data='24/09/2026 (previsto)',estado='A conferir'),
]
REQUISICOES=[  # entregas por O.S. liberada (Estoque · etapa 2) — só O.S. liberada tem requisição
 dict(id='REQ-031',os='OS-0417',item='MAP 11-52',un='sc 50 kg',solicitado=100,entregue=100,consumido=70,dev_declarada=20,dev_recebida=20,custodia=10,estado='Em conferência'),
 dict(id='REQ-035',os='OS-0421',item='Fungicida A',un='L',solicitado=175,entregue=160,consumido=95,dev_declarada=0,dev_recebida=0,custodia=65,estado='Em execução'),
 dict(id='REQ-036',os='OS-0420',item='Semente de soja 58 W',un='kg',solicitado=5200,entregue=1560,consumido=1560,dev_declarada=0,dev_recebida=0,custodia=0,estado='Impedida · ativo bloqueado'),
 dict(id='REQ-038',os='OS-0418',item='Ureia 45%',un='kg',solicitado=1140,entregue=0,consumido=0,dev_declarada=0,dev_recebida=0,custodia=0,estado='Aguardando liberação da O.S.'),
]
LOTES=[  # saldos por lote (Estoque · etapa 4): utilizável = físico − quarentena/bloqueio; disponível = utilizável − reservado
 dict(item='KCl 60%',lote='K26-11',local='Galpão 2',un='kg',fisico=60000,quarentena=10000,reservado=0,validade='—'),
 dict(item='MAP 11-52',lote='M26-07',local='Galpão 2',un='kg',fisico=90000,quarentena=0,reservado=0,validade='—'),
 dict(item='Fungicida A',lote='F26-02',local='Almox. defensivos',un='L',fisico=545,quarentena=0,reservado=65,validade='03/2028'),
 dict(item='Glifosato 480',lote='G26-14',local='Almox. defensivos',un='L',fisico=1200,quarentena=0,reservado=0,validade='11/2027'),
 dict(item='Semente de soja 58 W',lote='S58-0801',local='Câmara fria',un='kg',fisico=12000,quarentena=0,reservado=0,validade='06/2027'),
 dict(item='NPK 20-05-20',lote='N26-03',local='Galpão 1',un='kg',fisico=8000,quarentena=0,reservado=0,validade='—'),
 dict(item='Óleo mineral',lote='O26-05',local='Almox. defensivos',un='L',fisico=400,quarentena=0,reservado=0,validade='08/2028'),
]
CONTAGENS=[  # contagem cíclica (Estoque · etapa 5): diferença gera ajuste para aprovação, nunca ajuste automático
 dict(id='INV-2609',local='Galpão 2',item='MAP 11-52',lote='M26-07',un='kg',sistema=90000,contado=89400,estado='Divergência · aguardando aprovação'),
 dict(id='INV-2610',local='Almox. defensivos',item='Fungicida A',lote='F26-02',un='L',sistema=545,contado=545,estado='Conferido'),
 dict(id='INV-2611',local='Almox. defensivos',item='Glifosato 480',lote='G26-14',un='L',sistema=1200,contado=None,estado='A contar'),
]

def checa_coerencia():
    """disponível por lote (físico − quarentena − reservado) deve bater com ESTOQUE usado na demanda."""
    erros=[]
    for l in LOTES:
        disp=l['fisico']-l['quarentena']-l['reservado']
        if ESTOQUE.get(l['item']) is not None and abs(ESTOQUE[l['item']]-disp)>0.01: erros.append((l['item'],ESTOQUE[l['item']],disp))
    return erros

# =================== Acréscimos v3.8 (Compras e Estoque) — só novos campos e funções; nada acima muda ===================
# Parceiros (CD-05 e Compra etapa 3): contato, doc (CNPJ fictício com dígitos verificadores válidos) e canais autorizados para cotação.
# Cada canal exige o contato correspondente. Sem WhatsApp autorizado: Sementes Vale (F05, exemplo do CD-05) e Casa do Adubo
# (F02, que aparece na SOL-2026-07 em Fertilizantes e Inoculantes — sem ela a regra não apareceria na Compra, que não tem Sementes).
CONTATO_FORN={'F01':'Rafael Moura','F02':'Juliana Prado','F03':'Marcelo Tavares','F04':'Denise Rocha','F05':'Otávio Lima','F06':'Sandra Kuhn','F07':'Paulo Neri'}
SEM_WHATS_COTACAO={'F05','F02'}
def cnpj_valido(cnpj):
    """Mantém os 12 primeiros dígitos e recalcula os 2 verificadores (formato 00.000.000/0000-00)."""
    b=''.join(c for c in cnpj if c.isdigit())[:12]
    def dv(s,w): r=sum(int(a)*p for a,p in zip(s,w))%11; return '0' if r<2 else str(11-r)
    w1=[5,4,3,2,9,8,7,6,5,4,3,2]; d1=dv(b,w1); d2=dv(b+d1,[6]+w1); n=b+d1+d2
    return f'{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}'
def _completa_fornecedores():
    for f in FORNECEDORES:
        f.setdefault('contato',CONTATO_FORN.get(f['id'],''))
        f.setdefault('doc',cnpj_valido(f['cnpj']))
        f.setdefault('canais',[c for c,ok in (('E-mail',bool(f['email'])),('WhatsApp',bool(f['whats']) and f['id'] not in SEM_WHATS_COTACAO)) if ok])
_completa_fornecedores()
# Demanda datada (Compra etapas 2, 4 e 6): mesma base e mesma ordem das origens de demanda(), com a data de cada atividade.
def demanda_datada(safra,ajustes=None,planos_extra=None):
    ajustes=AJUSTES if ajustes is None else ajustes
    out={}
    for c in CULTIVOS[safra]:
        pid=(planos_extra or {}).get(c['id'],c['plano'])
        if not pid: continue
        for a in PLANO[pid]['atividades']:
            dt=data_atividade(c,a).isoformat()
            for i,p in enumerate(a['prods']):
                dose=ajustes.get(c['id'],{}).get(f"{a['id']}|{i}",p['dose'])
                out.setdefault(prod_nome(p['prod'],c),[]).append(dict(data=dt,local=c['local'],atv=a['nome'],dose=dose,area=c['area'],q=dose*c['area']))
    return out
def iso_br(s): d,m,a=s.split('/'); return f'{a}-{m}-{d}'
def falta_a_partir(ocorr,estoque,entradas):
    """Primeira data (ISO) em que a demanda acumulada supera o estoque apto + as entradas previstas até essa data; None se não falta.
    ocorr e entradas: listas de (data ISO, quantidade)."""
    acum=0.0
    for d in sorted({x for x,_ in ocorr}):
        acum+=sum(q for x,q in ocorr if x==d)
        if acum>estoque+sum(q for x,q in entradas if x<=d)+1e-9: return d
    return None
def faltas(safra='S2627',sem_pedido=None):
    """Falta a partir de, por insumo, com estoque apto e pedidos em aberto (PEDIDOS), opcionalmente sem um pedido."""
    return {nm:falta_a_partir([(o['data'],o['q']) for o in occ],ESTOQUE.get(nm,0),
                              [(iso_br(p['previsao']),p['a_entregar']) for p in PEDIDOS if p['item']==nm and p['id']!=sem_pedido and p['a_entregar']])
            for nm,occ in demanda_datada(safra).items()}

# =================== CAL-01 (PRD v3.9) · necessidade líquida por data — espelho de cal01.js (mesma ordem, mesmos números) ===================
def _nf(n,d=0):
    t=f"{n:,.{d}f}"; return t.replace(',','X').replace('.',',').replace('X','.')
def _nfa(n):   # como nfa do safra.js: até 2 casas, sem zeros à direita
    return _nf(n,2).rstrip('0').rstrip(',')
# recebimentos previstos com data e fazenda (pedidos em aberto, todos da Santa Rita; o calcário da Lagoa Grande não tem PC no protótipo: pedido de 30/09)
RECEB_DT=[dict(item=p['item'],un=p['un'],linha=p.get('linha'),q=p['a_entregar'],dt=iso_br(p['previsao']),ref=p['id'],faz='Santa Rita',t=f"Recebimento {p['id']} ({next(f['nome'] for f in FORNECEDORES if f['id']==p['f'])})")
          for p in PEDIDOS if p['a_entregar']]+[dict(item='Calcário dolomítico filler',un='kg',q=50000,dt='2026-09-30',ref=None,faz='Lagoa Grande',t='Recebimento previsto (pedido de 30/09)')]
# ---- CTL-4 · demanda única (DEM-01..07): espelho de cenOsDem (cenario.js) e de demRestante/demOsEvs/demFazenda (cal01.js) ----
OS_FASES_PEND=('A liberar','Liberadas','Em execução')
def _saf_id(faz,lab):   # rótulo de safra da ordem ('2026/27', 'Safrinha 2027') → id da safra aberta da fazenda
    return next((s['id'] for s in SAFRAS if s['fazenda']==faz and s['nome'].endswith(lab) and not s['ro']),None)
_OSB=[None]
def os_base():
    """Parte fixa das ordens para a demanda (vai às telas como D2.osb / MDATA.dem.osb): fazenda, safra (id), chaves do plano, talhões, início
    da janela e texto; as safras abertas (para a ordem nova emitida no cenário) e grupo, preço de referência e unidade de cada insumo
    (a unidade serve à linha "Acima da demanda" do insumo que saiu da demanda, DEM-09)."""
    if _OSB[0] is None:
        import areas.processo_os as P
        ords=[]
        for b in P._ordens():
            saf=_saf_id(b['faz'],b['saf'])
            if not saf: continue
            ords.append(dict(id=b['id'],faz=b['faz'],saf=saf,chaves=list(b['keys']),loc=[t['nome'] for t in (b.get('talhoes') or [])] or [b['talhao']],
                             ini=b.get('ini') or '',t=f"{b['talhao']} · {b['id']} · {b['atv']['nome']}"))
        cat={}
        for s_ in SAFRAS:
            for c in CULTIVOS.get(s_['id'],[]):
                for a in (PLANO[c['plano']]['atividades'] if c['plano'] else []):
                    for x in a['prods']: cat.setdefault(prod_nome(x['prod'],c),dict(g=x['grupo'],preco=x['preco'],un=x['un']))
        for pl in PLANOS:
            for a in pl['atividades']:
                for x in a['prods']: cat.setdefault(x['prod'],dict(g=x['grupo'],preco=x['preco'],un=x['un']))
        _OSB[0]=dict(ords=ords,safs=[dict(id=s_['id'],faz=s_['fazenda'],nome=s_['nome']) for s_ in SAFRAS if not s_['ro']],cat=cat,hoje=HOJE_ISO,
                     locFaz=LOC_FAZ,faz0='Santa Rita')   # local do lote → fazenda: a reserva em lote de outra fazenda cobre a ordem (revisão do 853a6a8, achado 3)
    return _OSB[0]
def _os_sup(c,co,r=None,fz=None,fo=None):
    """Espelho de cenOsSup (revisão do 853a6a8, achado 1): por insumo, bruto (o que falta aplicar; fora de A liberar/Liberadas/Em execução 0),
    cust (custódia da requisição), need = máx(0, bruto − cust) e sobra = máx(0, cust − bruto) — custódia sem uso, suprimento."""
    import quantidade as Q
    out={}
    if not co: return out
    r=r if r is not None else (c.get('reqs') or {}).get(co.get('req') or '')
    P=lambda p: out.setdefault(p,dict(bruto=0.0,cust=0.0,need=0.0,sobra=0.0,res=[]))
    if co['etapa'] in OS_FASES_PEND:
        real=co.get('realizado') or 0; saldo=(co.get('saldo') or 0) if real else (co.get('area') or 0)
        for i in co.get('ins') or []: P(i['p'])['bruto']+=Q.qtd(i['dose'],saldo) if real else (i.get('tot') or 0)
    dev={}   # turno no aparelho, sem sinal: a baixa volta à custódia até o envio (a mesma da tela O.S.; revisão do 853a6a8, achado 4)
    for a in co.get('ap') or []:
        if a.get('sinc') is False:
            for p_,q in (a.get('cons') or {}).items(): dev[p_]=dev.get(p_,0)+(q or 0)
    for it in (r or {}).get('itens') or []:
        pd=min(dev.get(it['prod'],0),it.get('consumido') or 0); dev[it['prod']]=dev.get(it['prod'],0)-pd; P(it['prod'])['cust']+=(it.get('custodia') or 0)+pd
    for x in out.values(): x['need']=max(0.0,Q.qtd(x['bruto']-x['cust'],1)); x['sobra']=max(0.0,Q.qtd(x['cust']-x['bruto'],1))
    # reservas presas no lote com a parte útil ef (até o need; primeiro os lotes da fazenda da ordem) — revisão do 853a6a8, achados 3 e 5
    if r and r.get('estado')!='Cancelada' and co['etapa'] in OS_FASES_PEND:
        lotes=c.get('lotes') or {}; rs=[]
        for it in r.get('itens') or []:
            l=lotes.get(it['prod']+'|'+it['lote'])
            if not l: continue
            q=_res_propria(c,r.get('id'),it,l)
            if q>1e-9: rs.append(dict(it=it,l=l,q=q,ef=0.0))
        rem={p_:x['need'] for p_,x in out.items()}
        for y in ([y for y in rs if fz(y['l'])==fo]+[y for y in rs if fz(y['l'])!=fo]) if fz else rs:
            p_=y['it']['prod']; y['ef']=min(y['q'],max(0.0,rem.get(p_,0))); rem[p_]=rem.get(p_,0)-y['ef']
        for y in rs: P(y['it']['prod'])['res'].append(y)
    return out
_OSD=[None]
def os_dem(cen=None):
    """DEM-02 · espelho de cenOsDem: o que cada O.S. ainda tira do almoxarifado, na semente do cenário (ou no estado cen). A liberar, Liberadas
    e Em execução: pendente = máx(0, quantidade(dose, saldo) − custódia da requisição); sem realizado, o total da versão. Em conferência e
    Encerradas: pendente 0, mas a ordem continua cobrindo o plano (DEM-01). Canceladas não cobrem nada. Data = máx(hoje, início da janela)."""
    if cen is None and _OSD[0] is not None: return _OSD[0]
    import cenario, quantidade as Q
    c=cenario.seed() if cen is None else cen; b=os_base(); out=[]
    fzl=lambda l: b['locFaz'].get(l['local']) or b['faz0']
    def um(x,co):
        if not co or co['etapa']=='Canceladas': return
        r=(c.get('reqs') or {}).get(co.get('req') or '') or {'itens':[]}; itens=[]
        if co['etapa'] in OS_FASES_PEND:
            real=co.get('realizado') or 0; saldo=(co.get('saldo') or 0) if real else (co.get('area') or 0); S=_os_sup(c,co,None,fzl,x['faz'])
            for i in co.get('ins') or []:
                s_=S.get(i['p']) or dict(need=0.0,cust=0.0,bruto=0.0,res=[]); cust=min(s_['cust'],s_['bruto']); k=b['cat'].get(i['p'],{})
                ox=[y for y in s_['res'] if fzl(y['l'])!=x['faz'] and y['ef']>1e-9]; rx=sum(y['ef'] for y in ox)
                locs=list(dict.fromkeys(f"{y['l']['local']} ({fzl(y['l'])})" for y in ox))
                itens.append(dict(p=i['p'],q=max(0.0,Q.qtd(s_['need']-rx,1)),un=i['un'],g=k.get('g',''),preco=k.get('preco',0),
                                  calc=f"{_nf(i['dose'],2)} {i['un']}/ha × {_nfa(saldo)} ha"+(f" − {_nfa(cust)} {i['un']} em custódia" if cust>0 else '')
                                       +(f" − {_nfa(rx)} {i['un']} reservados em {', '.join(locs)}" if rx>1e-9 else '')))
        if not x['chaves'] and not any(i['q']>0 for i in itens): return
        out.append(dict(id=x['id'],faz=x['faz'],saf=x['saf'],chaves=list(x['chaves']),area=co.get('area') or 0,dt=(x['ini'] if x['ini'] and x['ini']>b['hoje'] else b['hoje']),
                        etapa=co['etapa'],t=x['t'],loc=list(x['loc']),itens=itens))
    vistos=set()
    for x in b['ords']: vistos.add(x['id']); um(x,c['ordens'].get(x['id']))
    for k,co in c['ordens'].items():   # ordem nova emitida no cenário (tela O.S.): leva chave, talhão e janela
        no=((co or {}).get('osc') or {}).get('novo')
        if k in vistos or not no: continue
        saf=_saf_id(no.get('faz') or 'Santa Rita',no.get('saf') or '')
        if saf: um(dict(id=k,faz=no.get('faz') or 'Santa Rita',saf=saf,chaves=list(no.get('keys') or []),loc=[no.get('talhao')],ini=no.get('jan') or '',
                        t=f"{no.get('talhao')} · {k} · {(no.get('atv') or {}).get('nome') or no.get('tipo') or ''}"),co)
    if cen is None: _OSD[0]=out
    return out
# ---- CTL-4 (revisão, achado 1, S2) · estoque da demanda no MESMO cenário das ordens: espelho de cenEstDem (cenario.js) ----
# físico apto da fazenda (lote − quarentena; inclui as reservas, DEM-07), quarentena, reservas ativas (a mesma conta do Estoque, cenResPropria;
# chave = ID da O.S., DEM-04) e recebimentos previstos (RECEB_DT) sem o que o Estoque já conferiu da nota do pedido. Antes: semente fixa ao lado
# das ordens vivas (entregar 8.000 kg de NPK cortava 8.000 kg da compra).
LOC_FAZ={'Almox. Lagoa Grande':'Lagoa Grande'}   # local do lote → fazenda (fora do mapa: Santa Rita)
def est_base():
    """Parte fixa do estoque da demanda (vai às telas como D2.estb / MDATA.dem.b.est): pedidos em aberto com data e o local de cada fazenda."""
    return dict(rec=RECEB_DT,locFaz=LOC_FAZ,faz0='Santa Rita',hoje=HOJE_ISO)
_SEED=[None]
def _seed():
    if _SEED[0] is None:
        import cenario; _SEED[0]=cenario.seed()
    return _SEED[0]
def _res_propria(c,rid,it,l):
    """Espelho de cenResPropria/cenResTot: reserva ainda presa no lote para o item da requisição (da semente 'Reservada' ou dos movimentos de reserva)."""
    s0=_seed()['reqs'].get(rid)
    if s0 and s0['estado']=='Reservada': tot_=next((i['solicitado'] for i in s0['itens'] if i['prod']==it['prod']),0)
    else: tot_=sum(m.get('qtd') or 0 for m in (c.get('movs') or []) if m.get('tipo')=='reserva' and m.get('req')==rid and m.get('prod')==it['prod'])
    return max(0,min(l.get('reservado') or 0,tot_-(it.get('entregue') or 0)))
def os_faz(cen=None):
    """Espelho de cenOsFaz: fazenda de cada O.S. (registro e ordens emitidas no cenário)."""
    c=_seed() if cen is None else cen; f={x['id']:x['faz'] for x in os_base()['ords']}
    for k,co in (c.get('ordens') or {}).items():
        no=((co or {}).get('osc') or {}).get('novo')
        if no and k not in f: f[k]=no.get('faz') or 'Santa Rita'
    return f
def _reps_lote(c,l,qr):
    """Espelho de cenRepsLote (revisão do 16fb55e, ajuste 2): cada reprovação do lote com quantidade, laudo, motivo e as entradas bloqueadas que
    ela decidiu, do histórico; sem histórico que feche com o reprovado, o registro do lote (rep)."""
    pend=[]; reps=[]
    for m in (c.get('movs') or []):
        if m.get('prod')!=l['prod'] or m.get('lote')!=l['lote']: continue
        t=m.get('tipo')
        if t in ('recebimento-nf','devolucao') and not m.get('apto'):
            d=('devolução da '+str(m.get('req'))) if t=='devolucao' else (m.get('doc') or '')
            if d and d not in pend: pend.append(d)
        elif t=='inspecao': pend=[]
        elif t=='inspecao-reprovada':
            reps.append(dict(q=m.get('qtd') or 0,laudo=m.get('doc') or '',motivo=m.get('motivo') or '',quem=m.get('quem') or '',em=m.get('at') or '',doc=', '.join(pend))); pend=[]
    if abs(sum(r['q'] for r in reps)-qr)<1e-6: return reps
    x=dict(q=qr,doc=''); x.update(l.get('rep') or {}); x['q']=qr; return [x]
def est_dem(cen=None,faz='Santa Rita',osd=None):
    """Espelho de cenEstDem: {fisico, quar, reservas, recebDt, sobra} da fazenda no cenário cen (None = semente). osd: os_dem do mesmo cenário."""
    c=_seed() if cen is None else cen; b=est_base(); osd=os_dem(cen) if osd is None else osd; hoje=b['hoje']; ofaz=os_faz(cen)
    fz=lambda l: b['locFaz'].get(l['local']) or b['faz0']; lotes=c.get('lotes') or {}
    fisico={}; quar={}; quar_rep={}; quar_ref=[]; reservas=[]; receb=[]; sobra=[]
    for l in lotes.values():
        if fz(l)!=faz: continue
        fisico[l['prod']]=fisico.get(l['prod'],0)+(l.get('fisico') or 0)-(l.get('quarentena') or 0)
        qr=min(l.get('quarentena') or 0,l.get('quarRep') or 0); qp=(l.get('quarentena') or 0)-qr   # laudo pendente (condicionada) × reprovada (revisão do 853a6a8, achado 2)
        docs=[('devolução da '+str(m.get('req'))) if m.get('tipo')=='devolucao' else m.get('doc') for m in (c.get('movs') or [])
              if m.get('prod')==l['prod'] and m.get('lote')==l['lote'] and not m.get('apto') and m.get('tipo') in ('recebimento-nf','devolucao')]
        doc=([x for x in docs if x] or [''])[-1]
        mots=[str(m.get('obs') or (m.get('estRec') or {}).get('obs') or '').strip() for m in (c.get('movs') or [])
              if m.get('prod')==l['prod'] and m.get('lote')==l['lote'] and m.get('tipo') in ('recebimento-nf','devolucao')]   # motivo registrado na entrada (espelho de cenEstDem)
        mot=([x for x in mots if x] or [''])[-1]
        if qp>1e-9: quar[l['prod']]=quar.get(l['prod'],0)+qp; quar_ref.append(dict(item=l['prod'],q=qp,lote=l['lote'],doc=doc,mot=mot,rep=None))
        if qr>1e-9:
            quar_rep[l['prod']]=quar_rep.get(l['prod'],0)+qr; reps=_reps_lote(c,l,qr); dr=[]
            for r_ in reps:
                if r_['doc'] and r_['doc'] not in dr: dr.append(r_['doc'])
            quar_ref.append(dict(item=l['prod'],q=qr,lote=l['lote'],doc=', '.join(dr) or doc,mot=mot,rep=l.get('rep') or {},reps=reps))
    for rid,r in (c.get('reqs') or {}).items():
        o=(c.get('ordens') or {}).get(r['os'])
        if not o: continue
        l0=next((lotes[it['prod']+'|'+it['lote']] for it in r.get('itens') or [] if (it['prod']+'|'+it['lote']) in lotes),None)
        fo=ofaz.get(r['os']) or (fz(l0) if l0 else b['faz0'])
        if fo==faz:
            et=o['etapa']; rot='cancelada' if et=='Canceladas' else ('sobra da ordem' if et in OS_FASES_PEND else et.lower())
            for p_,x in _os_sup(c,o,r).items():
                if x['sobra']>1e-9: sobra.append(dict(item=p_,q=x['sobra'],t=f"{rid} · {r['os']} ({rot})",chave=r['os'],faz=faz))
        if r.get('estado')=='Cancelada' or o['etapa'] not in OS_FASES_PEND: continue
        od=next((x for x in osd if x['id']==r['os']),None); S=_os_sup(c,o,r,fz,fo)
        for it in r.get('itens') or []:
            l=lotes.get(it['prod']+'|'+it['lote'])
            if not l or fz(l)!=faz: continue
            y=next((z for z in (S.get(it['prod']) or {}).get('res') or [] if z['it'] is it),None)
            if not y or not y['ef']>1e-9: continue   # a ordem já não precisa desta reserva (revisão do 853a6a8, achado 5)
            mesma=fo==faz and od is not None
            reservas.append(dict(item=it['prod'],q=y['q'] if mesma else y['ef'],dt=od['dt'] if od else hoje,
                                 t=f"Reserva {rid} · {r['os']}"+(f" ({o['talhao']})" if o.get('talhao') else '')+(f" · {fo}" if fo!=faz else ''),chave=r['os'],faz=faz))
    recebidos=[]; vis=set(); nao_apuravel=[]
    for m in c.get('movs') or []:
        e=m.get('estRec') if m.get('tipo')=='recebimento-nf' else None
        if not e or not e.get('id') or e['id'] in vis: continue
        vis.add(e['id']); recebidos.append(e)
    def pc(e): return str(e.get('pedido') or e.get('ref') or e.get('ped') or e.get('id') or '').split(' · ')[0].strip()
    for r in b['rec']:
        if r['faz']!=faz: continue
        unidades={l.get('un') for l in lotes.values() if l.get('prod')==r['item']} | {e.get('un') for e in recebidos if pc(e)==r.get('ref') and e.get('item')==r['item']}
        unidades.discard(None); unidades.discard('')
        un=r.get('un') or (next(iter(unidades)) if len(unidades)==1 else None)
        if not un:
            nao_apuravel.append(dict(r,motivo='Unidade não apurável: previsão fora do suprimento. Confira o pedido e a unidade.')); continue
        def casa(e): return pc(e)==r.get('ref') and (e.get('item') or e.get('prod'))==r['item'] and e.get('un')==un and (e.get('linha') is None or r.get('linha') is None or str(e['linha'])==str(r['linha']))
        baixa=sum(float(e.get('conf') or 0) if e.get('apto') is None and e.get('quar') is None else float(e.get('apto') or 0)+float(e.get('quar') or 0) for e in recebidos if casa(e))
        q=max(0,r['q']-baixa)
        if q>1e-9: receb.append(dict(r,q=q))
    return dict(fisico=fisico,quar=quar,quarRep=quar_rep,quarRef=quar_ref,reservas=reservas,recebDt=receb,recebNaoApuravel=nao_apuravel,sobra=sobra)
def _tal_de(c):
    import ocupacao_cen as _OC
    return _OC.tal_de(c['local'],c['tipo'])
def occ_faz(safra,ajustes=None,planos_extra=None):
    """Ocorrências do plano das safras abertas da fazenda da safra (esta com os ajustes e os planos da tela), como o ocorr do safra.js:
    [{saf, k, a, local, tal, area, dt, nome, prods:[{nome, grupo, un, preco, dose, q, orig, laudo}]}] na ordem safra → cultivo → atividade."""
    ajustes=AJUSTES if ajustes is None else ajustes
    me=next(s for s in SAFRAS if s['id']==safra); out=[]
    for s in [me]+[x for x in SAFRAS if x['id']!=safra and not x['ro'] and x['fazenda']==me['fazenda']]:
        aj=ajustes if s['id']==safra else AJUSTES; px=planos_extra if s['id']==safra else None
        for c in CULTIVOS[s['id']]:
            pid=(px or {}).get(c['id'],c['plano'])
            if not pid: continue
            for a in PLANO[pid]['atividades']:
                prods=[]
                for i,p in enumerate(a['prods']):
                    dose=aj.get(c['id'],{}).get(f"{a['id']}|{i}",p['dose'])
                    # origem da dose (R21 da análise de solo): o ajuste do talhão é 'sessão' ("(ajustado pelo usuário)" na memória), como o ocorr do safra.js
                    prods.append(dict(nome=prod_nome(p['prod'],c),grupo=p['grupo'],un=p['un'],preco=p['preco'],dose=dose,q=dose*c['area'],
                                      orig=('sessão' if f"{a['id']}|{i}" in aj.get(c['id'],{}) else ''),laudo=''))
                out.append(dict(saf=s['id'],k=f"{c['id']}|{a['id']}",a=a['id'],local=c['local'],tal=_tal_de(c),area=c['area'],
                                dt=data_atividade(c,a).isoformat(),nome=a['nome'],prods=prods))
    return out
def dem_entradas(safra,ajustes=None,planos_extra=None,cen=None):
    """Entradas de demFazenda para a safra (sem as ordens): as mesmas que as telas montam (cenDemEntradas), com o estoque do cenário cen (None = semente)."""
    faz=next(s for s in SAFRAS if s['id']==safra)['fazenda']
    return dict(dict(saf=safra,faz=faz,hoje=HOJE_ISO,viavel=VIAVEL,ordem={s['id']:i for i,s in enumerate(SAFRAS)},nomes={s['id']:s['nome'] for s in SAFRAS},
                occ=occ_faz(safra,ajustes,planos_extra)),**est_dem(cen,faz))
def dem_fixas(safra):
    """Partes fixas da demanda da safra, sem ordens e sem estoque: as telas juntam o cenário vivo (cenDemEntradas) — Mapa › Insumos e Compra."""
    return {k:v for k,v in dem_entradas(safra).items() if k not in ('fisico','quar','quarRep','quarRef','reservas','recebDt','sobra')}
def js_dem_viva(safra):
    """Revisão do 853a6a8 (achado 6, S3): telas que afirmam algo sobre a compra (SU-03det, MB-05) leem a MESMA demanda do Planejar safra e da
    Compra — cal01.js + as partes fixas da safra (DEMV.x) + ordens e estoque do cenário vivo (cenDemEntradas(cenGet(), DEMV.x, DEMV.b)). Antes liam
    dados2.demanda('S2627') da semente no build ("sem pendência de compra" com a demanda pedindo complemento)."""
    import json as _j, os as _os
    return ('\n'+open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'cal01.js'),encoding='utf-8').read()+'\nconst DEMV = '
            +_j.dumps(dict(x=dem_fixas(safra),b=dict(osb=os_base(),est=est_base())),ensure_ascii=False).replace('</','<\\/')+';\n'
            +"function demViva(nome){ const m=demFazenda(cenDemEntradas(cenGet(),DEMV.x,DEMV.b)); return m[nome]||null; }\n")
def dem_restante(osd,occ):
    """DEM-01 · espelho de demRestante: {chave: {f: fração do plano sem O.S., txt}} pelo escopo da O.S. (atividade × talhões × safra dela)."""
    cob={}; txt={}
    for o in osd:
        ts=set(o.get('loc') or []); ats=[]
        for k in o.get('chaves') or []:
            a=str(k).split('|')[1]
            if a not in ats: ats.append(a)
        for a in ats:
            ks=[x for x in occ if x['saf']==o['saf'] and x['a']==a and (x['local'] in ts or x['tal'] in ts)]; tot=sum(x['area'] for x in ks)
            if not tot>0: continue
            for x in ks:
                cob[x['k']]=cob.get(x['k'],0)+min(1,(o.get('area') or 0)/tot)
                txt.setdefault(x['k'],[]).append(f"{o['id']} cobre {_nfa(o.get('area') or 0)} de {_nfa(tot)} ha"+(', rateados pela área' if len(ks)>1 else ''))
    return {k:dict(f=max(0,1-v),txt='; '.join(txt[k])) for k,v in cob.items()}
def _dem_tal(t): return str(t or '').split('-')[0]
def dem_os_evs(osd,prod,saf,ordem,tal_prod):
    """DEM-02/03/04 · espelho de demOsEvs."""
    out=[]
    for o in osd:
        for i in o['itens']:
            if i['p']!=prod or not i['q']>1e-9: continue
            av=(not o['chaves']) and any(prod in tal_prod.get(o['saf'],{}).get(_dem_tal(t),{}) for t in o['loc'])
            out.append(dict(dt=o['dt'],q=i['q'],tipo='dem',own=o['saf']==saf,ord=ordem.get(o['saf'],99),chave=o['id'],
                            t=o['t']+(' · sem vínculo com o plano do talhão: se for o mesmo uso, retire o produto do plano do talhão (etapa 2)' if av else ''),calc=i['calc'],loc=o['loc']))
    return out
def _dem_orig(p):
    """Origem da dose na memória (R21 da análise de solo), como demFazenda (cal01.js): pela análise (laudo) ou ajustada pelo usuário."""
    o=p.get('orig') or ''
    return f" (pela análise · {p.get('laudo') or ''})" if o=='análise' else (' (ajustado pelo usuário)' if o=='sessão' else '')
def dem_fazenda(x):
    """DEM-05/06/07 · espelho de demFazenda (cal01.js), passo a passo e na mesma ordem de eventos."""
    m={}; ordem=x['ordem']; occ=x['occ']; osd=[o for o in x['osd'] if o['faz']==x['faz']]; fr=dem_restante(osd,occ); tp={}
    for o in occ:
        for q in o['prods']: tp.setdefault(o['saf'],{}).setdefault(o['tal'],{})[q['nome']]=1
    def novo(nome,g,un,preco): return m.setdefault(nome,dict(nome=nome,grupo=g or '',un=un,preco=preco or 0,plano=0.0,evs=[]))
    for o in occ:
        if o['saf']!=x['saf']: continue
        c=fr.get(o['k']); f=c['f'] if c else 1
        for p in o['prods']:
            d=novo(p['nome'],p['grupo'],p['un'],p['preco']); d['plano']+=p['q']*f
            if not f>1e-9: continue
            ar=o['area']*f
            d['evs'].append(dict(dt=o['dt'] or '',q=p['dose']*ar,tipo='dem',own=True,ord=ordem.get(x['saf'],99),chave=o['k'],
                                 t=f"{o['local']} · {o['nome']}"+(f" · parte sem O.S. ({c['txt']})" if c and f<1-1e-9 else ''),calc=f"{_nf(p['dose'],2)} {p['un']}/ha{_dem_orig(p)} × {_nfa(ar)} ha",loc=[o['local']]))
    for o in osd:
        if o['saf']!=x['saf']: continue
        for i in o['itens']:
            if i['q']>1e-9: novo(i['p'],i['g'],i['un'],i['preco'])   # insumo que só a O.S. usa
    for d in m.values(): d['evs']+=dem_os_evs(osd,d['nome'],x['saf'],ordem,tp)
    for s in sorted(ordem,key=lambda k:ordem[k]):
        if s==x['saf']: continue
        ag={}
        for o in occ:
            if o['saf']!=s: continue
            c=fr.get(o['k']); f=c['f'] if c else 1
            if not f>1e-9: continue
            for p in o['prods']:
                if p['nome'] not in m: continue
                a=ag.setdefault((p['nome'],o['dt']),dict(nome=p['nome'],dt=o['dt'] or '',q=0.0,n=0,chaves=[])); a['q']+=p['q']*f; a['n']+=1; a['chaves'].append(o['k'])
        for a in ag.values():
            m[a['nome']]['evs'].append(dict(dt=a['dt'],q=a['q'],tipo='dem',own=False,ord=ordem.get(s,99),chaves=a['chaves'],t=f"{x['nomes'].get(s,s)} · {a['n']} {'usos' if a['n']>1 else 'uso'}"))
    for d in m.values():
        da=lambda r: r['item']==d['nome'] and r['faz']==x['faz']
        d['evs']+=[dict(dt=r['dt'],q=r['q'],tipo='res',own=False,ord=0,chave=r['chave'],t=r['t']) for r in x['reservas'] if da(r)]
        d['evs']+=[dict(dt=r['dt'],q=r['q'],tipo='rec',own=False,ord=0,ref=r['ref'],t=r['t']) for r in x['recebDt'] if da(r)]
        d['res']=sum(r['q'] for r in x['reservas'] if da(r)); d['rec']=sum(r['q'] for r in x['recebDt'] if da(r)); d['est']=x['fisico'].get(d['nome'],0)
        cs=[r for r in x.get('sobra') or [] if da(r)]; d['cust']=sum(r['q'] for r in cs); d['custT']=[f"{_nfa(r['q'])} {d['un']} · {r['t']}" for r in cs]   # custódia sem uso (suprimento)
        # quarentena com laudo pendente: cobertura condicionada (liq com ela; cond = falta só se o laudo reprovar); reprovada não cobre (revisão do 853a6a8, achado 2)
        d['quarC']=(x.get('quar') or {}).get(d['nome'],0) or 0; d['quarRep']=(x.get('quarRep') or {}).get(d['nome'],0) or 0; d['quarRef']=[q for q in x.get('quarRef') or [] if q['item']==d['nome']]
        rF=cal01(d['est']+d['cust'],d['evs'],0.0,x['hoje'],x['viavel'])
        r=cal01(d['est']+d['cust']+d['quarC'],d['evs'],0.0,x['hoje'],x['viavel']) if d['quarC']>1e-9 else rF
        d['cond']=max(0.0,_r2(_r2(rF['liq'])-_r2(r['liq']))) if d['quarC']>1e-9 else 0; d['condFalta']=(rF['falta'] or '') if d['cond']>0.001 else ''
        lq=_r2(r['liq'])   # a quantidade a comprar é a que a solicitação leva (0,01 da unidade) e o valor sai dela: Planejar safra = Compra (calR2)
        d.update(liq=lq,falta=r['falta'],antes=r['antes'],tarde=r['tarde'],valor=lq*d['preco'],bruta=r['bruta'],real=r['real'],rup=r['rupRec'],cob=r['cob'],
                 uso=min([e['dt'] for e in d['evs'] if e['tipo']=='dem' and e.get('own') and e['dt'] and e['dt']>=x['hoje']] or ['']))
    return m
# chegada viável de uma compra nova (CAL-01 · reposicao_proposta_com_chegada_viavel): hoje + prazo mínimo de reposição (parâmetro de demonstração)
PRAZO_REPOSICAO=7
HOJE_ISO=iso_br(HOJE)
VIAVEL=(_dt.date.fromisoformat(HOJE_ISO)+_dt.timedelta(days=PRAZO_REPOSICAO)).isoformat()
def cal01(fis,evs,seg=0.0,hoje='',viavel=''):
    """Mesmo algoritmo de cal01.js: físico apto com reservas, demanda única por data, recebimento só cobre uso na data dele ou depois,
    reposição proposta entra no saldo. hoje: uso planejado antes de hoje já foi realizado (sai do físico e da demanda residual).
    viavel: falta antes dessa data é ruptura — recebimentos até lá a cobrem (a mais antiga primeiro) e o resto vira reposição na data viável.
    Devolve liq (da solicitação: eventos own), falta (1ª data com falta ou ruptura dela) e totais."""
    ks=set()
    for e in evs:
        if e['tipo']!='dem': continue
        if e.get('chave'): ks.add(e['chave'])
        ks.update(e.get('chaves') or [])
    real=0.0; nreal=0; E0=[]
    for i,e in enumerate(evs):
        if e['tipo']=='dem' and hoje and e['dt'] and e['dt']<hoje:
            if e.get('own'): real+=float(e['q']); nreal+=1
            continue
        E0.append((i,e))
    if viavel: E0.append((10**9,dict(dt=viavel,q=0,tipo='via',ord=0)))
    pri=lambda e: {'rec':0,'via':1,'res':2}.get(e['tipo'],3)
    E=[e for _,e in sorted(E0,key=lambda x:(x[1]['dt'],pri(x[1]),x[1].get('ord',0) or 0,x[0]))]
    ult=max([e['dt'] for e in E if e['tipo']=='dem' and e.get('own')] or [''])
    saldo=float(fis); bruta=rec=liq=tot=antes=rup=rup_via=0.0; falta=falta_tot=cob=None; bk=[]
    deficit=lambda: max(0.0,seg-saldo)
    for e in E:
        q=float(e['q'])
        if e['tipo']=='via':
            d=deficit()
            if d<=1e-9: continue
            own=sum(b['q'] for b in bk if b['own']); bk.clear(); liq+=own; rup_via+=own; tot+=d; saldo=seg
            if own>1e-9: cob=e['dt']
            continue
        if e['tipo']=='rec':
            d0=deficit(); saldo+=q; rec+=q; c=d0-deficit(); dono=False
            while c>1e-9 and bk:
                b=bk[0]; x=min(b['q'],c); b['q']-=x; c-=x
                if b['own']: dono=True
                if b['q']<=1e-9: bk.pop(0)
            if dono and not any(b['own'] for b in bk): cob=e['dt']
            continue
        if e['tipo']=='res' and e.get('chave') and e['chave'] in ks: continue
        own=(e['tipo']=='dem' and bool(e.get('own'))); d0=deficit(); saldo-=q; nec=rp=0.0
        if saldo<seg-1e-9:
            if not viavel or e['dt']>=viavel: nec=seg-saldo; saldo=seg
            else: rp=deficit()-d0; bk.append(dict(own=own,q=rp))
        if own:
            bruta+=q; liq+=nec; rup+=rp
            if (nec>1e-9 or rp>1e-9) and not falta: falta=e['dt']
        elif e['dt']<=ult: antes+=q-nec-rp
        tot+=nec
        if (nec>1e-9 or rp>1e-9) and not falta_tot: falta_tot=e['dt']
    tarde=sum(float(e['q']) for e in E if e['tipo']=='rec' and falta and e['dt']>falta)
    return dict(fis=float(fis),bruta=bruta,rec=rec,liq=liq,tot=tot,falta=falta,faltaTot=falta_tot,antes=antes,tarde=tarde,saldo=saldo,
                real=real,nreal=nreal,rup=rup,rupRec=max(0.0,rup-rup_via),cob=cob)
def checa_reservas():
    """Reservas da demanda (est_dem, nas duas fazendas) fecham com o reservado dos lotes da semente por insumo."""
    rs=[r for f in EST_FAZ for r in est_dem(None,f)['reservas']]; lt=_seed()['lotes'].values()
    return [(i,sum(r['q'] for r in rs if r['item']==i),sum(l['reservado'] for l in lt if l['prod']==i))
            for i in {l['prod'] for l in lt}|{r['item'] for r in rs}
            if abs(sum(r['q'] for r in rs if r['item']==i)-sum(l['reservado'] for l in lt if l['prod']==i))>1e-9]

if __name__=='__main__':
    d=demanda('S2627'); tot=sum(o['valor'] for o in d.values())
    for nm,o in sorted(d.items(),key=lambda x:(x[1]['grupo'],x[0])): print(f"{o['grupo']:12} {nm:32} bruta {o['bruta']:>10.1f} {o['un']} est {o['estoque']:>7} rec {o['receb']:>6} líq {o['liq']:>9.1f} valor R$ {o['valor']:>11,.2f}")
    print('TOTAL líquido R$', f'{tot:,.2f}')
    full=demanda('S2627',planos_extra={'c4':'SOJA-AT','c5':'SOJA-AT','c6':'SOJA-AT','c7':'SOJA-AT'})
    print('após aplicar SOJA-AT em T4,T3,P1,P2 → R$', f"{sum(o['valor'] for o in full.values()):,.2f}")

