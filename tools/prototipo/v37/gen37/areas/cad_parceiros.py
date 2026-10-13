# -*- coding: utf-8 -*-
"""CD-05 Parceiros e fornecedores (módulo próprio; areas.cadastros.build() usa este cd05()).
Cada parceiro é cadastrado uma vez (um CPF/CNPJ) e recebe papéis: Fornecedor, Cliente, Parceiro de crédito, Transportador e Prestador.
- Listagem: filtros rápidos por papel com contagem; colunas comuns (parceiro · CPF/CNPJ, papéis, contato, situação do papel);
  no filtro Fornecedores as colunas passam a grupos homologados e homologação. A cobertura de cotação por grupo é a 2ª aba do bloco.
- Formulário G2: começa pelo CPF/CNPJ com verificação ao digitar ("Já cadastrado: … · Abrir e ativar papel", sem duplicar);
  seções só dos papéis marcados; "Suspender parceiro" com motivo obrigatório no rodapé.
- O motor compara condição por igualdade (cond k/eq). Para "papéis contém X" a tela mantém campos auxiliares escondidos
  (rp_forn, rp_cli, rp_cred, rp_transp, rp_prest = 'Sim' ou '') atualizados a cada clique em Papéis; g2lib.js não foi alterado.
- O formulário padrão (engine._g2form) recebe, só nesta grade, três acréscimos de marcação: título de seção, aviso de duplicidade
  sob o CPF/CNPJ e o botão de suspensão no rodapé. Dados: dados2.FORNECEDORES (fornecedores) + dados_cad (papéis), com os nomes
  já usados em Gestão (GE-08: Banco Terra, Coop Crédito, Fundo Agro Invest), Vendas e Gestão (clientes com pedido, contrato ou título:
  Frutas Real, Torrefação Serra, Rede Hortifrúti BA, Coop Grão Sul, Atacado Bom Preço e CD Horti; Agroquímica Delta, do barter CRE-0095,
  é fornecedor pago em grão) e Logística (Rota Sul Transportes).
- Filtro de papel × filtros de coluna: o menu de coluna só oferece valores das linhas do papel; ao trocar de papel, o filtro de uma coluna
  que sai da grade (e o de "Situação do papel", cujo texto muda com o papel) é limpo."""
import json
from engine import grid, _MINIP, BTN_ST, INK, MUTED, LINE, RED, YEL, YELS
import engine as E
from ui37 import shell37, HEIGHTS37
import dados2 as D2
import dados_cad as DC
from areas.cadastros import H, sel, num, txt, dat, cond, R, js
from areas.cadastros import (cadx_css, abas, pane, se, faixa, prim, bloco_cad, estado_cab, md, mestre, det_cab, vazio, md_css, criar_cab)

F_=H('false')
# ================= CD-05 · Parceiros e fornecedores =================
PAPEIS=DC.PAPEIS                      # Fornecedor · Cliente · Parceiro de crédito · Transportador · Prestador
CANAIS=['E-mail','WhatsApp']
OPS=sorted({c['op'] for c in D2.CONJ})
VEICULOS=['Bitrem graneleiro 37 t','Carreta graneleira 30 t','Truck graneleiro 14 t','Baú refrigerado 12 t']
PAG_DEF=DC.COND_PAG[0]
# prazos usados nos pedidos de Vendas (VE-04: CIF 14 d, 21 d) somados aos do cadastro, em ordem de prazo
PAG_14,PAG_21='14 dias após a entrega comprovada','21 dias após a entrega comprovada'
COND_PAG=[DC.COND_PAG[0],PAG_14,PAG_21]+[c for c in DC.COND_PAG[1:] if c not in (PAG_14,PAG_21)]
X=DC.PAPEL_EXTRA
CONTATO=getattr(D2,'CONTATO_FORN',{})
# CPF/CNPJ exibido e comparado = f['cnpj'], o mesmo que o Portal do parceiro (PT-07) mostra; o campo doc do dados2 não é usado aqui.
OUTROS=[
 # Coop Grão Sul: PV-030 (FOB · contra entrega), CT-201 e CT-203 (FOB), RT-0109, FAT-2079 e RC-13 em Vendas e Gestão
 dict(id='P08',nome='Coop Grão Sul',cnpj='98.765.432/0001-98',papeis=['Cliente'],email='originacao@coopgraosul.coop.br',whats='65 99210-4455',
      contato='Renata Paiva',canais=['E-mail','WhatsApp'],entrega='Retira no Armazém Sede (FOB) · seg–sáb 06–22h',
      **{k:X['P08'][k] for k in ('prod','pag','lim','limv')}),
 dict(id='P09',nome='TransVale Transportes',cnpj='44.222.111/0001-18',papeis=['Transportador'],email='fretes@transvale.com.br',whats='65 99321-7788',
      contato='Edson Lima',canais=['E-mail','WhatsApp'],rntrc='45123098',veic=['Bitrem graneleiro 37 t','Truck graneleiro 14 t']),
 # Banco Terra: credor do CRE-0102 (Gestão GE-08) e do Portal PT-04, onde Rafael Lima analisa o crédito e Carla Souza confere documentos
 dict(id='P10',nome='Banco Terra',cnpj='11.000.222/0001-20',papeis=['Parceiro de crédito'],email='agro@bancoterra.com.br',whats='',
      contato='Carla Souza',canais=['E-mail'],linhas=X['P10']['linhas'],gar=X['P10']['gar'],
      ger='Rafael Lima',ger_email='rafael.lima@bancoterra.com.br',ger_tel='64 99640-2210'),
 dict(id='P11',nome='Adão Ferreira',cnpj='123.456.789-09',papeis=['Prestador'],email='',whats='65 99102-3344',
      contato='Adão Ferreira',canais=['WhatsApp'],ops=X['P11']['ops']),
]
_N={p['id']:p for p in DC.NOVOS_PARCEIROS}
def _novo(i,**kw):
    d={k:v for k,v in _N[i].items() if k not in ('grupos','homologado')}; d.update(kw); return d
NOVOS=[
 # Frutas Real: PV-031 entrega CIF em Vitória/ES, janela 11:00–12:00 (Logística · Carga 07)
 _novo('P12',entrega='CD Frutas Real · Vitória/ES · seg–sáb 06–12h'),
 # Torrefação Serra: PV-028 é FOB armazém (Logística) → retira na fazenda
 _novo('P13',entrega='Retira no Armazém Sede (FOB) · seg–sex 07–16h'),
 _novo('P14'),
 # Coop Crédito: nome usado em Gestão (conta safra, CRE-0098 trator com alienação do bem, proposta do CRE-0102)
 _novo('P15',nome='Coop Crédito',cnpj=D2.cnpj_valido('08.604.771/0001-00'),email='agro@coopcredito.coop.br',
       linhas=['Custeio','Investimento','Comercialização'],gar=['Penhor de safra','Alienação fiduciária','Aval'],
       ger='Márcio Reis',ger_email='marcio.reis@coopcredito.coop.br',ger_tel='64 99420-1180'),
 dict(id='P16',nome='Fundo Agro Invest',cnpj=D2.cnpj_valido('19.880.214/0001-00'),papeis=['Parceiro de crédito'],email='credito@fundoagroinvest.com.br',whats='',
      contato='Tânia Moraes',canais=['E-mail'],linhas=['Comercialização','CPR'],gar=['CPR','Aval'],
      ger='Tânia Moraes',ger_email='tania.moraes@fundoagroinvest.com.br',ger_tel='11 99812-4470'),
 # Rota Sul Transportes: baú refrigerado 12 t da Carga 07 (Logística LO-01/LO-02)
 dict(id='P17',nome='Rota Sul Transportes',cnpj=D2.cnpj_valido('23.114.560/0001-00'),papeis=['Transportador'],email='fretes@rotasul.com.br',whats='27 99714-2230',
      contato='Wagner Dias',canais=['E-mail','WhatsApp'],rntrc='38017642',veic=['Baú refrigerado 12 t']),
 # Atacado Bom Preço: PV-029 milho CIF 14 d (VE-04), FAT-2090 atrasada (GE-05), RC-14 (VE-06)
 dict(id='P18',nome='Atacado Bom Preço',cnpj=D2.cnpj_valido('36.207.915/0001-00'),papeis=['Cliente'],email='compras@atacadobompreco.com.br',whats='62 99530-1177',
      contato='Rogério Alves',canais=['E-mail','WhatsApp'],prod=['Milho em grão'],entrega='CD Atacado Bom Preço · Goiânia/GO · seg–sex 06–14h',
      pag=PAG_14,lim=300000,limv='2027-03-31'),
 # CD Horti: PV-034 mamão A CIF 28 d, Carga 07 para Vitória/ES (VE-04, app do motorista)
 dict(id='P19',nome='CD Horti',cnpj=D2.cnpj_valido('29.644.083/0001-00'),papeis=['Cliente'],email='recebimento@cdhorti.com.br',whats='27 99640-3321',
      contato='Mirela Costa',canais=['E-mail','WhatsApp'],prod=['Mamão Formosa classe A'],entrega='CD Horti · Vitória/ES · seg–sáb 06–12h',
      pag=DC.COND_PAG[1],lim=100000,limv='2027-01-31'),
 # Agroquímica Delta: barter de defensivos pago em soja (CPR CRE-0095 em VE-05 e GE-08). Como a Fertisul no BT-090, é fornecedor
 # pago em grão, não cliente; fornece pelo contrato, fora da cotação, por isso não homologado
 dict(id='P20',nome='Agroquímica Delta',cnpj=D2.cnpj_valido('40.581.337/0001-00'),papeis=['Fornecedor'],email='barter@agroquimicadelta.com.br',whats='',
      contato='Sérgio Matos',canais=['E-mail'],grupos=[],homologado=False),
]
def _canais(f):
    """canais autorizados: usa o campo do cadastro; sem ele, autoriza os canais que o parceiro informou (e-mail e/ou WhatsApp)."""
    if f.get('canais') is not None: return [c for c in f['canais'] if c in CANAIS]
    return [c for c,k in (('E-mail','email'),('WhatsApp','whats')) if f.get(k)]
def _parceiros():
    out=[]
    for f in D2.FORNECEDORES:           # Coop. Vale (F06) também é cliente
        p=dict(f); ex=X.get(f['id'],{}); p['papeis']=ex.get('papeis',['Fornecedor']); p.update({k:v for k,v in ex.items() if k!='papeis'}); out.append(p)
    return out+OUTROS+NOVOS
def _v(f):
    j=lambda k: '; '.join(f.get(k) or [])
    return dict(cnpj=f['cnpj'],nome=f['nome'],papeis=j('papeis'),contato=f.get('contato') or CONTATO.get(f['id'],''),email=f.get('email',''),whats=f.get('whats',''),
                canais='; '.join(_canais(f)),grupos=j('grupos'),homol='Sim' if f.get('homologado') else 'Não',
                prod=j('prod'),entrega=f.get('entrega',''),pag=f.get('pag') or PAG_DEF,lim=f.get('lim',''),limv=f.get('limv',''),
                linhas=j('linhas'),gar=j('gar'),ger=f.get('ger',''),ger_email=f.get('ger_email',''),ger_tel=f.get('ger_tel',''),
                rntrc=f.get('rntrc',''),veic=j('veic'),ops=j('ops'),sit=f.get('sit','Ativo'),motivo=f.get('motivo',''))

# condição por papel: campo auxiliar escondido, mantido pela tela (o motor só compara igualdade)
RP={'Fornecedor':'rp_forn','Cliente':'rp_cli','Parceiro de crédito':'rp_cred','Transportador':'rp_transp','Prestador':'rp_prest'}
NUNCA=cond('_nunca','1')
def _pc(p): return cond(RP[p],'Sim')
def multi(k,l,opts,req=True,**kw): return dict(k=k,l=l,t='multi',opts=list(opts),req=req,**kw)
CAMPOS=[txt('cnpj','CPF ou CNPJ',newOnly=True,help='CPF com 11 dígitos ou CNPJ com 14; conferimos se já existe enquanto você digita.'),
        txt('nome','Nome ou razão social'),
        multi('papeis','Papéis',PAPEIS),
        txt('contato','Nome do contato',req=False,help='Obrigatório para homologar fornecedor.'),
        dict(k='email',l='E-mail',t='email',help='Obrigatório para homologar fornecedor: a cotação vai por e-mail (simulado).'),
        dict(k='whats',l='WhatsApp',t='tel',help='Com DDD.'),
        multi('canais','Canais autorizados',CANAIS,req=False,help='O parceiro autorizou receber mensagens por este canal (simulado).'),
        # Fornecedor
        multi('grupos','Grupos homologados',D2.GRUPOS,req=False,cond=_pc('Fornecedor'),help='Grupos de insumo em que pode receber cotação.'),
        sel('homol','Homologado',['Sim','Não'],cond=_pc('Fornecedor'),**{'def':'Não'},help='Fornecedor não homologado não recebe cotação, mesmo com grupo marcado.'),
        # Cliente
        multi('prod','Produtos de interesse',DC.PRODUTOS_VENDA,cond=_pc('Cliente')),
        txt('entrega','Local e horário de entrega',req=False,cond=_pc('Cliente'),help='Onde recebe ou retira e em que horário.'),
        sel('pag','Condição de pagamento',COND_PAG,cond=_pc('Cliente'),**{'def':PAG_DEF},help='O vencimento conta a partir do evento.'),
        num('lim','Limite de crédito comercial','R$',req=False,min=0,cond=_pc('Cliente')),
        dat('limv','Validade da análise de crédito',req=False,cond=_pc('Cliente'),help='Depois desta data, novos pedidos ficam retidos até nova análise.'),
        # Parceiro de crédito
        multi('linhas','Linhas de crédito',DC.LINHAS_CRED,cond=_pc('Parceiro de crédito')),
        multi('gar','Garantias aceitas',DC.GARANTIAS,req=False,cond=_pc('Parceiro de crédito')),
        txt('ger','Gerente do crédito',cond=_pc('Parceiro de crédito')),
        dict(k='ger_email',l='E-mail do gerente',t='email',req=False,cond=_pc('Parceiro de crédito')),
        dict(k='ger_tel',l='Telefone do gerente',t='tel',req=False,cond=_pc('Parceiro de crédito')),
        # Transportador
        txt('rntrc','RNTRC',cond=_pc('Transportador'),help='8 dígitos do registro na ANTT.'),
        multi('veic','Veículos e capacidade',VEICULOS,cond=_pc('Transportador')),
        # Prestador
        multi('ops','Operações que presta',OPS,cond=_pc('Prestador')),
        # Suspensão (aparece ao clicar em Suspender parceiro)
        txt('motivo','Motivo da suspensão',cond=cond('sit','Suspenso'),help='Aparece na listagem enquanto durar a suspensão.'),
        # escondidos: situação e papéis marcados (condição das seções)
        dict(k='sit',l='Situação',t='txt',req=False,cond=NUNCA,**{'def':'Ativo'})]+[dict(k=k,l=k,t='txt',req=False,cond=NUNCA) for k in RP.values()]
SECOES={'grupos':'FORNECEDOR','prod':'CLIENTE','linhas':'PARCEIRO DE CRÉDITO','rntrc':'TRANSPORTADOR','ops':'PRESTADOR','motivo':'SUSPENSÃO'}
# uma variável por coluna (TABELAS-FOCO, 04/10/2026): parceiro e CPF/CNPJ; contato, WhatsApp, e-mail e canais autorizados; a situação de cada papel
# em chip (multivalorada: filtra por estado). No filtro de um papel entram as colunas desse papel (grupos, limite e validade, linhas e garantias,
# RNTRC e veículos, operações); em Todos elas ficam no painel do parceiro. Listas (papéis, canais, grupos…) filtram por item. Com parceiro
# suspenso, a coluna "Motivo da suspensão" entra depois da situação (a listagem mostra o motivo enquanto durar a suspensão).
_ID=[dict(k='nome',l='Parceiro',w=180),dict(k='cnpj',l='CPF/CNPJ',w=150)]
_CT=[dict(k='cont',l='Contato',w=140),dict(k='whats',l='WhatsApp',w=130),dict(k='email',l='E-mail',w=220),dict(k='canais',l='Canais autorizados',multi=True,w=150)]
_SIT=dict(k='papel',l='Situação do papel',multi=True,w=220)
_PAP=dict(k='papeis',l='Papéis',multi=True,w=170)
COLS_T=_ID+[_PAP]+_CT+[_SIT]
COLS_P={'Fornecedor':_ID+[dict(k='grupos',l='Grupos homologados',multi=True,w=260)]+_CT+[dict(k='homol',l='Homologado',w=130)],
        'Cliente':_ID+[_PAP]+_CT+[dict(k='lim',l='Limite de crédito',t='num',a='r',un='R$',d=0),dict(k='limv',l='Validade da análise de crédito',t='date'),_SIT],
        'Parceiro de crédito':_ID+[_PAP]+_CT+[dict(k='linhas',l='Linhas de crédito',multi=True,w=220),dict(k='gar',l='Garantias aceitas',multi=True,w=240),_SIT],
        'Transportador':_ID+[_PAP]+_CT+[dict(k='rntrc',l='RNTRC'),dict(k='veic',l='Veículos',multi=True,w=260),_SIT],
        'Prestador':_ID+[_PAP]+_CT+[dict(k='ops',l='Operações que presta',multi=True,w=220),_SIT]}
COL_MOT=dict(k='motivo',l='Motivo da suspensão',w=220)
FILTROS=[('','Todos'),('Fornecedor','Fornecedores'),('Cliente','Clientes'),('Parceiro de crédito','Parceiros de crédito'),('Transportador','Transportadores'),('Prestador','Prestadores')]

def _form_extra(form):
    """acréscimos de marcação no formulário padrão desta grade: título de seção, aviso de duplicidade do CPF/CNPJ e suspensão no rodapé."""
    a='<label for="{{f.fid}}"'
    sec=(f'<sc-if value="{H("f.hasSec")}" hint-placeholder-val="{F_}"><div style="margin-top: 6px; padding-top: 12px; border-top: 1px solid {LINE}; '
         f'font-size: 11.5px; font-weight: 800; letter-spacing: .06em; color: {INK};">{H("f.sec")}</div></sc-if>')
    b='{{f.help}}</span></sc-if>'
    dup=(f'<sc-if value="{H("f.hasDup")}" hint-placeholder-val="{F_}"><div role="status" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; '
         f'padding: 8px 10px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;"><span style="flex-grow: 1;">{H("f.dupT")}</span>'
         f'<button type="button" onClick="{H("f.dupGo")}" style="{_MINIP}">Abrir e ativar papel</button></div></sc-if>')
    c=f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">'
    rod=(f'<sc-if value="{H("cd5_susp")}" hint-placeholder-val="{F_}"><button type="button" onClick="{H("cd5_suspender")}" style="{BTN_ST(False,True)} color: {RED}; border-color: {RED};">Suspender parceiro</button></sc-if>'
         f'<sc-if value="{H("cd5_reat")}" hint-placeholder-val="{F_}"><button type="button" onClick="{H("cd5_reativar")}" style="{BTN_ST(False,True)}">{H("cd5_reatT")}</button></sc-if>'
         '<span style="flex-grow: 1;"></span>')
    for k in (a,b,c): assert form.count(k)==1, k
    return form.replace(a,sec+a,1).replace(b,b+dup,1).replace(c,c+rod,1)
def _filtros():
    # filtro por papel dentro do bloco, à esquerda da barra da grade (também troca as colunas: Fornecedores mostra grupos e homologação)
    return (f'<div role="group" aria-label="Filtrar por papel" class="cadx-qf">'
            f'<sc-for list="{H("cd5_fil")}" as="x" hint-placeholder-count="{len(FILTROS)}"><button type="button" aria-pressed="{H("x.cur")}" onClick="{H("x.go")}" style="{H("x.st")}">'
            f'{H("x.t")}<span style="{H("x.nst")}">{H("x.n")}</span></button></sc-for></div>')
# CADUX (09/10/2026): mestre Todos · Fornecedores · Clientes · Crédito · Transportadores · Prestadores · Grupos de insumo → parceiros do papel
# (as colunas do papel) → painel do parceiro em consulta (identidade e um bloco por papel; no Fornecedor, os grupos homologados no topo).
# Grupos de insumo só em consulta (a fonte é o CD-06): fornecedores que recebem cotação e itens do grupo. A busca acha o fornecedor pelo insumo.
PAPEL_SLUG=[('fornecedor','Fornecedor','Fornecedores'),('cliente','Cliente','Clientes'),('credito','Parceiro de crédito','Crédito'),
            ('transportador','Transportador','Transportadores'),('prestador','Prestador','Prestadores')]
def cd05():
    fname='CD-05.dc.html'; E._reset_screen(fname)
    rows=[R(f['id'],_v(f)) for f in _parceiros()]
    g=grid(COLS_T,rows,gid='g_forn',total=False,frame=False,search=False,tools=f'<span class="cmd-conta">{H("cd5_conta")}</span>',
        edit=dict(m='form',title='Parceiro',newTitle='Criar parceiro',alvo='parceiro',
                  sub='Um cadastro por CPF ou CNPJ: comece pelo documento (conferimos se já existe) e marque os papéis; preencha só as seções deles.',fields=CAMPOS))
    assert 'g_forn_F.open' in E.EXTRA[-1]; E.EXTRA[-1]=_form_extra(E.EXTRA[-1])
    # Grupo | Situação | Fornecedores que recebem cotação | Itens no CD-06 (consulta; a fonte do grupo é o CD-06)
    cob=grid([dict(k='g',l='Grupo',w=220),dict(k='sit',l='Situação',w=200),dict(k='n',l='Fornecedores que recebem cotação',t='num',a='r'),dict(k='ni',l='Itens no CD-06',t='num',a='r')],[],
        gid='g_cob',total=False,search=False,frame=False,tools=f'<span class="cmd-conta">{H("cd5_contaG")}</span>',
        edit=dict(m='origin',title='Grupo',alvo='grupo',fields=[dict(k='g',l='Grupo',t='txt',ro=True),dict(k='n',l='Fornecedores que recebem cotação',t='num',ro=True)]))
    cadx_css(); md_css()
    det=det_cab()+f'<div class="cadx-dados">'+vazio('cd5_v')+se('cd5_forn_on',g,True)+se('cd5_cob_on',cob)+'</div>'
    corpo=md(mestre('Papéis','Buscar parceiro, CNPJ, grupo ou insumo'),det,'Parceiros e fornecedores')
    from areas.cadastros import _itens
    itg={}
    for n,d in _itens().items(): itg.setdefault(d['grupo'],[]).append(n)
    import dados_cad as _DC
    for n,d in getattr(_DC,'ITENS_NOVOS',{}).items(): itg.setdefault(d['grupo'],[]).append(n)
    js({},'const GRUPOS_='+json.dumps(D2.GRUPOS,ensure_ascii=False)+', COLS_T='+json.dumps(COLS_T,ensure_ascii=False)+', COLS_P='+json.dumps(COLS_P,ensure_ascii=False)+', COL_MOT='+json.dumps(COL_MOT,ensure_ascii=False)
       +', FILTROS='+json.dumps(FILTROS,ensure_ascii=False)+', RP='+json.dumps(RP,ensure_ascii=False)+', SECOES='+json.dumps(SECOES,ensure_ascii=False)
       +', PAPEIS_='+json.dumps(PAPEIS,ensure_ascii=False)+', PSLUG='+json.dumps(PAPEL_SLUG,ensure_ascii=False)+', ITG='+json.dumps(itg,ensure_ascii=False)+';\n'+CD05JS)
    HEIGHTS37[fname]=1000   # sem rolagem de página: só a lista rola
    shell37('CD-05','Parceiros e fornecedores',corpo,fname=fname,status=None,primary_html=criar_cab('cd5_criar','+ Criar parceiro'),search=False)
    estado_cab(fname,'Parceiros e fornecedores','cd5e')
    from areas.cadastros import ncol_dinamico
    ncol_dinamico(fname,['cd5_ncol',None])   # as colunas do papel mudam a quantidade de colunas
CD05JS=r'''
const OCULTO='cadm_g_forn';   // linha fora do papel escolhido no mestre (marca do mestre: a contagem "N de M" é do papel)
const C5G='grupos';
function dig(s){ return String(s||'').replace(/\D/g,''); }
// dígitos verificadores (módulo 11): CPF ou CNPJ com dígito errado não é aceito
function docOk(dg){ if(/^(\d)\1+$/.test(dg)) return false; const N=k=>Number(dg[k]);
  if(dg.length===11){ for(const n of [9,10]){ let s=0; for(let i=0;i<n;i++) s+=N(i)*(n+1-i); if((s*10)%11%10!==N(n)) return false; } return true; }
  if(dg.length===14){ const w=[6,5,4,3,2,9,8,7,6,5,4,3,2]; for(const n of [12,13]){ let s=0; for(let i=0;i<n;i++) s+=N(i)*w[i+13-n]; const r=s%11; if((r<2?0:11-r)!==N(n)) return false; } return true; }
  return false; }
function ordena(a){ return a.slice().sort((x,y)=>PAPEIS_.indexOf(x)-PAPEIS_.indexOf(y)); }
function rpFlags(pp){ const o={}; Object.keys(RP).forEach(p=>{ o[RP[p]]=pp.indexOf(p)>=0?'Sim':''; }); return o; }
function draftSet(self,gid,patch){ const cur=g2st(self,gid).fm; if(!cur) return; const er=Object.assign({},cur.errs||{}); Object.keys(patch).forEach(k=>{ delete er[k]; });
  g2set(self,gid,{fm:Object.assign({},cur,{draft:Object.assign({},cur.draft,patch),errs:er,warn:false})}); }
function dupDoc(self,doc,rid){ const dg=dig(doc); if(dg.length!==11&&dg.length!==14) return null; return RW(self,'g_forn').find(r=>r.id!==rid&&dig(r.v.cnpj)===dg)||null; }
// situação de cada papel (no filtro de um papel, só a dele): só o estado, em chip; o valor (limite, linhas, RNTRC…) fica na coluna do papel e no painel
function sitPapeis(V,pp,so){ if(V.sit==='Suspenso') return [{t:'Suspenso',c:'gray'}];
  const out=[]; pp.filter(p=>!so||p===so).forEach(p=>{
    if(p==='Fornecedor') out.push(V.homol==='Sim'?{t:'Homologado',c:'green'}:{t:'Não homologado',c:'gray'});
    if(p==='Cliente'){ const lim=Number(V.lim)||0; out.push(!lim?{t:'Sem limite de crédito',c:'yellow'}:(V.limv&&V.limv<HOJE?{t:'Limite vencido',c:'red'}:{t:'Limite vigente',c:'green'})); }
    if(p==='Parceiro de crédito') out.push(ml(V.linhas).length?{t:'Ativo',c:'green'}:{t:'Sem linha de crédito',c:'yellow'});
    if(p==='Transportador') out.push(V.rntrc?{t:'Ativo',c:'green'}:{t:'Sem RNTRC',c:'yellow'});
    if(p==='Prestador') out.push(ml(V.ops).length?{t:'Ativo',c:'green'}:{t:'Sem operação',c:'yellow'}); });
  return out; }
function c5papel(sel){ const x=PSLUG.find(p=>p[0]===sel); return x?x[1]:''; }
function c5slug(papel){ const x=PSLUG.find(p=>p[1]===papel); return x?x[0]:''; }
function cotaveis(rows){ return rows.filter(r=>ml(r.v.papeis).indexOf('Fornecedor')>=0&&r.v.sit!=='Suspenso'&&r.v.homol==='Sim'&&r.v.email&&ml(r.v.canais).indexOf('E-mail')>=0); }
// a busca casa nome, CPF/CNPJ, contato, papéis, grupos homologados e os itens desses grupos ("Tebuconazol" → fornecedores de Fungicidas)
function c5hay(V){ const gg=ml(V.grupos); return [V.nome,V.cnpj,V.contato,V.papeis,V.grupos,V.email].concat(V.homol==='Sim'?gg.reduce((a,g)=>a.concat(ITG[g]||[]),[]):[]).join(' '); }
// troca o papel: limpa o filtro de coluna que sai da grade e o de "Situação do papel" (o texto dela muda com o papel)
function c5limpa(self,fp){ if(self.__c5p===fp) return; self.__c5p=fp; const g=g2st(self,'g_forn'), ks=((fp&&COLS_P[fp])||COLS_T).map(c=>c.k), f={};
  Object.keys(g.f||{}).forEach(x=>{ if(ks.indexOf(x)>=0&&x!=='papel'&&(g.f[x]||[]).length) f[x]=g.f[x]; }); if(Object.keys(g.f||{}).length) g2set(self,'g_forn',{f:f,fmc:null}); }
// o que fazer com o parceiro: limite vencido (Cliente) → fornecedor com grupo marcado e não homologado; o verbo abre o formulário no campo
function c5pend(r,fp){ const V=r.v; const pp=ml(V.papeis); if(V.sit==='Suspenso') return null;
  if((!fp||fp==='Cliente')&&pp.indexOf('Cliente')>=0&&Number(V.lim)&&V.limv&&V.limv<HOJE) return {cor:'yellow',t:'Limite de crédito de '+V.nome+' vencido em '+br(V.limv)+': novos pedidos ficam retidos até nova análise.',prim:{t:'Renovar limite de '+V.nome,campo:'limv'},s:'limite de '+V.nome+' vencido'};
  if((!fp||fp==='Fornecedor')&&pp.indexOf('Fornecedor')>=0&&V.homol!=='Sim'&&ml(V.grupos).length) return {cor:'yellow',t:V.nome+' tem grupo marcado e não é homologado: não recebe cotação.',prim:{t:'Homologar fornecedor',campo:'homol'},s:V.nome+' não homologado'};
  return null; }
function c5pends(self,fp){ return RW(self,'g_forn').filter(r=>!fp||ml(r.v.papeis).indexOf(fp)>=0).map(r=>{ const p=c5pend(r,fp); return p?Object.assign(p,{rid:r.id}):null; }).filter(Boolean); }
function c5prox(self,ps,ok){ if(!ps.length) return {cor:'green',t:ok||'Em dia.'}; const p=ps[0], r=ps.slice(1);
  return {cor:p.cor,t:p.t,prim:{t:p.prim.t,go:()=>{ g2open(self,GR('g_forn'),p.rid,null); setTimeout(()=>g2editar(self,GR('g_forn'),p.rid,p.prim.campo),0); }},mais:r.length?('e mais '+r.length+': '+r.map(x=>x.s).join('; ')+'.'):''}; }
function c5consPar(self,r){ const V=r.v; const pp=ml(V.papeis); const S=sitPapeis(V,pp,''); const p=c5pend(r,'');
  const bl=[{t:'Identidade',lin:[{l:'CPF ou CNPJ',v:V.cnpj||'—'},{l:'Contato',v:V.contato||'—'},{l:'E-mail',v:V.email||'—'},{l:'WhatsApp',v:V.whats||'—'},{l:'Canais autorizados',v:ml(V.canais).join(', ')||'nenhum'},{l:'Papéis',v:pp.join(', ')}]}];
  if(pp.indexOf('Fornecedor')>=0){ const gg=ml(V.grupos); bl.unshift({t:'Fornecedor · grupos homologados',fil:gg.map(gn=>({t:gn,sub:(ITG[gn]||[]).length+' itens no CD-06',chip:V.homol==='Sim'?{t:'Recebe cotação',c:'green'}:{t:'Não homologado',c:'gray'},
      go:()=>{ g2set(self,'g_forn',{fm:null}); g2open(self,GR('g_cob'),'c_'+gn,null,{pai:{gid:'g_forn',rid:r.id,t:V.nome}}); }})),nota:gg.length?(V.homol==='Sim'?'':'Não homologado: não recebe cotação, mesmo com grupo marcado.'):'Nenhum grupo marcado.'}); }
  if(pp.indexOf('Cliente')>=0) bl.push({t:'Cliente',lin:[{l:'Produtos de interesse',v:ml(V.prod).join(', ')||'—'},{l:'Local e horário de entrega',v:V.entrega||'—'},{l:'Condição de pagamento',v:V.pag||'—'},
      {l:'Limite de crédito comercial',v:Number(V.lim)?'R$ '+nf(V.lim,0):'—'},{l:'Validade da análise',v:V.limv?br(V.limv):'—',cor:(V.limv&&V.limv<HOJE)?'red':''}]});
  if(pp.indexOf('Parceiro de crédito')>=0) bl.push({t:'Parceiro de crédito',lin:[{l:'Linhas',v:ml(V.linhas).join(', ')||'—'},{l:'Garantias aceitas',v:ml(V.gar).join(', ')||'—'},{l:'Gerente',v:V.ger||'—'}]});
  if(pp.indexOf('Transportador')>=0) bl.push({t:'Transportador',lin:[{l:'RNTRC',v:V.rntrc||'a informar',cor:V.rntrc?'':'yellow'},{l:'Veículos',v:ml(V.veic).join(', ')||'—'}]});
  if(pp.indexOf('Prestador')>=0) bl.push({t:'Prestador',lin:[{l:'Operações que presta',v:ml(V.ops).join(', ')||'—'}]});
  if(V.sit==='Suspenso') bl.push({t:'Suspensão',lin:[{l:'Motivo',v:V.motivo||'—',cor:'red'}]});
  return {titulo:'Parceiro · '+V.nome,sub:(V.cnpj||'')+' · '+S.map(x=>x.t).join(', '),
    prox:V.sit==='Suspenso'?{cor:'gray',t:'Suspenso: fora de cotação, oferta e crédito; o histórico continua.'}:(p?{cor:p.cor,t:p.t,prim:{t:p.prim.t,go:()=>g2editar(self,GR('g_forn'),r.id,p.prim.campo)}}:{cor:'green',t:'Em dia nos papéis: '+S.map(x=>x.t).join(', ')+'.'}),
    sec:[{t:'Editar parceiro',go:()=>g2editar(self,GR('g_forn'),r.id)}],blocos:bl}; }
function c5consGrp(self,r){ const gn=r.v.g; const ok=cotaveis(RW(self,'g_forn')).filter(x=>ml(x.v.grupos).indexOf(gn)>=0); const outros=RW(self,'g_forn').filter(x=>ml(x.v.grupos).indexOf(gn)>=0&&ok.indexOf(x)<0);
  const it=ITG[gn]||[];
  return {titulo:'Grupo · '+gn,sub:'Grupo de insumo do CD-06 · '+ok.length+(ok.length===1?' fornecedor recebe':' fornecedores recebem')+' cotação',
    prox:ok.length?(ok.length===1?{cor:'yellow',t:'Sem concorrência: só '+ok[0].v.nome+' recebe a cotação de '+gn+'.'}:{cor:'green',t:'Com concorrência: '+ok.length+' fornecedores recebem a cotação.'})
      :{cor:'yellow',t:'Nenhum fornecedor homologado com e-mail autorizado recebe a cotação de '+gn+'.',quem:'Homologue um fornecedor no painel dele (Editar parceiro).'},
    sec:[],blocos:[{t:'Fornecedores que recebem cotação',fil:ok.map(x=>({t:x.v.nome,sub:(x.v.contato?x.v.contato+' · ':'')+(x.v.email||''),go:()=>{ g2set(self,'g_cob',{fm:null}); g2open(self,GR('g_forn'),x.id,null,{pai:{gid:'g_cob',rid:r.id,t:gn}}); }})),nota:ok.length?'':'Nenhum.'},
      outros.length?{t:'Com o grupo marcado, sem receber cotação',fil:outros.map(x=>({t:x.v.nome,sub:x.v.sit==='Suspenso'?'suspenso':(x.v.homol!=='Sim'?'não homologado':'sem e-mail autorizado'),go:()=>{ g2set(self,'g_cob',{fm:null}); g2open(self,GR('g_forn'),x.id,null,{pai:{gid:'g_cob',rid:r.id,t:gn}}); }}))}:null,
      {t:'Itens do grupo no CD-06',lin:[{l:'Itens',v:it.length?it.join(', '):'nenhum'}],lks:[{t:'Abrir grupo nos Produtos',h:'CD-06.dc.html#grp='+encodeURIComponent(gn)}],nota:'A fonte do grupo é o CD-06: aqui não se cria nem renomeia grupo.'}]}; }
function c5cfg(self){ cmdIni(self,{gp:'papel',ip:{g_forn:'par',g_cob:'grp'},
  grupoDe:(s,gid,r,pedido)=>{ if(gid==='g_cob') return C5G; if(pedido){ const fq=c5papel(pedido); if(fq&&ml(r.v.papeis).indexOf(fq)>=0) return pedido; } const sel=cmdSel(s); if(sel===''&&s.state.mx_sel!==undefined) return ''; const pp=ml(r.v.papeis); const fp=c5papel(sel); return (fp&&pp.indexOf(fp)>=0)?sel:(sel===C5G?'':(sel||'')); },
  existeGrupo:(s,id)=>id===C5G||!!c5papel(id),
  normItem:(gid,rid)=>(gid==='g_cob'&&String(rid).indexOf('c_')!==0)?'c_'+rid:rid,
  reg:(s,id)=>RW(s,'g_forn').some(r=>r.id===id)?{gid:'g_forn',rid:id}:null,
  indisp:(id,gid)=>cmdIndisp(gid==='g_cob'?'Grupo de insumo':'Parceiro',id),
  indispGrupo:(id)=>'Papel “'+id+'” não existe nos Cadastros.',
  inativo:()=>null,
  novo:(s)=>{ if(s.__v&&s.__v.cd5_criar) s.__v.cd5_criar(); },
  anuncio:(s,id)=>{ if(id===C5G) return 'Grupos de insumo: '+GRUPOS_.length+' grupos'; const fp=c5papel(id); const n=RW(s,'g_forn').filter(r=>!fp||ml(r.v.papeis).indexOf(fp)>=0).length; const p=c5pends(s,fp).length;
    return (fp?(PSLUG.find(x=>x[0]===id)||[])[2]:'Todos os parceiros')+': '+n+(n===1?' parceiro':' parceiros')+' · '+(p?p+' a resolver':'Em dia'); },
  cons:{g_forn:c5consPar,g_cob:c5consGrp}}); }
function PREVALS(self,v){ if(self.state.mx_q===undefined){ const k=cadKeepLe('q'); if(k) self.state.mx_q=k; }
  const rows=RW(self,'g_forn'); const sel=cmdSel(self); const fp=c5papel(sel); const q=self.state.mx_q||''; c5limpa(self,fp);
  const cb=(fp&&COLS_P[fp])||COLS_T; const susp=rows.some(r=>r.v.sit==='Suspenso'&&(!fp||ml(r.v.papeis).indexOf(fp)>=0));
  // ≤ 7 colunas (AC-09): Parceiro | Situação do papel | as colunas próprias do papel | contato e canais até completar; CPF/CNPJ vai para o painel
  const base=[cb[0],cb.find(c=>c.k==='papel')||cb.find(c=>c.k==='homol')].filter(Boolean); const ct=['cont','email','whats','canais'];
  const prop=cb.filter(c=>base.indexOf(c)<0&&c.k!=='cnpj'&&ct.indexOf(c.k)<0); const cts=ct.map(k=>cb.find(c=>c.k===k)).filter(Boolean);
  const mot=susp?[COL_MOT]:[]; GR('g_forn').cols=base.concat(prop).concat(cts.slice(0,Math.max(0,7-base.length-prop.length-mot.length))).concat(mot); v.cd5_ncol=GR('g_forn').cols.length;
  rows.forEach(r=>{ const V=r.v; const pp=ml(V.papeis); Object.assign(V,rpFlags(pp)); if(!V.sit) V.sit='Ativo';
    const forn=pp.indexOf('Fornecedor')>=0, hom=V.homol==='Sim', gg=ml(V.grupos), susp=V.sit==='Suspenso';
    r.p.nome=[{k:'b',t:V.nome||''}]; r.s.nome=V.nome||''; r.p.cnpj=[V.cnpj?{k:'txt',t:V.cnpj}:{k:'mut',t:'—'}]; r.s.cnpj=V.cnpj||'';
    const M=r.m=Object.assign({},r.m||{}); const lst=(k,a)=>{ M[k]=a.map(x=>({id:x,l:x})); r.p[k]=[a.length?{k:'txt',t:a.join(', ')}:{k:'mut',t:'—'}]; r.s[k]=a.join(', '); };
    lst('papeis',pp); lst('canais',ml(V.canais)); lst('grupos',gg); lst('linhas',ml(V.linhas)); lst('gar',ml(V.gar)); lst('veic',ml(V.veic)); lst('ops',ml(V.ops));
    const cc=ml(V.canais), na=(c)=>cc.indexOf(c)<0?[{k:'mut',t:'não autorizado'}]:[];
    r.p.cont=[V.contato?{k:'txt',t:V.contato}:{k:'mut',t:'—'}]; r.s.cont=V.contato||''; r.p.whats=V.whats?[{k:'txt',t:V.whats}].concat(na('WhatsApp')):[{k:'mut',t:'—'}]; r.s.whats=V.whats||'';
    r.p.email=V.email?[{k:'txt',t:V.email}].concat(na('E-mail')):(forn&&hom&&!susp?[chipc('Sem e-mail','red')]:[{k:'mut',t:'—'}]); r.s.email=V.email||(forn&&hom&&!susp?'Sem e-mail':'');
    const S=sitPapeis(V,pp,fp); M.papel=S.map(x=>({id:x.t,l:x.t})); r.p.papel=S.length?S.map(x=>chipc(x.t,x.c)):[{k:'mut',t:'—'}]; r.s.papel=S.map(x=>x.t).join(', ');
    r.p.homol=[chipc(susp?'Suspenso':(hom?'Sim':'Não'),hom&&!susp?'green':'gray')].concat(!susp&&!hom?[{k:'mut',t:'não recebe cotação'}]:[]); r.s.homol=susp?'Suspenso':(hom?'Sim':'Não');
    const lim=Number(V.lim)||0; r.p.lim=[lim?{k:'txt',t:nf(lim,0)}:{k:'mut',t:'—'}]; r.s.lim=lim?nf(lim,0):'';
    r.p.limv=[V.limv?(V.limv<HOJE?{k:'cn',t:br(V.limv),c:'red'}:{k:'txt',t:br(V.limv)}):{k:'mut',t:'—'}]; r.s.limv=V.limv?br(V.limv):'';
    r.p.rntrc=[V.rntrc?{k:'txt',t:V.rntrc}:{k:'mut',t:'—'}]; r.s.rntrc=V.rntrc||'';
    const mt=V.sit==='Suspenso'?(V.motivo||''):''; r.p.motivo=[mt?{k:'txt',t:mt}:{k:'mut',t:'—'}]; r.s.motivo=mt; });
  // mestre (papel) → busca da tela; os grupos de insumo são outra lista
  cmdPasse(rows,OCULTO,r=>!fp||ml(r.v.papeis).indexOf(fp)>=0);
  cmdPasse(rows,'cadb_g_forn',r=>cmdCasa(c5hay(r.v),q));
  const ok=cotaveis(rows);
  GR('g_cob').rows=GRUPOS_.map(g=>{ const fs=ok.filter(r=>ml(r.v.grupos).indexOf(g)>=0); const n=fs.length; const ni=(ITG[g]||[]).length;
    const st=n===0?['Sem fornecedor',sitX('Sem fornecedor','yellow')]:(n===1?['Sem concorrência',[chipc('Sem concorrência','yellow')]]:['Com concorrência',sitOk('Com concorrência')]);
    return {id:'c_'+g,v:{g:g,n:n,ni:ni},s:{sit:st[0]},p:{g:[{k:'b',t:g}],sit:st[1]},o:null}; });
  cmdPasse(GR('g_cob').rows,'cadb_g_cob',r=>cmdCasa([r.v.g].concat(ITG[r.v.g]||[]).join(' '),q));
  c5cfg(self); }   // o endereço é lido depois que os grupos de insumo existem (#grp=Fungicidas abre o painel do grupo)
// "Abrir e ativar papel": abre o parceiro já cadastrado com os papéis marcados no cadastro novo (nada é duplicado)
function abrirAtivar(self,id){ const sp=GR('g_forn'); const cur=g2st(self,'g_forn').fm; const r=g2find(RW(self,'g_forn'),id); if(!r) return;
  const draft={}; sp.edit.fields.forEach(f=>{ const x=r.v[f.k]; draft[f.k]=(x!==undefined&&x!==null&&x!=='')?(f.t==='num'?String(x).replace('.',','):String(x)):''; });
  const orig=Object.assign({},draft); const tem=ml(draft.papeis); const novos=(cur?ml(cur.draft.papeis):[]).filter(p=>tem.indexOf(p)<0);
  const pp=ordena(tem.concat(novos)); Object.assign(draft,{papeis:pp.join('; ')},rpFlags(pp));
  g2set(self,'g_forn',{fm:{rid:id,draft:draft,orig:orig,errs:{},warn:false,ro:false,isNew:false,mode:'form',vc:true},fl:null,fmc:null});
  self.setState({g2toast:novos.length?(r.v.nome+': papel '+novos.join(', ')+' marcado. Confira a seção e salve.'):(r.v.nome+' aberto: marque o novo papel e salve.')}); }
// regras do cadastro (além das do motor): documento único, canais, homologação, limite, RNTRC
function regras(self,d,fm){ const e={}; const dg=dig(d.cnpj); const cc=ml(d.canais); const pp=ml(d.papeis); const tem=p=>pp.indexOf(p)>=0;
  if(d.cnpj&&dg.length!==11&&dg.length!==14) e.cnpj='Informe CPF (11 dígitos) ou CNPJ (14 dígitos).';
  else if(d.cnpj&&!docOk(dg)) e.cnpj=(dg.length===11?'CPF':'CNPJ')+' inválido: os dígitos verificadores não conferem.';
  else { const dup=dupDoc(self,d.cnpj,fm.rid); if(dup) e.cnpj=(dg.length===11?'CPF':'CNPJ')+' já cadastrado em '+dup.v.nome+'.'; }
  if(cc.indexOf('WhatsApp')>=0&&!String(d.whats||'').trim()) e.whats='Informe o WhatsApp ou desmarque o canal.';
  if(tem('Fornecedor')&&d.homol==='Sim'){
    if(!ml(d.grupos).length) e.grupos='Marque ao menos um grupo para homologar.';
    if(!String(d.contato||'').trim()) e.contato='Informe o nome do contato para homologar.';
    if(!String(d.email||'').trim()) e.email='Informe o e-mail: a cotação é enviada por ele.';
    if(cc.indexOf('E-mail')<0) e.canais='Marque E-mail: sem autorização o fornecedor não recebe cotação.'; }
  if(cc.indexOf('E-mail')>=0&&!String(d.email||'').trim()&&!e.email) e.email='Informe o e-mail ou desmarque o canal.';
  if(tem('Cliente')&&g2num(d.lim)>0&&!d.limv) e.limv='Informe a validade da análise de crédito.';
  if(tem('Transportador')&&String(d.rntrc||'').trim()&&dig(d.rntrc).length!==8) e.rntrc='O RNTRC tem 8 dígitos.';
  return e; }
function EXTRAVALS(self,v){ const sp=GR('g_forn'); const F=v.g_forn_F; v.cd5_susp=false; v.cd5_reat=false; const rows=RW(self,'g_forn'); const sel=cmdSel(self); const fp=c5papel(sel); const q=self.state.mx_q||''; const larga=cadLarga();
  // ---- mestre: Todos · os papéis · Grupos de insumo ----
  const its=PSLUG.map(([sl,pap,rot])=>{ const n=rows.filter(r=>ml(r.v.papeis).indexOf(pap)>=0).length; const p=c5pends(self,pap).length; return {id:sl,t:rot,n:String(n),sub:'',res:p?p+' a resolver':'Em dia',cor:p?'yellow':'green'}; })
    .filter(x=>!q||x.id===sel||rows.some(r=>ml(r.v.papeis).indexOf(c5papel(x.id))>=0&&cmdCasa(c5hay(r.v),q)));
  const semG=GR('g_cob').rows.filter(x=>x.v.n===0).length; its.push({tit:true,t:'Cotação'}); its.push({id:C5G,t:'Grupos de insumo',n:String(GRUPOS_.length),sub:'quem recebe a cotação de cada grupo',res:semG?semG+' sem fornecedor':'Em dia',cor:semG?'yellow':'green'});
  cadMestreVals(self,v,{todos:{t:'Todos os parceiros',sub:rows.length+' parceiros'},itens:its,sel:sel,inatN:0,escolhe:id=>cmdEscolhe(self,id)});
  const rs=[]; if(q&&!larga){ rows.filter(r=>cmdCasa(c5hay(r.v),q)).forEach(r=>rs.push({t:r.v.nome,sub:'Parceiro · '+ml(r.v.papeis).join(', '),go:()=>cmdAbre(self,'g_forn',r.id,'')}));
    GR('g_cob').rows.filter(r=>cmdCasa([r.v.g].concat(ITG[r.v.g]||[]).join(' '),q)).forEach(r=>rs.push({t:r.v.g,sub:'Grupo de insumo · '+r.v.n+' fornecedores',go:()=>cmdAbre(self,'g_cob',r.id,C5G)})); }
  cadResVals(v,rs);
  // ---- detalhe ----
  const av=cmdAviso(self,'Ver todos os parceiros'); v.cd5_forn_on=sel!==C5G; v.cd5_cob_on=sel===C5G;
  if(sel===C5G){ const sg=GR('g_cob').rows.filter(x=>x.v.n===0).map(x=>x.v.g);
    cadDetVals(self,v,Object.assign({t:'Grupos de insumo',sub:'Consulta: a fonte do grupo é o CD-06 (Produtos, unidades e locais); a cotação vai por e-mail a fornecedores homologados',
      chip:sg.length?{t:sg.length+' sem fornecedor',c:'yellow'}:{t:'Em dia',c:'green'},prox:sg.length?{cor:'yellow',t:lista(sg)+(sg.length>1?' não têm':' não tem')+' fornecedor que receba a cotação.',quem:'Homologue um fornecedor no painel dele (Editar parceiro).',
        lks:[{t:'Abrir fornecedores',go:()=>cmdEscolhe(self,'fornecedor')}]}:{cor:'green',t:'Em dia: todo grupo tem fornecedor que recebe a cotação.'},lks:[{t:'Abrir grupos nos Produtos',h:'CD-06.dc.html'}],volta:'Papéis',voltar:()=>cmdVolta(self)},av)); }
  else { const ps=c5pends(self,fp); const n=rows.filter(r=>!fp||ml(r.v.papeis).indexOf(fp)>=0).length; const rot=fp?(PSLUG.find(x=>x[1]===fp)||[])[2]:'Todos os parceiros';
    const sub={'Fornecedor':'recebem cotação só se homologados, com e-mail autorizado','Cliente':'limite e validade da análise de crédito por cliente','Parceiro de crédito':'linhas e garantias aceitas',
      'Transportador':'RNTRC e veículos','Prestador':'operações que presta'}[fp]||'um cadastro por CPF ou CNPJ, com os papéis marcados';
    cadDetVals(self,v,Object.assign({t:rot,sub:n+(n===1?' parceiro':' parceiros')+' · '+sub,chip:ps.length?{t:ps.length+' a resolver',c:'yellow'}:{t:'Em dia',c:'green'},prox:c5prox(self,ps,'Em dia: papéis sem pendência.'),volta:'Papéis',voltar:()=>cmdVolta(self)},av)); }
  // "+ Criar parceiro": CPF/CNPJ primeiro, papel herdado; com Grupos de insumo o cabeçalho fica sem verde (a fonte do grupo é o CD-06, R15)
  v.cab_criar_on=sel!==C5G; v.cab_criarT='+ Criar parceiro';
  v.cd5_criar=()=>{ if(sel===C5G) return; g2set(self,'g_forn',{fm:null}); const pp=fp?[fp]:[]; g2new(self,sp,{draft:Object.assign({papeis:pp.join('; ')},rpFlags(pp))});
    setTimeout(()=>{ try{ const x=document.getElementById('fx_g_forn_cnpj'); if(x) x.focus(); }catch(z){} },90); };
  const semGL=GR('g_cob').rows.filter(x=>x.v.n===0).length; const venc=rows.filter(r=>r.v.sit!=='Suspenso'&&ml(r.v.papeis).indexOf('Cliente')>=0&&Number(r.v.lim)&&r.v.limv&&r.v.limv<HOJE).length;
  const pend=[semGL?semGL+(semGL>1?' grupos':' grupo')+' sem fornecedor':'',venc?venc+(venc>1?' limites vencidos':' limite vencido'):''].filter(Boolean);
  cadEstado(v,'cd5e',pend.join(' · ')||'Cadastro em dia',pend.length?'yellow':'green');
  const ct=cmdConta(self,'g_forn',rows); v.cd5_conta=ct.n+' de '+ct.tot; const cg=cmdConta(self,'g_cob',GR('g_cob').rows); v.cd5_contaG=cg.n+' de '+cg.tot;
  const vz=sel===C5G?(!cg.n?{t:'Nenhum grupo de insumo encontrado para “'+q+'”.'}:null):(!ct.n?(q?{t:'Nenhum parceiro encontrado para “'+q+'”. Para cadastrar, use + Criar parceiro, no topo.'}:{t:'Nenhum parceiro com este papel. Crie em + Criar parceiro, no topo.'}):null);
  cadVazioSe(self,v,'cd5_v',vz,['g_forn','g_cob']);
  // menu do filtro de coluna: só os valores e as contagens das linhas do papel escolhido
  const fc=sp.cols.find(c=>c.k===g2st(self,'g_forn').fmc), FM=v.g_forn_fm;
  if(fc&&FM&&FM.open){ const cnt={}; rows.forEach(r=>{ if(r.sh===OCULTO) return; g2fkeys(r,fc).forEach(t=>{ cnt[t]=(cnt[t]||0)+1; }); });
    FM.vals=FM.vals.filter(x=>cnt[x.t]).map(x=>Object.assign(x,{n:cnt[x.t]})); }
  if(F&&F.open&&F.isRec&&F.edit){ const fm=g2st(self,'g_forn').fm; const d=fm.draft;
    if(fm.rid){ const r=g2find(rows,fm.rid); if(r) F.title='Parceiro · '+r.v.nome; }
    if(fm.orig.sit==='Suspenso') F.sub='Suspenso: fora de cotação, oferta e crédito; o histórico continua.';
    (F.fields||[]).forEach(f=>{ const k=f.fid.slice('fx_g_forn_'.length);
      if(SECOES[k]){ f.hasSec=true; f.sec=SECOES[k]; }
      if((k==='contato'||k==='email')&&d.rp_forn!=='Sim') f.hasHelp=false;
      if(k==='papeis') f.mopts.forEach(mo=>{ mo.tog=()=>{ const cur=g2st(self,'g_forn').fm; if(!cur) return; const a=ml(cur.draft.papeis); const i=a.indexOf(mo.t);
          if(i>=0) a.splice(i,1); else a.push(mo.t); const pp=ordena(a); draftSet(self,'g_forn',Object.assign({papeis:pp.join('; ')},rpFlags(pp))); }; });
      if(k==='cnpj'&&!fm.isNew){ f.help='Identifica o parceiro; não muda depois do cadastro.'; f.hasHelp=true; }
      if(k==='cnpj'&&fm.isNew){ const dup=dupDoc(self,d.cnpj,null);
        if(dup){ f.hasDup=true; f.dupT='Já cadastrado: '+dup.v.nome+' ('+ml(dup.v.papeis).join(', ')+')'; f.dupGo=()=>abrirAtivar(self,dup.id); } } });
    if(!fm.isNew){ v.cd5_susp=d.sit!=='Suspenso'; v.cd5_reat=d.sit==='Suspenso'; v.cd5_reatT=fm.orig.sit==='Suspenso'?'Reativar parceiro':'Manter ativo'; }
    F.save=()=>{ const cur=g2st(self,'g_forn').fm; if(!cur) return; const e=Object.assign(basic(sp,cur),regras(self,cur.draft,cur));
      if(Object.keys(e).length){ g2set(self,'g_forn',{fm:Object.assign({},cur,{errs:e,warn:false})}); return; }
      self._cd5d=Object.assign({},cur.draft); g2save(self,sp); }; }
  v.cd5_suspender=()=>draftSet(self,'g_forn',{sit:'Suspenso'});
  v.cd5_reativar=()=>draftSet(self,'g_forn',{sit:'Ativo'});
  self.g2after=(gid,rows2,r,isNew)=>{ if(gid!=='g_forn'||!r) return; const d=self._cd5d||{}; self._cd5d=null;
    const antes=r.v.sit||'Ativo'; r.v.sit=d.sit||'Ativo'; if(r.v.sit!=='Suspenso'){ r.v.motivo=''; if(r.s) delete r.s.motivo; }
    const pp=ml(r.v.papeis), forn=pp.indexOf('Fornecedor')>=0, hom=r.v.homol==='Sim'; let msg;
    if(r.v.sit==='Suspenso'&&antes!=='Suspenso') msg='Suspenso: '+r.v.nome+' sai de cotação, oferta e crédito; o histórico continua.';
    else if(r.v.sit!=='Suspenso'&&antes==='Suspenso') msg='Reativado: '+r.v.nome+' volta a cotação, oferta e crédito conforme os papéis.';
    else if(isNew) msg='Criado: '+r.v.nome+' · '+pp.join(', ')+'.'+(forn&&!hom?' Homologue por grupo para receber cotação.':'');
    else if(forn) msg=hom?('Salvo: '+r.v.nome+' recebe cotação de '+ml(r.v.grupos).join(', ')+'.'):('Salvo: '+r.v.nome+' não recebe cotação enquanto não for homologado.');
    else msg='Salvo: '+r.v.nome+'.';
    self.setState({g2toast:msg}); }; }
function lista(a){ return a.length<2?(a[0]||''):a.slice(0,-1).join(', ')+' e '+a[a.length-1]; }
'''
