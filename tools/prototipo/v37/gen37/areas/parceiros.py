# -*- coding: utf-8 -*-
"""Portal do parceiro (módulo OCULTO do menu, preservado) — padrão G2 de 25/09/2026.
PT-01 Início · PT-02 Cotações (+PT-02det proposta) · PT-03 Ofertas · PT-04 Crédito (+PT-04det dossiê) ·
PT-05 Negócios (+PT-05det negócio) · PT-06 Indicadores · PT-07 Perfil (caps. 46, 48–50, 57–59).

Regras (inalteradas): o parceiro vê SÓ o dossiê da oportunidade concedida (consentimento RN-039), com finalidade e prazo;
versões submetidas são preservadas; concorrentes nunca aparecem; motivo de perda é agregado; aprovação condicional de
crédito não equivale a desembolso; credenciamento (PT-07) alimenta a correspondência categoria/cultura/região (57.4.2).
Padrão: toda tabela é grid(); clicar na linha abre o painel lateral pela direita — formulário tipado nos registros que o
parceiro edita (proposta, condições, esclarecimento, previsão de carga, proposta de compra, perfil, preferências, usuários),
consulta nos registros concedidos/históricos e origem nos indicadores calculados. Módulo não sequencial: sem faixa de etapas.

Personas: Fertisul (F01 de dados2 · fornecedor) → PT-01, PT-02, PT-05, PT-06, PT-07; Frutas Real (comprador) → PT-03;
Banco Terra (credor do CRE-0102) → PT-04.

observacoes (dados locais coerentes com dados/dados2; declarados):
- A cotação aberta da Fertisul passa a ser a SOL-2026-07 · Fertilizantes (dados2: SOL_INICIAL + sol_itens() + PROPOSTAS F01
  fator 0,97 · 12 d · CIF · 28 dias · validade 30/09) — a mesma que Planejar safra envia e que SU-04 compara (3/3 respostas).
  Prazo de revisão 26/09 18:00 e acesso ao dossiê até 08/10 são constantes locais.
- O negócio em execução passa a ser CT-2026-11 / PC-088 (KCl 60 %, dados2 + suprimentos.py): 140 t contratadas, 100 t
  liberadas, cargas 1–2 (60 t, NF 4501, 50 t aptas + 10 t em quarentena, laudo 27/09), carga 3 (40 t, 02/10), carga 4 proposta.
  A cotação de origem COT-097 é constante local. O antigo PC-093 (MAP) saiu: PC-093 é o diesel em Suprimentos.
- Funil de 12 meses: 14 convites → 12 propostas (1 em análise: SOL-2026-07) → 3 selecionadas (2 concluídas R$ 120 mil +
  CT-2026-11 R$ 326,2 mil) → 8 não selecionadas. COT-108 (superfosfato, perdida) segue como exemplo de perda.
- Comprador: OF-103/RT-0112/OF-101/PV-032/OF-102/PV-031 espelham comercial.py (PV-031 “a confirmar”).
  OF-103 segue dados.CANON['OF103']: enviada à Frutas Real e reservada pela RT-0112. PC-088 segue dados.CANON['PC088']
  (100 t × R$ 2,33/kg = R$ 233.000 · título único, sem barter · 60 t recebidas (50 aptas + 10 quarentena) · 40 t a entregar).
- Credor: CRE-0102 de dados.CRE (R$ 850 mil · R$ 300 mil liberados · certidão pendente), CRE-0089 expirado (local)."""
import json
from engine import (grid,section,kpis,chip,btn,tag,icon,esc,msgbtn,drawer_button,stepper,toolrow,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,BTN_ST,EXTRAJS)
import engine as E
from ui37 import shell37, continuity, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
CTX_F=('Portal do parceiro','Fertisul',None);    PERFIL_F='Fertisul · Fornecedor'
CTX_C=('Portal do parceiro','Frutas Real',None); PERFIL_C='Frutas Real · Comprador'
CTX_B=('Portal do parceiro','Banco Terra',None); PERFIL_B='Banco Terra · Credor'
SIM=' (simulado · nenhuma mensagem real enviada)'

def nf(v,d=0):
    s=f'{v:,.{d}f}'; return s.replace(',','X').replace('.',',').replace('X','.')
def rs(v,d=2): return 'R$ '+nf(v,d)

# ---- Fertisul = F01 de dados2 ----
FERT=next(f for f in D2.FORNECEDORES if f['id']=='F01')
PROP=next(p for p in D2.PROPOSTAS['Fertilizantes'] if p['f']=='F01')
SOL=D2.SOL_INICIAL
SOL_IT=[(n,o) for n,o in D2.sol_itens().items() if o['grupo']=='Fertilizantes']
SOL_KG=sum(o['qtd'] for _,o in SOL_IT)
SOL_VAL=sum(o['qtd']*round(o['preco_ref']*PROP['fator'],3) for _,o in SOL_IT)
COT=dict(id=SOL['id']+' · Fertilizantes',sol=SOL['id'],itens=len(SOL_IT),t=nf(SOL_KG/1000,2)+' t',
         revisa='26/09 18:00',acesso='08/10',entrega='Galpão 2 · Faz. Santa Rita · até 10/10',enviada=SOL['enviada'])
PC=next(p for p in D2.PEDIDOS if p['id']=='PC-088')
NF1=next(r for r in D2.RECEBIMENTOS if r['pedido']=='PC-088')
KCL_T=PC['preco']*1000                                   # R$ 2.330/t
CT=dict(id='CT-2026-11',cot='COT-097',contratado=140,liberado=PC['qtd']//1000,recebido=PC['recebido']//1000,
        apto=PC['apto']//1000,quar=PC['quarentena']//1000,carga3=PC['a_entregar']//1000,prev3='02/10',laudo='27/09')
PC_VAL=PC['qtd']*PC['preco']                             # R$ 233.000 (CANON PC088)
CT_VAL=CT['contratado']*KCL_T                            # R$ 326.200
PERDIDA=dict(id='COT-108',neg='NEG-2088',item='Superfosfato simples',vol='60 t')
FUNIL=dict(convites=14,propostas=12,analise=1,ganhos=3,concl=2,concl_valor=120000,prop_valor=2940000)
FUNIL['perdidos']=FUNIL['propostas']-FUNIL['ganhos']-FUNIL['analise']
FUNIL['ganhos_valor']=FUNIL['concl_valor']+CT_VAL
def pct(a,b): return f'{round(a/b*100):.0f}%'
# ---- comprador (Frutas Real) — espelha comercial.py ----
OFERTA=dict(id='OF-103',prod='Mamão Formosa · classe A',kg=D.DISPON['atendivel_kg'],janela='05/10–11/10',
            local='CIF região Sudeste',preco=3.05,cond='28 d',validade='30/09')
RESERVA=dict(id='RT-0112',kg=2000,vence='24/09 18:00')
# ---- credor (Banco Terra) — espelha gestao.py (GE-08) e dados.CRE ----
CRE_TAXA='14,2% a.a.'; CRE_DOC='certidão do imóvel atualizada'; CRE_ACESSO='31/12/2026'
CRE_EXP=dict(id='CRE-0089',finalidade='custeio 2025/26',encerrado='12/08')

# ---------------- helpers ----------------
def plain(parts): return ' '.join(p['t'] for p in parts if p.get('k')!='br').strip()
def R(id,ro=False,o=None,v=None,**cells):
    """linha G2: texto/número → v (editável/ordenável); lista de partes → p (exibição rica)."""
    r=dict(id=id,v=dict(v or {}),s={},p={})
    for k,x in cells.items():
        if isinstance(x,list): r['p'][k]=x; r['s'][k]=plain(x)
        else: r['v'][k]=x
    if ro: r['ro']=True
    if o: r['o']=[dict(t=t,h=h) if h else dict(t=t) for t,h in o]
    return r
def C(k,l,**kw): return dict(k=k,l=l,**kw)
def F(k,l,t='txt',**kw):
    d=dict(k=k,l=l,t=t)
    if 'default' in kw: d['def']=kw.pop('default')
    d.update(kw); return d
def two(a,b): return [Pt.b(a),Pt.br(),Pt.mut(b)]
def ch(t,c='gray'): return [Pt.chip(t,c)]
def ic(html,name,title=None):
    """ação secundária com ícone + rótulo + title."""
    t=f' title="{esc(title)}"' if title else ''
    svg=icon(name,14)
    if html.startswith('<a '): return html.replace('<a ',f'<a{t} ',1).replace('">',f'">{svg}',1).replace('display: inline-block;','display: inline-flex; align-items: center; gap: 6px;',1)
    return html.replace('<button ',f'<button{t} ',1).replace('style="','style="display: inline-flex; align-items: center; gap: 6px; ',1).replace('">',f'">{svg}',1)
def acoes(*bs,top=0):
    return (f'<div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;{" margin-top: %dpx;" % top if top else ""}">'+''.join(bs)+'</div>')
def nota(t): return f'<div style="font-size: 12.5px; color: {MUTED}; line-height: 1.5; margin-top: 10px;">{t}</div>'
def drawer_part(label,d):
    """registra um painel (drawer) e devolve a parte de linha que o abre."""
    drawer_button(label,d); return {'k':'act','t':label,'fn':E.DRAWN[label]+'_open'}

class JS:
    """JS da tela: ações que executam uma vez (recibo idempotente) + ganchos da grade."""
    def __init__(s): s.parts=[]; s.hooks=[]
    def once(s,key,label,first,again,primary=False,name=None,title=None):
        s.parts.append(f"v.ok_{key}=()=>{{ const d=self.state.done||{{}}; if(d.{key}){{ self.setState({{g2toast:{json.dumps(again,ensure_ascii=False)}}}); return; }} "
                       f"self.setState({{done:Object.assign({{}},d,{{{key}:true}}),g2toast:{json.dumps(first,ensure_ascii=False)}}}); }};")
        b=f'<button type="button" onClick="{H("ok_"+key)}" style="{BTN_ST(primary,True)}">{esc(label)}</button>'
        return ic(b,name,title) if name else b
    def after(s,code): s.hooks.append(code)
    def flush(s,extra=''):
        hook=('self.g2after=(gid,rows,r)=>{ '+' '.join(s.hooks)+' };') if s.hooks else ''
        EXTRAJS[0]=('function _set(self,gid,rows){ g2set(self,gid,{rows}); }\n'+extra+
                    '\nfunction EXTRAVALS(self,v){ '+hook+' '+' '.join(s.parts)+(' _xv(self,v);' if 'function _xv' in extra else '')+' }')

def start(fname,h):
    E._reset_screen(fname); HEIGHTS37[fname]=h

def build():
    pt01(); pt02(); pt02det(); pt03(); pt04(); pt04det(); pt05(); pt05det(); pt06(); pt07()

# ============ PT-01 · Início do portal (Fertisul) ============
def pt01():
    start('PT-01.dc.html',860)
    op=grid([C('op','Oportunidade',w=260),C('acesso','Convite e acesso',w=240),C('prazo','Prazo'),C('sit','Situação',w=230),C('acao','Abrir')],[
        R('o1',op=two(COT['id'],f"{COT['itens']} itens · {COT['t']}"),
          acesso=[Pt.txt('convite de '+COT['enviada'][:5]),Pt.br(),Pt.mut(f"só esta cotação · acesso até {COT['acesso']}")],
          prazo=ch('Revisa até '+COT['revisa'],'yellow'),sit=ch('v1 submetida · esclarecimento aberto','yellow'),acao=[Pt.cta('Abrir proposta','PT-02det.dc.html',True)],
          o=[(f"Convite enviado por {SOL['por']} em {SOL['enviada']} · só a homologados do grupo Fertilizantes",None),
             (f"Finalidade: cotação da {SOL['id']} · acesso ao dossiê até {COT['acesso']}",None),('Abrir a proposta','PT-02det.dc.html')]),
        R('o2',op=two(f"{CT['id']} · PC-088",f"KCl 60% · {CT['liberado']} t liberadas de {CT['contratado']} t"),
          acesso=[Pt.txt('negócio próprio'),Pt.br(),Pt.mut('mensagens vinculadas ao pedido')],
          prazo=ch(f"Carga 3 · {CT['prev3']}",'green'),sit=ch('NF-e da carga 3 a enviar','yellow'),acao=[Pt.cta('Abrir negócio','PT-05det.dc.html')],
          o=[(f"Pedido PC-088 confirmado · {CT['recebido']} t recebidas (NF 4501) · {CT['carga3']} t a entregar em {CT['prev3']}",None),('Abrir o negócio','PT-05det.dc.html')]),
        R('o3',op=two(PERDIDA['id'],f"{PERDIDA['item']} · {PERDIDA['vol']}"),
          acesso=[Pt.mut('acesso encerrado com a cotação')],prazo=[Pt.mut('—')],sit=ch('Não selecionada','gray'),acao=[Pt.link('Ver negócios','PT-05.dc.html')],
          o=[('Motivo agregado: condição comercial — não revela proposta concorrente',None)]),
      ],edit=dict(m='ro',title='Oportunidade'),search=False,total=False,gid='g_op')
    av=grid([C('aviso','Aviso',w=460),C('reg','Registro'),C('abrir','Abrir')],[
        R('a1',aviso='Comprador pergunta: “o frete CIF até o Galpão 2 vale para os 4 itens?”',reg=COT['sol'],abrir=[Pt.cta('Responder esclarecimento','PT-02det.dc.html',True)]),
        R('a2',aviso='Comprador pede a placa do caminhão da carga 3',reg='PC-088',abrir=[Pt.cta('Abrir negócio','PT-05det.dc.html')]),
        R('a3',aviso=f"Laudo das {CT['quar']} t em quarentena (lote K26-11) vence em {CT['laudo']}",reg='NF 4501',abrir=[Pt.cta('Abrir negócio','PT-05det.dc.html')]),
        R('a4',aviso='Renovação do plano Parceiro Profissional pede seu aceite do novo preço até 30/09',reg='Assinatura',abrir=[Pt.link('Ver assinatura','PT-07.dc.html')]),
      ],edit=dict(m='ro',title='Aviso'),search=False,total=False,gid='g_av')
    corpo=(section('Oportunidades concedidas a você','Abra a oportunidade e responda no prazo; clique na linha para ver a concessão.','',op)
      +section('Avisos','Abra o registro de cada aviso para resolver.','',av,state='yellow')
      +section('Outros papéis no portal','Veja o portal pelos olhos de outros parceiros convidados.','',
        acoes(ic(btn('Abrir oferta · Frutas Real',small=True,href='PT-03.dc.html'),'Vendas','Portal do comprador (demonstração)'),
              ic(btn('Analisar crédito · Banco Terra',small=True,href='PT-04.dc.html'),'cash','Portal do credor (demonstração)')),state='gray'))
    shell37('PT-01','Portal do parceiro',corpo,ctx=CTX_F,perfil=PERFIL_F,
      subtitle='Oportunidades concedidas, tarefas e negócios próprios — só o convite autorizado dá acesso a dados do produtor.',
      status=('Revisa até '+COT['revisa'],'yellow'),
      primary='Responder esclarecimento',primary_href='PT-02det.dc.html',
      footer='Toda oportunidade depende de destinatário autorizado e da política de distribuição (57.4.2); assinatura não é consentimento do produtor (RN-039).')

# ============ PT-02 · Cotações concedidas (Fertisul) ============
def pt02():
    start('PT-02.dc.html',720)
    g=grid([C('cot','Cotação',w=240),C('item','Itens e volume',w=200),C('prazo','Responder até'),C('sit','Proposta e situação',w=230),C('acao','Abrir')],[
        R('c1',cot=two(COT['id'],'Planejar safra · Safra 2026/27'),item=[Pt.txt(f"{COT['itens']} itens · {COT['t']}"),Pt.br(),Pt.mut('entrega até 10/10')],prazo=ch(COT['revisa'],'yellow'),sit=[Pt.chip('Esclarecimento aberto','yellow'),Pt.br(),Pt.mut('v1 submetida')],
          acao=[Pt.cta('Abrir proposta','PT-02det.dc.html',True)],o=[(f"Convite de {COT['enviada']} · acesso até {COT['acesso']}",None),('Abrir a proposta','PT-02det.dc.html')]),
        R('c2',cot=two(CT['cot'],'Suprimentos'),item=[Pt.txt(f"KCl 60% · {CT['contratado']} t"),Pt.br(),Pt.mut('entrega set–out/26')],prazo=[Pt.mut('encerrada 05/09')],
          sit=[Pt.chip(f"Selecionada · {CT['id']}",'green'),Pt.br(),Pt.mut('v2 submetida')],acao=[Pt.cta('Abrir negócio','PT-05det.dc.html')],
          o=[(f"Proposta v2 selecionada · virou contrato {CT['id']} e pedido PC-088",None)]),
        R('c3',cot=two(PERDIDA['id'],'Suprimentos'),item=[Pt.txt(f"{PERDIDA['item']} · {PERDIDA['vol']}"),Pt.br(),Pt.mut('entrega ago/26')],prazo=[Pt.mut('encerrada 20/08')],
          sit=[Pt.chip('Não selecionada','gray'),Pt.br(),Pt.mut('v2 submetida')],
          acao=[Pt.act('Baixar comprovante','Comprovante da v2 (PDF) · motivo agregado da não seleção: condição comercial — sem proposta concorrente nem dado reservado.')]),
      ],edit=dict(m='ro',title='Cotação'),search=False,total=False,gid='g_cot')
    corpo=section('Minhas cotações','Abra a cotação para revisar sua proposta; outros fornecedores nunca aparecem aqui.','',
        g+nota('Cada versão submetida fica preservada — revisar antes do prazo cria nova versão; motivo de não seleção é agregado.'))
    shell37('PT-02','Cotações concedidas',corpo,ctx=CTX_F,perfil=PERFIL_F,
      subtitle='Você responde pelo convite recebido — o dossiê mostra só o que foi concedido, com finalidade e prazo de acesso.',
      status=('1 aberta · revisa até '+COT['revisa'],'yellow'),
      primary='Abrir proposta '+COT['sol'],primary_href='PT-02det.dc.html',
      footer=f"Convite nasce da correspondência categoria/cultura/região do seu perfil (57.4.2); acesso ao dossiê da {COT['sol']} expira em {COT['acesso']}.")

# ---- PT-02det · dossiê + proposta da SOL-2026-07 · Fertilizantes ----
def pt02det():
    fname='PT-02det.dc.html'; start(fname,1370); PARENT37[fname]='PT-02.dc.html'
    dos=grid([C('campo','Campo',w=180),C('valor','Valor',w=420),C('fonte','Fonte',w=260)],[
        R('d1',campo='Itens e volume',valor=f"{COT['itens']} fertilizantes · {nf(SOL_KG,0)} kg",fonte=f"{SOL['id']} · {SOL['origem']}"),
        R('d2',campo='Entrega',valor=COT['entrega'],fonte='local e janela concedidos'),
        R('d3',campo='Frete e pagamento pedidos',valor='CIF até o Galpão 2 · até 30 dias',fonte='condição do comprador'),
        R('d4',campo='Acesso ao dossiê',valor=f"até {COT['acesso']} · só esta cotação",fonte='consentimento do produtor (RN-039)'),
      ],edit=dict(m='ro',title='Dossiê'),search=False,total=False,gid='g_dos')
    it=grid([C('item','Item',w=220),C('qtd','Quantidade',t='num',a='r',u='kg'),C('preco','Preço (R$/kg)',t='num',a='r',d=3),
             C('tot','Total',t='num',a='r',pre='R$ ',d=2,agg='sum')],
        [R(f'i{i}',v=dict(item=n,qtd=o['qtd'],preco=round(o['preco_ref']*PROP['fator'],3),tot=round(o['qtd']*round(o['preco_ref']*PROP['fator'],3),2)))
         for i,(n,o) in enumerate(SOL_IT)],
        edit=dict(m='form',title='Item da proposta',sub='Revise o preço CIF por quilo; o total é recalculado. A v1 submetida fica preservada.',
                  fields=[F('item','Item',ro=True),F('qtd','Quantidade','num',ro=True,u='kg'),F('preco','Preço','num',req=True,min=0.01,max=50,u='R$/kg')],
                  calc=[dict(k='tot',op='mul',a=['qtd','preco'])]),search=False,total=True,gid='g_it')
    cd=grid([C('frete','Frete',w=200),C('pag','Pagamento'),C('prazo','Prazo de entrega',t='num',a='r',u='dias'),C('val','Validade',t='date'),C('obs','Observações',w=260)],[
        R('k1',v=dict(frete='CIF · incluso até o Galpão 2',pag=PROP['pag'],prazo=PROP['prazo'],val='2026-09-30',obs='laudo de garantia acompanha cada NF'))],
        edit=dict(m='form',title='Condições da proposta',sub='Ajuste frete, pagamento, prazo e validade; vale para todos os itens.',
                  fields=[F('frete','Frete','sel',req=True,opts=['CIF · incluso até o Galpão 2','FOB · retirada na unidade']),
                          F('pag','Pagamento','sel',req=True,opts=['28 dias','30 dias','à vista','safra']),
                          F('prazo','Prazo de entrega','num',req=True,min=1,max=60,u='dias',help='Contado do pedido; a entrega precisa chegar até 10/10.'),
                          F('val','Validade da proposta','date',req=True),F('obs','Observações','area')]),search=False,total=False,gid='g_cd')
    esc_=grid([C('perg','Pergunta',w=360),C('de','De · quando'),C('resp','Resposta',w=300),C('sit','Situação')],[
        R('e1',v=dict(perg='O frete CIF até o Galpão 2 vale para os 4 itens?',resp=''),de=two('Comprador','23/09 14:10'),sit=ch('Aguardando sua resposta','yellow')),
        R('e2',ro=True,v=dict(perg='Qual a data necessária do MAP 11-52?',resp='Até 10/10 no Galpão 2, junto com o NPK.'),de=two('Fertisul','23/09 11:05'),sit=ch('Respondida','green')),
      ],edit=dict(m='form',title='Esclarecimento',sub='Responda ao comprador; a resposta fica vinculada à cotação e visível a ele.',
                  fields=[F('perg','Pergunta','area',ro=True),F('resp','Sua resposta','area',req=True)]),search=False,total=False,gid='g_esc')
    js=JS()
    js.after("if(gid==='g_esc' && r){ r.p.sit=[{k:'chip',t:'Respondida',c:'green'}]; r.s.sit='Respondida'; r.ro=true; _set(self,gid,rows); "
             f"self.setState({{g2toast:'Resposta registrada na {COT['sol']} · visível ao comprador'+{json.dumps(SIM)}}}); }}")
    js.after("if((gid==='g_it'||gid==='g_cd') && r){ self.setState({chg:true}); }")
    js.parts.append(r"""const ver=self.state.ver||1, chg=!!self.state.chg;
  v.prim_t='Submeter proposta v'+(ver+1); v.prim_st='"""+BTN_ST(True)+r"""';
  v.prim_fn=()=>{ const s=self.state, vv=s.ver||1; if(!s.chg){ self.setState({g2toast:'Nada mudou desde a v'+vv+': clique num item ou nas condições para revisar — a v'+vv+' submetida continua valendo.'}); return; }
    self.setState({ver:vv+1,chg:false,g2toast:'Proposta v'+(vv+1)+' submetida · comprovante PR-'+(1141+vv)+' · a v'+vv+' fica preservada · pode revisar até """+COT['revisa']+r"""'}); };
  v.vtxt=chg?('Rascunho da v'+(ver+1)+' · não enviado ao comprador'):('v'+ver+' submetida · vale até ser revisada');""")
    comp=js.once('comp','Baixar comprovante','Comprovante da última versão submetida (PDF) · conteúdo, data e hora, sem dados de concorrentes.',
                 'Comprovante já baixado · o mesmo PDF da última versão submetida.',name='doc',title='Baixar o comprovante da versão submetida')
    js.flush()
    corpo=(continuity('Cotações concedidas','Proposta v1 submetida',f"responder esclarecimento · revisar até {COT['revisa']}",'Responder esclarecimento')
      +section('Esclarecimentos','Clique na pergunta pendente para responder ao comprador.','',esc_,state='yellow')
      +section('Itens e preços',f'Clique no item para revisar o preço; o total é recalculado.',[comp],
        f'<div style="font-size: 12.5px; color: {MUTED}; padding: 0 2px 8px;">Situação: <b style="color: {INK};">{H("vtxt")}</b></div>'+it)
      +section('Condições da proposta','Clique na linha para ajustar frete, pagamento, prazo e validade.','',cd)
      +section('Dossiê concedido','Confira só o que o comprador autorizou para esta cotação.','',dos,state='gray'))
    shell37('PT-02',f"Proposta · {COT['id']}",corpo,fname=fname,ctx=CTX_F,perfil=PERFIL_F,
      crumbs_extra=[COT['sol']],
      status=('Revisa até '+COT['revisa'],'yellow'),
      primary_html=f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>',
      footer='Versões submetidas são preservadas; concorrentes e a comparação do comprador ficam ocultos.')

# ============ PT-03 · Ofertas ao comprador (Frutas Real) ============
def pt03():
    start('PT-03.dc.html',940)
    of=grid([C('of','Oferta',w=120),C('prod','Produto e padrão',w=200),C('vol','Volume e janela'),C('preco','Preço, condição e local',w=240),
             C('val','Validade'),C('sit','Situação',w=220),C('acao','Ação')],[
        R('f1',of=[Pt.b(OFERTA['id'])],prod=OFERTA['prod'],vol=f"{nf(OFERTA['kg'])} kg · {OFERTA['janela']}",preco=[Pt.txt(f"R$ {nf(OFERTA['preco'],2)}/kg · {OFERTA['cond']}"),Pt.br(),Pt.mut(OFERTA['local'])],val=OFERTA['validade'],sit=[Pt.chip(f"Enviada · reservada pela {RESERVA['id']}",'yellow'),Pt.br(),Pt.mut(f"reserva vence {RESERVA['vence']}")],acao=[Pt.mut('proposta abaixo')],
          o=[(f"{OFERTA['id']} enviada a você (Frutas Real) · reservada pela {RESERVA['id']}",None),('Disponível publicado da semana 05/10 · nunca negativo',None),(f"Sua reserva {RESERVA['id']} já está deduzida",None)]),
        R('f2',of=[Pt.b('OF-101 · v1')],prod='Mamão Formosa · classe B',vol='1,8 t · 28/09–04/10',preco=[Pt.txt('R$ 2,10/kg · 21 d'),Pt.br(),Pt.mut('FOB fazenda')],val='26/09',
          sit=ch('Aceita · aguarda produtor','yellow'),
          acao=[Pt.act('Acompanhar negociação','OF-101 · sua aceitação da v1 foi registrada · pedido PV-032 aguarda confirmação do produtor — sem esse aceite nada vira contrato.')]),
        R('f3',of=[Pt.b('OF-102 · v2')],prod='Mamão Formosa · classe A',vol='10,0 t · 28/09–04/10',preco=[Pt.txt('R$ 3,05/kg · 28 d'),Pt.br(),Pt.mut('CIF Vitória/ES')],val='24/09',
          sit=ch('Virou PV-031 · a confirmar','yellow'),acao=[Pt.mut('—')],o=[('Pedido PV-031 aguarda confirmação do produtor',None)]),
      ],edit=dict(m='ro',title='Oferta'),search=False,total=False,gid='g_of')
    rv=grid([C('res','Reserva'),C('tipo','Tipo'),C('qtd','Quantidade',t='num',a='r',u='kg'),C('venc','Vencimento'),C('est','Estado'),C('efe','Efeito',w=420)],[
        R('r1',res=[Pt.b(RESERVA['id'])],tipo=[Pt.tag('Reserva temporária')],v=dict(qtd=RESERVA['kg'],venc=RESERVA['vence']),est=ch('Aguardando proposta','yellow'),
          efe='já deduzida do publicado — virar pedido não deduz de novo; sem proposta até o vencimento, expira e o saldo volta uma única vez')],
        edit=dict(m='ro',title='Reserva'),search=False,total=False,gid='g_rv')
    pp=grid([C('vol','Volume',t='num',a='r',u='kg'),C('jan','Janela de entrega'),C('preco','Preço proposto',t='num',a='r',pre='R$ ',d=2),C('local','Local de entrega'),C('obs','Observações',w=280)],[
        R('p1',v=dict(vol=RESERVA['kg'],jan=OFERTA['janela'],preco=OFERTA['preco'],local='CIF Vitória/ES',obs='caixas padrão · caminhão refrigerado'))],
        edit=dict(m='form',title='Proposta de compra · '+OFERTA['id'],sub='Ajuste volume, janela, preço e local. Enviar gera intenção de pedido, não venda irrevogável.',
                  fields=[F('vol','Volume','num',req=True,min=100,max=OFERTA['kg'],u='kg',help=f"Até {nf(OFERTA['kg'])} kg publicados; a reserva cobre {nf(RESERVA['kg'])} kg."),
                          F('jan','Janela de entrega','sel',req=True,opts=['05/10–11/10','05/10–08/10','08/10–11/10']),
                          F('preco','Preço proposto','num',req=True,min=0.5,max=20,u='R$/kg'),
                          F('local','Local de entrega','sel',req=True,opts=['CIF Vitória/ES','CIF região Sudeste','FOB fazenda']),F('obs','Observações','area')]),
        search=False,total=False,gid='g_pp')
    js=JS()
    js.after("if(gid==='g_pp' && r){ const d=Object.assign({},self.state.done||{}); if(d.env){ delete d.env; self.setState({done:d,g2toast:'Proposta alterada · envie de novo para valer (a enviada fica no histórico)'}); } }")
    env=js.once('env','Enviar proposta',f"Proposta enviada como intenção de pedido · reserva {RESERVA['id']} mantida até {RESERVA['vence']} e convertida sem nova dedução se o produtor aceitar — sem aceite das partes, nada vira contrato.",
                f"Proposta já enviada · recibo PC-7781 · nada foi duplicado; altere a linha para enviar nova versão.",primary=True)
    aj=ic(drawer_button('Pedir ajuste da oferta',dict(title='Pedir ajuste da oferta',sub='vai ao produtor como contraproposta vinculada à '+OFERTA['id'],
            fields=[('O que ajustar','Janela de entrega'),('Proposta','entregar em 05/10–08/10'),('Motivo','programação de revenda da semana')],
            confirm='Enviar pedido de ajuste',done='Contraproposta enviada · oferta original preservada')),'scale','Pedir ao produtor um ajuste da oferta')
    comp=js.once('comp','Baixar comprovante','Comprovante da proposta (PDF) · conteúdo, data e reserva vinculada.','Comprovante já baixado · mesmo PDF.',name='doc',title='Baixar o comprovante da proposta')
    js.flush()
    corpo=(section('Ofertas autorizadas a você','Confira volume, janela e preço de cada oferta concedida a você.','',of)
      +section('Sua reserva','Envie a proposta antes do vencimento; depois disso a reserva expira.','',rv,state='yellow')
      +section('Minha proposta de compra · '+OFERTA['id'],'Clique na linha para ajustar volume, janela e preço; depois envie.',[aj,comp],
        pp+acoes(env,top=12)))
    shell37('PT-03','Ofertas',corpo,ctx=CTX_C,perfil=PERFIL_C,
      subtitle='Ofertas autorizadas e a sua própria proposta — a carteira comercial interna do produtor fica privada.',
      status=(f"Reserva {RESERVA['id']} vence {RESERVA['vence']}",'yellow'),
      footer='Disponibilidade publicada nunca é negativa; reserva temporária expira por política visível; conversão em pedido mantém dedução única (49.2–49.3, ATP-04/05/07).')

# ============ PT-04 · Crédito (Banco Terra) ============
def pt04():
    start('PT-04.dc.html',820)
    ds=grid([C('dos','Dossiê',w=260),C('fin','Finalidade e blocos concedidos',w=260),C('vig','Vigência do acesso'),C('sit','Situação',w=220),C('acao','Abrir')],[
        R('x1',dos=two(D.CRE['id'],f"custeio 2026/27 · {D.CRE['valor']}"),fin=[Pt.txt('análise e concessão de crédito'),Pt.br(),Pt.mut('produção e áreas · fluxo de caixa')],vig=f'até {CRE_ACESSO}',
          sit=ch('Aprovado · documento pendente','yellow'),acao=[Pt.cta('Abrir dossiê','PT-04det.dc.html',True)],
          o=[(f"Liberado {D.CRE['liberado']} de {D.CRE['valor']} · 2ª parcela aguarda a {CRE_DOC}",None),('Abrir o dossiê','PT-04det.dc.html')]),
        R('x2',dos=two(CRE_EXP['id'],CRE_EXP['finalidade']),fin=[Pt.txt('análise de crédito'),Pt.br(),Pt.mut('fluxo de caixa')],vig=f"expirou {CRE_EXP['encerrado']}",sit=ch('Acesso expirado','gray'),
          acao=[Pt.act('Ver decisão registrada',f"{CRE_EXP['id']}: sua decisão registrada continua disponível · os blocos do dossiê deixaram de ser acessíveis em {CRE_EXP['encerrado']}.")]),
      ],edit=dict(m='ro',title='Dossiê'),search=False,total=False,gid='g_ds')
    hist=grid([C('q','Quando',w=120),C('u','Usuário',w=220),C('b','Bloco acessado'),C('f','Finalidade')],[
        R('h1',q='23/09 09:12',u='Rafael Lima (Banco Terra)',b='fluxo de caixa',f='análise do '+D.CRE['id']),
        R('h2',q='22/09 16:40',u='Rafael Lima (Banco Terra)',b='produção e áreas',f='análise do '+D.CRE['id']),
        R('h3',q='18/09 11:05',u='Carla Souza (Banco Terra)',b='documentos',f='análise do '+D.CRE['id']),
      ],edit=dict(m='ro',title='Acesso'),search=False,total=False,gid='g_hist')
    corpo=(section('Dossiês concedidos a você','Abra o dossiê vigente; acesso expirado mantém só a decisão registrada.','',ds)
      +section('Histórico de acesso','Confira cada acesso registrado — o produtor vê este mesmo histórico.','',hist,state='gray'))
    shell37('PT-04','Crédito',corpo,ctx=CTX_B,perfil=PERFIL_B,
      subtitle='Blocos concedidos com consentimento, finalidade e validade — aprovação pode ser condicional e não marca compra como paga.',
      status=(D.CRE['id']+' · documento condicionante pendente','yellow'),
      primary='Abrir dossiê '+D.CRE['id'],primary_href='PT-04det.dc.html',
      footer='Condição de crédito aceita não equivale a desembolso; o histórico de acesso integra o dossiê (RN-039).')

# ---- PT-04det · dossiê CRE-0102 ----
def pt04det():
    fname='PT-04det.dc.html'; start(fname,1120); PARENT37[fname]='PT-04.dc.html'
    con=grid([C('campo','Campo',w=180),C('valor','Valor',w=560)],[
        R('c1',campo='Finalidade',valor=f"análise e concessão do crédito de custeio {D.CRE['id']} · safra {D.SAFRA}"),
        R('c2',campo='Consentimento',valor='autorizado pela Direção do Grupo Santa Rita · revogável pelo produtor'),
        R('c3',campo='Vigência do acesso',valor=f'até {CRE_ACESSO} · por bloco'),
        R('c4',campo='Uso',valor=[Pt.tag('Exclusivo para esta finalidade · proibido revender ou repassar')]),
      ],edit=dict(m='ro',title='Concessão'),search=False,total=False,gid='g_con')
    blk=grid([C('b','Bloco',w=180),C('c','Conteúdo',w=300),C('f','Fonte',w=220),C('val','Validade'),C('s','Situação',w=220)],[
        R('b1',b=[Pt.b('Produção e áreas')],c='talhões, safras e produtividade dos últimos 3 anos',f='registro de safras do produtor',val=CRE_ACESSO,s=ch('Concedido','green')),
        R('b2',b=[Pt.b('Fluxo de caixa')],c='projeção por trimestre do orçamento V2',f='orçamento aprovado do produtor',val=CRE_ACESSO,s=ch('Concedido','green')),
        R('b3',b=[Pt.b('Compromissos e garantias')],c='contratos, barter e penhores vigentes',f='contratos registrados',val='—',s=ch('Solicitado · aguarda produtor','yellow')),
        R('b4',b=[Pt.b('Documentos')],c=f'matrícula e LCDPR recebidos · {CRE_DOC} pendente',f='envio do produtor',val=CRE_ACESSO,s=ch('Documento pendente','yellow')),
      ],edit=dict(m='ro',title='Bloco do dossiê'),search=False,total=False,gid='g_blk')
    comp=ic(drawer_button('Pedir complemento',dict(title='Pedir complemento ao produtor',sub='o pedido entra no dossiê com prazo',
            fields=[('Bloco','Compromissos e garantias'),('O que falta','autorização do bloco para verificar penhores vigentes'),('Prazo','30/09/2026')],
            confirm='Enviar pedido',done='Pedido de complemento registrado no dossiê')),'doc','Pedir ao produtor um bloco ou documento')
    cond=ic(drawer_button('Registrar condição',dict(title='Condição precedente',sub='a aprovação continua condicional até a condição ser cumprida',
            fields=[('Condição',CRE_DOC),('Prazo','05/10/2026'),('Efeito','bloqueia a 2ª e a 3ª parcelas')],
            confirm='Registrar condição',done='Condição registrada · aprovação segue condicional')),'check','Registrar condição precedente da aprovação')
    cp=ic(drawer_button('Contrapropor condições',dict(title='Contraproposta de condições',sub='gera nova versão — a proposta aceita fica preservada',
            fields=[('Taxa (a.a.)','13,9%'),('Parcelas de liberação','3'),('Garantia','manter penhor de 30% da soja')],
            confirm='Enviar contraproposta',done='Contraproposta v2 enviada · aguarda aceite do produtor')),'scale','Enviar nova versão das condições')
    acomp=ic(msgbtn('Acompanhar liberação',f"Parcela 1 · {D.CRE['liberado']} liberada · parcelas seguintes aguardam a {CRE_DOC} — aceite não equivale a desembolso."),'clock','Ver o andamento das liberações')
    rec=ic(msgbtn('Recusar crédito','Recusa registrada com motivo · os blocos do dossiê deixam de ser acessíveis; histórico de acesso preservado.'),'alert','Recusar o crédito com motivo')
    confer=msgbtn('Conferir documento',f"Ainda não recebido: {CRE_DOC}. O produtor anexa pelo painel dele; quando chegar, a conferência abre aqui e destrava a 2ª parcela. Liberado até agora: {D.CRE['liberado']} de {D.CRE['valor']}.",primary=True)
    corpo=(continuity('Dossiês concedidos',f"Aprovado com condição · {D.CRE['liberado']} liberados",CRE_DOC+' (produtor)','Conferir documento')
      +section('Proposta e decisão',f"Confira o documento condicionante antes de liberar a 2ª parcela.",[acomp],
        stepper([('Proposta de condições','done'),('Aceite do produtor','done'),('Documento condicionante','now'),('Liberações','todo'),('Serviço da dívida','todo')],
                f"Proposta aceita: {D.CRE['valor']} · {CRE_TAXA} · penhor de 30% da soja 26/27 · aprovação condicional: 1ª parcela de {D.CRE['liberado']} liberada; as próximas só liberam com a {CRE_DOC}.")
        +acoes(confer,comp,cond,cp,rec,top=14),state='yellow')
      +section('Blocos do dossiê','Consulte só os blocos concedidos; o que falta aparece como pendente.','',blk)
      +section('Concessão e finalidade','Confira o que o produtor autorizou e até quando.','',con,state='gray'))
    shell37('PT-04','Dossiê · '+D.CRE['id']+' custeio',corpo,fname=fname,ctx=CTX_B,perfil=PERFIL_B,
      crumbs_extra=[D.CRE['id']],status=(D.CRE['estado'],'yellow'),
      footer='Acesso expirável por bloco/finalidade; aprovação condicional não marca compra como paga nem antecipa desembolso.')

# ============ PT-05 · Negócios e documentos (Fertisul) ============
def pt05():
    start('PT-05.dc.html',820)
    ng=grid([C('neg','Negócio',w=240),C('res','Resultado'),C('cond','Condição aceita',w=190),C('doc','Pedido e documento',w=220),C('ent','Entrega',w=200),C('acao','Abrir')],[
        R('n1',neg=two(f"{CT['id']} · PC-088",f"KCl 60% · {CT['liberado']} de {CT['contratado']} t liberadas"),res=ch('Ganhou','green'),
          cond=f"R$ {nf(KCL_T)}/t · CIF · 28 d",doc=[Pt.txt('PC-088 confirmado'),Pt.br(),Pt.mut('NF 4501 · cargas 1–2')],
          ent=[Pt.txt(f"{CT['recebido']} t recebidas"),Pt.br(),Pt.mut(f"carga 3 · {CT['carga3']} t em {CT['prev3']}")],acao=[Pt.cta('Abrir negócio','PT-05det.dc.html',True)],
          o=[(f"Contrato {CT['id']}: {CT['contratado']} t · R$ {nf(CT_VAL)} · liberado {CT['liberado']} t no PC-088",None),('Abrir o negócio','PT-05det.dc.html')]),
        R('n2',neg=two(COT['id'],f"{COT['itens']} itens · {COT['t']}"),res=ch('Em cotação','yellow'),cond=[Pt.mut('—')],doc=[Pt.txt('proposta v1 submetida')],
          ent=[Pt.txt('até 10/10'),Pt.br(),Pt.mut('revisa até '+COT['revisa'])],acao=[Pt.cta('Abrir proposta','PT-02det.dc.html')]),
        R('n3',neg=two(PERDIDA['neg'],f"{PERDIDA['item']} · {PERDIDA['vol']}"),res=ch('Perdeu','gray'),cond=[Pt.mut('—')],doc=[Pt.txt('comprovante v2')],ent=[Pt.mut('—')],
          acao=[Pt.act('Ver motivo','Motivo agregado: condição comercial — não revela proposta concorrente nem dado reservado.')]),
      ],edit=dict(m='ro',title='Negócio'),search=False,total=False,gid='g_ng')
    msg=grid([C('neg','Negócio'),C('de','De · quando'),C('m','Mensagem',w=520)],[
        R('m1',neg='PC-088',de=two('Comprador','23/09 15:30'),m='Confirmem a placa do caminhão da carga 3 — responder dentro do negócio'),
        R('m2',neg='NF 4501',de=two('Comprador','19/09 17:02'),m=f"{CT['quar']} t da carga 2 em quarentena · enviar laudo de garantia até {CT['laudo']}"),
        R('m3',neg=PERDIDA['neg'],de=two('Resultado','20/08'),m='Motivo agregado “condição comercial” — não revela proposta concorrente'),
      ],edit=dict(m='ro',title='Mensagem'),search=False,total=False,gid='g_msg')
    corpo=(section('Meus negócios','Abra o negócio para programar entregas e enviar documentos.','',ng)
      +section('Mensagens vinculadas','Responda dentro do negócio; nada fica em canal avulso.','',msg,state='gray'))
    shell37('PT-05','Negócios e documentos',corpo,ctx=CTX_F,perfil=PERFIL_F,
      subtitle='Negócios ganhos e perdidos próprios, pedidos, documentos e a execução permitida a você.',
      status=('NF-e da carga 3 pendente','yellow'),
      primary='Abrir negócio PC-088',primary_href='PT-05det.dc.html',
      footer='Motivos agregados de perda não revelam proposta concorrente; mensagem permanece vinculada ao negócio.')

# ---- PT-05det · negócio CT-2026-11 / PC-088 ----
def pt05det():
    fname='PT-05det.dc.html'; start(fname,1180); PARENT37[fname]='PT-05.dc.html'
    cond=grid([C('campo','Campo',w=180),C('valor','Valor',w=520)],[
        R('c1',campo='Item e volume',valor=f"KCl 60% · contrato {CT['contratado']} t · liberado {CT['liberado']} t no PC-088"),
        R('c2',campo='Preço e frete',valor=f"R$ {nf(KCL_T)}/t · CIF Galpão 2 · tolerância −5% / +5% (v2 aceita)"),
        R('c3',campo='Pagamento',valor=f"28 dias após o aceite do recebimento · título único do PC-088 de R$ {nf(PC_VAL)} ({CT['liberado']} t × R$ {nf(PC['preco'],2)}/kg) · sem barter"),
        R('c4',campo='Origem',valor=f"cotação {CT['cot']} · proposta v2 selecionada em 05/09"),
      ],edit=dict(m='ro',title='Condição aceita'),search=False,total=False,gid='g_cond')
    cg=grid([C('c','Carga',w=140),C('q','Quantidade',t='num',a='r',u='t'),C('d','Data prevista',t='date'),C('placa','Placa'),C('doc','Documento',w=220),C('s','Situação',w=240)],[
        R('c12',ro=True,c=[Pt.b('Cargas 1–2')],v=dict(q=CT['recebido'],d='2026-09-19',placa='QAS-1B20'),doc=[Pt.txt('NF 4501')],
          s=[Pt.chip('Recebida','green'),Pt.br(),Pt.mut(f"{CT['apto']} t aptas + {CT['quar']} t em quarentena")],
          o=[(f"Conferida em 19/09 · lote K26-11 · laudo das {CT['quar']} t até {CT['laudo']}",None)]),
        R('c3',c=[Pt.b('Carga 3')],v=dict(q=CT['carga3'],d='2026-10-02',placa='',obs=''),doc=ch('NF-e a enviar','yellow'),s=ch('Liberada · a entregar','yellow')),
        R('c4',ro=True,c=[Pt.b('Carga 4')],v=dict(q=40,d='2026-10-08',placa=''),doc=[Pt.mut('—')],s=ch('Proposta · aguarda liberação do comprador','gray'),
          o=[('Só vira entrega quando o comprador liberar; até lá não há obrigação de envio',None)]),
      ],edit=dict(m='form',title='Previsão da carga',sub='Atualize data prevista e placa; o comprador é notificado e a condição aceita não muda.',
                  fields=[F('d','Data prevista','date',req=True,help='Janela da carga 3: até 10/10 (plantio do T4).'),F('placa','Placa do caminhão',req=True,help='Ex.: QAS-2C41'),
                          F('obs','Motivo da mudança','area')]),search=False,total=False,gid='g_cg')
    dc=grid([C('doc','Documento',w=200),C('carga','Carga'),C('prazo','Prazo'),C('s','Situação',w=200)],[
        R('d1',doc='NF 4501',carga='Cargas 1–2',prazo='19/09',s=ch('Enviada · conferida','green')),
        R('d2',doc='Laudo de garantia · K26-11',carga=f"Carga 2 · {CT['quar']} t",prazo=CT['laudo'],s=ch('A enviar','yellow')),
        R('d3',doc='NF-e + laudo',carga='Carga 3',prazo=CT['prev3'],s=ch('A enviar','yellow')),
      ],edit=dict(m='ro',title='Documento'),search=False,total=False,gid='g_dc')
    js=JS()
    js.after("if(gid==='g_cg' && r){ self.setState({g2toast:'Previsão da carga 3 atualizada · comprador notificado'+"+json.dumps(SIM)+"}); }")
    div=js.once('div','Abrir divergência','Divergência aberta e vinculada ao PC-088 · o comprador responde dentro do negócio — nada muda no estoque de ninguém sem tratativa.',
                'Já existe divergência aberta neste pedido · acompanhe pelas mensagens do negócio; nada foi duplicado.',name='alert',title='Abrir divergência vinculada ao pedido')
    js.flush()
    env=drawer_button('Enviar documento da carga 3',dict(title='Documento da carga 3',sub='fica vinculado ao pedido PC-088 e à carga',
            fields=[('Tipo','NF-e'),('Número','000.412'),('Anexo','nfe-000412.xml')],confirm='Enviar documento',done='NF-e vinculada à carga 3 · obrigação atendida'),primary=True,small=False)
    corpo=(continuity('Negócios e documentos',f"PC-088 · {CT['recebido']} t recebidas",f"NF-e da carga 3 ({CT['prev3']}) · laudo até {CT['laudo']}",'Enviar documento da carga 3')
      +section('Entregas','Clique na carga liberada para atualizar data prevista e placa.','',
        stepper([('Cotação respondida','done'),('Proposta selecionada','done'),('Pedido confirmado','done'),('Entrega e documentos','now'),('Recebimento','todo'),('Pagamento','todo')],
                'Entregue dentro da janela com NF-e e laudo por carga — recusa no recebimento abre divergência, não devolve ao estoque apto.')
        +'<div style="height: 12px;"></div>'+cg,state='yellow')
      +section('Documentos','Envie NF-e e laudo de cada carga; o comprador confere no recebimento.',[div],dc)
      +section('Condição aceita','Confira a condição acordada; mudar exige novo aceite do comprador.','',cond,state='gray'))
    shell37('PT-05',f"Negócio · {CT['id']} KCl 60%",corpo,fname=fname,ctx=CTX_F,perfil=PERFIL_F,
      crumbs_extra=['PC-088'],status=('Carga 3 a entregar · NF-e pendente','yellow'),primary_html=env,
      footer='Revisão de pedido preserva versões e exige novo aceite; recusa no recebimento não recoloca produto em estoque apto (FO-35).')

# ============ PT-06 · Indicadores do parceiro (Fertisul) ============
def pt06():
    start('PT-06.dc.html',1000)
    dec=FUNIL['propostas']-FUNIL['analise']
    fu=grid([C('e','Etapa',w=220),C('q','Quantidade',t='num',a='r'),C('val','Valor',t='num',a='r',pre='R$ ',zdash=True),C('conv','Conversão da etapa',w=220)],[
        R('f1',v=dict(e='Convites recebidos',q=FUNIL['convites'],val=0),conv=[Pt.mut('—')],o=[('11 no Sudoeste GO + 3 no Triângulo MG',None)]),
        R('f2',v=dict(e='Propostas submetidas',q=FUNIL['propostas'],val=FUNIL['prop_valor']),conv=[Pt.txt(pct(FUNIL['propostas'],FUNIL['convites'])+' dos convites')],
          o=[(f"{FUNIL['propostas']} de {FUNIL['convites']} convites respondidos",None),(f"inclui a {COT['sol']} em análise",'PT-02.dc.html')]),
        R('f3',v=dict(e='Selecionadas',q=FUNIL['ganhos'],val=FUNIL['ganhos_valor']),conv=[Pt.txt(pct(FUNIL['ganhos'],dec)+' das decididas')],
          o=[(f"{FUNIL['ganhos']} de {dec} propostas decididas ({FUNIL['analise']} ainda em análise)",None),(f"{CT['id']} · R$ {nf(CT_VAL)} em execução",'PT-05det.dc.html'),
             (f"2 negócios concluídos · R$ {nf(FUNIL['concl_valor'])}",'PT-05.dc.html')]),
        R('f4',v=dict(e='Negócios concluídos',q=FUNIL['concl'],val=FUNIL['concl_valor']),conv=[Pt.txt(pct(FUNIL['concl'],FUNIL['ganhos'])+' · 1 em execução')],
          o=[('Abrir negócios próprios','PT-05.dc.html')]),
      ],edit=dict(m='origin',title='Etapa do funil',fields=[F('e','Etapa',ro=True),F('q','Quantidade','num',ro=True)]),search=False,total=False,gid='g_fu')
    acao=drawer_part('Criar ação interna',dict(title='Ação interna da Fertisul',sub='fica só na sua organização — não chega ao produtor',
            fields=[('Tema','revisar condição comercial no Triângulo MG'),('Responsável','Diego Prado'),('Prazo','15/10/2026')],confirm='Criar ação',done='Ação interna criada · visível só para a Fertisul'))
    co=grid([C('reg','Categoria · região',w=300),C('conv','Convites',t='num',a='r'),C('gan','Ganhos',t='num',a='r'),C('rec','Receita própria',t='num',a='r',pre='R$ ',zdash=True),C('cob','Cobertura'),C('acao','Ação')],[
        R('r1',v=dict(reg='Fertilizantes e corretivos · Sudoeste GO',conv=11,gan=FUNIL['ganhos'],rec=FUNIL['concl_valor']),cob=ch('Região principal','green'),acao=[Pt.mut('—')],
          o=[(f"Receita própria = negócios concluídos; o {CT['id']} entra quando concluir",None)]),
        R('r2',v=dict(reg='Fertilizantes e corretivos · Triângulo MG',conv=3,gan=0,rec=0),cob=ch('Sem ganho no período','gray'),acao=[acao]),
      ],edit=dict(m='origin',title='Cobertura',fields=[F('reg','Categoria · região',ro=True)]),search=False,total=False,gid='g_co')
    ag=grid([C('i','Indicador agregado',w=380),C('p','Sua posição'),C('n','Amostra'),C('s','Situação')],[
        R('a1',i='Preço mediano de fertilizantes NPK · Sudoeste GO',p='−2% vs. mediana',n='n = 17',s=ch('Publicado','green'),o=[('Mediana de 17 propostas de 9 fornecedores, com consentimento',None)]),
        R('a2',i='Prazo médio de entrega · Triângulo MG',p='—',n='n < 10',s=ch('Suprimido · amostra pequena','gray'),o=[('Amostra menor que 10: suprimido para não identificar fazenda',None)]),
      ],edit=dict(m='origin',title='Agregado',fields=[F('i','Indicador',ro=True)]),search=False,total=False,gid='g_ag')
    exp=ic(msgbtn('Exportar autorizado','Exportação gerada só com dados próprios e agregados autorizados · o acesso fica registrado.'),'doc','Exportar só dados próprios e agregados autorizados')
    corpo=(kpis([('TAXA DE RESPOSTA',pct(FUNIL['propostas'],FUNIL['convites']),f"{FUNIL['propostas']} de {FUNIL['convites']} convites"),
                 ('CONVERSÃO',pct(FUNIL['ganhos'],dec),f"{FUNIL['ganhos']} de {dec} decididas"),
                 ('ENTREGAS NO PRAZO','92%','12 de 13 cargas'),
                 ('RECEITA PRÓPRIA',f"R$ {nf(FUNIL['concl_valor']/1000)} mil",'negócios concluídos')])
      +section('Funil próprio','Clique na etapa para ver de onde vem cada número.',[exp],fu)
      +section('Origem e cobertura','Compare regiões e crie ações internas onde não há ganho.','',co)
      +section('Agregados protegidos','Consulte o benchmark publicado; amostra pequena fica suprimida.','',ag,state='gray'))
    shell37('PT-06','Indicadores',corpo,ctx=CTX_F,perfil=PERFIL_F,
      subtitle='Últimos 12 meses · indicadores próprios e, quando contratado, agregados com proteção contra reidentificação.',
      footer='Filtros de amostras pequenas não permitem inferir fazenda individual; benchmark entre clientes exige governança e consentimentos aplicáveis.')

# ============ PT-07 · Perfil e assinatura (Fertisul) ============
def pt07():
    start('PT-07.dc.html',1260)
    CATS=['Fertilizantes e corretivos','Sementes','Defensivos','Combustível']
    REGS=['Sudoeste GO','Triângulo MG','Oeste BA','Médio-Norte MT']
    CULTS=['Soja','Milho','Café','Algodão','Feijão']
    emp=grid([C('emp','Empresa · CNPJ',w=220),C('cat','Categorias',w=180),C('reg','Regiões',w=170),C('cult','Culturas atendidas',w=180),C('mail','E-mail de cotação',w=200),C('whats','WhatsApp'),C('cred','Situação')],[
        R('e1',v=dict(cnpj=FERT['cnpj'],cat='Fertilizantes e corretivos',reg='Sudoeste GO; Triângulo MG',cult='Soja; Milho; Café',mail=FERT['email'],whats=FERT['whats']),
          emp=two('Fertisul Fertilizantes Ltda',FERT['cnpj']),cred=ch('Homologado','green'))],
        edit=dict(m='form',title='Credenciamento',sub='Mudar categoria ou região recalcula a correspondência de convites; credenciamento não altera a disputa.',
                  fields=[F('cnpj','CNPJ',ro=True),F('cat','Categorias','multi',req=True,opts=CATS),F('reg','Regiões','multi',req=True,opts=REGS),
                          F('cult','Culturas atendidas','multi',req=True,opts=CULTS),F('mail','E-mail de cotação','email',req=True),F('whats','WhatsApp','tel',req=True)]),
        search=False,total=False,gid='g_emp')
    pref=grid([C('tipo','Aviso',w=260),C('canal','Canal',w=220)],[
        R('p1',v=dict(tipo='Novos convites',canal='Portal + e-mail')),R('p2',v=dict(tipo='Prazos a vencer',canal='Portal + e-mail')),
        R('p3',v=dict(tipo='Mensagens de negócio',canal='Portal')),R('p4',v=dict(tipo='Resultado de cotação',canal='Portal + e-mail'))],
        edit=dict(m='form',title='Preferência de aviso',sub='Escolha por onde receber este tipo de aviso.',
                  fields=[F('tipo','Aviso',ro=True),F('canal','Canal','sel',req=True,opts=['Portal','Portal + e-mail','Portal + WhatsApp','Portal + e-mail + WhatsApp'])]),
        search=False,total=False,gid='g_pref')
    us=grid([C('nome','Usuário',w=180),C('mail','E-mail',w=220),C('papel','Papel'),C('sit','Situação'),C('acao','Ação')],[
        R('u1',ro=True,v=dict(nome='Marta Nunes',mail='marta@fertisul.com.br',papel='Administradora'),sit=ch('Ativa','green'),acao=[Pt.mut('você')],
          o=[('A administradora gere usuários; o próprio papel muda só com outra administradora',None)]),
        R('u2',v=dict(nome='Diego Prado',mail='diego@fertisul.com.br',papel='Comercial'),sit=ch('Ativo','green'),
          acao=[Pt.act('Revogar acesso','Acesso de Diego revogado imediatamente · sessões encerradas · registro no histórico do parceiro.',u=True)]),
        R('u3',v=dict(nome='Sônia Reis',mail='sonia@fertisul.com.br',papel='Financeiro'),sit=ch('Convite pendente','yellow'),
          acao=[Pt.act('Reenviar convite','Convite reenviado a Sônia · expira em 7 dias'+SIM+'.')]),
      ],edit=dict(m='form',title='Usuário',newTitle='Convidar usuário',sub='O papel limita o que a pessoa vê e faz no portal; o convite expira em 7 dias.',
                  fields=[F('nome','Nome',req=True),F('mail','E-mail','email',req=True),F('papel','Papel','sel',req=True,opts=['Administradora','Comercial','Financeiro','Logística'],default='Comercial')]),
        add='Convidar usuário',search=False,total=False,gid='g_us')
    pl=grid([C('item','Item',w=300),C('cond','Condição',w=280),C('vig','Vigência'),C('sit','Situação',w=220)],[
        R('l1',item='Fornecedor básico',cond='gratuito',vig='—',sit=ch('Ativo','green')),
        R('l2',item='Parceiro Profissional v1 · indicadores e ferramentas',cond=[Pt.txt('preço por organização em revisão'),Pt.br(),Pt.chip('Hipótese de preço · não decidido','yellow')],
          vig='01/09/2026 – 31/08/2027',sit=ch('Aceite do novo preço até 30/09','yellow'),o=[('Nada é cobrado sem o seu aceite',None)]),
        R('l3',item='Módulo credor',cond='se contratado: proposta comercial — nunca cobrança por hectare',vig='—',sit=ch('Não contratado','gray')),
      ],edit=dict(m='ro',title='Plano'),search=False,total=False,gid='g_pl')
    js=JS()
    js.after("if(gid==='g_emp' && r){ self.setState({g2toast:'Perfil atualizado · correspondência de convites recalculada'}); }")
    js.after("if(gid==='g_pref' && r){ self.setState({g2toast:'Preferência salva · '+r.v.tipo+' por '+r.v.canal}); }")
    js.after("if(gid==='g_us' && r && String(r.id).indexOf('n')===0 && !r.v.__ok){ r.v.__ok=1; r.p.sit=[{k:'chip',t:'Convite pendente',c:'yellow'}]; r.s.sit='Convite pendente'; _set(self,gid,rows); "
             "self.setState({g2toast:'Convite enviado a '+r.v.nome+' · expira em 7 dias'+"+json.dumps(SIM)+"}); }")
    js.flush()
    ver=ic(msgbtn('Ver assinatura e fatura','Parceiro Profissional v1 · vigência 01/09/2026 – 31/08/2027 · cartão final 3307 · renovação exige seu aceite do novo preço até 30/09 — nada é cobrado sem aceite.'),'card','Ver assinatura, fatura e forma de pagamento')
    corpo=(section('Empresa e credenciamento','Clique na linha para atualizar categorias, regiões e contatos; os convites são recalculados.','',emp)
      +section('Usuários e papéis','Clique no usuário para mudar o papel; convide novos pela barra da tabela.','',us)
      +section('Preferências de aviso','Clique no tipo de aviso para escolher o canal.','',pref,state='gray')
      +section('Plano e assinatura','Confira o plano; plano pago não altera ranking técnico nem autorização de dados.',[ver],pl,state='yellow'))
    shell37('PT-07','Perfil e assinatura',corpo,ctx=CTX_F,perfil=PERFIL_F,
      subtitle='Empresa, usuários, credenciamento, avisos e contrato de serviço — administrado pelo próprio parceiro.',
      status=('Aceite do novo preço até 30/09','yellow'),
      footer='Publicidade, se existir, é distinta de comparação econômica; plano pago não altera ranking técnico nem autorização de dados.')
