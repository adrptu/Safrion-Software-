# -*- coding: utf-8 -*-
"""Mundo único de demonstração — todos os números citados em mais de uma tela nascem aqui.
Codifica os cenários DEMO-01..20 do cap. 16 para que telas, Kanban, mapa, app e jornadas concordem."""

HOJE='23/09/2026'; SAFRA='2026/27'
FAZENDAS=['Santa Rita','Boa Vista']
TALHOES=[  # (nome, ha, cultura, estádio/fase, obs)
 ('T1',312,'Soja','pré-plantio','sequeiro'),
 ('T2',298,'Soja','pré-plantio','sequeiro'),
 ('T3',96,'Milho','colhido','sequeiro'),
 ('T4',204,'Soja','pré-plantio','sequeiro'),
 ('P1',95,'Feijão','R5','pivô 1'),
 ('P2',80,'Milho','V10','pivô 2'),
 ('T7',42,'Mamão Formosa','produção','gotejo'),
 ('C1',38,'Café','granação','sequeiro'),
]

# ---- Ordens (etapas do cap. 8.4.3; selos como condições) ----
# DEMO-13: O.S. 350 ha, 7 dias (50,50,50,40,50,50,60) — hoje = dia 4 ao abrir a demo (realizado 190, saldo 160)
OS=[
 dict(id='OS-0421', tipo='Pulverização · Fungicida 1ª aplicação', talhao='T1+T2', area=350, etapa='Em execução',
      selo='Parcial · dia 4 de 7', realizado=190, saldo=160, resp='Marcos', versao='v2',
      demo='DEMO-13', dias=[50,50,50,40,50,50,60]),
 dict(id='OS-0420', tipo='Plantio · Soja 58 W', talhao='T4', area=100, etapa='Em execução',
      selo='Impedida · ativo bloqueado', realizado=30, saldo=70, resp='Carlos', versao='v1',
      demo='DEMO-04/14', om='OM-0233'),
 dict(id='OS-0419', tipo='Irrigação · água por política', talhao='P2', area=80, etapa='Liberadas',
      selo=None, realizado=0, saldo=80, resp='João', versao='política PA-07 v3', demo='DEMO-15'),
 dict(id='OS-0418', tipo='Fertirrigação · reclassificada', talhao='P1', area=95, etapa='A liberar',
      selo=None, realizado=0, saldo=95, resp='João', versao='v2', demo='DEMO-16'),
 dict(id='OS-0417', tipo='Adubação de cobertura', talhao='P1', area=95, etapa='Em conferência',
      selo='Sobras a receber', realizado=95, saldo=0, resp='Paula', versao='v1', demo='DEMO-03'),
 dict(id='OS-0415', tipo='Dessecação pós-colheita', talhao='T3', area=96, etapa='Encerradas',
      selo=None, realizado=96, saldo=0, resp='Marcos', versao='v1'),
 dict(id='OB-0104', tipo='Beneficiamento · grãos', talhao='Armazém Sede', area=None, etapa='Encerradas',
      selo='Lote bloqueado', realizado=None, saldo=None, resp='Rui', versao='rota aprovada', demo='DEMO-19', lote='L27-013'),
]
KANBAN={'A liberar':[o for o in OS if o['etapa']=='A liberar'],'Liberadas':[o for o in OS if o['etapa']=='Liberadas'],
 'Em execução':[o for o in OS if o['etapa']=='Em execução'],'Em conferência':[o for o in OS if o['etapa']=='Em conferência'],
 'Encerradas':[o for o in OS if o['etapa']=='Encerradas']}

# ---- Materiais / custódia (DEMO-03: 100 entregues, 70 consumo, 20 devolvidos, 10 pendentes) ----
REQ=dict(id='REQ-031', os='OS-0417', item='MAP 11-52', un='sc 50 kg', entregue=100, consumido=70,
         devolvido_declarado=20, devolvido_recebido=20, custodia=10)
# DEMO-18: lote 100 un, duas reservas de 80
LOTE_DISPUTA=dict(id='F26-02', item='Fungicida A', utilizavel=100, reserva_a=80, conflito_b=80, livre_apos=20)
# DEMO-02: PC-088 compra 100, recebe 60 (50 aptas + 10 quarentena), 40 a entregar
PC=dict(id='PC-088', item='KCl 60 %', pedido=100, recebido=60, apto=50, quarentena=10, a_entregar=40)

# ---- Irrigação (DEMO-05/15) ----
# volta_62_h: uma volta a 62 % = 9,0 h ÷ 0,62 ≈ 14,52 h (= 10,81 mm × 80 ha ÷ 166 L/s); exec_h = andamento de 2,1 h (≈14,47 % da volta)
PIVO=dict(id='Pivô 2', volta_h=9.0, lamina_100=6.7, percent=62, exec_h=2.1, lamina_aplicada=10.81, cobertura_pct=14.47, volta_62_h=14.52)
# Ficha do pivô (pedido de 09/10/2026): capacidade do equipamento como está na ficha técnica do fabricante · DADOS SINTÉTICOS.
# Chave = o equipamento de irrigação do cadastro (dados_cad.ATIVOS a11, Bomba do Pivô 2). Tempo de volta e lâmina a 100 % são os de PIVO
# (fonte atual, sem cópia); a vazão daqui é a fonte da Irrigação (setor P2) e do cadastro da bomba. Tabela percentímetro × tempo de volta
# × lâmina registrada como está (texto da ficha, Decimal na conta; a linha 100 % vem de PIVO); a conferência fica em ficha_pivo.py.
# regime_h: "21 h" é o regime de operação (h/dia, fora do horário de ponta), guardado como referência, sem outro uso.
FICHA_PIVO={'a11':dict(pivo=PIVO['id'], fabricante='Fabricante demonstrativo (sintético)', modelo='pivô central fixo · 8 torres', raio_m=505, area_ha=80,
                       vazao_ls=166, pressao_mca=32, volta_100_h=PIVO['volta_h'], lamina_100_mm=PIVO['lamina_100'], regime_h=21, regime_obs='fora do horário de ponta',
                       tabela=[('100',str(PIVO['volta_h']),str(PIVO['lamina_100'])),('90','10.0','7.4'),('80','11.3','8.4'),('70','12.9','9.6'),('60','15.0','11.0'),
                               ('50','18.0','13.4'),('40','22.5','16.8'),('30','30.0','22.3'),('20','45.0','33.5'),('10','90.0','67.0')])}
POLITICA_AGUA=dict(id='PA-07 v3', lamina_max=12.0, intervalo_min='18 h', validade='30/11/2026', autor='Ana (agrônoma)')

# ---- Máquinas (DEMO-04/17) ----
OM=dict(id='OM-0233', ativo='Trator T1 · JD 6M 155', causa='Pressão hidráulica baixa', etapa='Em execução',
        bloqueio='CMD-18 ativo', os_afetada='OS-0420', substituto='Trator 02 · MF 7719')

# ---- Colheita/beneficiamento (DEMO-06/07/19) ----
PREVISAO=dict(pedido='PV-031', classeA_t=10.0, prev_bruta_t=12.0, rendA=0.80, futuras_A=9.6, falta=0.4)
PACKING=dict(entrada=12.0, saidaA=9.6, saidaB=1.8, descarte=0.6)
LOTE_BLOQ=dict(id='L27-013', produto='Café beneficiado', sc=3690, estado='Bloqueado', inspecao='INSP-88 aberta · Qualidade · prazo 25/09')

# ---- Logística (DEMO-20) ----
FILA=[('T1','08:00','atrasado · prev. 09:10'),('T2','08:30','presente · apto'),('T3','09:00','presente · apto'),
      ('T4','—','antecipado'),('Carga 07','—','impedida · NF pendente')]

# ---- Comercial / crédito ----
CRE=dict(id='CRE-0102', valor='R$ 850 mil', estado='Aprovação condicionada a documento', liberado='R$ 300 mil')
DISPON=dict(base_kg=3000, atendivel_kg=2000)

# ---- Aprovações pendentes (IN-02): uma por domínio, despacho por objeto · O.S. não entra (o agrônomo libera na própria O.S.) ----
APROV=[
 ('Política de água PA-08 (nova)','FO-43','Agrônomo','até 3 dias','lâmina máx. 14 mm · validade 60 d'),
 ('Ajuste de inventário Galpão 2','FO-32','Gestor','vence hoje','−12 sc MAP · contagem cega'),
 ('Política de estoque · Diesel S10','FO-31','Gestor','até 5 dias','mínimo do tanque 40%'),
 ('Orçamento revisado · safra 26/27','FO-36','Direção','até 7 dias','+R$ 180 mil defensivos'),
 ('Acesso · novo operador (Beto)','FO-39','Gestor','até 2 dias','perfil Operador · Santa Rita'),
]

# ===================== REGISTRO CANÔNICO DE ORDENS (25/09/2026) =====================
# Toda tela que mostra ordens usa estes IDs, fases, saldos e janelas. Fase = uma das 5 etapas; selo = condição.
# Histórico (encerradas antigas) usa a faixa OS-0380..OS-0399; novas ordens criadas no protótipo: OS-0440 em diante.
# Campos opcionais: selos_extra = condições além do selo principal (mesma lista na O.S., no Mapa e no detalhe);
# chave = cultivo|atividade do plano que gerou a ordem, ou lista delas quando a ordem cobre vários cultivos
# (a "Nova ordem" não emite outra para a mesma chave): OS-0421 = T1-A, T1-B e T2 · a6; OS-0425 = c9|k1; OS-0430 = c1|a1; OS-0431 = c3|a3.
# Selo com "Impedida" ou "Falta máquina" conta como ordem impedida em todas as telas.
ORDENS=[
 dict(id='OS-0415',tipo='Dessecação pós-colheita',talhao='T3',area=96,etapa='Encerradas',selo=None,realizado=96,saldo=0,janela='10–12/09',resp='Marcos',detalhe=None),
 dict(id='OS-0417',tipo='Adubação de cobertura',talhao='P1',area=95,etapa='Em conferência',selo='Sobras a receber',realizado=95,saldo=0,janela='19–21/09',resp='Paula',detalhe=None),
 dict(id='OS-0418',tipo='Fertirrigação · reclassificada',talhao='P1',area=95,etapa='A liberar',selo=None,realizado=0,saldo=95,janela='24/09 21:00–25/09 11:15',resp='João',detalhe=None),
 dict(id='OS-0419',tipo='Irrigação · água por política',talhao='P2',area=80,etapa='Liberadas',selo=None,realizado=0,saldo=80,janela='hoje 20:00–amanhã 10:31',resp='João',detalhe='IR-03det.dc.html'),
 dict(id='OS-0420',tipo='Plantio · Soja 58 W',talhao='T4',area=100,etapa='Em execução',selo='Impedida · ativo bloqueado',realizado=30,saldo=70,janela='22–28/09',resp='Carlos',detalhe='CA-01x-os0420.dc.html'),
 dict(id='OS-0421',tipo='Pulverização · Fungicida 1ª aplicação',talhao='T1+T2',area=350,etapa='Em execução',selo='Parcial · dia 4 de 7',realizado=190,saldo=160,janela='20–26/09',resp='Marcos',detalhe='CA-01det.dc.html',
      chave=['c1|a6','c2|a6','c3|a6']),
 dict(id='OS-0422',tipo='Irrigação · água',talhao='P2',area=80,etapa='A liberar',selo='Janela a definir',realizado=0,saldo=80,janela='a definir',resp='João',detalhe='IR-02.dc.html'),
 dict(id='OS-0423',tipo='Irrigação · água por gotejo',talhao='T7',area=42,etapa='A liberar',selo='Conflito · parada da B3',realizado=0,saldo=42,janela='hoje 14:00–16:00',resp='João',detalhe='IR-02.dc.html'),
 dict(id='OS-0424',tipo='Pulverização · Fungicida A',talhao='T1-B',area=128,etapa='Liberadas',selo=None,realizado=0,saldo=128,janela='24/09',resp='Marcos',detalhe=None),
 dict(id='OS-0425',tipo='Adubação 1ª parcela · café',talhao='C1',area=38,etapa='Liberadas',selo='Entrega sem saldo suficiente',realizado=0,saldo=38,janela='15/10',resp='Paula',detalhe=None,
      chave='c9|k1'),
 dict(id='OS-0430',tipo='Dessecação pré-plantio',talhao='T1-A',area=160,etapa='A liberar',selo=None,realizado=0,saldo=160,janela='25/09 (DAP −20)',resp='Marcos',detalhe=None,
      chave='c1|a1'),
 dict(id='OS-0431',tipo='Plantio · Soja 58 W',talhao='T2',area=102,etapa='A liberar',selo=None,realizado=0,saldo=102,janela='amanhã (24/09) 06:00',resp='Carlos',detalhe=None,
      selos_extra=['Falta máquina · Trator T1 bloqueado'],chave='c3|a3'),
 dict(id='OB-0104',tipo='Beneficiamento · grãos',talhao='Armazém Sede',area=None,etapa='Encerradas',selo='Lote bloqueado',realizado=None,saldo=None,janela='15–18/09',resp='Rui',detalhe='CO-06det.dc.html'),
]
# Fazenda e safra de cada ordem (filtros do topo da O.S.): todas na Santa Rita; OS-0415 (dessecação pós-colheita do milho T3) e
# OB-0104 (café da colheita C1 de jul/26) são da safra 2025/26 (set/2025 – ago/2026); as demais, da 2026/27.
# Irrigação só com água (OS-0419, OS-0422, OS-0423) não passa pelo agrônomo: libera pela prontidão operacional (decisão de 26/09).
for _o in ORDENS:
    _o.setdefault('faz','Santa Rita'); _o.setdefault('saf','2025/26' if _o['id'] in ('OS-0415','OB-0104') else '2026/27')
# TABELAS-FOCO (5983172395): vínculo estruturado com os talhões do cadastro da fazenda (ID e nome; nunca separado do texto
# por pontuação), local próprio da ordem sem talhão e início/fim da janela como data (demonstração: hoje = 23/09/2026).
_TAL={'OS-0415':['T3'],'OS-0417':['P1'],'OS-0418':['P1'],'OS-0419':['P2'],'OS-0420':['T4'],'OS-0421':['T1','T2'],'OS-0422':['P2'],
      'OS-0423':['T7'],'OS-0424':['T1-B'],'OS-0425':['C1'],'OS-0430':['T1-A'],'OS-0431':['T2'],'OB-0104':[]}
_JAN={'OS-0415':('2025-09-10','2025-09-12'),'OS-0417':('2026-09-19','2026-09-21'),'OS-0418':('2026-09-24','2026-09-25'),
      'OS-0419':('2026-09-23','2026-09-24'),'OS-0420':('2026-09-22','2026-09-28'),'OS-0421':('2026-09-20','2026-09-26'),'OS-0422':('',''),
      'OS-0423':('2026-09-23','2026-09-23'),'OS-0424':('2026-09-24','2026-09-24'),'OS-0425':('2026-10-15','2026-10-15'),
      'OS-0430':('2026-09-25','2026-09-25'),'OS-0431':('2026-09-24','2026-09-24'),'OB-0104':('2025-09-15','2025-09-18')}
for _o in ORDENS:
    _o['talhoes']=[dict(id=t,nome=t) for t in _TAL[_o['id']]]; _o['local']='' if _TAL[_o['id']] else _o['talhao']
    _o['ini'],_o['fim']=_JAN[_o['id']]
ORDEM={o['id']:o for o in ORDENS}
# ---- Geometria (fonte única para o Mapa IN-04 e o CD-01det): polígono validado do talhão e geometria de cada parcela
# (cultivo de dados2.CULTIVOS → situação). Cultivo fora do mapa = sem polígono no CD-01det; o Mapa só marca o que está aqui.
GEO_TAL={'T1':'polígono v3 validado 12/09'}
GEO_PARC={'c1':'Validada','c2':'Sem polígono','d1':'Validada','e1':'Validada'}
# fatos canônicos compartilhados entre módulos
CANON=dict(
 PC088='PC-088 · Fertisul · KCl 60 % · 100 t × R$ 2,33/kg = R$ 233.000 · título único, sem barter · 60 t recebidas (50 aptas + 10 quarentena) · 40 t a entregar',
 PV031='PV-031 · Frutas Real · mamão Formosa classe A · pedido 10,0 t · atendível 9,6 t × R$ 3,05/kg = R$ 29.280',
 PV028='PV-028 · Torrefação Serra · café · 500 sc',
 CARGA07='Carga 07 · impedida · NF pendente · dono Sandra (fiscal) · prazo 10:00',
 OF103='OF-103 · enviada à Frutas Real · reservada pela RT-0112',
)
# ---- Fazenda Lagoa Grande: O.S. em todas as fases (dados_lagoa_safra.py). Ficam fora de ORDENS (Meu dia e Agenda
# continuam só com a Santa Rita); a tela O.S. (filtro Fazenda), o Mapa e o cenário compartilhado as incluem.
import dados_lagoa_safra as _DL
ORDENS_LG=_DL.ORDENS
ORDEM.update({o['id']:o for o in ORDENS_LG})
