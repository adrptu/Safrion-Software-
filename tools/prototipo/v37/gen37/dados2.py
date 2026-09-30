# -*- coding: utf-8 -*-
"""Mundo de dados dos processos (menu vigente): Planejar safra → Compra de insumos → Estoque; Planos agronômicos; O.S.
Fonte única: telas geradas e cálculo em JS (SAF) usam estes dados; a demanda calculada aqui (Python) espelha a do JS."""
import datetime as _dt, json
HOJE='23/09/2026'
MESES=[('2026-09','set/26'),('2026-10','out/26'),('2026-11','nov/26'),('2026-12','dez/26'),('2027-01','jan/27'),('2027-02','fev/27'),
       ('2027-03','mar/27'),('2027-04','abr/27'),('2027-05','mai/27'),('2027-06','jun/27'),('2027-07','jul/27'),('2027-08','ago/27')]
DIAS_UTEIS={'2026-09':24,'2026-10':22,'2026-11':23,'2026-12':21,'2027-01':21,'2027-02':19,'2027-03':22,'2027-04':23,'2027-05':24,'2027-06':24,'2027-07':25,'2027-08':25}
SAFRAS=[
 dict(id='S2627',nome='Safra 2026/27',periodo='set/2026 – ago/2027',fazenda='Santa Rita',estado='Em planejamento',ro=False),
 dict(id='S27SF',nome='Safrinha 2027',periodo='fev – jul/2027',fazenda='Santa Rita',estado='Rascunho',ro=False),
 dict(id='S2526',nome='Safra 2025/26',periodo='set/2025 – ago/2026',fazenda='Santa Rita',estado='Encerrada',ro=True),
]
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
# recursos (etapa 5): capacidade = unidades × dias úteis × jornada × turnos − manutenção
RECURSOS=[
 dict(id='trator',nome='Tratores',un=4,jornada=10,turnos=1,manut=24),
 dict(id='pulv',nome='Pulverizadores',un=1,jornada=10,turnos=1,manut=16),
 dict(id='plant',nome='Plantadeiras',un=1,jornada=10,turnos=1,manut=16),
 dict(id='dist',nome='Distribuidores',un=1,jornada=10,turnos=1,manut=8),
 dict(id='colh',nome='Colhedoras',un=1,jornada=9,turnos=1,manut=16),
 dict(id='oper',nome='Operadores e equipe',un=8,jornada=9,turnos=1,manut=0),
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
def demanda(safra,ajustes=None,planos_extra=None):
    """Demanda bruta por produto (unidade, preço, origens) — igual ao cálculo da etapa 6 no JS."""
    ajustes=AJUSTES if ajustes is None else ajustes
    out={}
    for c in CULTIVOS[safra]:
        pid=(planos_extra or {}).get(c['id'],c['plano'])
        if not pid: continue
        for a in PLANO[pid]['atividades']:
            for i,p in enumerate(a['prods']):
                dose=ajustes.get(c['id'],{}).get(f"{a['id']}|{i}",p['dose'])
                nm=prod_nome(p['prod'],c); q=dose*c['area']
                o=out.setdefault(nm,dict(grupo=p['grupo'],un=p['un'],preco=p['preco'],bruta=0.0,orig=[]))
                o['bruta']+=q; o['orig'].append((c['local'],a['nome'],dose,c['area'],q))
    for nm,o in out.items():
        o['estoque']=ESTOQUE.get(nm,0); o['receb']=RECEB.get(nm,0)
        o['liq']=max(0.0,o['bruta']-o['estoque']-o['receb']); o['valor']=o['liq']*o['preco']
    return out
def js_data():
    return dict(meses=MESES,dias=DIAS_UTEIS,safras=SAFRAS,tipos=TIPOS,planos=PLANOS,cultivos=CULTIVOS,ajustes=AJUSTES,conj=CONJ,recursos=RECURSOS,estoque=ESTOQUE,receb=RECEB)
if __name__=='__main__':
    d=demanda('S2627'); tot=sum(o['valor'] for o in d.values())
    for nm,o in sorted(d.items(),key=lambda x:(x[1]['grupo'],x[0])): print(f"{o['grupo']:12} {nm:32} bruta {o['bruta']:>10.1f} {o['un']} est {o['estoque']:>7} rec {o['receb']:>6} líq {o['liq']:>9.1f} valor R$ {o['valor']:>11,.2f}")
    print('TOTAL líquido R$', f'{tot:,.2f}')
    full=demanda('S2627',planos_extra={'c4':'SOJA-AT','c5':'SOJA-AT','c6':'SOJA-AT','c7':'SOJA-AT'})
    print('após aplicar SOJA-AT em T4,T3,P1,P2 → R$', f"{sum(o['valor'] for o in full.values()):,.2f}")

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
REQUISICOES=[  # entregas por O.S. aprovada (Estoque · etapa 2) — só O.S. aprovada/liberada tem requisição
 dict(id='REQ-031',os='OS-0417',item='MAP 11-52',un='sc 50 kg',solicitado=100,entregue=100,consumido=70,dev_declarada=20,dev_recebida=20,custodia=10,estado='Em conferência'),
 dict(id='REQ-035',os='OS-0421',item='Fungicida A',un='L',solicitado=175,entregue=160,consumido=95,dev_declarada=0,dev_recebida=0,custodia=65,estado='Em execução'),
 dict(id='REQ-036',os='OS-0420',item='Semente de soja 58 W',un='kg',solicitado=5200,entregue=1560,consumido=1560,dev_declarada=0,dev_recebida=0,custodia=0,estado='Impedida · ativo bloqueado'),
 dict(id='REQ-038',os='OS-0418',item='Ureia 45%',un='kg',solicitado=1140,entregue=0,consumido=0,dev_declarada=0,dev_recebida=0,custodia=0,estado='Aguardando aprovação da O.S.'),
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
