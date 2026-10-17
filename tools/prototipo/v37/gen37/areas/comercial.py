# -*- coding: utf-8 -*-
"""Área Comercial (módulo OCULTO do menu, preservado) — processo sequencial por links:
VE-01 Confira demanda e oferta › VE-02 Acompanhe o mercado › VE-03 Faça ofertas › VE-04 Registre pedidos (+ VE-04det PV-031)
› VE-05 Controle contratos › VE-06 Trate reclamações.
Regras centrais (inalteradas): disponibilidade por data do cap. 49 (D.DISPON 3.000 base → 2.000 atendíveis),
reserva temporária → compromisso SEM dupla dedução (ATP-04/07), DEMO-06 (não prometer 10 t quando só 9,6 t A),
DEMO-08 (retorno bloqueado não vira vendável), DEMO-10 (barter e garantia contam uma vez), DEMO-18 (disputa de saldo
com conflito e recibo idempotente), DEMO-19 (PV-028 sem alocação por L27-013 bloqueado).
Padrão v3.7-processos: faixa de etapas por links, descrição imperativa sob cada bloco, edição pela linha (G2)."""
from engine import (grid,section,kpis,chip,btn,tag,icon,esc,seg,msgbtn,drawer_button,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,RED,GRAYS,EXTRAJS)
import engine as E
from ui37 import shell37, steps_bar, continuity, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
# ---- dados locais da área (coerentes com dados.py/dados2.py; números compartilhados vêm de D/D2) ----
PV=dict(id='PV-031', cliente='Frutas Real', item='Mamão Formosa · classe A', qtd_t=D.PREVISAO['classeA_t'],
        prometivel_t=D.PREVISAO['futuras_A'], falta_t=D.PREVISAO['falta'],
        preco=3.05, janela='28/09–04/10', cond='CIF Vitória/ES · 28 d após entrega')
LOTE_A=dict(id='L39-120', ob='OB-0110', insp='INSP-92', origem='L38-115..118', t=D.PACKING['saidaA'])  # CO-05det/CO-07
LOTE_B=dict(id='L39-121', t=D.PACKING['saidaB'])
RT=dict(id='RT-0112', qtd_kg=2000, vence='24/09 18:00')           # reserva temporária do portal (PT-03)
RTP=dict(id='RT-0107', t=D.PREVISAO['futuras_A'])                  # reserva provisória do PV-031 sobre L39-120 (CO-07)
CASO=dict(id='RC-12', pedido='PV-027', qtd_kg=300, lote='L26-118') # retorno recebido bloqueado (DEMO-08)
VG=dict(id='VG-117', pedido='PV-026', lote='L38-110', recusa_t=0.4, oc='OC-77')  # recusa parcial registrada em LO-03
PC=next(p for p in D2.PEDIDOS if p['id']=='PC-088')                # PC-088 · Fertisul · KCl 60 % (fonte única)
FORN_PC=next(f['nome'] for f in D2.FORNECEDORES if f['id']==PC['f'])
PC_VALOR=round(PC['qtd']*PC['preco'])                              # R$ 233.000
BT=dict(id='BT-090', sc=1000, eq=131.00)                           # barter de insumos 26/27 · sem pedido de compra vinculado (PC-088 é título único, D.CANON['PC088'])
BT_VALOR=round(BT['sc']*BT['eq'])                                  # R$ 131.000
SOJA_V2=51280                                                      # previsão V2 de soja 26/27 (GE-02/GE-08)
CPR=dict(id='CRE-0095', sc=6900, contraparte='Agroquímica Delta')  # barter de defensivos (GE-08)
CT203=12000
FIS=CT203+CPR['sc']+BT['sc']                                       # obrigações físicas soja 26/27
PENHOR=round(SOJA_V2*0.30)                                         # penhor do CRE-0102 (GE-08)
GAR=PENHOR+CPR['sc']

def n0(v): return f'{v:,.0f}'.replace(',','.')
def n1(v): return f'{v:.1f}'.replace('.',',')
def rs(v): return 'R$ '+n0(v)
def pct(a,b): return f'{a/b*100:.0f}%'

STEPS=[('Confira demanda e oferta','VE-01.dc.html'),('Acompanhe o mercado','VE-02.dc.html'),('Faça ofertas','VE-03.dc.html'),
       ('Registre pedidos','VE-04.dc.html'),('Controle contratos','VE-05.dc.html'),('Trate reclamações','VE-06.dc.html')]
WHY={4:f'{PV["id"]} · falta {n1(PV["falta_t"])} t',6:f'{CASO["id"]} aguarda Qualidade'}
def faixa(i):
    return steps_bar([dict(t=t,href=h,why=WHY.get(k,''),tip=t+(' · '+WHY[k] if k in WHY else '')) for k,(t,h) in enumerate(STEPS,1)],current=i,label='Etapas')

def ic(html,name,title=None):
    """Ação secundária com ícone + rótulo + title (acessível)."""
    t=f' title="{esc(title)}"' if title else ''
    svg=icon(name,14)
    html=html.replace('display: inline-block;','display: inline-flex; align-items: center; gap: 6px;',1)
    if html.startswith('<a '): return html.replace('<a ',f'<a{t} ',1).replace('">',f'">{svg}',1)
    return html.replace('<button ',f'<button{t} ',1).replace('style="',f'style="display: inline-flex; align-items: center; gap: 6px; ',1).replace('">',f'">{svg}',1)

def nota(txt): return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6;">{txt}</div>'
def B(t): return f'<b style="color:{INK};">{t}</b>'

def C(k,l,**kw): return dict(k=k,l=l,**kw)
def plain(parts): return ' '.join(p['t'] for p in parts if p.get('k')!='br').strip()
def R(id,ro=False,o=None,v=None,**cells):
    """linha G2: str/número → v (editável, ordenável); lista de partes → p (exibição rica, busca por texto)."""
    r=dict(id=id,v=dict(v or {}),s={},p={})
    for k,x in cells.items():
        if isinstance(x,list): r['p'][k]=x; r['s'][k]=plain(x)
        else: r['v'][k]=x
    if ro: r['ro']=True
    if o: r['o']=[dict(t=t,h=h) if h else dict(t=t) for t,h in o]
    return r
def two(a,b): return [Pt.b(a),Pt.br(),Pt.mut(b)]
PRIM_ST=E.BTN_ST(True)   # o primário do engine (antes uma cópia local, sem alvo de toque)
PRIM=f'<button type="button" onClick="{H("prim_fn")}" title="{H("prim_tip")}" style="{H("prim_st")}">{H("prim_t")}</button>'
JS_BASE='''
function GR(id){ return GRIDS.find(g=>g.id===id); }
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function setRow(self,gid,rid,fn){ const sp=GR(gid); const rows=g2clone(g2rows(self,sp)); const r=g2find(rows,rid); if(r) fn(r); g2set(self,gid,{rows}); return r; }
function isNew(r){ return r && String(r.id).indexOf('n')===0 && !r.v.__ok; }
'''

def build():
    # ================= VE-01 · Confira demanda e oferta =================
    fname='VE-01.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    estoque,futura,compr,marg=2400,9100,6000,500
    formula=(f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: stretch;">'
      +''.join(f'<div style="flex: 1 1 0; min-width: 128px; background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px;">'
               f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .05em; color: {MUTED};">{lbl}</div>'
               f'<div style="font-size: 17px; font-weight: 800; color: {cor}; margin-top: 4px;">{val}</div>'
               f'<div style="font-size: 11.5px; color: {MUTED}; margin-top: 2px;">{sub}</div></div>'
        for lbl,val,sub,cor in [
          ('VENDÁVEL ELEGÍVEL',n0(estoque+futura)+' kg',f'estoque apto {n0(estoque)} kg + produção {n0(futura)} kg',INK),
          ('− COMPROMISSOS',n0(compr)+' kg','pedidos firmes, contados uma vez',INK),
          ('− RESERVAS TEMP.',H('f_rt'),f'{RT["id"]} · vence {RT["vence"]}',INK),
          ('− MARGEM',n0(marg)+' kg','segurança definida pelo produtor',INK),
          ('= SALDO PRODUTO',H('f_base'),'disponível na base do produto',ACC),
          ('PUBLICADO',H('f_pub'),'limite de packing e expedição',ACC),
        ])+'</div>'
      + f'<div style="font-size: 12px; color: {MUTED}; margin-top: 8px;">Atualizado hoje 06:30</div>')
    bal_cols=[C('prod','Produto · classe',w=160),C('janela','Janela'),C('dem','Demanda',w=220),C('ofe','Oferta',w=220),
              C('saldo','Falta ou excesso',w=200),C('acao','Próximo passo')]
    bal=[
      R('b1',prod=two('Mamão Formosa · A','T7 · packing'),janela='28/09–04/10',
        dem=[Pt.txt(f'{n1(PV["qtd_t"])} t · '),Pt.link(PV['id'],'VE-04det.dc.html'),Pt.mut(' a confirmar')],
        ofe=[Pt.txt(f'{n1(LOTE_A["t"])} t · '),Pt.link(LOTE_A['id'],'CO-07.dc.html'),Pt.mut(' em inspeção')],
        saldo=[Pt.chip(f'Falta {n1(PV["falta_t"])} t','yellow')],acao=[Pt.cta('Detalhar demanda','VE-04det.dc.html',True)],
        o=[(f'Demanda: {PV["id"]} · {PV["cliente"]} · {n1(PV["qtd_t"])} t classe A (a confirmar)','VE-04det.dc.html'),
           (f'Oferta: {LOTE_A["id"]} · {n1(LOTE_A["t"])} t classe A do packing {LOTE_A["ob"]} (12,0 t × 80%)','CO-05det.dc.html'),
           (f'{LOTE_A["id"]} reservado provisoriamente ({RTP["id"]}) e aguardando {LOTE_A["insp"]}','CO-07.dc.html'),
           (f'Falta = {n1(PV["qtd_t"])} − {n1(LOTE_A["t"])} = {n1(PV["falta_t"])} t sem origem',None)]),
      R('b2',prod=two('Mamão Formosa · A','T7 · packing'),janela='05/10–11/10',
        dem=[Pt.txt(f'{n0(compr)} kg firmes + {n0(RT["qtd_kg"])} kg '),Pt.link(RT['id'],'PT-03.dc.html')],
        ofe=[Pt.txt(f'{n0(estoque)} kg estoque + {n0(futura)} kg produção')],
        saldo=[Pt.chip(f'Publicável {n0(D.DISPON["atendivel_kg"])} kg','green')],
        acao=[Pt.cta('Criar oferta','VE-03.dc.html')],
        o=[('Cálculo no bloco "Disponibilidade da semana 05/10" abaixo',None),
           (f'{n0(estoque+futura)} − {n0(compr)} − {n0(RT["qtd_kg"])} − {n0(marg)} (margem) = {n0(D.DISPON["base_kg"])} kg',None),
           (f'Publicável limitado a {n0(D.DISPON["atendivel_kg"])} kg pela capacidade de packing e expedição',None)]),
      R('b3',prod=two('Mamão Formosa · B','T7 · packing'),janela='28/09–04/10',
        dem=[Pt.txt('3,0 t · '),Pt.link('PV-032','VE-04.dc.html'),Pt.txt(' 1,8 + '),Pt.link('PV-033','VE-04.dc.html'),Pt.txt(' 1,2')],
        ofe=[Pt.txt(f'{n1(LOTE_B["t"])} t · '),Pt.link(LOTE_B['id'],'CO-07.dc.html'),Pt.mut(' em inspeção')],
        saldo=[Pt.chip('Disputa · falta 1,2 t','yellow')],acao=[Pt.cta('Confirmar pedidos','VE-04.dc.html')],
        o=[('PV-032 · Frutas Real · 1,8 t B (OF-101 v1)','VE-04.dc.html'),('PV-033 · Rede Hortifrúti BA · 1,2 t B (contraproposta v2)','VE-04.dc.html'),
           (f'Oferta: {LOTE_B["id"]} · {n1(LOTE_B["t"])} t classe B do packing {LOTE_A["ob"]}','CO-05det.dc.html'),
           ('Quem confirmar primeiro leva o saldo; o outro recebe conflito com o disponível consultado',None)]),
      R('b4',prod=two('Café beneficiado','Armazém Sede'),janela='out–nov/26',
        dem=[Pt.txt('2.500 sc · '),Pt.link('CT-198','VE-05.dc.html'),Pt.txt(' 2.000 + '),Pt.link('PV-028','VE-04.dc.html'),Pt.txt(' 500')],
        ofe=[Pt.txt('0 sc · '),Pt.link(D.LOTE_BLOQ['id'],'CO-06det.dc.html'),Pt.mut(' bloqueado')],
        saldo=[Pt.chip('Falta 2.500 sc','red')],acao=[Pt.cta('Abrir inspeção','CO-06det.dc.html',True)],
        o=[('CT-198 · Torrefação Serra · 2.000 sc','VE-05.dc.html'),('PV-028 · Torrefação Serra · 500 sc sem alocação','VE-04.dc.html'),
           (f'{D.LOTE_BLOQ["id"]} · {n0(D.LOTE_BLOQ["sc"])} sc · {D.LOTE_BLOQ["inspecao"]} — bloqueado não conta como oferta','CO-06det.dc.html')]),
      R('b5',prod=two('Soja · padrão 26/27','T1+T2+T4'),janela='fev–mar/27',
        dem=[Pt.txt(f'{n0(FIS)} sc · '),Pt.link('obrigações físicas','VE-05.dc.html')],
        ofe=[Pt.txt(f'{n0(SOJA_V2)} sc · '),Pt.link('previsão V2','GE-08.dc.html')],
        saldo=[Pt.chip(f'Sem obrigação {n0(SOJA_V2-FIS)} sc','yellow')],acao=[Pt.cta('Propor ajuste','PL-06.dc.html')],
        o=[(f'CT-203 {n0(CT203)} sc + CPR {CPR["id"]} {n0(CPR["sc"])} sc + {BT["id"]} {n0(BT["sc"])} sc = {n0(FIS)} sc','VE-05.dc.html'),
           (f'Previsão V2 de soja 26/27: {n0(SOJA_V2)} sc','GE-08.dc.html'),
           (f'Penhor do CRE-0102 ({n0(PENHOR)} sc) é garantia, não demanda — dimensão separada',None)]),
    ]
    g_bal=grid(bal_cols,bal,edit=dict(m='origin',title='Balanço',fields=[]),gid='g_bal',total=False)
    res_cols=[C('res','Reserva',w=170),C('tipo','Tipo'),C('qt','Quantidade',a='r'),C('venc','Vencimento'),C('estado','Estado'),C('efeito','Efeito no saldo',w=260)]
    res=[
      R('r1',v=dict(qtd=RT['qtd_kg'],un='kg'),res=two(RT['id'],'Frutas Real · portal · OF-103'),tipo=[Pt.tag('Reserva temporária')],qt=[Pt.txt(f'{n0(RT["qtd_kg"])} kg')],
        venc=RT['vence'],estado=[Pt.chip('Aguardando pedido','yellow')],efeito='já deduzida; vira pedido sem nova dedução'),
      R('r2',v=dict(qtd=RTP['t']*1000,un='kg'),res=two(RTP['id'],f'{PV["id"]} · Frutas Real'),tipo=[Pt.tag('Reserva provisória')],qt=[Pt.txt(f'{n0(RTP["t"]*1000)} kg')],
        venc=f'até confirmar {PV["id"]}',estado=[Pt.chip(f'Em {LOTE_A["id"]} · aguarda {LOTE_A["insp"]}','yellow')],
        efeito='deduzida uma vez; vira compromisso ao confirmar o pedido'),
      R('r3',ro=True,v=dict(qtd=5000,un='sc'),res=two('RT-0109','Coop Grão Sul'),tipo=[Pt.tag('Reserva temporária')],qt=[Pt.txt('5.000 sc')],
        venc='20/09 12:00',estado=[Pt.chip('Expirada','gray')],efeito='saldo liberado uma única vez'),
    ]
    g_res=grid(res_cols,res,edit=dict(m='form',title='Reserva',sub='Ajuste quantidade e vencimento. A dedução continua única: o saldo é recalculado, nunca somado de novo.',
        fields=[dict(k='qtd',l='Quantidade reservada',t='num',req=True,min=1,u='kg'),dict(k='venc',l='Vencimento',t='txt',req=True,help='Ex.: 24/09 18:00')]),
        search=False,gid='g_res',total=False)
    EXTRAJS[0]=JS_BASE+f'''
const ELEG={estoque+futura}, COMPR={compr}, MARG={marg}, CAP={D.DISPON['atendivel_kg']}, RTQ0={RT['qtd_kg']};
function saldoRT(self){{ const q=(self.state.rtq===undefined)?RTQ0:self.state.rtq; const base=Math.max(0,ELEG-COMPR-q-MARG); return {{q,base,pub:Math.min(base,CAP)}}; }}
function PREVALS(self,v){{ const s=saldoRT(self); const g=GR('g_bal'); const b=g.rows.find(x=>x.id==='b2');
  b.p.dem=[{{k:'txt',t:nf(COMPR)+' kg firmes + '+nf(s.q)+' kg '}},{{k:'link',t:'{RT['id']}',h:'PT-03.dc.html'}}]; b.s.dem=nf(COMPR)+' kg firmes + '+nf(s.q)+' kg {RT['id']}';
  b.p.saldo=[{{k:'chip',t:'Publicável '+nf(s.pub)+' kg',c:'green'}}]; b.s.saldo='Publicável '+nf(s.pub)+' kg';
  b.o=[{{t:'Cálculo no bloco "Disponibilidade da semana 05/10" abaixo'}},{{t:nf(ELEG)+' − '+nf(COMPR)+' − '+nf(s.q)+' − '+nf(MARG)+' (margem) = '+nf(s.base)+' kg'}},{{t:'Publicável limitado a '+nf(CAP)+' kg pela capacidade de packing e expedição'}}];
  v.f_rt=nf(s.q)+' kg'; v.f_base=nf(s.base)+' kg'; v.f_pub=nf(s.pub)+' kg'; }}
function EXTRAVALS(self,v){{ self.g2after=(gid,rows,r)=>{{ if(gid==='g_res'&&r){{ r.p.qt=[{{k:'txt',t:nf(r.v.qtd)+' '+(r.v.un||'kg')}}]; r.s.qt=nf(r.v.qtd)+' kg';
    if(r.id==='r1'){{ const s0=saldoRT(self); self.setState({{rtq:Number(r.v.qtd)||0,g2toast:'{RT['id']} ajustada para '+nf(r.v.qtd)+' kg · saldo recalculado com dedução única (antes '+nf(s0.base)+' kg).'}}); }}
    else self.setState({{tick:Date.now()}}); }} }}; }}
'''
    corpo=(
      section('Balanço por produto, classe e janela','Compare demanda e oferta de cada janela e trate a falta antes de prometer.',
        [seg(['Semana','Dia'],0),
         ic(btn('Rever previsão',small=True,href='CO-01.dc.html'),'trend','Abrir a previsão de colheita (CO-01)'),
         ic(msgbtn('Simular atendimento',f'Mamão A · 28/09–04/10: máximo factível {n1(LOTE_A["t"])} t ({LOTE_A["id"]}, se a {LOTE_A["insp"]} liberar) contra {n1(PV["qtd_t"])} t do {PV["id"]} — {n1(PV["falta_t"])} t descobertas; alternativa: {n0(D.DISPON["atendivel_kg"])} kg publicáveis na semana 05/10.'),'calc','Simular o atendimento da janela'),
         ic(btn('Propor ajuste',small=True,href='PL-06.dc.html'),'layers','Propor ajuste no plano (PL-06)')],
        g_bal)
      + section('Disponibilidade da semana 05/10 · Mamão A','Confira como o saldo publicado é calculado: cada obrigação deduz uma vez.','',formula)
      + section('Reservas e promessas','Acompanhe cada reserva até virar pedido ou expirar; clique na linha para ajustar.','',g_res)
      + section('Déficit visível ao produtor','Resolva a falta com aceite do cliente; ao comprador publique zero, nunca quantidade negativa.',
        ic(btn('Renegociar no pedido',small=True,href='VE-04det.dc.html'),'doc',f'Abrir o pedido {PV["id"]}'),
        nota(f'{B("Mamão A · 28/09: −"+n1(PV["falta_t"])+" t")} · causa: rendimento A de 80% sobre 12,0 t brutas · pedido em risco: {B(PV["id"])} (a confirmar; {n1(PV["prometivel_t"])} t prometíveis). '
             f'Saídas com aceite: revisão v3 com {n1(PV["prometivel_t"])} t, deslocar {n1(PV["falta_t"])} t para 05/10 ou origem parceira elegível e rastreável.'),state='yellow'))
    shell37('VE-01','Demanda e oferta',corpo,
      subtitle='Estoque elegível + oferta confiável − compromissos únicos − margem, por dia e classe.',
      status=(f'Falta {n1(PV["falta_t"])} t · Mamão A','yellow'),
      primary='Criar oferta',primary_href='VE-03.dc.html',steps=faixa(1),
      footer='Compromisso firme, reserva temporária e reserva física da mesma obrigação são fases com identidade comum — nunca deduções cumulativas (49.2–49.3, ATP-07). '
             'Saldo final é o máximo factível sob capacidade e prazo: folga de outra classe ou dia não cobre esta janela; é condição prevista, não garantia.')

    # ================= VE-02 · Acompanhe o mercado =================
    fname='VE-02.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    pr_cols=[C('inst','Instrumento',w=200),C('fonte','Fonte · licença'),C('praca','Praça'),C('un','Unidade'),C('moeda','Moeda'),C('venc','Vencimento/data'),C('preco','Preço/basis',a='r'),C('atraso','Atraso')]
    PR=[('Soja futuro SFH27','B3 · uso interno','Paranaguá','sc 50 kg','BRL','fev/27',[Pt.txt('R$ 132,00')],'15 min'),
        ('Soja ZS','CBOT · licença corretora','Chicago','bushel','USD','mai/27',[Pt.txt('US$ 10,42 · basis −0,35')],'15 min'),
        ('Soja indicador','CEPEA/Esalq · pública','Paraná','sc 50 kg','BRL','22/09',[Pt.txt('R$ 129,40')],'D-1'),
        ('Milho indicador','CEPEA/Esalq · pública','Campinas','sc 60 kg','BRL','22/09',[Pt.txt('R$ 61,80')],'D-1'),
        ('Mamão Formosa','CEAGESP · pública','São Paulo','kg','BRL','22/09',[Pt.txt('R$ 3,10')],'D-1'),
        ('Café arábica','B3/ICE · licença corretora','Nova York','lb','USD','set/27',[Pt.txt('US¢ 248,5')],'15 min'),
        ('Feijão carioca','—','—','sc 60 kg','BRL','—',[Pt.chip('Sem cotação · ausente ≠ zero','gray')],'—')]
    g_pr=grid(pr_cols,[R(f'p{i}',inst=[Pt.b(a)],fonte=b,praca=c,un=d,moeda=e,venc=f,preco=g,atraso=[Pt.tag(h)] if h!='—' else '—') for i,(a,b,c,d,e,f,g,h) in enumerate(PR)],
        edit=dict(m='ro',title='Cotação',fields=[dict(k='fonte',l='Fonte · licença',t='txt'),dict(k='praca',l='Praça',t='txt'),dict(k='un',l='Unidade',t='txt'),dict(k='venc',l='Vencimento/data',t='txt')]),
        gid='g_pr',total=False)
    al_cols=[C('inst','Instrumento',w=180),C('cond','Condição'),C('lim','Limite',t='num',a='r',pre='R$ ',d=2),C('canal','Avisar por'),C('val','Validade',t='date'),C('estado','Estado',chips={'Ativo':'green','Pausado':'gray'})]
    g_al=grid(al_cols,[R('a1',v=dict(estado='Ativo'),inst='Soja fev/27 · B3',cond='Acima de',lim=135.0,canal='WhatsApp',val='2026-11-30',estado=[Pt.chip('Ativo','green')]),
                      R('a2',v=dict(estado='Ativo'),inst='Mamão Formosa · CEAGESP',cond='Abaixo de',lim=2.60,canal='E-mail',val='2026-10-31',estado=[Pt.chip('Ativo','green')])],
        edit=dict(m='form',title='Alerta',newTitle='Novo alerta de preço',sub='O alerta avisa quando o preço cruza o limite; ele não realiza venda.',
          fields=[dict(k='inst',l='Instrumento',t='sel',req=True,opts=['Soja fev/27 · B3','Soja indicador · CEPEA','Milho indicador · CEPEA','Mamão Formosa · CEAGESP','Café arábica · ICE'],**{'def':'Soja fev/27 · B3'}),
                  dict(k='cond',l='Condição',t='sel',req=True,opts=['Acima de','Abaixo de'],**{'def':'Acima de'}),
                  dict(k='lim',l='Limite',t='num',req=True,min=0.01,u='R$ por unidade da cotação'),
                  dict(k='canal',l='Avisar por',t='sel',req=True,opts=['WhatsApp','E-mail','Push no app'],**{'def':'WhatsApp'}),
                  dict(k='val',l='Validade',t='date',req=True),
                  dict(k='estado',l='Estado',t='sel',opts=['Ativo','Pausado'],**{'def':'Ativo'})]),
        add='Novo alerta',search=False,gid='g_al',total=False)
    corpo=(
      section('Preços observados por instrumento e mercado','Compare preços com fonte, licença e atraso à vista; cotação ausente não vira zero.',
        [seg(['Físico','Futuros','Câmbio'],0),
         ic(msgbtn('Comparar janelas','Soja fev/27 × mai/27: +R$ 4,20/sc no diferido; carrego (armazenagem + juros) estimado R$ 3,10/sc → janela mai/27 ganha R$ 1,10/sc.'),'trend','Comparar janelas de venda'),
         ic(msgbtn('Simular preço líquido','Soja fev/27 a R$ 132,00/sc − frete R$ 6,50 − impostos/taxas R$ 6,60 = R$ 118,90/sc líquido na fazenda · frete e taxas são hipóteses da simulação.'),'calc','Simular o preço líquido na fazenda')],
        g_pr)
      + section('Alertas de preço','Crie alertas para ser avisado quando o preço cruzar o limite; clique na linha para ajustar.','',g_al)
      + section('Conversões declaradas','Declare a conversão antes de comparar bushel, saca, tonelada e moedas.',
        ic(btn('Usar premissa',small=True,href='GE-02.dc.html'),'cash','Levar o câmbio como premissa da gestão (GE-02)'),
        nota('1 sc soja = 50 kg · 1 bushel soja = 27,216 kg (≈ 0,5443 sc) · 1 lb = 0,4536 kg. '
             f'Câmbio da simulação: R$ 5,32/US$ (PTAX D-1) — {B("hipótese de simulação")}.')))
    shell37('VE-02','Mercado e preços',corpo,
      subtitle='Preços observados, contratos, câmbio e sazonalidade por instrumento e mercado, com atraso visível.',
      primary='Preparar oferta',primary_href='VE-03.dc.html',steps=faixa(2),
      footer='Alerta não realiza venda; cotação ausente não vira zero; toda conversão de unidade e moeda é declarada com fonte e licença. '
             'O câmbio da simulação vira premissa só ao usar na gestão. Contrato futuro não é inventado: só instrumentos existentes nas fontes.')

    # ================= VE-03 · Faça ofertas =================
    fname='VE-03.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    of_cols=[C('of','Oferta',w=150),C('vol','Volume',a='r'),C('janela','Janela'),C('dest','Destino · clientes',w=170),C('pr','Preço · condição'),C('estado','Estado · validade',w=240),C('acao','Ação')]
    def oferta(oid,ver,prod,volkg,vtx,janela,destv,cli,preco,unp,prazo,val,estado,cor,acao,ro=True,o=None):
        return R(oid,ro=ro,o=o,v=dict(prod=prod,volkg=volkg,preco=preco,prazo=prazo,destv=destv,janela=janela,val=val),
          of=two(f'{oid} · {ver}',prod.replace(' · classe',' ')),vol=[Pt.txt(vtx)],janela=janela,dest=[Pt.txt(destv),Pt.br(),Pt.mut(cli)],
          pr=[Pt.txt(f'R$ {preco:,.2f}'.replace(',','X').replace('.',',').replace('X','.')+f'/{unp} · {prazo}')],
          estado=[Pt.chip(estado,cor),Pt.br(),Pt.mut(f'válida até {val}' if val!='—' else 'sem validade')],acao=acao)
    ofertas=[
      oferta('OF-103','enviada','Mamão Formosa · classe A',D.DISPON['atendivel_kg'],f'{n0(D.DISPON["atendivel_kg"])} kg','05/10–11/10','CIF região Sudeste','Frutas Real',3.05,'kg','28 d','30/09',
             f'Enviada · reservada pela {RT["id"]}','yellow',[Pt.cta('Ver reserva','VE-01.dc.html')],o=[('Volume = publicável da semana 05/10 (VE-01)','VE-01.dc.html'),(f'{RT["id"]} · {n0(RT["qtd_kg"])} kg reservados pela Frutas Real no portal','PT-03.dc.html')]),
      oferta('OF-101','v1','Mamão Formosa · classe B',1800,'1,8 t','28/09–04/10','FOB fazenda','Frutas Real · Rede Hortifrúti BA',2.10,'kg','21 d','26/09',
             'Aceita · PV-032 e PV-033','yellow',[Pt.cta('Confirmar no pedido','VE-04.dc.html')]),
      oferta('OF-102','v2','Mamão Formosa · classe A',10000,'10,0 t','28/09–04/10','CIF Vitória/ES','Frutas Real',3.05,'kg','28 d','24/09',
             f'Virou {PV["id"]} · a confirmar','yellow',[Pt.cta('Ver pedido','VE-04det.dc.html')]),
      oferta('OF-100','v1','Café beneficiado',30000,'500 sc','out/26','FOB armazém','Torrefação Serra',2480.00,'sc','FOB','—',
             f'Virou PV-028 · {D.LOTE_BLOQ["id"]} bloqueado','red',[Pt.cta('Ver pedido','VE-04.dc.html')]),
      oferta('OF-099','v1','Soja padrão 26/27',250000,'5.000 sc','fev/27','CIF Paranaguá','Coop Grão Sul',131.00,'sc','à vista','20/09',
             'Expirada · RT-0109 liberada','gray','—'),
    ]
    g_of=grid(of_cols,ofertas,edit=dict(m='form',title='Oferta',newTitle='Nova oferta privada',
        sub='Rascunho privado: nada é enviado ao salvar. Enviar exige revisar destinatários; oferta aceita ou expirada abre só para consulta.',
        fields=[dict(k='prod',l='Produto · classe',t='sel',req=True,opts=['Mamão Formosa · classe A','Mamão Formosa · classe B','Café beneficiado','Soja padrão 26/27','Milho padrão'],**{'def':'Mamão Formosa · classe A'}),
                dict(k='volkg',l='Volume',t='num',req=True,min=1,u='kg',help=f'Máximo publicável na semana 05/10: {n0(D.DISPON["atendivel_kg"])} kg (VE-01).'),
                dict(k='janela',l='Janela',t='txt',req=True,help='Ex.: 05/10–11/10'),
                dict(k='destv',l='Destino · frete',t='sel',req=True,opts=['CIF região Sudeste','CIF Vitória/ES','FOB fazenda','FOB armazém','CIF Paranaguá'],**{'def':'CIF região Sudeste'}),
                dict(k='preco',l='Preço',t='num',req=True,min=0.01,u='R$',help='Por kg (frutas) ou por saca (grãos e café).'),
                dict(k='prazo',l='Prazo de pagamento',t='sel',opts=['21 d','28 d','35 d','contra entrega'],**{'def':'28 d'}),
                dict(k='val',l='Validade',t='txt',req=True,help='Ex.: 30/09')]),
        add=None,gid='g_of',total=False)
    cmp_cols=[C('prop','Proposta',w=220),C('cli','Cliente'),C('preco','Preço',a='r'),C('frete','Frete por conta'),C('prazo','Prazo'),C('liq','Líquido/kg',a='r'),C('dif','Diferença')]
    g_cmp=grid(cmp_cols,[
        R('c1',prop=[Pt.b('v1 · aceita (PV-032)')],cli='Frutas Real',preco=[Pt.txt('R$ 2,10/kg')],frete='cliente (FOB)',prazo='21 d',liq=[Pt.b('R$ 2,10')],dif=[Pt.chip('Melhor líquido','green')],
          o=[('R$ 2,10/kg − frete R$ 0,00 (FOB) = R$ 2,10/kg',None),('Pedido PV-032 · 1,8 t B','VE-04.dc.html')]),
        R('c2',prop=[Pt.txt('v2 · contraproposta (PV-033)')],cli='Rede Hortifrúti BA',preco=[Pt.txt('R$ 2,25/kg')],frete='produtor (CIF, R$ 0,26/kg)',prazo='35 d',liq=[Pt.txt('R$ 1,99')],dif=[Pt.txt('−R$ 0,11/kg')],
          o=[('R$ 2,25/kg − frete CIF R$ 0,26/kg = R$ 1,99/kg',None),('Pedido PV-033 · 1,2 t B','VE-04.dc.html')])],
        edit=dict(m='origin',title='Líquido',fields=[]),search=False,gid='g_cmp',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_of'||!r) return; const q=Number(r.v.volkg)||0;
    if(isNew(r)){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; r.id='OF-'+(103+n); r.v.__ok=1; r.p.of=[{k:'b',t:r.id+' · rascunho'},{k:'br',t:''},{k:'mut',t:r.v.prod}]; r.s.of=r.id; r.p.estado=[{k:'chip',t:'Rascunho · privado',c:'gray'}]; r.p.acao=[{k:'mut',t:'clique para ajustar'}]; }
    const un=String(r.v.prod).indexOf('Mamão')>=0?'kg':'sc'; r.p.vol=[{k:'txt',t:nf(q)+' kg'}]; r.s.vol=nf(q)+' kg'; r.p.pr=[{k:'txt',t:'R$ '+nf(r.v.preco,2)+'/'+un+' · '+(r.v.prazo||'')}]; r.s.pr=r.p.pr[0].t;
    const cli=(r.p.dest&&r.p.dest[2])?r.p.dest[2].t:'a definir'; r.p.dest=[{k:'txt',t:r.v.destv},{k:'br',t:''},{k:'mut',t:cli}]; r.s.dest=r.v.destv;
    const ch=(r.p.estado&&r.p.estado[0])?r.p.estado[0]:{k:'chip',t:'Rascunho · privado',c:'gray'}; r.p.estado=[ch,{k:'br',t:''},{k:'mut',t:'válida até '+r.v.val}]; r.s.estado=ch.t; self.setState({tick:Date.now()}); }; }
'''
    corpo=(
      section('Negociações em andamento','Prepare ofertas privadas por cliente; proposta aceita só vira venda na confirmação do pedido.',
        [drawer_button('Revisar destinatários',dict(title='Destinatários elegíveis',sub='correspondência explicada por categoria, cultura e região — acesso só por convite confirmado ou política autorizada',
           fields=[('Cliente','Frutas Real — atacado de frutas · Sudeste · convite confirmado'),
                   ('Cliente','Rede Hortifrúti BA — varejo · Nordeste · convite confirmado'),
                   ('Finalidade e prazo','cotação de mamão · acesso até 30/09 · documentos: padrão de classificação')],
           confirm='Confirmar destinatários',done='2 destinatários confirmados — parceiro pagante sem convite NÃO recebe')).replace('<button ','<button title="Revisar quem pode receber a oferta" ',1),
         ic(msgbtn('Enviar oferta','Rascunho enviado aos destinatários com convite confirmado pelo portal do cliente (PT-03) · finalidade, prazo e documentos registrados · simulado, nenhuma mensagem real enviada. OF-103 já está com a Frutas Real (RT-0112).'),'users','Enviar a oferta em rascunho aos destinatários confirmados'),
         f'<button type="button" onClick="{H("g_of_new")}" title="Criar oferta privada" style="{E.BTN_ST(False,True)}">Criar oferta</button>'],
        g_of)
      + section('Comparação de recebimento líquido · OF-101','Compare propostas pelo líquido na fazenda, não pelo preço de face.',
        ic(msgbtn('Comparar propostas','OF-101: Frutas Real v1 rende R$ 2,10/kg líquidos contra R$ 1,99/kg da contraproposta da Rede Hortifrúti BA (frete CIF por conta do produtor) — melhor líquido: Frutas Real (PV-032).'),'scale','Comparar propostas pelo líquido'),
        g_cmp))
    shell37('VE-03','Ofertas e propostas',corpo,
      subtitle='Negociação com propostas privadas por cliente, preço líquido e atendimento possível.',
      status=('OF-101 aceita · 2 pedidos a confirmar','yellow'),
      primary='Abrir pedidos da OF-101',primary_href='VE-04.dc.html',steps=faixa(3),
      footer='Proposta não fecha pedido sozinha; contraproposta é versionada e o aceite vale para a versão exata (cap. 46). '
             'Confirme só pedidos que passam em margem, crédito, exposição, saldo e capacidade. Aceite registrado pelas duas partes, por versão. Confirmação automática só sob política prévia explícita do produtor. Alteração de preço fora da política volta à negociação como nova versão.')

    # ================= VE-04 · Registre pedidos =================
    fname='VE-04.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    cart_cols=[C('ped','Pedido',w=90),C('cli','Cliente'),C('item','Item · classe'),C('qt','Quantidade · janela',a='r',w=120),C('pr','Preço · condição',w=160),C('aloc','Alocação · estado',w=240),C('acao','Ação')]
    def ped(pid,cli,item,q,un,preco,unp,janela,cond,aloc,acao,ro=True,o=None):
        qs=(n1(q) if un=='t' else n0(q))+' '+un; ps='R$ '+(f'{preco:,.2f}'.replace(',','X').replace('.',',').replace('X','.'))+'/'+unp
        return R(pid,ro=ro,o=o,v=dict(qtd=q,un=un,preco=preco,unp='R$/'+unp,cond=cond,janela=janela),ped=[Pt.b(pid)],cli=cli,item=item,qt=[Pt.txt(qs),Pt.br(),Pt.mut(janela)],pr=[Pt.txt(ps),Pt.br(),Pt.mut(cond)],aloc=aloc,acao=acao)
    cart=[
      ped('PV-033','Rede Hortifrúti BA','Mamão Formosa · B',1.2,'t',2.25,'kg','28/09–04/10','CIF · 35 d',[Pt.chip('A confirmar · disputa 1,8 t B','yellow')],
          [{'k':'act','t':'Confirmar pedido','fn':'confirmar:PV-033'}],ro=False),
      ped('PV-032','Frutas Real','Mamão Formosa · B',1.8,'t',2.10,'kg','28/09–04/10','FOB · 21 d',[Pt.chip('A confirmar · disputa 1,8 t B','yellow')],
          [{'k':'act','t':'Confirmar pedido','fn':'confirmar:PV-032'}],ro=False),
      ped(PV['id'],PV['cliente'],'Mamão Formosa · A',PV['qtd_t'],'t',PV['preco'],'kg',PV['janela'],'CIF · 28 d',
          [Pt.chip(f'A confirmar · {n1(PV["prometivel_t"])} t com origem','yellow')],[Pt.cta('Resolver alocação','VE-04det.dc.html',True)]),
      ped('PV-034','CD Horti','Mamão Formosa · A',9.6,'t',3.05,'kg','25/09 11:00–12:00','CIF · 28 d',
          [Pt.chip('Alocado PK-L-M09 · Carga 07 impedida · NF pendente','red')],[Pt.cta('Ver carga','LO-01.dc.html')],
          o=[('Carga 07 · CD Horti · Vitória/ES · lote embalado PK-L-M09 · 9,6 t','LO-01.dc.html'),('NF pendente · dono Sandra (fiscal) · prazo 10:00',None)]),
      ped('PV-030','Coop Grão Sul','Soja · padrão 25/26',12000,'sc',128.00,'sc','set–out/26','FOB · contra entrega',
          [Pt.chip('Expedido 8.000 · saldo 4.000 sc','yellow')],[Pt.cta('Programar entrega','LO-01.dc.html')]),
      ped('PV-029','Atacado Bom Preço','Milho · padrão',4000,'sc',61.00,'sc','set/26','CIF · 14 d',
          [Pt.chip('Entregue · pagamento em aberto','yellow')],[Pt.cta('Ver recebíveis','GE-05.dc.html')]),
      ped('PV-028','Torrefação Serra','Café beneficiado',500,'sc',2480.00,'sc','out/26','FOB armazém',
          [Pt.chip(f'Sem alocação · {D.LOTE_BLOQ["id"]} bloqueado','red')],[Pt.cta('Abrir inspeção','CO-06det.dc.html',True)]),
      ped('PV-027','Rede Hortifrúti BA','Mamão Formosa · A',6.0,'t',2.95,'kg','14/09–20/09','CIF · 21 d',
          [Pt.chip(f'Devolução parcial · {CASO["id"]}','yellow')],[Pt.cta('Tratar devolução','VE-06.dc.html')]),
      ped(VG['pedido'],'Frutas Real','Mamão Formosa · A',9.4,'t',3.00,'kg','21/09–22/09','CIF · 28 d',
          [Pt.chip(f'Entregue 9,0 t · recusa 0,4 t (RC-15)','yellow')],[Pt.cta('Tratar recusa','VE-06.dc.html')]),
    ]
    g_cart=grid(cart_cols,cart,edit=dict(m='form',title='Pedido',newTitle='Novo pedido de venda',
        sub='Pedido a confirmar pode ser ajustado aqui. Confirmado, entregue ou em revisão abre em consulta: mudança vira nova versão com novo aceite.',
        fields=[dict(k='cli',l='Cliente',t='sel',req=True,opts=['Frutas Real','Rede Hortifrúti BA','Coop Grão Sul','Atacado Bom Preço','Torrefação Serra'],**{'def':'Frutas Real'}),
                dict(k='item',l='Itens · classe',t='sel',req=True,opts=['Mamão Formosa · A','Mamão Formosa · B','Café beneficiado','Soja · padrão 25/26','Soja · padrão 26/27','Milho · padrão'],**{'def':'Mamão Formosa · A'}),
                dict(k='qtd',l='Quantidade',t='num',req=True,min=0.1),
                dict(k='un',l='Unidade',t='sel',req=True,opts=['t','sc','kg'],**{'def':'t'}),
                dict(k='preco',l='Preço por unidade',t='num',req=True,min=0.01,u='R$'),
                dict(k='janela',l='Janela',t='txt',req=True,help='Ex.: 05/10–11/10'),
                dict(k='cond',l='Condição',t='sel',req=True,opts=['FOB · 21 d','CIF · 14 d','CIF · 21 d','CIF · 28 d','CIF · 35 d','FOB · contra entrega','FOB armazém'],**{'def':'CIF · 28 d'})]),
        add='Novo pedido',gid='g_cart',total=False)
    # colheita (06/10, spec §3.5): seção "Reservas de produto" com os pedidos do estado (c.producao) e o mesmo comando prReservar do Estoque
    # de produto; a linha estática do PV-030 na carteira continua até a frente Comercial (§9)
    import cenario, dados_carencia as _DC
    from areas import producao as _PRD
    g_rsv=grid([C('ped','Pedido · cliente',w=200),C('prod','Produto',w=190),C('tipo','Tipo · janela',w=160),dict(k='qtd',l='Quantidade',t='num',a='r'),
                dict(k='res',l='Reservado',t='num',a='r'),dict(k='falta',l='Falta',t='num',a='r'),C('sit','Situação · próximo passo',w=250)],
               [],edit=dict(m='pick'),gid='g_rsv',total=False,qf=dict(k='sit',cut=' · ',l='Situação',todas='Todos'))
    E.EXTRA.append(_PRD.painel())
    EXTRAJS[0]=cenario.js_prefixo()+_DC.js_nucleo()+_PRD.PR_UI_JS+_PRD.PR_PED_JS+JS_BASE+'''
const NEED={'PV-032':1.8,'PV-033':1.2}; const SALDO_B=1.8; const REC={'PV-032':'CMD-5521','PV-033':'CMD-5522'};
function qtxt(r){ return (r.v.un==='t'?nf(r.v.qtd,1):nf(r.v.qtd))+' '+(r.v.un||''); }
function EXTRAVALS(self,v){
  v.confirmar=(pid)=>{ const conf=Object.assign({},self.state.vconf||{});
    if(conf[pid]){ self.setState({g2toast:pid+' já confirmado · mesmo recibo '+conf[pid]+' devolvido · nada deduzido de novo.'}); return; }
    const q=(id)=>{ const r=g2find(g2rows(self,GR('g_cart')),id); return r?(Number(r.v.qtd)||0):(NEED[id]||0); };
    let usado=0; for(const k in conf){ usado+=q(k); } const disp=Math.max(0,SALDO_B-usado); const need=q(pid);
    if(need>disp+1e-9){ const ver=15+Object.keys(conf).length;
      setRow(self,'g_cart',pid,r=>{ r.p.aloc=[{k:'chip',t:'Conflito de saldo · '+nf(disp,1)+' t B livres',c:'red'}]; r.s.aloc='Conflito de saldo'; });
      self.setState({g2toast:'Conflito de saldo no '+pid+': a versão do saldo mudou (v'+(ver-1)+' → v'+ver+') · disponível classe B 28/09–04/10 = '+nf(disp,1)+' t · alternativas: 1,2 t B na semana 05/10 ou reduzir o volume com aceite · nada foi reservado.'}); return; }
    conf[pid]=REC[pid];
    setRow(self,'g_cart',pid,r=>{ r.ro=true; r.p.aloc=[{k:'chip',t:'Confirmado · recibo '+REC[pid],c:'green'}]; r.s.aloc='Confirmado'; });
    self.setState({vconf:conf,g2toast:pid+' confirmado numa transação única: preço, crédito, saldo ('+nf(need,1)+' t B) e capacidade verificados · '+nf(need,1)+' t alocadas uma única vez · recibo '+REC[pid]+'.'}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_cart'||!r) return;
    if(isNew(r)){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; const id='PV-0'+(33+n); r.v.__ok=1; r.p.ped=[{k:'b',t:id}]; r.s.ped=id; r.p.aloc=[{k:'chip',t:'Aguardando confirmação',c:'yellow'}]; r.s.aloc='Aguardando confirmação'; r.p.acao=[{k:'mut',t:'confirmação verifica saldo e crédito'}]; }
    r.v.unp='R$/'+(r.v.un==='t'?'kg':r.v.un); r.p.qt=[{k:'txt',t:qtxt(r)},{k:'br',t:''},{k:'mut',t:r.v.janela||''}]; r.s.qt=qtxt(r); r.p.pr=[{k:'txt',t:'R$ '+nf(r.v.preco,2)+'/'+(r.v.un==='t'?'kg':r.v.un)},{k:'br',t:''},{k:'mut',t:r.v.cond||''}]; r.s.pr=r.p.pr[0].t; self.setState({tick:Date.now()}); };
}
/* reservas de produto (estado compartilhado com Produção › Estoque de produto): mesma linha, mesmo painel, mesmo prReservar */
const PR_GRIDS={g_rsv:1};
const _g2rows0=g2rows; g2rows=function(self,sp){ return PR_GRIDS[sp.id]?sp.rows:_g2rows0(self,sp); };
function PREVALS(self,v){ cenOuvir(self); const c=cenGet(); self._c=c;
  self.g2pick=(gid,rid)=>{ if(gid==='g_rsv') self.setState({pr_sel:{g:gid,id:rid},pr_pan:{g:gid,id:rid},pr_form:null,pr_err:'',pr_cx:null,pr_ch:prChave('W-RS')}); };   /* chave do formulário aberto (colheita, revisão A-03) */
  GR('g_rsv').rows=Object.values(prP(c).pedidos).sort((a,b)=>a.id.localeCompare(b.id)).map(p=>prPedRow(c,p)); }
const _EXV_VE=EXTRAVALS; EXTRAVALS=function(self,v){ _EXV_VE(self,v); const c=self._c||cenGet(); const P=prP(c); const pan=self.state.pr_pan;
  prPainel(self,v,(pan&&pan.g==='g_rsv'&&P.pedidos[pan.id])?prPanPed(self,c,P.pedidos[pan.id]):null); };
'''
    # TAB-07 (DS-MODULOS-2, 17/10/2026): sem cartões de resumo sobre a lista; o que pede atenção vai no selo do cabeçalho e o resto já está nas linhas
    corpo=(
      section('Carteira de pedidos','Confirme pedidos pela linha de ação e clique na linha para ajustar um pedido ainda a confirmar.',
        '',g_cart)
      + section('Reservas de produto','Pedidos do estado: clique num pedido para reservar lote apto ou cancelar reserva (o mesmo comando do Estoque de produto).','',g_rsv))
    shell37('VE-04','Pedidos de venda',corpo,
      subtitle='Confirmação valida preço, crédito, saldo e capacidade numa transação única; alocações futuras e físicas ficam separadas.',
      status=('3 a confirmar · 2 em risco · 1 disputa','yellow'),
      primary=f'Resolver alocação do {PV["id"]}',primary_href='VE-04det.dc.html',steps=faixa(4),
      footer='Expedição parcial mantém saldo; recebimento não é inferido da entrega; confirmar é idempotente — repetir devolve o mesmo recibo (49.3, ATP-05).')

    # ---- VE-04det · detalhe-âncora do pedido PV-031 ----
    fname='VE-04det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000; PARENT37[fname]='VE-04.dc.html'
    ver_cols=[C('ver','Versão',w=70),C('qt','Quantidade',a='r'),C('pr','Preço · medição'),C('janela','Janela'),C('frete','Frete'),C('venc','Vencimento'),C('motivo','Motivo',w=210),C('estado','Estado',w=200)]
    g_ver=grid(ver_cols,[R('v2',ro=True,v=dict(qtd=PV['qtd_t'],preco=PV['preco']),ver=[Pt.b('v2')],qt=[Pt.txt(f'{n1(PV["qtd_t"])} t')],
          pr=[Pt.txt('R$ 3,05/kg · saída do packing')],janela=PV['janela'],frete='CIF · produtor',venc='28 d após entrega',
          motivo='OF-102 v2 aceita',estado=[Pt.chip('Aceita · 22/09','green')])],
        edit=dict(m='form',title='Versão',newTitle='Revisão v3 do pedido',
          sub='A revisão preserva a v2 e as aceitações; a v3 só vale com novo aceite do cliente. Salvar envia a revisão (simulado · nenhuma mensagem real enviada).',
          fields=[dict(k='qtd',l='Quantidade',t='num',req=True,min=0.1,max=PV['qtd_t'],u='t',help=f'Prometível hoje: {n1(PV["prometivel_t"])} t classe A ({LOTE_A["id"]}).',**{'def':str(PV['prometivel_t']).replace('.',',')}),
                  dict(k='preco',l='Preço',t='num',req=True,min=0.01,u='R$/kg',**{'def':'3,05'}),
                  dict(k='janela',l='Janela',t='txt',req=True,**{'def':PV['janela']}),
                  dict(k='motivo',l='Motivo',t='sel',req=True,opts=['Rendimento A de 80% sobre 12,0 t brutas','Pedido do cliente','Deslocar saldo para outra janela'],**{'def':'Rendimento A de 80% sobre 12,0 t brutas'})]),
        search=False,gid='g_ver',total=False)
    at_cols=[C('orig','Origem',w=230),C('tipo','Tipo de alocação'),C('qt','Quantidade',a='r'),C('estado','Estado',w=210),C('obs','Rastreio',w=300)]
    g_at=grid(at_cols,[
        R('a1',orig=[Pt.link(LOTE_A['id'],'CO-07.dc.html'),Pt.txt(' · '),Pt.link(LOTE_A['ob'],'CO-05det.dc.html')],tipo=[Pt.tag(f'Reserva provisória {RTP["id"]}')],
          qt=[Pt.txt(f'{n1(LOTE_A["t"])} t A')],estado=[Pt.chip(f'Aguardando {LOTE_A["insp"]}','yellow')],
          obs=[Pt.txt(f'genealogia: {LOTE_A["origem"]} → {LOTE_A["ob"]} → {LOTE_A["id"]} → {PV["id"]}')],
          o=[(f'Estoque de produção: {LOTE_A["id"]} · {n1(LOTE_A["t"])} t · reserva provisória do {PV["id"]}','CO-07.dc.html'),
             (f'Packing {LOTE_A["ob"]}: 12,0 t de {LOTE_A["origem"]} → 9,6 t A + 1,8 t B + 0,6 t descarte','CO-05det.dc.html'),
             (f'Inspeção {LOTE_A["insp"]}: sem liberação o lote não expede','CO-06.dc.html')]),
        R('a2',orig=[Pt.mut('— sem origem')],tipo=[Pt.tag('Sem origem')],qt=[Pt.txt(f'{n1(PV["falta_t"])} t A')],estado=[Pt.chip('Falta origem','yellow')],
          obs='não se promete classe A pelo peso bruto a colher',o=[(f'{n1(PV["qtd_t"])} t pedidas − {n1(LOTE_A["t"])} t prometíveis = {n1(PV["falta_t"])} t',None)]),
        R('a3',orig=[Pt.txt(f'{RTP["id"]} → compromisso')],tipo=[Pt.tag('Conversão na confirmação')],qt=[Pt.txt(f'{n1(RTP["t"])} t A')],estado=[Pt.chip('Dedução única','green')],
          obs='ao confirmar, a reserva provisória vira alocação definitiva na mesma transação — sem intervalo livre e sem duas deduções',
          o=[('Regra 49.3 / ATP-07: reserva e compromisso da mesma obrigação têm identidade comum',None)]),
      ],edit=dict(m='origin',title='Alocação',fields=[]),search=False,gid='g_at',total=False)
    fin_cols=[C('ev','Evento',w=200),C('base','Base'),C('val','Valor previsto',a='r'),C('venc','Vencimento'),C('estado','Estado')]
    g_fin=grid(fin_cols,[
        R('f1',ev=f'Entrega de {n1(PV["prometivel_t"])} t',base='R$ 3,05/kg',val=[Pt.txt('R$ 29,3 mil')],venc='28 d após entrega',estado=[Pt.chip('Aguardando entrega','yellow')],
          o=[(f'{n1(PV["prometivel_t"])} t × R$ 3,05/kg = R$ 29.280',None)]),
        R('f2',ev=f'Saldo {n1(PV["falta_t"])} t',base='R$ 3,05/kg',val=[Pt.txt('R$ 1,2 mil')],venc='—',estado=[Pt.chip('Condicionado à origem','gray')],
          o=[(f'{n1(PV["falta_t"])} t × R$ 3,05/kg = R$ 1.220 · sai do pedido se a v3 for aceita',None)]),
      ],edit=dict(m='origin',title='Evento financeiro',fields=[]),search=False,gid='g_fin',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){ const v3=!!self.state.v3;
  v.pv_aqui=v3?'Revisão v3 aguardando aceite':'A confirmar · 9,6 de 10,0 t prometíveis';
  v.pv_falta=v3?'aceite do cliente na v3':'0,4 t A sem origem';
  v.pv_prox=v3?'Confirmar 9,6 t após o aceite':'Enviar revisão v3';
  v.pv_st=v3?'Revisão v3 aguardando aceite':'A confirmar · falta 0,4 t';
  v.prim_t=v3?'Aguardando aceite da v3':'Enviar revisão v3';
  v.prim_tip=v3?'A v3 já foi enviada; aguarde o aceite do cliente':'Abrir a revisão v3 com o volume prometível';
  v.prim_fn=v3?(()=>self.setState({g2toast:'Revisão v3 já enviada '+self.state.v3+' · nada reenviado · aguarda aceite do cliente.'})):v.g_ver_new;
  v.prim_st='padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;'+(v3?'background:#EEF1EE;color:#5B6660;border:1px solid #E4E9E5;':'background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;');
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_ver'||!r||!isNew(r)) return; r.v.__ok=1; r.id='v3'; r.ro=true;
    r.p.ver=[{k:'b',t:'v3'}]; r.s.ver='v3'; r.p.qt=[{k:'txt',t:nf(r.v.qtd,1)+' t'}]; r.s.qt=r.p.qt[0].t; r.p.pr=[{k:'txt',t:'R$ '+nf(r.v.preco,2)+'/kg · saída do packing'}]; r.s.pr=r.p.pr[0].t;
    r.v.frete='CIF · produtor'; r.v.venc='28 d após entrega'; r.p.estado=[{k:'chip',t:'Enviada · aguarda aceite',c:'yellow'}]; r.s.estado='Enviada';
    self.setState({v3:'hoje '+new Date().toTimeString().slice(0,5),g2toast:'Revisão v3 ('+nf(r.v.qtd,1)+' t) enviada ao cliente · v2 preservada · o pedido fica “Revisão v3 aguardando aceite” (simulado · nenhuma mensagem real enviada).'}); };
}
'''
    corpo=(
      continuity('OF-102 v2 aceita',H('pv_aqui'),H('pv_falta'),H('pv_prox'))
      + section('Comercial · versões do acordo','Revise volume ou preço criando nova versão; a v2 e as aceitações ficam preservadas.','',g_ver)
      + section('Atendimento · origem do pedido','Confira de qual lote sai cada tonelada e o que ainda não tem origem.',
        [ic(msgbtn('Alocar produção/estoque',f'Sem outra origem classe A apta: {LOTE_A["id"]} já reservado ({n1(LOTE_A["t"])} t) · {n1(PV["falta_t"])} t seguem descobertas — alternativas: revisão v3 com {n1(PV["prometivel_t"])} t, deslocar {n1(PV["falta_t"])} t para 05/10 ou origem parceira rastreável.'),'box','Procurar outra origem para a falta'),
         ic(btn('Programar entrega',small=True,href='LO-01.dc.html'),'truck','Programar a entrega em Logística (LO-01)')],
        g_at)
      + section('Financeiro','Acompanhe o recebimento pelo evento do acordo; a entrega sozinha não baixa o título.',
        [ic(msgbtn('Emitir solicitação fiscal','Bloqueada: entrega não programada — programe a entrega em Logística para emitir a solicitação fiscal.'),'doc','Emitir a solicitação fiscal do pedido'),
         ic(btn('Ver recebíveis',small=True,href='GE-05.dc.html'),'cash','Abrir contas a receber (GE-05)')],
        g_fin))
    shell37('VE-04',f'Pedido {PV["id"]} · Mamão Formosa A',corpo,fname=fname,crumbs_extra=[f'{PV["id"]} · {PV["cliente"]}'],
      subtitle=f'{PV["cliente"]} pediu {n1(PV["qtd_t"])} t; só {n1(PV["prometivel_t"])} t classe A têm origem ({LOTE_A["id"]}) — a falta aparece antes de prometer.',
      status=(H('pv_st'),'yellow'),primary_html=PRIM,steps=faixa(4),
      footer='Confirmar recalcula e reserva atomicamente; conversão de reserva em compromisso mantém dedução única (49.3, DEMO-06/07).')

    # ================= VE-05 · Controle contratos =================
    fname='VE-05.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    ob_cols=[C('ob','Obrigação · contraparte',w=180),C('prod','Produto · janela',w=190),C('vol','Volume',t='num',a='r',u='sc'),C('cond','Condições · vínculo',w=210),C('estado','Estado',w=220),C('acao','Ação')]
    def obr(oid,tipo,cp,prod,vol,janela,cond,vinc,est,cor,acao,o=None):
        return R(oid,ro=True,o=o,v=dict(cp=cp,prodv=prod,janela=janela,condv=cond),ob=[Pt.b(f'{oid} · {tipo}'),Pt.br(),Pt.mut(cp)],
                 prod=[Pt.txt(prod),Pt.br(),Pt.mut(janela)],vol=vol,cond=[Pt.txt(cond)]+([Pt.br()]+vinc if isinstance(vinc,list) else []),estado=[Pt.chip(est,cor)],acao=acao)
    obs=[
      obr('CT-201','venda','Coop Grão Sul','Soja 25/26 · sc 50 kg · FOB',12000,'set–out/26','R$ 128,00/sc',[Pt.link('PV-030','VE-04.dc.html')],
          '8.000 de 12.000 sc entregues','yellow',[Pt.cta('Programar entrega','LO-01.dc.html')]),
      obr('CT-203','venda','Coop Grão Sul','Soja 26/27 · sc 50 kg · FOB',CT203,'fev–mar/27','R$ 132,00/sc','—','Aguarda colheita','gray',[Pt.cta('Ver pedidos','VE-04.dc.html')]),
      obr(f'CPR {CPR["id"]}','barter',CPR['contraparte'],'Soja 26/27 · sc 50 kg',CPR['sc'],'fev–mar/27 · na colheita','R$ 820 mil em defensivos · 5,8 sc/ha',
          [Pt.mut('também garantia do crédito')],'Contratado · entrega na colheita','green',[Pt.cta('Ver crédito','GE-08.dc.html')],
          o=[('Contrato de crédito e garantia em GE-08','GE-08.dc.html')]),
      obr(BT['id'],'barter',FORN_PC,'Soja 26/27 · sc 50 kg',BT['sc'],'mar/27',f'{rs(BT_VALOR)} em insumos 26/27',[Pt.mut('sem pedido de compra vinculado')],
          'Conta uma vez','green',[Pt.cta('Ver contas a pagar','GE-04.dc.html')]),
      obr('CT-198','venda','Torrefação Serra','Café · sc 60 kg',2000,'out–nov/26','R$ 2.480,00/sc',[Pt.tag('CPR de garantia')],
          f'Em risco · {D.LOTE_BLOQ["id"]} bloqueado','red',[Pt.cta('Abrir inspeção','CO-06det.dc.html',True)]),
    ]
    g_ob=grid(ob_cols,obs,edit=dict(m='form',title='Obrigação',newTitle='Novo compromisso',
        sub='Obrigação única com contraparte, base e janela. Contrato assinado abre em consulta: mudança exige aditivo com aceite das partes.',
        fields=[dict(k='cp',l='Contraparte',t='sel',req=True,opts=['Coop Grão Sul','Torrefação Serra','Frutas Real',FORN_PC,CPR['contraparte']],**{'def':'Coop Grão Sul'}),
                dict(k='prodv',l='Produto · base',t='sel',req=True,opts=['Soja 26/27 · sc 50 kg · FOB','Soja 26/27 · sc 50 kg · Paranaguá','Café · sc 60 kg','Milho · sc 60 kg'],**{'def':'Soja 26/27 · sc 50 kg · Paranaguá'}),
                dict(k='vol',l='Volume',t='num',req=True,min=1,u='sc',help=f'Soja 26/27 sem obrigação física: {n0(SOJA_V2-FIS)} sc da previsão V2.'),
                dict(k='janela',l='Janela',t='txt',req=True,help='Ex.: mar/27'),
                dict(k='condv',l='Condições',t='txt',req=True,help='Ex.: R$ 133,00/sc · pagamento contra entrega')]),
        add=None,gid='g_ob',total=False)
    dim_cols=[C('dim','Dimensão',w=200),C('vol','Volume',t='num',a='r',u='sc'),C('pct','% da previsão V2',a='r'),C('comp','Composição',w=380)]
    g_dim=grid(dim_cols,[
        R('d1',dim=[Pt.b('Obrigações físicas')],vol=FIS,pct=pct(FIS,SOJA_V2),comp=f'CT-203 {n0(CT203)} + CPR {CPR["id"]} {n0(CPR["sc"])} + {BT["id"]} {n0(BT["sc"])} sc',
          o=[(f'CT-203 · Coop Grão Sul · {n0(CT203)} sc',None),(f'CPR {CPR["id"]} · {CPR["contraparte"]} · {n0(CPR["sc"])} sc','GE-08.dc.html'),(f'{BT["id"]} · {FORN_PC} · {n0(BT["sc"])} sc',None)]),
        R('d2',dim=[Pt.b('Garantias')],vol=GAR,pct=pct(GAR,SOJA_V2),comp=f'penhor CRE-0102 {n0(PENHOR)} (30%) + CPR {CPR["id"]} {n0(CPR["sc"])} sc — não é venda',
          o=[('Mesma conta de GE-08: penhor + CPR sobre a previsão V2','GE-08.dc.html'),('A CPR é obrigação física e garantia da mesma obrigação: conta uma vez em cada dimensão, nunca como segunda venda',None)]),
        R('d3',dim=[Pt.b('Sem preço (exposição)')],vol=SOJA_V2-FIS,pct=pct(SOJA_V2-FIS,SOJA_V2),comp=f'{n0(SOJA_V2)} − {n0(FIS)} sc de obrigações físicas',
          o=[(f'Previsão V2 {n0(SOJA_V2)} sc − obrigações físicas {n0(FIS)} sc',None)]),
      ],edit=dict(m='origin',title='Dimensão',fields=[]),search=False,gid='g_dim',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_ob'||!r||!isNew(r)) return; const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; const id='CT-'+(203+n);
  r.v.__ok=1; r.ro=true; r.p.ob=[{k:'b',t:id+' · venda'},{k:'br',t:''},{k:'mut',t:r.v.cp}]; r.s.ob=id; r.p.prod=[{k:'txt',t:r.v.prodv},{k:'br',t:''},{k:'mut',t:r.v.janela}]; r.s.prod=r.v.prodv; r.p.cond=[{k:'txt',t:r.v.condv}]; r.s.cond=r.v.condv; r.p.estado=[{k:'chip',t:'Formalizado · aguarda colheita',c:'gray'}]; r.s.estado='Formalizado';
  self.setState({tick:Date.now(),g2toast:id+' formalizado · obrigação registrada uma única vez · soja sem obrigação física recalculada.'}); }; }
'''
    corpo=(
      section('Obrigações físicas e vínculos','Registre cada obrigação uma vez; barter e garantia da mesma obrigação não viram segunda venda.',
        [ic(msgbtn('Vincular compra/crédito',f'{BT["id"]} segue sem pedido de compra vinculado ({rs(BT_VALOR)} em insumos 26/27 · {n0(BT["sc"])} sc). O {PC["id"]} ({FORN_PC} · {PC["item"]} · {n0(PC["qtd"]/1000)} t · {rs(PC_VALOR)}) é título único em Contas a pagar, sem barter — vincule o {BT["id"]} só a um pedido novo, sem título duplicado.'),'layers','Vincular a obrigação à compra ou ao crédito'),
         ic(msgbtn('Simular exposição',f'Soja 26/27 sobre a previsão V2 de {n0(SOJA_V2)} sc: obrigações físicas {n0(FIS)} sc ({pct(FIS,SOJA_V2)}) · garantias {n0(GAR)} sc ({pct(GAR,SOJA_V2)}, penhor + CPR, dimensão separada) · sem preço {n0(SOJA_V2-FIS)} sc · preço médio travado R$ 131,92/sc (CT-203 + {BT["id"]}; CPR paga em produto).'),'calc','Simular a exposição a preço'),
         ic(msgbtn('Liquidar por eventos','Nada a liquidar agora: liquidação usa somente eventos confirmados — 2 entregas e 1 pagamento aguardam confirmação.'),'check','Liquidar pelos eventos confirmados')],
        g_ob)
      + section(f'Soja 26/27 · previsão V2 de {n0(SOJA_V2)} sc','Veja obrigações físicas, garantias e exposição como dimensões separadas sobre a mesma base.','',g_dim))
    shell37('VE-05','Contratos e compromissos',corpo,
      subtitle='Contratos físicos, barter e compromissos vinculados a compra, venda e garantia — cada obrigação contada uma vez.',
      status=(f'CT-198 em risco · {D.LOTE_BLOQ["id"]} bloqueado','yellow'),
      primary_html=f'<button type="button" onClick="{H("g_ob_new")}" style="{PRIM_ST}">Formalizar compromisso</button>',steps=faixa(5),
      footer='Derivativos importados ficam em dimensão separada; liquidação usa eventos confirmados de entrega e pagamento, nunca o calendário (DEMO-10).')

    # ================= VE-06 · Trate reclamações =================
    fname='VE-06.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    MOT=['Avaria no transporte','Impureza acima do padrão','Umidade acima do padrão','Grãos ardidos','Maturação avançada','Classe divergente']
    TRAT=['a definir','Crédito solicitado','Crédito emitido','Sem crédito']
    rc_cols=[C('rc','Caso',w=70),C('ped','Pedido · entrega',w=200),C('motivo','Motivo · evidências',w=190),C('lq','Lote · quantidade',w=140),
             C('dec','Decisão · financeiro',w=210),C('acao','Ação')]
    def caso(cid,ped,sub,motivo,lote,qtd,evid,dec,cor,trat,acao,ro=False):
        return R(cid,ro=ro,v=dict(pedtx=ped,lote=lote,qtd=qtd,trat=trat,dect=dec,motivo=motivo,evid=evid),rc=[Pt.b(cid)],ped=[Pt.b(ped),Pt.br(),Pt.mut(sub)],motivo=[Pt.txt(motivo),Pt.br(),Pt.mut(evid)],
                 lq=[Pt.txt(f'{lote} · {qtd}')],dec=[Pt.chip(dec,cor),Pt.br(),Pt.mut(f'financeiro: {trat}')],acao=acao)
    rcs=[
      caso('RC-15',f'{VG["pedido"]} · {VG["id"]}','entrega 22/09 · recusa em LO-03','Avaria no transporte',VG['lote'],f'{n1(VG["recusa_t"])} t',
           f'{VG["oc"]} · canhoto + 4 fotos','Recusa registrada','yellow','a definir',
           [Pt.act('Autorizar retorno',f'Retorno de {n1(VG["recusa_t"])} t do {VG["lote"]} autorizado · entra BLOQUEADO no recebimento (CO-04) — não volta ao vendável até a Qualidade decidir.')]),
      caso('RC-14','PV-029 · 1/1','milho · Atacado Bom Preço','Grãos ardidos','L26-140','150 sc','—','Aguardando evidências','yellow','a definir',
           [Pt.act('Cobrar evidências','Evidências pedidas ao Atacado Bom Preço (laudo + fotos) · simulado, nenhuma mensagem real enviada · retorno só é autorizado com evidências.')]),
      caso('RC-13','PV-030 · 2/3','soja 25/26 · Coop Grão Sul','Umidade acima do padrão','L27-020','900 sc','laudo de umidade · 2 fotos','Retorno a caminho','yellow','a definir',
           [Pt.cta('Receber bloqueado','CO-04.dc.html')]),
      caso(CASO['id'],f'{CASO["pedido"]} · 2/2','mamão A · Rede Hortifrúti BA','Maturação avançada',CASO['lote'],f'{CASO["qtd_kg"]} kg','4 fotos · laudo do cliente',
           'Bloqueado · aguarda Qualidade','red','Crédito solicitado',[Pt.cta('Decidir destinação','CO-06.dc.html',True)]),
      caso('RC-11','PV-025 · 1/1','mamão A · Frutas Real','Avaria no transporte','L26-101','120 kg','fotos + canhoto','Encerrado · descarte','gray','Crédito emitido','—',ro=True),
    ]
    g_rc=grid(rc_cols,rcs,edit=dict(m='form',title='Caso',newTitle='Novo caso',
        sub='Vincule o caso à entrega e ao lote de origem. A decisão muda só pelos comandos da linha; reclamação não libera estoque.',
        fields=[dict(k='pedtx',l='Pedido · entrega',t='txt',req=True,help='Ex.: PV-030 · entrega 1 de 3'),
                dict(k='motivo',l='Motivo',t='sel',req=True,opts=MOT,**{'def':MOT[1]}),
                dict(k='lote',l='Lote',t='txt',req=True,help='Genealogia e clientes afetados são carregados pelo lote.'),
                dict(k='qtd',l='Quantidade',t='txt',req=True,help='Com unidade: ex.: 200 sc ou 0,4 t'),
                dict(k='evid',l='Evidências',t='txt',help='Laudos, fotos, comprovantes'),
                dict(k='trat',l='Tratamento financeiro',t='sel',opts=TRAT,**{'def':'a definir'})]),
        add=None,gid='g_rc',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_rc'||!r) return;
  if(isNew(r)){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; const id='RC-'+(15+n); r.v.__ok=1;
    r.p.rc=[{k:'b',t:id}]; r.s.rc=id; r.v.dect='Aberto'; r.p.acao=[{k:'mut',t:'cobre evidências para autorizar retorno'}];
    self.setState({g2toast:'Caso '+id+' aberto · lote '+r.v.lote+' e clientes afetados carregados pela genealogia.'}); }
  const sub=(r.p.ped&&r.p.ped[2])?r.p.ped[2].t:'entrega informada'; r.p.ped=[{k:'b',t:r.v.pedtx},{k:'br',t:''},{k:'mut',t:sub}]; r.s.ped=r.v.pedtx;
  r.p.lq=[{k:'txt',t:r.v.lote+' · '+r.v.qtd}]; r.s.lq=r.v.lote; r.p.motivo=[{k:'txt',t:r.v.motivo||''},{k:'br',t:''},{k:'mut',t:r.v.evid||'—'}]; r.s.motivo=r.v.motivo;
  const ch=(r.p.dec&&r.p.dec[0])?r.p.dec[0]:{k:'chip',t:r.v.dect||'Aberto',c:'yellow'}; r.p.dec=[ch,{k:'br',t:''},{k:'mut',t:'financeiro: '+(r.v.trat||'a definir')}]; r.s.dec=ch.t;
  self.setState({tick:Date.now()}); }; }
'''
    corpo=(
      section('Casos por entrega e lote','Trate cada caso pela ação da linha; clique na linha para completar motivo, evidências e tratamento financeiro.',
        [ic(btn('Emitir solicitação de crédito',small=True,href='GE-05.dc.html'),'cash','Abrir contas a receber para o crédito do caso (GE-05)'),
         ic(msgbtn('Encerrar caso',f'Bloqueado para {CASO["id"]}: falta destinação física do retorno bloqueado — decida a destinação na Qualidade; encerrar exige destinação física e tratamento financeiro.'),'check','Encerrar o caso selecionado')],
        g_rc)
      + section(f'Efeito no estoque · retorno do {CASO["id"]}','Mantenha o retorno bloqueado até a Qualidade decidir a destinação.','',
        nota(f'{CASO["qtd_kg"]} kg retornaram e foram recebidos como {B("bloqueados")}: o estoque vendável <b style="color:{RED};">não aumentou</b> e o lote {CASO["lote"]} '
             f'segue indisponível para reserva e expedição.'),state='yellow'))
    shell37('VE-06','Reclamações e devoluções',corpo,
      subtitle='Casos por entrega e lote, com retorno, destinação, crédito e ação corretiva.',
      status=(f'{CASO["id"]} aguarda destinação · RC-15 aberto hoje','yellow'),
      primary_html=f'<button type="button" onClick="{H("g_rc_new")}" style="{PRIM_ST}">Abrir caso</button>',steps=faixa(6),
      footer='Encerrar exige destinação física e financeira aplicável; item devolvido bloqueado não vira vendável até a Qualidade decidir (DEMO-08). '
             'O ajuste financeiro fica vinculado ao caso: crédito não é emitido pelo retorno em si. Recolhimento, se decidido, usa a genealogia do lote para listar clientes afetados.')
