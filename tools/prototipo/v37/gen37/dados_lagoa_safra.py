# -*- coding: utf-8 -*-
"""Fazenda Lagoa Grande (Lagoa Grande · MG): safra de mamão Formosa nos 23 pivôs do KML do proprietário, planos agronômicos
de implantação e de produção irrigada, e O.S. em todas as fases (dados de demonstração sobre a geometria real).

Coerência com a imagem de satélite da fazenda (dados_lagoa_fonte.DIR): NDVI alto = produção; médio = formação;
baixo = plantio recente; solo exposto = preparo ou renovação.
Equipe e insumos da Lagoa Grande têm nomes próprios (abamectina, tebuconazol, sulfato de potássio…) para não alterar os saldos da
demonstração da Santa Rita; o estoque abaixo é o saldo apto depois das entregas já feitas às O.S."""

FAZ = 'Lagoa Grande'
SAFRA = dict(id='LG2627', nome='Safra Mamão 2026/27', ini='2026-09-01', fim='2027-08-31', fazenda=FAZ, estado='Em planejamento', ro=False)
# pivôs do KML: número → hectares declarados
from dados_lagoa_fonte import PIVOS_HA as PIVOS   # real só no Mac; sintético fora dele
def nome(n): return f'Pivô {n}'
def pid(n): return f'PV{n:02d}'
TALHOES = {nome(n): ha for n, ha in PIVOS.items()}           # talhão (pivô) → hectares
TALFAZ = {nome(n): FAZ for n in PIVOS}                        # talhão → fazenda
PID_DE = {nome(n): pid(n) for n in PIVOS}                     # nome do talhão → id do mapa

# ---------- planos agronômicos ----------
def A(i, nm, op, g, prods): return dict(id=i, nome=nm, op=op, g=g, prods=[dict(grupo=a, prod=b, dose=c, un=d, preco=e) for a, b, c, d, e in prods])
DAP = lambda d: dict(tipo='DAP', dias=d, data=None)
DATA = lambda s: dict(tipo='DATA', dias=None, data=s)
PLANOS = [
 dict(id='MAMAO-IMP', nome='Mamão Formosa · implantação irrigada', cultura='Mamão Formosa', versao=1, estado='Publicado', atividades=[
   A('i1', 'Calagem', 'Adubação a lanço', DAP(-60), [('Corretivos', 'Calcário dolomítico filler', 2000.0, 'kg', 0.18)]),
   A('i2', 'Gessagem', 'Adubação a lanço', DAP(-45), [('Corretivos', 'Gesso agrícola', 1000.0, 'kg', 0.22)]),
   A('i3', 'Dessecação pré-plantio', 'Pulverização', DAP(-20), [('Herbicidas', 'Glifosato 480', 3.0, 'L', 28.0), ('Adjuvantes', 'Óleo mineral', 0.5, 'L', 18.0)]),
   A('i4', 'Plantio de mudas e adubação de cova', 'Plantio de mudas', DAP(0), [('Mudas', 'Muda de mamão Formosa', 1850.0, 'un', 0.85), ('Fertilizantes', 'Superfosfato simples', 400.0, 'kg', 1.95)]),
   A('i5', 'Fertirrigação de arranque', 'Fertirrigação', DAP(20), [('Fertilizantes', 'Nitrato de amônio', 25.0, 'kg', 3.6), ('Fertilizantes', 'Ácido bórico', 1.0, 'kg', 14.0)]),
   A('i6', 'Controle de pulgão e ácaro', 'Pulverização', DAP(30), [('Inseticidas', 'Acetamiprido 200 SP', 0.25, 'kg', 210.0), ('Inseticidas', 'Abamectina 18 EC', 0.4, 'L', 85.0)]),
   A('i7', 'Fertirrigação de formação 1', 'Fertirrigação', DAP(45), [('Fertilizantes', 'Nitrato de amônio', 30.0, 'kg', 3.6), ('Fertilizantes', 'Sulfato de potássio', 25.0, 'kg', 4.8)]),
   A('i8', 'Sexagem e desbaste', 'Tratos culturais', DAP(90), []),
   A('i9', 'Fertirrigação de formação 2', 'Fertirrigação', DAP(100), [('Fertilizantes', 'Sulfato de potássio', 40.0, 'kg', 4.8), ('Fertilizantes', 'Sulfato de magnésio', 20.0, 'kg', 2.1)]),
   A('i10', 'Fungicida preventivo (antracnose e oídio)', 'Pulverização', DAP(120), [('Fungicidas', 'Tebuconazol 200 EC', 1.0, 'L', 62.0)]),
   A('i11', 'Fertirrigação de pré-florada', 'Fertirrigação', DAP(150), [('Fertilizantes', 'Sulfato de potássio', 50.0, 'kg', 4.8), ('Fertilizantes', 'Ácido bórico', 1.0, 'kg', 14.0)]),
   A('i12', 'Início da colheita', 'Colheita de frutas', DAP(270), []),
 ]),
 dict(id='MAMAO-PROD', nome='Mamão Formosa · produção irrigada', cultura='Mamão Formosa', versao=1, estado='Publicado', atividades=[
   A('q1', 'Fertirrigação NK · out', 'Fertirrigação', DATA('2026-10-05'), [('Fertilizantes', 'Sulfato de potássio', 45.0, 'kg', 4.8), ('Fertilizantes', 'Nitrato de amônio', 20.0, 'kg', 3.6)]),
   A('q2', 'Controle de ácaro e cochonilha', 'Pulverização', DATA('2026-10-12'), [('Inseticidas', 'Abamectina 18 EC', 0.5, 'L', 85.0), ('Adjuvantes', 'Óleo mineral', 1.0, 'L', 18.0)]),
   A('q3', 'Colheita · out/26', 'Colheita de frutas', DATA('2026-10-20'), []),
   A('q4', 'Fungicida para antracnose', 'Pulverização', DATA('2026-10-26'), [('Fungicidas', 'Tebuconazol 200 EC', 1.0, 'L', 62.0)]),
   A('q5', 'Fertirrigação Ca-B · nov', 'Fertirrigação', DATA('2026-11-05'), [('Fertilizantes', 'Nitrato de cálcio', 40.0, 'kg', 4.2), ('Fertilizantes', 'Ácido bórico', 1.0, 'kg', 14.0)]),
   A('q6', 'Desbrota e limpeza', 'Tratos culturais', DATA('2026-11-16'), []),
   A('q7', 'Colheita · nov/26', 'Colheita de frutas', DATA('2026-11-20'), []),
   A('q8', 'Fertirrigação NK · dez', 'Fertirrigação', DATA('2026-12-05'), [('Fertilizantes', 'Sulfato de potássio', 45.0, 'kg', 4.8), ('Fertilizantes', 'Nitrato de amônio', 20.0, 'kg', 3.6)]),
   A('q9', 'Controle de mosca-branca', 'Pulverização', DATA('2026-12-10'), [('Inseticidas', 'Acetamiprido 200 SP', 0.3, 'kg', 210.0)]),
   A('q10', 'Colheita · dez/26', 'Colheita de frutas', DATA('2026-12-18'), []),
   A('q11', 'Adubação de cobertura', 'Adubação a lanço', DATA('2027-01-15'), [('Fertilizantes', 'Sulfato de potássio', 150.0, 'kg', 4.8), ('Fertilizantes', 'Sulfato de magnésio', 50.0, 'kg', 2.1)]),
   A('q12', 'Colheita · jan/27', 'Colheita de frutas', DATA('2027-01-20'), []),
 ]),
]
# operações novas da fruticultura (rendimento do conjunto e equipe da etapa 3 do Planejar safra)
CONJ = [
 dict(id='r9', op='Plantio de mudas', conj='Sulcador + equipe de plantio (8 pessoas)', rend=0.25, maq=120, impl=30, pess=8, pess_rs=32, prod=0, rec={'trator': 1, 'oper': 8}),
 dict(id='r10', op='Tratos culturais', conj='Equipe de tratos culturais (6 pessoas)', rend=0.6, maq=0, impl=0, pess=6, pess_rs=30, prod=0, rec={'oper': 6}),
 dict(id='r11', op='Colheita de frutas', conj='Equipe de colheita (10 pessoas) + trator com carreta', rend=0.45, maq=150, impl=25, pess=10, pess_rs=32, prod=0, rec={'trator': 1, 'oper': 10}),
]
# ---------- cultivos (um por pivô): (pivô, variedade, plantio, plano) ----------
_C = [(6, 'Tainung 1', '2025-03-12', 'MAMAO-PROD'), (24, 'Tainung 1', '2025-03-12', 'MAMAO-PROD'), (18, 'Tainung 1', '2025-04-02', 'MAMAO-PROD'),
      (19, 'Tainung 1', '2025-04-02', 'MAMAO-PROD'), (4, 'Tainung 1', '2025-06-10', 'MAMAO-PROD'), (23, 'Tainung 1', '2025-07-08', 'MAMAO-PROD'),
      (9, 'UENF/Caliman 01', '2025-08-05', 'MAMAO-PROD'), (20, 'UENF/Caliman 01', '2025-08-05', 'MAMAO-PROD'), (22, 'Tainung 1', '2025-09-02', 'MAMAO-PROD'),
      (2, 'UENF/Caliman 01', '2025-09-02', 'MAMAO-PROD'), (17, 'Tainung 1', '2025-10-07', 'MAMAO-PROD'),
      (21, 'Tainung 1', '2026-03-10', 'MAMAO-IMP'), (10, 'Tainung 1', '2026-03-24', 'MAMAO-IMP'), (14, 'Tainung 1', '2026-04-07', 'MAMAO-IMP'),
      (3, 'Tainung 1', '2026-05-05', 'MAMAO-IMP'), (1, 'Tainung 1', '2026-05-19', 'MAMAO-IMP'),
      (15, 'Tainung 1', '2026-07-14', 'MAMAO-IMP'), (7, 'Tainung 1', '2026-07-28', 'MAMAO-IMP'), (8, 'Tainung 1', '2026-08-11', 'MAMAO-IMP'), (5, 'Tainung 1', '2026-08-25', 'MAMAO-IMP'),
      (11, 'Tainung 1', '2026-10-06', 'MAMAO-IMP'), (13, 'Tainung 1', '2026-10-20', 'MAMAO-IMP'), (12, 'Tainung 1', '2026-11-24', 'MAMAO-IMP')]
CULTIVOS = [dict(id=f'lg{n:02d}', fazenda=FAZ, local=nome(n), tipo='Talhão inteiro', cultura='Mamão Formosa', variedade=v, area=PIVOS[n], plantio=d,
                 meta=(50 if p == 'MAMAO-PROD' else 45), un_meta='t/ha/ano', plano=p, colheita=None, ro=False) for n, v, d, p in sorted(_C)]
RENOVACAO = {12: 'renovação · lavoura velha erradicada em 12–13/09 (OS-0509)'}
# ---------- estoque apto da Lagoa Grande (depois das entregas já feitas) e pedidos a receber ----------
ESTOQUE = {'Calcário dolomítico filler': 60000, 'Gesso agrícola': 40000, 'Muda de mamão Formosa': 46000, 'Superfosfato simples': 12000, 'Ácido bórico': 150,
           'Sulfato de magnésio': 3000, 'Sulfato de potássio': 6000, 'Nitrato de amônio': 4500, 'Abamectina 18 EC': 120, 'Acetamiprido 200 SP': 40,
           'Tebuconazol 200 EC': 150}
RECEB = {'Calcário dolomítico filler': 50000}
EMB = {'Calcário dolomítico filler': 'granel', 'Gesso agrícola': 'granel', 'Muda de mamão Formosa': 'bandeja 50 mudas', 'Superfosfato simples': 'saco 50 kg',
       'Sulfato de potássio': 'saco 25 kg', 'Nitrato de amônio': 'saco 25 kg', 'Ácido bórico': 'saco 25 kg', 'Abamectina 18 EC': 'galão 5 L',
       'Tebuconazol 200 EC': 'galão 5 L', 'Acetamiprido 200 SP': 'pacote 1 kg'}

# ---------- O.S. da Lagoa Grande (todas as fases) ----------
def _o(i, tipo, n, etapa, selo, real, janela, resp, chave, extra=None):
    ha = PIVOS[n]; area = ha
    d = dict(id=i, tipo=tipo, talhao=nome(n), area=area, etapa=etapa, selo=selo, realizado=real, saldo=max(0, area - real), janela=janela, resp=resp,
             detalhe=None, faz=FAZ, saf='2026/27', chave=chave)
    if extra: d['selos_extra'] = extra
    return d
ORDENS = [
 _o('OS-0501', 'Dessecação pré-plantio', 13, 'A liberar', None, 0, '30/09 (DAP −20)', 'Wesley', 'lg13|i3'),
 _o('OS-0502', 'Calagem', 12, 'A liberar', None, 0, '25–27/09 (DAP −60)', 'Lúcia', 'lg12|i1'),
 _o('OS-0503', 'Plantio de mudas · Tainung 1', 11, 'Liberadas', None, 0, '06–08/10', 'Renato', 'lg11|i4'),
 _o('OS-0504', 'Controle de ácaro e cochonilha', 6, 'Liberadas', None, 0, '24–25/09', 'Wesley', 'lg06|q2'),
 _o('OS-0505', 'Colheita · semana 39', 19, 'Em execução', 'Parcial · dia 2 de 3', 28, '21–24/09', 'Sérgio', None),
 _o('OS-0506', 'Fertirrigação NK', 4, 'Em execução', 'Parcial · turno 1 de 2', 34, '22–24/09', 'Joaquim', None),
 _o('OS-0507', 'Fertirrigação de arranque', 5, 'Em execução', 'Impedida · bomba em manutenção', 20, '21–23/09', 'Joaquim', 'lg05|i5'),
 _o('OS-0508', 'Fungicida para antracnose', 23, 'Em conferência', None, 60, '19–20/09', 'Wesley', None),
 _o('OS-0509', 'Erradicação da lavoura velha', 12, 'Encerradas', None, 55, '12–13/09', 'Wesley', None),
 _o('OS-0510', 'Colheita · semana 38', 6, 'Encerradas', None, 86, '16–18/09', 'Sérgio', None),
 _o('OS-0511', 'Sexagem e desbaste', 15, 'A liberar', None, 0, '12–14/10 (DAP +90)', 'Sérgio', 'lg15|i8'),
]
for _x in ORDENS:
    if not _x['chave']: del _x['chave']
VERSAO = {'OS-0501': 'v1', 'OS-0502': 'v1', 'OS-0503': 'v1', 'OS-0504': 'v1', 'OS-0505': 'v1', 'OS-0506': 'v1',
          'OS-0507': 'v1', 'OS-0508': 'v1', 'OS-0509': 'v1', 'OS-0510': 'v1', 'OS-0511': 'v1'}
AP = {'OS-0505': [('21/09', 1, 14, 'Conferido'), ('22/09', 2, 14, 'Provisório'), ('24/09', 3, 14, 'Previsto')],
      'OS-0506': [('22/09', 1, 34, 'Provisório'), ('24/09', 2, 34, 'Previsto')],
      'OS-0507': [('21/09', 1, 20, 'Conferido')],
      'OS-0508': [('19/09', 1, 30, 'Conferido'), ('20/09', 2, 30, 'Conferido')],
      'OS-0509': [('12/09', 1, 28, 'Conferido'), ('13/09', 2, 27, 'Conferido')],
      'OS-0510': [('16/09', 1, 43, 'Conferido'), ('18/09', 2, 43, 'Conferido')]}
COND = {'OS-0501': 'Liberação · Ana (agrônoma), que pode ajustar antes. Dessecação a 20 dias do plantio das mudas (DAP −20).',
        'OS-0502': 'Ana (agrônoma) libera e reserva 110.000 kg de calcário; o estoque tem 60.000 kg e o pedido de 50.000 kg chega em 30/09.',
        'OS-0503': 'Liberada · REQ-021 reservou 44.400 mudas e 9.600 kg de superfosfato simples. Próximo passo: Edson entrega no almoxarifado e Renato confirma no app.',
        'OS-0504': 'Abamectina entregue a Wesley e confirmada no app. Próximo passo: iniciar na janela 24–25/09.',
        'OS-0505': 'Dia 2 da colheita em conferência · 28 de 42 ha colhidos; 14 ha no dia 3 (24/09).',
        'OS-0506': 'Turno 1 com 34 ha fertirrigados (provisório); turno 2 previsto para 24/09.',
        'OS-0507': 'Bomba do Pivô 5 em manutenção (OM-0251): 20 de 56 ha fertirrigados; saldo parado até a troca do selo mecânico.',
        'OS-0508': 'Apontamentos conferidos (60 ha) e nada em custódia. Próximo passo: conferir e encerrar.',
        'OS-0509': 'Nenhuma · ordem encerrada, somente consulta.',
        'OS-0510': 'Nenhuma · ordem encerrada, somente consulta.',
        'OS-0511': 'Operação manual sem insumos. Próximo passo: Ana (agrônoma) libera para execução.'}
ORIG = {'OS-0501': ['Safra Mamão 2026/27 · Pivô 13 · plano MAMAO-IMP', 'Dessecação pré-plantio · 30 ha'],
        'OS-0502': ['Safra Mamão 2026/27 · Pivô 12 (renovação) · plano MAMAO-IMP', 'Calagem pela análise de solo · 2 t/ha'],
        'OS-0503': ['Safra Mamão 2026/27 · Pivô 11 · plano MAMAO-IMP', 'Requisição REQ-021 · mudas e superfosfato simples'],
        'OS-0504': ['Safra Mamão 2026/27 · Pivô 6 · plano MAMAO-PROD', 'Requisição REQ-022 · Abamectina 18 EC, 43 L'],
        'OS-0505': ['Safra Mamão 2026/27 · Pivô 19 · colheita semanal'], 'OS-0506': ['Safra Mamão 2026/27 · Pivô 4 · plano MAMAO-PROD', 'Requisição REQ-023'],
        'OS-0507': ['Safra Mamão 2026/27 · Pivô 5 · plano MAMAO-IMP', 'Requisição REQ-024'], 'OS-0508': ['Safra Mamão 2026/27 · Pivô 23 · plano MAMAO-PROD', 'Requisição REQ-025'],
        'OS-0509': ['Renovação do Pivô 12 · lavoura com 3 anos', 'Dessecação para erradicação · 55 ha'], 'OS-0510': ['Safra Mamão 2026/27 · Pivô 6 · colheita semanal'],
        'OS-0511': ['Safra Mamão 2026/27 · Pivô 15 · plano MAMAO-IMP', 'Sexagem: mantém plantas hermafroditas, 1 por cova']}
ATV = {'OS-0501': ('Pulverização', 'Dessecação pré-plantio', 'DAP −20 · 30/09', 'Mamão Formosa · implantação irrigada v1', 'Pulverização'),
       'OS-0502': ('Adubação a lanço', 'Calagem', 'DAP −60 · 25/09', 'Mamão Formosa · implantação irrigada v1', 'Adubação a lanço'),
       'OS-0503': ('Plantio de mudas', 'Plantio de mudas e adubação de cova', 'DAP 0 · 06/10', 'Mamão Formosa · implantação irrigada v1', 'Plantio de mudas'),
       'OS-0504': ('Pulverização', 'Controle de ácaro e cochonilha', '24/09', 'Mamão Formosa · produção irrigada v1', 'Pulverização'),
       'OS-0505': ('Colheita de frutas', 'Colheita semanal', 'semana 39', 'Mamão Formosa · produção irrigada v1', 'Colheita de frutas'),
       'OS-0506': ('Fertirrigação', 'Fertirrigação NK', '22/09', 'Mamão Formosa · produção irrigada v1', 'Fertirrigação'),
       'OS-0507': ('Fertirrigação', 'Fertirrigação de arranque', 'DAP +20 · 14/09', 'Mamão Formosa · implantação irrigada v1', 'Fertirrigação'),
       'OS-0508': ('Pulverização', 'Fungicida para antracnose', '19/09', 'Mamão Formosa · produção irrigada v1', 'Pulverização'),
       'OS-0509': ('Pulverização', 'Erradicação da lavoura velha', '12/09', 'Renovação do Pivô 12', 'Pulverização'),
       'OS-0510': ('Colheita de frutas', 'Colheita semanal', 'semana 38', 'Mamão Formosa · produção irrigada v1', 'Colheita de frutas'),
       'OS-0511': ('Tratos culturais', 'Sexagem e desbaste', 'DAP +90 · 12/10', 'Mamão Formosa · implantação irrigada v1', 'Tratos culturais')}
INS = {'OS-0501': [('Herbicidas', 'Glifosato 480', 3.0, 'L', None, 'Reserva ao liberar'), ('Adjuvantes', 'Óleo mineral', 0.5, 'L', None, 'Reserva ao liberar')],
       'OS-0502': [('Corretivos', 'Calcário dolomítico filler', 2000.0, 'kg', None, 'Reserva ao liberar · estoque 60.000 kg · pedido de 50.000 kg em 30/09')],
       'OS-0503': [('Mudas', 'Muda de mamão Formosa', 1850.0, 'un', None, 'Reservado · REQ-021'), ('Fertilizantes', 'Superfosfato simples', 400.0, 'kg', None, 'Reservado · REQ-021')],
       'OS-0504': [('Inseticidas', 'Abamectina 18 EC', 0.5, 'L', None, 'Entregue a Wesley · confirmado no app')],
       'OS-0506': [('Fertilizantes', 'Sulfato de potássio', 45.0, 'kg', None, 'Entregue · metade em custódia'), ('Fertilizantes', 'Nitrato de amônio', 20.0, 'kg', None, 'Entregue · metade em custódia')],
       'OS-0507': [('Fertilizantes', 'Nitrato de amônio', 25.0, 'kg', None, 'Entregue · 20 ha aplicados'), ('Fertilizantes', 'Ácido bórico', 1.0, 'kg', None, 'Entregue · 20 ha aplicados')],
       'OS-0508': [('Fungicidas', 'Tebuconazol 200 EC', 1.0, 'L', None, 'Consumido 60 L')],
       'OS-0509': [('Herbicidas', 'Glifosato 480', 3.0, 'L', None, 'Consumo conferido')]}
SEM_INS = {'OS-0505': 'Colheita: sem insumos do almoxarifado; caixas e carreta da equipe.', 'OS-0510': 'Colheita: sem insumos do almoxarifado; caixas e carreta da equipe.',
           'OS-0511': 'Operação manual: sem insumos.'}
BLOQ = {'OS-0507': dict(acao='apontar', t='Apontamento parado: bomba do Pivô 5 em manutenção (OM-0251).', q='Manutenção troca o selo mecânico até 25/09; Joaquim religa o pivô.')}
DONO = {'OS-0501': ('Ana (agrônoma)', 'antes de 30/09'), 'OS-0502': ('Suprimentos', 'calcário chega em 30/09'), 'OS-0503': ('Rui (almoxarife)', 'entregar até 05/10'),
        'OS-0505': ('Lúcia', 'conferir o dia 2'), 'OS-0507': ('Manutenção', 'bomba até 25/09'), 'OS-0508': ('Lúcia', 'conferir e encerrar hoje')}
# requisições no cenário compartilhado: (requisição, fração entregue, fração consumida)
REQS = {'OS-0503': ('REQ-021', 0.0, 0.0), 'OS-0504': ('REQ-022', 1.0, 0.0), 'OS-0506': ('REQ-023', 1.0, 0.5), 'OS-0507': ('REQ-024', 1.0, 20 / 56), 'OS-0508': ('REQ-025', 1.0, 1.0)}
# no mapa: talhão (id do mapa), complemento do realizado, prazo e próxima ação
ORD_MAPA = [('OS-0501', ['PV13'], '', 'até 3 dias', ('Ajustar antes de liberar', 'OS.dc.html#OS-0501', 'lib', 'ag')), ('OS-0502', ['PV12'], '', 'vence hoje', ('Ajustar antes de liberar', 'OS.dc.html#OS-0502', 'lib', 'ag')),
            ('OS-0503', ['PV11'], '', 'no prazo', None), ('OS-0504', ['PV06'], '', 'até 3 dias', None), ('OS-0505', ['PV19'], '', 'até 3 dias', None),
            ('OS-0506', ['PV04'], '', 'até 3 dias', None), ('OS-0507', ['PV05'], '', 'atrasada', None), ('OS-0508', ['PV23'], '', 'vence hoje', None),
            ('OS-0509', ['PV12'], '', 'encerrada', None), ('OS-0510', ['PV06'], '', 'encerrada', None), ('OS-0511', ['PV15'], '', 'no prazo', ('Ajustar antes de liberar', 'OS.dc.html#OS-0511', 'lib', 'ag'))]
INTEG = {'PV13': ['ok', 'OS-0501 dessecação'], 'PV12': ['yellow', 'OS-0502 calagem · falta calcário'], 'PV11': ['ok', 'OS-0503 plantio liberado'],
         'PV06': ['ok', 'OS-0504 ácaro · liberada'], 'PV19': ['ok', 'OS-0505 colheita · {OS-0505}'], 'PV04': ['ok', 'OS-0506 · {OS-0506}'],
         'PV05': ['red', 'OS-0507 impedida · bomba'], 'PV23': ['yellow', 'OS-0508 em conferência'], 'PV15': ['ok', 'OS-0511 sexagem']}
