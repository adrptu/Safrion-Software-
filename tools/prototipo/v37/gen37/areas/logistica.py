# -*- coding: utf-8 -*-
"""Área Logística (módulo OCULTO do menu, preservado) — processo sequencial por links:
LO-01 Programe o transporte › LO-02 Expeça as cargas (+ LO-02det conferência do T2) › LO-03 Acompanhe viagens › LO-04 Controle fretes.
Regras de negócio inalteradas (cap. 48–50; LOG, ATP, FILA; FL-21, FL-R07; DEMO-08/19/20): fila explicável por elegibilidade e política v4,
janela original congelada para pontualidade, saída física única (CMD-26), recusa parcial vira caso comercial, frete ≠ recebível,
rateio versionado reconcilia ao custo único da viagem.
Padrão v3.7-processos: faixa de etapas por links, descrição imperativa sob cada bloco, edição pela linha (G2), ações com ícone + title.
Relógio da demonstração nesta área: 23/09/2026 09:52 (T3 espera 1h02 desde 08:50; T4 47 min desde 09:05)."""
from engine import (grid,kpis,chip,esc,icon,Pt,BTN_ST,_MINI,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,SH,DISP,EXTRA,EXTRAJS)
import engine as E
from ui37 import shell37, steps_bar, continuity, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
FALSE=H('false')
# ---- dados locais da área (coerentes com dados.py/dados2.py; números que só aparecem aqui) ----
TOLERANCIA='30 min'                                   # tolerância de chegada da instalação Sede — hipótese configurável
VD=dict(id='VD-2101', cliente='Cooperativa Central', produto='Milho a granel', lote='MZ-26-03', carga_t='37,00 t')  # 3 cargas de 37 t (retirada)
CARGA07=dict(id='Carga 07', pedido='PV-031', cliente='Frutas Real', produto='Mamão Formosa classe A', lote='L39-120', t='9,6 t',
             destino='Frutas Real · Vitória/ES', janela='11:00–12:00')   # = D.CANON['CARGA07'] · PV-031 (VE-04, CIF Vitória/ES, 9,6 t A de L39-120)
KCL=next(l for l in D2.LOTES if l['item']=='KCl 60%')                  # K26-11 · Galpão 2 · 60 t físico, 10 t quarentena (NF 4501)
KCL_APTO=KCL['fisico']-KCL['quarentena']-KCL['reservado']              # 50.000 kg
TRANSF=dict(id='TR-0459', produto='KCl 60 %', kg=10000, sc=200, lote=KCL['id'] if 'id' in KCL else KCL['lote'], origem=KCL['local'],
            destino='Boa Vista', janela='11:00–11:45', doca='Doca 3 · ensacados')
TICKET=dict(id='TK-5531', tara='14,20 t', bruto='51,20 t', liquido='37,00 t', base='13,8% · base 14%')
NF_T2='NF 45.812'
FRETE_C07=dict(prestador='Rota Sul Transportes', base='9,6 t × R$ 190/t', total=1824)
VG117=dict(id='VG-117', pedido='PV-026', lote='L38-110', caso='RC-15', oc='OC-77', frete=1882, base='9,4 t', pedagio=96, recusa='0,4 t', aceito='9,0 t')
RATEIO_V='Rateio v2 · peso líquido'

def n0(v): return f'{v:,.0f}'.replace(',','.')
def rs(v): return 'R$ '+n0(v)

STEPS=[('Programe o transporte','LO-01.dc.html'),('Expeça as cargas','LO-02.dc.html'),('Acompanhe viagens','LO-03.dc.html'),('Controle fretes','LO-04.dc.html')]
WHY={2:'Doca 1 ocupada · Carga 07 sem NF',3:f'{VG117["id"]} · recusa em {VG117["caso"]}'}
def faixa(i):
    return steps_bar([dict(t=t,href=h,why=WHY.get(k,''),tip=t+(' · '+WHY[k] if k in WHY else '')) for k,(t,h) in enumerate(STEPS,1)],current=i)

# ---- helpers de grade e ações ----
def C(k,l,**kw): return dict(k=k,l=l,**kw)
def plain(parts): return ' '.join(p['t'] for p in parts if p.get('k')!='br').strip()
def R(id,ro=False,o=None,v=None,**cells):
    """linha G2: str/número → v (editável/ordenável); lista de partes → p (exibição rica)."""
    r=dict(id=id,v=dict(v or {}),s={},p={})
    for k,x in cells.items():
        if isinstance(x,list): r['p'][k]=x; r['s'][k]=plain(x)
        else: r['v'][k]=x
    if ro: r['ro']=True
    if o: r['o']=[dict(t=t,h=h) if h else dict(t=t) for t,h in o]
    return r
def two(a,b): return [Pt.b(a),Pt.br(),Pt.mut(b)]
def twot(a,b): return [Pt.txt(a),Pt.br(),Pt.mut(b)]
def say(t,key): return {'k':'act','t':t,'fn':'say:'+key}
def fn(t,name,arg,u=False): return {'k':'act','t':t,'fn':f'{name}:{arg}','u':u}

def ibtn(label,hole,ic,title,primary=False):
    return (f'<button type="button" onClick="{H(hole)}" title="{esc(title)}" aria-label="{esc(title)}" style="{BTN_ST(primary,True)} display: inline-flex; align-items: center; gap: 6px;">'
            f'{icon(ic,14)}{esc(label)}</button>')
def ilink(label,href,ic,title):
    return (f'<a href="{href}" title="{esc(title)}" style="{BTN_ST(False,True)} text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">{icon(ic,14)}{esc(label)}</a>')
def bloco(titulo,desc,corpo,acao='',state='green'):
    dot={'green':ACC,'yellow':YEL,'red':RED,'gray':'#8A968E'}[state]
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px; flex-wrap: wrap;">'
            f'<span style="width: 9px; height: 9px; border-radius: 999px; background: {dot}; margin-top: 6px; flex-shrink: 0;"></span>'
            f'<div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 240px;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3>'
            f'<div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">{acao}</div></div>'
            f'<div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')
def nota(txt): return f'<div style="font-size: 12.5px; color: {MUTED}; line-height: 1.5; padding: 0 4px;">{txt}</div>'

PRIM=f'<button type="button" onClick="{H("prim_fn")}" title="{H("prim_tip")}" style="{H("prim_st")}">{H("prim_t")}</button>'

# ---- painel lateral próprio (ações que não são edição de linha) ----
_INP=f'font-family: inherit; font-size: 14px; font-weight: 500; color: {INK}; padding: 9px 11px; border: 1px solid {LINE}; border-radius: 10px; background: {SURF}; box-sizing: border-box; width: 100%;'
def _lab(pid,k,label): return f'<label for="{pid}_{k}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{esc(label)}</label>'
def _err(pid,k):
    return f'<sc-if value="{H(pid+"_"+k+"_hasErr")}" hint-placeholder-val="{FALSE}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H(pid+"_"+k+"_errMsg")}</span></sc-if>'
def _help(t): return f'<span style="font-size: 11.5px; color: {MUTED};">{esc(t)}</span>' if t else ''
def p_sel(pid,k,label,help=''):
    return (f'<div style="display: flex; flex-direction: column; gap: 4px;">{_lab(pid,k,label)}'
            f'<select id="{pid}_{k}" value="{H(pid+"_"+k)}" onChange="{H(pid+"_set_"+k)}" style="{_INP}">'
            f'<sc-for list="{H(pid+"_"+k+"_opts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}" disabled="{H("o.dis")}">{H("o.t")}</option></sc-for></select>'
            f'{_err(pid,k)}{_help(help)}</div>')
def p_inp(pid,k,label,typ='text',unit_hole=None,help=''):
    u=f'<span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{H(unit_hole)}</span>' if unit_hole else ''
    return (f'<div style="display: flex; flex-direction: column; gap: 4px;">{_lab(pid,k,label)}'
            f'<div style="display: flex; align-items: center; gap: 8px;"><input id="{pid}_{k}" type="{typ}" value="{H(pid+"_"+k)}" onChange="{H(pid+"_set_"+k)}" style="{_INP}">{u}</div>'
            f'{_err(pid,k)}{_help(help)}</div>')
def painel(pid,titulo,sub,campos,confirm):
    P=lambda s: H(pid+'_'+s)
    return (f'<sc-if value="{P("open")}" hint-placeholder-val="{FALSE}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar painel" onClick="{P("cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-label="{esc(titulo)}" style="position: relative; width: 460px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">{esc(titulo)}</h2>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{P("cancel")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{esc(sub)}</div>'
            f'<sc-if value="{P("hasErrs")}" hint-placeholder-val="{FALSE}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div></sc-if>'
            f'{campos}<div style="flex-grow: 1;"></div>'
            f'<sc-if value="{P("warn")}" hint-placeholder-val="{FALSE}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
            f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{P("discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{P("keep")}" style="{_MINI}">Continuar editando</button></div></div></sc-if>'
            f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">'
            f'<button type="button" onClick="{P("cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{P("ok")}" style="{BTN_ST(True,True)}">{esc(confirm)}</button></div></aside></div></sc-if>')

JS_BASE='''
function GR(id){ return GRIDS.find(g=>g.id===id); }
function setRow(self,gid,rid,f){ const sp=GR(gid); const rows=g2clone(g2rows(self,sp)); const r=g2find(rows,rid); if(r) f(r); g2set(self,gid,{rows}); return r; }
function isNew(r){ return r && String(r.id).indexOf('n')===0 && !r.v.__ok; }
function toast(self,t){ self.setState({g2toast:t}); }
function PST(on){ return 'padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;'+(on?'background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;':'background:#EEF1EE;color:#5B6660;border:1px solid #E4E9E5;'); }
function mins(h){ const m=/^(\\d{1,2}):(\\d{2})/.exec(String(h||'')); return m?(+m[1])*60+(+m[2]):null; }
function hm(n){ const h=Math.floor(Math.abs(n)/60), m=Math.abs(n)%60; return (h?h+'h':'')+(h?String(m).padStart(2,'0'):m+' min'); }
function PNL(self,v,pid,fields,onok){
  const st=self.state[pid]||{}; const d=st.d||{}; const errs=st.errs||{};
  v[pid+'_open']=!!st.open;
  Object.keys(fields).forEach(k=>{ const f=fields[k];
    v[pid+'_'+k]=(d[k]!==undefined)?d[k]:'';
    v[pid+'_set_'+k]=(e)=>{ const s=self.state[pid]||{}; const d2=Object.assign({},s.d||{},{[k]:e.target.value}); if(f.reset) f.reset.forEach(x=>{ d2[x]=''; }); const er=Object.assign({},s.errs||{}); delete er[k]; self.setState({[pid]:Object.assign({},s,{d:d2,errs:er,warn:false})}); };
    if(f.opts) v[pid+'_'+k+'_opts']=(typeof f.opts==='function'?f.opts(d):f.opts).map(o=>Object.assign({dis:false},o));
    v[pid+'_'+k+'_hasErr']=!!errs[k]; v[pid+'_'+k+'_errMsg']=errs[k]||''; });
  const dirty=()=>{ const s=self.state[pid]||{}; return JSON.stringify(s.d||{})!==JSON.stringify(s.orig||{}); };
  v[pid+'_cancel']=()=>{ if(dirty()) self.setState({[pid]:Object.assign({},self.state[pid],{warn:true})}); else self.setState({[pid]:{open:false}}); };
  v[pid+'_discard']=()=>self.setState({[pid]:{open:false}});
  v[pid+'_keep']=()=>self.setState({[pid]:Object.assign({},self.state[pid],{warn:false})});
  v[pid+'_warn']=!!st.warn; v[pid+'_hasErrs']=Object.keys(errs).length>0;
  v[pid+'_ok']=()=>{ const s=self.state[pid]||{}; const er=onok(Object.assign({},s.d||{})); if(er && Object.keys(er).length){ self.setState({[pid]:Object.assign({},self.state[pid]||s,{errs:er,warn:false})}); return; } self.setState({[pid]:{open:false}}); }; }
function PNLopen(self,pid,d){ self.setState({[pid]:{open:true,d:Object.assign({},d),orig:Object.assign({},d),errs:{},warn:false}}); }
function SAY(self,v,M){ v.say=(k)=>toast(self,M[k]||''); Object.keys(M).forEach(k=>{ v['say_'+k]=()=>toast(self,M[k]); }); }
'''

def build():
    # =====================================================================
    # LO-01 · Programe o transporte
    # =====================================================================
    fname='LO-01.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    ag_cols=[C('carga','Carga · tipo',w=130),C('prod','Produto · rota',w=195),C('jan','Janela',w=160),
             C('veic','Veículo · compatibilidade',w=190),C('custo','Frete',w=140),C('acao','Ação')]
    def ag(id,carga,rota,prod,jan,veic,compat,custo,acao,ro=False,janp=None):
        r=R(id,ro=ro,v=dict(jan=jan,orig=jan,mot=''),carga=carga,prod=[Pt.txt(prod),Pt.br(),Pt.mut(rota)],veic=veic+[Pt.br()]+compat,custo=custo,acao=acao)
        if janp: r['p']['jan']=janp; r['s']['jan']=plain(janp)
        return r
    agenda=[
      ag('T1',[Pt.b('T1'),Pt.txt(' · 1ª de 3'),Pt.br(),Pt.tag('Retirada · cliente')],'Silo Sede → '+VD['cliente'],f'{VD["produto"]} · {VD["carga_t"]}','08:00–09:00',
         twot('Cliente · Rota Norte','ocupação 37/37 t'),[Pt.chip('Compatível · granel','green')],'frete do cliente',[Pt.cta('Ver fila','LO-02.dc.html',True)],
         janp=[Pt.txt('08:00–09:00'),Pt.br(),Pt.chip('Atrasado · prev. 09:10','red')]),
      ag('T2',[Pt.b('T2'),Pt.txt(' · 2ª de 3'),Pt.br(),Pt.tag('Retirada · cliente')],'Silo Sede → '+VD['cliente'],f'{VD["produto"]} · {VD["carga_t"]}','08:30–09:30',
         twot('Cliente · Rota Norte','ocupação 37/37 t'),[Pt.chip('Compatível · granel','green')],'frete do cliente',[Pt.cta('Conferir carga','LO-02det.dc.html')],ro=True,
         janp=[Pt.txt('08:30–09:30'),Pt.br(),Pt.mut('em doca 1 · lacre pendente')]),
      ag('T3',[Pt.b('T3'),Pt.txt(' · 3ª de 3'),Pt.br(),Pt.tag('Retirada · cliente')],'Silo Sede → '+VD['cliente'],f'{VD["produto"]} · {VD["carga_t"]}','09:00–10:00',
         twot('Cliente · Rota Norte','ocupação 37/37 t'),[Pt.chip('Compatível · granel','green')],'frete do cliente',[Pt.cta('Ver na fila','LO-02.dc.html')],
         janp=[Pt.txt('09:00–10:00'),Pt.br(),Pt.mut('presente · aguarda doca 1')]),
      ag('TR',[Pt.b(TRANSF['id']),Pt.br(),Pt.tag('Transferência')],f'{TRANSF["origem"]} → {TRANSF["destino"]}',f'{TRANSF["produto"]} · {n0(TRANSF["kg"])} kg ({TRANSF["sc"]} sc)',TRANSF['janela'],
         twot('T4 · frota própria','ocupação 10/12 t'),[Pt.chip('Compatível · ensacado','green')],twot('custo interno','apropriado uma vez'),[Pt.cta('Separar lotes','LO-02.dc.html')]),
      ag('C07',[Pt.b(CARGA07['id']),Pt.txt(' · '+CARGA07['pedido']),Pt.br(),Pt.tag('Entrega · agricultor')],'Packing Sede → '+CARGA07['destino'],f'{CARGA07["produto"]} · {CARGA07["t"]}',CARGA07['janela'],
         twot('Rota Sul · baú refrigerado','ocupação 9,6/12 t'),[Pt.chip('Compatível · refrigerado','green')],twot(rs(FRETE_C07['total']),'cotado · a contratar'),
         [Pt.cta('Contratar frete','LO-04.dc.html')],janp=[Pt.txt(CARGA07['janela']),Pt.br(),Pt.chip('Impedida · NF pendente','red')]),
    ]
    g_ag=grid(ag_cols,agenda,edit=dict(m='form',title='Reprogramar janela',sub='A janela original fica congelada para a pontualidade; a reprogramação muda só a expectativa operacional.',
        fields=[dict(k='jan',l='Nova janela',t='txt',req=True,help='Ex.: 10:00–11:00'),
                dict(k='mot',l='Motivo da reprogramação',t='sel',req=True,opts=['Pedido do cliente','Atraso do transportador','Capacidade de doca','Chuva na rota','Documento fiscal pendente'])]),
        so={'k':'jan','d':False},gid='g_ag',total=False)
    cp_cols=[C('cand','Candidata a agrupar com a Carga 07',w=260),C('cons','Produto · conservação'),C('rota','Rota'),C('jan','Janela'),C('comp','Compatibilidade',w=260)]
    g_cp=grid(cp_cols,[
        R('c1',cand='Remessa SU · Fungicida A · 12 cx',cons='Defensivo químico',rota='Vitória/ES',jan='flexível',comp=[Pt.chip('Incompatível · defensivo × alimento','red')],
          o=[('Regra de segregação: defensivo não viaja com alimento refrigerado',None),('Mesmo destino não basta para agrupar',None)]),
        R('c2',cand=f'{TRANSF["id"]} · {TRANSF["produto"]} · {n0(TRANSF["kg"])} kg',cons='Fertilizante ensacado',rota=TRANSF['destino'],jan=TRANSF['janela'],comp=[Pt.chip('Rota diferente · não agrupa','gray')],
          o=[(f'Destino {TRANSF["destino"]} × Vitória/ES: rotas sem trecho comum',None)]),
      ],edit=dict(m='origin',title='Compatibilidade',fields=[]),search=False,gid='g_cp',total=False)
    sl_cols=[C('slot','Slot'),C('doca','Doca'),C('carga','Carga · transportador',w=190),C('dur','Duração',w=170),C('resp','Responsabilidade',w=210),C('estado','Estado',w=230)]
    DOCAS=['Doca 1 · granel','Doca 2 · paletizados','Doca 3 · ensacados']
    slots=[
      R('s1',ro=True,v=dict(slot='08:00–09:00',doca=DOCAS[0],dur='45 min'),carga=[Pt.b('T1'),Pt.txt(' · janela original preservada')],resp='—',
        estado=[Pt.chip('Vencido · vaga ao próximo elegível','red')]),
      R('s2',ro=True,v=dict(slot='08:35–09:40',doca=DOCAS[0],dur='45 min + setup 10 min + pesagem',fim='09:52'),carga=[Pt.b('T2'),Pt.txt(' · cliente (Rota Norte)')],
        resp='Expedição: carga e balança · Cliente: veículo e motorista',estado=[Pt.chip('Em uso · excede o slot 12 min (lacre)','yellow')]),
      R('s3',v=dict(slot='09:50–10:45',doca=DOCAS[0],dur='45 min + setup 10 min'),carga=[Pt.b('T3'),Pt.txt(' · cliente (Rota Norte)')],
        resp='Expedição: carga e balança · Cliente: veículo e motorista',estado=[Pt.chip('Reservado · doca 1 ainda com o T2','yellow')]),
      R('s4',v=dict(slot='11:00–11:55',doca=DOCAS[2],dur='45 min + setup 10 min'),carga=[Pt.b(TRANSF['id']),Pt.txt(' · T4 frota própria')],
        resp='Expedição: separação e carga · Frota: veículo',estado=[Pt.chip('Reservado','gray')]),
      R('s5',v=dict(slot=CARGA07['janela'],doca=DOCAS[1],dur='60 min + inspeção refrigerado'),carga=[Pt.b(CARGA07['id']),Pt.txt(' · '+FRETE_C07['prestador'])],
        resp='Expedição: carga · Transportador: baú e temperatura',estado=[Pt.chip('Impedida · NF pendente','red')]),
    ]
    g_sl=grid(sl_cols,slots,edit=dict(m='form',title='Slot de doca',newTitle='Reservar slot de doca',
        sub='A duração vem do tipo e volume da carga, com setup e balança compartilhada. Sobreposição na mesma doca é recusada.',
        fields=[dict(k='slot',l='Horário (início–fim)',t='txt',req=True,help='Ex.: 10:50–11:45'),dict(k='doca',l='Doca',t='sel',req=True,opts=DOCAS,**{'def':DOCAS[0]}),
                dict(k='carga',l='Carga',t='txt',req=True,help='Ex.: T3 · VD-2101 3ª carga'),dict(k='dur',l='Duração estimada',t='txt',req=True,**{'def':'45 min + setup 10 min'})]),
        so={'k':'slot','d':False},add='Reservar slot',search=False,gid='g_sl',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){
  SAY(self,v,{agrupar:'Nenhum grupo criado · Fungicida A é incompatível com alimento refrigerado e a TR-0459 segue outra rota. Uma proposta mostraria custo, ocupação e risco antes da decisão.'});
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_ag'){ r.p.jan=[{k:'txt',t:r.v.jan},{k:'br',t:''},{k:'mut',t:'original '+r.v.orig+' preservada · '+r.v.mot}]; r.s.jan=r.v.jan;
      toast(self,r.id+': janela reprogramada para '+r.v.jan+' ('+r.v.mot+') · a pontualidade continua medida contra '+r.v.orig+'.'); self.setState({tick:Date.now()}); return; }
    if(gid==='g_sl'){ const a=String(r.v.slot).split(/[–-]/); const i0=mins(a[0]), i1=mins(a[1]);
      if(isNew(r)){ r.v.__ok=1; r.v.resp='Expedição: carga'; }
      r.p.carga=[{k:'b',t:String(r.v.carga||'')}]; r.s.carga=String(r.v.carga||'');
      let conf=null; rows.forEach(x=>{ if(x===r||x.id==='s1'||x.v.doca!==r.v.doca) return; const b=String(x.v.slot).split(/[–-]/); const j0=mins(b[0]); let j1=mins(b[1]); if(x.v.fim) j1=Math.max(j1,mins(x.v.fim)+10);
        if(i0!==null&&i1!==null&&j0!==null&&j1!==null&&i0<j1&&j0<i1) conf=x; });
      if(i0===null||i1===null||i1<=i0){ r.p.estado=[{k:'chip',t:'Horário inválido · use início–fim',c:'red'}]; toast(self,'Horário inválido: informe início e fim (ex.: 10:50–11:45).'); }
      else if(conf){ r.p.estado=[{k:'chip',t:'Conflito com '+conf.s.carga.split(' ·')[0]+' · escolha outro horário',c:'red'}]; toast(self,'Slot não reservado: '+r.v.doca+' ocupada por '+conf.s.carga.split(' ·')[0]+' nesse horário. Escolha outro horário ou outra doca.'); }
      else { r.p.estado=[{k:'chip',t:'Reservado',c:'gray'}]; toast(self,'Slot '+r.v.slot+' reservado na '+r.v.doca+' · balança e equipe alocadas.'); }
      r.s.estado=r.p.estado[0].t; self.setState({tick:Date.now()}); } };
}
'''
    corpo=(
      kpis([('CARGAS HOJE','5','3 retiradas · 1 entrega · 1 transf.'),('ATRASADAS','1','T1 · prev. 09:10'),
            ('OCUPAÇÃO DAS DOCAS','64%','doca 1 crítica até 10:45'),('FRETE PREVISTO','R$ 1,8 mil','só entrega do agricultor')])
      + bloco('Agenda de cargas do dia','Confira janela, veículo e compatibilidade; clique na carga para reprogramar a janela.',g_ag,
              ilink('Cotar frete','LO-04.dc.html','cash','Comparar cotações de frete em Controle fretes'))
      + bloco('Agrupar entregas compatíveis','Agrupe só entregas compatíveis em produto, conservação e rota.',g_cp,
              ibtn('Agrupar entregas','say_agrupar','layers','Simular agrupamento das entregas compatíveis com a Carga 07'),state='gray')
      + bloco('Docas e slots','Reserve slots pela duração da carga; clique no slot para ajustar horário ou doca.',g_sl,
              ilink('Ver viagens','LO-03.dc.html','map','Acompanhar as viagens programadas'))
    )
    shell37('LO-01','Programação de transporte',corpo,
      subtitle='Capacidade, janelas e docas das cargas de venda, transferência e compra.',
      status=('1 carga atrasada · T1','red'),primary='Expedir cargas',primary_href='LO-02.dc.html',steps=faixa(1),
      footer='Agendamento comercial e sequência real de carga são registros diferentes (48.2); atraso perde prioridade, não a janela original. DEMO-20.')

    # =====================================================================
    # LO-02 · Expeça as cargas (fila DEMO-20)
    # =====================================================================
    fname='LO-02.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    fi_cols=[C('veic','Veículo',w=130),C('pos','Pos.',t='num',a='r'),C('jan','Janela original'),C('cheg','Chegada real · espera',w=150),
             C('sit','Situação · elegibilidade',w=200),C('mot','Por que está nesta posição',w=225),C('acao','Ação')]
    fila=[
      R('T2',ro=True,v=dict(pos=1,jan='08:30'),veic=[Pt.b('T2')],cheg=twot('08:12','espera 23 min até a chamada'),
        sit=[Pt.chip('Em doca 1 · carregada','green'),Pt.br(),Pt.chip('Lacre pendente','yellow')],
        mot='Chamado 08:35 (presente, apto, doca 1 livre, NF autorizada). Ocupa a doca 1 até a saída confirmada.',acao=[Pt.cta('Conferir carga','LO-02det.dc.html',True)]),
      R('T3',v=dict(pos=2,jan='09:00',pmot=''),veic=[Pt.b('T3')],cheg=twot('08:50','espera 1h02 · alerta'),
        sit=[Pt.chip('Presente · carga pronta','green'),Pt.br(),Pt.chip('Aguarda doca 1 (T2)','yellow')],
        mot='Próximo elegível: janela 09:00 cumprida e carga pronta; entra na doca 1 assim que o T2 sair.',acao=[Pt.mut('na saída do T2')]),
      R('T4',v=dict(pos=3,jan=TRANSF['janela'],pmot=''),veic=two('T4','frota própria'),cheg=twot('09:05','espera 47 min'),
        sit=[Pt.chip('Antecipado','gray'),Pt.br(),Pt.chip('Carga a separar','yellow')],
        mot='Só entra com folga, sem prejudicar janelas cumpridas; a TR-0459 ainda está a separar.',acao=[fn('Avaliar encaixe','encaixe','T4')]),
      R('T1',v=dict(pos=4,jan='08:00',pmot=''),veic=[Pt.b('T1')],cheg=twot('—','aviso do motorista não é check-in'),
        sit=[Pt.chip('Atrasado · prev. 09:10','red'),Pt.br(),Pt.chip('Ausente · não elegível','gray')],
        mot=f'Tolerância de {TOLERANCIA} vencida às 08:30: a vaga passa ao próximo elegível; pedido e reserva do produto mantidos.',acao=[fn('Registrar chegada','chegada','T1')]),
      R('C07',ro=True,v=dict(pos='',jan=CARGA07['janela']),veic=[Pt.b(CARGA07['id'])],cheg='—',
        sit=[Pt.chip('Impedida · sem NF','red')],
        mot='Dono: Sandra (fiscal) · prazo hoje 10:00. Não trava os aptos; volta à seleção ao resolver.',acao=[say('Reprocessar NF','nf')]),
    ]
    g_fi=grid(fi_cols,fila,edit=dict(m='form',title='Posição na fila',
        sub='Reordenar exige motivo; autor, horário e versão da fila ficam registrados. Janela original e relógio de espera não mudam. O T2 está em doca e fica em 1º.',
        fields=[dict(k='pos',l='Nova posição',t='sel',req=True,opts=['2','3','4']),
                dict(k='pmot',l='Motivo',t='sel',req=True,opts=['Encaixe com folga · não prejudica janelas cumpridas','Janela em risco','Carga perecível','Espera acumulada','Correção de prioridade'])]),
        so={'k':'pos','d':False},search=False,gid='g_fi',total=False)
    ex_cols=[C('ped','Pedido · destino',w=170),C('lote','Lote · quantidade',w=190),C('veic','Veículo · doca',w=120),C('doc','Documento',w=190),C('etapa','Etapa · checklist',w=210),C('acao','Ação')]
    VEICS=['T3 · doca 1','T4 · doca 3','T4 · doca 2']
    exped=[
      R('E1',ro=True,ped=two(f'{VD["id"]} · 2ª de 3',VD['cliente']),lote=twot(f'{VD["lote"]} · {TICKET["liquido"]} líquido',f'bruto {TICKET["bruto"]} · tara {TICKET["tara"]}'),
        veic='T2 · doca 1',doc=[Pt.chip(f'{NF_T2} autorizada','green')],etapa=[Pt.chip('Carregada','green'),Pt.br(),Pt.mut('checklist 4/5 · falta lacre')],
        acao=[Pt.cta('Conferir carga','LO-02det.dc.html',True)],o=[(f'Ticket {TICKET["id"]}: bruto {TICKET["bruto"]} − tara {TICKET["tara"]} = {TICKET["liquido"]}','LO-02det.dc.html')]),
      R('E2',v=dict(veic='T3 · doca 1',obs=''),ped=two(f'{VD["id"]} · 3ª de 3',VD['cliente']),lote=twot(f'{VD["lote"]} · {VD["carga_t"]} previstos','separado 09:40 · reservado'),
        doc=[Pt.chip('NF autorizada','green')],etapa=[Pt.chip('Pronta p/ carregar','green'),Pt.br(),Pt.mut('checklist 4/5 · lacre após carregar')],acao=[Pt.mut('aguarda doca 1')]),
      R('E3',ro=True,ped=two(f'{CARGA07["pedido"]} · {CARGA07["id"]}',CARGA07['destino']),lote=twot(f'{CARGA07["lote"]} · {CARGA07["t"]}','paletizado refrigerado'),
        veic=twot('Rota Sul · doca 2','baú refrig.'),doc=[Pt.chip('NF pendente · prot. 8841','red')],
        etapa=[Pt.chip('Pronta p/ carregar · impedida','red'),Pt.br(),Pt.mut('checklist 4/5 · falta NF')],acao=[say('Cobrar NF','nf2')]),
      R('E4',v=dict(veic='T4 · doca 3',obs=''),ped=two(TRANSF['id'],'transferência · '+TRANSF['destino']),
        lote=twot(f'{TRANSF["lote"]} · {n0(TRANSF["kg"])} kg ({TRANSF["sc"]} sc)',f'{TRANSF["origem"]} · a separar'),
        doc=[Pt.chip('Documento interno OK','green')],etapa=[Pt.chip('A separar','gray'),Pt.br(),Pt.mut('checklist 1/5 · documento interno')],acao=[fn('Separar lotes','separar','TR-0459')]),
      R('E5',ro=True,ped=two('PV-028','Torrefação Serra · FOB armazém'),lote=twot('Café beneficiado · 500 sc',f'{D.LOTE_BLOQ["id"]} bloqueado'),
        veic='retirada out/26',doc=[Pt.chip('Não emitido','gray')],etapa=[Pt.chip('Impedida · sem lote apto','red')],acao=[Pt.cta('Abrir inspeção','CO-06det.dc.html')],
        o=[(f'{D.LOTE_BLOQ["id"]} · {n0(D.LOTE_BLOQ["sc"])} sc · {D.LOTE_BLOQ["inspecao"]}','CO-06det.dc.html'),('Pedido PV-028 sem alocação','VE-04.dc.html')]),
    ]
    g_ex=grid(ex_cols,exped,edit=dict(m='form',title='Expedição',sub='Ajuste veículo e doca de uma expedição ainda não carregada. Carregada, impedida ou já saída abre em consulta.',
        fields=[dict(k='veic',l='Veículo · doca',t='sel',req=True,opts=VEICS),dict(k='obs',l='Observação para a equipe',t='area')]),
        search=False,gid='g_ex',total=False)
    po_cols=[C('veic','Veículo'),C('jan','Janela original'),C('cheg','Chegada real',w=220),C('pont','Pontualidade (vs. janela original)',w=260),C('esp','Espera desde a chegada',w=280)]
    g_po=grid(po_cols,[
      R('T1',veic=[Pt.b('T1')],jan='08:00',cheg='— (prev. 09:10, informada 07:40)',pont=[Pt.chip('Atrasado 1h52 e contando','red')],esp='só conta a partir da chegada real',
        o=[('Janela original 08:00 · relógio 09:52 · sem chegada real',None),('Previsão do motorista não é check-in',None)]),
      R('T2',veic=[Pt.b('T2')],jan='08:30',cheg='08:12',pont=[Pt.chip('Antecipado 18 min','green')],esp='23 min até a chamada',o=[('Chegada 08:12 · chamado 08:35',None)]),
      R('T3',veic=[Pt.b('T3')],jan='09:00',cheg='08:50',pont=[Pt.chip('Pontual','green')],esp='1h02 · alerta: espera acumulada ganha prioridade',o=[('Chegada 08:50 · relógio 09:52',None)]),
      R('T4',veic=[Pt.b('T4')],jan='11:00',cheg='09:05',pont=[Pt.chip('Antecipado 1h55','gray')],esp='47 min · aguarda folga',o=[('Chegada 09:05 · janela 11:00 · relógio 09:52',None)]),
      ],edit=dict(m='origin',title='Pontualidade',fields=[]),search=False,gid='g_po',total=False)
    sep_p=painel('ps','Separar lotes da carga','Só aparecem lotes do pedido escolhido; lote em quarentena ou bloqueado fica indisponível com o motivo. Classe e embalagem não mudam sem aceite.',
        p_sel('ps','ped','Pedido · carga')+p_sel('ps','lote','Lote apto e reservado',help='Lotes de outros produtos não aparecem.')+p_inp('ps','qtd','Quantidade a separar','number','ps_un'),
        'Confirmar separação')
    che_p=painel('pc','Registrar chegada na portaria · T1','Chegada real só existe com identificação verificada; aviso do motorista não é check-in.',
        p_inp('pc','data','Data da chegada','date')+p_inp('pc','hora','Hora da chegada','time')
        +p_sel('pc','doc','Identificação',help='Confira CNH do motorista e placa contra a autorização do pedido VD-2101.'),
        'Confirmar chegada do T1')
    EXTRA.append(sep_p); EXTRA.append(che_p)
    enc=(f'<sc-if value="{H("enc_open")}" hint-placeholder-val="{FALSE}"><div role="region" aria-label="Avaliação de encaixe do T4" style="border: 1px solid {LINE}; border-radius: 12px; background: {BG}; padding: 12px 14px; display: flex; flex-direction: column; gap: 6px; font-size: 13px;">'
         f'<div style="display: flex; align-items: center; gap: 8px;"><b style="font-size: 14px; flex-grow: 1;">Encaixe do T4 · {TRANSF["id"]} ({TRANSF["produto"]} ensacado)</b>'
         f'<button type="button" aria-label="Fechar avaliação" title="Fechar avaliação" onClick="{H("enc_close")}" style="{_MINI}">Fechar</button></div>'
         f'<div>Folga: <b>{TRANSF["doca"]} livre de 09:52 até 11:00</b> (68 min). Carga de 45 min + setup 10 min → <b>10:00–10:55</b>.</div>'
         f'<div>Impacto: janela 11:00 da {TRANSF["id"]} é antecipada; <b>Carga 07</b> (doca 2, 11:00) e <b>T3</b> (doca 1) não são afetados. Doca 1 é só granel.</div>'
         f'<div style="{H("enc_cst")}">{H("enc_cond")}</div>'
         f'<div style="display: flex; gap: 8px; flex-wrap: wrap; padding-top: 4px;">'
         f'<button type="button" onClick="{H("enc_yes")}" title="Chamar o T4 para a doca 3 às 10:00" style="{BTN_ST(True,True)}">Encaixar T4 na doca 3 às 10:00</button>'
         f'<button type="button" onClick="{H("enc_no")}" title="Manter o T4 aguardando a janela" style="{BTN_ST(False,True)}">Manter T4 aguardando</button></div></div></sc-if>')
    EXTRAJS[0]=JS_BASE+'''
const LOTES={'TR-0459':[{v:'',t:'Selecione o lote…'},{v:'K26-11',t:'K26-11 · Galpão 2 · 50.000 kg aptos'},{v:'K26-11Q',t:'K26-11 · 10.000 kg em quarentena (NF 4501) · indisponível',dis:true}],
  'PV-028':[{v:'',t:'Nenhum lote apto para este pedido'},{v:'L27-013',t:'L27-013 · 3.690 sc · Bloqueado · INSP-88',dis:true}]};
function EXTRAVALS(self,v){ const s=self.state;
  SAY(self,v,{nf:'NF da Carga 07 reenviada à SEFAZ 09:32 · protocolo 8841 · autorização ainda pendente — solicitar não é obter; a saída continua bloqueada.',
    nf2:'NF da Carga 07 já solicitada 08:55 à Sandra (fiscal) · prazo 10:00 · protocolo 8841 pendente — a saída continua bloqueada (simulado · nenhuma mensagem real enviada).'});
  v.k_patio=s.t1?'4':'3'; v.k_patio_u=s.t1?'T2 em doca · T3 · T4 · T1 chegou '+s.t1:'T2 em doca · T3 pronto · T4 antecipado';
  v.chamar=()=>{ toast(self,'Chamada bloqueada: doca 1 ocupada pelo T2 até a saída (lacre pendente; slot 08:35–09:40 excedido). O T3 é o próximo elegível e será chamado quando a doca 1 liberar'+(s.t1?'; o T1 (chegou '+s.t1+') entra depois do T3':'')+'. Resolva em Conferir carga do T2.'); };
  // ---- separação de lotes ----
  const openSep=(ped)=>PNLopen(self,'ps',{ped:ped||'',lote:'',qtd:ped==='TR-0459'?'10000':''});
  v.separar=(id)=>openSep(id); v.sep_open=()=>openSep('');
  const d=(s.ps&&s.ps.d)||{}; v.ps_un=d.ped==='PV-028'?'sc':'kg';
  PNL(self,v,'ps',{ped:{opts:[{v:'',t:'Selecione o pedido…'},{v:'TR-0459',t:'TR-0459 · KCl 60 % · 10.000 kg · Boa Vista'},{v:'PV-028',t:'PV-028 · Café beneficiado · 500 sc'}],reset:['lote']},
    lote:{opts:(dd)=>LOTES[dd.ped]||[{v:'',t:'Escolha o pedido primeiro'}]},qtd:{}},(dd)=>{ const er={};
    if(!dd.ped){ er.ped='Escolha o pedido.'; return er; }
    if(dd.ped==='PV-028'){ er.lote='Separação recusada: L27-013 bloqueado pela INSP-88 (Qualidade · prazo 25/09). PV-028 segue sem alocação.'; return er; }
    if(self.state.sepTR){ toast(self,'TR-0459 já separada às '+self.state.sepTR+' · nada foi reservado de novo.'); return er; }
    if(dd.lote!=='K26-11') er.lote='Escolha um lote apto.';
    const q=Number(String(dd.qtd).replace(',','.')); if(!(q>0)) er.qtd='Informe a quantidade.'; else if(q>10000) er.qtd='Máximo 10.000 kg (quantidade da carga).';
    if(Object.keys(er).length) return er;
    const hh='09:53';
    setRow(self,'g_ex','E4',r=>{ r.ro=true; r.p.lote=[{k:'txt',t:'K26-11 · '+q.toLocaleString('pt-BR')+' kg'},{k:'br',t:''},{k:'mut',t:'Galpão 2 · separado '+hh}]; r.s.lote='K26-11';
      r.p.etapa=[{k:'chip',t:'Separada · em conferência',c:'yellow'},{k:'br',t:''},{k:'mut',t:'checklist 2/5 · lote conferido'}]; r.s.etapa='Separada'; r.p.acao=[{k:'mut',t:'encaixe avaliado na fila'}]; });
    setRow(self,'g_fi','T4',r=>{ r.p.sit=[{k:'chip',t:'Antecipado',c:'gray'},{k:'br',t:''},{k:'chip',t:'Carga separada',c:'green'}]; r.p.mot=[{k:'txt',t:'Carga separada; só entra com folga, sem prejudicar janelas cumpridas.'}]; });
    self.setState({sepTR:hh}); toast(self,'TR-0459 separada: '+q.toLocaleString('pt-BR')+' kg do K26-11 (Galpão 2) · saldo apto do lote 50.000 → '+(50000-q).toLocaleString('pt-BR')+' kg; os 10.000 kg em quarentena não foram usados.'); return er; });
  // ---- chegada do T1 ----
  v.chegada=()=>PNLopen(self,'pc',{data:'2026-09-23',hora:'09:52',doc:''});
  PNL(self,v,'pc',{data:{},hora:{},doc:{opts:[{v:'',t:'Selecione…'},{v:'ok',t:'CNH e placa conferidas com a autorização'},{v:'nao',t:'Não foi possível conferir'}]}},(dd)=>{ const er={};
    if(!dd.data) er.data='Informe a data.'; if(mins(dd.hora)===null) er.hora='Informe a hora (ex.: 09:52).';
    if(!dd.doc) er.doc='Informe a verificação de identificação.'; else if(dd.doc!=='ok') er.doc='Sem identificação verificada não há check-in: o T1 continua ausente.';
    if(Object.keys(er).length) return er;
    const h=dd.hora.slice(0,5), at=mins(h)-mins('08:00');
    setRow(self,'g_fi','T1',r=>{ r.p.cheg=[{k:'txt',t:h},{k:'br',t:''},{k:'mut',t:'check-in com identificação verificada'}]; r.s.cheg=h;
      r.p.sit=[{k:'chip',t:'Presente · apto',c:'green'},{k:'br',t:''},{k:'chip',t:'Chegou atrasado '+hm(at),c:'yellow'}]; r.s.sit='Presente · apto';
      r.p.mot=[{k:'txt',t:'Chegou '+h+', após a tolerância: entra na primeira oportunidade viável depois do T3, sem interromper carga iniciada; pedido e reserva mantidos.'}];
      r.p.acao=[{k:'mut',t:'check-in '+h}]; });
    setRow(self,'g_po','T1',r=>{ r.v.cheg=h; delete r.s.cheg; delete r.p.cheg; r.p.pont=[{k:'chip',t:'Atrasado '+hm(at)+' vs. janela original',c:'red'}]; r.v.esp='desde '+h; delete r.p.esp; delete r.s.esp;
      r.o=[{t:'Janela original 08:00 · chegada real '+h+' · atraso '+hm(at)}]; });
    self.setState({t1:h}); toast(self,'Chegada do T1 registrada às '+h+' · identificação verificada · entra depois do T3 na doca 1.'); return er; });
  // ---- encaixe do T4 ----
  v.encaixe=()=>self.setState({enc_open:true}); v.enc_open=!!s.enc_open; v.enc_close=()=>self.setState({enc_open:false});
  v.enc_cond=s.sepTR?'Condição atendida: lotes da TR-0459 separados às '+s.sepTR+'.':'Condição pendente: separe os lotes da TR-0459 (K26-11) antes de encaixar.';
  v.enc_cst='font-weight:700;color:'+(s.sepTR?'#1E7A4C':'#B42318')+';';
  v.enc_yes=()=>{ const st=self.state;
    if(st.enc==='ok'){ toast(self,'T4 já chamado para a doca 3 às 10:00 · nada alterado.'); return; }
    if(!st.sepTR){ toast(self,'Encaixe bloqueado: TR-0459 ainda a separar. Use Separar lotes (K26-11) e avalie de novo.'); return; }
    setRow(self,'g_fi','T4',r=>{ r.ro=true; r.p.sit=[{k:'chip',t:'Chamado · doca 3 · 10:00',c:'green'}]; r.s.sit='Chamado';
      r.p.mot=[{k:'txt',t:'Encaixe com folga: doca 3 livre até 11:00; Carga 07 e T3 sem impacto · decisão de Ana às 09:54.'}]; r.p.acao=[{k:'mut',t:'chamado 09:54'}]; });
    self.setState({enc:'ok',enc_open:false}); toast(self,'T4 chamado para a doca 3 às 10:00 (termina 10:55) · decisão registrada com motivo · janelas cumpridas preservadas.'); };
  v.enc_no=()=>{ self.setState({enc:'manter',enc_open:false}); toast(self,'T4 mantido aguardando a janela 11:00 · decisão registrada com motivo.'); };
  // ---- reordenação pela linha ----
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_fi'||!r) return;
    const alvo=Number(r.v.pos)||r.v.pos; const lst=rows.filter(x=>x.id!=='T2'&&x.id!=='C07'&&x!==r).sort((a,b)=>a.v.pos-b.v.pos);
    lst.splice(Math.max(0,alvo-2),0,r); lst.forEach((x,i)=>{ x.v.pos=i+2; delete x.s.pos; delete x.p.pos; });
    r.p.mot=[{k:'txt',t:'Reordenado por Ana às 09:52: '+r.v.pmot+'.'}];
    self.setState({fv:(self.state.fv||4)+1,g2toast:'Fila v'+((self.state.fv||4)+1)+' publicada · '+r.id+' na posição '+alvo+' · motivo, autor e horário registrados; janelas originais e esperas preservadas.'}); };
}
'''
    corpo=(
      kpis([('NO PÁTIO',H('k_patio'),H('k_patio_u')),('ATRASADOS','1','T1 · janela 08:00'),
            ('IMPEDIDAS','1','Carga 07 · NF pendente'),('DOCA OCIOSA EVITÁVEL','0 min','fila reordenada com motivo')])
      + bloco('Fila ao vivo','Chame o próximo elegível; clique na linha para reordenar com motivo.',
              nota(f'Política v4: elegibilidade (presença, prontidão, doca livre, documentos) › janela em risco › perecibilidade › pontualidade › espera acumulada. Tolerância de chegada: {TOLERANCIA}.')
              + g_fi + enc,
              ibtn('Chamar próximo elegível','chamar','truck','Chamar o próximo caminhão elegível para a doca livre'),state='yellow')
      + bloco('Expedições em preparação','Separe os lotes aptos e acompanhe cada carga até a saída.',
              nota('A preparar → Em separação → Conferência → Pronta p/ carregar → Carregada → Saída confirmada. Qualidade, financeiro e documentos são dimensões separadas.')+g_ex,
              ibtn('Separar lotes','sep_open','box','Separar lotes aptos e reservados para um pedido'))
      + bloco('Pontualidade e espera','Confira pontualidade e espera contra a janela original.',g_po,state='gray')
    )
    shell37('LO-02','Expedições e cargas',corpo,
      subtitle='Fila de presentes aptos, bloqueados e atrasados sobre as cargas da agenda; chamar exige doca livre e carga pronta.',
      status=('Doca 1 ocupada · Carga 07 impedida','red'),primary='Conferir carga do T2',primary_href='LO-02det.dc.html',steps=faixa(2),
      footer='Sem conectividade a fila local tem escritor único (portaria) e reconciliação idempotente — nunca duas filas autoritativas (FILA-07). DEMO-19/20.')

    # =====================================================================
    # LO-02det · Conferir carga T2 (saída física única)
    # =====================================================================
    fname='LO-02det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000; PARENT37[fname]='LO-02.dc.html'
    g_cf=grid([C('item','Item',w=170),C('lote','Lote'),C('ped','Pedido (parcela)',a='r'),C('sep','Separado',a='r'),C('car','Carregado',a='r'),C('saldo','Saldo da parcela',w=260),C('conf','Conferência')],[
      R('i1',item=[Pt.b(VD['produto'])],lote=VD['lote'],ped=VD['carga_t'],sep=VD['carga_t'],car=VD['carga_t'],saldo='0 t · 2ª de 3 cargas (37,00 t na 3ª)',conf=[Pt.chip('Conferido','green')],
        o=[(f'Pedido {VD["id"]}: 111 t em 3 cargas de 37,00 t',None),(f'Carregado = líquido do ticket {TICKET["id"]} ({TICKET["liquido"]})',None),('Leitura de código na separação · Rui (expedição)',None)]),
      ],edit=dict(m='origin',title='Conferência',fields=[]),search=False,gid='g_cf',total=False)
    g_ps=grid([C('tk','Ticket'),C('tara','Tara',a='r'),C('bruto','Bruto',a='r'),C('liq','Líquido',a='r'),C('base','Umidade · base'),C('orig','Origem da medição',w=240)],[
      R('p1',ro=True,tk=[Pt.b(TICKET['id']),Pt.txt(' · balança 1')],tara=TICKET['tara'],bruto=TICKET['bruto'],liq=[Pt.b(TICKET['liquido'])],base=TICKET['base'],orig='balança integrada · hoje 09:22'),
      ],edit=dict(m='ro',title='Ticket de pesagem',fields=[dict(k='tara',l='Tara',t='txt'),dict(k='bruto',l='Bruto',t='txt'),dict(k='base',l='Umidade · base',t='txt'),dict(k='orig',l='Origem da medição',t='txt')]),
      search=False,gid='g_ps',total=False)
    g_ck=grid([C('item','Verificação',w=300),C('estado','Estado',w=250),C('resp','Responsável',w=200)],[
      R('prod',ro=True,item='Produto, lote e destino conferem com o pedido',estado=[Pt.chip('Conferido · leitura de código','green')],resp='Rui (expedição)'),
      R('veic',ro=True,item='Veículo compatível · graneleiro com lona',estado=[Pt.chip('Conferido','green')],resp='Portaria'),
      R('lacre',v=dict(num='',apl='Rui (expedição)',confp='',evid=''),item=[Pt.b('Lacre aplicado')],estado=[Pt.chip('Pendente · registre antes da saída','yellow')],resp='Rui (expedição)'),
      R('nf',ro=True,item=f'Documento fiscal · {NF_T2}',estado=[Pt.chip('Autorizada','green')],resp='Sandra (fiscal)'),
      R('fin',ro=True,item='Prontidão financeira/comercial',estado=[Pt.chip('Liberada · condição do pedido','green')],resp='Comercial'),
      ],edit=dict(m='form',title='Registrar lacre',sub='Número e foto ficam na evidência da expedição; quem confere não pode ser quem aplicou.',
        fields=[dict(k='num',l='Nº do lacre',t='txt',req=True,help='Ex.: LC-778120'),dict(k='apl',l='Aplicado por',t='txt',ro=True),
                dict(k='confp',l='Conferido por',t='sel',req=True,opts=['Portaria (Jair)','Sandra (fiscal)']),
                dict(k='evid',l='Evidência',t='sel',req=True,opts=['Foto do lacre anexada'])]),
      search=False,gid='g_ck',total=False)
    g_sa=grid([C('ev','Evento',w=220),C('estado','Estado',w=280),C('quem','Quem · quando',w=220)],[
      R('aut',ro=True,ev='Autorização de saída',estado=[Pt.chip('Aguarda o lacre','gray')],quem='Sandra (fiscal)'),
      R('sai',ro=True,ev='Saída física confirmada',estado=[Pt.chip('Bloqueada · falta lacre e autorização','yellow')],quem='Portaria'),
      R('est',ro=True,ev=f'Baixa de estoque · {VD["lote"]}',estado=[Pt.chip('Na saída · uma única vez','gray')],quem='automática'),
      R('vg',ro=True,ev='Viagem VG-118',estado=[Pt.chip('Aguardando saída','yellow')],quem='cumprida na retirada'),
      ],edit=dict(m='ro',title='Evento da saída',fields=[dict(k='ev',l='Evento',t='txt'),dict(k='quem',l='Quem · quando',t='txt')]),search=False,gid='g_sa',total=False)
    ETAPAS=['A preparar','Em separação','Conferência','Pronta p/ carregar','Carregada','Saída confirmada']
    stp=''.join(f'<span style="{H("stg"+str(i)+"_st")}">{esc(t)}</span>'+(f'<span aria-hidden="true" style="color: {MUTED};">→</span>' if i<len(ETAPAS)-1 else '') for i,t in enumerate(ETAPAS))
    stepper=f'<div aria-label="Etapa da expedição" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12.5px;">{stp}</div>'
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){ const s=self.state; const lac=s.lacre, aut=s.aut, sai=s.saida;
  const cur=sai?5:4;
  for(let i=0;i<6;i++){ v['stg'+i+'_st']='padding:4px 10px;border-radius:999px;font-weight:'+(i===cur?'800':'600')+';'+(i<cur?'background:#E4F3E9;color:#1E7A4C;':(i===cur?'background:#1E7A4C;color:#fff;':'background:#EEF1EE;color:#5B6660;')); }
  v.c_aqui=sai?'Saída confirmada '+sai:(aut?'Autorizada · pronta para sair':(lac?'Lacre registrado':'Carregada · lacre pendente'));
  v.c_falta=sai?'—':(aut?'confirmar saída':(lac?'autorização de saída':'lacre · autorização de saída'));
  v.c_prox=sai?'Acompanhar viagem VG-118':(aut?'Confirmar saída':(lac?'Pedir autorização de saída':'Registrar lacre'));
  v.st_t=sai?'Saída confirmada · doca 1 livre':(aut?'Autorizada · aguarda saída':(lac?'Lacre registrado · aguarda autorização':'Carregada · lacre pendente'));
  v.prim_t=sai?'Saída confirmada':(aut?'Confirmar saída':(lac?'Pedir autorização de saída':'Registrar lacre'));
  v.prim_tip=sai?'A saída já foi confirmada; repetir não duplica a baixa':v.prim_t;
  v.prim_st=PST(!sai);
  v.prim_fn=()=>{ const st=self.state;
    if(st.saida){ toast(self,'Saída já confirmada às '+st.saida+' · mesmo recibo MV-3318 · repetir não duplica a baixa de estoque.'); return; }
    if(!st.lacre){ g2open(self,GR('g_ck'),'lacre',null); return; }
    if(!st.aut){ setRow(self,'g_sa','aut',r=>{ r.p.estado=[{k:'chip',t:'Concedida',c:'green'}]; r.v.quem='Sandra (fiscal) · 09:55'; delete r.s.quem; });
      setRow(self,'g_sa','sai',r=>{ r.p.estado=[{k:'chip',t:'Liberada para confirmar',c:'yellow'}]; });
      self.setState({aut:'09:55'}); toast(self,'Autorização de saída concedida por Sandra (fiscal) às 09:55 (simulado · nenhuma mensagem real enviada).'); return; }
    setRow(self,'g_sa','sai',r=>{ r.p.estado=[{k:'chip',t:'Confirmada · recibo MV-3318',c:'green'}]; r.v.quem='Portaria · 09:58'; delete r.s.quem; });
    setRow(self,'g_sa','est',r=>{ r.p.estado=[{k:'chip',t:'Baixados 37,00 t do MZ-26-03',c:'green'}]; r.v.quem='automática · 09:58'; delete r.s.quem; });
    setRow(self,'g_sa','vg',r=>{ r.p.estado=[{k:'chip',t:'Cumprida na retirada',c:'green'}]; });
    self.setState({saida:'09:58'}); toast(self,'Saída do T2 confirmada às 09:58 · estoque MZ-26-03 baixado 37,00 t uma única vez · VG-118 cumprida na retirada · doca 1 liberada para o T3.'); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_ck'||!r||r.id!=='lacre') return;
    r.ro=true; r.p.estado=[{k:'chip',t:'Aplicado · '+r.v.num,c:'green'}]; r.s.estado='Aplicado'; r.p.resp=[{k:'txt',t:'Rui · conferido por '+r.v.confp}]; r.s.resp='Rui';
    setRow(self,'g_sa','aut',x=>{ x.p.estado=[{k:'chip',t:'A pedir',c:'yellow'}]; });
    self.setState({lacre:r.v.num,g2toast:'Lacre '+r.v.num+' registrado · checklist 5/5 · falta a autorização de saída.'}); };
}
'''
    corpo=(
      continuity('Fila de expedição · T2 chamado 08:35',H('c_aqui'),H('c_falta'),H('c_prox'))
      + stepper
      + bloco('Conferência por pedido e lote','Confira pedido, separado e carregado por lote.',g_cf)
      + bloco('Pesagem e base comercial','Confira tara, bruto e líquido na base comercial; tara não é vendida como produto.',g_ps,state='gray')
      + bloco('Checklist e documentos','Registre o lacre pela linha; a saída exige todos os itens verdes.',
              g_ck+nota('Frete: retirada pelo cliente — custo e transportador do cliente; o rateio da instalação não se aplica a esta carga.'),state='yellow')
      + bloco('Saída','Confirme a saída uma única vez; o estoque baixa nesse evento.',g_sa,
              ilink('Acompanhar viagem','LO-03.dc.html','map','Abrir a viagem VG-118 em Acompanhe viagens'))
    )
    shell37('LO-02','Conferir carga · T2 · VD-2101',corpo,fname='LO-02det.dc.html',crumbs_extra=['T2 · VD-2101 · 2ª de 3'],
      subtitle='Retirada pelo cliente: conferência, pesagem, documentos e saída física única no ponto contratado.',
      status=(H('st_t'),'yellow'),primary_html=PRIM,steps=faixa(2),
      footer='Confirmar saída comprova retirada no ponto contratado; não prova chegada ao destino (48.2). CMD-26 acontece uma única vez, aqui.')

    # =====================================================================
    # LO-03 · Acompanhe viagens
    # =====================================================================
    fname='LO-03.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    vg_cols=[C('vg','Viagem'),C('carga','Carga → destinatário',w=220),C('ev','Eventos · evidência',w=200),C('rec','Recebido · ocorrência',w=200),C('estado','Estado',w=180),C('acao','Ação')]
    viagens=[
      R('VG-117',ro=True,vg=[Pt.b('VG-117')],carga=twot(f'Mamão classe A · {VG117["base"]} · {VG117["pedido"]} · {VG117["lote"]}','→ '+CARGA07['destino']),
        ev=twot('saída 22/09 14:10 · chegada 18:40 (janela até 18:00)','comprovante assinado + 4 fotos'),
        rec=[Pt.b(VG117['aceito']),Pt.txt(' aceitas · '),Pt.b(VG117['recusa']),Pt.txt(' recusadas'),Pt.br(),Pt.mut(f'{VG117["oc"]} · avaria em 2 pallets'),Pt.br(),Pt.chip(f'Caso {VG117["caso"]} aberto','yellow')],
        estado=[Pt.chip('Entregue · aceite parcial','yellow')],acao=[Pt.cta(f'Abrir caso {VG117["caso"]}','VE-06.dc.html',True)],
        o=[(f'Recusa de {VG117["recusa"]} por avaria ({VG117["oc"]}) registrada como caso {VG117["caso"]} do pedido {VG117["pedido"]} · lote {VG117["lote"]}','VE-06.dc.html'),
           (f'Pedido {VG117["pedido"]}: 9,4 t entregues em 22/09 · saldo recusado preservado para decisão comercial','VE-04.dc.html')]),
      R('VG-118',ro=True,vg=[Pt.b('VG-118')],carga=twot(f'{VD["produto"]} · {VD["carga_t"]} (retirada · T2)','→ '+VD['cliente']),ev=twot('carregada 09:22 · saída pendente',f'{TICKET["id"]} + {NF_T2}'),rec=twot('—','lacre pendente'),estado=[Pt.chip('Aguardando saída','yellow')],acao=[Pt.cta('Conferir carga','LO-02det.dc.html')]),
      R('VG-119',v=dict(prev='11:00',transp=FRETE_C07['prestador']),vg=[Pt.b('VG-119')],carga=twot(f'{CARGA07["produto"]} · {CARGA07["t"]} ({CARGA07["id"]} · {CARGA07["pedido"]})','→ '+CARGA07['destino']),
        ev=twot('programada · saída prevista 11:00',FRETE_C07['prestador']),rec=twot('—','NF pendente · Sandra até 10:00'),estado=[Pt.chip('Programada · impedida','red')],acao=[Pt.cta('Resolver na expedição','LO-02.dc.html')]),
      R('VG-112',ro=True,vg=[Pt.b('VG-112')],carga=twot('Diesel S10 · 8 mil L (transferência 19/09)','→ Boa Vista'),ev=twot('entrega 19/09 16:20','romaneio assinado'),rec='8 mil L aceitos · sem ocorrência',estado=[Pt.chip('Concluída no prazo','green')],acao=[Pt.cta('Ver frete','LO-04.dc.html')]),
    ]
    g_vg=grid(vg_cols,viagens,edit=dict(m='form',title='Viagem programada',sub='Ajuste a previsão de saída de uma viagem ainda não iniciada; viagens em curso ou encerradas abrem em consulta.',
        fields=[dict(k='prev',l='Saída prevista',t='txt',req=True,help='Ex.: 11:30 · depende da NF autorizada'),
                dict(k='transp',l='Transportador',t='sel',req=True,opts=[FRETE_C07['prestador'],'Frota própria'])]),
        so={'k':'vg','d':False},gid='g_vg',total=False)
    g_tar=grid([C('reg','Registro',w=240),C('val','Valor',w=520)],[
      R('t1',reg='Janela original (compromisso)',val='22/09 até 18:00 · congelada para o indicador'),
      R('t2',reg='Causa observada',val='chuva forte na BR-101 · informada pelo transportador 16:05'),
      R('t3',reg='Reprogramação aceita',val='chegada 18:40–19:00 · aceite do cliente 16:20 · muda a expectativa, não o compromisso'),
      R('t4',reg='Chegada real',val='22/09 18:40'),
      R('t5',reg='Pontualidade',val=[Pt.chip('Atrasada 40 min vs. compromisso original','red')]),
      ],edit=dict(m='ro',title='Registro da entrega',fields=[dict(k='reg',l='Registro',t='txt'),dict(k='val',l='Valor',t='txt')]),search=False,gid='g_tar',total=False)
    g_rt=grid([C('vg','Viagem'),C('dir','Direcionador · versão'),C('base','Base',a='r'),C('comp','Componentes',w=300),C('tot','Total',t='num',a='r',pre='R$ '),C('rec','Reconciliação',w=240)],[
      R('r1',vg=[Pt.b('VG-117')],dir=RATEIO_V,base=VG117['base'],comp=f'frete base R$ 1.786 (direto) · pedágio R$ {VG117["pedagio"]} (comum, rateado)',tot=VG117['frete'],
        rec=[Pt.chip('Confere · 100% do custo da viagem','green')],o=[('9,4 t × R$ 190/t = R$ 1.786',None),(f'Pedágio R$ {VG117["pedagio"]} rateado por peso líquido',None),(f'Total R$ {n0(VG117["frete"])} = custo único da viagem','LO-04.dc.html')]),
      ],edit=dict(m='origin',title='Rateio da viagem',fields=[]),search=False,gid='g_rt',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_vg'||!r) return;
    r.p.ev=[{k:'txt',t:'programada · saída prevista '+r.v.prev},{k:'br',t:''},{k:'mut',t:r.v.transp}]; r.s.ev='programada '+r.v.prev;
    toast(self,r.id+': saída prevista '+r.v.prev+' com '+r.v.transp+' · previsão de chegada recalculada (estimativa, não nova garantia); a saída continua bloqueada até a NF.'); self.setState({tick:Date.now()}); };
}
'''
    corpo=(
      kpis([('AGUARDANDO SAÍDA','2','VG-118 lacre · VG-119 NF'),('DIVERGÊNCIAS ABERTAS','1',f'VG-117 · caso {VG117["caso"]}'),
            ('CONCLUÍDAS 7 D','2','VG-117 parcial · VG-112'),('OTIF 30 D','92%','contra a janela original')])
      + bloco('Viagens','Acompanhe cada viagem por eventos e abra o caso de cada recusa.',g_vg,
              ilink('Ver financeiro','GE-05.dc.html','cash','Ver recebíveis dos pedidos entregues (GE-05)'))
      + bloco('Entrega tardia · VG-117','Compare o compromisso original com a reprogramação aceita.',g_tar,state='yellow')
      + bloco('Rateio aplicado à viagem','Confira o rateio copiado da versão vigente na expedição.',g_rt,state='gray')
    )
    shell37('LO-03','Viagens e entregas',corpo,
      subtitle='Entrega tardia distingue causa, reprogramação e compromisso original; recusa parcial vira caso comercial com saldo preservado.',
      status=('1 divergência aberta','yellow'),primary='Conciliar frete da VG-117',primary_href='LO-04.dc.html',steps=faixa(3),
      footer='Frete devido ao prestador é obrigação separada do recebível do cliente; o marco de pagamento usa o evento contratado no pedido (48.5). DEMO-08.')

    # =====================================================================
    # LO-04 · Controle fretes
    # =====================================================================
    fname='LO-04.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    PRESTS=[FRETE_C07['prestador'],'TransGrão Ltda','Frota própria']
    ct_cols=[C('prest','Prestador',w=190),C('base','Base'),C('total','Custo total',t='num',a='r',pre='R$ '),C('prazo','Prazo'),C('cons','Conservação'),C('inc','Itens incluídos'),C('sit','Situação',w=260)]
    cot=[
      R('q1',ro=True,prest=[Pt.b(FRETE_C07['prestador'])],base=FRETE_C07['base'],total=FRETE_C07['total'],prazo='chegada até 18:00',cons='baú refrigerado OK',inc='pedágio incluído',
        sit=[Pt.chip('Melhor custo total comparável','green')],o=[('9,6 t × R$ 190/t = R$ 1.824 · pedágio incluído',None),('Documentos RNTRC + RCTR-C válidos',None)]),
      R('q2',ro=True,prest=[Pt.b('Frota própria')],base='512 km × R$ 4,10',total=2099,prazo='até 19:00',cons='sem baú refrigerado',inc='—',
        sit=[Pt.chip('Incompatível · conservação','red')],o=[('512 km × R$ 4,10/km = R$ 2.099 (custo interno)',None),('Sem baú refrigerado: não atende mamão',None)]),
      R('q3',ro=True,prest=[Pt.b('TransGrão Ltda')],base='R$ 2.400/viagem',total=2496,prazo='até 17:00',cons='refrigerado OK',inc='pedágio à parte (+R$ 96)',
        sit=[Pt.chip('Documento vencido · não elegível','red')],o=[('R$ 2.400 + pedágio R$ 96 = R$ 2.496',None),('Seguro RCTR-C vencido em 15/09',None)]),
    ]
    g_ct=grid(ct_cols,cot,edit=dict(m='form',title='Cotação recebida',newTitle='Pedir cotação',
        sub='A cotação compara custo total, base, capacidade, prazo e conservação; não despacha transportador. Pedido de cotação é simulado (nenhuma mensagem real enviada).',
        fields=[dict(k='prest',l='Prestador',t='sel',req=True,opts=PRESTS),dict(k='carga',l='Carga',t='sel',req=True,opts=['Carga 07 · mamão 9,6 t refrigerado',f'{TRANSF["id"]} · KCl 10 t ensacado']),
                dict(k='unid',l='Unidade de cobrança',t='sel',req=True,opts=['R$/t','R$/viagem','R$/km']),dict(k='prazo',l='Resposta até',t='txt',req=True,**{'def':'hoje 10:30'})]),
        add='Pedir cotação',search=False,gid='g_ct',total=False)
    pr_cols=[C('prest','Prestador · rota',w=200),C('preco','Preço',a='r'),C('cond','Condição',w=170),C('docs','Documentos',w=210),C('desemp','Desempenho 90 d',w=170),C('acao','Ação')]
    def prc(v,u): return f'R$ {n0(v) if float(v).is_integer() else str(v).replace(".",",")}{"/"+u.split("/")[1] if "/" in u else ""}'
    prest=[
      R('p1',v=dict(rota='Sede → Vitória/ES',unid='R$/t',pv=190,cond='28 dd após aceite da medição',v90=12),prest=two(FRETE_C07['prestador'],'Sede → Vitória/ES'),preco=[Pt.txt(prc(190,'R$/t'))],
        docs=[Pt.chip('RNTRC + RCTR-C válidos','green')],desemp=twot('12 viagens','OTIF 92% · avaria 0,3%'),acao=[Pt.mut('contrato vigente')]),
      R('p2',v=dict(rota='Sede → Porto de Vitória',unid='R$/viagem',pv=2400,cond='21 dd',v90=4),prest=two('TransGrão Ltda','Sede → Porto de Vitória'),preco=[Pt.txt(prc(2400,'R$/viagem'))],
        docs=[Pt.chip('Seguro vencido 15/09 · não elegível','red')],desemp=twot('4 viagens','OTIF 75% · 1 avaria'),acao=[say('Solicitar documento','doc')]),
      R('p3',v=dict(rota='rotas internas · Boa Vista',unid='R$/km',pv=4.10,cond='custo interno',v90=22),prest=two('Frota própria · 2 caminhões','rotas internas · Boa Vista'),preco=[Pt.txt('R$ 4,10/km')],
        docs=[Pt.chip('Licenças em dia','green')],desemp=twot('22 viagens','ocupação 61%'),acao=[Pt.cta('Ver programação','LO-01.dc.html')]),
    ]
    g_pr=grid(pr_cols,prest,edit=dict(m='form',title='Prestador',sub='Preço e condição valem para novas viagens; viagens vinculadas mantêm o preço do contrato. Documento vencido tira a elegibilidade sem apagar o histórico.',
        fields=[dict(k='rota',l='Rota',t='txt',req=True),dict(k='unid',l='Unidade de cobrança',t='sel',req=True,opts=['R$/t','R$/viagem','R$/km']),
                dict(k='pv',l='Preço',t='num',req=True,min=0.01,u='R$'),dict(k='cond',l='Condição de pagamento',t='txt',req=True)]),
        search=False,gid='g_pr',total=False)
    sv_cols=[C('vg','Viagem'),C('prest','Prestador',w=150),C('med','Medição',w=200),C('rat','Rateio aplicado',w=150),C('val','Valor do serviço',t='num',a='r',pre='R$ '),C('estado','Estado',w=220),C('acao','Ação')]
    g_sv=grid(sv_cols,[
      R('VG-112',vg=[Pt.b('VG-112')],prest='Frota própria',med='8 mil L · romaneio conferido',rat='—',val='',estado=[Pt.chip('Apropriado à transferência','green')],acao=[Pt.mut('custo interno')],
        o=[('Custo interno apropriado uma única vez à transferência',None)]),
      R('VG-117',vg=[Pt.b('VG-117')],prest=FRETE_C07['prestador'],med='9,4 t entregues · medição aceita hoje 08:50',rat=RATEIO_V,val=VG117['frete'],
        estado=[Pt.chip('A encaminhar ao financeiro','yellow')],acao=[fn('Encaminhar pagamento','pagar','VG-117')],
        o=[('9,4 t × R$ 190/t = R$ 1.786 + pedágio R$ 96 = R$ 1.882',None),(f'Avaria de {VG117["recusa"]} tratada no caso {VG117["caso"]}; não descontada do frete sem acordo','VE-06.dc.html'),('Rateio da viagem','LO-03.dc.html')]),
      ],edit=dict(m='origin',title='Serviço de frete',fields=[]),search=False,gid='g_sv',total=False)
    g_ra=grid([C('dir','Direcionador',w=170),C('ver','Versão'),C('quando','Quando usar',w=230),C('salv','Salvaguardas',w=420)],[
      R('d1',dir=[Pt.b('Peso líquido (t)')],ver='v2 · vigente desde 01/08',quando='padrão inicial',salv='custos exclusivos de um pedido atribuídos antes de ratear o saldo comum'),
      R('d2',dir='Peso × distância',ver='opcional',quando='viagens com trechos distintos',salv='cada trecho só para os itens transportados nele; base zero gera pendência, não rateio silencioso'),
      R('d3',dir='Posições de pallet',ver='opcional',quando='quando volume/pallet é a restrição',salv='bases não comparáveis não se somam'),
      ],edit=dict(m='ro',title='Direcionador de rateio',fields=[dict(k='ver',l='Versão',t='txt'),dict(k='quando',l='Quando usar',t='txt'),dict(k='salv',l='Salvaguardas',t='txt')]),
      search=False,gid='g_ra',total=False)
    EXTRAJS[0]=JS_BASE+'''
function prc(v,u){ const n=Number(v); return 'R$ '+n.toLocaleString('pt-BR',{minimumFractionDigits:(n%1?2:0),maximumFractionDigits:2})+'/'+String(u).split('/')[1]; }
function EXTRAVALS(self,v){ const s=self.state;
  SAY(self,v,{doc:'Pedido de seguro RCTR-C renovado enviado à TransGrão Ltda (simulado · nenhuma mensagem real enviada) · segue inelegível até o documento ser validado.'});
  v.prim_t=s.ct?'Rota Sul contratada':'Contratar Rota Sul · R$ 1.824'; v.prim_st=PST(!s.ct);
  v.prim_tip=s.ct?'Contrato já registrado (CT-0912)':'Contratar o melhor custo total elegível para a Carga 07';
  v.prim_fn=()=>{ if(self.state.ct){ toast(self,'Rota Sul já contratada · mesmo recibo CT-0912 · nada duplicado.'); return; }
    setRow(self,'g_ct','q1',r=>{ r.p.sit=[{k:'chip',t:'Contratada · CT-0912',c:'green'}]; r.s.sit='Contratada'; });
    const sp=GR('g_sv'); const rows=g2clone(g2rows(self,sp)); rows.push({id:'VG-119',v:{rat:'Rateio v2 · peso líquido',val:1824},s:{},p:{vg:[{k:'b',t:'VG-119'}],prest:[{k:'txt',t:'Rota Sul Transportes'}],
      med:[{k:'txt',t:'medição na entrega (9,6 t)'}],estado:[{k:'chip',t:'Contratado · aguarda entrega',c:'gray'}],acao:[{k:'mut',t:'paga após medição'}]},
      o:[{t:'9,6 t × R$ 190/t = R$ 1.824 · pedágio incluído'},{t:'Contrato CT-0912 · medição e NF do serviço exigidas na entrega'}]});
    g2set(self,'g_sv',{rows});
    self.setState({ct:'CT-0912'}); toast(self,'Rota Sul contratada · R$ 1.824 (9,6 t × R$ 190/t) · VG-119 vinculada ao contrato CT-0912 · medição e NF do serviço exigidas na entrega.'); };
  v.pagar=(id)=>{ if(self.state.pg){ toast(self,'VG-117 já encaminhada · título CP-2291 · nada duplicado.'); return; }
    setRow(self,'g_sv','VG-117',r=>{ r.p.estado=[{k:'chip',t:'Encaminhado · CP-2291',c:'green'},{k:'br',t:''},{k:'mut',t:'vence 21/10'}]; r.s.estado='Encaminhado'; r.p.acao=[{k:'link',t:'Ver contas a pagar',h:'GE-04.dc.html'}]; });
    self.setState({pg:1}); toast(self,'Serviço da VG-117 encaminhado ao financeiro · título CP-2291 de R$ 1.882 · vence 21/10 (28 dd após o aceite da medição) · custo apropriado uma única vez.'); };
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_pr'){ r.p.preco=[{k:'txt',t:prc(r.v.pv,r.v.unid)}]; r.s.preco=r.p.preco[0].t; const nm=(r.p.prest&&r.p.prest[0])?r.p.prest[0].t:''; r.p.prest=[{k:'b',t:nm},{k:'br',t:''},{k:'mut',t:r.v.rota}]; self.setState({tick:Date.now()}); return; }
    if(gid==='g_ct' && isNew(r)){ r.v.__ok=1; r.ro=true; r.p.prest=[{k:'b',t:r.v.prest}]; r.s.prest=r.v.prest; r.v.base=String(r.v.carga).split(' ·')[0]+' · '+r.v.unid; r.v.total='';
      r.p.sit=[{k:'chip',t:'Solicitada · resposta até '+r.v.prazo,c:'gray'}]; r.s.sit='Solicitada';
      toast(self,'Cotação pedida a '+r.v.prest+' ('+r.v.carga+') · resposta até '+r.v.prazo+' (simulado · nenhuma mensagem real enviada).'); self.setState({tick:Date.now()}); } };
}
'''
    corpo=(
      kpis([('PRESTADORES ELEGÍVEIS','1','+ frota própria · TransGrão inelegível'),('COTAÇÃO ABERTA','1','Carga 07 · até 10:30'),
            ('A PAGAR','R$ 1.882','VG-117 · medição aceita'),('OTIF MÉDIO 30 D','92%','vs. janela original')])
      + bloco('Comparar cotações · Carga 07','Compare o custo total na mesma base e contrate a melhor opção elegível.',
              nota('Mesma base: 9,6 t · 512 km · refrigerado. Sugestão não despacha transportador.')+g_ct,state='yellow')
      + bloco('Prestadores e frota','Mantenha preço e condição de cada prestador; clique na linha para ajustar.',g_pr)
      + bloco('Conferência e pagamento do serviço','Encaminhe ao pagamento só o serviço medido e aceito.',g_sv,
              ilink('Ver contas a pagar','GE-04.dc.html','cash','Abrir contas a pagar (GE-04)'))
      + bloco('Padrão de rateio da instalação','Consulte os direcionadores e a versão vigente copiada para cada viagem.',g_ra,state='gray')
    )
    shell37('LO-04','Fretes e transportadores',corpo,
      subtitle='Cotação, contrato, vínculo com viagens e conferência do serviço; desempenho medido contra a janela original.',
      status=('1 cotação a decidir · até 10:30','yellow'),primary_html=PRIM,steps=faixa(4),
      footer='Contratar é ação autorizada; cotação ou sugestão de rota não despacha transportador (48.3). Documento fiscal, conta a pagar e medição não triplicam o custo.')
