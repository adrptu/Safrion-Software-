# -*- coding: utf-8 -*-
"""Área Suprimentos (módulo OCULTO no menu, preservado) — padrão G2 de 25/09/2026.
SU-01 Necessidades e cobertura · SU-02 Políticas de estoque · SU-03 Saldos e lotes (+SU-03det reserva em conflito F26-02) ·
SU-04 Solicitações e cotações · SU-05 Contratos, pedidos e entregas (+SU-05det contrato CT-2026-11) · SU-06 Recebimentos e divergências ·
SU-07 Requisições e entregas (+SU-07det REQ-031) · SU-08 Transferências e movimentos · SU-09 Inventários e ajustes.

Padrão: toda tabela é grid(); clicar na linha abre o painel lateral pela direita — formulário tipado nos registros editáveis,
consulta nos históricos e origem/memória de cálculo nos indicadores calculados. Ações de processo mudam o estado da própria tela
(linha, indicador, selo do cabeçalho) e recusam repetição com recibo. Módulo não sequencial: sem faixa de etapas.

observacoes (dados locais coerentes com dados2/dados; declarados):
- Fonte única: dados2 (PEDIDOS, RECEBIMENTOS, REQUISICOES, LOTES, CONTAGENS, FORNECEDORES, PROPOSTAS, SOL-2026-07, demanda) e dados (O.S.).
- PC-088 = Fertisul (dados2), R$ 2,33/kg, contrato CT-2026-11 de 140 t; pagamento 28 d, título único (sem barter).
- PC-090/PC-091 = sementes (dados2). O diesel passou a PC-093 e o kit de filtros a PC-094 (antes PC-090/PC-091 neste módulo).
- REQ-037 (local): KCl da OS-0420, lote antigo K26-07 (zerado): 4.800 kg entregues, 3.600 consumidos em 30 ha, 1.200 kg em custódia de Carlos;
  v3 (−12 % só no saldo de 70 ha) = 7.392 kg residuais. REQ-039 (local): OS-0424 · 65 L do F26-02 (a reserva de 65 L de dados2).
- REQ-040 = a mesma de areas/processo_estoque.py (OS-0425 · NPK 11.400 kg contra 8.000 kg no lote N26-03).
- DEMO-18 rebaseado nos saldos de dados2: F26-02 tem 545 L, 65 L reservados (OS-0424) e 480 L livres; a reserva planejada da
  Safra 2026/27 (625,2 L de Fungicida A) chegou junto e recebeu conflito; a pendência de 145,2 L é o líquido da SOL-2026-07.
- MAP 11-52 · lote M26-05 (sobras, quarentena) guarda as devoluções da REQ-031; não entra no disponível de dados2.
- Diesel, rolamento, peças, consignado Herbicida Z e frete FOB (R$ 0,06/kg em fertilizantes; 1,5 % nos demais) são constantes locais.
- SU-06: NF 8812 (diesel PC-093, R$ 5,96/L × contrato R$ 5,84/L) e PC-094 são locais; laudo LAB-4501 / recibo LQ-2031 simulados.
- SU-07: REQ-038 (OS-0418, dados2) substitui a antiga REQ-044; REQ-041 nasce do painel Solicitar (Adjuvante 87,5 L = 0,25 L/ha × 350 ha).
- SU-08: TR-0452 chega ao Almox. em lote novo G26-15 (não altera G26-14 de dados2); MV-8790/ES-0071/MV-8791 = estorno do lote S58-0726 digitado errado.
- SU-09: INV-2609/2610/2611 = dados2.CONTAGENS; INV-2612 (filtro de óleo, oficina) é local.
- DEMO-02 em SU-01: demanda KCl = 140 t (plano S2627 + OS-0420 + origem local "cobertura nov · programa CT-2026-11" que fecha o
  contrato); falta firme 140 − 50 − 40 = 50 t; as 10 t em quarentena aparecem só como "coberto se o laudo aprovar".
- OS-0420 segue 30/70 ha de dados.OS (o card 60/40 do PRD fica para reconciliação).
"""
import json, os, datetime as _dt
from engine import (grid, esc, icon, chip, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, GRAYS, SH, DISP,
                    BTN_ST, EXTRA, EXTRAJS, _MINI, _MINIP)
import engine as E
import ui37
from ui37 import shell37, continuity, tabs, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
for _f in ('SU-05.dc.html','SU-05det.dc.html'): ui37.H_OVR.pop(_f,None)   # layout novo: alturas antigas não valem

# ======================= formatação e dados locais =======================
def nf(x,d=0):
    s=f'{x:,.{d}f}'; return s.replace(',','X').replace('.',',').replace('X','.')
def nq(x):
    return nf(x,0) if abs(x-round(x))<1e-6 else nf(x,1)
def dm(iso): a=str(iso).split('-'); return f'{a[2]}/{a[1]}' if len(a)==3 else str(iso)
HOJE=_dt.date(2026,9,23)
FORN={f['id']:f['nome'] for f in D2.FORNECEDORES}
PED={p['id']:p for p in D2.PEDIDOS}
REQS={r['id']:r for r in D2.REQUISICOES}
LOT={l['lote']:l for l in D2.LOTES}
PC88=PED['PC-088']; K11=LOT['K26-11']; F02=LOT['F26-02']; M07=LOT['M26-07']
R31=REQS['REQ-031']; R35=REQS['REQ-035']; R36=REQS['REQ-036']; R38=REQS['REQ-038']
PRECO={}
for _p in D2.PLANOS:
    for _a in _p['atividades']:
        for _x in _a['prods']: PRECO.setdefault(_x['prod'],_x['preco'])
PRECO.update({'Semente de soja 58 W':9.50,'Semente de soja 62 X':9.50,'KCl 60%':2.40})
KCL_T=PC88['preco']*1000                 # R$/t do contrato Fertisul (2.330)
KCL_DEM=140000                           # DEMO-02: demanda do KCl = programa do CT-2026-11 (140 t)
# REQ-037 · KCl da OS-0420 (REC-014 v2 120 kg/ha; v3 −12 % só no saldo)
DOSE_KCL=120; SALDO_HA=D.OS[1]['saldo']; REAL_HA=D.OS[1]['realizado']
R37=dict(id='REQ-037',os='OS-0420',item='KCl 60%',un='kg',lote='K26-07',solicitado=DOSE_KCL*100,entregue=4800,consumido=DOSE_KCL*REAL_HA,
         custodia=4800-DOSE_KCL*REAL_HA,resid_v2=DOSE_KCL*SALDO_HA,resid_v3=round(DOSE_KCL*0.88*SALDO_HA))
R39=dict(id='REQ-039',os='OS-0424',item='Fungicida A',un='L',lote='F26-02',solicitado=F02['reservado'],reservado=F02['reservado'])
R40=dict(id='REQ-040',os='OS-0425',item='NPK 20-05-20',un='kg',lote='N26-03',solicitado=11400,disp=LOT['N26-03']['fisico'])
DOSE_SEM=52   # kg/ha · plano SOJA-AT (dados2) → REQ-036 5.200 / 1.560 / 3.640 kg
SEM_RESID=R36['solicitado']-R36['entregue']
DIESEL=dict(ped='PC-093',ctr='CT-2026-03',q=15000,preco=5.84,tanque=12400,res=3000,demanda=35400)
PLANO_FA=round(D2.demanda('S2627')['Fungicida A']['bruta'],1)            # 625,2 L
SOL_FA=round(D2.demanda('S2627')['Fungicida A']['liq'],1)                 # 145,2 L
LIVRE_FA=F02['fisico']-F02['quarentena']-F02['reservado']                  # 480 L
# revisão do CTL-4 (S4): com a demanda única (O.S. pelo pendente, plano sem a parte delas) o Fungicida A não tem pendência na SOL-2026-07 e o
# DEMO-18 deixa de ter conflito; SU-03 e SU-03det mostram a reserva da OS-0424 e o uso da safra que o lote cobre (nunca "pendência 0 L")
CONFL_FA=SOL_FA>0.05

# ======================= blocos, botões e KPIs =======================
def bloco(titulo,desc,corpo,acao='',tit_hole=False):
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    t=titulo if tit_hole else esc(titulo)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 260px;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">{acao}</div></div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def _ic(ic,c='currentColor'): return icon(ic,14,c) if ic else ''
def mini(fn,rotulo,dica,ic=None,prim=False):
    return (f'<button type="button" onClick="{H(fn)}" title="{esc(dica)}" style="{_MINIP if prim else _MINI} display: inline-flex; align-items: center; gap: 6px;">'
            f'{_ic(ic)}{esc(rotulo)}</button>')
def alink(href,rotulo,dica,ic=None):
    return (f'<a href="{href}" title="{esc(dica)}" style="{_MINI} display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">{_ic(ic)}{esc(rotulo)} ›</a>')
def primb(fn,rotulo,ic=None):
    return f'<button type="button" onClick="{H(fn)}" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 8px;">{_ic(ic,"#fff")}{esc(rotulo)}</button>'
def prima(href,rotulo):
    return f'<a href="{href}" style="{BTN_ST(True)} text-decoration: none; display: inline-flex; align-items: center;">{esc(rotulo)}</a>'
def nota(t): return f'<div style="font-size: 12px; color: {MUTED}; padding: 8px 4px 0; line-height: 1.45;">{esc(t)}</div>'
def kpis(items):
    """[(rótulo, valor ou buraco, complemento)] — valor aceita buraco {{x}} para indicador que muda na tela."""
    cells=''.join(f'<div style="flex: 1 1 0; min-width: 0; padding: 12px 16px; background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; gap: 4px;">'
                  f'<div style="font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: {MUTED}; font-weight: 700;">{esc(l)}</div>'
                  f'<div style="font-family: {DISP}; font-size: 24px; font-weight: 700; letter-spacing: -.02em; font-variant-numeric: tabular-nums; line-height: 1.1;">{v}</div>'
                  f'<div style="font-size: 12px; color: {MUTED};">{u}</div></div>' for l,v,u in items)
    return f'<div style="display: flex; gap: 12px;">{cells}</div>'
def R(id,v,p=None,**kw): return dict(id=id,v=v,s={},p=p or {},**kw)
def txt(t): return {'k':'txt','t':t}
def b(t): return {'k':'b','t':t}
def mut(t): return {'k':'mut','t':t}
def ch(t,c='gray'): return {'k':'chip','t':t,'c':c}
def lk(t,h): return {'k':'link','t':t,'h':h}
def cta(t,h,u=False): return {'k':'cta','t':t,'h':h,'u':u}
def act(t,fn,u=False): return {'k':'act','t':t,'fn':fn,'u':u}
BR={'k':'br','t':''}
def fs(k,l,t='txt',**kw): return dict(k=k,l=l,t=t,**kw)

# ======================= JS comum: painel lateral, selo dinâmico, utilidades =======================
SUJS=r'''
function GR(id){ return GRIDS.find(g=>g.id===id); }
function RW(self,id){ return g2rows(self,GR(id)); }
function RF(self,gid,rid){ return g2find(RW(self,gid),rid); }
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function dm(s){ if(!s) return '—'; const a=String(s).split('-'); return a.length===3? a[2]+'/'+a[1] : String(s); }
const HOJE='2026-09-23';
function addd(s,n){ const d=new Date(s+'T12:00:00'); d.setDate(d.getDate()+Number(n||0)); return d.toISOString().slice(0,10); }
function ddiff(a,b){ return Math.round((new Date(b+'T12:00:00')-new Date(a+'T12:00:00'))/86400000); }
function chipc(t,c){ return {k:'chip',t:t,c:c}; }
function T(t){ return {k:'txt',t:t}; } function B(t){ return {k:'b',t:t}; } function M(t){ return {k:'mut',t:t}; } const BRK={k:'br',t:''};
function CST(c){ const cc=G2C[c]||G2C.gray; return {st:'display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';',dot:'width:6px;height:6px;border-radius:999px;background:'+cc[0]+';'}; }
function hstatus(v,t,c){ const s=CST(c); v.hs_t=t; v.hs_st=s.st; v.hs_dot=s.dot; }
function faixa(iso){ const d=ddiff(HOJE,iso); if(d<0) return chipc(dm(iso)+' · atrasado','red'); if(d===0) return chipc('hoje','red'); if(d<=3) return chipc(dm(iso)+' · até 3 dias','yellow'); return T(dm(iso)); }
function setRows(self,gid,fn){ const rows=g2clone(RW(self,gid)); fn(rows); g2set(self,gid,{rows:rows}); return rows; }
function toast(self,t){ self.setState({g2toast:t}); }
function sims(self,v){ Object.keys(SIMS).forEach(k=>{ v['sim_'+k]=()=>toast(self,SIMS[k]); }); }
// painel lateral genérico: campos tipados, validação junto ao campo, Salvar/Cancelar e aviso de alteração não salva
function pnOpen(self,id,init){ const P=PN[id]; const d={}; P.fields.forEach(f=>{ d[f.k]=(init&&init[f.k]!==undefined)?String(init[f.k]):(f.def!==undefined?String(f.def):''); });
  self.setState({pn:id,pd:d,po:Object.assign({},d),pe:{},pw:false}); }
function pnVals(self,v){ const st=self.state, id=st.pn, P=id?PN[id]:null; v.pn_open=!!P;
  Object.keys(PN).forEach(k=>{ v['open_'+k]=()=>pnOpen(self,k); });
  if(!P){ v.pn_title=''; v.pn_sub=''; v.pn_fields=[]; v.pn_lines=[]; v.pn_ok_t=''; v.pn_warn=false; v.pn_haserr=false; v.pn_cancel=()=>{}; v.pn_ok=()=>{}; v.pn_key=()=>{}; v.pn_discard=()=>{}; v.pn_keep=()=>{}; return; }
  const d=st.pd||{}, e=st.pe||{};
  v.pn_title=P.title; v.pn_sub=P.sub||''; v.pn_ok_t=P.ok; v.pn_warn=!!st.pw; v.pn_haserr=Object.keys(e).length>0;
  v.pn_lines=(LINES[id]?LINES[id](self,d):[]).map(x=>({t:x[0],v:x[1]}));
  const vis=P.fields.filter(f=>!f.cond||String(d[f.cond.k])===String(f.cond.eq));
  v.pn_fields=vis.map(f=>({l:f.l+(f.req?' *':''), fid:'pn_'+f.k, isSel:f.t==='sel', isTxt:(f.t!=='sel'&&f.t!=='area'), isArea:f.t==='area', type:(f.t==='date'?'date':'text'),
     v:(d[f.k]===undefined?'':d[f.k]), opts:(f.opts||[]).map(o=>({v:o,t:o})), u:f.u||'', hasU:!!f.u, help:f.help||'', hasHelp:!!f.help, err:!!e[f.k], errMsg:e[f.k]||'', dis:!!f.ro,
     ist:'font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;border:1px solid '+(e[f.k]?'#B42318':'#E4E9E5')+';background:'+(f.ro?'#F4F6F3':'#FFFFFF')+';color:#15201A;',
     set:(ev)=>{ const s=self.state; const nd=Object.assign({},s.pd,{[f.k]:ev.target.value}); const ne=Object.assign({},s.pe); delete ne[f.k]; self.setState({pd:nd,pe:ne,pw:false}); }}));
  const dirty=()=>Object.keys(self.state.pd||{}).some(k=>String(self.state.pd[k])!==String((self.state.po||{})[k]));
  v.pn_cancel=()=>{ if(dirty()) self.setState({pw:true}); else self.setState({pn:null}); };
  v.pn_discard=()=>self.setState({pn:null,pw:false}); v.pn_keep=()=>self.setState({pw:false});
  v.pn_key=(ev)=>{ if(ev&&ev.key==='Escape'){ ev.preventDefault(); v.pn_cancel(); } };
  v.pn_ok=()=>{ const s=self.state; const dd=s.pd||{}; const er={};
    vis.forEach(f=>{ if(f.ro) return; const val=String(dd[f.k]||'').trim(); if(f.req&&!val){ er[f.k]='Informe '+f.l.toLowerCase().replace(/ \(.*\)$/,'')+'.'; return; }
      if(f.t==='num'&&val){ const n=g2num(val); if(isNaN(n)){ er[f.k]='Use um número (ex.: 12,5).'; return; }
        if(f.min!==undefined&&n<f.min){ er[f.k]='Mínimo '+nf(f.min,f.d||0)+(f.u?' '+f.u:'')+'.'; return; }
        const mx=(f.maxfn&&MAXFN[f.maxfn])?MAXFN[f.maxfn](self,dd):f.max; if(mx!==undefined&&mx!==null&&n>mx){ er[f.k]='Máximo '+nf(mx,f.d||0)+(f.u?' '+f.u:'')+'.'; return; } } });
    if(!Object.keys(er).length && CHECK[id]) Object.assign(er,CHECK[id](self,dd)||{});
    if(Object.keys(er).length){ self.setState({pe:er}); return; }
    const msg=RUN[id](self,dd); self.setState({pn:null,pw:false,pe:{},g2toast:msg||''}); }; }
'''
def js(pn,code,simsd=None):
    EXTRAJS[0]=('const PN = '+json.dumps(pn,ensure_ascii=False)+';\nconst SIMS = '+json.dumps(simsd or {},ensure_ascii=False)+
                ';\nconst RUN = {}, CHECK = {}, MAXFN = {}, LINES = {};\n'+SUJS+code)
def painel():
    """painel lateral (direita) do PN ativo: campos, resumo, erros junto ao campo, Salvar/Cancelar e aviso de não salvo."""
    EXTRA.append(
      f'<sc-if value="{H("pn_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("pn_cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("pn_title")}" onKeyDown="{H("pn_key")}" style="position: relative; width: 460px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">{H("pn_title")}</h2>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pn_cancel")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H("pn_sub")}</div>'
      f'<sc-for list="{H("pn_lines")}" as="ln" hint-placeholder-count="0"><div style="display: flex; justify-content: space-between; gap: 10px; padding: 5px 0; border-bottom: 1px solid {LINE}; font-size: 13px;"><span style="color: {MUTED};">{H("ln.t")}</span><b style="text-align: right;">{H("ln.v")}</b></div></sc-for>'
      f'<sc-if value="{H("pn_haserr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div></sc-if>'
      f'<sc-for list="{H("pn_fields")}" as="f" hint-placeholder-count="3"><div style="display: flex; flex-direction: column; gap: 4px;">'
      f'<label for="{H("f.fid")}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{H("f.l")}</label><div style="display: flex; align-items: center; gap: 8px;">'
      f'<sc-if value="{H("f.isSel")}" hint-placeholder-val="{F()}"><select id="{H("f.fid")}" value="{H("f.v")}" onChange="{H("f.set")}" disabled="{H("f.dis")}" style="{H("f.ist")}"><sc-for list="{H("f.opts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></sc-if>'
      f'<sc-if value="{H("f.isTxt")}" hint-placeholder-val="{T()}"><input id="{H("f.fid")}" type="{H("f.type")}" value="{H("f.v")}" onChange="{H("f.set")}" readOnly="{H("f.dis")}" style="{H("f.ist")}"></sc-if>'
      f'<sc-if value="{H("f.isArea")}" hint-placeholder-val="{F()}"><textarea id="{H("f.fid")}" value="{H("f.v")}" onChange="{H("f.set")}" style="{H("f.ist")} min-height: 64px; resize: vertical;"></textarea></sc-if>'
      f'<sc-if value="{H("f.hasU")}" hint-placeholder-val="{F()}"><span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{H("f.u")}</span></sc-if></div>'
      f'<sc-if value="{H("f.err")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("f.errMsg")}</span></sc-if>'
      f'<sc-if value="{H("f.hasHelp")}" hint-placeholder-val="{F()}"><span style="font-size: 11.5px; color: {MUTED};">{H("f.help")}</span></sc-if></div></sc-for>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("pn_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pn_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("pn_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("pn_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
      f'<button type="button" onClick="{H("pn_ok")}" style="{BTN_ST(True,True)}">{H("pn_ok_t")}</button></div></aside></div></sc-if>')
MARK='§STATUS§'
def dyn_status(fname):
    """troca o selo estático do cabeçalho por um selo ligado ao estado da tela (buracos hs_t/hs_st/hs_dot)."""
    p=os.path.join(E.P,fname); s=open(p).read(); old=chip(MARK,'gray')
    assert old in s, 'selo do cabeçalho não encontrado'
    s=s.replace(old,f'<span style="{H("hs_st")}"><span style="{H("hs_dot")}"></span>{H("hs_t")}</span>',1); open(p,'w').write(s)

def build():
    su01(); su02(); su03(); su03det(); su04(); su05(); su05det(); su06(); su07(); su07det(); su08(); su09()

# ================= SU-01 · Necessidades e cobertura =================
SEG=7   # dias de segurança antes do prazo de entrega
def _lead(g): return min((p['prazo'] for p in D2.PROPOSTAS.get(g,[])),default=10)
def _faixa(iso):
    d=(_dt.date.fromisoformat(iso)-HOJE).days
    return 'atrasada' if d<0 else ('vence hoje' if d==0 else ('até 3 dias' if d<=3 else 'no prazo'))
def _origens():
    out={}
    for c in D2.CULTIVOS['S2627']:
        if not c['plano']: continue
        pl=D2.PLANO[c['plano']]
        for a in pl['atividades']:
            dt=D2.data_atividade(c,a)
            for i,p in enumerate(a['prods']):
                dose=D2.AJUSTES.get(c['id'],{}).get(f"{a['id']}|{i}",p['dose'])
                nm=D2.prod_nome(p['prod'],c)
                out.setdefault(nm,[]).append(dict(t=f"{c['local']} · {a['nome']}",dt=dt.isoformat(),q=dose*c['area'],
                    memo=f"{nf(dose,2 if dose<10 else 0)} {p['un']}/ha × {nf(c['area'])} ha",
                    o=[dict(t=f"Cultivo {c['local']} · {c['cultura']} {c['variedade']} · {nf(c['area'])} ha"),
                       dict(t=f"Plano {pl['nome']} v{pl['versao']} · {a['nome']} · {a['g']['tipo']} {a['g']['dias'] if a['g']['dias'] is not None else ''}".strip()),
                       dict(t=f"{nf(dose,2 if dose<10 else 0)} {p['un']}/ha × {nf(c['area'])} ha = {nf(dose*c['area'],1 if p['un']=='L' else 0)} {p['un']}"),
                       dict(t='Abrir em Planejar safra',h='SAF.dc.html')]))
    return out
def _sup_man_js():
    import dados_manutencao as DM
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sup_necessidades.js'), encoding='utf-8') as f:
        return DM.js_prefixo() + f.read()

def su01():
    fname='SU-01.dc.html'; E._reset_screen(fname)
    dem=D2.demanda('S2627'); org=_origens()
    org.setdefault('KCl 60%',[]).append(dict(t=f'OS-0420 · plantio T4 · saldo {SALDO_HA} ha (v3)',dt='2026-09-24',q=R37['resid_v3']-R37['custodia'],
        memo=f"{nf(R37['resid_v3'])} kg da v3 − {nf(R37['custodia'])} kg já em custódia",
        o=[dict(t=f"REC-014: {DOSE_KCL} kg/ha; v3 −12 % só no saldo de {SALDO_HA} ha = {nf(R37['resid_v3'])} kg"),dict(t=f"{nf(R37['custodia'])} kg já estão com Carlos (REQ-037) e saem da conta"),dict(t='Abrir a requisição',h='SU-07.dc.html')]))
    org.setdefault('Semente de soja 58 W',[]).append(dict(t=f'OS-0420 · plantio T4 · saldo {SALDO_HA} ha',dt='2026-09-24',q=SEM_RESID,
        memo=f'{DOSE_SEM} kg/ha × {SALDO_HA} ha',o=[dict(t=f"REQ-036: {nf(R36['solicitado'])} kg pedidos = {DOSE_SEM} kg/ha × 100 ha; {nf(R36['entregue'])} kg plantados em {REAL_HA} ha"),dict(t='Abrir a requisição',h='SU-07.dc.html')]))
    _kq=KCL_DEM-sum(x['q'] for x in org['KCl 60%'])   # DEMO-02: programa do CT-2026-11 fecha a demanda em 140 t
    org['KCl 60%'].append(dict(t='Cobertura nov · T4, T3, P1 e P2 (programa CT-2026-11)',dt='2026-11-03',q=_kq,
        memo=f'{KCL_DEM//1000} t do contrato − origens do plano e da OS-0420',
        o=[dict(t=f"CT-2026-11: {KCL_DEM//1000} t (cargas 1–2 adubação · 3 plantio T4 · 4 cobertura nov)"),dict(t=f'Parcela fora do plano S2627 = {nf(_kq)} kg'),dict(t='Abrir o contrato',h='SU-05det.dc.html')]))
    rows=[]; nfalta=0; natr=0
    for nm,o in sorted(dem.items(),key=lambda x:(x[1]['grupo'],x[0])):
        un=o['un']; d=1 if un=='L' else 0
        lots=[l for l in D2.LOTES if l['item']==nm]
        util=sum(l['fisico']-l['quarentena'] for l in lots) if lots else D2.ESTOQUE.get(nm,0)
        res=sum(l['reservado'] for l in lots); disp=D2.ESTOQUE.get(nm,0); cond=sum(l['quarentena'] for l in lots)
        firm=D2.RECEB.get(nm,0); ped=next((p for p in D2.PEDIDOS if p['item']==nm and p['a_entregar']>0),None)
        oo=org.get(nm,[]); tot=sum(x['q'] for x in oo); falta=max(0.0,tot-disp-firm)
        if not oo: continue   # CTL-4: insumo que só uma O.S. usa (Ureia da OS-0418) não tem origem do plano nesta tela antiga (oculta)
        data=min(x['dt'] for x in oo); lead=_lead(o['grupo'])+SEG
        if falta>0.001:
            nfalta+=1
            if _faixa((_dt.date.fromisoformat(data)-_dt.timedelta(days=lead)).isoformat())=='atrasada': natr+=1
        pf=([ch(f'{nq(falta)} {un}','red')] if falta>0.001 else [ch('Coberta','green')])+([BR,mut(f'{nq(min(cond,falta))} {un} coberto se o laudo aprovar')] if cond and falta>0.001 else [])
        acao=([lk('Ver contrato','SU-05det.dc.html')] if cond else [lk('Em cotação','CMP.dc.html')]) if falta>0.001 else ([lk('Ver laudo','SU-06.dc.html')] if cond else [mut('—')])
        kids=[R(f'{nm}|{i}',dict(item=x['t'],data=x['dt'],dem=round(x['q'],1)),dict(item=[txt(x['t'])],dem=[txt(f"{nq(x['q'])} {un}"),BR,mut(x['memo'])]),o=x['o']) for i,x in enumerate(oo)]
        memo=[dict(t=f'Demanda {nf(tot,d)} {un} = soma de {len(oo)} origens (expanda a linha)'),
              dict(t=f'Utilizável {nf(util,d)} {un} · reservado {nf(res,d)} · disponível {nf(disp,d)} {un}'+(f' · lotes {", ".join(l["lote"] for l in lots)}' if lots else '')),
              dict(t=f'Recebimento firme {nf(firm,d)} {un}'+(f' · {ped["id"]} ({FORN[ped["f"]]}) · {ped["previsao"][:5]}' if ped else '')),
              dict(t=f'Condicionado à qualidade {nf(cond,d)} {un} — não soma à cobertura até o laudo') if cond else dict(t='Sem fornecimento condicionado'),
              *([dict(t=f'Se o laudo de 27/09 aprovar: {nf(min(cond,falta),d)} {un} cobertos e a falta firme cai para {nf(falta-min(cond,falta),d)} {un} (carga 4 do CT-2026-11)',h='SU-06.dc.html')] if cond and falta>0.001 else []),
              dict(t=f'Falta firme = {nf(tot,d)} − {nf(disp,d)} − {nf(firm,d)} = {nf(falta,d)} {un}' if falta>0.001 else f'Sem falta firme · sobra {nf(disp+firm-tot,d)} {un}'),
              dict(t=f'Pedir até = data necessária − prazo do fornecedor ({lead-SEG} d) − segurança ({SEG} d)')]
        if falta>0.001: memo.append(dict(t='Liberar a carga 4 do CT-2026-11 · abrir o contrato',h='SU-05det.dc.html') if cond else dict(t=f'Na SOL-2026-07 · abrir em Compra de insumos',h='CMP.dc.html'))
        rows.append(R(nm,dict(item=nm,data=data,dem=round(tot,1),disp=disp,firm=firm,cond=cond,falta=round(falta,1),un=un),
            dict(item=[b(nm),mut(f"{o['grupo']} · {len(oo)} {'origem' if len(oo)==1 else 'origens'}")],dem=[txt(f'{nq(tot)} {un}')],
                 disp=[txt(f'{nq(disp)} {un}')]+([mut(f'res. {nq(res)}')] if res else []),
                 firm=([txt(f'{nq(firm)} {un}'),mut(ped["id"])] if firm else [mut('—')])+([BR,mut(f'+{nq(cond)} {un} condicionado ao laudo de 27/09')] if cond else []),falta=pf,acao=acao),
            kids=kids,o=memo,lead=lead))
    # origens fora da safra: frota (PCP) e manutenção (PCM)
    dfalta=DIESEL['demanda']-(DIESEL['tanque']-DIESEL['res'])-DIESEL['q']
    rows.append(R('Diesel S10',dict(item='Diesel S10',data='2026-10-05',dem=DIESEL['demanda'],disp=DIESEL['tanque']-DIESEL['res'],firm=DIESEL['q'],cond=0,falta=dfalta,un='L'),
        dict(item=[b('Diesel S10'),mut('Combustível · frota do plantio')],dem=[txt(f"{nf(DIESEL['demanda'])} L")],disp=[txt(f"{nf(DIESEL['tanque']-DIESEL['res'])} L"),mut(f"res. {nf(DIESEL['res'])}")],
             firm=[txt(f"{nf(DIESEL['q'])} L"),mut(DIESEL['ped'])],falta=[ch(f'{nf(dfalta)} L','red')],acao=[lk('Ver contrato','SU-05.dc.html')]),
        o=[dict(t='Programação do plantio (PCP): 35.400 L entre 25/09 e 05/10'),dict(t=f'Falta firme = 35.400 − 9.400 − 15.000 = {nf(dfalta)} L'),dict(t='Contrato Ipiranga CT-2026-03',h='SU-05.dc.html')],lead=2+SEG))
    nfalta+=1; natr+=int(_faixa((_dt.date.fromisoformat(rows[-1]['v']['data'])-_dt.timedelta(days=rows[-1]['lead'])).isoformat())=='atrasada')
    g=grid([dict(k='item',l='Item · origem',w=210),dict(k='falta',l='Falta firme',t='num',a='r'),dict(k='pedir',l='Pedir até · necessária',t='date'),
            dict(k='dem',l='Demanda',t='num',a='r'),dict(k='disp',l='Disponível',t='num',a='r'),dict(k='firm',l='Receb. firmes',t='num',a='r',w=170),
            dict(k='acao',l='Próxima ação')],
        rows,gid='g_nec',tree=True,total=False,so={'k':'pedir','d':False},
        edit=dict(m='origin',leafOnly=False,title='Necessidade',fields=[fs('item','Item ou origem',ro=True),fs('data','Data necessária','date',ro=True)]))
    faltas=[r['v']['item'] for r in rows if r['v']['falta']>0.001]
    valor=sum(o['valor'] for o in dem.values())
    pn={'rep':dict(title='Reprogramar proposta de reposição',sub='Muda a data necessária e recalcula o “pedir até”. Nenhuma cotação nova é enviada.',ok='Reprogramar',
        fields=[fs('item','Item','sel',opts=faltas,req=True,**{'def':faltas[0]}),fs('data','Nova data necessária','date',req=True),fs('motivo','Motivo','txt',req=True,help='Ex.: janela de plantio deslocada pela chuva.')])}
    js(pn,_sup_man_js()+r'''
CHECK.rep=(self,d)=>(d.data<HOJE?{data:'A data não pode ser anterior a hoje (23/09).'}:null);
RUN.rep=(self,d)=>{ let lead=0; setRows(self,'g_nec',rows=>{ const r=rows.find(x=>x.v.item===d.item); if(r){ r.v.data=d.data; lead=r.lead; } });
  return d.item+' reprogramado para '+dm(d.data)+' · pedir até '+dm(addd(d.data,-lead))+' · nenhuma cotação nova enviada'; };
function PREVALS(self,v){ cenOuvir(self); supAtualizaNec(self); RW(self,'g_nec').forEach(r=>{ const V=r.v; (r.kids||[]).forEach(k=>{ k.p.pedir=[M('necessária '+dm(k.v.data))]; });
  if(!r.lead) return; const pa=supPedirAte(V.data,{prazo:r.lead,seguranca:0}); V.pedir=pa;
  r.p.pedir=((V.falta>0.001)?[faixa(pa)]:[M('—')]).concat([BRK,M('necessária '+dm(V.data))]); r.s.pedir=(V.falta>0.001)?pa:''; }); }
function EXTRAVALS(self,v){ pnVals(self,v); }''')
    painel()
    corpo=(kpis([('Itens com falta firme',str(nfalta),'SOL-2026-07 em cotação + KCl, diesel e rolamento'),('Pedido atrasado',str(natr),'o “pedir até” já passou'),
                 ('Condicionado à qualidade','10 t','KCl 60% · K26-11 · laudo 27/09'),('Valor da falta firme',f'R$ {nf(valor/1000,1)} mil','SOL-2026-07 · preço de referência')])
           + bloco('Necessidade líquida por data','Confira a falta firme de cada item e abra a cotação; expanda o item para ver a origem da demanda.',g
                   + nota('KCl 60%: falta firme 140 − 50 − 40 = 50 t.'),
                   acao=mini('open_rep','Reprogramar proposta','Muda a data necessária de um item sem enviar nova cotação','calendar')))
    HEIGHTS37[fname]=1760
    shell37('SU-01','Necessidades e cobertura',corpo,fname=fname,
      subtitle='Necessidade líquida por data com origem, físico apto, reservas, entregas firmes e data limite de compra.',
      status=(f'{nfalta} itens com falta firme · {natr} atrasados','red'),primary_html=prima('CMP.dc.html','Abrir cotação da SOL-2026-07'),
      footer='Revisar uma falta não envia cotação; cobertura prevista e estoque físico aparecem em colunas separadas (SU-01 · CAL-01). '
             'As toneladas em quarentena não entram na falta firme e ficam como coberto se o laudo aprovar, somadas uma única vez; a linha abre a memória de cálculo.')

# ================= SU-02 · Políticas de estoque =================
DEPOS=['Galpão 1','Galpão 2','Câmara fria','Almox. defensivos','Tanque Sede','Almox. oficina']
METODOS=['Necessidade datada','Datada + proteção','Mínimo/máximo','Híbrida']
def su02():
    fname='SU-02.dc.html'; E._reset_screen(fname)
    POL=[('p1','Fertilizantes','Galpão 2','A','Alta','Necessidade datada',7,12,'carreta 36 t','—',400000,'Vigente · v4'),
         ('p2','Defensivos','Almox. defensivos','A','Alta','Datada + proteção',5,8,'caixa 12 un','18 meses · FEFO',250000,'Vigente · v2'),
         ('p3','Sementes','Câmara fria','A','Alta','Necessidade datada',5,10,'big bag 1 t','12 meses',180000,'Vigente · v3'),
         ('p4','Diesel S10','Tanque Sede','B','Alta','Mínimo/máximo',2,2,'15 mil L','—',90000,'Aguarda gestor · v5'),
         ('p5','Peças de manutenção','Almox. oficina','C','Alta','Mínimo/máximo',0,15,'un','—',60000,'Com exceção · v3.1'),
         ('p6','EPIs','Almox. oficina','C','Média','Mínimo/máximo',0,7,'par/un','24 meses',12000,'Vigente · v1')]
    rows=[R(i,dict(grp=g,dep=dp,abc=a,crit=c,met=m,seg=sg,prazo=pz,lote=lt,val=vl,lim=lm,estado=st,just='')) for i,g,dp,a,c,m,sg,pz,lt,vl,lm,st in POL]
    g=grid([dict(k='grp',l='Item/grupo · depósito',w=230),dict(k='abc',l='ABC · criticidade'),dict(k='met',l='Método'),dict(k='seg',l='Segurança · prazo'),
            dict(k='lote',l='Lote/múltiplo'),dict(k='val',l='Validade'),dict(k='lim',l='Limite econômico',t='num',a='r',pre='R$ '),dict(k='estado',l='Versão · estado')],
        rows,gid='g_pol',total=False,
        edit=dict(m='form',title='Política',sub='Salvar cria uma proposta de nova versão; a versão vigente segue valendo até o gestor aprovar e publicar.',
          fields=[fs('lote','Lote/múltiplo de compra',req=True,help='Ex.: carreta 36 t, caixa 12 un.'),fs('dep','Depósito','sel',opts=DEPOS,req=True),
                  fs('abc','Classe ABC (valor)','sel',opts=['A','B','C'],req=True),fs('crit','Criticidade','sel',opts=['Alta','Média','Baixa'],req=True,help='ABC financeira não substitui criticidade.'),
                  fs('met','Método de reposição','sel',opts=METODOS,req=True),fs('seg','Segurança','num',req=True,min=0,max=60,u='dias'),fs('prazo','Prazo de reposição','num',req=True,min=0,max=120,u='dias'),
                  fs('val','Validade / regra de saída',req=False),fs('lim','Limite econômico','num',req=True,min=0,u='R$'),
                  fs('just','Justificativa da proposta','area',req=True,help='Obrigatória: aparece para o gestor na aprovação.')]))
    pn={'exc':dict(title='Submeter exceção versionada',sub='A exceção vale só no período informado e passa pela alçada do gestor.',ok='Submeter exceção',
        fields=[fs('grp','Item/grupo','sel',opts=[p[1] for p in POL],req=True,**{'def':'Peças de manutenção'}),fs('alt','Alteração','txt',req=True,**{'def':'mínimo 2 → 4 un durante a colheita'}),
                fs('ini','Início','date',req=True,**{'def':'2026-10-01'}),fs('fim','Fim','date',req=True,**{'def':'2026-12-20'}),fs('just','Justificativa','area',req=True)])}
    js(pn,r'''
CHECK.exc=(self,d)=>(d.fim<=d.ini?{fim:'O fim precisa ser depois do início.'}:null);
RUN.exc=(self,d)=>{ setRows(self,'g_pol',rows=>{ const r=rows.find(x=>x.v.grp===d.grp); if(r) r.v.estado='Exceção submetida · aguarda gestor'; });
  return 'Exceção de '+d.grp+' submetida ('+dm(d.ini)+' a '+dm(d.fim)+') · aguarda o gestor · a política vigente não muda até a aprovação'; };
function PREVALS(self,v){ RW(self,'g_pol').forEach(r=>{ const V=r.v;
  r.p.grp=[B(V.grp),M(V.dep)]; r.s.grp=V.grp+' '+V.dep;
  r.p.abc=[T(V.abc+' ·'),chipc(V.crit,V.crit==='Alta'?'red':(V.crit==='Média'?'yellow':'gray'))]; r.s.abc=V.abc+' '+V.crit;
  r.p.seg=[T(nf(V.seg)+' d · '+nf(V.prazo)+' d')]; r.s.seg=String(V.seg);
  const e=String(V.estado); const i=e.lastIndexOf(' · '); r.p.estado=[chipc(i>0?e.slice(0,i):e,e.indexOf('Vigente')===0?'green':'yellow')].concat(i>0?[BRK,M(e.slice(i+3))]:[]); r.s.estado=e; }); }
function EXTRAVALS(self,v){ pnVals(self,v); sims(self,v);
  self.g2after=(gid,rows,r)=>{ if(gid==='g_pol'&&r){ const m=String(r.v.estado).match(/v(\d+)/); const nv='v'+(m?Number(m[1])+1:2);
    r.v.estado='Proposta '+nv+' · aguarda gestor'; self.setState({g2toast:'Proposta '+nv+' de '+r.v.grp+' salva · aguarda aprovação do gestor; a versão vigente segue valendo'}); } }; }''',
    simsd=dict(sim='Simulação do Diesel S10: mínimo de 40 % cobre 9 dias do pico do plantio sem ruptura · a política vigente não foi alterada',
               pub='Ainda não publicável · a proposta v5 do Diesel S10 aguarda o gestor (vence em 5 dias). Depois da aprovação, publique aqui; a versão vigente não é sobrescrita.'))
    painel()
    corpo=(bloco('Políticas por item e depósito','Confira segurança, prazo e limites de cada política; clique na linha para propor uma nova versão.',
                 g,
                 acao=mini('sim_sim','Simular cobertura','Simula o efeito de uma política sem alterá-la','calc')+alink('SU-01.dc.html','Ver efeito em Necessidades','Abre Necessidades com a cobertura calculada','trend'))
           + bloco('Publicação de vigência','Publique só a versão aprovada; a simulação e as propostas não alteram a política vigente.',
                   nota('Propostas e exceções aguardando: Diesel S10 v5 (gestor, vence em 5 dias).'),acao=mini('sim_pub','Publicar vigência','Publica a versão aprovada','check')))
    HEIGHTS37[fname]=900
    shell37('SU-02','Políticas de estoque',corpo,fname=fname,
      subtitle='Política por item e local com segurança, prazo, lote, múltiplo, validade e justificativa; exceções versionadas.',
      status=('1 proposta aguardando gestor','yellow'),primary_html=primb('open_exc','Submeter exceção'),
      footer='Publicar vigência exige aprovação (FO-31); simulação nunca altera a política vigente (SU-02, cap. 65). '
             'Classe ABC financeira não substitui criticidade: Diesel é B em valor e Alta em criticidade. Limites do depósito e validade restringem a entrega, sem equivaler ao tamanho do contrato.')

# ================= SU-03 · Saldos e lotes de materiais =================
LOTES_X=[  # além de dados2.LOTES: sobras da REQ-031, lote zerado com custódia da OS-0420, consignado, diesel e café (produção)
 dict(item='MAP 11-52',lote='M26-05',local='Galpão 2',un='kg',fisico=1000,quarentena=1000,reservado=0,validade='—',cust=R31['custodia']*50,cos='OS-0417',prop='própria',ret='Quarentena · sobras de campo',orig='devolução REQ-031'),
 dict(item='KCl 60%',lote='K26-07',local='Galpão 2',un='kg',fisico=0,quarentena=0,reservado=0,validade='—',cust=R37['custodia'],cos='OS-0420',prop='própria',ret='',orig='REQ-037'),
 dict(item='Herbicida Z',lote='H26-09',local='Almox. defensivos',un='L',fisico=40,quarentena=0,reservado=0,validade='05/2027',cust=0,cos='',prop='Santa Rita Insumos · consignado',ret='',orig='CT-2026-08'),
 dict(item='Diesel S10',lote='tanque',local='Tanque Sede',un='L',fisico=DIESEL['tanque'],quarentena=0,reservado=DIESEL['res'],validade='—',cust=0,cos='',prop='própria',ret='',orig='PC-084'),
 dict(item='Café beneficiado',lote=D.LOTE_BLOQ['id'],local='Armazém Sede',un='sc',fisico=D.LOTE_BLOQ['sc'],quarentena=D.LOTE_BLOQ['sc'],reservado=0,validade='—',cust=0,cos='',prop='própria',ret='Bloqueado · INSP-88',orig='produção'),
]
CUST_LOTE={'F26-02':(R35['custodia'],'OS-0421')}
ORIG_LOTE={'K26-11':'NF 4501 · PC-088','M26-07':'NF 4211','F26-02':'NF 4390','G26-14':'NF 4402','S58-0801':'NF 4288','N26-03':'NF 4310','O26-05':'NF 4390'}
def _lotes():
    out=[]
    for l in D2.LOTES:
        c=CUST_LOTE.get(l['lote'],(0,''))
        out.append(dict(l,cust=c[0],cos=c[1],prop='própria',ret=('Quarentena · laudo 27/09' if l['quarentena'] else ''),orig=ORIG_LOTE.get(l['lote'],'')))
    return out+LOTES_X
def _valor(l):
    if l['item']=='Café beneficiado' or 'consignado' in l['prop']: return 0
    if l['item']=='Diesel S10': return l['fisico']*DIESEL['preco']
    pr=KCL_T/1000 if l['item']=='KCl 60%' else PRECO.get(l['item'],0)
    return l['fisico']*pr
def su03():
    fname='SU-03.dc.html'; E._reset_screen(fname)
    rows=[]; tot=0
    for l in _lotes():
        un=l['un']; util=l['fisico']-l['quarentena']; disp=util-l['reservado']; val=_valor(l); tot+=val
        o=[dict(t=f"Físico {nq(l['fisico'])} {un} no {l['local']} · origem {l['orig']} · proprietário {l['prop']}" + (f" · validade {l['validade']}" if l['validade']!='—' else '')),
           dict(t=f"Retido {nq(l['quarentena'])} {un}" + (f" · {l['ret']}" if l['ret'] else '')),
           dict(t=f"Utilizável {nq(util)} − reservado {nq(l['reservado'])} = disponível {nq(disp)} {un}"),
           dict(t=(f"Custódia em campo {nq(l['cust'])} {un} com a {l['cos']} — fora do físico do depósito" if l['cust'] else 'Sem custódia em campo'))]
        if l['lote']=='F26-02': o.append(dict(t='Reserva planejada da safra em conflito' if CONFL_FA else 'Reservas do lote e uso da safra',h='SU-03det.dc.html'))
        o+= [dict(t='Ver movimentos do lote',h='SU-08.dc.html'),dict(t='Requisitar para uma O.S.',h='SU-07.dc.html')]
        if l['ret']: o.append(dict(t='Inspecionar',h='SU-06.dc.html'))
        pit=[b(f"{l['item']} · {l['lote']}")]+([mut('consignado')] if 'consignado' in l['prop'] else [])
        if l['lote']=='F26-02': pit+=[BR,lk('Reserva em conflito','SU-03det.dc.html')]
        rows.append(R(l['lote'],dict(item=f"{l['item']} · {l['lote']}",loc=l['local'],fis=l['fisico'],ret=l['quarentena'],util=util,res=l['reservado'],disp=disp,cust=l['cust'],val=round(val),un=un,lote=l['lote']),
            dict(item=pit,loc=[txt(l['local'])],fis=[txt(f"{nq(l['fisico'])} {un}")],
                 ret=([ch(f"{nq(l['quarentena'])} {un}",'red' if 'Bloq' in l['ret'] else 'yellow')] if l['quarentena'] else [mut('—')]),
                 util=[txt(f"{nq(util)} {un}")],cust=([txt(f"{nq(l['cust'])} {un}"),mut(l['cos'])] if l['cust'] else [mut('—')]),
                 val=([txt(f'R$ {nf(val/1000,1)} mil')] if val else [mut('do proprietário' if 'consignado' in l['prop'] else ('fora do total' if l['item']=='Café beneficiado' else '—'))])),o=o))
    g=grid([dict(k='item',l='Item · lote',w=230),dict(k='loc',l='Local'),dict(k='fis',l='Físico',t='num',a='r'),dict(k='ret',l='Retido'),
            dict(k='util',l='Utilizável',t='num',a='r'),dict(k='res',l='Reservado',t='num',a='r'),dict(k='disp',l='Disponível',t='num',a='r'),dict(k='cust',l='Custódia',t='num',a='r'),
            dict(k='val',l='Valor',t='num',a='r')],rows,gid='g_sal',total=False,
        edit=dict(m='origin',title='Saldo',fields=[fs('item','Item · lote',ro=True),fs('loc','Local',ro=True)]))
    pn={'res':dict(title='Reservar saldo para ordem',sub='A reserva nunca passa do disponível do lote e fica ligada à ordem de destino.',ok='Reservar',
        fields=[fs('os','Ordem de destino','sel',opts=[f"OS-0421 · Fungicida 1ª aplicação (REQ-035 · faltam {nq(R35['solicitado']-R35['entregue'])} L)"],req=True,**{'def':f"OS-0421 · Fungicida 1ª aplicação (REQ-035 · faltam {nq(R35['solicitado']-R35['entregue'])} L)"}),
                fs('lote','Lote','sel',opts=['F26-02 · Fungicida A · Almox. defensivos'],req=True,**{'def':'F26-02 · Fungicida A · Almox. defensivos'}),
                fs('q','Quantidade','num',req=True,min=0.1,u='L',maxfn='disp',**{'def':nq(R35['solicitado']-R35['entregue'])})])}
    js(pn,r'''
const FALTA_0421=%s;
MAXFN.disp=(self)=>{ const r=RF(self,'g_sal','F26-02'); return r?r.v.disp:0; };
CHECK.res=(self,d)=>{ const ja=self.state.res0421||0; const q=g2num(d.q); if(ja>=FALTA_0421) return {q:'A OS-0421 já tem os '+nf(FALTA_0421)+' L reservados (recibo '+self.state.rcb+') — nada reservado de novo.'}; if(ja+q>FALTA_0421) return {q:'A OS-0421 precisa de só '+nf(FALTA_0421-ja)+' L.'}; return null; };
RUN.res=(self,d)=>{ const q=g2num(d.q); let de=0, pa=0; setRows(self,'g_sal',rows=>{ const r=rows.find(x=>x.id==='F26-02'); de=r.v.disp; r.v.res+=q; r.v.disp-=q; pa=r.v.disp; });
  const rc='RS-78'+String(10+Math.round(q)).slice(-2); self.setState({res0421:(self.state.res0421||0)+q,rcb:rc});
  return 'Reserva confirmada para a OS-0421 · F26-02: disponível '+nf(de)+' → '+nf(pa)+' L · recibo '+rc; };
function PREVALS(self,v){ RW(self,'g_sal').forEach(r=>{ const V=r.v, u=' '+V.un;
  r.p.res=[T(V.res?nf(V.res,V.res%%1?1:0)+u:'—')]; r.p.disp=[V.disp>0?B(nf(V.disp,V.disp%%1?1:0)+u):M('0'+u)]; }); }
function EXTRAVALS(self,v){ pnVals(self,v); }''' % (R35['solicitado']-R35['entregue']))
    painel()
    ncust=len([l for l in _lotes() if l['cust']])
    corpo=(kpis([('Conflito de reserva','1',f'F26-02 · pendência {nq(SOL_FA)} L') if CONFL_FA else ('Conflito de reserva','0','F26-02 · uso da safra e pendência de compra na demanda única'),('Lotes retidos','3','K26-11 · M26-05 · L27-013'),
                 ('Custódia em campo',f'{ncust} ordens','OS-0417 · OS-0421 · OS-0420'),('Valor em insumos',f'R$ {nf(tot/1e6,2)} mi','próprio · sem café e consignado')])
           + bloco('Estoque por item, lote, proprietário e local','Confira físico, retido, reservado e disponível de cada lote; clique na linha para ver a origem do saldo.',
                   g,
                   acao=alink('SU-08.dc.html','Ver movimentos','Abre o extrato de movimentos','lista')))
    HEIGHTS37[fname]=1000
    shell37('SU-03','Saldos e lotes de materiais',corpo,fname=fname,
      subtitle='Estoque por item, lote, proprietário e local com custódias; cada saldo mostra fonte e documento de origem.',
      status=('1 conflito de reserva · 3 lotes retidos','red') if CONFL_FA else ('3 lotes retidos','yellow'),primary_html=primb('open_res','Reservar para ordem','box'),
      footer='Os saldos são os mesmos do processo Estoque; requisitar, transferir e inspecionar abrem o registro de destino (SU-07, SU-08, SU-06). '
             'Físico ≠ utilizável ≠ disponível. Custódia em campo fica fora do físico do depósito e não soma duas vezes; consignado aparece identificado e obedece à autorização do proprietário.')

# ---- SU-03det · F26-02 · reserva em conflito (DEMO-18 nos saldos de dados2) ----
def su03det():
    fname='SU-03det.dc.html'; E._reset_screen(fname); PARENT37[fname]='SU-03.dc.html'
    if not CONFL_FA: return su03det_sem_conflito(fname)
    org=_origens()['Fungicida A']
    a1=round(sum(x['q'] for x in org if '1ª' in x['t']),1); a2=round(sum(x['q'] for x in org if '2ª' in x['t']),1)
    rows=[R('fis',dict(m='Físico no lote',q=F02['fisico']),dict(q=[b(f"{nq(F02['fisico'])} L")],sit=[txt('validade 03/2028 · NF 4390')]),o=[dict(t='Almox. defensivos · sem quarentena'),dict(t='Movimentos do lote',h='SU-08.dc.html')]),
          R('os24',dict(m='Reserva confirmada · OS-0424 (fungicida T1-B)',q=F02['reservado']),dict(q=[txt(f"{nq(F02['reservado'])} L")],sit=[ch('Confirmada · recibo RS-7741','green')]),o=[dict(t='Requisição REQ-039 · separar pelo FEFO',h='SU-07.dc.html')]),
          R('plano',dict(m='Reserva planejada · Safra 2026/27',q=PLANO_FA),dict(),o=[dict(t=f'1ª aplicação (DAP 45) · T1-A, T1-B e T2 = {nq(a1)} L'),dict(t=f'2ª aplicação (DAP 60) · T1-A, T1-B e T2 = {nq(a2)} L'),dict(t='Abrir em Planejar safra',h='SAF.dc.html')]),
          R('disp',dict(m='Disponível no lote',q=LIVRE_FA),dict(),o=[dict(t=f"Físico {nq(F02['fisico'])} − reservado {nq(F02['reservado'])} = {nq(LIVRE_FA)} L; nunca fica negativo")]),
          R('pend',dict(m='Pendência sem saldo',q=0),dict(),o=[dict(t=f'Coberta pela SOL-2026-07 (líquido de Fungicida A = {nq(SOL_FA)} L)'),dict(t='Abrir em Compra de insumos',h='CMP.dc.html')])]
    g=grid([dict(k='m',l='Medida',w=600),dict(k='q',l='Quantidade',t='num',a='r'),dict(k='sit',l='Situação',w=600)],rows,gid='g_lot',search=False,total=False,
        edit=dict(m='origin',title='Saldo do lote',fields=[fs('m','Medida',ro=True)]))
    js({},r'''
const A1=%s, A2=%s, PL=%s, LV=%s, SOLQ=%s;
function PREVALS(self,v){ const dec=self.state.dec; const rs=RW(self,'g_lot');
  const P=rs.find(r=>r.id==='plano'), Dp=rs.find(r=>r.id==='disp'), Pe=rs.find(r=>r.id==='pend');
  P.p.q=[T(nf(PL,1)+' L')]; Dp.v.q=(dec==='res'?0:LV); Pe.v.q=(dec==='res'?SOLQ:(dec==='wait'?PL:0));
  P.p.sit=dec==='res'?[chipc('Parcial · '+nf(LV)+' L reservados','yellow')]:(dec==='wait'?[chipc('Adiada · aguarda a compra','gray')]:[chipc('Conflito · saldo insuficiente','red')]);
  Dp.p.q=[B(nf(Dp.v.q)+' L')]; Dp.p.sit=dec==='res'?[chipc('Livre 0 · sem saldo negativo','green')]:[T('consultado pela reserva planejada')];
  Pe.p.q=[T(Pe.v.q?nf(Pe.v.q,1)+' L':'—')]; Pe.p.sit=dec?[chipc('Na SOL-2026-07','yellow'),{k:'link',t:'Abrir compra',h:'CMP.dc.html'}]:[M('decida abaixo')]; }
function EXTRAVALS(self,v){ const dec=self.state.dec;
  v.undec=!dec; v.decres=dec==='res'; v.decwait=dec==='wait';
  if(dec==='res') hstatus(v,'Conflito tratado · livre 0 L','green'); else if(dec==='wait') hstatus(v,'Conflito tratado · aguarda compra','yellow'); else hstatus(v,'Conflito ativo · livre '+nf(LV)+' L','red');
  v.ct_falta=dec?('Receber '+nf(dec==='res'?SOLQ:PL,1)+' L da SOL-2026-07'):'Decidir a reserva planejada'; v.ct_prox=dec?'Acompanhar a compra':('Reservar '+nf(LV)+' L com pendência');
  v.tl=[{t:'23/09 10:02:01 · OS-0424 pede 65 L → confirmada (recibo RS-7741)'},{t:'23/09 10:02:01 · reserva planejada da safra pede '+nf(PL,1)+' L → conflito: só '+nf(LV)+' L livres, nada reservado'},{t:'23/09 10:04 · reenvio da OS-0424 devolve o mesmo recibo RS-7741, sem nova dedução'}];
  if(dec==='res') v.tl.push({t:'23/09 · '+nf(LV)+' L reservados para a safra (recibo RS-7790) · pendência de '+nf(SOLQ,1)+' L ligada à SOL-2026-07'});
  if(dec==='wait') v.tl.push({t:'23/09 · reserva planejada adiada · '+nf(PL,1)+' L aguardam a compra da SOL-2026-07; o livre segue '+nf(LV)+' L'});
  const ja=()=>toast(self,'Conflito já tratado ('+(self.state.dec==='res'?'recibo RS-7790':'reserva adiada')+') · nada reservado de novo');
  v.do_res=()=>{ if(self.state.dec) return ja(); self.setState({dec:'res',g2toast:'Reservados '+nf(LV)+' L para a safra: a 1ª aplicação ('+nf(A1,1)+' L) está coberta; a 2ª fica retida com '+nf(SOLQ,1)+' L pendentes — mistura incompleta não é liberada'}); };
  v.do_wait=()=>{ if(self.state.dec) return ja(); self.setState({dec:'wait',g2toast:'Reserva planejada adiada · o livre do lote segue '+nf(LV)+' L para ordens urgentes; a safra aguarda a compra'}); }; }''' % (a1,a2,PLANO_FA,LIVRE_FA,SOL_FA))
    tl=f'<div style="display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: {MUTED}; line-height: 1.5;"><sc-for list="{H("tl")}" as="x" hint-placeholder-count="3"><div>{H("x.t")}</div></sc-for></div>'
    decide=(f'<sc-if value="{H("undec")}" hint-placeholder-val="{T()}"><div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">'
            + mini('do_res',f'Reservar {nq(LIVRE_FA)} L com pendência',f'Reserva todo o livre e liga os {nq(SOL_FA)} L que faltam à SOL-2026-07','box',prim=True)
            + mini('do_wait','Aguardar a compra da SOL-2026-07','Não reserva agora; o livre fica para ordens urgentes','clock')+'</div></sc-if>'
            + f'<sc-if value="{H("decres")}" hint-placeholder-val="{F()}"><div style="font-size: 13px;">{chip("Tratado","green")} <b>{nq(LIVRE_FA)} L reservados</b> para a safra · 1ª aplicação ({nq(a1)} L) coberta · 2ª aplicação retida até chegarem {nq(SOL_FA)} L.</div></sc-if>'
            + f'<sc-if value="{H("decwait")}" hint-placeholder-val="{F()}"><div style="font-size: 13px;">{chip("Tratado","yellow")} Reserva adiada · {nq(PLANO_FA)} L aguardam a SOL-2026-07; o livre segue {nq(LIVRE_FA)} L.</div></sc-if>')
    corpo=(continuity('Duas reservas no mesmo instante','Conflito · lote F26-02',H('ct_falta'),H('ct_prox'))
           + bloco('Saldo do lote','Confira o que foi confirmado e o que ficou sem saldo; clique na linha para ver a origem.',g)
           + bloco('Linha do tempo da disputa','Confira a ordem dos pedidos: um confirma, o outro recebe conflito, sem sobrescrita e sem saldo negativo.',tl)
           + bloco('Decidir a reserva planejada','Escolha uma saída; entrega parcial não libera mistura incompleta.',decide))
    HEIGHTS37[fname]=960
    prim=(f'<sc-if value="{H("decres")}" hint-placeholder-val="{F()}">{prima("CMP.dc.html","Acompanhar a SOL-2026-07")}</sc-if>'
          f'<sc-if value="{H("decwait")}" hint-placeholder-val="{F()}">{prima("CMP.dc.html","Acompanhar a SOL-2026-07")}</sc-if>')
    shell37('SU-03','Lote F26-02 · conflito de reserva',corpo,fname=fname,crumbs_extra=['Fungicida A · F26-02'],
      subtitle=f"Reserva concorrente: {nq(F02['fisico'])} L no lote; a OS-0424 confirmou {nq(F02['reservado'])} L e a reserva planejada da safra recebeu conflito.",
      status=(MARK,'gray'),primary_html=prim,
      footer='DEMO-18 · várias reservas válidas podem coexistir em partes do lote; reenvio devolve o mesmo recibo; vencimento retira elegibilidade sem apagar histórico (ESTOS-02/03).')
    dyn_status(fname)

def su03det_sem_conflito(fname):
    """SU-03det sem conflito (revisão do CTL-4, S4): o lote F26-02, a reserva da OS-0424 e o uso da safra de hoje em diante pela demanda única.
    Revisão do 853a6a8 (achado 6, S3): lote, reserva, uso da safra e pendência de compra são lidos AO VIVO do cenário compartilhado e da mesma
    demanda do Planejar safra e da Compra (dados2.js_dem_viva: demFazenda sobre cenDemEntradas) — nunca "sem pendência de compra" da semente
    enquanto a demanda pede complemento (ex.: 30 L devolvidos bloqueados viram qualidade pendente; uma O.S. nova vira pendência)."""
    import cenario
    rows=[R('fis',dict(m='Físico no lote',q=F02['fisico']),dict(q=[b(f"{nq(F02['fisico'])} L")],sit=[txt('validade 03/2028 · NF 4390')]),o=[dict(t='Almox. defensivos'),dict(t='Movimentos do lote',h='SU-08.dc.html')]),
          R('os24',dict(m='Reserva confirmada · OS-0424 (fungicida T1-B)',q=F02['reservado']),dict(q=[txt(f"{nq(F02['reservado'])} L")],sit=[ch('Confirmada · recibo RS-7741','green')]),o=[dict(t='Requisição REQ-039 · separar pelo FEFO',h='SU-07.dc.html')]),
          R('uso',dict(m='Uso da safra 2026/27 de hoje em diante',q=0),dict(q=[mut('—')],sit=[mut('calculando')]),o=[dict(t='Abrir a demanda no Planejar safra',h='SAF.dc.html#saf=S2627&passo=demanda')]),
          R('disp',dict(m='Disponível no lote',q=LIVRE_FA),dict(q=[b(f"{nq(LIVRE_FA)} L")],sit=[txt('livre para outras ordens; nunca fica negativo')]),o=[dict(t=f"Físico {nq(F02['fisico'])} − reservado {nq(F02['reservado'])} = {nq(LIVRE_FA)} L")]),
          R('pend',dict(m='Pendência de compra',q=0),dict(q=[mut('—')],sit=[mut('calculando')]),o=[dict(t='A Compra de insumos e o Planejar safra leem a mesma demanda'),dict(t='Abrir a Compra de insumos',h='CMP.dc.html')])]
    g=grid([dict(k='m',l='Medida',w=600),dict(k='q',l='Quantidade',t='num',a='r'),dict(k='sit',l='Situação',w=600)],rows,gid='g_lot',search=False,total=False,
        edit=dict(m='origin',title='Saldo do lote',fields=[fs('m','Medida',ro=True)]))
    js({},cenario.js_prefixo()+D2.js_dem_viva('S2627')+r"""
/* lote F26-02, reserva da OS-0424 e a demanda única do Fungicida A na Safra 2026/27, do cenário vivo (Estoque, O.S. e app mudam e a tela acompanha) */
function faViva(){ const c=cenGet(); const l=c.lotes['Fungicida A|F26-02']||{fisico:0,quarentena:0,reservado:0}; const r=c.reqs['REQ-039']; const it=r&&r.itens.find(i=>i.prod==='Fungicida A');
  const o=c.ordens['OS-0424']||{}; const res=(it&&r.estado!=='Cancelada'&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0)?cenResPropria(c,'REQ-039',it,l):0;
  const d=demViva('Fungicida A')||{liq:0,cond:0,bruta:0,evs:[]}; const own=(d.evs||[]).filter(e=>e.tipo==='dem'&&e.own); const isOS=e=>/^OS-/.test(String(e.chave||''));
  return {l,res,disp:cenDisp(l),liq:d.liq||0,cond:d.cond||0,bruta:d.bruta||0,qos:own.filter(isOS).reduce((a,e)=>a+e.q,0),qpl:own.filter(e=>!isOS(e)).reduce((a,e)=>a+e.q,0),
    oss:own.filter(isOS).map(e=>e.chave+' '+nf(e.q,1)+' L').join(', ')}; }
function PREVALS(self,v){ const x=faViva(); const rs=RW(self,'g_lot'); const R_=(id)=>rs.find(r=>r.id===id)||{v:{},p:{}};
  const F=R_('fis'), O=R_('os24'), U=R_('uso'), Dp=R_('disp'), Pe=R_('pend'); const L=x.l;
  F.v.q=L.fisico; F.p.q=[B(nf(L.fisico)+' L')]; F.p.sit=[T('validade 03/2028 · NF 4390')].concat(L.quarentena>1e-9?[BRK,chipc(nf(L.quarentena)+' L em quarentena · aguardam laudo','yellow')]:[]);
  O.v.q=x.res; O.p.q=[T(x.res>1e-9?nf(x.res)+' L':'—')]; O.p.sit=x.res>1e-9?[chipc('Confirmada · recibo RS-7741','green')]:[M('sem reserva presa (entregue ou cancelada)')];
  U.v.q=Math.round(x.bruta*10)/10; U.p.q=[T(nf(x.bruta,1)+' L')];
  /* falta firme e qualidade pendente juntas: as duas à vista, a ação segue a da compra firme (revisão do 16fb55e, ajuste 1) */
  const QP=x.cond>0.05?[chipc('Qualidade pendente · '+nf(x.cond,1)+' L','yellow')]:[];
  U.p.sit=x.liq>0.05?[chipc('Falta '+nf(x.liq,1)+' L','yellow')].concat(QP):(x.cond>0.05?QP:[chipc('Coberto pelo lote','green')]);
  U.o=[{t:'O.S. abertas pelo que falta tirar do almoxarifado: '+nf(x.qos,1)+' L'+(x.oss?' ('+x.oss+')':'')},{t:'Plano sem O.S. (sem a parte que as ordens já cobrem): '+nf(x.qpl,1)+' L'},{t:'Abrir a demanda no Planejar safra',h:'SAF.dc.html#saf=S2627&passo=demanda'}];
  Dp.v.q=x.disp; Dp.p.q=[B(nf(x.disp)+' L')]; Dp.o=[{t:'Físico '+nf(L.fisico)+' − bloqueado '+nf(L.quarentena)+' − reservado '+nf(L.reservado)+' = '+nf(x.disp)+' L'}];
  Pe.v.q=x.liq; Pe.p.q=[T(x.liq>0.05?nf(x.liq,1)+' L':'—')];
  Pe.p.sit=x.liq>0.05?[chipc('Pendência de compra · '+nf(x.liq,1)+' L','yellow')].concat(QP.length?QP.concat([M('fora da compra · o gestor libera ou reprova no Estoque')]):[]).concat([{k:'link',t:'Ver no Planejar safra',h:'SAF.dc.html#saf=S2627&passo=demanda'}])
    :(x.cond>0.05?[chipc('Qualidade pendente · '+nf(x.cond,1)+' L','yellow'),M('condicionada ao laudo · sem nova compra automática')]:[chipc('Sem pendência de compra','green')]);
  Pe.o=[{t:'A Compra de insumos e o Planejar safra leem a mesma demanda: '+(x.liq>0.05?'faltam '+nf(x.liq,1)+' L de Fungicida A nesta safra'+(x.cond>0.05?'; mais '+nf(x.cond,1)+' L dependem do laudo da quarentena (fora da compra, sem nova compra automática)':''):(x.cond>0.05?nf(x.cond,1)+' L dependem do laudo da quarentena':'o estoque apto cobre o Fungicida A desta safra'))},{t:'Abrir a Compra de insumos',h:'CMP.dc.html'}]; }
function EXTRAVALS(self,v){ cenOuvir(self); const x=faViva();
  if(x.liq>0.05) hstatus(v,'Pendência de compra · '+nf(x.liq,1)+' L','yellow'); else if(x.cond>0.05) hstatus(v,'Qualidade pendente · '+nf(x.cond,1)+' L','yellow'); else hstatus(v,'Sem conflito · livre '+nf(x.disp)+' L','green');
  v.ct_falta=x.liq>0.05?('Comprar '+nf(x.liq,1)+' L (complemento no Planejar safra)'+(x.cond>0.05?' · mais '+nf(x.cond,1)+' L aguardam o laudo da quarentena (o gestor libera ou reprova no Estoque)':'')):(x.cond>0.05?('Laudo da quarentena ('+nf(x.cond,1)+' L condicionados)'):'Nada a decidir');
  v.ct_prox=x.liq>0.05?'Enviar o complemento no Planejar safra':(x.cond>0.05?'O gestor libera ou reprova a qualidade no Estoque':'Acompanhar as O.S. da safra');
  v.tl=[{t:'23/09 10:02:01 · OS-0424 pede 65 L → confirmada (recibo RS-7741)'},{t:'23/09 10:04 · reenvio da OS-0424 devolve o mesmo recibo RS-7741, sem nova dedução'},
        {t:'demanda única de agora: uso da safra de hoje em diante '+nf(x.bruta,1)+' L · '+(x.liq>0.05?'faltam '+nf(x.liq,1)+' L'+(x.cond>0.05?' + '+nf(x.cond,1)+' L condicionados ao laudo':''):(x.cond>0.05?nf(x.cond,1)+' L condicionados ao laudo':'o lote cobre'))}]; }""")
    tl=f'<div style="display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: {MUTED}; line-height: 1.5;"><sc-for list="{H("tl")}" as="x" hint-placeholder-count="3"><div>{H("x.t")}</div></sc-for></div>'
    corpo=(continuity('Reservas do lote','Lote F26-02 · Fungicida A',H('ct_falta'),H('ct_prox'))
           + bloco('Saldo do lote','Confira o reservado, o uso da safra e o disponível; clique na linha para ver a origem.',g)
           + bloco('Linha do tempo das reservas','Confira a ordem dos pedidos de reserva: reenvio devolve o mesmo recibo, sem saldo negativo.',tl))
    HEIGHTS37[fname]=760
    shell37('SU-03','Lote F26-02 · reservas',corpo,fname=fname,crumbs_extra=['Fungicida A · F26-02'],
      subtitle="Lote F26-02 de Fungicida A: a reserva da OS-0424 e o uso da Safra 2026/27 pela demanda única, a mesma do Planejar safra e da Compra de insumos, com o estoque de agora.",
      status=(MARK,'gray'),primary_html=prima('SAF.dc.html#saf=S2627&passo=demanda','Ver a demanda no Planejar safra'),
      footer='DEMO-18 · várias reservas válidas podem coexistir em partes do lote; reenvio devolve o mesmo recibo; vencimento retira elegibilidade sem apagar histórico (ESTOS-02/03).')
    dyn_status(fname)

# ================= SU-04 · Solicitações e cotações =================
FRETE_KG=0.06; FRETE_PCT=0.015
FORN_PECAS=['Rolamentos Centro-Oeste','Casa das Peças','JD Peças Rio Verde']
def _cotacao(grupo,itens):
    out=[]
    for pr in D2.PROPOSTAS.get(grupo,[]):
        merc=sum(o['qtd']*o['preco_ref']*pr['fator'] for o in itens.values())
        kg=sum(o['qtd'] for o in itens.values() if o['un']=='kg')
        fr=0 if pr['frete']=='CIF' else (kg*FRETE_KG if grupo in ('Fertilizantes','Sementes') else merc*FRETE_PCT)
        out.append(dict(f=pr['f'],nome=FORN[pr['f']],merc=merc,frete=fr,tot=merc+fr,prazo=pr['prazo'],cond=f"{pr['frete']} · {pr['pag']}",val=pr['validade']))
    return sorted(out,key=lambda x:x['tot'])
def _alcada(v): return next(a['quem'] for a in D2.ALCADA if a['ate'] is None or v<=a['ate'])
def su04():
    fname='SU-04.dc.html'; E._reset_screen(fname)
    sol=D2.sol_itens(); grupos={}
    for n,o in sol.items(): grupos.setdefault(o['grupo'],{})[n]=o
    rows=[]
    for gname in sorted(grupos):
        its=grupos[gname]; cot=_cotacao(gname,its); conv=[f['nome'] for f in D2.FORNECEDORES if f['homologado'] and gname in f['grupos']]
        best=cot[0] if cot else None; nresp=len(cot)
        rows.append(R('G'+gname,dict(cot=f'SOL-2026-07 · {gname}',itens=len(its),forn=len(conv),resp=nresp,melhor=round(best['tot']) if best else 0,estado='enviada',tipo='Enviada em 23/09 · consulta'),
            dict(cot=[b(f'SOL-2026-07 · {gname}'),mut('Planejar safra · demanda de insumos')],itens=[txt(f'{len(its)} {"item" if len(its)==1 else "itens"}'),mut(', '.join(list(its)[:2])+('…' if len(its)>2 else ''))],
                 forn=[txt(f'{len(conv)} homologados')],resp=[ch(f'{nresp}/{len(conv)}','green' if nresp==len(conv) else 'yellow')],
                 melhor=([txt(f"R$ {nf(best['tot'])}"),mut(best['nome'])] if best else [mut('—')]),
                 estado=[ch('Pronta','green') if nresp==len(conv) else ch(f'Falta {len(conv)-nresp} resposta','yellow')]),
            ro=True,o=[dict(t=f"{c['nome']}: mercadoria R$ {nf(c['merc'])} + frete R$ {nf(c['frete'])} = R$ {nf(c['tot'])} · {c['prazo']} d · {c['cond']}") for c in cot]
                     +[dict(t='Convites enviados em 23/09 10:40 por Ana (gestora) · só a homologados do grupo'),dict(t='Abrir em Compra de insumos',h='CMP.dc.html')]))
    rows.append(R('COT-110',dict(cot='COT-110 · Kit filtros + óleo 15W40',itens=1,forn=3,resp=1,melhor=0,estado='aguardando',tipo='Enviada em 21/09 · consulta'),
        dict(cot=[b('COT-110 · Kit filtros + óleo 15W40'),mut('Manutenção · OM-0234')],itens=[txt('1 item'),mut('1 kit')],forn=[txt('3 convidados')],resp=[ch('1/3','yellow')],melhor=[mut('—')],
             estado=[ch('Até 24/09','yellow')]),ro=True,o=[dict(t='Respostas até 24/09; depois disso compara com as recebidas')]))
    g=grid([dict(k='cot',l='Cotação · origem',w=260),dict(k='itens',l='Itens'),dict(k='forn',l='Fornecedores'),dict(k='resp',l='Respostas',t='num',a='r'),
            dict(k='melhor',l='Melhor custo equalizado',t='num',a='r'),dict(k='estado',l='Estado')],rows,gid='g_cot',total=False,
        edit=dict(m='form',title='Cotação',sub='Rascunho: ajuste especificação, quantidade, entrega e destinatários antes de enviar. Cotação enviada abre em consulta.',
          fields=[fs('tipo','Situação',ro=True)]+[dict(f,cond=dict(k='tipo',eq='Rascunho')) for f in [fs('esp','Especificação',req=True),fs('qtd','Quantidade','num',req=True,min=1,u='un'),fs('ent','Entrega até','date',req=True),
                  fs('local','Local de entrega','sel',opts=DEPOS,req=True),fs('dest','Destinatários','multi',opts=FORN_PECAS,req=True,help='Sugestões por categoria e região; o convite dá acesso só a esta cotação.')]]))
    # comparação equalizada · Fertilizantes (maior valor da SOL)
    fert=grupos['Fertilizantes']; cot=_cotacao('Fertilizantes',fert); best=cot[0]
    crow=[R(c['f'],dict(nome=c['nome'],merc=round(c['merc']),frete=round(c['frete']),prazo=c['prazo'],cond=c['cond'],tot=round(c['tot'])),
            dict(nome=[b(c['nome'])],frete=([txt(f"R$ {nf(c['frete'])}"),mut('FOB · estimado')] if c['frete'] else [mut('CIF · incluso')])),
            o=[dict(t=f"{n}: {nf(o['qtd'])} {o['un']} × R$ {nf(o['preco_ref']*next(p['fator'] for p in D2.PROPOSTAS['Fertilizantes'] if p['f']==c['f']),3)}") for n,o in fert.items()]
              +[dict(t=f"Frete FOB estimado em R$ {nf(FRETE_KG,2)}/kg" if c['frete'] else 'Frete CIF incluso no preço'),dict(t=f"Validade da proposta {c['val']}")]) for c in cot]
    gc=grid([dict(k='nome',l='Fornecedor',w=200),dict(k='merc',l='Mercadoria',t='num',a='r',pre='R$ '),dict(k='frete',l='Frete',t='num',a='r',pre='R$ '),
             dict(k='prazo',l='Prazo de entrega',t='num',a='r',u='dias'),dict(k='cond',l='Condição'),dict(k='tot',l='Custo comparável',t='num',a='r',pre='R$ '),dict(k='sit',l='Situação')],
        crow,gid='g_cmp',search=False,total=False,edit=dict(m='origin',title='Proposta',fields=[fs('nome','Fornecedor',ro=True),fs('cond','Condição',ro=True)]))
    js({},r'''
const BEST=%s, ALC=%s;
function PREVALS(self,v){ const sel=self.state.selp;
  RW(self,'g_cmp').forEach((r,i)=>{ r.p.tot=[i===0?B('R$ '+nf(r.v.tot)):T('R$ '+nf(r.v.tot))];
    r.p.sit=(sel===r.id)?[chipc('Selecionada','green')]:(i===0?[chipc('Melhor equalizado','green')]:[M('+R$ '+nf(r.v.tot-RW(self,'g_cmp')[0].v.tot))]); });
  }
function EXTRAVALS(self,v){
  v.sel_prop=()=>{ if(self.state.selp) return toast(self,BEST.nome+' já foi selecionada · justificativa registrada; nada muda'); self.setState({selp:BEST.id,g2toast:BEST.nome+' selecionada (R$ '+nf(BEST.tot)+' equalizado) · segue para aprovação de contratação: '+ALC}); }; }''' % (json.dumps(dict(id=best['f'],nome=best['nome'],tot=round(best['tot']))),json.dumps(_alcada(best['tot']))))
    # EX-50(a)-SUP (PR #106): sem rascunho fictício; falta de manutenção é conferida em Necessidades (SU-01), não enviada daqui
    corpo=(bloco('Cotações em andamento','Confira as respostas de cada cotação.',g)
           + bloco(f'Comparação equalizada · SOL-2026-07 · Fertilizantes','Compare mercadoria, frete, prazo e condição no mesmo critério e selecione a proposta.',gc
                   + nota('Itens: '+', '.join(n+' '+nf(o['qtd'])+' '+o['un'] for n,o in fert.items())+f". Alçada pelo valor: {_alcada(best['tot'])} (até R$ 300 mil)."),
                   acao=alink('SU-05.dc.html','Aprovar contratação','Abre contratos e pedidos','doc')))
    HEIGHTS37[fname]=1190
    shell37('SU-04','Solicitações e cotações',corpo,fname=fname,
      subtitle='Cotações nascem da necessidade (SOL-2026-07 e faltas de manutenção); a comparação equaliza propostas e a seleção registra justificativa.',
      status=(f'{sum(1 for gname in grupos if len(_cotacao(gname,grupos[gname]))==len([f for f in D2.FORNECEDORES if f["homologado"] and gname in f["grupos"]]))} prontas para comparar','yellow'),
      primary_html=primb('sel_prop',f"Selecionar {best['nome']}",'check'),
      footer='Token externo do fornecedor abre o portal PT-02, não esta lista; aprovar contratação segue em Contratos e pedidos (FO-16/FO-17). '
             'O fornecedor responde pelo portal externo com convite próprio, nunca por esta lista. A SOL-2026-07 veio de Planejar safra e é a mesma de Compra de insumos.')

# ================= SU-05 · Contratos, pedidos e entregas =================
C=dict(id='CT-2026-11',f=FORN['F01'],item='KCl 60%',contratado=140,liberado=PC88['qtd']//1000,recebido=PC88['recebido']//1000,apto=PC88['apto']//1000,
       quar=PC88['quarentena']//1000,pendente=PC88['a_entregar']//1000,a_liberar=140-PC88['qtd']//1000,limite=150000,
       apolice='limite de crédito Fertisul nº 88.412 · vigência até 30/11/2026',ritmo='2 cargas por semana · recebimento do Galpão 2: 36 t/dia')
C['exp']=C['pendente']*KCL_T; C['pico']=(C['pendente']+C['a_liberar'])*KCL_T
DIESEL_EXP=DIESEL['q']*DIESEL['preco']
def _rs(v): return f'R$ {nf(v/1000,1)} mil'
def su05():
    fname='SU-05.dc.html'; E._reset_screen(fname)
    ctr=[R('CT-2026-11',dict(ctr=f"{C['f']} · {C['id']}",item='KCl 60% · t',vol=C['contratado'],tol='−5% / +5% · v2 aceita',preco=KCL_T,pag='28 dias',exp=C['exp'],lim=C['limite'],resp='Comprador Léo',fim='2027-01-31',estado='Conflito'),
           {},o=[dict(t=f"Contratado {C['contratado']} t · liberado {C['liberado']} t (PC-088) · recebido {C['recebido']} t · a liberar {C['a_liberar']} t"),dict(t='Pagamento 28 dias em título único (NF 4501); sem barter'),dict(t='Abrir o contrato',h='SU-05det.dc.html')]),
         R('CT-2026-03',dict(ctr='Ipiranga Agro · CT-2026-03',item='Diesel S10 · mil L',vol=180,tol='±10% · hipótese, não aceita',preco=DIESEL['preco'],pag='quinzenal',exp=DIESEL_EXP,lim=120000,resp='Comprador Léo',fim='2026-12-31',estado='Vigente'),{},
           o=[dict(t='Contratado 180 mil L · liberado 103 · recebido 88 · pendente 15 mil L (PC-093)')]),
         R('CT-2026-08',dict(ctr='Santa Rita Insumos · CT-2026-08',item='Defensivos · consignação',vol=0,tol='por item · v1 aceita',preco=0,pag='acerto mensal',exp=22000,lim=80000,resp='Ana',fim='2027-06-30',estado='Consignado'),{},
           o=[dict(t='Consignado: Herbicida Z · H26-09 · 40 L no Almox. defensivos'),dict(t='Ver saldo consignado',h='SU-03.dc.html')])]
    gctr=grid([dict(k='ctr',l='Contraparte · contrato',w=240),dict(k='item',l='Item · unidade'),dict(k='vol',l='Contratado',t='num',a='r'),dict(k='tol',l='Tolerância (versão aceita)'),
               dict(k='preco',l='Preço · condição',t='num',a='r'),dict(k='exp',l='Exposição · limite',t='num',a='r'),dict(k='estado',l='Estado')],ctr,gid='g_ctr',total=False,
        edit=dict(m='form',title='Contrato',sub='Ajuste responsável, condição e vigência. Volume, preço e tolerância mudam só por aditivo aceito pela contraparte.',
          fields=[fs('resp','Responsável','sel',opts=['Comprador Léo','Ana'],req=True),fs('pag','Condição de pagamento','sel',opts=['28 dias','30 dias','quinzenal','acerto mensal','à vista'],req=True),
                  fs('fim','Fim da vigência','date',req=True),fs('tol','Tolerância','txt',ro=True,help='Muda só por aditivo.')]))
    peds=[]
    for p in D2.PEDIDOS:
        dep={'KCl 60%':'Galpão 2'}.get(p['item'],'Câmara fria'); uso={'PC-088':'plantio T4 e cobertura','PC-090':'plantio T1-A e T2 · out','PC-091':'plantio T1-B e T3 · out'}[p['id']]
        peds.append(R(p['id'],dict(ped=p['id'],forn=FORN[p['f']],item=p['item'],un=p['un'],qtd=p['qtd'],rec=p['recebido'],ae=p['a_entregar'],cheg='2026-'+p['previsao'][3:5]+'-'+p['previsao'][:2],uso=uso,dep=dep,estado=p['estado']),{},**({'o':[dict(t=D.CANON['PC088']),dict(t='Abrir o contrato CT-2026-11',h='SU-05det.dc.html')]} if p['id']=='PC-088' else {})))
    peds.append(R('PC-093',dict(ped='PC-093',forn='Ipiranga Agro',item='Diesel S10',un='L',qtd=DIESEL['q'],rec=0,ae=DIESEL['q'],cheg='2026-09-26',uso='frota do plantio',dep='Tanque Sede',estado='Confirmado'),{}))
    peds.append(R('PC-094',dict(ped='PC-094',forn='Casa das Peças',item='Kit filtros + óleo 15W40',un='kit',qtd=1,rec=0,ae=1,cheg='2026-09-26',uso='OM-0234 · preventiva',dep='Almox. oficina',estado='A confirmar'),{}))
    gped=grid([dict(k='ped',l='Pedido · fornecedor',w=200),dict(k='item',l='Item'),dict(k='qtd',l='Quantidade',t='num',a='r'),dict(k='rec',l='Recebido',t='num',a='r'),dict(k='ae',l='A entregar',t='num',a='r'),
               dict(k='cheg',l='Chegada prevista',t='date'),dict(k='uso',l='Uso previsto'),dict(k='dep',l='Depósito'),dict(k='estado',l='Estado')],peds,gid='g_ped',total=False,
        edit=dict(m='form',title='Pedido',sub='Ajuste chegada, uso e depósito. Quantidade e preço mudam só com o fornecedor; recebimento parcial mantém o saldo aberto.',
          fields=[fs('cheg','Chegada prevista','date',req=True),fs('uso','Uso previsto',req=True),fs('dep','Depósito','sel',opts=DEPOS,req=True)]))
    car=[('c12','Cargas 1–2 · CT-2026-11 · PC-088','KCl 60%','60 t','19/09 · NF 4501','adubação','Galpão 2',0,'Recebida','green'),
         ('c3','Carga 3 · CT-2026-11 · PC-088','KCl 60%','40 t','02/10','plantio T4 · até 10/10','Galpão 2',C['exp'],'A entregar','yellow'),
         ('c4','Carga 4 · CT-2026-11 · proposta','KCl 60%','40 t','08/10 (proposta)','cobertura nov · T4, T3, P1 e P2','Galpão 2',C['pico'],'Conflito','red'),
         ('d12','Carga D-12 · CT-2026-03 · PC-093','Diesel S10','15 mil L','26/09','frota do plantio','Tanque Sede',DIESEL_EXP,'Pronta','green'),
         ('s90','PC-090 · Coop. Vale','Semente de soja 58 W','20.000 kg','05/10','plantio T1-A e T2','Câmara fria',0,'Confirmada','green'),
         ('s91','PC-091 · Sementes Vale','Semente de soja 62 X','8.000 kg','08/10','plantio T1-B e T3','Câmara fria',0,'Confirmada','green')]
    gcar=grid([dict(k='c',l='Carga · contrato/pedido',w=240),dict(k='i',l='Item'),dict(k='q',l='Quantidade',a='r'),dict(k='d',l='Chegada'),dict(k='u',l='Uso previsto (cobertura)',w=180),
               dict(k='dp',l='Depósito'),dict(k='e',l='Exposição projetada',t='num',a='r'),dict(k='s',l='Estado')],
        [R(i,dict(c=c,i=it,q=q,d=d,u=u,dp=dp,e=e),dict(c=[b(c)],e=([txt(_rs(e))] if e else [mut('—')]),s=[ch(st,cc)])) for i,c,it,q,d,u,dp,e,st,cc in car],gid='g_car',total=False,edit='ro' and dict(m='ro',title='Carga',fields=[fs('c','Carga',ro=True),fs('u','Uso previsto',ro=True)]))
    gitem=grid([dict(k='i',l='Item',w=200),dict(k='c',l='Contratado'),dict(k='r',l='Recebido'),dict(k='l',l='Liberado pendente'),dict(k='p',l='Proposto'),dict(k='s',l='Estado')],
        [R('i1',dict(i='KCl 60%',c='140 t',r='60 t (50 aptas + 10 quarentena)',l='40 t',p='40 t'),dict(s=[ch('Conflito','red')])),
         R('i2',dict(i='Diesel S10',c='180 mil L',r='88 mil L',l='15 mil L',p='—'),dict(s=[ch('Pronta','green')])),
         R('i3',dict(i='Sementes (PC-090 e PC-091)',c='—',r='0 kg',l='28.000 kg',p='—'),dict(s=[ch('Confirmado','green')]))],gid='g_itm',search=False,total=False,edit=dict(m='ro',title='Item',fields=[fs('i','Item',ro=True)]))
    gdep=grid([dict(k='d',l='Depósito',w=200),dict(k='c',l='Capacidade'),dict(k='o',l='Ocupação na chegada'),dict(k='e',l='Exposição projetada'),dict(k='l',l='Limite'),dict(k='s',l='Estado')],
        [R('d1',dict(d='Galpão 2',c='250 t · 36 t/dia',o='190 t em 02/10 (76 %)',e=f"{_rs(C['exp'])} → {_rs(C['pico'])} com a carga 4",l=f"{_rs(C['limite'])} (Fertisul)"),dict(s=[ch('Conflito','red')])),
         R('d2',dict(d='Tanque Sede',c='60 mil L',o='27,4 mil L em 26/09 (46 %)',e=_rs(DIESEL_EXP),l='R$ 120,0 mil (Ipiranga)'),dict(s=[ch('Dentro','green')])),
         R('d3',dict(d='Câmara fria',c='40 t',o='40 t em 08/10 (100 %)',e='—',l='sem limite cadastrado'),dict(s=[ch('No limite','yellow')]))],gid='g_dep',search=False,total=False,edit=dict(m='ro',title='Depósito',fields=[fs('d','Depósito',ro=True)]))
    gmes=grid([dict(k='m',l='Mês',w=140),dict(k='c',l='Cargas'),dict(k='q',l='Quantidade'),dict(k='e',l='Exposição de pico'),dict(k='s',l='Estado')],
        [R('m1',dict(m='set/2026',c='cargas 1–2 · D-12',q='60 t · 15 mil L',e=_rs(DIESEL_EXP)),dict(s=[ch('Em curso','green')])),
         R('m2',dict(m='out/2026',c='carga 3 (+ carga 4 proposta) · sementes',q='40 t (+40 t) · 28 t de semente',e=f"{_rs(C['exp'])} ({_rs(C['pico'])} com a proposta)"),dict(s=[ch('Conflito','red')])),
         R('m3',dict(m='nov/2026',c='cobertura',q='—',e='—'),dict(s=[ch('A programar','gray')]))],gid='g_mes',search=False,total=False,edit=dict(m='ro',title='Mês',fields=[fs('m','Mês',ro=True)]))
    bar,panes=tabs(['Por carga','Por item','Por depósito','Por mês'],[gcar,gitem,gdep,gmes])
    pn={'ctr':dict(title='Formalizar contrato',sub='Nasce da proposta selecionada na comparação da SOL-2026-07 · Fertilizantes.',ok='Formalizar contrato',
        fields=[fs('cp','Contraparte','sel',opts=['Fertisul','Casa do Adubo','Coop. Vale'],req=True,**{'def':'Fertisul'}),fs('item','Itens','txt',req=True,**{'def':'MAP 11-52, NPK 20-05-20 e nitratos (SOL-2026-07)'}),
                fs('vol','Volume líquido preliminar','num',req=True,min=0.1,u='t',**{'def':'78,85'}),fs('tol','Tolerância inferior/superior','sel',opts=['−5% / +5%','−10% / +10%','sem tolerância'],req=True,**{'def':'−5% / +5%'}),
                fs('pag','Condição de pagamento','sel',opts=['28 dias','30 dias','à vista'],req=True,**{'def':'28 dias'}),fs('fim','Fim da vigência','date',req=True,**{'def':'2027-01-31'})])}
    js(pn,r'''
const CH={Conflito:'red',Vigente:'green'};
CHECK.ctr=(self)=>(self.state.ctr14?{cp:'O contrato CT-2026-14 já foi formalizado · nada criado de novo.'}:null);
RUN.ctr=(self,d)=>{ setRows(self,'g_ctr',rows=>{ rows.push({id:'CT-2026-14',v:{ctr:d.cp+' · CT-2026-14',item:d.item,vol:g2num(d.vol),tol:d.tol+' · v1',preco:0,pag:d.pag,exp:0,lim:0,resp:'Comprador Léo',fim:d.fim,estado:'Aguardando aceite'},s:{},p:{},o:[{t:'Formalizado a partir da proposta selecionada · aguarda o aceite da contraparte'}]}); });
  self.setState({ctr14:true}); return 'Contrato CT-2026-14 formalizado com '+d.cp+' · aguarda aceite da contraparte (simulado · nenhuma mensagem real enviada)'; };
function PREVALS(self,v){
  RW(self,'g_ctr').forEach(r=>{ const V=r.v; r.p.ctr=[B(V.ctr)].concat(r.id==='CT-2026-11'?[BRK,{k:'link',t:'Abrir contrato',h:'SU-05det.dc.html'}]:[]); r.s.ctr=V.ctr;
    r.p.vol=[V.vol?T(nf(V.vol,V.vol%1?2:0)+(r.id==='CT-2026-03'?' mil L':' t')):M('por item')];
    r.p.preco=[V.preco?T('R$ '+nf(V.preco,V.preco<100?2:0)+(r.id==='CT-2026-03'?'/L':'/t')):M('tabela'),M(V.pag)];
    r.p.exp=[V.lim?T('R$ '+nf(V.exp/1000,1)+' mil'):M('—'),M(V.lim?'de R$ '+nf(V.lim/1000,0)+' mil':'')];
    const e=String(V.estado); r.p.estado=[chipc(e,e.indexOf('Conflito')===0?'red':(e==='Aguardando aceite'?'yellow':'green'))]; });
  RW(self,'g_ped').forEach(r=>{ const V=r.v, u=' '+V.un; r.p.ped=[B(V.ped),M(V.forn)]; r.s.ped=V.ped+' '+V.forn;
    ['qtd','rec','ae'].forEach(k=>{ r.p[k]=[V[k]?T(nf(V[k])+u):M('—')]; });
    r.p.estado=[chipc(V.ae&&V.rec?'Parcial':V.estado,V.ae&&V.rec?'yellow':(V.estado==='Confirmado'?'green':'yellow'))]; }); }
function EXTRAVALS(self,v){ pnVals(self,v); sims(self,v); }''',
    simsd=dict(ped='PC-095 programado · 11.000 L contra o CT-2026-03 · emissão automática em 26/09, depois do recebimento do PC-093; a exposição fica em R$ 64,2 mil, dentro do limite de R$ 120 mil',
               conf='Fertisul confirmou a carga 3 (40 t) para 02/10 · programação atualizada sem alterar o contratado (simulado · nenhuma mensagem real enviada)',
               pico=f"Pico projetado {_rs(C['exp'])} em 02/10 (carga 3) · dentro do limite de {_rs(C['limite'])} · emitir a carga 4 antes de receber a 3 levaria o pico a {_rs(C['pico'])} (conflito)"))
    painel()
    corpo=(kpis([('Conflitos','1','carga 4 · CT-2026-11'),('A receber até 26/09','3','NF 4533 · PC-093 · PC-094'),('Liberado a entregar',_rs(C['exp']+DIESEL_EXP),'KCl · diesel'),('Contratos vigentes','3','Fertisul · Ipiranga · Santa Rita Insumos')])
           + bloco('Contratos de fornecimento','Confira contratado, liberado e exposição de cada contrato; clique na linha para ajustar condição e vigência.',gctr
                   ,
                   acao=mini('open_ctr','Formalizar contrato','Cria o contrato a partir da proposta selecionada','doc'))
           + bloco('Pedidos','Confira o que falta entregar em cada pedido; clique na linha para ajustar chegada, uso e depósito.',gped
                   ,
                   acao=mini('sim_ped','Emitir pedido','Programa o próximo pedido de diesel contra o contrato','cart')+mini('sim_conf','Confirmar fornecedor','Registra a confirmação da carga pelo fornecedor','check')+alink('SU-06.dc.html','Receber','Abre Recebimentos para conferir a entrega','truck'))
           + bloco('Programação de entregas','Simule o pico de exposição e o ritmo de cargas antes de liberar; o que passa do limite vira conflito.',
                   f'<div style="padding: 0 0 10px;">{bar}</div>'+panes,acao=mini('sim_pico','Simular pico de exposição','Calcula o pico por data sem liberar nada','trend')))
    HEIGHTS37[fname]=1580
    shell37('SU-05','Contratos, pedidos e entregas',corpo,fname=fname,
      subtitle='Contratos, pedidos e programação de entregas com saldos explícitos e exposição em R$ quando há limite.',
      status=('1 conflito de liberação','red'),primary_html=prima('SU-05det.dc.html','Resolver conflito da carga 4'),
      footer='Proposta de carga não equivale a entrega confirmada; capacidade do depósito e validade seguem 65.5 / PCE-08. Antecipação e prazo têm títulos próprios (GE-04). '
             'O recebido já está dentro das liberações acumuladas e não é subtraído de novo do saldo contratual. Recebimento parcial mantém o saldo do pedido aberto; o aceite físico acontece em Recebimentos.')

# ---- SU-05det · contrato CT-2026-11 · Fertisul · KCl 60% ----
def su05det():
    fname='SU-05det.dc.html'; E._reset_screen(fname); PARENT37[fname]='SU-05.dc.html'
    sal=[('ct','Contratado',f"{C['contratado']} t",f"{C['id']} · versão v2 aceita"),('tol','Tolerância inferior/superior','−5% / +5%','aceita pela Fertisul na v2'),
         ('lib','Liberado acumulado',f"{C['liberado']} t (cargas 1–3)",'pedido PC-088'),('rec','Recebido',f"{C['recebido']} t ({C['apto']} aptas + {C['quar']} em quarentena)",'NF 4501 · 19/09'),
         ('pen','Liberado pendente de entrega',f"{C['pendente']} t (carga 3)",'chegada 02/10'),('alib','Saldo a liberar',f"{C['a_liberar']} t (carga 4 proposta)",f"{C['contratado']} − {C['liberado']} liberadas"),
         ('pr','Preço · condição',f"R$ {nf(KCL_T)}/t · 28 dias",'título único na NF · sem barter')]
    gs=grid([dict(k='m',l='Medida',w=300),dict(k='v',l='Valor',w=360),dict(k='f',l='Fonte',w=360)],[R(i,dict(m=m,v=v,f=f)) for i,m,v,f in sal],gid='g_sal',search=False,total=False,
        edit=dict(m='origin',title='Saldo do contrato',fields=[fs('m','Medida',ro=True),fs('v','Valor',ro=True)]))
    lib=[('c12','Cargas 1–2','60 t','19/09','adubação · set',0,'Recebida','green'),('c3','Carga 3','40 t','02/10','plantio T4 · até 10/10',C['exp'],'Liberada · a entregar','yellow'),
         ('c4','Carga 4 (proposta)','40 t','08/10','cobertura nov · T4, T3, P1 e P2',C['pico'],'Conflito · acima do limite','red')]
    gl=grid([dict(k='c',l='Liberação · carga',w=220),dict(k='q',l='Quantidade',a='r'),dict(k='d',l='Chegada prevista'),dict(k='u',l='Cobertura atendida'),dict(k='e',l='Exposição projetada',t='num',a='r'),dict(k='s',l='Estado')],
        [R(i,dict(c=c,q=q,d=d,u=u,e=e),dict(c=[b(c)],e=([txt(_rs(e))] if e else [mut('—')]),s=[ch(st,cc)])) for i,c,q,d,u,e,st,cc in lib],gid='g_lib',search=False,total=False,
        edit=dict(m='ro',title='Liberação',fields=[fs('c','Carga',ro=True),fs('u','Cobertura',ro=True)]))
    pn={'rep':dict(title='Reprogramar carga 4',sub='Emitir depois de receber a carga 3 mantém o pico dentro do limite de crédito.',ok='Reprogramar carga 4',
        fields=[fs('em','Nova emissão','date',req=True,**{'def':'2026-10-10'}),fs('ch','Chegada prevista','date',req=True,**{'def':'2026-10-15'}),
                fs('mot','Motivo','txt',req=True,**{'def':'pico de exposição acima do limite de crédito'})])}
    js(pn,r'''
const EXP=%s, PICO=%s, LIM=%s;
CHECK.rep=(self,d)=>{ if(d.em<='2026-10-02') return {em:'Emita depois de 02/10 (chegada da carga 3); antes disso o pico chega a R$ '+nf(PICO/1000,1)+' mil.'}; if(d.ch<d.em) return {ch:'A chegada não pode ser antes da emissão.'}; return null; };
RUN.rep=(self,d)=>{ self.setState({rep:{em:d.em,ch:d.ch}}); return 'Carga 4 reprogramada: emissão '+dm(d.em)+', chegada '+dm(d.ch)+' · pico volta a R$ '+nf(EXP/1000,1)+' mil · Fertisul avisada (simulado · nenhuma mensagem real enviada)'; };
function PREVALS(self,v){ const rp=self.state.rep; const r=RF(self,'g_lib','c4'); if(!r) return;
  if(rp){ r.v.d=dm(rp.ch); r.v.e=EXP; r.p.c=[B('Carga 4')]; r.p.e=[T('R$ '+nf(EXP/1000,1)+' mil')]; r.p.s=[chipc(self.state.emit?'Liberação agendada · '+dm(rp.em):'Reprogramada · dentro do limite','green')]; } }
function EXTRAVALS(self,v){ pnVals(self,v); const rp=self.state.rep;
  if(rp) hstatus(v,self.state.emit?'Carga 4 agendada · dentro do limite':'Carga 4 reprogramada · dentro do limite','green'); else hstatus(v,'Conflito · carga 4 acima do limite','red');
  v.norep=!rp; v.hasrep=!!rp; v.pico_v='R$ '+nf((rp?EXP:PICO)/1000,1)+' mil'; v.pico_t=rp?'PICO APÓS REPROGRAMAR':'PICO COM A CARGA 4'; v.pico_s=rp?'carga 4 emitida depois de receber a 3':'se emitida antes de receber a carga 3';
  v.pico_st='border: 1px solid '+(rp?'#E4E9E5':'#B42318')+'; border-radius: 12px; padding: 12px 14px;'; v.pico_c='font-size: 22px; font-weight: 800; margin-top: 4px; color: '+(rp?'#15201A':'#B42318')+';';
  v.ct_aqui=rp?'Carga 4 reprogramada':'Carga 4 em conflito'; v.ct_falta=rp?'Emitir a liberação':'Carga 4 dentro do limite'; v.ct_prox=rp?'Emitir liberação da carga 4':'Reprogramar carga 4';
  v.do_emit=()=>{ const s=self.state; if(!s.rep) return toast(self,'Bloqueado · o pico projetado de R$ '+nf(PICO/1000,1)+' mil passa do limite de R$ '+nf(LIM/1000,0)+' mil. Reprograme a emissão para depois de 02/10 ou solicite ampliação de crédito. Responsável: comprador Léo.');
    if(s.emit) return toast(self,'Liberação da carga 4 já agendada para '+dm(s.rep.em)+' · nada emitido de novo');
    self.setState({emit:true,g2toast:'Liberação da carga 4 agendada para '+dm(s.rep.em)+' · emite só depois do recebimento da carga 3 (simulado)'}); }; }''' % (C['exp'],C['pico'],C['limite']))
    painel()
    card=lambda t,vv,sub,bd=LINE: (f'<div style="border: 1px solid {bd}; border-radius: 12px; padding: 12px 14px;"><div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em;">{t}</div>'
                                   f'<div style="font-size: 22px; font-weight: 800; margin-top: 4px;">{vv}</div><div style="font-size: 12px; color: {MUTED};">{sub}</div></div>')
    cards=(f'<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">'
           + card('EXPOSIÇÃO ATUAL',_rs(C['exp']),f"{C['pendente']} t liberadas e não recebidas")
           + f'<div style="{H("pico_st")}"><div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em;">{H("pico_t")}</div><div style="{H("pico_c")}">{H("pico_v")}</div><div style="font-size: 12px; color: {MUTED};">{H("pico_s")}</div></div>'
           + card('LIMITE',_rs(C['limite']),esc(C['apolice']))+'</div>')
    corpo=(continuity('Falta firme coberta pelo contrato',H('ct_aqui'),H('ct_falta'),H('ct_prox'))
           + bloco('Saldos do contrato','Confira contratado, liberado, recebido e a liberar; o recebido não é subtraído duas vezes.',gs)
           + bloco('Exposição financeira do fornecedor','Compare a exposição atual e projetada com o limite de crédito e sua vigência.',cards)
           + bloco('Plano de liberações por cobertura','Confira o ritmo das cargas contra a capacidade de recebimento e o limite de exposição.',gl+nota(f"Ritmo: {C['ritmo']} · validade 04/2028 comporta o plano."),
                   acao=f'<sc-if value="{H("norep")}" hint-placeholder-val="{T()}">'+mini('do_emit','Emitir liberação da carga 4','Tenta emitir agora; mostra o bloqueio e como resolver','alert')+'</sc-if>'
                        +alink('GE-08.dc.html','Solicitar crédito','Pede ampliação do limite de crédito','cash')))
    prim=(f'<sc-if value="{H("norep")}" hint-placeholder-val="{T()}">{primb("open_rep","Reprogramar carga 4","calendar")}</sc-if>'
          f'<sc-if value="{H("hasrep")}" hint-placeholder-val="{F()}">{primb("do_emit","Emitir liberação da carga 4","check")}</sc-if>')
    HEIGHTS37[fname]=1180
    shell37('SU-05',f"{C['id']} · Fertisul · KCl 60%",corpo,fname=fname,crumbs_extra=[C['id']],
      subtitle='Contratado, liberado, recebido e a liberar com tolerância aceita, exposição em R$ e plano de liberações por cobertura.',
      status=(MARK,'gray'),primary_html=prim,
      footer='Emitir liberação passa pela simulação de pico e ritmo de cargas (65.5.1 / PCE-08); o recebido não é subtraído de novo do saldo contratual.')
    dyn_status(fname)

# ================= SU-06 · Recebimentos e divergências =================
INSP=['Visual · aprovada','Em laudo · quarentena','Reprovada · segregar']
DIVS=['Sem divergência','Falta','Sobra','Avaria','Item diferente do pedido']
PRECO_NF_DIESEL=5.96
def su06():
    fname='SU-06.dc.html'; E._reset_screen(fname)
    r0=D2.RECEBIMENTOS[0]; r1=D2.RECEBIMENTOS[1]; p90=PED[r1['pedido']]
    rows=[
     R('r4501',dict(doc=r0['id'],ped=r0['pedido'],forn=FORN[r0['f']],item=r0['item'],lote=r0['lote'],un=r0['un'],nf=r0['qtd_nf'],conf=r0['qtd_conf'],apto=r0['apto'],quar=r0['quarentena'],
                    val=K11['validade'],insp=INSP[1],dep=K11['local'],div=DIVS[0],st='conf',aberto=PC88['a_entregar'],chega='19/09'),{},ro=True,
       o=[dict(t=f"Conferida em {r0['data']}: {nf(r0['qtd_conf'])} kg contra a NF de {nf(r0['qtd_nf'])} kg · lote {r0['lote']} no {K11['local']}"),
          dict(t=f"{nf(r0['quarentena'])} kg em quarentena até o laudo de umidade (prazo 27/09) · fora do disponível e da cobertura firme"),
          dict(t=f"Pedido {PC88['id']}: {nf(PC88['qtd'])} kg · recebido {nf(PC88['recebido'])} · a entregar {nf(PC88['a_entregar'])} kg (carga 3 em 02/10)"),
          dict(t='Título encaminhado a Contas a pagar',h='GE-04.dc.html'),dict(t='Ver o saldo do lote',h='SU-03.dc.html')]),
     R('dup',dict(doc=r0['id']+' · 2ª leitura',ped=r0['pedido'],forn=FORN[r0['f']],item=r0['item'],lote=r0['lote'],un=r0['un'],nf=r0['qtd_nf'],conf='',apto=0,quar=0,val='',insp='',dep='',div=DIVS[0],st='dup',aberto=0,chega='23/09'),{},ro=True,
       o=[dict(t='Mesma chave de acesso da NF 4501, lida de novo às 10:12 de 23/09'),dict(t='Nenhuma entrada nova: o recibo original REC-4501 foi devolvido')]),
     R('r4533',dict(doc=r1['id'],ped=r1['pedido'],forn=FORN[p90['f']],item=r1['item'],lote=r1['lote'],un=r1['un'],nf=r1['qtd_nf'],conf='',apto=0,quar=0,val='',insp='',dep='Câmara fria',div=DIVS[0],st='pend',aberto=p90['a_entregar'],chega='24/09'),{},
       o=[dict(t=f"Pedido {p90['id']} · {FORN[p90['f']]} · {nf(p90['qtd'])} kg a R$ {nf(p90['preco'],2)}/kg"),dict(t='Uso previsto: plantio T1-A e T2 (Safra 2026/27)'),dict(t='Ver o pedido',h='SU-05.dc.html')]),
     R('r8812',dict(doc='NF 8812',ped=DIESEL['ped'],forn='Ipiranga Agro',item='Diesel S10',lote='tanque',un='L',nf=DIESEL['q'],conf='',apto=0,quar=0,val='',insp='',dep='Tanque Sede',div='Preço',st='carga',aberto=DIESEL['q'],chega='26/09'),{},ro=True,
       o=[dict(t=f"NF antecipada a R$ {nf(PRECO_NF_DIESEL,2)}/L contra R$ {nf(DIESEL['preco'],2)}/L do contrato {DIESEL.get('ctr','CT-2026-03')}"),
          dict(t=f"Diferença de R$ {nf(PRECO_NF_DIESEL-DIESEL['preco'],2)}/L × {nf(DIESEL['q'])} L = R$ {nf((PRECO_NF_DIESEL-DIESEL['preco'])*DIESEL['q'],2)}"),dict(t='Ver o contrato',h='SU-05.dc.html')]),
     R('r094',dict(doc='sem NF',ped='PC-094',forn='Casa das Peças',item='Kit filtros + óleo 15W40',lote='',un='kit',nf=1,conf='',apto=0,quar=0,val='',insp='',dep='Almox. oficina',div=DIVS[0],st='aguarda',aberto=1,chega='26/09'),{},ro=True,
       o=[dict(t='Pedido PC-094 · a confirmar pelo fornecedor · uso OM-0234 (preventiva da colhedora)'),dict(t='Ver o pedido',h='SU-05.dc.html')])]
    g=grid([dict(k='doc',l='Documento · pedido',w=190),dict(k='item',l='Item · lote',w=170),dict(k='conf',l='Conferido',t='num',a='r'),dict(k='apto',l='Apto · retido',t='num',a='r'),
            dict(k='insp',l='Inspeção · divergência',w=220),dict(k='est',l='Físico · título · ação',w=230)],
        rows,gid='g_rec',total=False,
        edit=dict(m='form',title='Recebimento',sub='Registre o que foi conferido contra o pedido e a NF. Parcial mantém o saldo do pedido aberto; aceite físico não aprova o título.',
          fields=[fs('conf','Quantidade conferida','num',req=True,min=0,max=r1['qtd_nf']*1.05,u='kg',help=f"NF {nf(r1['qtd_nf'])} kg · tolerância de +5 %."),
                  fs('lote','Lote','txt',req=True),fs('val','Validade','txt',req=True,help='mês/ano, ex.: 09/2027'),
                  fs('insp','Inspeção','sel',opts=INSP,req=True,help='Em laudo retém tudo em quarentena até o resultado.'),
                  fs('dep','Depósito','sel',opts=DEPOS,req=True),fs('div','Divergência','sel',opts=DIVS,req=True)]))
    pn={'div':dict(title='Resolver diferença · NF 8812',sub=f"Preço da NF R$ {nf(PRECO_NF_DIESEL,2)}/L contra R$ {nf(DIESEL['preco'],2)}/L do contrato. A decisão não muda o aceite físico da carga.",ok='Registrar decisão',
          fields=[fs('dec','Decisão','sel',opts=['Aceitar físico e contestar título','Aceitar diferença por aditivo','Recusar a NF'],req=True,**{'def':'Aceitar físico e contestar título'}),
                  fs('resp','Responsável','sel',opts=['Comprador Léo','Ana (gestora)'],req=True,**{'def':'Comprador Léo'}),fs('obs','Observação','area')]),
        'seg':dict(title='Segregar lote',sub='Move a quantidade do apto para retido; sai do disponível e da cobertura firme até nova liberação.',ok='Segregar',
          fields=[fs('lote','Lote','sel',opts=[f"{K11['lote']} · {K11['item']} · {K11['local']}"],req=True,**{'def':f"{K11['lote']} · {K11['item']} · {K11['local']}"}),
                  fs('q','Quantidade','num',req=True,min=1,u='kg',maxfn='apto'),fs('mot','Motivo','txt',req=True,help='Ex.: sacaria molhada na descarga.')])}
    code=r'''
const DIESEL_OK=__DOK__, DIESEL_NF=__DNF__, DIESEL_Q=__DQ__;
function qq(n,un){ return nf(n,(n%1)?1:0)+' '+un; }
MAXFN.apto=(self)=>{ const r=RF(self,'g_rec','r4501'); return r?r.v.apto:0; };
CHECK.div=(self)=>(self.state.divok?{dec:'Diferença já decidida ('+self.state.divok+') · nada registrado de novo.'}:null);
RUN.div=(self,d)=>{ setRows(self,'g_rec',rows=>{ const r=rows.find(x=>x.id==='r8812'); r.v.div=d.dec; });
  self.setState({divok:d.dec}); const dif=(DIESEL_NF-DIESEL_OK)*DIESEL_Q;
  if(d.dec==='Recusar a NF') return 'NF 8812 recusada · a carga de 26/09 só entra com NF corrigida · '+d.resp+' responde';
  if(d.dec==='Aceitar diferença por aditivo') return 'Diferença de R$ '+nf(dif,2)+' vai a aditivo do CT-2026-03 · aguarda aceite do gestor · físico segue normal';
  return 'Físico aceito na chegada · título contestado em R$ '+nf(dif,2)+' (retido até a NF de ajuste) · '+d.resp+' acompanha'; };
RUN.seg=(self,d)=>{ const q=g2num(d.q); let a=0,b=0; setRows(self,'g_rec',rows=>{ const r=rows.find(x=>x.id==='r4501'); a=r.v.apto; r.v.apto-=q; r.v.quar+=q; b=r.v.apto; r.v.insp='Segregado · '+d.mot; });
  self.setState({lib:null}); return 'Segregados '+qq(q,'kg')+' do K26-11 · apto '+nf(a)+' → '+nf(b)+' kg · fora da cobertura firme até nova liberação'; };
function PREVALS(self,v){ const lib=self.state.lib;
  RW(self,'g_rec').forEach(r=>{ const V=r.v, u=V.un; const c=(V.conf===''||V.conf===null||V.conf===undefined)?null:Number(V.conf);
    r.p.doc=[B(V.doc),M(V.ped+' · '+V.forn)]; r.s.doc=V.doc+' '+V.ped+' '+V.forn;
    r.p.item=[T(V.item)].concat(V.lote?[M(V.lote)]:[]); r.s.item=V.item+' '+V.lote;
    if(V.st==='dup'){ ['conf','apto','insp'].forEach(k=>{ r.p[k]=[M('—')]; }); r.p.est=[chipc('Duplicado · sem nova entrada','gray')]; r.s.est='Duplicado'; return; }
    r.p.conf=c===null?[M('NF '+qq(V.nf,u))]:[T(qq(c,u))].concat(c!==V.nf?[M('NF '+qq(V.nf,u))]:[]); r.s.conf=c===null?'':c;
    r.p.apto=c===null?[M('—')]:[V.apto?B(qq(V.apto,u)):M('0 apto')].concat(V.quar?[BRK,chipc(qq(V.quar,u)+' retidos','yellow')]:[]);
    const ins=String(V.insp||''); r.p.insp=ins?[chipc(ins,ins.indexOf('aprovad')>=0||ins.indexOf('Laudo')===0?'green':(ins.indexOf('Reprov')===0||ins.indexOf('Segreg')===0?'red':'yellow'))]:[M(u==='L'?'isenta':(u==='kit'?'visual na chegada':'—'))]; r.s.insp=ins;
    const dv=String(V.div||''); if(dv&&dv!=='Sem divergência'){ r.p.insp=r.p.insp.concat([BRK,chipc(dv==='Preço'?'Preço +R$ '+nf(DIESEL_NF-DIESEL_OK,2)+'/L':dv,dv==='Preço'||dv==='Falta'||dv==='Avaria'||dv==='Recusar a NF'?'red':'yellow')]); } r.s.insp=ins+' '+dv;
    if(V.st==='conf'){ const ab=V.aberto; r.p.est=[chipc(ab?'Parcial · '+qq(ab,u)+' abertos':'Aceito',ab?'yellow':'green'),BRK,
        r.id==='r4501'?M('título encaminhado'):{k:'link',t:'Encaminhar título',h:'GE-04.dc.html'}]; r.s.est=ab?'Parcial':'Aceito'; }
    else if(V.st==='pend'){ r.p.est=[chipc('A conferir · chega '+V.chega,'yellow')]; r.s.est='A conferir'; }
    else { r.p.est=[chipc((V.st==='carga'?'Aguarda carga · ':'Aguarda chegada · ')+V.chega,'gray')]; r.s.est='Aguarda'; }
    if(r.id==='r4501') r.p.est=r.p.est.concat(V.quar>0?[BRK,{k:'act',t:'Liberar qualidade',fn:'do_lib:K26-11'}]:(lib?[BRK,M('liberado · '+lib.rc)]:[])); }); }
function EXTRAVALS(self,v){ pnVals(self,v); sims(self,v); const rs=RW(self,'g_rec');
  const rq=rs.find(x=>x.id==='r4501'), rn=rs.find(x=>x.id==='r4533'), rd=rs.find(x=>x.id==='r8812');
  const ndiv=rs.filter(x=>x.v.st!=='dup'&&x.v.div&&x.v.div!=='Sem divergência'&&!(x.id==='r8812'&&self.state.divok)).length;
  const quar=rs.reduce((a,x)=>a+(x.v.un==='kg'&&x.v.st==='conf'?Number(x.v.quar)||0:0),0);
  const pend=rs.filter(x=>x.v.st==='pend'||x.v.st==='carga'||x.v.st==='aguarda');
  v.k_div=String(ndiv); v.k_div_s=ndiv?(self.state.divok?'':'preço da NF 8812 · diesel'):'nenhuma aberta';
  v.k_quar=nf(quar/1000,quar%1000?1:0)+' t'; v.k_quar_s=quar?'K26-11 · laudo até 27/09':(self.state.lib?'laudo aprovado · '+self.state.lib.rc:'nada retido');
  v.k_pend=String(pend.length); v.k_pend_s=pend.map(x=>x.v.doc==='sem NF'?x.v.ped:x.v.doc).join(' · ')||'nada a receber';
  const ab=rs.filter(x=>x.v.st!=='dup'&&(x.v.st!=='conf'||x.v.aberto>0)); v.k_ab=String(ab.length); v.k_ab_s=ab.map(x=>x.v.ped).join(' · ')||'todos entregues';
  const parts=[]; if(ndiv) parts.push(ndiv+(ndiv>1?' divergências':' divergência')); if(quar) parts.push(nf(quar/1000)+' t em quarentena');
  hstatus(v,parts.length?parts.join(' · '):'Sem divergência aberta · nada em quarentena',ndiv?'red':(quar?'yellow':'green'));
  v.pend4533=rn.v.st==='pend'; v.done4533=!v.pend4533;
  v.conf4533=()=>g2open(self,GR('g_rec'),'r4533');
  v.ler=()=>{ const n=RF(self,'g_rec','r4533'); if(n.v.st==='pend'){ toast(self,'Chave da NF 4533 lida · pedido PC-090 localizado (simulado)'); g2open(self,GR('g_rec'),'r4533'); } else toast(self,'NF 4533 já recebida · nova leitura não cria segunda entrada'); };
  v.do_lib=()=>{ const s=self.state; if(s.lib) return toast(self,'Já liberado em '+s.lib.em+' · recibo '+s.lib.rc+', nada somado de novo'); let q=0,a=0,b=0;
    setRows(self,'g_rec',rows=>{ const r=rows.find(x=>x.id==='r4501'); q=r.v.quar; a=r.v.apto; r.v.apto+=q; r.v.quar=0; b=r.v.apto; r.v.insp='Laudo aprovado · LAB-4501'; });
    self.setState({lib:{em:'23/09',rc:'LQ-2031'},g2toast:'Laudo LAB-4501 aprovado · '+nf(q)+' kg liberados no K26-11: apto '+nf(a)+' → '+nf(b)+' kg, quarentena '+nf(q)+' → 0 · somado uma única vez (recibo LQ-2031)'}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_rec'||!r||r.id!=='r4533') return; const c=Number(r.v.conf)||0; const ins=String(r.v.insp);
    const ret=(ins.indexOf('Em laudo')===0||ins.indexOf('Reprov')===0);
    r.v.apto=ret?0:c; r.v.quar=ret?c:0; r.v.st='conf'; r.v.aberto=Math.max(0,r.v.nf-c); r.ro=true;
    if(c<r.v.nf&&r.v.div==='Sem divergência') r.v.div='Falta';
    self.setState({g2toast:'NF 4533 conferida: '+qq(c,'kg')+' · apto '+nf(r.v.apto)+' · retido '+nf(r.v.quar)+' kg · PC-090 a entregar 20.000 → '+nf(r.v.aberto)+' kg · título a encaminhar (aceite físico ≠ aprovação financeira)'}); }; }'''
    js(pn,code.replace('__DOK__',str(DIESEL['preco'])).replace('__DNF__',str(PRECO_NF_DIESEL)).replace('__DQ__',str(DIESEL['q'])))
    painel()
    corpo=(kpis([('Divergências abertas',H('k_div'),H('k_div_s')),('Em quarentena',H('k_quar'),H('k_quar_s')),('A receber',H('k_pend'),H('k_pend_s')),('Pedidos com saldo aberto',H('k_ab'),H('k_ab_s'))])
           + bloco('Conferência de pedido, documento e material','Confira cada entrega contra o pedido e a NF; clique na linha pendente para registrar o conferido.',
                   g,
                   acao=mini('ler','Ler documento/QR','Lê a chave da NF e localiza o pedido (simulado)','doc')+mini('open_seg','Segregar lote','Retém parte do apto de um lote','alert')
                        +mini('open_div','Resolver diferença','Decide a divergência de preço da NF 8812','cash')))
    HEIGHTS37[fname]=880
    prim=(f'<sc-if value="{H("pend4533")}" hint-placeholder-val="{T()}">{primb("conf4533","Conferir NF 4533","truck")}</sc-if>'
          f'<sc-if value="{H("done4533")}" hint-placeholder-val="{F()}">{prima("GE-04.dc.html","Encaminhar títulos")}</sc-if>')
    shell37('SU-06','Recebimentos e divergências',corpo,fname=fname,
      subtitle='Conferência de pedido, documento e material; parcial mantém o saldo aberto e documento duplicado não cria segunda entrada.',
      status=(MARK,'gray'),primary_html=prim,
      footer='DEMO-02: PC-088 100 t → 60 recebidas (50 aptas + 10 em quarentena) e 40 a entregar; liberar qualidade soma as 10 t uma única vez (SU-06 · FO-18). '
             'Aceite físico não aprova o título: o título segue para Contas a pagar à parte. O retido em quarentena alimenta só a cobertura condicionada em Necessidades até o laudo, e soma uma única vez.')
    dyn_status(fname)

# ================= SU-07 · Requisições e entregas =================
PESSOAS=['Paula','Marcos','Carlos','João']
def _reqs():
    """requisições de dados2 + locais (REQ-037/039/040) com o mesmo vocabulário do processo Estoque."""
    out=[dict(id='REQ-031',os='OS-0417',tipo='Adubação de cobertura · P1',item=R31['item'],lote='M26-07',un='sc',sol=R31['solicitado'],ent=R31['entregue'],cons=R31['consumido'],
              cust=R31['custodia'],resp='Paula',local='campo P1',data='2026-09-18',st='sobras',ro=True),
         dict(id='REQ-035',os='OS-0421',tipo='Fungicida 1ª aplicação · T1+T2',item=R35['item'],lote='F26-02',un='L',sol=R35['solicitado'],ent=R35['entregue'],cons=R35['consumido'],
              cust=R35['custodia'],resp='Marcos',local='campo T1+T2',data='2026-09-20',st='uso',ro=True),
         dict(id='REQ-036',os='OS-0420',tipo='Plantio soja 58 W · T4',item=R36['item'],lote='S58-0801',un='kg',sol=R36['solicitado'],ent=R36['entregue'],cons=R36['consumido'],
              cust=R36['custodia'],resp='Carlos',local='campo T4',data='2026-09-24',st='imp',ro=False),
         dict(id='REQ-037',os='OS-0420',tipo='Plantio soja 58 W · T4',item=R37['item'],lote=R37['lote'],un='kg',sol=R37['solicitado'],ent=R37['entregue'],cons=R37['consumido'],
              cust=R37['custodia'],resp='Carlos',local='campo T4',data='2026-09-26',st='devp',ro=True),
         dict(id='REQ-038',os='OS-0418',tipo='Fertirrigação · P1',item=R38['item'],lote='—',un='kg',sol=R38['solicitado'],ent=0,cons=0,cust=0,resp='João',local='casa de bombas P1',data='2026-09-29',st='agr',ro=False),
         dict(id='REQ-039',os='OS-0424',tipo='Fungicida · T1-B',item=R39['item'],lote=R39['lote'],un='L',sol=R39['solicitado'],ent=0,cons=0,cust=0,resp='Marcos',local='campo T1-B',data='2026-09-24',st='sep',ro=False),
         dict(id='REQ-040',os='OS-0425',tipo='Adubação 1ª parcela · café C1',item=R40['item'],lote=R40['lote'],un='kg',sol=R40['solicitado'],ent=0,cons=0,cust=0,resp='Paula',local='café C1',data='2026-10-15',st='parc',ro=False)]
    return out
def su07():
    fname='SU-07.dc.html'; E._reset_screen(fname)
    kcl_saldo=R37['resid_v3']-R37['custodia']
    memo={
     'REQ-031':[dict(t=f"Entregue {R31['entregue']} sc · consumo apontado {R31['consumido']} sc · devolução recebida {R31['dev_recebida']} sc = {R31['custodia']} sc com Paula"),dict(t='Declarar a devolução não transfere custódia; só o recebimento conferido'),dict(t='Abrir a requisição',h='SU-07det.dc.html')],
     'REQ-035':[dict(t=f"Entregue {nq(R35['entregue'])} de {nq(R35['solicitado'])} L (parcela executável) · consumo {nq(R35['consumido'])} L em 190 ha · {nq(R35['custodia'])} L com Marcos"),dict(t='O consumo apontado no campo não gera segunda saída no depósito'),dict(t='Ver a O.S.',h='OS.dc.html')],
     'REQ-036':[dict(t=f"Plano Soja alta tecnologia: {DOSE_SEM} kg/ha × 100 ha = {nf(R36['solicitado'])} kg"),dict(t=f"Entregue e plantado {nf(R36['entregue'])} kg em {REAL_HA} ha ({DOSE_SEM} kg/ha)"),
                dict(t=f"Necessidade residual {DOSE_SEM} kg/ha × {SALDO_HA} ha = {nf(SEM_RESID)} kg · fica reservada no S58-0801"),dict(t='O.S. impedida pela OM-0233 (Trator T1 · pressão hidráulica)',h='OS.dc.html')],
     'REQ-037':[dict(t=f"v2 (REC-014): {DOSE_KCL} kg/ha × 100 ha = {nf(R37['solicitado'])} kg · entregue {nf(R37['entregue'])} kg do lote {R37['lote']}"),
                dict(t=f"Consumo {nf(R37['consumido'])} kg em {REAL_HA} ha ({DOSE_KCL} kg/ha) · {nf(R37['custodia'])} kg em custódia de Carlos"),
                dict(t=f"v3: −12 % só no saldo de {SALDO_HA} ha = {nf(R37['resid_v3'])} kg; os {REAL_HA} ha realizados ficam preservados"),
                dict(t=f"A entregar quando a O.S. voltar: {nf(R37['resid_v3'])} − {nf(R37['custodia'])} em custódia = {nf(kcl_saldo)} kg"),
                dict(t=f"O.S. impedida: devolver os {nf(R37['custodia'])} kg ao Galpão 2 até 26/09 (Carlos)"),dict(t='Receber a devolução no Estoque',h='EST.dc.html')],
     'REQ-038':[dict(t='Fertirrigação reclassificada: a v2 aguarda o agrônomo · sem aprovação nada é separado'),dict(t='Depois da aprovação: liberação → entrega à custódia com conferência de carga → consumo e devolução → conciliação, sem encerramento automático'),dict(t='Ver a aprovação',h='OS.dc.html')],
     'REQ-039':[dict(t=f"Reserva confirmada de {nq(R39['reservado'])} L no F26-02 (recibo RS-7741)"),dict(t='Separar pelo FEFO e entregar à custódia de Marcos'),dict(t='Ver o lote',h='SU-03det.dc.html')],
     'REQ-040':[dict(t='Plano Café arábica: 300 kg/ha × 38 ha = 11.400 kg (1ª parcela, 15/10)'),dict(t=f"Lote N26-03 com {nf(R40['disp'])} kg · entrega parcial libera só {nf(R40['disp']/300,1)} de 38 ha"),
                dict(t=f"Pendência {nf(R40['solicitado']-R40['disp'])} kg coberta pela SOL-2026-07",h='CMP.dc.html')]}
    rows=[R(x['id'],dict(req=x['id'],os=x['os'],tipo=x['tipo'],item=x['item'],lote=x['lote'],un=x['un'],sol=x['sol'],ent=x['ent'],cons=x['cons'],cust=x['cust'],resp=x['resp'],local=x['local'],data=x['data'],st=x['st']),
            {},ro=x['ro'],o=memo[x['id']]) for x in _reqs()]
    g=grid([dict(k='req',l='Requisição · O.S.',w=230),dict(k='item',l='Item · lote',w=190),dict(k='sol',l='Solicitado',t='num',a='r'),dict(k='ent',l='Entregue',t='num',a='r'),
            dict(k='cons',l='Consumido',t='num',a='r'),dict(k='cust',l='Em custódia',t='num',a='r'),dict(k='est',l='Estado · próxima ação',w=210)],
        rows,gid='g_req',total=False,
        edit=dict(m='form',title='Requisição',sub='Ajuste recebedor, local e data da entrega. Quantidade vem da versão aprovada da O.S.: excesso ou substituição exigem revisão.',
          fields=[fs('resp','Recebedor','sel',opts=PESSOAS,req=True,help='Quem recebe assume a custódia até consumir ou devolver.'),fs('local','Local de entrega','txt',req=True),fs('data','Entrega prevista','date',req=True)]))
    pn={'sol':dict(title='Solicitar requisição',sub='Nasce da versão aprovada da O.S.; só o saldo autorizado por produto pode ser pedido.',ok='Criar requisição',
        fields=[fs('os','O.S. · item autorizado','sel',opts=['OS-0421 · Adjuvante espalhante · v2 autoriza 87,5 L'],req=True,**{'def':'OS-0421 · Adjuvante espalhante · v2 autoriza 87,5 L'}),
                fs('q','Quantidade','num',req=True,min=0.1,max=87.5,u='L',**{'def':'87,5'}),fs('local','Local de entrega','txt',req=True,**{'def':'campo T1+T2'}),
                fs('resp','Recebedor','sel',opts=PESSOAS,req=True,**{'def':'Marcos'})])}
    code=r'''
const RESID36=__R36__, KCL_SALDO=__KS__;
function qq(n,un){ return nf(n,(n%1)?1:0)+' '+un; }
const ST={sobras:['Sobras a receber','red'],uso:['Em uso','green'],imp:['Impedida · OM-0233','red'],devp:['Devolver até 26/09','yellow'],
  agr:['Aguarda agrônomo','gray'],sep:['A separar','yellow'],separada:['Separada','yellow'],entregue:['Entregue','green'],parc:['A separar · parcial','yellow'],
  parcial:['Parcial · pendência na SOL','yellow'],sol:['Solicitada','yellow']};
CHECK.sol=(self)=>(self.state.sol41?{os:'A REQ-041 já foi criada para este item · nada criado de novo.'}:null);
RUN.sol=(self,d)=>{ const q=g2num(d.q); setRows(self,'g_req',rows=>{ rows.push({id:'REQ-041',v:{req:'REQ-041',os:'OS-0421',tipo:'Fungicida 1ª aplicação · T1+T2',item:'Adjuvante espalhante',lote:'FEFO',un:'L',sol:q,ent:0,cons:0,cust:0,resp:d.resp,local:d.local,data:'2026-09-24',st:'sol'},s:{},p:{},
    o:[{t:'Criada a partir da v2 aprovada da OS-0421 · autoriza 87,5 L (0,25 L/ha × 350 ha)'}]}); });
  self.setState({sol41:true}); return 'REQ-041 criada: '+qq(q,'L')+' de Adjuvante espalhante para a OS-0421 · entra na fila de separação'; };
function PREVALS(self,v){ RW(self,'g_req').forEach(r=>{ const V=r.v, u=V.un;
  r.p.req=[B(V.req),M(V.os+' · '+V.tipo)]; r.s.req=V.req+' '+V.os+' '+V.tipo;
  r.p.item=[T(V.item),M(V.lote)]; r.s.item=V.item+' '+V.lote;
  r.p.sol=[T(qq(V.sol,u))].concat(r.id==='REQ-037'?[BRK,M('v3: '+nf(__V3T__)+' kg')]:[]);
  ['ent','cons'].forEach(k=>{ r.p[k]=[V[k]?T(qq(V[k],u)):M('—')]; });
  r.p.cust=V.cust?[B(qq(V.cust,u)),M('com '+V.resp)]:[M('—')];
  const s=ST[V.st]||[V.st,'gray']; r.s.est=s[0];
  const A=(t,fn)=>({k:'act',t:t,fn:fn});
  const nx= V.st==='sobras'?[{k:'cta',t:'Receber devolução',h:'SU-07det.dc.html'}]
    : V.st==='uso'?[{k:'link',t:'Ver consumo',h:'OS.dc.html'}]
    : V.st==='imp'?[A('Confirmar entrega','ent36:REQ-036')]
    : V.st==='devp'?[{k:'link',t:'Receber no Estoque',h:'EST.dc.html'}]
    : V.st==='agr'?[A('Separar FEFO','sep38:REQ-038')]
    : (V.st==='sep'||V.st==='sol')?[A('Separar FEFO','sep:'+r.id)]
    : V.st==='separada'?[A('Confirmar entrega','ent:'+r.id)]
    : V.st==='parc'?[A('Entregar '+nf(__N26__)+' kg','ent40:REQ-040')]
    : []; r.p.est=[chipc(s[0],s[1])].concat(nx.length?[BRK].concat(nx):[]); }); }
function EXTRAVALS(self,v){ pnVals(self,v); const rs=RW(self,'g_req');
  const cu=rs.filter(x=>x.v.cust>0), se=rs.filter(x=>['sep','sol','separada','parc'].indexOf(x.v.st)>=0), im=rs.filter(x=>x.v.st==='imp'||x.v.st==='agr');
  v.k_cu=String(cu.length)+(cu.length===1?' ordem':' ordens'); v.k_cu_s=cu.map(x=>x.v.os).filter((a,i,l)=>l.indexOf(a)===i).join(' · ');
  v.k_se=String(se.length); v.k_se_s=se.map(x=>x.id).join(' · ')||'fila vazia';
  v.k_im=String(im.length); v.k_im_s='OM-0233 · aprovação do agrônomo';
  v.ent36=()=>toast(self,'Bloqueado · a OS-0420 está impedida pela OM-0233 (Trator T1). Nada entregue: os '+nf(RESID36)+' kg do saldo de 70 ha seguem reservados no S58-0801 até a O.S. voltar a executar. Responsável: Carlos.');
  v.sep38=()=>toast(self,'Bloqueado · a OS-0418 aguarda o agrônomo aprovar a v2. Nada separado: a entrega só vale na versão aprovada. Responsável: João.');
  v.sep=(id)=>{ const r=RF(self,'g_req',id); if(!r||(r.v.st!=='sep'&&r.v.st!=='sol')) return toast(self,id+' já separada · nada separado de novo');
    setRows(self,'g_req',rows=>{ const x=rows.find(y=>y.id===id); x.v.st='separada'; if(x.v.lote==='FEFO') x.v.lote='A26-05 (FEFO)'; });
    toast(self,id+' separada pelo FEFO: '+qq(r.v.sol,r.v.un)+' de '+r.v.item+' · falta confirmar a entrega a '+r.v.resp); };
  v.ent=(id)=>{ const r=RF(self,'g_req',id); if(!r||r.v.st!=='separada') return toast(self,id+' já entregue · nada entregue de novo');
    setRows(self,'g_req',rows=>{ const x=rows.find(y=>y.id===id); x.v.ent=x.v.sol; x.v.cust=x.v.sol; x.v.st='entregue'; x.ro=true; });
    toast(self,'Entregue '+qq(r.v.sol,r.v.un)+' à '+r.v.os+' · custódia de '+r.v.resp+' 0 → '+qq(r.v.sol,r.v.un)+' · sai do disponível do depósito'); };
  v.ent40=()=>{ const r=RF(self,'g_req','REQ-040'); if(r.v.st!=='parc') return toast(self,'Entrega parcial da REQ-040 já feita · nada entregue de novo');
    setRows(self,'g_req',rows=>{ const x=rows.find(y=>y.id==='REQ-040'); x.v.ent=__N26__; x.v.cust=__N26__; x.v.st='parcial'; x.ro=true; });
    toast(self,'Entrega parcial: '+nf(__N26__)+' kg do N26-03 à custódia de Paula · libera '+nf(__N26__/300,1)+' de 38 ha · '+nf(__PEN__)+' kg pendentes cobertos pela SOL-2026-07'); }; }'''
    js(pn,code.replace('__R36__',str(SEM_RESID)).replace('__KS__',str(kcl_saldo)).replace('__V3T__',str(R37['consumido']+R37['resid_v3']))
            .replace('__N26__',str(R40['disp'])).replace('__PEN__',str(R40['solicitado']-R40['disp'])))
    painel()
    corpo=(kpis([('Em custódia',H('k_cu'),H('k_cu_s')),('Fila de separação',H('k_se'),H('k_se_s')),('Impedidas',H('k_im'),H('k_im_s')),('Sobras a receber',f"{R31['custodia']} sc",'REQ-031 · OS-0417 em conferência')])
           + bloco('Fila de separação por ordem','Separe e entregue só o saldo autorizado da versão aprovada; clique na linha para ajustar recebedor, local e data.',
                   g,
                   acao=mini('open_sol','Solicitar','Cria requisição a partir da versão aprovada da O.S.','doc')+alink('MB-05.dc.html','Ler QR no app','Confere a entrega pelo app de campo','box')))
    HEIGHTS37[fname]=1080
    shell37('SU-07','Requisições e entregas',corpo,fname=fname,
      subtitle='Fila de separação por ordem com solicitado, entregue, consumido e custódia; o detalhe concilia a devolução.',
      status=('2 impedidas · 10 sc de sobras a receber','red'),primary_html=prima('SU-07det.dc.html','Receber devolução da REQ-031'),
      footer='Entrega só da versão aprovada pelo agrônomo; excesso e substituição exigem revisão (SU-07 · FO-09 · cap. 42). '
             'Material entregue sai do disponível e passa à custódia da ordem; o consumo apontado no campo não repete a saída. Entrega parcial libera só a parcela executável.')

# ---- SU-07det · REQ-031 · OS-0417 · MAP 11-52 (DEMO-03) ----
def su07det():
    fname='SU-07det.dc.html'; E._reset_screen(fname); PARENT37[fname]='SU-07.dc.html'
    E0,C0,D0,V0,K0=R31['entregue'],R31['consumido'],R31['dev_declarada'],R31['dev_recebida'],R31['custodia']
    rows=[R('ent',dict(m='Entregue à ordem',q=E0),dict(sit=[txt('lote M26-07 · separado FEFO em 18/09')]),o=[dict(t='Saída MV-8760 · Galpão 2 → OS-0417 · custódia de Paula',h='SU-08.dc.html')]),
          R('cons',dict(m='Consumo apontado',q=C0),dict(sit=[txt('apontamentos do campo · 95 ha a 36,8 kg/ha')]),o=[dict(t='Apontamentos da OS-0417 · dose conferida pelo agrônomo',h='OS.dc.html')]),
          R('decl',dict(m='Devolução declarada',q=D0),dict(sit=[mut('declaração não transfere custódia')]),o=[dict(t='Declarada por Paula no término físico')]),
          R('rec',dict(m='Devolução recebida e conferida',q=V0),dict(),o=[dict(t='Recebida por Rui (almoxarife) · lote M26-05 (quarentena de sobras)',h='SU-08.dc.html')]),
          R('cust',dict(m='Saldo em custódia',q=K0),dict(),o=[dict(t=f'Entregue {E0} − consumo {C0} − devolução recebida {V0} (+ recebido agora)')])]
    g=grid([dict(k='m',l='Medida',w=300),dict(k='q',l='Quantidade',t='num',a='r',u='sc'),dict(k='sit',l='Situação',w=420)],rows,gid='g_bal',search=False,total=False,
        edit=dict(m='origin',title='Balanço',fields=[fs('m','Medida',ro=True)]))
    pn={'rec':dict(title='Receber devolução · REQ-031',sub='Registre a quantidade medida pelo almoxarife, não a declarada. Embalagem aberta vai para quarentena.',ok='Confirmar recebimento',
          fields=[fs('q','Quantidade medida','num',req=True,min=0.5,u='sc',maxfn='cust',**{'def':str(K0)}),
                  fs('cond','Condição','sel',opts=['Lacrada · volta apta ao M26-07','Embalagem aberta · quarentena no M26-05','Imprópria · bloqueio para destinação'],req=True,**{'def':'Embalagem aberta · quarentena no M26-05'}),
                  fs('resp','Recebedor','sel',opts=['Rui (almoxarife)','Ana (gestora)'],req=True,**{'def':'Rui (almoxarife)'},help='Quem estava com a custódia (Paula) não confirma o próprio recebimento.')]),
        'dst':dict(title='Destinar saldo em custódia',sub='Perda ou consumo adicional passam por aprovação; a custódia só baixa depois da decisão.',ok='Submeter destinação',
          fields=[fs('q','Quantidade','num',req=True,min=0.5,u='sc',maxfn='cust'),
                  fs('dest','Destinação','sel',opts=['Perda em campo · alçada do gestor','Consumo adicional · revisão da versão','Transferir a outra O.S.'],req=True,**{'def':'Perda em campo · alçada do gestor'}),
                  fs('ev','Evidência','txt',req=True,help='Ex.: foto da sacaria rasgada.'),fs('apr','Aprovador','sel',opts=['Ana (gestora)'],req=True,**{'def':'Ana (gestora)'})])}
    code=r'''
const E0=__E0__, C0=__C0__, V0=__V0__, K0=__K0__;
function cust(self){ return Math.max(0,K0-(self.state.rcv||0)); }
MAXFN.cust=(self)=>cust(self)-((self.state.dst&&self.state.pn==='rec')?self.state.dst.q:0);
CHECK.dst=(self)=>(self.state.dst?{q:'Destinação já submetida ('+nf(self.state.dst.q)+' sc · aguarda '+self.state.dst.apr+') · nada submetido de novo.'}:null);
RUN.rec=(self,d)=>{ const q=g2num(d.q); const a=cust(self); const b=Math.max(0,a-q); const tl=(self.state.tlx||[]).slice();
  tl.push('23/09 · '+nf(q,q%1?1:0)+' sc recebidas por '+d.resp+' · '+d.cond+' · custódia '+nf(a)+' → '+nf(b)+' sc');
  self.setState({rcv:(self.state.rcv||0)+q,cond:d.cond,tlx:tl});
  return 'Devolução recebida: '+nf(q,q%1?1:0)+' sc · '+d.cond+' · custódia de Paula '+nf(a)+' → '+nf(b)+' sc'+(b<=0?' · OS-0417 pronta para conciliar':''); };
RUN.dst=(self,d)=>{ const q=g2num(d.q); const tl=(self.state.tlx||[]).slice(); tl.push('23/09 · destinação de '+nf(q)+' sc submetida ('+d.dest+') · aguarda '+d.apr);
  self.setState({dst:{q:q,dest:d.dest,apr:d.apr},tlx:tl}); return 'Destinação de '+nf(q)+' sc submetida · aguarda '+d.apr+' · a custódia segue até a aprovação'; };
function PREVALS(self,v){ const rcv=self.state.rcv||0, k=cust(self), conc=!!self.state.conc; const rs=RW(self,'g_bal');
  const Rr=rs.find(r=>r.id==='rec'), Rc=rs.find(r=>r.id==='cust');
  Rr.v.q=V0+rcv; Rr.p.q=[T(nf(V0+rcv,rcv%1?1:0)+' sc')].concat(rcv?[M('+'+nf(rcv,rcv%1?1:0)+' agora')]:[]);
  Rr.p.sit=rcv?[chipc('Recebida · '+(String(self.state.cond||'').split(' · ')[1]||''),'green')]:[T('voltou ao M26-05 · quarentena')];
  Rc.v.q=k; Rc.p.q=[B(nf(k,k%1?1:0)+' sc')];
  Rc.p.sit=conc?[chipc('Conciliada · recibo CC-0417','green')]:(k>0?[chipc('Impede encerrar a ordem · prazo 24/09','red')].concat(self.state.dst?[M('destinação aguarda '+self.state.dst.apr)]:[]):[chipc('Zerada · pronta para conciliar','yellow')]); }
function EXTRAVALS(self,v){ pnVals(self,v); const k=cust(self), conc=!!self.state.conc;
  if(conc) hstatus(v,'Custódia conciliada · OS-0417 pronta para encerrar','green'); else if(k>0) hstatus(v,'Custódia aberta · '+nf(k,k%1?1:0)+' sc','red'); else hstatus(v,'Custódia zerada · pronta para conciliar','yellow');
  v.open=k>0&&!conc; v.zero=k<=0&&!conc; v.conc=conc;
  v.ct_falta=conc?'Encerrar a O.S.':(k>0?'Receber '+nf(k,k%1?1:0)+' sc ou destinar':'Conciliar a custódia'); v.ct_prox=conc?'Encerrar a OS-0417':(k>0?'Receber devolução':'Conciliar custódia');
  v.tl=[{t:'18/09 · 100 sc entregues à custódia de Paula (MV-8760, lote M26-07)'},{t:'22/09 · término físico · consumo apontado 70 sc em 95 ha'},{t:'22/09 · devolução declarada 20 sc · 23/09 09:41 20 sc recebidas e conferidas por Rui'}]
    .concat((self.state.tlx||[]).map(t=>({t:t}))).concat(conc?[{t:'23/09 · custódia conciliada: entregue 100 = consumo 70 + devolvido '+nf(E0-C0)+' (recibo CC-0417)'}]:[]);
  v.do_conc=()=>{ const s=self.state; if(s.conc) return toast(self,'Custódia já conciliada em 23/09 · recibo CC-0417, nada muda');
    const kk=cust(self); if(kk>0) return toast(self,'Conciliação recusada · '+nf(kk,kk%1?1:0)+' sc seguem sob custódia de Paula (prazo 24/09). Receba a devolução ou destine o saldo.');
    self.setState({conc:true,g2toast:'Custódia conciliada · OS-0417 pronta para encerrar (recibo CC-0417): entregue 100 = consumo 70 + devolvido '+nf(E0-C0)+' sc'}); };
  v.try_dst=()=>{ if(cust(self)<=0) return toast(self,'Nada em custódia · nada a destinar'); pnOpen(self,'dst'); };
  v.try_rec=()=>{ if(cust(self)<=0) return toast(self,'Custódia já zerada · nada a receber'); pnOpen(self,'rec'); }; }'''
    for k,val in (('__E0__',E0),('__C0__',C0),('__V0__',V0),('__K0__',K0)): code=code.replace(k,str(val))
    js(pn,code)
    painel()
    tl=f'<div style="display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: {MUTED}; line-height: 1.5;"><sc-for list="{H("tl")}" as="x" hint-placeholder-count="3"><div>{H("x.t")}</div></sc-for></div>'
    acts=(f'<sc-if value="{H("open")}" hint-placeholder-val="{T()}">'+mini('try_dst','Destinar saldo','Submete perda, consumo adicional ou transferência para aprovação','alert')
          +mini('do_conc','Conciliar custódia','Tenta conciliar; recusa enquanto houver saldo em custódia','check')+'</sc-if>')
    corpo=(continuity('Término físico · consumo 70 sc','OS-0417 em conferência',H('ct_falta'),H('ct_prox'))
           + bloco('Balanço da requisição','Confira entregue, consumido, devolvido e o saldo em custódia; clique na linha para ver a origem.',g
                   ,acao=acts)
           + bloco('Linha do tempo','Acompanhe cada entrega, apontamento e devolução desta requisição.',tl))
    prim=(f'<sc-if value="{H("open")}" hint-placeholder-val="{T()}">{primb("try_rec","Receber devolução","truck")}</sc-if>'
          f'<sc-if value="{H("zero")}" hint-placeholder-val="{F()}">{primb("do_conc","Conciliar custódia","check")}</sc-if>'
          f'<sc-if value="{H("conc")}" hint-placeholder-val="{F()}">{prima("OS.dc.html","Encerrar a OS-0417")}</sc-if>')
    HEIGHTS37[fname]=880
    shell37('SU-07',f"REQ-031 · OS-0417 · {R31['item']}",corpo,fname=fname,crumbs_extra=['REQ-031'],
      subtitle=f'Devolução parcial: {E0} entregues − {C0} consumidas − {V0} recebidas = {K0} sc sob custódia; o encerramento espera a conciliação.',
      status=(MARK,'gray'),primary_html=prim,
      footer='DEMO-03 · item recebido em quarentena não vira apto; calda pronta não volta como produto puro (ESTOS-04/05/06 · OSFASE-05). '
             'É o mesmo balanço que a conferência da ordem usa. Declarar a devolução não aumenta o utilizável do depósito; só o recebimento conferido transfere a custódia.')
    dyn_status(fname)

# ================= SU-08 · Transferências e movimentos =================
def su08():
    fname='SU-08.dc.html'; E._reset_screen(fname)
    M=[('tr452','23/09 10:12','TR-0452','Transferência','Galpão Boa Vista → Almox. defensivos','Glifosato 480 · G26-15',200,'L','própria','reforço da dessecação','transito'),
       ('dv031','23/09 09:41','Devolução REQ-031','Devolução recebida','Custódia OS-0417 → Galpão 2','MAP 11-52 · M26-05',20,'sc','própria','sobras de campo · quarentena','conf'),
       ('mv8821','22/09 16:20','MV-8821','Saída p/ custódia de ordem','Almox. defensivos → OS-0421','Fungicida A · F26-02',160,'L','própria','REQ-035','conf'),
       ('mv8791','22/09 14:05','MV-8791','Saída p/ custódia de ordem','Câmara fria → OS-0420','Semente de soja 58 W · S58-0801',1560,'kg','própria','REQ-036 · lote correto','conf'),
       ('es071','22/09 14:02','ES-0071','Estorno · vínculo MV-8790','OS-0420 → Câmara fria','Semente de soja 58 W · S58-0726',1560,'kg','própria','lote digitado errado','estorno'),
       ('mv8790','22/09 11:37','MV-8790','Saída p/ custódia de ordem','Câmara fria → OS-0420','Semente de soja 58 W · S58-0726',1560,'kg','própria','REQ-036','estornado'),
       ('mv8788','21/09 17:10','MV-8788','Saída p/ custódia de ordem','Galpão 2 → OS-0420','KCl 60% · K26-07',R37['entregue'],'kg','própria','REQ-037','conf'),
       ('nf5520','21/09 15:04','NF 5520','Entre empresas','Faz. Santa Rita → Boa Vista Ltda','Diesel S10 · tanque',2000,'L','muda de proprietário','apoio de frota','conf'),
       ('pe012','21/09 09:12','PE-012','Perda em alçada','Galpão 2 → perda','MAP 11-52 · M26-07',50,'kg','própria','quebra de embalagem','gestor'),
       ('nf4501','19/09 16:40','NF 4501','Entrada por compra','Fertisul → Galpão 2','KCl 60% · K26-11',60000,'kg','própria','PC-088 · 10 t em quarentena','conf')]
    ORG={'tr452':[dict(t='Saiu do Galpão Boa Vista em 23/09 10:12 · em trânsito; o saldo só muda de local ao confirmar no destino')],
         'dv031':[dict(t='Recebida por Rui · embalagem aberta → quarentena'),dict(t='Abrir a requisição',h='SU-07det.dc.html')],
         'mv8821':[dict(t='Entrega da REQ-035 à custódia de Marcos'),dict(t='Ver a requisição',h='SU-07.dc.html')],
         'mv8791':[dict(t='Lançamento correto depois do estorno ES-0071')],
         'es071':[dict(t='Estorna o MV-8790 (lote S58-0726 digitado errado); o original segue no extrato')],
         'mv8790':[dict(t='Estornado pelo ES-0071 · a operação original não foi apagada')],
         'mv8788':[dict(t='Entrega da REQ-037 à custódia de Carlos'),dict(t='Ver a requisição',h='SU-07.dc.html')],
         'nf5520':[dict(t='Transferência entre empresas com NF 5520 · muda o proprietário do saldo')],
         'pe012':[dict(t='R$ 195 (50 kg × R$ 3,90/kg) · alçada do gestor de suprimentos (até R$ 50 mil)')],
         'nf4501':[dict(t='Entrada do PC-088 · 50.000 kg aptos + 10.000 kg em quarentena'),dict(t='Ver o recebimento',h='SU-06.dc.html')]}
    rows=[R(i,dict(dh=dh,doc=doc,mov=mv,od=od,it=it,q=q,un=un,prop=pr,mot=mo,st=st),{},o=ORG[i]) for i,dh,doc,mv,od,it,q,un,pr,mo,st in M]
    g=grid([dict(k='doc',l='Documento · data',w=170),dict(k='mov',l='Movimento · motivo',w=200),dict(k='od',l='Origem → destino',w=200),dict(k='it',l='Item · lote',w=190),
            dict(k='q',l='Quantidade',t='num',a='r'),dict(k='est',l='Estado',w=200)],rows,gid='g_mov',total=False,
        edit=dict(m='ro',title='Movimento',fields=[fs('doc','Documento',ro=True),fs('mov','Movimento',ro=True),fs('od','Origem → destino',ro=True),fs('it','Item · lote',ro=True),fs('mot','Motivo',ro=True)]))
    LOCS=['Galpão 1','Galpão 2','Câmara fria','Almox. defensivos','Tanque Sede','Galpão Boa Vista']
    ESTORNAVEIS=['MV-8788 · KCl 60% 4.800 kg → OS-0420','MV-8821 · Fungicida A 160 L → OS-0421','NF 5520 · Diesel S10 2.000 L → Boa Vista Ltda']
    pn={'trf':dict(title='Transferir entre locais',sub='A transferência fica em trânsito até a confirmação no destino.',ok='Iniciar transferência',
          fields=[fs('it','Item · lote','sel',opts=['KCl 60% · K26-11','MAP 11-52 · M26-07','Glifosato 480 · G26-14','Semente de soja 58 W · S58-0801'],req=True,**{'def':'MAP 11-52 · M26-07'}),
                  fs('q','Quantidade','num',req=True,min=1,u='kg ou L'),fs('o','Origem','sel',opts=LOCS,req=True,**{'def':'Galpão 2'}),fs('d','Destino','sel',opts=LOCS,req=True,**{'def':'Galpão 1'}),
                  fs('mot','Motivo','txt',req=True,help='Ex.: abastecer a frente de plantio.')]),
        'per':dict(title='Registrar perda em alçada',sub='A perda entra no extrato só depois da aprovação na alçada; o saldo não muda antes disso.',ok='Submeter perda',
          fields=[fs('it','Item · lote','sel',opts=['MAP 11-52 · M26-07','KCl 60% · K26-11','Glifosato 480 · G26-14'],req=True,**{'def':'MAP 11-52 · M26-07'}),
                  fs('q','Quantidade','num',req=True,min=0.1,u='kg ou L'),fs('causa','Causa','txt',req=True),fs('ev','Evidência','txt',req=True,help='Ex.: foto, laudo, boletim.'),
                  fs('apr','Aprovador','sel',opts=['Ana (gestora)','Gerente da fazenda'],req=True,**{'def':'Ana (gestora)'})]),
        'est':dict(title='Estornar com vínculo',sub='O estorno cria um movimento novo que referencia o original; nada é apagado.',ok='Estornar com vínculo',
          fields=[fs('orig','Movimento original','sel',opts=ESTORNAVEIS,req=True,**{'def':ESTORNAVEIS[0]}),fs('mot','Motivo','txt',req=True,help='Ex.: quantidade digitada errada.')])}
    code=r'''
const ST={transito:['Em trânsito','yellow'],conf:['Confirmado','green'],estorno:['Estorno lançado','gray'],estornado:['Estornado · ver ES-0071','gray'],gestor:['Aguarda gestor','yellow'],aprov:['Aprovada · lançada','green']};
function qq(n,un){ return nf(n,(n%1)?1:0)+' '+un; }
function un(it){ return /Glifosato|Fungicida|Diesel/.test(it)?'L':'kg'; }
CHECK.trf=(self,d)=>(d.o===d.d?{d:'O destino precisa ser diferente da origem.'}:null);
CHECK.est=(self,d)=>{ const doc=d.orig.split(' · ')[0]; const r=RW(self,'g_mov').find(x=>x.v.doc===doc); return (r&&r.v.st==='estornado')?{orig:doc+' já foi estornado · nada estornado de novo.'}:null; };
function add(self,row){ setRows(self,'g_mov',rows=>{ rows.unshift(row); }); }
function nx(self,k,base){ const n=(self.state[k]||base)+1; self.setState({[k]:n}); return n; }
RUN.trf=(self,d)=>{ const n=nx(self,'ntr',452); const id='TR-0'+n; const q=g2num(d.q);
  add(self,{id:id,v:{dh:'23/09 agora',doc:id,mov:'Transferência',od:d.o+' → '+d.d,it:d.it,q:q,un:un(d.it),prop:'própria',mot:d.mot,st:'transito'},s:{},p:{},o:[{t:'Em trânsito; o saldo só muda de local ao confirmar no destino'}]});
  return id+' iniciada: '+qq(q,un(d.it))+' de '+d.it+' em trânsito '+d.o+' → '+d.d+' · confirme no destino'; };
RUN.per=(self,d)=>{ const n=nx(self,'npe',12); const id='PE-0'+n; const q=g2num(d.q);
  add(self,{id:id,v:{dh:'23/09 agora',doc:id,mov:'Perda em alçada',od:d.it.split(' · ')[0]+' → perda',it:d.it,q:q,un:un(d.it),prop:'própria',mot:d.causa,st:'gestor'},s:{},p:{},o:[{t:'Evidência: '+d.ev},{t:'Aprovador: '+d.apr}]});
  return id+' submetida a '+d.apr+' · o saldo só baixa depois da aprovação'; };
RUN.est=(self,d)=>{ const doc=d.orig.split(' · ')[0]; const n=nx(self,'nes',71); const id='ES-00'+n; let src=null;
  setRows(self,'g_mov',rows=>{ src=rows.find(x=>x.v.doc===doc); src.v.st='estornado'; src.v.est_ref=id;
    const p=src.v.od.split(' → '); rows.unshift({id:id,v:{dh:'23/09 agora',doc:id,mov:'Estorno · vínculo '+doc,od:p[1]+' → '+p[0],it:src.v.it,q:src.v.q,un:src.v.un,prop:src.v.prop,mot:d.mot,st:'estorno'},s:{},p:{},o:[{t:'Estorna o '+doc+'; o original segue no extrato'}]}); });
  return id+' lançado com vínculo ao '+doc+' · o original fica no extrato como estornado'; };
function PREVALS(self,v){ RW(self,'g_mov').forEach(r=>{ const V=r.v;
  r.p.doc=[B(V.doc),BRK,M(V.dh)]; r.s.doc=V.doc+' '+V.dh; r.p.q=[T(qq(V.q,V.un))];
  r.p.mov=[T(V.mov),BRK,M(V.mot)]; r.s.mov=V.mov+' '+V.mot; r.p.od=[T(V.od)].concat(V.prop!=='própria'?[BRK,M(V.prop)]:[]);
  const s=ST[V.st]||[V.st,'gray']; const t=V.st==='estornado'?'Estornado · ver '+(V.est_ref||'ES-0071'):s[0];
  r.p.est=[chipc(t,s[1])].concat(V.st==='transito'?[BRK,{k:'act',t:'Confirmar recebimento',fn:'conf:'+r.id}]:(V.st==='gestor'?[BRK,{k:'act',t:'Aprovar perda',fn:'apr:'+r.id}]:[])); r.s.est=t; }); }
function EXTRAVALS(self,v){ pnVals(self,v); const rs=RW(self,'g_mov');
  const tr=rs.filter(x=>x.v.st==='transito'), pe=rs.filter(x=>x.v.st==='gestor'), es=rs.filter(x=>x.v.st==='estorno');
  v.k_tr=String(tr.length); v.k_tr_s=tr.map(x=>x.v.doc).join(' · ')||'nada em trânsito'; v.k_pe=String(pe.length); v.k_pe_s=pe.map(x=>x.v.doc).join(' · ')||'nenhuma aguardando';
  v.k_es=String(es.length); v.k_es_s=es.map(x=>x.v.doc).join(' · ');
  const parts=[]; if(tr.length) parts.push(tr.length+' em trânsito'); if(pe.length) parts.push(pe.length+(pe.length>1?' perdas':' perda')+' em alçada');
  hstatus(v,parts.join(' · ')||'Sem pendência no extrato',parts.length?'yellow':'green');
  v.conf=(id)=>{ const r=RF(self,'g_mov',id); if(!r||r.v.st!=='transito') return toast(self,(r?r.v.doc:id)+' já confirmada no destino · nada muda');
    setRows(self,'g_mov',rows=>{ rows.find(x=>x.id===id).v.st='conf'; }); toast(self,r.v.doc+' confirmada no destino: '+qq(r.v.q,r.v.un)+' de '+r.v.it+' saem do trânsito e entram em '+r.v.od.split(' → ')[1]); };
  v.apr=(id)=>{ const r=RF(self,'g_mov',id); if(!r||r.v.st!=='gestor') return toast(self,(r?r.v.doc:id)+' já aprovada · nada lançado de novo');
    setRows(self,'g_mov',rows=>{ rows.find(x=>x.id===id).v.st='aprov'; }); toast(self,r.v.doc+' aprovada por Ana (gestora) · '+qq(r.v.q,r.v.un)+' baixados de '+r.v.it+' com vínculo à perda'); }; }'''
    js(pn,code)
    painel()
    corpo=(kpis([('Em trânsito',H('k_tr'),H('k_tr_s')),('Perdas aguardando gestor',H('k_pe'),H('k_pe_s')),('Estornos lançados',H('k_es'),H('k_es_s'))])
           + bloco('Extrato imutável','Confira cada movimento com documento, origem e destino; clique na linha para ver o vínculo e a origem.',
                   g,
                   acao=mini('open_per','Registrar perda','Submete perda à alçada do gestor','alert')+mini('open_est','Estornar com vínculo','Cria estorno que referencia o movimento original','doc')
                        +alink('SU-07.dc.html','Devolver','Devoluções de campo entram pela requisição','truck')))
    HEIGHTS37[fname]=1180
    shell37('SU-08','Transferências e movimentos',corpo,fname=fname,
      subtitle='Extrato imutável e transferências entre locais, custódias e empresas; cada linha com documento e confirmação.',
      status=(MARK,'gray'),primary_html=primb('open_trf','Transferir entre locais','truck'),
      footer='Transferência tem trânsito e confirmação no destino; estorno referencia o movimento estornado (SU-08 · FO-32). '
             'Correção não apaga a operação original: o estorno cria movimento novo com vínculo. Movimentos entre empresas seguem a NF; devoluções de campo entram pela requisição com o mesmo documento.')
    dyn_status(fname)

# ================= SU-09 · Inventários e ajustes =================
CONTADORES=['Rui (conferente)','Paula (almoxarife)','Marta (conferente)']
APROV=['Ana (gestora)','Gerente da fazenda']
def su09():
    fname='SU-09.dc.html'; E._reset_screen(fname)
    I={c['id']:c for c in D2.CONTAGENS}; a,b_,c_=I['INV-2609'],I['INV-2610'],I['INV-2611']
    dif=a['contado']-a['sistema']; val=abs(dif)*PRECO['MAP 11-52']
    rows=[R('INV-2609',dict(inv='INV-2609',esc=f"{a['local']} · {a['item']} · {a['lote']}",corte='2026-09-20',cont='Rui (conferente)',sis=a['sistema'],obs=a['contado'],un='kg',
                            regra='Automática se diferença > 0,5 %',recont='confirmou 89.400 kg (Paula)',dif=dif,causa='Sacaria rasgada na pilha 3',ev='foto IMG-2209',val=round(val),apr='Ana (gestora)',st='aguarda'),{},ro=True,
            o=[dict(t=f"Contagem cega {nf(a['contado'])} kg × sistema {nf(a['sistema'])} kg · recontagem confirmou"),dict(t=f"Diferença {nf(dif)} kg × R$ {nf(PRECO['MAP 11-52'],2)}/kg = R$ {nf(val)} · alçada do gestor de suprimentos (até R$ 50 mil)"),
               dict(t='Contador (Rui) ≠ aprovador (Ana): segregação de funções atendida')]),
          R('INV-2612',dict(inv='INV-2612',esc='Almox. oficina · Filtro de óleo RE504836',corte='2026-09-22',cont='Marta (conferente)',sis=6,obs=5,un='un',regra='Sempre',recont='',dif=-1,causa='',ev='',val=86,apr='Ana (gestora)',st='dif'),{},
            o=[dict(t='Contagem cega 5 un × sistema 6 un'),dict(t='Diferença −1 un × R$ 86,00 = R$ 86 · alçada do gestor'),dict(t='Informe causa e evidência na linha antes de submeter')]),
          R('INV-2610',dict(inv='INV-2610',esc=f"{b_['local']} · {b_['item']} · {b_['lote']}",corte='2026-09-21',cont='Paula (almoxarife)',sis=b_['sistema'],obs=b_['contado'],un='L',regra='Automática se diferença > 0,5 %',recont='',dif=0,causa='',ev='',val=0,apr='—',st='ok'),{},ro=True,
            o=[dict(t=f"Contado {nf(b_['contado'])} L = sistema · encerrado sem ajuste"),dict(t='Ver o extrato do lote',h='SU-08.dc.html')]),
          R('INV-2611',dict(inv='INV-2611',esc=f"{c_['local']} · {c_['item']} · {c_['lote']}",corte='2026-09-25',cont='Paula (almoxarife)',sis=c_['sistema'],obs='',un='L',regra='Automática se diferença > 0,5 %',recont='',dif='',causa='',ev='',val=0,apr='Ana (gestora)',st='plan'),{},
            o=[dict(t='Contagem cega: o contador não vê o saldo do sistema'),dict(t='Movimentos do escopo ficam suspensos do corte ao encerramento'),dict(t='Contar no app de campo',h='MB-05.dc.html')])]
    g=grid([dict(k='inv',l='Inventário · escopo',w=250),dict(k='corte',l='Corte · contador',t='date'),dict(k='obs',l='Observado × sistema · recontagem',w=220),
            dict(k='dif',l='Diferença · causa',w=200),dict(k='est',l='Estado · ação',w=230)],
        rows,gid='g_inv',total=False,
        edit=dict(m='form',title='Inventário',sub='Contagem planejada: ajuste corte, contador e regra de recontagem. Com diferença: informe causa e evidência antes de submeter.',
          fields=[fs('sit','Situação','txt',ro=True),
                  fs('corte','Data de corte','date',req=True,cond=dict(k='sit',eq='Planejada')),fs('cont','Contador','sel',opts=CONTADORES,req=True,cond=dict(k='sit',eq='Planejada'),help='Quem conta não movimenta o local no período.'),
                  fs('regra','Recontagem','sel',opts=['Automática se diferença > 0,5 %','Sempre','Não recontar'],req=True,cond=dict(k='sit',eq='Planejada')),
                  fs('causa','Causa da diferença','txt',req=True,cond=dict(k='sit',eq='Com diferença · a submeter')),fs('ev','Evidência','txt',req=True,cond=dict(k='sit',eq='Com diferença · a submeter'),help='Ex.: foto, relatório de avaria.'),
                  fs('apr','Aprovador','sel',opts=APROV,req=True,cond=dict(k='sit',eq='Com diferença · a submeter'))]))
    ESC=['Galpão 1 · NPK 20-05-20 · N26-03','Câmara fria · Semente de soja 58 W · S58-0801','Tanque Sede · Diesel S10']
    pn={'plan':dict(title='Planejar contagem',sub='Contagem cega: quem conta não vê o saldo e não movimenta o local; movimentos do escopo ficam suspensos a partir do corte.',ok='Planejar contagem',
          fields=[fs('esc','Escopo','sel',opts=ESC,req=True,**{'def':ESC[0]}),fs('corte','Data de corte','date',req=True,**{'def':'2026-09-26'}),
                  fs('cont','Contador','sel',opts=CONTADORES,req=True,**{'def':'Rui (conferente)'}),fs('regra','Recontagem','sel',opts=['Automática se diferença > 0,5 %','Sempre','Não recontar'],req=True,**{'def':'Automática se diferença > 0,5 %'})])}
    code=r'''
const ST={aguarda:['Aguarda gestor · ajuste','yellow'],dif:['Diferença · a submeter','red'],ok:['Encerrado · sem diferença','green'],plan:['Planejada · corte ','gray'],ajustado:['Ajustado · ','green'],curso:['Em contagem · movimentos suspensos','yellow']};
function qq(n,un){ return nf(n,(n%1)?1:0)+' '+un; }
CHECK.plan=(self,d)=>{ if(d.corte<HOJE) return {corte:'O corte não pode ser antes de hoje (23/09).'}; if(RW(self,'g_inv').some(r=>r.v.esc===d.esc&&(r.v.st==='plan'||r.v.st==='curso'))) return {esc:'Já existe contagem aberta para este escopo · nada criado de novo.'}; return null; };
RUN.plan=(self,d)=>{ const n=(self.state.ninv||2612)+1; self.setState({ninv:n}); const id='INV-'+n;
  setRows(self,'g_inv',rows=>{ rows.push({id:id,v:{inv:id,esc:d.esc,corte:d.corte,cont:d.cont,sis:0,obs:'',un:'',regra:d.regra,recont:'',dif:'',causa:'',ev:'',val:0,apr:'Ana (gestora)',st:'plan'},s:{},p:{},o:[{t:'Contagem cega planejada · movimentos do escopo suspensos a partir de '+dm(d.corte)}]}); });
  return id+' planejada · corte '+dm(d.corte)+' · '+d.cont+' conta às cegas pelo app'; };
function PREVALS(self,v){ RW(self,'g_inv').forEach(r=>{ const V=r.v; V.sit=V.st==='plan'?'Planejada':(V.st==='dif'?'Com diferença · a submeter':(ST[V.st]||[V.st])[0]);
  r.p.inv=[B(V.inv),BRK,M(V.esc)]; r.s.inv=V.inv+' '+V.esc;
  r.p.corte=[T(dm(V.corte)),BRK,M(V.cont)];
  r.p.obs=((V.obs===''||V.obs===null)?[M(V.st==='plan'?'saldo oculto ao contador':'—')]:[T(qq(V.obs,V.un)+' × '+qq(V.sis,V.un))])
    .concat(V.recont?[BRK,M('recontagem: '+V.recont)]:(V.st==='plan'?[BRK,M('recontagem: '+V.regra.toLowerCase())]:[])); r.s.obs=String(V.obs);
  r.p.dif=(V.dif===''||V.dif===0)?[M(V.dif===0?'0':'—')]:[chipc((V.dif>0?'+':'')+qq(V.dif,V.un),'red')].concat(V.causa?[M(V.causa)]:[M('causa a informar')]);
  const s=ST[V.st]||[V.st,'gray']; const t=V.st==='plan'?s[0]+dm(V.corte):(V.st==='ajustado'?s[0]+V.aj:s[0]); r.s.est=t;
  r.ro=(V.st!=='plan'&&V.st!=='dif');
  const nx= V.st==='aguarda'?[{k:'act',t:'Aprovar ajuste',fn:'apr:'+r.id}] : V.st==='dif'?[{k:'act',t:'Submeter ajuste',fn:'sub:'+r.id},{k:'act',t:'Recontar',fn:'rct:'+r.id,lk:true}]
    : V.st==='plan'?[{k:'link',t:'Contar no app',h:'MB-05.dc.html'}] : (V.st==='ajustado'||V.st==='ok')?[{k:'link',t:'Ver efeito no extrato',h:'SU-08.dc.html'}] : [];
  r.p.est=[chipc(t,s[1])].concat(V.st==='aguarda'?[M(V.apr)]:[]).concat(nx.length?[BRK].concat(nx):[]); }); }
function EXTRAVALS(self,v){ pnVals(self,v); const rs=RW(self,'g_inv');
  const ag=rs.filter(x=>x.v.st==='aguarda'), di=rs.filter(x=>x.v.st==='dif'), pl=rs.filter(x=>x.v.st==='plan');
  v.k_ag=String(ag.length); v.k_ag_s=ag.length?ag.map(x=>x.id+' · R$ '+nf(x.v.val)).join(' · '):'nenhum ajuste pendente';
  v.k_di=String(di.length); v.k_di_s=di.map(x=>x.id).join(' · ')||'nenhuma'; v.k_pl=String(pl.length); v.k_pl_s=pl.map(x=>x.id+' · '+dm(x.v.corte)).join(' · ')||'nenhuma';
  const parts=[]; if(ag.length) parts.push(ag.length+(ag.length>1?' ajustes aguardando gestor':' ajuste aguardando gestor')); if(di.length) parts.push(di.length+' diferença a submeter');
  hstatus(v,parts.join(' · ')||'Sem ajuste pendente',ag.length||di.length?'yellow':'green');
  const a=rs.find(x=>x.id==='INV-2609'); v.has2609=a&&a.v.st==='aguarda'; v.no2609=!v.has2609;
  v.apr=(id)=>{ const r=RF(self,'g_inv',id); if(!r) return; if(r.v.st==='ajustado') return toast(self,id+' já aprovado · '+r.v.aj+', nada lançado de novo');
    if(r.v.st!=='aguarda') return toast(self,id+' ainda não foi submetido');
    const n=(self.state.naj||92)+1; const aj='AJ-00'+n; setRows(self,'g_inv',rows=>{ const x=rows.find(y=>y.id===id); x.v.st='ajustado'; x.v.aj=aj; });
    self.setState({naj:n}); toast(self,'Ajuste '+aj+' aprovado por Ana: '+r.v.esc.split(' · ').slice(-1)[0]+' '+nf(r.v.sis)+' → '+nf(r.v.obs)+' '+r.v.un+' ('+(r.v.dif>0?'+':'')+nf(r.v.dif)+' '+r.v.un+' · R$ '+nf(r.v.val)+') · movimento lançado no extrato com vínculo ao '+id); };
  v.apr2609=()=>v.apr('INV-2609');
  v.rct=(id)=>{ const r=RF(self,'g_inv',id); if(r.v.recont) return toast(self,'Recontagem já pedida · '+r.v.recont);
    setRows(self,'g_inv',rows=>{ rows.find(y=>y.id===id).v.recont='pedida a Rui (cega)'; }); toast(self,'Recontagem cega pedida a Rui (conferente) · quem contou não reconta · movimentos do escopo seguem suspensos'); };
  v.sub=(id)=>{ const r=RF(self,'g_inv',id); if(r.v.st!=='dif') return toast(self,id+' já submetido · nada submetido de novo');
    if(!String(r.v.causa||'').trim()||!String(r.v.ev||'').trim()) return toast(self,'Informe causa e evidência: clique na linha do '+id+' e preencha antes de submeter');
    setRows(self,'g_inv',rows=>{ rows.find(y=>y.id===id).v.st='aguarda'; }); toast(self,id+' submetido a '+r.v.apr+' · R$ '+nf(r.v.val)+' dentro da alçada do gestor · o saldo só muda depois da aprovação'); }; }'''
    js(pn,code)
    painel()
    corpo=(kpis([('Ajustes aguardando gestor',H('k_ag'),H('k_ag_s')),('Diferenças a submeter',H('k_di'),H('k_di_s')),('Contagens planejadas',H('k_pl'),H('k_pl_s'))])
           + bloco('Contagens cegas por local, item e lote','Planeje, conte e trate cada diferença com causa, evidência e aprovador; clique na linha para completar os dados.',
                   g,
                   acao=mini('open_plan','Planejar contagem','Cria contagem cega com corte de movimentos','calendar')+alink('MB-05.dc.html','Contar no app','Abre a contagem no app de campo','box')))
    prim=(f'<sc-if value="{H("has2609")}" hint-placeholder-val="{T()}">{primb("apr2609","Aprovar ajuste INV-2609","check")}</sc-if>'
          f'<sc-if value="{H("no2609")}" hint-placeholder-val="{F()}">{prima("SU-08.dc.html","Ver efeito no extrato")}</sc-if>')
    HEIGHTS37[fname]=820
    shell37('SU-09','Inventários e ajustes',corpo,fname=fname,
      subtitle='Contagens cegas com corte de movimentos, recontagem, causa e alçada; ajuste aprovado vira movimento no extrato.',
      status=(MARK,'gray'),primary_html=prim,
      footer='Diferença vira ajuste com causa, evidência e alçada, nunca correção silenciosa; limite e segregação seguem Configurações › Usuários e alçadas (SU-09 · FO-32). '
             'O contador não vê o saldo do sistema e os movimentos do escopo ficam suspensos entre o corte e o encerramento: movimentação durante a contagem não vira diferença fictícia. Quem conta não aprova o ajuste.')
    dyn_status(fname)

