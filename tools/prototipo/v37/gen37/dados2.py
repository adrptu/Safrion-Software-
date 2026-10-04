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
def C(id,local,tipo,cultura,variedade,area,plantio,meta,un_meta,plano,colheita=None,ro=False):
    return dict(id=id,fazenda='Santa Rita',local=local,tipo=tipo,cultura=cultura,variedade=variedade,area=area,plantio=plantio,meta=meta,un_meta=un_meta,plano=plano,colheita=colheita,ro=ro)
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
          C('e3','T3','Talhão inteiro','Milho','Híbrido AG 8700',96,'2025-10-20',170,'sc/ha','MILHO-SF',ro=True)],
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
def demanda(safra,ajustes=None,planos_extra=None):
    """Demanda por produto (unidade, preço, origens) e necessidade líquida por data (CAL-01) — igual ao cálculo da etapa 6 no JS (safra.js + cal01.js).
    estoque = físico apto (inclui reservas); receb = recebimentos previstos (total); liq/falta saem da projeção datada com as outras origens do mesmo estoque.
    bruta = demanda residual (usos de hoje em diante); real = usos planejados antes de hoje (já realizados); plano = total do plano."""
    ajustes=AJUSTES if ajustes is None else ajustes
    out={}; ordem={s['id']:i for i,s in enumerate(SAFRAS)}
    for c,a,p,dose,q in _ocorr_py(safra,ajustes,planos_extra):
        nm=prod_nome(p['prod'],c)
        o=out.setdefault(nm,dict(grupo=p['grupo'],un=p['un'],preco=p['preco'],bruta=0.0,orig=[],evs=[]))
        o['bruta']+=q; o['orig'].append((c['local'],a['nome'],dose,c['area'],q))
        o['evs'].append(dict(dt=data_atividade(c,a).isoformat(),q=q,tipo='dem',own=True,ord=ordem.get(safra,99),chave=f"{c['id']}|{a['id']}",
                             t=f"{c['local']} · {a['nome']}",calc=f"{_nf(dose,2)} {p['un']}/ha × {_nfa(c['area'])} ha"))   # área com até 2 casas (PRE-REV R5)
    for nm,o in out.items():
        o['evs']+=_outras_origens(safra,nm)
        o['estoque']=fisico_apto(nm); o['reservado']=sum(r['q'] for r in RESERVAS if r['item']==nm); o['receb']=RECEB.get(nm,0)
        r=cal01(o['estoque'],o['evs'],0.0,HOJE_ISO,VIAVEL); o['liq']=r['liq']; o['falta']=r['falta']; o['valor']=o['liq']*o['preco']
        o['plano']=o['bruta']; o['bruta']=r['bruta']; o['real']=r['real']; o['rup']=r['rupRec']; o['cob']=r['cob']
    return out
# ---- Fazenda Lagoa Grande (dados_lagoa_safra.py): safra de mamão nos 23 pivôs reais, planos, conjuntos e estoque ----
import dados_lagoa_safra as _DL
_DL.SAFRA['periodo']=periodo_txt(_DL.SAFRA['ini'],_DL.SAFRA['fim']); SAFRAS.append(_DL.SAFRA); CULTIVOS[_DL.SAFRA['id']]=_DL.CULTIVOS; PLANOS.extend(_DL.PLANOS); PLANO.update({p['id']:p for p in _DL.PLANOS}); CONJ.extend(_DL.CONJ)
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
# 1) junta quem trabalha em sequência antes de dividir a área; a sequência divide a janela da ocorrência (a maior entre as dela), começa a
#    de menor troca e cada outra entra com a sua troca (PRD 44.3: capacidade depois de respeitar simultaneidade e conflitos)
# 2) % fixos primeiro; o resto às sem % na proporção do rendimento (as mesmas horas); cada uma para na própria janela e a sequência para
#    quando as horas dela com as trocas enchem a janela; o que não cabe fica sem conjunto. Pendente diz a causa.
# 3) REND-RETORNO-1818 (S5): PLANO (demanda inteira pela partilha, sem janela) → necessidade da sequência e déficit; ATENDIDO (janelas);
#    SALDO (área sem conjunto + horas que faltam pelas premissas do plano). nec = atendido + saldo em ha e em horas-conjunto.
import math as _math
from fractions import Fraction as _Fr
def _rp_num(x):
    if x is None or x=='': return None
    if isinstance(x,bool): return _math.nan
    if isinstance(x,(int,float,_Fr)): return x if not (isinstance(x,float) and (_math.isnan(x) or _math.isinf(x))) else _math.nan
    try:
        n=float(str(x).strip().replace(',','.')); return n if not (_math.isnan(n) or _math.isinf(n)) else _math.nan
    except ValueError: return _math.nan
def _ok(n): return n is not None and not (isinstance(n,float) and _math.isnan(n))
def _rp_f(n):
    v=_math.floor(float(n)*100+0.5)/100
    return (str(int(v)) if v==int(v) else repr(v)).replace('.',',')
def repartir(Q,cfgs,pools=None):
    mot=[]
    def add(m):
        if m not in mot: mot.append(m)
    Q=_rp_num(Q)
    if not _ok(Q) or Q<0: add('área inválida'); Q=0
    it=[]
    for i,c in enumerate(cfgs or []):
        r,p,H,ch,d,tr,pe=(_rp_num(c.get(k)) for k in ('rend','part','jan','custo_h','diesel','troca','pess'))
        x=dict(i=i,id=c.get('id'),nome=c.get('nome') or f'Configuração {i+1}',r=r if _ok(r) and r>0 else None,p=p if _ok(p) and p>=0 else None,
               H=_math.inf if (H is None or not _ok(H) or H<0) else H,ch=ch if _ok(ch) and ch>=0 else None,d=d if _ok(d) and d>=0 else None,
               troca=tr if _ok(tr) and tr>0 else 0,pess=pe if _ok(pe) and pe>0 else 0,seq=bool(c.get('seq')),ativos=[a for a in (c.get('ativos') or []) if a],
               rec=c.get('rec') or {},t=0,q=0,h=0,ht=0,custo=None,diesel=None,emSeq=False,grupo=i)
        if H is not None and (not _ok(H) or H<0): add(x['nome']+': janela inválida, considerada sem limite')
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
    def junto(x,y): return (x['seq'] and y['seq']) or any(z in y['ativos'] for z in x['ativos'])   # nunca ao mesmo tempo
    def simul(us,k):   # maior uso simultâneo do grupo k entre usuários que podem trabalhar juntos
        n=len(us)
        if n>14: return sum(((_rp_num(x['rec'].get(k)) or 0) for x in us),0)
        mx=0
        for m in range(1,1<<n):
            ok=True; s_=0
            for i in range(n):
                if not ok: break
                if not m&(1<<i): continue
                s_+=_rp_num(us[i]['rec'].get(k)) or 0
                for j in range(i+1,n):
                    if m&(1<<j) and junto(us[i],us[j]): ok=False; break
            if ok and s_>mx: mx=s_
        return mx
    for k,pv in (pools or {}).items():
        un=_rp_num((pv or {}).get('un'))
        if not _ok(un): continue
        u_p=[x for x in cand_p if (_rp_num(x['rec'].get(k)) or 0)>0]; u_a=[x for x in u_p if x['H']>0]
        s_a=simul(u_a,k) if len(u_a)>1 else 0; s_p=simul(u_p,k) if len(u_p)>1 else 0
        ea=len(u_a)>1 and (un<=1 or s_a>un+1e-9); ep=len(u_p)>1 and (un<=1 or s_p>un+1e-9)   # 1 unidade: uma máquina só, como um ativo
        if ea:
            for x in u_a: U.une(u_a[0]['i'],x['i'])
        if ep:
            for x in u_p: UP.une(u_p[0]['i'],x['i'])
        if ea or ep:
            RS.append(('pl:'+str(k),u_p if ep else [],u_a if ea else [])); sm=s_a if ea else s_p
            add(f"{pv.get('nome') or k}"+(f": ao mesmo tempo precisariam de {_rp_f(sm)}, a fazenda tem {_rp_f(un)}; trabalham em sequência" if sm>un+1e-9 else f": a fazenda tem {_rp_f(un)}; quem a usa divide a janela dela"))
    def troca_de(xs):
        if len(xs)<2: return 0
        return sum((x['troca'] for x in xs),0)-min(x['troca'] for x in xs)
    def troca_r(xs,P,V):   # a troca que o decorrido cobra: a de cada membro, menos a menor troca do fecho se um membro a tem
        if len(xs)<2: return 0
        g=V.raiz(xs[0]['i']); mn=min((y['troca'] for y in P if V.raiz(y['i'])==g),default=_math.inf)
        return sum((x['troca'] for x in xs),0)-(mn if any(x['troca']==mn for x in xs) else 0)
    W={}; jan={}; pista={}; pista_a={}
    for k,xs,xa in RS:
        w=max((x['H'] for x in xs+xa),default=-_math.inf)
        if w==_math.inf or w==-_math.inf: continue
        W[k]=w
        if len(xs)>1: pista[k]=xs
        if len(xa)>1: pista_a[k]=xa; jan[k]=w-troca_r(xa,cand,U)
    def pl(x): return [g for g in jan if any(y is x for y in pista_a[g])]   # restrições de janela da divisão de uma configuração
    def aloca(ad):
        q=[0]*len(it); saldo=0; cz={}; uso={}
        for x in fx:
            t=x['t']
            if t<=1e-12: continue
            if x['r'] is None: saldo+=t; cz['rend']=1; ad(x['nome']+': sem rendimento válido (ha/h), a parte dela fica sem conjunto'); continue
            q[x['i']]=min(t,x['r']*x['H'])
            if t-q[x['i']]>1e-9: saldo+=t-q[x['i']]; cz['jan']=1; ad(f"{x['nome']}: a parte fixa não cabe na janela de {_rp_f(x['H'])} h")
        cab=q[:]; cortes=[]   # o que cabia na própria janela; o motivo diz a fração final, depois de todas as restrições
        for g in jan:
            xs=[x for x in pista_a[g] if x['p'] is not None and q[x['i']]>0]; hf=sum((q[x['i']]/x['r'] for x in xs),0); B=max(0,jan[g])
            if hf>B+1e-9:
                f=B/hf
                for x in xs: n=q[x['i']]*f; saldo+=q[x['i']]-n; q[x['i']]=n
                cz['seq']=1; cortes.append(g)
        for g in cortes:
            fs=[q[x['i']]/cab[x['i']] for x in pista_a[g] if x['p'] is not None and cab[x['i']]>0]; mn,mx=min(fs),max(fs)
            ad(f"as partes fixas em sequência não cabem na janela de {_rp_f(W[g])} h: "+(f'cada uma faz {_rp_f(mn*100)} %' if mx-mn<=1e-9 else f'fazem de {_rp_f(mn*100)} % a {_rp_f(mx*100)} %')+' do que cabia na própria janela')
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
                rest=R; at=livres[:]; bj=False; bs=False
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
                            if tl[g]<=e: bs=True
                        if x['H']<=e: bj=True
                    fzi={x['i'] for x in fz}; at=[x for x in at if x['i'] not in fzi]
                if rest>1e-9:
                    saldo+=rest
                    if bs: cz['seq']=1; ad('em sequência dividem a mesma janela: a área que não cabe fica sem conjunto')
                    if bj or not bs: cz['jan']=1; ad('as janelas não comportam toda a área')
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
    conflito=False; deficit=0
    P1=[x for x in cand_p if q1[x['i']]>1e-12]
    for g in pista:
        xs=[x for x in pista[g] if q1[x['i']]>1e-12]
        if len(xs)<2: continue
        nec=sum((q1[x['i']]/x['r'] for x in xs),0)+troca_r(xs,P1,UP)
        if nec>W[g]+1e-9: conflito=True; deficit=max(deficit,nec-W[g]); add(f"em sequência precisam de {_rp_f(nec)} h para {_rp_f(sum((q1[x['i']] for x in xs),0))} ha; a janela tem {_rp_f(W[g])} h")
    grp={}
    for x in it:
        if x['q']>1e-12: grp.setdefault(raiz(x['i']),[]).append(x)
    decorrido=0; troca_t=0
    for g in sorted(grp):
        xs=grp[g]; soma=0; mn=min(x['troca'] for x in xs)
        em_r=lambda x: any(any(y is x for y in pista_a[k]) for k in jan)
        ini=next((x for x in xs if x['troca']==mn and em_r(x)),None) or next(x for x in xs if x['troca']==mn)   # no empate, a que divide janela
        for x in xs:
            x['h']=x['q']/x['r']; tr=0
            if len(xs)>1 and x is not ini: tr=x['troca']
            x['ht']=x['h']+tr; troca_t+=tr; x['emSeq']=len(xs)>1; x['grupo']=g; soma+=x['ht']
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
    causa='' if not pend else ('sem conjunto' if cz.get('cfg') else ('sem rendimento' if cz.get('rend') else ('sem horas na janela' if (cz.get('jan') or cz.get('seq')) else 'partes fixas abaixo de 100 %')))
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
                custoHa=(custo/alocado) if (custo_ok and alocado>1e-12) else None,diesel=diesel,dieselOk=diesel_ok,hh=hh,conflito=conflito,deficit=deficit,nec=nec,falta=falta,motivos=mot,itens=it)
# <<< REPARTIR
def plano_op(safra):
    """Espelho dos totais da etapa 4 (Confira o plano operacional) com os dados iniciais: área, horas-conjunto, custo de operação,
    diesel, horas-homem, área sem conjunto e ocorrências pendentes; as configurações vêm de cfgs_rend e os grupos de recursos de RECURSOS.
    REND-RETORNO-1818: também as horas-conjunto necessárias (nec_h = hconj + falta_h) e a área sem horas calculáveis (sem_h) das etapas 4 e 5."""
    pools={r['id']:dict(un=r['un'],nome=r['nome']) for r in RECURSOS}
    t=dict(area=0,hconj=0,cop=0,diesel=0,hh=0,saldo=0,pend=0,conflito=0,ocorr=0,multi=0,nec_h=0,falta_h=0,sem_h=0)
    for c in CULTIVOS[safra]:
        pl=PLANO.get(c['plano']) if c['plano'] else None
        if not pl or pl['cultura']!=c['cultura']: continue
        for a in pl['atividades']:
            cfs=cfgs_rend(safra,a['op'],a['nome']); rp=repartir(c['area'],[cfg_in(x) for x in cfs],pools)
            t['ocorr']+=1; t['area']+=c['area']; t['hconj']+=rp['hconj'] or 0; t['cop']+=rp['custo']; t['diesel']+=rp['diesel']; t['hh']+=rp['hh']; t['saldo']+=rp['saldo']
            t['pend']+=1 if rp['pendente'] else 0; t['conflito']+=1 if rp['conflito'] else 0; t['multi']+=1 if len(cfs)>1 else 0
            t['nec_h']+=rp['nec']['hconj'] or 0; t['falta_h']+=rp['falta']['hconj'] or 0; t['sem_h']+=rp['falta']['semHoras']
    return t
def js_data():
    return dict(meses=MESES,dias=DIAS_UTEIS,safras=SAFRAS,tipos=TIPOS,planos=PLANOS,cultivos=CULTIVOS,ajustes=AJUSTES,conj=CONJ,recursos=RECURSOS,estoque=ESTOQUE,receb=RECEB,
                fisico={k:fisico_apto(k) for k in ESTOQUE},reservas=RESERVAS,recebDt=RECEB_DT,
                quar={l['item']:l['quarentena'] for l in LOTES if l['quarentena']})
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
SOL_INICIAL=dict(id='SOL-2026-07',safra='S2627',origem='Planejar safra · Safra 2026/27 · etapa 6',enviada='23/09/2026 10:40',por='Ana (gestora)')
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
# reservas ativas por destino (o físico apto as inclui; LOTES.reservado = soma delas por insumo). chave = cultivo|atividade quando a reserva é da
# mesma demanda do plano (conta uma vez); sem chave = outro destino, entra como demanda na data da reserva.
RESERVAS=[dict(item='Fungicida A',q=65,dt='2026-09-24',t='Reserva REQ-039 · OS-0424 (P2)',chave=None,faz='Santa Rita')]
def fisico_apto(item):
    """Físico apto (fora quarentena) = disponível + reservado. ESTOQUE guarda o disponível por item (checa_coerencia)."""
    return ESTOQUE.get(item,0)+sum(l['reservado'] for l in LOTES if l['item']==item)
# recebimentos previstos com data (pedidos em aberto; o calcário da Lagoa Grande não tem PC no protótipo: pedido de 30/09)
RECEB_DT=[dict(item=p['item'],q=p['a_entregar'],dt=iso_br(p['previsao']),ref=p['id'],t=f"Recebimento {p['id']} ({next(f['nome'] for f in FORNECEDORES if f['id']==p['f'])})")
          for p in PEDIDOS if p['a_entregar']]+[dict(item='Calcário dolomítico filler',q=50000,dt='2026-09-30',ref=None,t='Recebimento previsto (pedido de 30/09)')]
def _outras_origens(safra,nm):
    """Outras origens do mesmo estoque para o insumo nm: safras abertas da mesma fazenda (agregadas por data), reservas e recebimentos datados."""
    me=next((s for s in SAFRAS if s['id']==safra),None); faz=(me or {}).get('fazenda','Santa Rita'); evs=[]
    for i,s in enumerate(SAFRAS):
        if s['id']==safra or s['ro'] or s['fazenda']!=faz: continue
        ag={}
        for c,a,p,dose,q in _ocorr_py(s['id'],AJUSTES,None):
            if prod_nome(p['prod'],c)!=nm: continue
            dt=data_atividade(c,a).isoformat(); x=ag.setdefault(dt,dict(q=0.0,n=0,chaves=[])); x['q']+=q; x['n']+=1; x['chaves'].append(f"{c['id']}|{a['id']}")
        for dt,x in ag.items():
            evs.append(dict(dt=dt,q=x['q'],tipo='dem',own=False,ord=i,chaves=x['chaves'],t=f"{s['nome']} · {x['n']} {'usos' if x['n']>1 else 'uso'}"))
    evs+=[dict(dt=r['dt'],q=r['q'],tipo='res',own=False,ord=0,chave=r['chave'],t=r['t']) for r in RESERVAS if r['item']==nm and r['faz']==faz]
    evs+=[dict(dt=r['dt'],q=r['q'],tipo='rec',own=False,ord=0,ref=r['ref'],t=r['t']) for r in RECEB_DT if r['item']==nm]
    return evs
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
    """RESERVAS fecham com LOTES.reservado por insumo."""
    return [(i,sum(r['q'] for r in RESERVAS if r['item']==i),sum(l['reservado'] for l in LOTES if l['item']==i))
            for i in {l['item'] for l in LOTES}|{r['item'] for r in RESERVAS}
            if abs(sum(r['q'] for r in RESERVAS if r['item']==i)-sum(l['reservado'] for l in LOTES if l['item']==i))>1e-9]

if __name__=='__main__':
    d=demanda('S2627'); tot=sum(o['valor'] for o in d.values())
    for nm,o in sorted(d.items(),key=lambda x:(x[1]['grupo'],x[0])): print(f"{o['grupo']:12} {nm:32} bruta {o['bruta']:>10.1f} {o['un']} est {o['estoque']:>7} rec {o['receb']:>6} líq {o['liq']:>9.1f} valor R$ {o['valor']:>11,.2f}")
    print('TOTAL líquido R$', f'{tot:,.2f}')
    full=demanda('S2627',planos_extra={'c4':'SOJA-AT','c5':'SOJA-AT','c6':'SOJA-AT','c7':'SOJA-AT'})
    print('após aplicar SOJA-AT em T4,T3,P1,P2 → R$', f"{sum(o['valor'] for o in full.values()):,.2f}")

