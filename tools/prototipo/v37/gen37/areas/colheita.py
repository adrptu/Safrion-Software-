# -*- coding: utf-8 -*-
"""Colheita e pós-colheita (módulo OCULTO do menu, preservado) — processo sequencial por links:
CO-01 Preveja a colheita › CO-02 Programe as ordens (+ CO-02det OC-0510) › CO-03 Registre cargas › CO-04 Receba a produção
› CO-05 Beneficie (+ CO-05det OB-0110) › CO-06 Confira a qualidade (+ CO-06det INSP-88) › CO-07 Controle o estoque de produção.
Cenários: DEMO-06 (PV-031 12 t × 80% = 9,6 t A, falta 0,4 t), DEMO-07 (packing 12,0 = 9,6 + 1,8 + 0,6), DEMO-08 (retornos RC-12/RC-13),
DEMO-19 (OB-0104 encerrada · L27-013 bloqueado · INSP-88).

observacoes (dados locais coerentes com dados.py / dados2.py / comercial.py):
- OC/CARGAS/RECEB/OB continuam locais (não existem em dados/dados2). PREVISAO, PACKING e LOTE_BLOQ vêm de dados.py.
- OB-0110 tem uma única origem em todos os níveis: OC-0507 · T7 · S38 (encerrada, 12,0 t → lotes L38-115 a L38-118), e não a
  OC-0510 em andamento (9,3 t até 23/09, cargas CG-1205/1206/1207 → lotes L39-*). Lista CO-05, detalhe CO-05det e genealogia. A carga do café
  CG-1103 passa a criar o lote L27-022 (antes L27-020), porque L27-020 é o lote de soja do retorno RC-13 (PV-030 · 900 sc) em comercial.py.
- Retornos do DEMO-08 (de comercial.py): RC-12 · PV-027 · L26-118 · 300 kg recebido bloqueado (inspeção local INSP-93) e
  RC-13 · PV-030 · L27-020 · 900 sc a caminho (Receber bloqueado em CO-04). AM-3320 e INSP-93 são IDs locais novos.
- OB-0104 segue dados.ORDENS: Encerradas · selo Lote bloqueado · janela 15–18/09 · resp. Rui · lote L27-013.
"""
import json, re
from engine import (grid,table,section,kpis,chip,btn,tag,icon,esc,msgbtn,drawer_button,prazo,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAY,GRAYS,BTN_ST,EXTRAJS,_MINI)
import engine as E
from ui37 import shell37, steps_bar, continuity, HEIGHTS37, PARENT37
import dados as D
def _lmr_ext():   # data da extração do LMR (ANVISA) para a dica ⓘ do CO-06, a mesma que a tela mostrava (dd/mm/aaaa)
    import dados_carencia as _DC
    a=str(_DC._lmr().get('extraido','')).split('-'); return '/'.join(reversed(a)) if len(a)==3 else '—'

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
# ---------- faixa de etapas (processo sequencial por links) ----------
ETAPAS=[('Preveja a colheita','CO-01.dc.html',''),('Programe as ordens','CO-02.dc.html','OC-0514 impedida'),
        ('Registre cargas','CO-03.dc.html',''),('Receba a produção','CO-04.dc.html',''),('Beneficie','CO-05.dc.html',''),
        ('Confira a qualidade','CO-06.dc.html','L27-013 bloqueado'),('Controle o estoque de produção','CO-07.dc.html','')]
def faixa(i):
    return steps_bar([dict(t=t,href=h,why=w,tip=(t+(' · '+w if w else ''))) for t,h,w in ETAPAS],current=i)

# ---------- botões com ícone + rótulo + title ----------
def _ic(html,name,title):
    m=re.match(r'^(<(button|a)\b[^>]*?)>(.*)</(button|a)>$',html,re.S)
    return f'{m.group(1)} title="{esc(title)}"><span style="display: inline-flex; align-items: center; gap: 6px;">{icon(name,14)}{m.group(3)}</span></{m.group(4)}>'
def imsg(t,msg,ic,title,primary=False): return _ic(msgbtn(t,msg,primary=primary),ic,title)
def idrw(t,d,ic,title,primary=False): return _ic(drawer_button(t,d,primary=primary),ic,title)
def ilnk(t,href,ic,title): return _ic(btn(t,small=True,href=href),ic,title)
def sbtn(t,fn,ic,title,primary=False):
    return (f'<button type="button" onClick="{H(fn)}" title="{esc(title)}" style="{BTN_ST(primary,True)}">'
            f'<span style="display: inline-flex; align-items: center; gap: 6px;">{icon(ic,14)}{esc(t)}</span></button>')
def dact(t,d):
    """ação de linha que abre um painel lateral (drawer) sem abrir a edição da linha."""
    h=drawer_button(t,d); fn=re.search(r'onClick="\{\{\s*(\w+)\s*\}\}"',h).group(1)
    return {'k':'act','t':t,'fn':fn}
def sec(titulo,desc,acao,corpo,state='green'): return section(titulo,desc,acao,corpo,state)

# ---------- grade: colunas e linhas ----------
def C(k,l,**kw): d=dict(k=k,l=l); d.update(kw); return d
def R(id_,ro=False,o=None,**cells):
    """linha G2: string simples → v (editável/ordenável); HTML → partes ricas; lista → partes; número → v."""
    r={'id':id_,'v':{},'s':{},'p':{}}
    for k,val in cells.items():
        if isinstance(val,list): r['p'][k]=val; r['s'][k]=' '.join(p.get('t','') for p in val if p.get('k')!='br').strip()
        elif isinstance(val,str) and '<' in val:
            pl=E.cell_parts(val); r['p'][k]=pl; r['s'][k]=E._plain(pl)
        else: r['v'][k]=val
    if ro: r['ro']=True
    if o: r['o']=[x if isinstance(x,dict) else dict(t=x) for x in o]
    return r
def grid(cols,rows,**kw):
    """grade G2 com selos iniciais: coluna com chips={valor:cor} já nasce com o selo (o motor só aplica ao salvar)."""
    for c in cols:
        if c.get('chips'):
            for r in rows:
                val=r['v'].get(c['k'])
                if val in c['chips'] and c['k'] not in r['p']: r['p'][c['k']]=[Pt.chip(val,c['chips'][val])]
    return E.grid(cols,rows,**kw)
def ch(t,c='gray'): return Pt.chip(t,c)
def mut(t): return Pt.mut(t)
def b(t): return Pt.b(t)
def br(): return Pt.br()
nota=lambda txt:f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6;">{txt}</div>'
B=lambda t:f'<b style="color:{INK};">{t}</b>'
milhar=lambda n:f'{n:,}'.replace(',','.')
f_t=lambda v:f'{v:.1f} t'.replace('.',',')

# ---------- dados locais (coerentes com dados.py e comercial.py) ----------
OC=[  # OC-0510: cargas 2.960 + 3.210 + 3.130 kg = 9,3 t realizadas de 12,0 t previstas → saldo 2,7 t
 dict(id='OC-0510', origem='T7 · Mamão Formosa', janela='22–27/09', etapa='Em execução', prev='12,0 t', real='6,3 t hoje · 9,3 t acum.',
      saldo='2,7 t', equipe='Turma A (8) · 2 carretas', cargas='3', selo=('Parcial · dia 2 de 5','yellow')),
 dict(id='OC-0513', origem='T7 · Mamão Formosa', janela='29/09–04/10', etapa='Liberadas', prev='11,5 t', real='—',
      saldo='11,5 t', equipe='Turma A (8) · 2 carretas', cargas='—', selo=None),
 dict(id='OC-0508', origem='C1 · Café (repasse 25/26)', janela='15–20/09', etapa='Em conferência', prev='420 sc 60 kg', real='405 sc',
      saldo='15 sc', equipe='Turma B (12) · 1 colhedora', cargas='6', selo=('Divergência de carga','yellow')),
 dict(id='OC-0514', origem='P1 · Feijão', janela='30/09–02/10', etapa='A liberar', prev='95 ha', real='—',
      saldo='95 ha', equipe='a alocar', cargas='—', selo=('Impedida · excede 14 t/d','red')),
 dict(id='OC-0507', origem='T7 · Mamão Formosa (S38)', janela='15–20/09', etapa='Encerradas', prev='12,0 t', real='12,0 t',
      saldo='0', equipe='Turma A (8) · 2 carretas', cargas='4 conciliadas · lotes L38-115 a 118', selo=None),
 dict(id='OC-0501', origem='T3 · Milho', janela='01–08/09', etapa='Encerradas', prev='96 ha · 8.640 sc', real='96 ha · 8.612 sc',
      saldo='0', equipe='Colhedora CH-01', cargas='14 conciliadas', selo=None),
]
ETAPA_CH={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'}
CARGAS=[  # carga, horário, ordem·origem, veículo, bruto, tara, qualidade inicial, destino, romaneio, situação
 ('CG-1207','09:40','OC-0510 · T7 (mamão)','Carreta 03',4310,1180,'Classe A · calibre 9','Packing Sede','ROM-0791',('Chegada a confirmar','yellow')),
 ('CG-1206','07:55','OC-0510 · T7 (mamão)','Carreta 02',4390,1180,'Classe A/B · calibre 8–10','Packing Sede','ROM-0790',('Recebida','green')),
 ('CG-1205','06:30','OC-0510 · T7 Q1+Q2 (mamão)','Carreta 02',4140,1180,'Mistura Q1+Q2 · 60/40 estimada','Packing Sede','ROM-0789',('Recebida','green')),
 ('CG-1103','16:10','OC-0508 · C1 (café)','Caminhão 07',9140,5020,'Bica corrida · rend. 52%','Terreiro/armazém','ROM-0762',('Pesagem pendente','yellow')),
 ('CG-0988','11:20','OC-0501 · T3 (milho)','Caminhão 05',15980,6140,'Umidade 17,2% · impureza 1,1%','Silo 2 (secador)','ROM-0701',('Recebida','green')),
]
OB=[
 dict(id='OB-0110', rota='Packing frutas · v3', prod='Mamão Formosa', janela='23–24/09', etapa='Em execução',
      ent='12,0 t · OC-0507 (T7 · S38) · L38-115 a 118', saidas=f'{f_t(D.PACKING["saidaA"])} A · {f_t(D.PACKING["saidaB"])} B',
      proc='descarte 0,6 t · em processo 0,0 t', bal=('balanço 0,0 t · sem divergência','green'), qual=('Aguardando inspeção','yellow')),
 dict(id='OB-0106', rota='Secagem grãos · v2', prod='Milho 17,2% → 14%', janela='20–26/09', etapa='Em execução',
      ent='48,0 t úmidas · OC-0501 (T3)', saidas='39,1 t secas (base 14%)', proc='em processo 7,1 t · quebra 1,8 t', bal=('balanço 0,0 t · sem divergência','green'),
      qual=None),
 dict(id='OB-0104', rota='Café bica → beneficiado · v1', prod='Café', janela='15–18/09', etapa='Encerradas',
      ent='bica L27-018/019 · colheita C1 jul/26', saidas='3.690 sc 60 kg (L27-013)', proc='perdas 4,1%', bal=('balanço 0 · conciliado','green'),
      qual=('L27-013 bloqueado · INSP-88','red')),
 dict(id='OB-0112', rota='Packing frutas · v3', prod='Mamão Formosa', janela='29/09–04/10', etapa='A liberar',
      ent='a receber · OC-0513 (T7)', saidas='—', proc='—', bal=None, qual=None),
]
SOJA=dict(lote='Silo 1 · Soja 25/26', fisico=38420, reservado=3875, disponivel=34545)
MILHO=dict(fisico=8612, reservado=2000, disponivel=6612)
GRAOS_FIS=SOJA['fisico']+MILHO['fisico']            # 47.032 sc 50 kg
GRAOS_DISP=SOJA['disponivel']+MILHO['disponivel']   # 41.157 sc 50 kg
RC12=dict(id='RC-12',pedido='PV-027',lote='L26-118',kg=300,insp='INSP-93')
RC13=dict(id='RC-13',pedido='PV-030',lote='L27-020',sc=900)

# ---------- estado local dos detalhes (JS) ----------
JSBASE=f'''
function co_G(id){{ return GRIDS.find(g=>g.id===id); }}
function co_R(self,id){{ return g2rows(self,co_G(id)); }}
function co_nf(n,d){{ return Number(n||0).toLocaleString('pt-BR',{{minimumFractionDigits:d||0,maximumFractionDigits:d||0}}); }}
const CO_CHIP={{green:['{ACC}','{ACCS}'],yellow:['{YEL}','{YELS}'],red:['{RED}','{REDS}'],gray:['{GRAY}','{GRAYS}']}};
function co_chipst(c){{ const x=CO_CHIP[c]||CO_CHIP.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+x[0]+';background:'+x[1]+';'; }}
function co_dotst(c){{ const x=CO_CHIP[c]||CO_CHIP.gray; return 'width:6px;height:6px;border-radius:999px;background:'+x[0]+';'; }}
function co_steps(v,pre,cur){{ for(let i=1;i<=5;i++){{ const done=i<cur, now=i===cur;
  v[pre+i+'_dot']='width:22px;height:22px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;box-sizing:border-box;font-size:12px;font-weight:800;'+(done?'background:{ACC};color:#fff;':(now?'border:2px solid {ACC};background:#fff;color:{ACC};':'border:2px solid {LINE};background:#fff;color:transparent;'));
  v[pre+i+'_sym']=done?'✓':(now?'●':'');
  v[pre+i+'_tx']='display:flex;align-items:center;gap:8px;font-size:13px;white-space:nowrap;'+(now?'font-weight:800;color:{INK};':(done?'font-weight:600;color:{INK};':'font-weight:600;color:{MUTED};'));
  v[pre+i+'_ln']='flex-grow:1;height:2px;margin:0 10px;min-width:24px;background:'+(done?'{ACC}':'{LINE}')+';'; }} }}
'''
def dstepper(pre,hint_hole):
    nomes=['A liberar','Liberadas','Em execução','Em conferência','Encerradas']
    out=''
    for i,n in enumerate(nomes,1):
        out+=f'<div style="{H(pre+str(i)+"_tx")}"><span style="{H(pre+str(i)+"_dot")}">{H(pre+str(i)+"_sym")}</span>{esc(n)}</div>'
        if i<5: out+=f'<span style="{H(pre+str(i)+"_ln")}"></span>'
    return (f'<div style="display: flex; flex-direction: column; gap: 8px;"><div style="display: flex; align-items: center;">{out}</div>'
            f'<div style="font-size: 13.5px; color: {MUTED};">{H(hint_hole)}</div></div>')
def dyn_status(fname,hole):
    """troca o selo estático do cabeçalho por um selo com cor dinâmica ({{hole}} / {{hole_st}} / {{hole_dot}})."""
    p=f'{E.P}/{fname}'; s=open(p).read(); old=chip(H(hole),'green')
    assert old in s, 'selo dinâmico não encontrado'
    s=s.replace(old,f'<span style="{H(hole+"_st")}"><span style="{H(hole+"_dot")}"></span>{H(hole)}</span>',1)
    open(p,'w').write(s)
def dyn_primary(pre):
    return (f'<sc-if value="{H(pre+"_isbtn")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H(pre+"_fn")}" style="{BTN_ST(True)}">{H(pre+"_t")}</button></sc-if>'
            f'<sc-if value="{H(pre+"_islnk")}" hint-placeholder-val="{F()}"><a href="{H(pre+"_href")}" style="text-decoration: none; display: inline-block; {BTN_ST(True)}">{H(pre+"_t")}</a></sc-if>')

# =====================================================================================
def co01():
    fn='CO-01.dc.html'; HEIGHTS37[fn]=1000
    P=D.PREVISAO
    g_of=grid([C('parc',l='Parcela · cultura · área',w=140),C('ciclo',l='Ciclo / estádio',w=100),C('plantas',l='Plantas vivas',w=100),
               C('peso',l='Peso · curva',w=100),C('rp',l='Rend. comercial · perdas',w=120),C('faixa',l='Faixa prevista',w=150),C('dest',l='Destino',w=130),C('acao',l='Ação')],
      [R('T7',parc=[b('T7'),mut('Mamão Formosa · 42 ha')],ciclo='produção · sem. 39',plantas='11.980 (98,2%)',peso='1,45 kg/fruto · +2%',rend='80% classe A',perdas='5% campo',rp=[Pt.txt('80% classe A'),br(),mut('perdas '+'5% campo')],
         faixa='11,2 – 12,6 t (média 12,0) · S39',dest=[Pt.tag('PV-031 · classe A')],acao=[Pt.cta('Comparar pedidos','VE-01.dc.html')],just=''),
       R('C1',parc=[b('C1'),mut('Café · 38 ha')],ciclo='granação · safra 26/27',plantas='—',peso='—',rend='52% bica → beneficiado',perdas='—',rp=[Pt.txt('52% bica → beneficiado'),br(),mut('perdas '+'—')],
         faixa='1.050 – 1.200 sc 60 kg · mai–jul/27',dest=[Pt.tag('estoque')],acao=[Pt.cta('Coletar contagem','MB-07.dc.html')],just=''),
       R('P1',parc=[b('P1'),mut('Feijão · 95 ha')],ciclo='R5',plantas='—',peso='enchimento de grão',rend='—',perdas='—',rp=[Pt.txt('—'),br(),mut('perdas '+'—')],
         faixa='2.660 – 2.950 sc 50 kg · S40',dest=[Pt.tag('a definir')],acao=[Pt.cta('Programar colheita','CO-02.dc.html')],just=''),
       R('T3',ro=True,parc=[b('T3'),mut('Milho · 96 ha')],ciclo='colhido',plantas='—',peso='—',rend='realizado 8.612 sc',perdas='0,3%',rp=[Pt.txt('realizado 8.612 sc'),br(),mut('perdas '+'0,3%')],
         faixa=[ch('Realizado · fora da oferta','gray')],dest=[Pt.tag('Silo 2')],acao=[mut('—')])],
      edit=dict(m='form',title='Revisar previsão',sub='Salvar cria o rascunho v S39-03 sobre a v S39-02; publicar exige autorização. Parcela colhida abre em consulta.',
        fields=[dict(k='ciclo',l='Ciclo / estádio',t='txt',req=True),dict(k='plantas',l='Plantas vivas',t='txt'),dict(k='peso',l='Peso médio · curva',t='txt'),
                dict(k='rend',l='Rendimento comercial',t='txt'),dict(k='perdas',l='Perdas previstas',t='txt'),
                dict(k='faixa',l='Faixa prevista',t='txt',req=True,help='Mínimo – máximo, média e semana (ex.: 11,2 – 12,6 t (média 12,0) · S39)'),
                dict(k='just',l='Justificativa da revisão',t='area',help='Registre o motivo (ex.: chuva de 18 mm antecipou a maturação); ele acompanha o rascunho até a publicação.')]),
      gid='g_of',total=False)
    g_ped=grid([C('ped',l='Pedido'),C('pede',l='Cliente pede'),C('fut',l='Futuras em classe A'),C('falta',l='Falta'),C('sem',l='Semana'),C('sit',l='Situação')],
      [R('pv031',ped=[b(P['pedido'])],pede=f'{P["classeA_t"]:.1f} t classe A'.replace('.',','),fut=[b(f_t(P['futuras_A'])),mut('12,0 t × 80%')],
         falta=[ch(f'falta {P["falta"]:.1f} t'.replace('.',','),'red')],sem='S39',sit=[ch('Não prometer integralmente','yellow')],
         o=[f'Oferta bruta S39 · T7: {f_t(P["prev_bruta_t"])} (previsão v S39-02)',f'Rendimento classe A: {int(P["rendA"]*100)}% (curva de packing)',
            f'Futuras em classe A: 12,0 t × 80% = {f_t(P["futuras_A"])}',f'Pedido {P["pedido"]}: {f_t(P["classeA_t"])} → falta {f_t(P["falta"])}'])],
      edit=dict(m='origin',title='Pedido × oferta de classe A',fields=[dict(k='ped',l='Pedido',ro=True),dict(k='pede',l='Cliente pede',ro=True)]),
      search=False,gid='g_ped',total=False)
    g_wape=grid([C('ciclo',l='Ciclo'),C('ver',l='Versão congelada'),C('ant',l='Antecedência'),C('wape',l='WAPE'),C('vies',l='Viés'),C('am',l='Amostra'),C('meta',l='Meta')],
      [R('mam',ciclo='Mamão · semanal',ver='v S39-02 · 21/09',ant='7 d',wape=[ch('9,4%','yellow')],vies='+3,1%',am='18 pontos',meta=[Pt.txt('WAPE ≤ 8%'),ch('Hipótese · meta proposta','yellow')],
         o=['Σ |previsto − realizado| ÷ Σ realizado nas 6 últimas semanas do T7','Versão medida: v S39-02 (congelada em 21/09)']),
       R('mil',ciclo='Milho · safra',ver='v ago-26 · 01/08',ant='35 d',wape=[ch('4,2%','green')],vies='−0,8%',am='12 pontos',meta=[Pt.txt('WAPE ≤ 6%'),ch('Hipótese · meta proposta','yellow')],
         o=['Previsto 8.990 sc × realizado 8.612 sc (T3 · 96 ha)','Versão medida: v ago-26 (congelada em 01/08)'])],
      edit=dict(m='origin',title='Erro da previsão',fields=[dict(k='ciclo',l='Ciclo',ro=True),dict(k='ver',l='Versão congelada',ro=True)]),
      search=False,gid='g_wape',total=False)
    # TAB-07 (DS-MODULOS-2, 17/10/2026): sem cartões de resumo sobre a lista; o que pede atenção vai no selo do cabeçalho e o resto já está nas linhas
    corpo=(
      sec('Oferta semanal por parcela','Confira a faixa prevista por parcela; clique na linha para revisar a previsão em rascunho.',
        [ilnk('Coletar contagem','MB-07.dc.html','leaf','Coletar contagem de frutos no celular (observação, não publica)'),
         imsg('Publicar versão','Não publicada: você não tem autorização de publicação. A agrônoma responsável (Ana) recebe o rascunho v S39-03 para publicar · a v S39-02 segue vigente e congelada para medir erro.',
              'doc','Publicar a versão em rascunho (exige autorização)')],g_of)
      + sec('Pedido PV-031 × oferta de classe A','Compare o pedido com a oferta: 12,0 t brutas × 80% = 9,6 t em classe A.',
        [imsg('Renegociar saldo do pedido','Tratativa aberta no Comercial: renegociar 0,4 t do PV-031 ou alocar origem alternativa · nada foi prometido além de 9,6 t.',
              'cart','Abrir tratativa com o Comercial para o saldo sem oferta')],g_ped,state='yellow')
      + sec('Qualidade da previsão','Acompanhe o erro da versão congelada; clique na linha para ver como o erro foi calculado.',
        [idrw('Revisar amostragem',dict(title='Ação de melhoria da previsão',sub='WAPE acima do alvo proposto no mamão',
           fields=[('Responsável','Equipe agronomia · Bia'),('Prazo','30/09/2026'),('Escopo','ampliar amostra de 18 para 24 pontos em T7')],
           confirm='Criar ação com dono e prazo',done='Ação registrada · acompanhada em GE-02'),'lab','Criar ação de melhoria da amostragem com dono e prazo')],g_wape,state='gray'))
    EXTRAJS[0]=JSBASE+r'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid==='g_of'&&r){ r.p.rp=[{k:'txt',t:r.v.rend||'—'},{k:'br',t:''},{k:'mut',t:'perdas '+(r.v.perdas||'—')}]; r.s.rp=(r.v.rend||'')+' '+(r.v.perdas||''); } if(gid==='g_of'&&r) self.setState({g2toast:'Rascunho v S39-03 salvo para '+r.id+' · a v S39-02 segue vigente · publicar exige autorização'}); }; }
'''
    shell37('CO-01','Previsão e maturação',corpo,
      subtitle='Oferta semanal por ciclo, parcela, classe/calibre e destino — contagem é observação; publicar é responsabilidade autorizada.',
      status=('S39 publicada · falta 0,4 t no PV-031','yellow'),
      primary='Programar colheita',primary_href='CO-02.dc.html',steps=faixa(1),
      footer='Volume total não é duplicado em semanas sucessivas nem soma produtos como substitutos (DEMO-06 · AC-45).')

# =====================================================================================
def co02():
    fn='CO-02.dc.html'; HEIGHTS37[fn]=1000
    acao={'OC-0510':[Pt.cta('Registrar avanço','CO-02det.dc.html')],
          'OC-0513':[Pt.act('Iniciar ordem','OC-0513 iniciada · Em execução · equipe e carretas reservadas na janela 29/09–04/10.')],
          'OC-0508':[Pt.act('Conferir cargas','Conferência aberta: 6 cargas · 1 divergência (CG-1103 sem pesagem de destino) — encerrar só após conciliação.')],
          'OC-0514':[Pt.act('Liberar ordem','Não liberada: recebimento do packing excede 14 t/d em 01/10. Resolva movendo a frente para 02/10 ou reduzindo para 12 t/d e libere de novo.',u=True)],
          'OC-0507':[Pt.cta('Ver cargas','CO-03.dc.html')],
          'OC-0501':[Pt.cta('Ver cargas','CO-03.dc.html')]}
    rows=[]
    for o in OC:
        rows.append(R(o['id'],ro=(o['etapa']=='Encerradas'),
          id=([Pt.link(o['id'],'CO-02det.dc.html')] if o['id']=='OC-0510' else [b(o['id'])])+[br(),mut(o['origem'])],
          origem=o['origem'],janela=o['janela'],
          etapa=[ch(o['etapa'],ETAPA_CH[o['etapa']])]+([br(),ch(*o['selo'])] if o['selo'] else []),
          prev=o['prev'],real=o['real'],saldo=[b(o['saldo'])],equipe=o['equipe'],acao=acao[o['id']]))
    g_oc=grid([C('id',l='Ordem · origem',w=140),C('janela',l='Janela',w=90),C('etapa',l='Etapa · selo'),C('prev',l='Previsto',w=80),
               C('real',l='Realizado',w=90),C('saldo',l='Saldo',a='r'),C('equipe',l='Equipe',w=105),C('acao',l='Ação')],rows,
      edit=dict(m='form',title='Ordem de colheita',sub='Ajuste janela e equipe; a etapa avança só pelas ações da ordem. Ordem encerrada abre em consulta.',
        fields=[dict(k='origem',l='Origem',ro=True),dict(k='janela',l='Janela',t='txt',req=True,help='Ex.: 29/09–04/10'),
                dict(k='equipe',l='Equipe e máquinas',t='sel',req=True,opts=['Turma A (8) · 2 carretas','Turma B (12) · 1 colhedora','Colhedora CH-01','a alocar']),
                dict(k='prev',l='Previsto',ro=True,help='Vem da previsão publicada (CO-01).')]),
      gid='g_oc',total=False)
    # TAB-07 (DS-MODULOS-2, 17/10/2026): sem cartões de resumo sobre a lista; o que pede atenção vai no selo do cabeçalho e o resto já está nas linhas
    corpo=(
      sec('Ordens de colheita do período','Prepare e libere as ordens; clique na linha para ajustar janela e equipe.',
        [idrw('Preparar ordens do período',dict(title='Preparar ordens · semana 40',sub='deriva da previsão publicada e reserva recursos compartilhados',
           fields=[('Período','29/09 – 04/10'),('Origem da demanda','Previsão S40 + pedido PV-031'),('Equipe','Turma A (8)'),('Máquinas','2 carretas · 1 empilhadeira'),
                   ('Capacidade de recebimento','14 t/dia · packing Sede')],
           confirm='Emitir ordens em A liberar',done='2 ordens emitidas em A liberar · liberação é ação separada'),'calendar','Derivar as ordens da semana 40 da previsão publicada',primary=True),
         imsg('Liberar ordens prontas','0 de 1 liberada · OC-0514: recebimento excede 14 t/d em 01/10 — mova para 02/10 ou reduza a frente. Resultado por item.',
              'check','Liberar as ordens em A liberar que têm recursos e capacidade')],g_oc))
    shell37('CO-02','Programação e ordens de colheita',corpo,
      subtitle='Recorte da agenda integrada com maturação, pedido, equipe, embalagem, packing e transporte — capacidade em unidades compatíveis.',
      status=('Janela 22–27/09 · 1 impedida · 1 em conferência','yellow'),steps=faixa(2),
      footer='Ciclo canônico: A liberar → Liberadas → Em execução → Em conferência → Encerradas. Finalizar turno mantém Em execução; término físico entra em Em conferência. '
             'Avanço × carga: área e horas vão no avanço e o peso na carga, sem misturar unidades. Hectares concluídos não geram quilogramas de estoque, e pesagens não duplicam a produção da mesma carga '
             '(ex.: avanço de 30 ha numa ordem de 100 ha fica como 30 ha realizados e 70 ha de saldo; a pesagem é conciliada depois, sem impedir o registro do turno).')

# =====================================================================================
def co02det():
    fn='CO-02det.dc.html'; HEIGHTS37[fn]=1000; PARENT37[fn]='CO-02.dc.html'
    g_ap=grid([C('dia',l='Dia'),C('q',l='Quantidade',t='num',a='r',u='t',d=1,agg='sum'),C('horas',l='Horas de equipe'),C('cargas',l='Cargas do dia',w=240),
               C('sit',l='Situação',chips={'Conferido':'green','Aberto':'yellow','Travado para conferência':'gray'})],
      [R('d1',ro=True,dia='22/09',q=3.0,horas='8 × 7,0 h',cargas='CG-1205 (2.960 kg)',sit='Conferido',obs=''),
       R('d2',dia='23/09 (hoje)',q=6.3,horas='8 × 6,5 h',cargas='CG-1206 · CG-1207 (6.340 kg)',sit='Aberto',obs='')],
      edit=dict(m='form',title='Avanço do turno · OC-0510',newTitle='Registrar avanço do turno · OC-0510',
        sub='Quantidade e horas do turno; a pesagem é vinculada depois. Dia conferido abre em consulta.',
        fields=[dict(k='dia',l='Dia',t='txt',req=True,**{'def':'24/09'}),dict(k='q',l='Quantidade colhida',t='num',u='t',req=True,min=0,max=14,help='Capacidade de recebimento do packing: 14 t/d'),
                dict(k='horas',l='Horas de equipe',t='txt',req=True,**{'def':'8 × 3,0 h'}),dict(k='obs',l='Observação',t='area')]),
      gid='g_ap',total=True)
    g_cv=grid([C('carga',l='Carga'),C('liq',l='Líquido',t='num',a='r',u='kg'),C('qual',l='Qualidade inicial',w=240),C('dest',l='Destino'),C('vinc',l='Vínculo')],
      [R('CG-1205',carga=[Pt.link('CG-1205','CO-03.dc.html')],liq=2960,qual='mistura Q1+Q2 · 60/40 estimada',dest='Packing Sede',vinc=[ch('Conciliada','green')]),
       R('CG-1206',carga=[Pt.link('CG-1206','CO-03.dc.html')],liq=3210,qual='classe A/B · calibre 8–10',dest='Packing Sede',vinc=[ch('Conciliada','green')]),
       R('CG-1207',carga=[Pt.link('CG-1207','CO-03.dc.html')],liq=3130,qual='classe A · calibre 9',dest='Packing Sede',vinc=[ch('Aguardando recebimento','yellow')])],
      edit=dict(m='ro',title='Carga vinculada',sub='A carga é corrigida em Registre cargas (CO-03); aqui só se consulta o vínculo.',
        fields=[dict(k='carga',l='Carga',ro=True),dict(k='liq',l='Líquido',t='num',u='kg',ro=True),dict(k='qual',l='Qualidade inicial',ro=True),dict(k='dest',l='Destino',ro=True)]),
      search=False,gid='g_cv',total=False)
    corpo=(
      continuity('CO-01 · previsão S39 publicada',H('c2_aqui'),H('c2_falta'),H('c2_prox'))
      + dstepper('c2s','c2_hint')
      + sec('Apontamentos por dia','Registre o avanço de cada turno; clique no dia aberto para corrigir.',
        [f'<sc-if value="{H("c2_exec")}" hint-placeholder-val="{T()}">'
         + E.recolhe_acoes('Apontamentos por dia',[sbtn('Finalizar apontamento do turno','c2_fin','clock','Trava os apontamentos do turno; a ordem continua Em execução'),
           sbtn('Concluir execução','c2_concl','check','Registra o término físico; a ordem entra em Em conferência')])+'</sc-if>'],g_ap)
      + sec('Cargas vinculadas','Confira o vínculo de cada carga; dois tickets da mesma carga não duplicam produção.',
        [ilnk('Registrar carga','CO-03.dc.html','truck','Registrar pesagem e romaneio em Registre cargas')],g_cv,state='gray'))
    EXTRAJS[0]=JSBASE+r'''
function PREVALS(self,v){ const f=self.state.c2f||'exec'; co_R(self,'g_ap').forEach(r=>{ if(f!=='exec'){ r.ro=true; if(r.v.sit==='Aberto'){ r.v.sit='Travado para conferência'; r.s.sit=r.v.sit; r.p.sit=[{k:'chip',t:r.v.sit,c:'gray'}]; } } }); }
function EXTRAVALS(self,v){ const st=self.state; const f=st.c2f||'exec';
  const acum=co_R(self,'g_ap').reduce((s,r)=>s+(Number(r.v.q)||0),0); const saldo=Math.max(0,12-acum);
  v.c2_exec=(f==='exec');
  v.c2_aqui = f==='exec'? 'Em execução · dia 2 de 5' : 'Em conferência';
  v.c2_falta= 'saldo '+co_nf(saldo,1)+' t · conciliar CG-1207';
  const sel = f==='exec'? ['Em execução · parcial dia 2 de 5','yellow'] : (st.c2c? ['Em conferência · CG-1207 a conciliar','yellow'] : ['Em conferência · cargas a conferir','yellow']);
  v.c2_selo=sel[0]; v.c2_selo_st=co_chipst(sel[1]); v.c2_selo_dot=co_dotst(sel[1]);
  co_steps(v,'c2s',f==='exec'?3:4);
  v.c2_hint = f==='exec'? '' : 'Em conferência: concilie as cargas com os apontamentos antes de encerrar.';   /* 14/10/2026: a regra da execução foi para a dica ⓘ */
  if(f==='exec'){ v.c2p_t='Registrar avanço'; v.c2p_fn=v.g_ap_new; v.c2p_isbtn=true; v.c2p_islnk=false; v.c2_prox='Registrar avanço do turno'; }
  else if(!st.c2c){ v.c2p_t='Conferir cargas'; v.c2p_isbtn=true; v.c2p_islnk=false; v.c2_prox='Conferir cargas';
    v.c2p_fn=()=>self.setState({c2c:true,g2toast:'Conferência: 2 de 3 cargas conciliadas (CG-1205, CG-1206) · CG-1207 aguarda recebimento — encerrar só após conciliação.'}); }
  else { v.c2p_t='Receber a CG-1207'; v.c2p_href='CO-04.dc.html'; v.c2p_isbtn=false; v.c2p_islnk=true; v.c2_prox='Receber a CG-1207'; }
  v.c2_fin=()=>self.setState({g2toast:'Turno finalizado · ordem PERMANECE Em execução · apontamentos do dia travados para conferência.'});
  v.c2_concl=()=>self.setState({c2f:'conf',g2toast:'Término físico registrado · OC-0510 entra em Em conferência — ainda não está encerrada · saldo de '+co_nf(saldo,1)+' t fica registrado para justificar.'});
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_ap'||!r) return; if(!r.v.sit){ r.v.sit='Aberto'; r.s.sit='Aberto'; r.p.sit=[{k:'chip',t:'Aberto',c:'yellow'}]; r.v.cargas=r.v.cargas||'pesagem a vincular'; }
    const ac=rows.reduce((s,x)=>s+(Number(x.v.q)||0),0); self.setState({g2toast:'Avanço registrado na mesma ordem · acumulado '+co_nf(ac,1)+' t · saldo '+co_nf(Math.max(0,12-ac),1)+' t · pesagem vinculada depois'}); }; }
'''
    shell37('CO-02','OC-0510 · Colheita de mamão T7',corpo,fname=fn,crumbs_extra=['OC-0510'],
      subtitle='Área executada não gera massa fictícia; pesagem não confirma área — os dois fatos convivem na mesma ordem e são conciliados.',
      status=(H('c2_selo'),'green'),primary_html=dyn_primary('c2p'),steps=faixa(2),
      footer='Qualidade do lote permanece separada da execução: classe/calibre definitivos saem do packing (CO-05) e da inspeção (CO-06). '
             'Término físico entra automaticamente em Em conferência; encerrar exige cargas e apontamentos conciliados.')
    dyn_status(fn,'c2_selo')

# =====================================================================================
def co03():
    fn='CO-03.dc.html'; HEIGHTS37[fn]=1000
    rows=[]
    for c,hor,os_,vei,bru,tar,qual,dest,doc,sit in CARGAS:
        a=([Pt.cta('Confirmar chegada','CO-04.dc.html')] if c=='CG-1207' else
           [Pt.act('Vincular pesagem','Pesagem de destino vinculada ao MESMO ticket da CG-1103 · líquido recalculado · produção não duplicada.')] if c=='CG-1103' else
           [Pt.act('Emitir romaneio',f'Romaneio {doc} emitido de novo · documento vinculado à carga e à ordem.')])
        rows.append(R(c,ro=(c!='CG-1207'),carga=[b(c),br(),mut(f'{hor} · {vei}')],hora=hor,os=os_,veic=vei,bru=bru,tar=tar,bt=[Pt.txt(f'{milhar(bru)} − {milhar(tar)}')],liq=bru-tar,qual=qual,dest=dest,rom=doc,
                      sit=[ch(sit[0],sit[1]),br(),mut(doc)],acao=a))
    g_cg=grid([C('carga',l='Carga · hora · veículo',w=120),C('os',l='Ordem · origem',w=100),C('bt',l='Bruto − tara (kg)',a='r'),
               C('liq',l='Líquido',t='num',a='r',u='kg'),C('qual',l='Qualidade inicial',w=100),C('dest',l='Destino',w=90),
               C('sit',l='Situação · romaneio'),C('acao',l='Ação')],rows,
      edit=dict(m='form',title='Carga',newTitle='Registrar carga',sub='Líquido = bruto − tara. Carga já recebida abre em consulta; corrija-a pelo recebimento (CO-04).',
        fields=[dict(k='os',l='Ordem · origem',t='sel',req=True,opts=['OC-0510 · T7 (mamão)','OC-0508 · C1 (café)','OC-0513 · T7 (mamão)'],**{'def':'OC-0510 · T7 (mamão)'}),
                dict(k='veic',l='Veículo',t='sel',req=True,opts=['Carreta 02','Carreta 03','Caminhão 05','Caminhão 07'],**{'def':'Carreta 03'}),
                dict(k='bru',l='Peso bruto',t='num',u='kg',req=True,min=1),dict(k='tar',l='Tara',t='num',u='kg',req=True,min=0),
                dict(k='liq',l='Líquido',t='num',u='kg',ro=True,help='Calculado ao salvar.'),
                dict(k='qual',l='Qualidade inicial',t='txt',req=True,help='Frutas: classe/calibre · grãos: umidade/impureza · café: bica e rendimento'),
                dict(k='dest',l='Destino',t='sel',req=True,opts=['Packing Sede','Terreiro/armazém','Silo 2 (secador)'],**{'def':'Packing Sede'})],
        calc=[dict(k='liq',op='sub',a=['bru','tar'])]),
      sel=False,gid='g_cg',total=True,so={'k':'carga','d':True})
    corpo=(
      sec('Cargas do período','Registre pesagem e romaneio de cada carga; clique na carga a confirmar para corrigir.',
        [sbtn('Registrar carga','g_cg_new','truck','Registrar nova carga com pesagem e romaneio',primary=True),
         ilnk('Registrar no celular','MB-10.dc.html','lista','Registrar a carga no celular, na balança ou no campo')],g_cg)
      + sec('Qualidade inicial por cultura','Informe a qualidade inicial no padrão da cultura da carga.','',
        nota(f'CG-0988 (milho) carrega {B("umidade 17,2% e impureza 1,1%")}; CG-1206/1207 (mamão) carregam {B("classe e calibre")}; '
             f'CG-1103 (café) carrega {B("bica corrida e rendimento 52%")}. A mistura Q1+Q2 da CG-1205 mantém rastreio com participação {B("estimada 60/40")}.'),state='gray'))
    EXTRAJS[0]=JSBASE+'const CO3_ACT='+json.dumps([Pt.cta('Confirmar chegada','CO-04.dc.html')],ensure_ascii=False)+';\n'+r'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_cg'||!r) return;
  r.p.bt=[{k:'txt',t:co_nf(r.v.bru)+' − '+co_nf(r.v.tar)}]; r.s.bt=r.p.bt[0].t;
  if(r.p.carga) r.p.carga=[r.p.carga[0],{k:'br',t:''},{k:'mut',t:(r.v.hora||'')+' · '+r.v.veic}];
  if(!r.v.rom){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; const id='CG-'+(1207+n); r.v.rom='ROM-0'+(791+n);
    const d=new Date(); r.v.hora=String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');
    r.p.carga=[{k:'b',t:id},{k:'br',t:''},{k:'mut',t:r.v.hora+' · '+r.v.veic}]; r.s.carga=id;
    r.p.sit=[{k:'chip',t:'Chegada a confirmar',c:'yellow'},{k:'br',t:''},{k:'mut',t:r.v.rom}]; r.s.sit='Chegada a confirmar '+r.v.rom; r.p.acao=CO3_ACT;
    self.setState({g2toast:'Carga '+id+' registrada · líquido '+co_nf(r.v.liq)+' kg · romaneio '+r.v.rom+' emitido'}); }
  else self.setState({g2toast:'Carga '+r.id+' corrigida · líquido '+co_nf(r.v.liq)+' kg · a produção não é duplicada'}); }; }
'''
    shell37('CO-03','Cargas, pesagens e romaneios',corpo,
      subtitle='Dois tickets da mesma carga não duplicam produção; toda carga fica atribuída à parcela de origem.',
      status=('1 chegada a confirmar · 1 pesagem pendente','yellow'),steps=faixa(3),
      footer='Confirmar chegada abre o recebimento (CO-04) preservando carga, qualidade inicial e documento.')

# =====================================================================================
def co04():
    fn='CO-04.dc.html'; HEIGHTS37[fn]=1000
    COND={'Íntegra':'green','Avaria térmica parcial':'yellow','Grão úmido 17,2%':'yellow','Bloqueado':'red'}
    rows=[
     R('RC-13',ent=[b(RC13['id']),br(),mut(f'retorno {RC13["pedido"]} · a caminho')],peso=f'{RC13["sc"]} sc previstos',local='Armazém Sede · área de bloqueio',cond='Bloqueado',
       am='a coletar',div='—',lote=f'{RC13["lote"]} · soja (retorno)',
       acao=[Pt.act('Receber bloqueado',f'{RC13["id"]} recebido bloqueado · {RC13["lote"]} ({RC13["sc"]} sc) em área segregada · estoque vendável não aumenta · inspeção de umidade aberta na qualidade (CO-06).',u=True)]),
     R('CG-1207',ent=[b('CG-1207'),br(),mut('OC-0510 · T7')],peso='3.130 kg',local='Packing Sede',cond='Avaria térmica parcial',am='AM-3315 coletada',div='—',lote='pendente · segregar',
       acao=[Pt.act('Segregar carga','CG-1207 segregada em área identificada · lote provisório L39-119Q criado · inspeção solicitada.',u=True)]),
     R('CG-1206',ent=[b('CG-1206'),br(),mut('OC-0510 · T7')],peso='3.180 kg',local='Packing Sede',cond='Íntegra',am='AM-3312 coletada',div='−30 kg (0,9% · na tolerância)',lote='L39-118 · mamão',
       acao=[Pt.act('Conferir carga','Carga CG-1206 conferida · peso recebido substitui a estimativa pela regra de medição, sem duplicação.')]),
     R('CG-1103',ent=[b('CG-1103'),br(),mut('OC-0508 · C1')],peso='4.120 kg',local='Terreiro/armazém',cond='Íntegra',am='AM-3288 coletada',div='—',lote='L27-022 · café bica',
       acao=[Pt.cta('Solicitar inspeção','CO-06.dc.html')]),
     R('CG-0988',ro=True,ent=[b('CG-0988'),br(),mut('OC-0501 · T3')],peso='9.840 kg',local='Silo 2 (secador)',cond='Grão úmido 17,2%',am='AM-3140 coletada',div='—',lote='em processo · OB-0106',
       acao=[Pt.cta('Encaminhar processo','CO-05.dc.html')]),
     R('RC-12',ro=True,ent=[b(RC12['id']),br(),mut(f'retorno {RC12["pedido"]} · recebido')],peso=f'{RC12["kg"]} kg',local='Packing Sede · área de bloqueio',cond='Bloqueado',
       am='AM-3320 coletada',div='—',lote=f'{RC12["lote"]} · mamão (retorno)',acao=[Pt.cta('Abrir inspeção','CO-06.dc.html')]),
    ]
    g_rc=grid([C('ent',l='Entrada · origem',w=140),C('peso',l='Peso recebido',w=90),C('local',l='Local',w=120),C('cond',l='Condição',chips=COND),
               C('am',l='Amostra',w=80),C('div',l='Divergência',w=110),C('lote',l='Lote criado',w=110),C('acao',l='Ação')],rows,
      edit=dict(m='form',title='Recebimento',sub='Registre condição, amostra e divergência na própria entrada. Entrada já encaminhada abre em consulta.',
        fields=[dict(k='peso',l='Peso recebido',t='txt',req=True),dict(k='local',l='Local',t='sel',req=True,opts=['Packing Sede','Packing Sede · área de bloqueio','Terreiro/armazém','Silo 2 (secador)','Armazém Sede · área de bloqueio']),
                dict(k='cond',l='Condição',t='sel',req=True,opts=list(COND)),dict(k='am',l='Amostra',t='txt'),
                dict(k='div',l='Divergência',t='txt',help='Ex.: −30 kg (0,9% · na tolerância). A trilha fica vinculada à carga e ao documento.'),
                dict(k='lote',l='Lote criado',ro=True)]),
      gid='g_rc',total=False)
    corpo=(
      sec('Cargas e retornos recebidos','Confira cada entrada, trate a divergência na linha e segregue o que não pode seguir.','',g_rc)
      )
    shell37('CO-04','Recebimento da produção',corpo,
      subtitle='Confira cargas e retornos — entrada NÃO equivale a liberação comercial; divergência é tratada na origem e o destino provisório fica rastreável.',
      status=('1 carga a segregar · 1 retorno a receber bloqueado','yellow'),steps=faixa(4),
      footer='Encaminhar processo abre o beneficiamento (CO-05); solicitar inspeção abre a qualidade (CO-06) — sempre preservando a carga de origem. '
             'A entrada não equivale a liberação comercial: produto em processo continua identificado (CG-0988 segue no secador como OB-0106) e retorno de cliente entra bloqueado até a decisão da qualidade (CO-06). '
             'A quantidade recebida substitui a estimativa conforme a regra de medição, nunca soma com ela.')

# =====================================================================================
def co05():
    fn='CO-05.dc.html'; HEIGHTS37[fn]=1000
    acao={'OB-0110':[Pt.cta('Registrar saídas','CO-05det.dc.html')],
          'OB-0106':[Pt.act('Registrar avanço','Turno registrado: +6,2 t secas base 14% · quebra de secagem apropriada · em processo recalculado · ordem segue Em execução.')],
          'OB-0104':[Pt.cta('Ver lote','CO-06det.dc.html')],
          'OB-0112':[Pt.act('Liberar ordem','Rota Packing frutas v3 autorizada · OB-0112 Liberada — início só com lotes de entrada recebidos (OC-0513).')]}
    rows=[]
    for o in OB:
        rows.append(R(o['id'],ro=(o['etapa']=='Encerradas'),
          id=([Pt.link(o['id'],'CO-05det.dc.html')] if o['id']=='OB-0110' else [b(o['id'])])+[br(),mut(o['prod']+' · '+o['rota'])],
          rota=o['rota'],prod=o['prod'],janela=o['janela'],etapa=o['etapa'],ent=o['ent'],saidas=o['saidas'],
          proc=[Pt.txt(o['saidas']+(' · '+o['proc'] if o['proc']!='—' else ''))]+([br(),ch(*o['bal'])] if o['bal'] else [])+([br(),ch(*o['qual'])] if o['qual'] else []),acao=acao[o['id']]))
    g_ob=grid([C('id',l='Ordem · produto · rota',w=170),C('janela',l='Janela',w=90),C('etapa',l='Etapa',chips=ETAPA_CH),
               C('ent',l='Lotes de entrada · origem',w=150),C('proc',l='Saídas · balanço · qualidade do lote',w=250),
               C('acao',l='Ação')],rows,
      edit=dict(m='form',title='Ordem de processo',newTitle='Criar ordem de processo',
        sub='Ajuste rota, janela e lotes de entrada; a etapa avança só pelas ações da ordem. Ordem encerrada abre em consulta.',
        fields=[dict(k='rota',l='Rota',t='sel',req=True,opts=['Packing frutas · v3','Secagem grãos · v2','Café bica → beneficiado · v1'],**{'def':'Packing frutas · v3'}),
                dict(k='prod',l='Produto',t='sel',req=True,opts=['Mamão Formosa','Milho 17,2% → 14%','Café'],**{'def':'Mamão Formosa'}),
                dict(k='janela',l='Janela',t='txt',req=True,**{'def':'29/09–04/10'}),
                dict(k='ent',l='Lotes de entrada · origem',t='txt',req=True,**{'def':'a receber · OC-0513 (T7)'}),
                dict(k='saidas',l='Saídas por classe',ro=True,help='Registradas no detalhe da ordem.')]),
      gid='g_ob',total=False)
    lib=Pt.act('Autorizar rota','Rota autorizada · ordem Liberada — início só com lotes de entrada recebidos.')
    corpo=(
      sec('Ordens de processo','Acompanhe cada ordem pela rota da cultura; clique na linha para ajustar rota e janela.',
        [sbtn('Criar ordem de processo','g_ob_new','layers','Criar ordem de processo em A liberar (deriva do PCP)',primary=True)],g_ob)
      + sec('Encerrada ≠ liberada','Encerre o processo pelo balanço; libere o lote só pela qualidade.','',
        nota(f'{B("OB-0104")} fechou com balanço conciliado e perdas de 4,1%, e foi Encerrada. '
             f'O lote {B("L27-013 (3.690 sc 60 kg)")} segue <b style="color:{RED};">Bloqueado</b> pela inspeção INSP-88 — indisponível para reserva e expedição em CO-07 até a decisão da qualidade.'),state='yellow'))
    EXTRAJS[0]=JSBASE+'const CO5_ACT='+json.dumps([lib],ensure_ascii=False)+';\n'+r'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_ob'||!r) return;
  const sub={k:'mut',t:r.v.prod+' · '+r.v.rota};
  if(r.v.id && r.p.id){ r.p.id=[r.p.id[0],{k:'br',t:''},sub]; self.setState({g2toast:'Salvo · '+r.v.id+' · rota e janela atualizadas; a etapa segue pelas ações da ordem'}); }
  if(!r.v.id){ const id='OB-0'+(113+rows.length-5); r.v.id=id; r.p.id=[{k:'b',t:id},{k:'br',t:''},sub]; r.s.id=id; r.v.etapa='A liberar'; r.s.etapa='A liberar'; r.p.etapa=[{k:'chip',t:'A liberar',c:'gray'}];
    r.v.saidas='—'; r.p.proc=[{k:'mut',t:'—'}]; r.p.acao=CO5_ACT;
    self.setState({g2toast:id+' criada em A liberar · autorizar a rota é ação separada'}); } }; }
'''
    shell37('CO-05','Beneficiamento',corpo,
      subtitle='Ordens de processo e lotes com múltiplas entradas/saídas; genealogia permanece após mistura e divisão.',
      status=('1 lote bloqueado após encerramento','yellow'),steps=faixa(5),
      footer='Ciclo canônico das ordens de processo; sem liberação automática de lote por balanço fechado — qualidade decide em CO-06 (DEMO-19). Fechar processo não libera lote; decisão posterior de qualidade não reabre a ordem encerrada.')

# =====================================================================================
def co05det():
    fn='CO-05det.dc.html'; HEIGHTS37[fn]=1000; PARENT37[fn]='CO-05.dc.html'
    PK=D.PACKING
    g_bal=grid([C('fluxo',l='Fluxo'),C('q',l='Quantidade',t='num',a='r',u='t',d=1),C('classe',l='Classe / destino',w=260),C('lote',l='Lote'),
                C('sit',l='Situação',chips={'Recebida':'green','Aguardando inspeção':'yellow','Registrado':'gray'})],
      [R('ent',fluxo='Entrada',q=PK['entrada'],classe='mamão de campo (L38-115 a L38-118)',lote='origem OC-0507 · T7 (S38)',sit='Recebida'),
       R('sa',fluxo='Saída A',q=PK['saidaA'],classe='classe A · calibre 8–10 · caixa 10 kg',lote='L39-120',sit='Aguardando inspeção'),
       R('sb',fluxo='Saída B',q=PK['saidaB'],classe='classe B · caixa 15 kg',lote='L39-121',sit='Aguardando inspeção'),
       R('desc',fluxo='Descarte',q=PK['descarte'],classe='compostagem · perda de packing',lote='—',sit='Registrado')],
      edit=dict(m='form',title='Saída do packing · OB-0110',sub='Corrija a quantidade da saída; o balanço é recalculado. A entrada vem do recebimento (CO-04) e abre em consulta.',
        fields=[dict(k='fluxo',l='Fluxo',ro=True),dict(k='q',l='Quantidade',t='num',u='t',req=True,min=0,max=12),dict(k='classe',l='Classe / destino',t='txt',req=True),
                dict(k='lote',l='Lote de destino',ro=True)]),
      search=False,gid='g_bal',total=False)
    corpo=(
      continuity('CO-04 · lotes L38-115 a L38-118 · OC-0507 (S38)',H('c5_aqui'),H('c5_falta'),H('c5_prox'))
      + dstepper('c5s','c5_hint')
      + sec('Balanço de materiais','Confira a entrada contra as saídas por classe e o descarte — embalagem controlada em separado.',
        [f'<sc-if value="{H("c5_exec")}" hint-placeholder-val="{T()}">'
         + E.recolhe_acoes('Balanço de materiais',[sbtn('Finalizar apontamento do turno','c5_fin','clock','Trava os apontamentos do turno; a ordem continua Em execução'),
           sbtn('Conferir balanço','c5_confb','scale','Conferir entrada contra saídas (disponível em Em conferência)')])+'</sc-if>'],
        g_bal+f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 4px 0; font-size: 13px;"><b>{H("c5_bal")}</b>'
              f'<span style="{H("c5_div_st")}"><span style="{H("c5_div_dot")}"></span>{H("c5_div")}</span></div>')
      + sec('Genealogia do lote','Rastreie do cliente ao lote de origem; mistura e divisão preservam a árvore.','',
        f'<div style="font-size: 13px; line-height: 1.8; color: {MUTED};">'
        f'{B("OC-0507 (T7 · S38, encerrada)")} → lotes de campo {B("L38-115 a L38-118")} (12,0 t recebidos em CO-04) → '
        f'packing OB-0110 → {B("L39-120 (9,6 t A)")} · {B("L39-121 (1,8 t B)")} → pedido PV-031 / estoque CO-07</div>',state='gray')
      + sec('Qualidade separada da produção','Encaminhe os lotes de saída à inspeção; encaminhar não libera o lote.',
        [ilnk('Encaminhar qualidade','CO-06.dc.html','lab','Abrir a inspeção dos lotes L39-120/121 na qualidade')],
        nota(f'L39-120/121 seguem {B("Aguardando inspeção")} até a decisão em CO-06, mesmo com o processo encerrado.'),state='gray'))
    EXTRAJS[0]=JSBASE+r'''
function co5_bal(self){ const rows=co_R(self,'g_bal'); const q=id=>Number((rows.find(r=>r.id===id)||{v:{}}).v.q)||0;
  const b={e:q('ent'),a:q('sa'),b:q('sb'),d:q('desc')}; b.div=Math.round((b.e-b.a-b.b-b.d)*100)/100; b.ok=Math.abs(b.div)<0.05;
  b.eq=co_nf(b.e,1)+' = '+co_nf(b.a,1)+' + '+co_nf(b.b,1)+' + '+co_nf(b.d,1); return b; }
function PREVALS(self,v){ const f=self.state.c5f||'exec'; co_R(self,'g_bal').forEach(r=>{ r.ro=(r.id==='ent')||f==='enc'; }); }
function EXTRAVALS(self,v){ const st=self.state; const f=st.c5f||'exec'; const bl=co5_bal(self); const ok=bl.ok, cf=!!st.c5c;
  v.c5_exec=(f==='exec');
  v.c5_bal='Balanço: '+bl.eq+' t';
  const dv= ok? ['divergência 0,0 t','green'] : ['divergência '+co_nf(Math.abs(bl.div),1)+' t','red']; v.c5_div=dv[0]; v.c5_div_st=co_chipst(dv[1]); v.c5_div_dot=co_dotst(dv[1]);
  let sel;
  if(f==='exec') sel= ok? ['Em execução · balanço sem divergência','green'] : ['Em execução · divergência de '+co_nf(Math.abs(bl.div),1)+' t','red'];
  else if(f==='conf') sel= cf? ['Em conferência · balanço conferido','green'] : ['Em conferência · balanço a conferir','yellow'];
  else sel=['Encerrada · lotes Aguardando inspeção','gray'];
  v.c5_selo=sel[0]; v.c5_selo_st=co_chipst(sel[1]); v.c5_selo_dot=co_dotst(sel[1]);
  co_steps(v,'c5s', f==='exec'?3:(f==='conf'?4:6));
  v.c5_aqui= f==='exec'? 'Em execução · packing' : (f==='conf'? 'Em conferência' : 'Encerrada');
  v.c5_falta= f==='enc'? 'inspeção dos lotes L39-120/121' : (f==='conf'&&cf? 'fechar processo · inspeção dos lotes' : 'conferir balanço · inspeção dos lotes');
  v.c5_hint= f==='exec'? '' :   /* 14/10/2026: a regra da execução foi para a dica ⓘ */
             (f==='conf'? 'Confira o balanço; conferido e sem divergência, a ordem fica elegível a Fechar processo.' : 'Processo encerrado com balanço conciliado; a liberação dos lotes é decisão da qualidade (CO-06).');
  const toast=t=>self.setState({g2toast:t});
  v.c5_fin=()=>toast('Turno finalizado · ordem PERMANECE Em execução · apontamentos do turno travados para conferência.');
  const confb=()=>{ const s=self.state; const fx=s.c5f||'exec'; const b2=co5_bal(self);
    if(fx==='exec') return toast('Ainda não disponível: a ordem está Em execução. Conclua a execução para abrir a conferência · parcial '+b2.eq+', '+(b2.ok?'sem divergência':'divergência de '+co_nf(Math.abs(b2.div),1)+' t')+'.');
    if(!b2.ok) return self.setState({c5c:false,g2toast:'Divergência de '+co_nf(Math.abs(b2.div),1)+' t: corrija as saídas na tabela antes de fechar o processo.'});
    self.setState({c5c:true,g2toast:'Balanço conferido · '+b2.eq+' t conciliado · perdas 0,6 t (descarte) · em processo 0,0 t · sem divergência · elegível a Fechar processo · L39-120/121 seguem Aguardando inspeção.'}); };
  v.c5_confb=confb;
  const concl=()=>{ self.setState({c5f:'conf',c5c:false,g2toast:'Término físico registrado · OB-0110 entra em Em conferência — confira o balanço antes de fechar o processo.'}); };
  const fechar=()=>{ const s=self.state; if(!s.c5c) return toast('Ainda não elegível: confira o balanço antes de fechar o processo.');
    self.setState({c5f:'enc',g2toast:'OB-0110 Encerrada · balanço conciliado · L39-120/121 seguem Aguardando inspeção — fechar processo não libera lote; a qualidade decide em CO-06.'}); };
  if(f==='exec'){ v.c5p_t='Concluir execução'; v.c5p_fn=concl; v.c5_prox='Concluir execução'; v.c5p_isbtn=true; v.c5p_islnk=false; }
  else if(f==='conf' && !cf){ v.c5p_t='Conferir balanço'; v.c5p_fn=confb; v.c5_prox='Conferir balanço'; v.c5p_isbtn=true; v.c5p_islnk=false; }
  else if(f==='conf'){ v.c5p_t='Fechar processo'; v.c5p_fn=fechar; v.c5_prox='Fechar processo'; v.c5p_isbtn=true; v.c5p_islnk=false; }
  else { v.c5p_t='Encaminhar qualidade'; v.c5p_href='CO-06.dc.html'; v.c5_prox='Encaminhar qualidade'; v.c5p_isbtn=false; v.c5p_islnk=true; }
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_bal'||!r) return; const b2=co5_bal(self);
    self.setState({c5c:false,g2toast:r.v.fluxo+' atualizado · balanço '+b2.eq+' t · '+(b2.ok?'sem divergência':'divergência de '+co_nf(Math.abs(b2.div),1)+' t')+((self.state.c5f||'exec')==='conf'?' · confira o balanço de novo':'')}); }; }
'''
    shell37('CO-05','OB-0110 · Packing do mamão',corpo,fname=fn,crumbs_extra=['OB-0110'],
      subtitle='Entradas e saídas por estado físico, classes, embalagens, perdas e genealogia.',
      status=(H('c5_selo'),'green'),primary_html=dyn_primary('c5p'),steps=faixa(5),
      footer='Concluir execução leva a Em conferência; fechar processo exige balanço conferido. Balanço conferido torna o processo elegível a fechar; a liberação comercial dos lotes é decisão de qualidade (CO-06 · DEMO-07).')
    dyn_status(fn,'c5_selo')

# =====================================================================================
def co06():
    fn='CO-06.dc.html'; HEIGHTS37[fn]=1000
    LB=D.LOTE_BLOQ
    DEC={'Bloqueado':'red','Liberado':'green','Em inspeção':'yellow','Retorno bloqueado':'red'}
    dest=dact('Decidir lote',dict(title=f'Destinação do retorno {RC12["lote"]}',sub=f'{RC12["kg"]} kg de mamão A devolvidos no {RC12["id"]} ({RC12["pedido"]}) · maturação avançada',
        fields=[('Destinação','Descarte · compostagem'),('Justificativa','maturação avançada em 40% da amostra (INSP-93)'),('Responsável','Marta')],
        confirm='Registrar destinação',done=f'Destinação do {RC12["lote"]} registrada · 300 kg saem do estoque bloqueado · o {RC12["id"]} já pode ser encerrado no Comercial (VE-06)'))
    rows=[
     R('INSP-88',insp=[b('INSP-88'),mut(LB['id'])],prod='Café beneficiado',pad='defeitos/peneira · COB · 3 × 300 g',res=[ch('Defeitos acima do tipo 6','red')],
       dec='Bloqueado',resp='Marta',przo=[Pt.txt('Marta'),br(),ch('até 3 dias · 25/09','yellow')],acao=[Pt.cta('Decidir lote','CO-06det.dc.html',u=True)]),
     R('INSP-93',insp=[b('INSP-93'),mut(f'{RC12["lote"]} · retorno {RC12["id"]}')],prod='Mamão A (retorno)',pad='maturação/firmeza · 12 frutos',res=[ch('Maturação avançada · 40%','red')],
       dec='Retorno bloqueado',resp='Marta',przo=[Pt.txt('Marta'),br(),ch('vence hoje','red')],acao=[dict(dest,u=True)]),
     R('INSP-92',insp=[b('INSP-92'),mut('L39-120/121')],prod='Mamão classe A e B',pad='calibre e firmeza · coleta hoje',res=[ch('Aguardando resultado','yellow')],
       dec='Em inspeção',resp='Marta',przo=[Pt.txt('Marta'),br(),ch('vence hoje','red')],
       acao=[Pt.act('Registrar resultado','Resultado da INSP-92 registrado · decidir Liberar ou Bloquear continua com a qualidade — o resultado sozinho não libera o lote.')]),
     R('INSP-91',ro=True,insp=[b('INSP-91'),mut('L38-118')],prod='Mamão de campo · consumido na OB-0110',pad='calibre/firmeza · 24 frutos',res=[ch('Conforme','green')],
       dec='Liberado',resp='Marta',przo=[Pt.txt('Marta'),br(),ch('no prazo','green')],acao=[mut('—')]),
     R('INSP-85',ro=True,insp=[b('INSP-85'),mut('Silo 2')],prod='Milho seco',pad='umidade/impureza · 3 × 1 kg',res=[ch('14,0% · 0,9% conforme','green')],
       dec='Liberado',resp='Rui',przo=[Pt.txt('Rui'),br(),ch('no prazo','green')],acao=[mut('—')]),
    ]
    g_in=grid([C('insp',l='Inspeção · lote',w=130),C('prod',l='Produto',w=90),C('pad',l='Padrão · amostra',w=120),C('res',l='Resultado'),C('dec',l='Decisão',chips=DEC),
               C('przo',l='Responsável · prazo',w=140),C('acao',l='Ação')],rows,
      edit=dict(m='form',title='Inspeção',sub='Ajuste padrão, amostra e responsável. Liberar ou bloquear é decisão registrada pela ação do lote, não pela edição. Inspeção concluída abre em consulta.',
        fields=[dict(k='prod',l='Produto',ro=True),dict(k='pad',l='Padrão · amostra',t='txt',req=True),
                dict(k='resp',l='Responsável',t='sel',req=True,opts=['Marta','Rui','Ana']),dict(k='dec',l='Decisão',ro=True)]),
      gid='g_in',total=False)
    corpo=(
      sec('Inspeções e decisões','Inspecione cada lote pelo padrão do produto e decida com responsável e prazo.',
        [idrw('Inspecionar lote',dict(title='Nova inspeção',sub='amostra e método do padrão do produto',
           fields=[('Lote','L39-120 · Mamão classe A'),('Padrão / método','calibre e firmeza · amostra 2%'),('Responsável','Equipe qualidade · Marta'),('Prazo','24/09/2026')],
           confirm='Abrir inspeção',done='INSP-94 aberta · lote permanece Aguardando inspeção'),'lab','Abrir nova inspeção pelo padrão do produto',primary=True)],g_in)
      + _car_sec()   # carência e destino dos lotes de mamão (MAPA-CARENCIA-LMR-20261003)
      + sec('Árvore de lotes e recolhimento','Rastreie para trás e para frente, mesmo sem saldo no lote.',
        [imsg('Rastrear clientes','Rastreio do L27-013: nenhum cliente atendido — lote nunca saiu para venda; para trás: OB-0104 ← bica L27-018/019 ← colheita C1 de jul/26.','layers','Rastrear clientes e origem do lote L27-013'),
         ilnk('Abrir recolhimento','VE-06.dc.html','alert','Abrir o caso de recolhimento no Comercial'),ilnk('Ver viagens afetadas','LO-03.dc.html','truck','Ver viagens que levaram lotes afetados')],
        '',state='gray'))
    # + carência e destino dos lotes (MAPA-CARENCIA-LMR-20261003): cenário, motor e CARVALS
    EXTRAJS[0]=JSBASE+_car_js()+r'''
function EXTRAVALS(self,v){ CARVALS(self,v); self.g2after=(gid,rows,r)=>{ if(gid==='g_in'&&r&&r.p.przo){ r.p.przo=[{k:'txt',t:r.v.resp}].concat(r.p.przo.slice(1)); r.s.przo=r.v.resp; } }; }
'''
    shell37('CO-06','Qualidade e rastreabilidade',corpo,
      subtitle='Inspeções, bloqueios e árvore de lotes; liberar e bloquear são decisões da qualidade, independentes do encerramento da produção.',
      status=('1 lote bloqueado · decisão até 25/09 · 1 retorno a destinar','red'),steps=faixa(6),
      footer='Padrões variam por cultura: grãos por umidade/impureza; frutas por classe/calibre; café por defeitos e rendimento bica → beneficiado. '
             'Bloqueio invalida a elegibilidade das reservas afetadas e avisa o Comercial automaticamente; tentativas de reservar ou expedir o lote falham com motivo (ver CO-07). '
             'A simulação de recolhimento usa a mesma árvore, mesmo com saldo zero. '
             'Carência e destino: lotes de campo vêm dos apontamentos das O.S. de colheita (parcela + data); pós-colheita, mistura, divisão, laudo e destinos iniciais são registros demonstrativos. '
             f'LMR Brasil: ANVISA (monografias, extração {_lmr_ext()}). Regras de exportação não carregadas; o "Mercado sintético" usa valores sintéticos.')

# =====================================================================================
def co06det():
    fn='CO-06det.dc.html'; HEIGHTS37[fn]=1000; PARENT37[fn]='CO-06.dc.html'
    LB=D.LOTE_BLOQ
    g_pd=grid([C('pend',l='Pendência'),C('lote',l='Lote'),C('q',l='Quantidade',a='r'),C('resp',l='Responsável'),C('przo',l='Prazo'),C('cond',l='Condição de resolução',w=260)],
      [R('p1',pend=[b('INSP-88')],lote=[b(LB['id']),mut(LB['produto'])],q=f'{milhar(LB["sc"])} sc 60 kg',resp='Qualidade · Marta',przo=[ch('até 3 dias · 25/09','yellow')],
         cond='laudo COB revisado + decisão Liberar/Destinar')],
      edit=dict(m='ro',title='Pendência de qualidade',fields=[dict(k='q',l='Quantidade',ro=True),dict(k='resp',l='Responsável',ro=True),dict(k='cond',l='Condição de resolução',ro=True)]),
      search=False,gid='g_pd',total=False)
    g_am=grid([C('crit',l='Critério'),C('pad',l='Padrão do tipo 6'),C('med',l='Medido',a='r'),C('sit',l='Situação')],
      [R('def',crit='Defeitos (equiv.)',pad='≤ 86',med=[b('103')],sit=[ch('Acima do tipo','red')],o=['3 amostras × 300 g · classificação oficial COB','Média de defeitos equivalentes: 101 · 104 · 104 → 103']),
       R('pen',crit='Peneira 16 acima',pad='≥ 60%',med='58%',sit=[ch('Limítrofe','yellow')],o=['Retido na peneira 16 e acima ÷ amostra total']),
       R('umi',crit='Umidade',pad='≤ 12%',med='11,4%',sit=[ch('Conforme','green')],o=['Medidor calibrado · média de 3 leituras'])],
      edit=dict(m='origin',title='Resultado da amostra',fields=[dict(k='crit',l='Critério',ro=True),dict(k='pad',l='Padrão',ro=True)]),
      search=False,gid='g_am',total=False)
    g_ef=grid([C('tent',l='Tentativa',w=260),C('orig',l='Origem'),C('res',l='Resultado')],
      [R('e1',tent='Reserva de 500 sc · pedido PV-028',orig=[Pt.link('Comercial (VE-04)','VE-04.dc.html')],res=[ch('Falhou · lote bloqueado por INSP-88','red')]),
       R('e2',tent='Expedição · programação da doca',orig=[Pt.link('Logística (LO-02)','LO-02.dc.html')],res=[ch('Falhou · lote indisponível','red')])],
      edit=dict(m='ro',title='Tentativa recusada',fields=[dict(k='tent',l='Tentativa',ro=True)]),search=False,gid='g_ef',total=False)
    corpo=(
      continuity('CO-05 · OB-0104 encerrada','Lote L27-013 · Bloqueado','decisão da qualidade · destinação','Registrar decisão do lote')
      + sec('Pendência formal de qualidade','Resolva a pendência com o responsável até o prazo.','',g_pd,state='red')
      + sec('Resultado da amostra','Compare o medido com o padrão do tipo 6 (3 × 300 g · COB); clique no critério para ver o cálculo.','',g_am,state='yellow')
      + sec('Efeito do bloqueio','Confira as tentativas recusadas; o Comercial já foi avisado.','',g_ef,state='red')
      + sec('Decisão','Decida o destino do lote; a liberação habilita só destinações compatíveis e NÃO reabre a ordem encerrada.','',
        f'<div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">'
        + imsg('Liberar para destinação compatível','Liberado para blend/mercado interno tipo 7 · reservas voltam a ser elegíveis só nessas destinações · OB-0104 permanece Encerrada. Recibo QL-1148.',
               'check','Liberar o lote só para destinações compatíveis com o tipo 7',primary=True)
        + idrw('Definir destinação',dict(title='Destinação do lote L27-013',sub='reprocessamento físico exige ordem vinculada, sem apagar os fatos',
            fields=[('Destinação','Reprocesso · repasse de beneficiamento'),('Ordem vinculada','nova OB a criar'),('Justificativa','reduzir defeitos por catação')],
            confirm='Registrar destinação',done='Destinação registrada · ordem de reprocesso criada em A liberar'),'tag','Definir destinação física (reprocesso exige ordem vinculada)')
        + imsg('Manter bloqueio','Bloqueio mantido · pendência INSP-88 segue com dono e prazo · Comercial permanece avisado.','alert','Manter o lote bloqueado com a pendência aberta')
        + '</div>'))
    shell37('CO-06','INSP-88 · Lote L27-013 bloqueado',corpo,fname=fn,crumbs_extra=['INSP-88'],
      subtitle='Produção e qualidade independentes: a ordem encerrou reconciliada; o lote só circula por decisão daqui.',
      status=('Bloqueado · decisão até 25/09','red'),steps=faixa(6),
      footer='Encerrar processo não libera lote; decisão de qualidade não reabre ordem encerrada (DEMO-19 · AC-49).')

# =====================================================================================
def co07():
    fn='CO-07.dc.html'; HEIGHTS37[fn]=1000
    LB=D.LOTE_BLOQ
    rows=[
     R(LB['id'],lote=[b(LB['id']),br(),mut('Armazém Sede · Santa Rita')],prod='Café beneficiado · tipo em revisão',prop='Santa Rita',fis=f'{milhar(LB["sc"])} sc 60 kg',qual=[ch('Bloqueado · INSP-88','red')],
       res='0',disp=[b('0 · bloqueado')],val='—',orig='OB-0104',acao=[Pt.cta('Abrir lote','CO-06det.dc.html',u=True)],vis='B',
       o=['Entrada 3.690 sc 60 kg · OB-0104 (encerrada 18/09)','Bloqueio INSP-88 · 21/09 · reservas afetadas: PV-028 (500 sc) recusada','Disponível = físico apto − reservado = 0']),
     R(RC12['lote'],lote=[b(RC12['lote']),br(),mut('Packing Sede (bloqueio) · Santa Rita')],prod='Mamão A · retorno RC-12 · validade 3 d',prop='Santa Rita',fis=f'{RC12["kg"]} kg',
       qual=[ch('Bloqueado · aguarda qualidade','red')],res='0',disp=[b('0 · bloqueado')],val='3 d (perecível)',orig=f'{RC12["id"]} · {RC12["pedido"]}',
       acao=[Pt.cta('Abrir inspeção','CO-06.dc.html',u=True)],vis='B',
       o=[f'Retorno autorizado {RC12["id"]} ({RC12["pedido"]} · entrega 2/2) · recebido bloqueado 300 kg (CO-04)','Inspeção INSP-93 · destinação pendente','Estoque vendável não aumenta com o retorno']),
     R('soja',lote=[b(SOJA['lote']),br(),mut('Santa Rita')],prod='Soja em grão · padrão',prop='Santa Rita',fis=f'{milhar(SOJA["fisico"])} sc 50 kg',qual=[ch('Apto','green')],
       res=f'{milhar(SOJA["reservado"])} sc (contrato barter)',disp=[b(f'{milhar(SOJA["disponivel"])} sc')],val='—',orig='safra 25/26',acao=[Pt.cta('Alocar pedido','VE-04.dc.html')],vis='LC',
       o=['Físico apto 38.420 sc 50 kg','Reserva do contrato barter: 3.875 sc (subtraída uma única vez)','Disponível = 38.420 − 3.875 = 34.545 sc']),
     R('milho',lote=[b('Silo 2'),br(),mut('Santa Rita')],prod='Milho seco · base 14%',prop='Santa Rita',fis=f'{milhar(MILHO["fisico"])} sc 50 kg',qual=[ch('Apto · INSP-85','green')],
       res=f'{milhar(MILHO["reservado"])} sc',disp=[b(f'{milhar(MILHO["disponivel"])} sc')],val='—',orig='OC-0501 · OB-0106',acao=[Pt.cta('Alocar pedido','VE-04.dc.html')],vis='LC',
       o=['Colheita OC-0501 · T3: 8.612 sc (base 14%, após secagem OB-0106)','Reservado: 2.000 sc','Disponível = 8.612 − 2.000 = 6.612 sc']),
     R('L39-120',lote=[b('L39-120'),br(),mut('Packing Sede · Santa Rita')],prod='Mamão · classe A cal. 8–10 · validade 7 d',prop='Santa Rita',fis='9,6 t',qual=[ch('Em inspeção · INSP-92','yellow')],
       res='9,6 t provisória (PV-031)',disp=[b('0 t até liberar')],val='7 d (perecível)',orig='OB-0110',acao=[Pt.cta('Abrir inspeção','CO-06.dc.html')],vis='CB',
       o=['Saída A da OB-0110 (packing 23–24/09): 9,6 t','Reserva provisória do PV-031: 9,6 t (pedido de 10,0 t · falta 0,4 t)','Disponível 0 t até a INSP-92 decidir']),
     R('L39-121',lote=[b('L39-121'),br(),mut('Packing Sede · Santa Rita')],prod='Mamão · classe B · validade 7 d',prop='Santa Rita',fis='1,8 t',qual=[ch('Em inspeção · INSP-92','yellow')],
       res='0',disp=[b('0 t até liberar')],val='7 d (perecível)',orig='OB-0110',acao=[Pt.cta('Abrir inspeção','CO-06.dc.html')],vis='B',
       o=['Saída B da OB-0110: 1,8 t','Disponível 0 t até a INSP-92 decidir']),
     R('L38-118',lote=[b('L38-118'),br(),mut('Packing Sede · Santa Rita')],prod='Mamão de campo · consumido na OB-0110',prop='Santa Rita',fis='0 kg',qual=[ch('Liberado · INSP-91','green')],
       res='—',disp='0',val='—',orig='OC-0507 · S38',acao=[mut('—')],vis='',
       o=['Entrada 3.020 kg · OC-0507 (T7 · S38) · recebida em CO-04','Consumo integral na OB-0110','Rastreio ativo mesmo sem saldo']),
    ]
    g_es=grid([C('lote',l='Lote · local · proprietário',w=140),C('prod',l='Produto · classe · validade',w=130),C('fis',l='Físico',a='r',w=100),C('qual',l='Qualidade'),
               C('res',l='Reservado',a='r',w=100),C('disp',l='Disponível',a='r',w=100),C('orig',l='Origem',w=80),C('acao',l='Ação')],rows,
      edit=dict(m='origin',title='Movimentos do lote',sub='Saldo calculado pelos movimentos; corrija na origem (recebimento, processo, qualidade ou inventário).',
        fields=[dict(k='prod',l='Produto · classe',ro=True),dict(k='fis',l='Físico',ro=True),dict(k='res',l='Reservado',ro=True)]),
      gid='g_es',total=False)
    VIS=[('Tudo',''),('Livres','L'),('Comprometidos','C'),('Bloqueados','B')]
    segh=('<div role="group" aria-label="Visão do estoque" style="display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: '+GRAYS+'; gap: 2px;">'
          + ''.join(f'<button type="button" onClick="{H("c7v"+str(i))}" title="Mostrar {esc(t.lower())}" style="{H("c7s"+str(i))}">{esc(t)}</button>' for i,(t,_) in enumerate(VIS))+'</div>')
    # TAB-07 (DS-MODULOS-2, 17/10/2026): sem cartões de resumo sobre a lista; o que pede atenção vai no selo do cabeçalho e o resto já está nas linhas
    corpo=(
      sec('Saldo por lote, classe, local e proprietário','Escolha a visão e clique no lote para ver os movimentos que formam o saldo.',
        [segh,ilnk('Transferir','SU-08.dc.html','truck','Transferir saldo entre locais'),ilnk('Inventariar','SU-09.dc.html','lista','Abrir contagem de inventário')],g_es)
      + sec('Reserva não conta duas vezes','Desconte a reserva uma única vez do físico apto.','',
        nota(f'Soja: físico apto {B("38.420 sc")} − reserva {B("3.875 sc")} = disponível {B("34.545 sc")}.'),state='gray'))
    SEG_ON=E.SEG_ON(); SEG_OFF=E.SEG_OFF()
    EXTRAJS[0]=JSBASE+'const C7VIS='+json.dumps([k for _,k in VIS])+';\nconst C7_ON='+json.dumps(SEG_ON)+';\nconst C7_OFF='+json.dumps(SEG_OFF)+';\n'+r'''
function PREVALS(self,v){ const sp=co_G('g_es'); if(!sp._all) sp._all=sp.rows; const k=C7VIS[self.state.c7||0];
  sp.rows= k? sp._all.filter(r=>String(r.v.vis||'').indexOf(k)>=0) : sp._all; }
function EXTRAVALS(self,v){ C7VIS.forEach((k,i)=>{ v['c7v'+i]=()=>self.setState({c7:i}); v['c7s'+i]=((self.state.c7||0)===i)?C7_ON:C7_OFF; }); }
'''
    shell37('CO-07','Estoque de produção',corpo,
      subtitle='Saldo físico, bloqueado, apto, reservado e disponível por lote, classe, local e proprietário — única tela canônica de produto acabado.',
      status=('2 lotes bloqueados · 2 em inspeção','yellow'),
      primary='Alocar pedido',primary_href='VE-04.dc.html',steps=faixa(7),
      footer='Tentar alocar ou expedir o L27-013 falha com motivo (bloqueio INSP-88); liberação posterior habilita apenas destinações compatíveis (AC-50). '
             'A reserva conta uma vez: o contrato barter que originou a reserva não é subtraído de novo. A oferta futura (previsão em CO-01) não soma como estoque; '
             'café em sc 60 kg não soma com grãos em sc 50 kg; retorno bloqueado não aumenta o vendável.')

def build():
    co01(); co02(); co02det(); co03(); co04(); co05(); co05det(); co06(); co06det(); co07()


# ===================== Carência e destino dos lotes (MAPA-CARENCIA-LMR-20261003) =====================
# Lote → avaliação do destino: origem (parcela + data de colheita), aplicações até a colheita, pós-colheita, genealogia, regra do mercado,
# evidência (laudo) e o que falta com quem resolve. Motor e regras em dados_carencia.py (o mesmo do Mapa e da O.S.), lotes do cenário.
def _car_js():
    import cenario, dados_carencia as DCAR
    return cenario.js_prefixo()+DCAR.js_nucleo()+r"""
function carBl(t,itens,vazio){ return {t,itens,vazio:vazio||'',temItens:itens.length>0,semItens:!itens.length}; }
function carIt(t,sub,cor){ const b={red:'#C8553D',yellow:'#D4B25A',green:'#5F8F55',gray:'#C9CFCB'}[cor||'gray'];
  return {t,sub:sub||'',hasSub:!!sub,st:'border-left:3px solid '+b+';padding:5px 9px;background:#FFFFFF;border-radius:6px;display:flex;flex-direction:column;gap:2px;'}; }
function CARVALS(self,v){ cenOuvir(self); const c=cenGet(); const L=carLotes(c); const ids=Object.keys(L); const av={}; ids.forEach(k=>{ av[k]=carAvaliar(c,k); });
  const ORD={nao_conforme:0,pendente:1,nao_avaliado:2,conforme:3}; ids.sort((a,b)=>(ORD[av[a].st]-ORD[av[b].st])||((L[a].d||'')<(L[b].d||'')?1:-1)||(a<b?-1:1));
  if(!self.__carh){ self.__carh=1; let h=''; try{ h=decodeURIComponent(location.hash.slice(1)); }catch(e){}
    if(L[h]) setTimeout(()=>{ self.setState({carsel:h}); setTimeout(()=>{ const el=document.getElementById('car-det'); if(el) el.scrollIntoView({block:'start'}); },80); },0); }
  const sel=(self.state.carsel&&L[self.state.carsel])?self.state.carsel:'';
  const orig=(l)=>carAncestrais(L,l.id).filter(x=>x.tipo==='campo').map(x=>carNome(x.tal)+' ('+((CARD.tal[x.tal]||{}).faz||'')+') · '+carBr(x.d)).join(' + ');
  const nomeD=(d)=>d?((CARD.dest[d]||{}).nome||d):'sem destino';
  /* 14/10/2026 (proprietário: "reduza ou elimine ... os demais soltos pela tela"): a origem dos lotes e a fonte do LMR foram para a dica ⓘ; à vista só o rótulo de demonstração */
  v.car_fonte='Demonstração · pós-colheita, laudos e destinos sintéticos';
  const Nn=(st,u,p)=>{ const n=ids.filter(k=>av[k].st===st).length; return n+' '+(n===1?u:p); };
  v.car_n=ids.length+' lotes · '+Nn('nao_conforme','não conforme','não conformes')+' · '+Nn('pendente','pendente','pendentes')+' · '+Nn('nao_avaliado','sem destino','sem destino')+' · '+Nn('conforme','conforme no escopo','conformes no escopo');
  v.car_lotes=ids.map(k=>{ const l=L[k], a=av[k]; const on=k===sel;
    return {id:k,orig:(l.tipo==='campo'?'colhido · ':(l.tipo==='mistura'?'mistura · ':'divisão · '))+orig(l)+(l.tipo!=='campo'&&l.q?' · '+l.q:''),dest:'destino: '+nomeD(a.dest)+(a.lib&&a.lib.valida?' · liberado':'')+(a.libSusp?' · liberação suspensa':''),rot:a.rot,chst:co_chipst(a.cor),acao:a.acao,on:g2seta(on).exp,   /* TAB-09: a seta abre a linha, à esquerda; o verbo fica no fim. TAB-11: a seta gira com o aria-expanded */
      go:()=>self.setState({carsel:on?'':k,cardest:null,carerr:''}),
      st:'display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;width:100%;box-sizing:border-box;text-align:left;padding:9px 12px;border-radius:10px;cursor:pointer;font-family:inherit;color:#15201A;font-size:13px;'+(on?'border:2px solid #1E7A4C;background:#F4FAF6;':'border:1px solid #E4E9E5;background:#FFFFFF;')}; });
  v.car_has=!!sel; v.car_err=self.state.carerr||''; v.car_hasErr=!!v.car_err;
  const E0=()=>{ v.car_id=''; v.car_tit=''; v.car_rot=''; v.car_chst=''; v.car_dests=[]; v.car_dest=''; v.car_setdest=()=>{}; v.car_save=()=>{}; v.car_save_t=''; v.car_save_st=''; v.car_bls=[]; v.car_prox='';
    v.car_lib_has=false; v.car_lib_btn=false; v.car_lib_t=''; v.car_lib_bt=''; v.car_lib_st=''; v.car_lib_susp=false; v.car_lib_susp_t=''; v.car_lib_go=()=>{}; };
  if(!sel){ E0(); return; }
  const l=L[sel], a=av[sel]; v.car_id=sel; v.car_rot=a.rot; v.car_chst=co_chipst(a.cor)+'; white-space: normal; max-width: 100%; box-sizing: border-box;';   /* no celular a situação longa quebra em vez de vazar a seção */
  v.car_tit=(l.tipo==='campo')?('colhido em '+carBr(l.d)+' no '+carNome(l.tal)+(l.parc?' ('+l.parc+')':'')+', fazenda '+((CARD.tal[l.tal]||{}).faz||'—')+' · '+l.q):((l.tipo==='mistura'?'mistura de ':'divisão de ')+l.pais.join(' + ')+' em '+carBr(l.d)+(l.q?' · '+l.q:''));
  v.car_prox={nao_avaliado:'Próximo passo: o Comercial define o destino do lote; a avaliação começa pela regra desse mercado.',pendente:'Próximo passo: resolver o que falta abaixo; até lá o lote não é liberado para este destino.',
    conforme:'Conforme apenas neste destino e neste escopo. Outro destino pede nova avaliação.',nao_conforme:'Não conforme: '+CARD.quem.ag+' e a Qualidade registram a destinação compatível; o fato não é apagado.'}[a.st];
  const cur=(self.state.cardest&&self.state.cardest.id===sel)?self.state.cardest.v:a.dest; const muda=cur!==a.dest;
  v.car_dests=[{v:'',t:'— sem destino —'}].concat(Object.keys(CARD.dest).map(k=>{ const D=CARD.dest[k]; return {v:k,t:D.nome+(D.sint?' (valores sintéticos)':(D.indef?'':(D.carregada?'':' · regra não carregada')))}; }));
  v.car_dest=cur; v.car_setdest=(e)=>self.setState({cardest:{id:sel,v:e.target.value},carerr:''});
  v.car_save_t=a.dest?'Trocar destino e reavaliar':'Definir destino';
  const BT='font-family:inherit;font-size:13px;font-weight:700;padding:8px 14px;border-radius:9px;cursor:pointer;white-space:nowrap;';
  v.car_save_st=BT+((muda||a.st==='nao_avaliado')?'background:#1E7A4C;color:#FFFFFF;border:1px solid #1E7A4C;':'background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;');
  v.car_save=()=>{ const s=self.state; const d=(s.cardest&&s.cardest.id===sel)?s.cardest.v:a.dest; if(d===a.dest){ self.setState({carerr:'Escolha um destino diferente do atual para reavaliar.'}); return; }
    const r=cenMudar(self,c0=>carc_destino(c0,sel,d)); if(r.erro) self.setState({carerr:r.erro}); else self.setState({cardest:null,carerr:''}); };
  // liberação comercial do lote para o destino: comando impedido fora de "conforme no escopo"; dado novo ou outro destino a suspende
  const lb=a.lib, dn=nomeD(a.dest); v.car_lib_has=(!!a.dest&&!muda)||!!a.libSusp; v.car_lib_btn=!!a.dest&&!muda&&a.st==='conforme'&&!(lb&&lb.valida);
  v.car_lib_t=(lb&&lb.valida)?('Liberado para '+dn+(lb.at?' às '+lb.at:'')+' por '+lb.por+' · só neste destino e escopo.'):(a.st==='conforme'?'Conforme no escopo: registre a liberação comercial para '+dn+'.'
    :'Liberação comercial impedida enquanto o lote estiver '+a.rot.split(' · ')[0].toLowerCase()+': resolva o que falta abaixo.');
  v.car_lib_bt='Liberar para '+dn; v.car_lib_st=BT+'background:#1E7A4C;color:#FFFFFF;border:1px solid #1E7A4C;';
  v.car_lib_susp=!!a.libSusp; v.car_lib_susp_t=a.libSusp?(a.libSusp.t+' · '+a.libSusp.q):'';
  v.car_lib_go=()=>{ const r=cenMudar(self,c0=>carc_liberar_lote(c0,sel)); if(r.erro) self.setState({carerr:r.erro}); else self.setState({carerr:''}); };
  const bl=[];
  bl.push(carBl('O que impede ou falta · quem resolve',a.motivos.map(x=>carIt(x.t,'Quem resolve: '+x.q,'red')).concat(a.faltas.map(x=>carIt(x.t,'Quem resolve: '+x.q,'yellow'))),'Nada pendente no escopo avaliado.'));
  bl.push(carBl('Escopo da avaliação',a.dest&&(CARD.dest[a.dest]||{}).carregada?[carIt((a.sint?'Valores sintéticos de demonstração · ':'')+'Regra: '+a.regra,a.escopo,a.sint?'yellow':'gray')]:[],a.dest?'Regra do destino ainda não avaliável (veja o que falta).':'Sem destino: nada foi avaliado.'));
  bl.push(carBl('Origem e genealogia',carAncestrais(L,sel).map(x=>carIt(x.id+' · '+(x.tipo==='campo'?('colheita '+x.os+' dia '+x.q.split(' dia ')[1]+' · '+carNome(x.tal)+(x.parc?' ('+x.parc+')':'')+' · '+carBr(x.d)+' · '+carNum(x.ha)+' ha'+(x.st==='Provisório'?' · apontamento provisório':'')):((x.tipo==='mistura'?'mistura de ':'divisão de ')+x.pais.join(' + ')+' em '+carBr(x.d)+(x.q?' · '+x.q:''))),x.fonte||'','gray'))));
  bl.push(carBl('Aplicações de defensivo até a colheita',a.apl.map(r=>carIt(r.p+' · '+r.os+' dia '+r.dia+' · aplicado em '+carBr(r.d)+' · origem '+r.lote,'carência '+(r.na?'não se aplica ('+r.txt+')':r.txt)+(r.fim?' · até '+carAte(r.fim):''),'gray')),
    'Nenhuma aplicação apontada na parcela até a colheita. Aplicação posterior à colheita não conta para este lote.'));
  bl.push(carBl('Pós-colheita',a.pos.map(t=>carIt(t.p+' · '+carBr(t.d)+' · lote '+t.lote,(t.reg?'uso pós-colheita conferido':'uso pós-colheita não conferido no registro')+(t.fonte?' · '+t.fonte:''),t.reg?'gray':'yellow')),'Nenhum tratamento pós-colheita registrado.'));
  bl.push(carBl('Limites do destino e resíduos',a.ings.map(g=>carIt(g.ingr+' · '+(g.lim||'sem limite carregado'),'origem: '+g.de+(g.res?' · resultado: '+g.res:''),g.st==='ok'?'gray':(g.st==='acima'?'red':'yellow'))),
    a.dest&&(CARD.dest[a.dest]||{}).carregada?'Nenhum ingrediente aplicado na origem do lote.':'Limites não avaliados: destino sem regra carregada ou indefinido.'));
  const hs=(((c.car||{}).hist||{})[sel]||[]); bl.push(carBl('Histórico de avaliações',hs.slice().reverse().map(h=>carIt((h.at?h.at+' · ':'')+'destino '+nomeD(h.de)+' → '+nomeD(h.para),'antes: '+h.rot0+' · depois: '+h.rot1,'gray')),'Nenhuma troca de destino registrada.'));
  v.car_bls=bl; }
"""

def _car_sec():
    cap=f'font-size: 10.5px; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: {MUTED};'
    sel=f'font-family: inherit; font-size: 13px; padding: 8px 10px; border: 1px solid {LINE}; border-radius: 9px; background: #fff; max-width: 100%; box-sizing: border-box;'
    lista=(f'<div role="list" aria-label="Lotes de mamão por avaliação" style="display: flex; flex-direction: column; gap: 6px;"><sc-for list="{H("car_lotes")}" as="l" hint-placeholder-count="3">'
           f'<div role="listitem"><button type="button" onClick="{H("l.go")}" aria-expanded="{H("l.on")}" aria-controls="car-det" style="{H("l.st")}">'
           + E.seta() +
           f'<b style="font-weight: 800;">{H("l.id")}</b><span style="color: {MUTED}; min-width: 0;">{H("l.orig")}</span><span style="color: {MUTED};">{H("l.dest")}</span>'
           f'<span style="{H("l.chst")}">{H("l.rot")}</span><span style="margin-left: auto; font-weight: 700; text-decoration: underline; text-underline-offset: 3px;">{H("l.acao")}</span></button></div></sc-for></div>')
    blocos=(f'<sc-for list="{H("car_bls")}" as="b" hint-placeholder-count="3"><div style="display: flex; flex-direction: column; gap: 5px;"><div style="{cap}">{H("b.t")}</div>'
            f'<sc-if value="{H("b.temItens")}" hint-placeholder-val="{T()}"><sc-for list="{H("b.itens")}" as="i" hint-placeholder-count="2"><div style="{H("i.st")}"><span style="font-size: 12.8px; font-weight: 700; line-height: 1.35;">{H("i.t")}</span>'
            f'<sc-if value="{H("i.hasSub")}" hint-placeholder-val="{T()}"><span style="font-size: 12px; color: {MUTED}; line-height: 1.35;">{H("i.sub")}</span></sc-if></div></sc-for></sc-if>'
            f'<sc-if value="{H("b.semItens")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {MUTED};">{H("b.vazio")}</div></sc-if></div></sc-for>')
    det=(f'<sc-if value="{H("car_has")}" hint-placeholder-val="{F()}"><section id="car-det" aria-label="Avaliação do lote {H("car_id")}" style="display: flex; flex-direction: column; gap: 12px; padding: 14px; border: 1px solid {LINE}; border-radius: 12px; background: {BG};">'
         f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px;"><h3 style="margin: 0; font-size: 16px; font-weight: 800;">Lote {H("car_id")}</h3><span style="{H("car_chst")}">{H("car_rot")}</span></div>'
         f'<div style="font-size: 13px; color: {MUTED}; margin-top: -6px;">{H("car_tit")}</div>'
         f'<div role="status" style="font-size: 13px; font-weight: 700; line-height: 1.45;">{H("car_prox")}</div>'
         f'<div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 8px;"><label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; min-width: 0; max-width: 100%;">Destino do lote'
         f'<select value="{H("car_dest")}" onChange="{H("car_setdest")}" style="{sel}"><sc-for list="{H("car_dests")}" as="d" hint-placeholder-count="3"><option value="{H("d.v")}">{H("d.t")}</option></sc-for></select></label>'
         f'<button type="button" onClick="{H("car_save")}" style="{H("car_save_st")}">{H("car_save_t")}</button></div>'
         f'<sc-if value="{H("car_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("car_err")}</div></sc-if>'
         f'<sc-if value="{H("car_lib_has")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Liberação comercial do lote" style="display: flex; flex-direction: column; gap: 6px;"><div style="{cap}">Liberação comercial</div>'
         f'<div style="font-size: 13px; line-height: 1.45;">{H("car_lib_t")}</div>'
         f'<sc-if value="{H("car_lib_btn")}" hint-placeholder-val="{F()}"><div><button type="button" onClick="{H("car_lib_go")}" style="{H("car_lib_st")}">{H("car_lib_bt")}</button></div></sc-if>'
         f'<sc-if value="{H("car_lib_susp")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("car_lib_susp_t")}</div></sc-if></div></sc-if>'
         f'{blocos}</section></sc-if>')
    corpo=(f'<div style="display: flex; flex-direction: column; gap: 12px;"><div style="font-size: 12.5px; color: {MUTED}; line-height: 1.5;">{H("car_fonte")}</div>'
           f'<div style="font-size: 13px; font-weight: 700;">{H("car_n")}</div>{lista}{det}</div>')
    return sec('Carência e destino dos lotes de mamão','Avalie cada lote para o destino: origem, aplicações até a colheita, pós-colheita, limite do mercado e evidência. Carência cumprida não é conformidade.',
               [ilnk('Ver carência no mapa','IN-04.dc.html#car','clock','Abrir no mapa: Colheita e produtividade › Carência e destino')],corpo,state='yellow')
