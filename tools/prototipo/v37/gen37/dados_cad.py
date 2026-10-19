# -*- coding: utf-8 -*-
"""Dados dos cadastros (CD-01..CD-07) que não existiam no mundo DEMO: fazendas, culturas, operações, papéis de parceiros
(cliente, parceiro de crédito, transportador, prestador), preço e embalagem dos itens, custo/h e capacidade das máquinas,
conjuntos, habilidades das pessoas e estrutura gerencial. Nada aqui altera dados.py ou dados2.py (só lê)."""
import dados as D
import dados2 as D2

# ============ CD-01 · fazendas e talhões ============
FUSOS=['América/São Paulo (UTC−3)','América/Cuiabá (UTC−4)','América/Manaus (UTC−4)','América/Porto Velho (UTC−4)','América/Rio Branco (UTC−5)']
FUSO_UF={'MT':FUSOS[1],'MS':FUSOS[1],'AM':FUSOS[2],'RR':FUSOS[2],'RO':FUSOS[3],'AC':FUSOS[4]}   # demais UFs: América/São Paulo
EMPRESAS=['Santa Rita Agro','Boa Vista Ltda']
POSSE=['Própria','Arrendada','Parceria agrícola']
FAZENDAS=[
 dict(id='SR',nome='Santa Rita',empresa='Santa Rita Agro',mun='Rio Verde/GO',fuso=FUSOS[0],area=1480,posse='Própria',arrend='',fim='',custo='',
      car='GO-5218805-7F2A.1C9B.44E0.9D31',matr='12.401 · CRI de Rio Verde',pend='',sit='Ativa'),
 dict(id='BV',nome='Boa Vista',empresa='Boa Vista Ltda',mun='Sorriso/MT',fuso=FUSOS[1],area=420,posse='Arrendada',arrend='Otávio Almeida · CPF 321.654.987-91',
      fim='2029-08-31',custo=8,car='',matr='8.421 · CRI de Sorriso',pend='Contrato de arrendamento BV-03 sem registro em cartório',sit='Ativa'),
]
# talhões de Santa Rita (D.TALHOES): polígono validado (ha), sistema e pivô/setor (CD-03)
CALC={'T1':312.4,'T2':298.1,'T3':96.0,'T4':203.6,'P1':94.7,'P2':80.2,'T7':42.0,'C1':38.3}
SISTEMA={'sequeiro':('Sequeiro',''),'pivô 1':('Pivô central','Bomba do Pivô 1'),'pivô 2':('Pivô central','Bomba do Pivô 2'),'gotejo':('Gotejo','Gotejo T7')}
SETORES=['Bomba do Pivô 1','Bomba do Pivô 2','Gotejo T7']
MOTIVOS_DIF=['Carreador ou estrada','APP ou reserva','Sede ou benfeitoria','Documento desatualizado']
# versões da geometria de cada talhão (a mais nova é a atual; as antigas ficam para as O.S. que as usaram)
GEO_VERS={'T1':[('v2','2025-08-20','Importado · levantamento 2025',311.8),('v3','2026-09-12','Importado · levantamento RTK',312.4)]}
def geo_vers(t):
    return GEO_VERS.get(t,[('v1','2024-09-01','Importado · implantação',CALC[t])])

# ============ CD-02 · culturas e operações ============
UNID_PROD=['sc de 60 kg/ha','t/ha','t/ha/ano','cx de 20 kg/ha','kg/ha']
CULTURAS=[('Soja','SOJA','Anual','sc de 60 kg/ha'),('Milho','MILHO','Anual','sc de 60 kg/ha'),('Feijão','FEIJAO','Anual','sc de 60 kg/ha'),
          ('Café','CAFE','Perene','sc de 60 kg/ha'),('Mamão Formosa','MAMAO','Perene','t/ha/ano')]
# Unidade de mercado por cultura (DEC-0510-03; docs/culturas/UNIDADES-DE-MERCADO.md; colheita D-03): fonte ÚNICA do fator de produção,
# produtividade, estoque de produto e pedido. A tupla CULTURAS não muda (CD-02 e Planejar safra a leem). Quantidade guardada na base:
# kg (6 casas) · frutos (coco, abacaxi) · L do café da roça (campo). un = unidade de produção e estoque; massa = base por un (decimal em
# texto); prtv = unidade de produtividade; base = base física da produtividade (coluna "Base física": comercial corrigido no grão,
# beneficiado no café, massa líquida pesada na fruta e na cana, frutos no coco e no abacaxi); grão: umidade e impureza padrão (R-08);
# lado = unidade mostrada ao lado; prod = produto de estoque (o item do CD-06 com fator tem de coincidir: Soja em grão e Café beneficiado
# em sc 60 kg); est = unidade do estoque e do pedido quando não é a de produção; vida = vida útil em dias (perecível, D-21).
# Laranja, coco e abacaxi seguem a proposta da UNIDADES-DE-MERCADO (D-04); arroz RS/SC em sc 50 kg (só no teste).
CULTURA_UN={
 'Soja':dict(un='sc',massa='60',prtv='sc/ha',base='comercial',grao=True,u='14',imp='1',prod='Soja em grão'),
 'Milho':dict(un='sc',massa='60',prtv='sc/ha',base='comercial',grao=True,u='14',imp='1',prod='Milho em grão'),
 'Feijão':dict(un='sc',massa='60',prtv='sc/ha',base='comercial',grao=True,u='14',imp='0.5',prod='Feijão em grão'),
 'Café':dict(un='sc',massa='60',prtv='sc/ha',base='beneficiado',campo='L',prod='Café beneficiado',proc='Café da roça'),
 'Mamão Formosa':dict(un='t',massa='1000',prtv='t/ha',base='massa',prod='Mamão Formosa · fruta de campo',est='kg',vida=7),
 'Laranja':dict(un='cx',massa='40.8',prtv='cx/ha',lado='t/ha',base='massa',prod='Laranja'),
 'Coco':dict(un='mil frutos',massa='1000',prtv='mil frutos/ha',base='frutos',prod='Coco verde',est='fruto'),
 'Abacaxi':dict(un='mil frutos',massa='1000',prtv='mil frutos/ha',base='frutos',prod='Abacaxi',est='fruto'),
 'Arroz RS':dict(un='sc',massa='50',prtv='sc/ha',base='comercial',grao=True,u='13',imp='0',prod='Arroz em casca RS'),
 'Arroz SC':dict(un='sc',massa='50',prtv='sc/ha',base='comercial',grao=True,u='13',imp='0',prod='Arroz em casca SC'),
 'Cana-de-açúcar':dict(un='t',massa='1000',prtv='t/ha',base='massa',prod='Cana-de-açúcar'),
 # UNID-PROD D-U07: algodão em caroço e em pluma (@ de 15 kg, UNIDADES-DE-MERCADO), produtos diferentes que nunca se somam (R-U08); sem fazenda
 'Algodão em caroço':dict(un='@',massa='15',prtv='@/ha',base='massa',prod='Algodão em caroço'),
 'Algodão em pluma':dict(un='@',massa='15',prtv='@/ha',base='massa',prod='Algodão em pluma'),
}
# processo = etapa de custo (dimensão Processo do CD-07); cada operação aponta o seu
PROCESSOS=[('IMPL','Implantação'),('TRAT','Tratos culturais'),('COLH','Colheita'),('POSC','Pós-colheita')]
OP_PROC={'Pulverização':'Tratos culturais','Plantio':'Implantação','Adubação a lanço':'Tratos culturais','Tratamento de sementes':'Implantação',
         'Colheita de grãos':'Colheita','Colheita de café':'Colheita','Poda':'Tratos culturais','Fertirrigação':'Tratos culturais'}
SEMENTES={('Soja','58 W'):'Semente de soja 58 W',('Soja','62 X'):'Semente de soja 62 X',('Milho','Híbrido AG 8700'):'Semente de milho AG 8700',('Feijão','Pérola'):'Semente de feijão Pérola'}

# ============ CD-03 · máquinas, instalações e conjuntos ============
# capacidade por classe: pot (cv) · barra (m) + tanque (L) · linhas × esp (m) · larg (m) [+ carga kg] · plat (m) · vazao (m³/h) · kgh (kg/h) · cap_sc (sc 60 kg)
# custo_h: máquina/implemento R$/h que o rendimento (CD-02 e Planejar safra etapa 3) usa
# vazão (m³/h) do equipamento de irrigação = a fonte da Irrigação (dados_irrigacao.eq_vazao_ls lê daqui): Bomba do Pivô 2 = a da ficha do pivô
# (dados.FICHA_PIVO, 166 L/s; antes 340 m³/h); Bomba do Pivô 1 = 540 m³/h (150 L/s; antes 300); Gotejo T7 = 838,8 m³/h (233 L/s; antes 45)
# (revisão de 10/10, A2: a mesma vazão no cadastro e na Irrigação). Modelo da a11 = o conjunto da ficha (pivô + motobomba), A7.
ATIVOS=[
 dict(id='a01',nome='Trator T1',modelo='JD 6M 155',classe='Trator',pot=155,custo_h=180,cont=4312,exige='Não',local='Oficina Sede',fonte='Fabricante'),
 dict(id='a02',nome='Trator 02',modelo='MF 7719',classe='Trator',pot=190,custo_h=180,cont=2988,exige='Não',local='Santa Rita · T4',fonte='Fabricante'),
 dict(id='a03',nome='Trator 03',modelo='MF 4292',classe='Trator',pot=110,custo_h=150,cont=5120,exige='Não',local='Galpão 1',fonte='Fabricante'),
 dict(id='a04',nome='Trator 04',modelo='JD 5078E',classe='Trator',pot=78,custo_h=150,cont=3410,exige='Não',local='Galpão 1',fonte='Fabricante'),
 dict(id='a05',nome='Pulverizador PJ-3030',modelo='Uniport 3030',classe='Pulverizador',barra=36,tanque=3000,esp_bicos=0.5,ponta='leque 110-015',pressao=3,custo_h=95,cont=1542,exige='Sim',calib='2026-09-15',interv=90,local='Santa Rita · T1',fonte='Ensaio da fazenda'),
 dict(id='a06',nome='Plantadeira 24 linhas',modelo='PD-12',classe='Plantadeira',linhas=24,esp=0.5,custo_h=140,cont=886,exige='Sim',calib='2026-09-10',interv=180,local='Galpão 1',fonte='Ensaio da fazenda'),
 dict(id='a07',nome='Distribuidor 3 t',modelo='Lancer 3000',classe='Distribuidor',larg=24,carga=3000,custo_h=45,cont=640,exige='Sim',calib='2026-08-01',interv=90,local='Galpão 1',fonte='Fabricante'),
 dict(id='a08',nome='Colhedora Axial-Flow 7250',modelo='Case IH 7250',classe='Colhedora',plat=10,custo_h=950,cont=2150,exige='Não',local='Galpão 1',fonte='Fabricante'),
 dict(id='a09',nome='Máquina TSI',modelo='tratamento de sementes na sede',classe='Tratamento de sementes',kgh=2400,custo_h=60,cont=720,exige='Sim',calib='2026-07-20',interv=60,local='Oficina Sede',fonte='Ensaio da fazenda'),
 dict(id='a10',nome='Esqueletadeira',modelo='café · 1 linha',classe='Implemento',larg=3,custo_h=60,cont=310,exige='Não',local='Galpão 1',fonte='Fabricante'),
 dict(id='a15',nome='Bomba do Pivô 1',modelo='motobomba 125 cv',classe='Irrigação',vazao=540,custo_h=85,cont=7650,exige='Sim',calib='2026-09-12',interv=30,local='Pivô 1',fonte='Ensaio da fazenda'),
 dict(id='a11',nome='Bomba do Pivô 2',modelo='pivô central fixo · 8 torres · motobomba + hidrômetro novo',classe='Irrigação',vazao=round(D.FICHA_PIVO['a11']['vazao_ls']*3.6,1),custo_h=85,cont=8914,exige='Sim',calib='',interv=30,local='Pivô 2',fonte='Ensaio da fazenda'),
 dict(id='a12',nome='Gotejo T7',modelo='cabeçal + injetora de fertilizante',classe='Irrigação',vazao=838.8,custo_h=25,cont=5210,exige='Sim',calib='2026-09-05',interv=60,local='Talhão T7',fonte='Ensaio da fazenda'),
 dict(id='a13',nome='Packing linha 1',modelo='esteira + balança',classe='Beneficiamento',kgh=2400,custo_h=120,cont=12301,exige='Sim',calib='2026-09-01',interv=30,local='Armazém Sede',fonte='Ensaio da fazenda'),
 dict(id='a14',nome='Silo 01',modelo='aeração + termometria',classe='Armazenagem',cap_sc=60000,custo_h='',cont='',exige='Sim',calib='2026-09-18',interv=90,local='Armazém Sede',fonte='Fabricante'),
 # ATIVO-UNICO (18/10/2026): o comboio de abastecimento existia só na Manutenção (dados_manutencao); o cadastro é a fonte única do ativo
 dict(id='cb01',nome='Comboio CB-01',modelo='caminhão comboio 6 m³',classe='Veículo',carga=6000,custo_h='',cont=48200,exige='Não',local='Sede',fonte='Fabricante'),
]
# condição técnica vem da Manutenção (somente leitura no cadastro)
CONDICAO={'a01':dict(t='Em manutenção',om=D.OM['id'],det='retorno previsto 24/09 · aguardando teste',ordens=['OS-0420','OS-0431'])}
# conjuntos máquina + implemento (rendimento correspondente em D2.CONJ)
CONJUNTOS=[('k1','Trator 02','Pulverizador PJ-3030','Pulverização','r1'),('k2','Trator T1','Plantadeira 24 linhas','Plantio','r2'),
           ('k3','Trator 03','Distribuidor 3 t','Adubação a lanço','r3'),('k4','Máquina TSI','','Tratamento de sementes','r4'),
           ('k5','Colhedora Axial-Flow 7250','','Colheita de grãos','r5'),('k6','Trator 04','Esqueletadeira','Poda','r7'),('k7','Gotejo T7','','Fertirrigação','r8')]

# ============ CD-04 · pessoas, habilidades e habilitações ============
HABILIDADES=['Operar trator','Operar pulverizador','Operar plantadeira','Operar colhedora','Preparar calda','Irrigar','Almoxarifado',
             'Operar empilhadeira','Conferir','Manutenção de máquinas','Testar reparo','Aprovar O.S. de manutenção','Liberar ativo','Liberar O.S. (agrônomo)',
             'Autorizar rota e liberar ordem de processo','Liberar lote (qualidade)']   # PCM (D-20/D-36): teste, aprovação e aptidão; BEN-1 (docs/beneficiamento §2.3): Igor e Marta
# habilitação exigida por habilidade (validade controlada na pessoa)
HAB_EXIGE={'Operar trator':'NR-31','Operar pulverizador':'NR-31','Operar plantadeira':'NR-31','Operar colhedora':'NR-31','Preparar calda':'NR-31',
           'Irrigar':'NR-10','Operar empilhadeira':'NR-11','Manutenção de máquinas':'NR-12','Liberar O.S. (agrônomo)':'CREA'}
HAB_CAMPO={'NR-31':'v31','NR-10':'v10','NR-11':'v11','NR-12':'v12','CREA':'vcrea'}
EQUIPES=[('e1','Agronomia','Ana','seg–sex · 07–17h'),('e2','Campo 1','Marcos','seg–sáb · 06–15h'),('e3','Campo 2','Lucas','seg–sáb · 06–15h'),
         ('e4','Irrigação','João','escala 6×2 · 8h'),('e6','Suprimentos','Rui','seg–sex · 07–17h'),('e7','Oficina','Zé','seg–sex · 07–17h'),
         ('e8','Beneficiamento e qualidade','Igor','seg–sáb · 06–15h'),('e9','Comercial','Dora','seg–sex · 07–17h')]
CALS=['seg–sex · 07–17h','seg–sex · 08–18h','seg–sáb · 06–15h','escala 6×2 · 8h']
# custo-hora com encargos alinhado ao rendimento (D2.CONJ: operador R$ 38/h; irrigante e equipe de café R$ 32/h)
PESSOAS=[
 dict(id='p1',nome='Ana',funcao='Agrônoma e gestora',equipe='Agronomia',vinc='CLT',hab=['Liberar O.S. (agrônomo)'],vcrea='2027-12-31',adm='2019-02-01',custo=84,login=True),
 dict(id='p2',nome='Marcos',funcao='Operador de pulverização',equipe='Campo 1',vinc='CLT',hab=['Operar trator','Operar pulverizador'],v31='2026-09-30',adm='2021-03-15',custo=38,login=True),
 dict(id='p3',nome='Carlos',funcao='Operador de plantio',equipe='Campo 1',vinc='CLT',hab=['Operar trator','Operar plantadeira'],v31='2027-08-31',adm='2020-07-01',custo=38,login=True),
 dict(id='p10',nome='Nilton',funcao='Caldeiro',equipe='Campo 1',vinc='CLT',hab=['Preparar calda'],v31='2027-04-30',adm='2022-01-10',custo=32,login=True),
 dict(id='p4',nome='Lucas',funcao='Operador de colheita',equipe='Campo 2',vinc='Safrista',hab=['Operar trator','Operar colhedora'],v31='2026-08-15',adm='2026-08-01',ate='2027-07-31',custo=38,login=True),
 dict(id='p5',nome='João',funcao='Irrigante',equipe='Irrigação',vinc='CLT',hab=['Irrigar'],v10='2027-03-31',adm='2018-05-02',custo=32,login=True),
 dict(id='p6',nome='Paula',funcao='Almoxarife',equipe='Suprimentos',vinc='CLT',hab=['Almoxarifado','Conferir'],adm='2020-02-03',custo=32,login=True),
 dict(id='p7',nome='Rui',funcao='Conferente',equipe='Suprimentos',vinc='CLT',hab=['Conferir','Almoxarifado','Operar empilhadeira'],v11='2027-02-28',adm='2017-09-11',custo=30,login=True),
 dict(id='p8',nome='Zé',funcao='Mecânico',equipe='Oficina',vinc='CLT',hab=['Manutenção de máquinas','Testar reparo'],v12='2027-05-31',adm='2016-04-04',custo=34,login=True),
 # PCM simplificado (05/10, D-20/D-37): Otávio, responsável de manutenção (sintético), aprova a OM e decide a aptidão do ativo (CMD-19)
 dict(id='p14',nome='Otávio',funcao='Responsável de manutenção',equipe='Oficina',vinc='CLT',hab=['Aprovar O.S. de manutenção','Liberar ativo'],adm='2015-03-02',custo=58,login=True),
 dict(id='p9',nome='Beto',funcao='Operador',equipe='Campo 1',vinc='CLT',hab=['Operar trator'],v31='',adm='2026-09-22',custo=38,login=False),
 # CONF-D04: Caio (PCP) decide pelo perfil de demonstração desde o CTL-3 e não estava no cadastro (segundo cadastro de pessoas); entra aqui (sintético)
 dict(id='p11',nome='Caio',funcao='PCP',equipe='Agronomia',vinc='CLT',hab=['Conferir'],adm='2024-03-04',custo=52,login=True),
 # BEN-1 (docs/beneficiamento §2.3, §10.2; sintéticos): responsável de produção do packing e a Qualidade que libera lote (a Marta que a
 # carência e a Produção já citam como "Qualidade (Marta)"); perfis de quem age em g2lib.js (G2_PERFIS)
 dict(id='p12',nome='Igor',funcao='Responsável de produção',equipe='Beneficiamento e qualidade',vinc='CLT',hab=['Autorizar rota e liberar ordem de processo'],adm='2024-03-04',custo=38,login=True),
 dict(id='p13',nome='Marta',funcao='Qualidade',equipe='Beneficiamento e qualidade',vinc='CLT',hab=['Liberar lote (qualidade)'],adm='2023-08-14',custo=34,login=True),
 dict(id='p15',nome='Dora',funcao='Comercial',equipe='Comercial',vinc='CLT',hab=[],adm='2024-03-04',custo=40,login=True),   # v57: quem decide no Comercial é pessoa do CD-04 (CONF R5)
]

# ============ CD-05 · parceiros com papéis ============
PAPEIS=['Fornecedor','Cliente','Parceiro de crédito','Transportador','Prestador']
PRODUTOS_VENDA=['Soja em grão','Milho em grão','Feijão','Café beneficiado','Mamão Formosa classe A','Mamão Formosa classe B']
COND_PAG=['À vista na entrega','28 dias após a entrega comprovada','30 dias após a entrega comprovada','Antecipado']
LINHAS_CRED=['Custeio','Investimento','Comercialização','CPR']
GARANTIAS=['Penhor de safra','Alienação fiduciária','Hipoteca','Aval','CPR']
# dados por papel dos parceiros existentes (D2.FORNECEDORES e OUTROS do CD-05) e parceiros novos (clientes e crédito)
PAPEL_EXTRA={
 'F06':dict(papeis=['Fornecedor','Cliente'],prod=['Soja em grão','Milho em grão'],entrega='Armazém Coop. Vale · Rio Verde/GO · 24 h na safra',pag=COND_PAG[0],lim=1500000,limv='2027-06-30'),
 'P08':dict(prod=['Soja em grão','Milho em grão'],entrega='Armazém Coopergrão · Rio Verde/GO · seg–sáb 06–22h',pag=COND_PAG[0],lim=2000000,limv='2027-06-30'),
 'P09':dict(rntrc='012345678',veic='Bitrem 37 t (3); Truck 14 t (2)'),
 'P10':dict(papeis=['Parceiro de crédito'],contato='Helena Castro',linhas=['Custeio','Investimento','CPR'],gar=['Penhor de safra','Alienação fiduciária','Hipoteca']),
 'P11':dict(ops=['Colheita de café','Poda']),
}
NOVOS_PARCEIROS=[
 dict(id='P12',nome='Frutas Real',cnpj=D2.cnpj_valido('31.402.118/0001-00'),papeis=['Cliente'],grupos=[],email='compras@frutasreal.com.br',whats='31 99301-4412',homologado=False,
      contato='Lívia Barros',canais=['E-mail','WhatsApp'],prod=['Mamão Formosa classe A','Mamão Formosa classe B'],entrega='CD Frutas Real · Contagem/MG · seg–sex 05–11h',
      pag=COND_PAG[1],lim=120000,limv='2026-12-31'),
 dict(id='P13',nome='Torrefação Serra',cnpj=D2.cnpj_valido('27.815.440/0001-00'),papeis=['Cliente'],grupos=[],email='cafe@torrefacaoserra.com.br',whats='34 99812-3070',homologado=False,
      contato='Fábio Serra',canais=['E-mail'],prod=['Café beneficiado'],entrega='Armazém da torrefação · Patrocínio/MG · seg–sex 07–16h',pag=COND_PAG[2],lim=900000,limv='2026-11-30'),
 dict(id='P14',nome='Rede Hortifrúti BA',cnpj=D2.cnpj_valido('15.332.907/0001-00'),papeis=['Cliente'],grupos=[],email='hortifruti@redehfba.com.br',whats='71 99655-2103',homologado=False,
      contato='Caio Nunes',canais=['E-mail'],prod=['Mamão Formosa classe B'],entrega='CD Salvador/BA · seg–sáb 04–10h',pag=COND_PAG[0],lim=40000,limv='2026-08-31'),
 dict(id='P15',nome='Coop Crédito Vale',cnpj=D2.cnpj_valido('08.604.771/0001-00'),papeis=['Parceiro de crédito'],grupos=[],email='agro@coopcreditovale.coop.br',whats='64 99420-1180',homologado=False,
      contato='Márcio Reis',canais=['E-mail','WhatsApp'],linhas=['Custeio','Comercialização'],gar=['Penhor de safra','Aval']),
]

# ============ CD-06 · itens, grupos e locais ============
GRUPOS=D2.GRUPOS+['Corretivos','Produto agrícola','Embalagem']
# natureza de custo (CD-07) de cada grupo; produto agrícola é receita, não custo
GRUPO_NAT={'Sementes':'3.1.03','Inoculantes':'3.1.03','Fertilizantes':'3.1.01','Corretivos':'3.1.01','Herbicidas':'3.1.02','Fungicidas':'3.1.02',
           'Inseticidas':'3.1.02','Adjuvantes':'3.1.02','Combustível':'3.1.04','Peças':'3.1.05','Embalagem':'3.1.06','Produto agrícola':''}
EMBALAGENS=['Galão','Frasco','Saco','Big bag','Tambor','Caixa','Pallet','Granel']
CONTROLES=['Lote e validade','Só lote','Sem lote']
CONTROLE_GRUPO={'Sementes':'Lote e validade','Herbicidas':'Lote e validade','Fungicidas':'Lote e validade','Inseticidas':'Lote e validade','Adjuvantes':'Lote e validade',
                'Inoculantes':'Lote e validade','Fertilizantes':'Só lote','Corretivos':'Só lote','Produto agrícola':'Só lote','Combustível':'Sem lote','Embalagem':'Sem lote','Peças':'Sem lote'}
# embalagem de entrega: (tipo, conteúdo na unidade-base)
EMB_ITEM={'Glifosato 480':('Galão',20),'2,4-D 806':('Galão',20),'Óleo mineral':('Galão',20),'Fungicida TS':('Galão',5),'Inoculante líquido':('Frasco',1),
          'MAP 11-52':('Saco',50),'KCl 60%':('Big bag',1000),'Ureia 45%':('Saco',50),'NPK 20-05-20':('Saco',50),'Nitrato de cálcio':('Saco',25),'Nitrato de potássio':('Saco',25),
          'Cletodim 240':('Galão',5),'Fungicida A':('Galão',5),'Adjuvante espalhante':('Galão',5),'Inseticida B':('Galão',5),'Fungicida C':('Galão',5),'Acaricida D':('Frasco',1),
          'Atrazina 500':('Galão',20),'Diquat 200':('Galão',20),'Semente de soja 58 W':('Saco',40),'Semente de soja 62 X':('Saco',40),'Semente de milho AG 8700':('Saco',20),
          'Semente de feijão Pérola':('Saco',40),'Diesel S10':('Granel',''),'Soja em grão':('Granel',''),'Café beneficiado':('Saco',1),'Caixa de mamão Formosa 10 kg':('Pallet',60),
          'Calcário dolomítico':('Granel','')}
PRECO_DATA='2026-09-15'   # preço de referência dos itens de plano (última cotação homologada)
# Calcário dolomítico: R$ 180,00/t sintético (SOLO-01, D-10): sem preço, a calagem incluída pela análise daria custo 0 na safra e proposta de R$ 0 na Compra
PRECO_EXTRA={'Diesel S10':6.19,'Caixa de mamão Formosa 10 kg':2.90,'Calcário dolomítico':180.0}
# Caixa do packing com massa declarada (BEN-1; DEC-0510-03 e docs/culturas/UNIDADES-DE-MERCADO.md: mamão formosa em kg ao produtor e
# cx 10 kg no atacado, CEPEA/Ceagesp; havaí por número de frutos fica para quando houver havaí). Fonte única do conteúdo nominal e da tara
# (sintética): o CD-06 e o beneficiamento leem daqui. Massa e tara em texto decimal (kg).
CX_MAMAO='Caixa de mamão Formosa 10 kg'
EMB_PACK={CX_MAMAO:dict(massa='10',tara='0.6',un='un',cultura='Mamão Formosa',fonte='cx 10 kg do formosa (CEPEA/Ceagesp); tara sintética')}
ITENS_NOVOS={'Calcário dolomítico':dict(grupo='Corretivos',un='t')}   # corretivo: cadastrável, homologável e cotável
def preco_ref(n):
    """preço de referência (fonte única do CD-06 e da análise de solo): o dos planos (última cotação homologada) e os extras; a semente de
    cultivar usa o preço da semente da cultura no plano. Sem preço: ''."""
    if not hasattr(preco_ref,'_m'):
        m={}
        for p in D2.PLANOS:
            for a in p['atividades']:
                for x in a['prods']:
                    if 'do cultivo' in x['prod']: m.setdefault('Semente de '+p['cultura'].lower(),x['preco'])
                    else: m.setdefault(x['prod'],x['preco'])
        m.update(PRECO_EXTRA); preco_ref._m=m
    m=preco_ref._m
    return m.get(n, next((v for k,v in m.items() if k.startswith('Semente de ') and n.startswith(k+' ')),''))
# Garantia estruturada (SOLO-01, D-11): uma fonte para o texto do CD-06 (txt) e para a regra da análise de solo (PRNT do corretivo e
# % de K₂O da fonte simples de potássio). Números em texto decimal (a regra usa a aritmética decimal pr*). Filler: PRNT 90 % sintético.
GARANTIA={'MAP 11-52':dict(txt='11% N · 52% P₂O₅'),'KCl 60%':dict(txt='60% K₂O',k2o='60'),'Ureia 45%':dict(txt='45% N'),'NPK 20-05-20':dict(txt='20-05-20'),
          'Nitrato de cálcio':dict(txt='15,5% N · 19% Ca'),'Nitrato de potássio':dict(txt='13% N · 44% K₂O'),'Diesel S10':dict(txt='densidade 0,85 kg/L a 20 °C'),
          'Soja em grão':dict(txt='umidade-base 14%'),'Café beneficiado':dict(txt='umidade-base 12%'),CX_MAMAO:dict(txt='tara '+EMB_PACK[CX_MAMAO]['tara'].replace('.',',')+' kg'),
          'Calcário dolomítico':dict(txt='PRNT 85%',prnt='85'),'Calcário dolomítico filler':dict(txt='PRNT 90%',prnt='90')}
LOCAIS=[('l1','Galpão 1','Santa Rita','Galpão','',''),('l2','Galpão 2','Santa Rita','Galpão','',''),('l3','Almox. defensivos','Santa Rita','Almoxarifado','',''),
        ('l4','Câmara fria','Santa Rita','Câmara fria','',''),('l5','Tanque Sede','Santa Rita','Tanque',15000,'L'),('l6','Silo 01','Santa Rita','Silo',60000,'sc 60 kg'),
        ('l7','Armazém Sede','Santa Rita','Armazém','',''),('l8','Packing','Santa Rita','Packing','',''),('l9','Galpão Boa Vista','Boa Vista','Galpão','',''),
        ('l10','Almox. Lagoa Grande','Lagoa Grande','Almoxarifado','',''),('l11','Galpão de frutas Lagoa Grande','Lagoa Grande','Galpão','','')]
# colheita D-24: o l8 Packing é local de processo (tipo Packing): fruta recebida nele nasce Em processo (R-10); l11 recebe a fruta da Lagoa Grande (D-20)

# ============ CD-07 · estrutura gerencial ============
DIMS=['Empresa','Natureza','Centro de resultado','Centro de responsabilidade','Cultura','Processo','Projeto']
RATEIO=['Horas de máquina','Horas de equipe','Área atendida (ha)','kg processados']
# (id, dimensão, código, nome, superior, rateio, início, fim, tradução, conta, TOP, tem lançamentos)
ESTR=[('d1','Empresa','01','Santa Rita Agro','','','2024-07-01','','Conta do ERP','empresa 1','',True),
      ('d11','Empresa','02','Boa Vista Ltda','','','2026-09-01','','Conta do ERP','empresa 2','',False),
      ('d12','Natureza','3.1','Custo direto de produção','','','2026-07-01','2027-06-30','Conta do ERP','4.1.1','',True),
      ('d2','Natureza','3.1.01','Fertilizantes e corretivos','3.1','','2026-07-01','2027-06-30','Conta do ERP','4.1.1.01','1201',True),
      ('d3','Natureza','3.1.02','Defensivos','3.1','','2026-07-01','2027-06-30','Conta do ERP','4.1.1.02','1201',True),
      ('d4','Natureza','3.1.03','Sementes e inoculantes','3.1','','2026-07-01','2027-06-30','Conta do ERP','4.1.1.03','1201',True),
      ('d13','Natureza','3.1.04','Combustíveis e lubrificantes','3.1','','2026-07-01','2027-06-30','Conta do ERP','4.1.1.04','1202',True),
      ('d14','Natureza','3.1.05','Peças e manutenção','3.1','','2026-07-01','2027-06-30','Conta do ERP','4.1.1.05','1202',False),
      ('d15','Natureza','3.1.06','Embalagens','3.1','','2026-07-01','2027-06-30','Conta do ERP','4.1.1.06','1201',False),
      ('d5','Centro de resultado','CR-SR','Fazenda Santa Rita','','','2024-07-01','','Conta do ERP','centro 201','',True),
      ('d6','Centro de resultado','CR-BV','Fazenda Boa Vista','','','2026-09-01','','Conta do ERP','centro 202','',False),
      ('d7','Centro de responsabilidade','CC-OFI','Oficina · apoio','','Horas de máquina','2024-07-01','','Conta do ERP','centro 310','',True),
      ('d16','Centro de responsabilidade','CC-IRR','Irrigação · apoio','','Área atendida (ha)','2024-07-01','','Conta do ERP','centro 311','',True),
      ('d10','Projeto','PRJ-PIVO3','Expansão pivô 3 · investimento','','','2026-08-01','2027-12-31','Conta do ERP','','',False)]

# ============ Fazenda Lagoa Grande · cadastro (CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01) ============
# Os dados reais do KML do proprietário (pivôs, perímetros/CAR, RL/APP, pontos de água) ficam só no Mac em
# dados_lagoa_kml.py; fora dele vale a demonstração sintética de dados_lagoa_sintetico/ (mesmos nomes e formatos).
from dados_lagoa_fonte import LG_FONTE, LG_GEO, LG_PIVOS, LG_PERIMETROS, LG_AMBIENTAL, LG_AGUA
FAZENDAS.append(dict(id='LG',nome='Lagoa Grande',empresa='',mun='Lagoa Grande/MG',fuso=FUSOS[0],area=LG_PERIMETROS[0]['area'],posse='',arrend='',fim='',custo='',
     car=LG_PERIMETROS[0]['car'],matr='',pend='',sit='Ativa',mf=LG_PERIMETROS[0]['mf']))

# PA-OPER F1 (P18, EX-38 R10): curva ponta × pressão, fonte distinta da vazão alvo. Demonstração: valor de catálogo de ponta de jato plano
# 110-015 a 3 bar (0,59 L/min); não é medição da fazenda. No software real vem do cadastro da ponta, com fonte e vigência.
CURVA_PONTA = {'leque 110-015': [dict(bar=3, lmin=0.59)]}
CURVA_ORIGEM = 'catálogo de ponta (demonstração)'
