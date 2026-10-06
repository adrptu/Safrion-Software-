# -*- coding: utf-8 -*-
"""Produção (grupo do menu logo depois de Agrícola, D-01) · colheita de ponta a ponta (docs/colheita/ESPECIFICACAO.md v1.1).
Três telas ligadas ao mesmo estado (cenario.js + producao.js, D-22), sem redigitar:
  COLH.dc.html  Previsão e colheita   planejamento + controle por talhão: previsão por contagem, programar a O.S., resultado
  CARGA.dc.html Cargas e recebimento  execução: ticket, origem, descontos, lote
  PROD.dc.html  Estoque de produto    controle: físico, bloqueado, apto, reservado, disponível; pedidos e reservas
Padrão das três (spec §3): master-detail (grade G2 com filtro e ordenação → painel do registro), filtros Fazenda e Safra no topo,
uma ação primária com verbo escolhida pelo registro selecionado (no cabeçalho; no celular fica presa ao rodapé), estado e próximo
passo em toda linha, unidade junto do número. Abaixo de 480 px a lista vira cartões (sem rolagem horizontal).
Regras, contas e comandos: producao.js (prXxx). Esta área só monta a tela e chama os comandos dentro de cenMudar.
Telas antigas CO-01..CO-07 continuam ocultas e intocadas (D-12)."""
import json
from engine import (grid,esc,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,BTN_ST,EXTRA,EXTRAJS,_MINI)
import engine as E
from ui37 import shell37, HEIGHTS37
import ui37
import cenario
import dados_carencia as DCAR

H=lambda s: '{{'+s+'}}'
T=lambda: H('true'); F=lambda: H('false')
def IF(h,body,d=False): return f'<sc-if value="{H(h)}" hint-placeholder-val="{T() if d else F()}">{body}</sc-if>'
LAB=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'

# ---------- casca comum ----------
CSS=('.pr-cards{display:none;flex-direction:column;gap:8px}'
     '.pr-card{display:flex;flex-direction:column;gap:5px;width:100%;text-align:left;padding:11px 13px;border:1px solid #E4E9E5;border-radius:14px;background:#FFFFFF;font-family:inherit;color:#15201A;cursor:pointer;box-sizing:border-box}'
     '.pr-card[aria-current=true]{border-color:#1E7A4C;box-shadow:0 0 0 1px #1E7A4C}'
     '.pr-card .pr-grp{font-size:11px;font-weight:800;letter-spacing:.05em;color:#65736A;text-transform:uppercase}'
     '@media (max-width:479px){.pr-lista .g2rola{display:none!important}.pr-cards{display:flex}'
     '.pr-prim{position:fixed!important;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:40;justify-content:center;text-align:center;white-space:normal!important;box-shadow:0 10px 24px -8px rgba(21,32,26,.45)!important;padding:12px 16px!important;font-size:14.5px!important}'
     'main[data-scroll]{padding-bottom:92px!important}main[data-scroll]+div{padding-bottom:84px!important}.pp-kv{grid-template-columns:minmax(0,1fr)!important}}'
     '.pr-vis{display:inline-flex;padding:3px;border-radius:999px;background:#EEF1EE;gap:2px}'
     '.pr-vis button{font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 14px;border-radius:999px;border:0;cursor:pointer;background:transparent;color:#65736A}'
     '.pr-vis button[aria-pressed=true]{background:#FFFFFF;color:#15201A;box-shadow:0 1px 2px rgba(21,32,26,.12)}')

def bloco(titulo,desc,corpo,acao=''):
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div class="pr-lista" style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')

def cartoes(lst):
    """Cartões do celular (< 480 px): os mesmos registros e o mesmo filtro da grade; tocar abre o painel do registro."""
    return (f'<div class="pr-cards" role="list" aria-label="Lista em cartões"><sc-for list="{H(lst)}" as="k" hint-placeholder-count="2">'
            f'<sc-if value="{H("k.grp")}" hint-placeholder-val="{F()}"><div class="pr-grp" role="listitem" style="font-size: 11px; font-weight: 800; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase; padding: 6px 2px 0;">{H("k.t1")} · {H("k.num")}</div></sc-if>'
            f'<sc-if value="{H("k.reg")}" hint-placeholder-val="{T()}"><button type="button" role="listitem" class="pr-card" aria-current="{H("k.cur")}" onClick="{H("k.go")}">'
            f'<span style="display: flex; align-items: baseline; gap: 8px; width: 100%;"><b style="font-size: 14px; flex-grow: 1; min-width: 0;">{H("k.t1")}</b><span style="font-size: 14px; font-weight: 800; white-space: nowrap;">{H("k.num")}</span></span>'
            f'<span style="font-size: 12.5px; color: {MUTED}; line-height: 1.35;">{H("k.t2")}</span>'
            f'<span style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;"><span style="{H("k.cst")}"><span style="{H("k.cdot")}"></span>{H("k.ct")}</span>'
            f'<span style="font-size: 12.5px; font-weight: 700; color: {ACC};">{H("k.nx")}</span></span></button></sc-if></sc-for></div>')

def painel():
    """Painel do registro (detalhe do master-detail), fora do main: próximo passo, dados, seções, formulário e uma ação primária."""
    chip=f'<span style="{H("pp_cst")}"><span style="{H("pp_cdot")}"></span>{H("pp_ct")}</span>'
    kv=(f'<sc-if value="{H("pp_hasKv")}" hint-placeholder-val="{F()}"><div class="pp-kv" style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 16px; padding: 10px 12px; background: {BG}; border-radius: 12px;">'
        f'<sc-for list="{H("pp_kv")}" as="x" hint-placeholder-count="4"><div style="min-width: 0;"><div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div>'
        f'<div style="font-size: 13px; font-weight: 600; margin-top: 2px; overflow-wrap: anywhere;">{H("x.v")}</div></div></sc-for></div></sc-if>')
    secs=(f'<sc-for list="{H("pp_secs")}" as="s" hint-placeholder-count="2"><section aria-label="{H("s.t")}" style="display: flex; flex-direction: column; gap: 2px;">{LAB(H("s.t"))}'
          f'<sc-for list="{H("s.rows")}" as="r" hint-placeholder-count="2"><div style="display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 10px; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px; line-height: 1.4;">'
          f'<sc-for list="{H("r.c")}" as="q" hint-placeholder-count="2"><span style="{H("q.st")}">{H("q.t")}</span></sc-for>'
          f'<sc-if value="{H("r.hasA")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("r.go")}" style="{_MINI}">{H("r.at")}</button></sc-if>'
          f'<sc-if value="{H("r.hasL")}" hint-placeholder-val="{F()}"><a href="{H("r.h")}" style="color: {ACC}; font-weight: 700; text-decoration: none; font-size: 12.5px;">{H("r.lt")} ›</a></sc-if></div></sc-for>'
          f'<sc-if value="{H("s.vazio")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {MUTED}; padding: 4px 0;">{H("s.vt")}</div></sc-if></section></sc-for>')
    fld=(f'<sc-for list="{H("pp_fields")}" as="f" hint-placeholder-count="2"><div style="display: flex; flex-direction: column; gap: 4px;">'
         f'<label for="{H("f.id")}" style="font-size: 12px; font-weight: 700; color: {MUTED};">{H("f.l")}</label>'
         f'<sc-if value="{H("f.isTxt")}" hint-placeholder-val="{F()}"><div style="display: flex; align-items: center; gap: 8px;"><input id="{H("f.id")}" type="text" inputMode="{H("f.im")}" autoComplete="off" value="{H("f.v")}" onChange="{H("f.set")}" placeholder="{H("f.ph")}" style="{H("f.st")}"><span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{H("f.u")}</span></div></sc-if>'
         f'<sc-if value="{H("f.isOpts")}" hint-placeholder-val="{F()}"><div role="group" aria-label="{H("f.l")}" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("f.opts")}" as="o" hint-placeholder-count="2"><button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></div></sc-if>'
         f'<sc-if value="{H("f.isSel")}" hint-placeholder-val="{F()}"><select id="{H("f.id")}" value="{H("f.v")}" onChange="{H("f.set")}" style="{H("f.st")}"><sc-for list="{H("f.opts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></sc-if>'
         f'<sc-if value="{H("f.hasH")}" hint-placeholder-val="{F()}"><span style="font-size: 11.8px; color: {MUTED}; line-height: 1.4;">{H("f.h")}</span></sc-if>'
         f'<sc-if value="{H("f.hasE")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("f.e")}</span></sc-if></div></sc-for>')
    form=(f'<sc-if value="{H("pp_hasForm")}" hint-placeholder-val="{F()}"><div role="group" aria-label="{H("pp_formT")}" style="display: flex; flex-direction: column; gap: 10px; padding: 12px; border: 1px solid {LINE}; border-radius: 12px;">'
          f'{LAB(H("pp_formT"))}<sc-if value="{H("pp_hasFormH")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {MUTED}; line-height: 1.45;">{H("pp_formH")}</div></sc-if>{fld}'
          f'<sc-if value="{H("pp_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700; line-height: 1.4;">{H("pp_err")}</div></sc-if></div></sc-if>')
    pe=(f'<div style="position: sticky; bottom: -20px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 0 -22px -20px; padding: 12px 22px; background: {SURF}; border-top: 1px solid {LINE};">'
        f'<sc-for list="{H("pp_sec")}" as="b" hint-placeholder-count="0"><button type="button" onClick="{H("b.go")}" style="{BTN_ST(False,True)}">{H("b.t")}</button></sc-for>'
        f'<span style="flex-grow: 1;"></span><button type="button" onClick="{H("pp_close")}" style="{BTN_ST(False,True)}">{H("pp_closeT")}</button>'
        f'<sc-if value="{H("pp_hasPB")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pp_pgo")}" style="{BTN_ST(True,True)}">{H("pp_pt")}</button></sc-if>'
        f'<sc-if value="{H("pp_hasPA")}" hint-placeholder-val="{F()}"><a href="{H("pp_ph")}" style="{BTN_ST(True,True)} text-decoration: none;">{H("pp_pt")}</a></sc-if></div>')
    return (f'<sc-if value="{H("pp_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar painel" tabIndex="-1" onClick="{H("pp_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-modal="true" aria-label="{H("pp_title")}" onKeyDown="{H("pp_key")}" style="position: relative; width: 540px; max-width: 100%; height: 100%; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 20px 22px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px;"><div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px;">'
            f'<h2 style="margin: 0; font-family: \'Sora\', \'Manrope\', system-ui, sans-serif; font-size: 19px; font-weight: 700; letter-spacing: -.02em;">{H("pp_title")}</h2>'
            f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 12.8px; color: {MUTED};">{chip}<span>{H("pp_sub")}</span></div></div>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pp_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
            f'<sc-if value="{H("pp_hasNext")}" hint-placeholder-val="{F()}"><div role="note" style="display: flex; flex-direction: column; gap: 3px; padding: 10px 12px; border-radius: 12px; background: {H("pp_nbg")};">{LAB("Próximo passo")}'
            f'<div style="font-size: 13.5px; line-height: 1.45; font-weight: 600;">{H("pp_next")}</div></div></sc-if>'
            + kv + form + secs + f'<div style="flex-grow: 1;"></div>' + pe + '</aside></div></sc-if>')

def prim_html():
    """Ação primária do cabeçalho: link (navega) ou botão (abre o painel na ação); nunca as duas ao mesmo tempo."""
    st=BTN_ST(True)
    return (f'<sc-if value="{H("prim_isB")}" hint-placeholder-val="{F()}"><button type="button" class="pr-prim" onClick="{H("prim_fn")}" style="{st}">{H("prim_t")}</button></sc-if>'
            f'<sc-if value="{H("prim_isA")}" hint-placeholder-val="{F()}"><a class="pr-prim" href="{H("prim_h")}" style="{st} text-decoration: none; display: inline-flex; align-items: center;">{H("prim_t")}</a></sc-if>')

def _status(fname):
    """selo do cabeçalho com cor calculada na tela (st_t/st_st/st_dot), como o da O.S."""
    import os
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H('st_t'),'yellow')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H("st_st")}"><span style="{H("st_dot")}"></span>{H("st_t")}</span>'))

def _shell(fid,title,sub,corpo,fname,altura,foot):
    EXTRA.append('<style>'+CSS+'</style>'); EXTRA.append(painel())
    HEIGHTS37[fname]=altura
    shell37(fid,title,corpo,fname=fname,subtitle=sub,status=(H('st_t'),'yellow'),primary_html=prim_html(),search=False,footer=foot)
    _status(fname)

def _js(tela):
    return cenario.js_prefixo()+DCAR.js_nucleo()+PR_UI_JS+tela

# =====================================================================================================================
# JS comum das três telas (leitura do estado e painel); regras e comandos em producao.js
# =====================================================================================================================
PR_UI_JS=r'''
/* ===== Produção · telas (COLH, CARGA, PROD): só montam a tela; regras e comandos em producao.js ===== */
function GR(id){ return GRIDS.find(g=>g.id===id); }
const PRK={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],blue:['#1E5F8F','#E3F0FB']};
function prChs(c){ const k=PRK[c]||PRK.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
function prDot(c){ const k=PRK[c]||PRK.gray; return 'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+k[0]+';'; }
const PR_QCOR={'Liberado':'green','Em inspeção':'yellow','Bloqueado':'red','Em processo':'blue','Esgotado':'gray'};
function prPill(on){ return 'font-family:inherit;font-size:13px;font-weight:700;padding:7px 12px;border-radius:999px;cursor:pointer;white-space:nowrap;min-height:36px;border:1px solid '+(on?'#1E7A4C':'#E4E9E5')+';background:'+(on?'#E4F3E9':'#FFFFFF')+';color:'+(on?'#1E6B47':'#15201A')+';'; }
function prInSt(err){ return 'font-family:inherit;font-size:15px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;max-width:240px;background:#FFFFFF;color:#15201A;border:1px solid '+(err?'#B42318':'#E4E9E5')+';'; }
function prCel(t,k){ return {t:String(t==null?'':t), st:k==='b'?'font-weight:800;color:#15201A;':(k==='mut'?'color:#65736A;':(k==='red'?'color:#B42318;font-weight:700;':(k==='ok'?'color:#1E7A4C;font-weight:700;':'color:#15201A;')))}; }
/* filtros do topo (DEC-2609-11): nestas telas a fazenda começa em Todas (a colheita em curso é da Lagoa Grande e o estoque de grão da Santa Rita) */
function prTopo(self,v){ if(self.state.mf_faz===undefined){ self.state.mf_faz='Todas'; } v.mf_faz=self.state.mf_faz; v.mf_saf=self.state.mf_saf||'Todas'; }
function prFazOk(self,faz){ const f=self.state.mf_faz||'Todas'; return f==='Todas'||!faz||faz===f; }
function prSafOk(self,saf){ const s=self.state.mf_saf||'Todas'; return s==='Todas'||!saf||saf===s; }
/* formulário do painel: valores em self.state.pr_form; o padrão (o.v) só para o que é herdado ou calculado, nunca último valor */
function prFval(self,k,def){ const F=self.state.pr_form||{}; return F[k]!==undefined?F[k]:(def===undefined?'':String(def)); }
function prFset(self,k,val){ self.setState({pr_form:Object.assign({},self.state.pr_form||{},{[k]:val}),pr_err:''}); }
function prFld(self,k,l,o){ o=o||{}; const val=prFval(self,k,o.v); const e=(self.state.pr_ferr||{})[k]||'';
  const f={id:'pf_'+k,l,isTxt:o.t==='txt',isOpts:o.t==='opts',isSel:o.t==='sel',v:val,u:o.u||'',im:o.im||'decimal',ph:o.ph||'',hasH:!!o.h,h:o.h||'',hasE:!!e,e,st:prInSt(e),
    set:(ev)=>prFset(self,k,ev.target.value)};
  if(o.opts) f.opts=o.opts.map(x=>({t:x.t,v:x.v,on:String(val===x.v),st:prPill(val===x.v),go:()=>prFset(self,k,(o.t==='opts'&&val===x.v&&o.tog)?'':x.v)}));
  return f; }
/* painel do registro: P = {title, chip:[t,cor], sub, next, kv, secs, form:{t,h,fields}, err, sec:[{t,go}], prim:{t,go}|{t,h}} */
function prPainel(self,v,P){ v.pp_open=!!P; P=P||{chip:['','gray']};
  v.pp_title=P.title||''; v.pp_ct=P.chip[0]; v.pp_cst=prChs(P.chip[1]); v.pp_cdot=prDot(P.chip[1]); v.pp_sub=P.sub||'';
  v.pp_hasNext=!!P.next; v.pp_next=P.next||''; v.pp_nbg=P.nred?'#FDE8E6':'#E4F3E9';
  v.pp_kv=P.kv||[]; v.pp_hasKv=v.pp_kv.length>0;
  v.pp_secs=(P.secs||[]).map(s=>({t:s.t,rows:(s.rows||[]).map(r=>({c:(r.c||[]).map(q=>Array.isArray(q)?prCel(q[0],q[1]):prCel(q)),hasA:!!r.a,at:r.a?r.a.t:'',go:r.a?r.a.go:(()=>{}),
    hasL:!!r.l,lt:r.l?r.l.t:'',h:r.l?r.l.h:'#'})),vazio:!(s.rows||[]).length,vt:s.vazio||'Nada registrado.'}));
  v.pp_hasForm=!!P.form; v.pp_formT=P.form?P.form.t:''; v.pp_hasFormH=!!(P.form&&P.form.h); v.pp_formH=P.form?(P.form.h||''):''; v.pp_fields=P.form?P.form.fields:[];
  v.pp_hasErr=!!P.err; v.pp_err=P.err||''; v.pp_sec=P.sec||[];
  v.pp_hasPB=!!(P.prim&&P.prim.go); v.pp_hasPA=!!(P.prim&&P.prim.h&&!P.prim.go); v.pp_pt=P.prim?P.prim.t:''; v.pp_ph=(P.prim&&P.prim.h)||'#'; v.pp_pgo=(P.prim&&P.prim.go)||(()=>{});
  v.pp_close=()=>self.setState({pr_pan:null,pr_form:null,pr_err:'',pr_ferr:null,pr_modo:null}); v.pp_closeT=P.form?'Cancelar':'Fechar';
  v.pp_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.pp_close(); } }; }
/* executa um comando no estado (atômico) e mostra o resultado; erro fica no painel, junto da ação */
function prRun(self,fn,ok){ const r=cenMudar(null,fn); if(r.erro){ self.setState({pr_err:r.erro,g2toast:''}); return r; }
  self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg||'Registrado.',pr_err:'',pr_ferr:null},ok||{})); return r; }
function prPrim(v,p){ v.prim_isB=!!(p&&p.go); v.prim_isA=!!(p&&p.h&&!p.go); v.prim_t=p?p.t:''; v.prim_fn=(p&&p.go)||(()=>{}); v.prim_h=(p&&p.h)||'#'; }
function prStatus(v,t,c){ v.st_t=t; v.st_st=prChs(c); v.st_dot=prDot(c); }
/* cartões: as linhas que a grade mostra agora (mesmo filtro, busca e ordem) */
function prCards(self,v,gid,mk){ const ids=(v[gid+'_rows']||[]).map(r=>r.id); const sel=(self.state.pr_sel||{}).id; return ids.map(id=>{ const k=mk(id); if(!k) return null; k.cur=String(id===sel); return k; }).filter(Boolean); }
function prCard(o){ return {grp:!!o.grp,reg:!o.grp,t1:o.t1||'',num:o.num||'',t2:o.t2||'',ct:(o.chip||['',''])[0],cst:prChs((o.chip||['','gray'])[1]),cdot:prDot((o.chip||['','gray'])[1]),nx:o.nx||'',go:o.go||(()=>{}),cur:'false'}; }
/* números com unidade na célula (decisão de 05/10/2026): valor tipado em v (base kg) para ordenar, texto em p */
function prTx(t){ return [{k:'txt',t}]; }
'''

# =====================================================================================================================
# PROD · Estoque de produto
# =====================================================================================================================
def prod():
    fname='PROD.dc.html'; E._reset_screen(fname)
    g_lot=grid([dict(k='nome',l='Lote · produto',w=230),dict(k='prod',l='Produto',w=170),dict(k='loc',l='Local · validade',w=190),
                dict(k='fis',l='Físico',t='num',a='r'),dict(k='blq',l='Bloqueado',t='num',a='r'),dict(k='apto',l='Apto',t='num',a='r'),
                dict(k='res',l='Reservado',t='num',a='r'),dict(k='disp',l='Disponível',t='num',a='r'),dict(k='q',l='Qualidade · próximo passo',w=260)],
               [],edit=dict(m='pick'),tree=True,gid='g_lot',total=False,qf=dict(k='q',cut=' · ',l='Qualidade',todas='Todos'),
               tools=f'<button type="button" aria-pressed="{H("sl_on")}" onClick="{H("sl_tog")}" style="{H("sl_st")}">Só com saldo</button>')
    g_ped=grid([dict(k='ped',l='Pedido · cliente',w=210),dict(k='prod',l='Produto',w=190),dict(k='tipo',l='Tipo · janela',w=170),dict(k='qtd',l='Quantidade',t='num',a='r'),
                dict(k='res',l='Reservado',t='num',a='r'),dict(k='falta',l='Falta',t='num',a='r'),dict(k='sit',l='Situação · próximo passo',w=260)],
               [],edit=dict(m='pick'),gid='g_ped',total=False,qf=dict(k='sit',cut=' · ',l='Situação',todas='Todos'))
    EXTRAJS[0]=_js(PROD_JS)
    corpo=(bloco('Lotes de produto','Produto › lote: físico, bloqueado, apto, reservado e disponível pela qualidade efetiva. Clique num lote para ver origem, qualidade, reservas e movimentos.',
                 g_lot+cartoes('cards_lot'))
           +bloco('Pedidos','Pronta entrega reserva lote apto; venda futura compromete a previsão, não o físico. Clique num pedido para reservar ou cancelar reserva.',
                  g_ped+cartoes('cards_ped')))
    _shell('PROD','Estoque de produto','Quanto tenho de cada produto, quanto está livre para vender e para quem está reservado.',corpo,fname,1250,
           'Entrada não é liberação: só lote Liberado vai para reserva. Venda futura não desconta o físico. Saca é derivada da massa (DEC-0510-03).')

PROD_JS=r'''
function prLoteRow(c,L,S){ const cu=L.cultura; const U=x=>prEstTxt(cu,x); const loc=(PRDC.locais[L.local]||{}).nome||L.local;
  const q=S.esgotado?'Esgotado':S.q; const nx=prLoteProx(c,L,S);
  return {id:L.id,ro:true,v:{nome:L.id,prod:L.prod,loc,fis:S.fis,blq:S.blq,apto:S.apto,res:S.res,disp:S.disp,q},
    s:{nome:L.id+' '+L.prod,prod:L.prod,loc:loc+' '+(L.validade?prBr(L.validade):''),q:q+' · '+nx.t,fis:U(S.fis),blq:U(S.blq),apto:U(S.apto),res:U(S.res),disp:U(S.disp)},
    p:{nome:[{k:'b',t:L.id},{k:'mut',t:' · '+(L.classe?L.classe+' ':'')+(L.saf||'')}],prod:[{k:'txt',t:L.prod}],
       loc:[{k:'txt',t:loc},{k:'br'},{k:L.validade&&S.vencido?'chip':'mut',t:L.validade?('vence '+prBr(L.validade)+(S.vencido?' · vencido':'')):'—',c:'yellow'}],
       fis:prTx(U(S.fis)),blq:prTx(U(S.blq)),apto:prTx(U(S.apto)),res:prTx(U(S.res)),disp:[{k:'b',t:U(S.disp)}],
       q:[{k:'chip',t:q,c:PR_QCOR[q]||'gray'},{k:'br'},{k:'mut',t:nx.t}]}}; }
/* próximo passo do lote (texto da linha) e ação primária (R-13, R-15) */
function prPedidosPara(c,L){ return Object.values(prP(c).pedidos).filter(p=>prCompat(p,L)&&prCmp(prFalta(c,p),0)>0).sort((a,b)=>(a.tipo==='pronta'?0:1)-(b.tipo==='pronta'?0:1)||a.id.localeCompare(b.id)); }
function prLoteProx(c,L,S){ if(S.esgotado) return {t:'sem saldo · rastreio guardado'};
  if(S.q==='Em processo') return {t:'no beneficiamento · fora do vendável'};
  if(S.q==='Bloqueado') return {t:S.dono+' decide · carência'};
  if(S.q==='Em inspeção') return {t:'Liberar lote · '+(S.dono||prQuem('qual')),a:'liberar'};
  if(prCmp(S.disp,0)>0&&prPedidosPara(c,L).length) return {t:'Reservar para pedido · '+prQuem('com'),a:'reservar'};
  return {t:prCmp(S.disp,0)>0?'disponível para venda':'todo reservado'}; }
function prPedRow(c,p){ const cu=p.cultura; const U=x=>prEstTxt(cu,x); const rs=prResPed(c,p.id); const res=prSoma(rs.map(r=>r.kg)); const falta=prFalta(c,p); const st=prSitPed(c,p);
  const nx=st.t==='Em risco'?('expedição impedida: '+st.imp.map(r=>r.lote).join(', ')):(st.t==='Entregue'?'entregue':(prCmp(falta,0)>0?(p.tipo==='futura'?'oferta da '+(p.sem?prSemTxt(p.sem):'safra')+' · reservar quando houver lote':'Reservar lote · '+prQuem('com')):'aguardar expedição'));
  return {id:p.id,ro:true,v:{ped:p.id,prod:p.prod,tipo:p.tipo==='futura'?'Futura':'Pronta entrega',qtd:p.qtd,res,falta,sit:st.t},
    s:{ped:p.id+' '+p.cliente,prod:p.prod,tipo:(p.tipo==='futura'?'Futura':'Pronta entrega')+' · '+p.janela,qtd:U(p.qtd),res:U(res),falta:U(falta),sit:st.t+' · '+nx},
    p:{ped:[{k:'b',t:p.id},{k:'mut',t:' · '+p.cliente}],prod:[{k:'txt',t:p.prod}],tipo:[{k:'txt',t:p.tipo==='futura'?'Futura':'Pronta entrega'},{k:'br'},{k:'mut',t:p.janela}],
       qtd:prTx(U(p.qtd)),res:prTx(U(res)),falta:[{k:'b',t:U(falta)}],sit:[{k:'chip',t:st.t,c:st.c},{k:'br'},{k:'mut',t:nx}]}}; }
const PR_GRIDS={g_lot:1,g_ped:1};
const _g2rows0=g2rows; g2rows=function(self,sp){ return PR_GRIDS[sp.id]?sp.rows:_g2rows0(self,sp); };
function PREVALS(self,v){ cenOuvir(self); prTopo(self,v); const c=cenGet(); self._c=c; const P=prP(c);
  self.g2pick=(gid,rid)=>{ if(String(rid).indexOf('grp:')===0) return; self.setState({pr_sel:{g:gid,id:rid},pr_pan:{g:gid,id:rid},pr_form:null,pr_err:'',pr_ferr:null,pr_modo:null}); };
  const so=self.state.pr_saldo!==false; v.sl_on=String(so); v.sl_st=prPill(so); v.sl_tog=()=>self.setState({pr_saldo:!so});
  const lots=Object.values(P.lotes).filter(L=>prFazOk(self,L.faz)&&prSafOk(self,L.saf)); const prods={};
  lots.forEach(L=>{ const S=prSaldos(c,L); if(so&&S.esgotado) return; (prods[L.prod]=prods[L.prod]||[]).push({L,S}); });
  const rows=Object.keys(prods).sort().map(pr=>{ const ls=prods[pr]; const cu=ls[0].L.cultura; const U=x=>prEstTxt(cu,x); const sm=k=>prSoma(ls.map(x=>x.S[k]));
    return {id:'grp:'+pr,ro:true,v:{nome:pr,prod:pr,fis:sm('fis'),blq:sm('blq'),apto:sm('apto'),res:sm('res'),disp:sm('disp')},
      s:{nome:pr,prod:pr,fis:U(sm('fis')),blq:U(sm('blq')),apto:U(sm('apto')),res:U(sm('res')),disp:U(sm('disp'))},
      p:{nome:[{k:'b',t:pr}],prod:[{k:'mut',t:ls.length+(ls.length>1?' lotes':' lote')}],loc:[{k:'mut',t:''}],fis:prTx(U(sm('fis'))),blq:prTx(U(sm('blq'))),apto:prTx(U(sm('apto'))),res:prTx(U(sm('res'))),disp:[{k:'b',t:U(sm('disp'))}],q:[{k:'mut',t:''}]},
      kids:ls.sort((a,b)=>a.L.id.localeCompare(b.L.id)).map(x=>prLoteRow(c,x.L,x.S))}; });
  GR('g_lot').rows=rows; const x0={}; rows.forEach(r=>{ x0[r.id]=true; }); GR('g_lot').x0=x0;
  const peds=Object.values(P.pedidos).filter(p=>{ const L=Object.values(P.lotes).find(x=>x.prod===p.prod); return prFazOk(self,L?L.faz:'')&&prSafOk(self,p.saf||(L&&L.saf)); });
  GR('g_ped').rows=peds.sort((a,b)=>a.id.localeCompare(b.id)).map(p=>prPedRow(c,p));
  self._lots=lots; self._peds=peds; }
function EXTRAVALS(self,v){ const c=self._c||cenGet(); const P=prP(c); const st=self.state;
  /* cartões (celular): mesmos registros, filtro e ordem da grade */
  v.cards_lot=prCards(self,v,'g_lot',id=>{ if(String(id).indexOf('grp:')===0){ const pr=id.slice(4); const ls=(self._lots||[]).filter(L=>L.prod===pr); if(!ls.length) return null; const cu=ls[0].cultura;
      return prCard({grp:true,t1:pr,num:prEstTxt(cu,prSoma(ls.map(L=>prSaldos(c,L).disp)))+' disponível'}); }
    const L=P.lotes[id]; if(!L) return null; const S=prSaldos(c,L); const q=S.esgotado?'Esgotado':S.q; const nx=prLoteProx(c,L,S);
    return prCard({t1:L.id+' · '+L.prod,num:prEstTxt(L.cultura,S.disp),t2:'Físico '+prEstTxt(L.cultura,S.fis)+' · reservado '+prEstTxt(L.cultura,S.res)+' · '+((PRDC.locais[L.local]||{}).nome||''),chip:[q,PR_QCOR[q]||'gray'],nx:nx.t,go:()=>self.g2pick('g_lot',id)}); });
  v.cards_ped=prCards(self,v,'g_ped',id=>{ const p=P.pedidos[id]; if(!p) return null; const st2=prSitPed(c,p);
    return prCard({t1:p.id+' · '+p.cliente,num:prEstTxt(p.cultura,prFalta(c,p))+' falta',t2:p.prod+' · '+(p.tipo==='futura'?'futura':'pronta entrega')+' · '+p.janela,chip:[st2.t,st2.c],nx:'',go:()=>self.g2pick('g_ped',id)}); });
  /* seleção → ação primária (uma, do registro); sem seleção: reservar o primeiro lote com disponível e pedido compatível */
  const sel=st.pr_sel; let alvo=null;
  if(sel&&sel.g==='g_lot'&&P.lotes[sel.id]) alvo={g:'g_lot',id:sel.id}; else if(sel&&sel.g==='g_ped'&&P.pedidos[sel.id]) alvo={g:'g_ped',id:sel.id};
  const acaoLote=(L)=>{ const S=prSaldos(c,L); const nx=prLoteProx(c,L,S); if(nx.a==='liberar') return {t:'Liberar '+L.id,go:()=>self.setState({pr_sel:{g:'g_lot',id:L.id},pr_pan:{g:'g_lot',id:L.id},pr_modo:'liberar',pr_form:null,pr_err:''})};
    if(nx.a==='reservar') return {t:'Reservar '+L.id+' para pedido',go:()=>self.setState({pr_sel:{g:'g_lot',id:L.id},pr_pan:{g:'g_lot',id:L.id},pr_modo:'reservar',pr_form:null,pr_err:''})}; return null; };
  const acaoPed=(p)=>{ if(prCmp(prFalta(c,p),0)<=0) return null; const ls=Object.values(P.lotes).filter(L=>prCompat(p,L)&&prCmp(prSaldos(c,L).disp,0)>0); if(!ls.length) return null;
    return {t:'Reservar lote para o '+p.id,go:()=>self.setState({pr_sel:{g:'g_ped',id:p.id},pr_pan:{g:'g_ped',id:p.id},pr_modo:'reservar',pr_form:null,pr_err:''})}; };
  let prim=null; if(alvo) prim=alvo.g==='g_lot'?acaoLote(P.lotes[alvo.id]):acaoPed(P.pedidos[alvo.id]);
  else { const ls=[].concat(...(GR('g_lot').rows||[]).map(r=>r.kids||[])).map(r=>P.lotes[r.id]).filter(Boolean); for(const L of ls){ const a=acaoLote(L); if(a&&/^Reservar/.test(a.t)){ prim=a; break; } } }
  prPrim(v,prim);
  const nPed=(self._peds||[]).filter(p=>{ const s=prSitPed(c,p).t; return s==='Sem reserva'||s==='Parcial'||s==='Em risco'; }).length;
  const nInsp=(self._lots||[]).filter(L=>prSaldos(c,L).q==='Em inspeção').length; const nProc=(self._lots||[]).filter(L=>{ const S=prSaldos(c,L); return S.q==='Em processo'&&!S.esgotado; }).length;
  const risco=(self._peds||[]).some(p=>prSitPed(c,p).t==='Em risco');
  prStatus(v,[nPed?nPed+(nPed>1?' pedidos sem cobertura':' pedido sem cobertura'):'pedidos cobertos',nInsp?nInsp+' em inspeção':'',nProc?nProc+' em processo':''].filter(Boolean).join(' · '),risco?'red':(nPed||nInsp?'yellow':'green'));
  /* painel */
  const pan=st.pr_pan; let PP=null;
  if(pan&&pan.g==='g_lot'&&P.lotes[pan.id]) PP=prPanLote(self,c,P.lotes[pan.id]); else if(pan&&pan.g==='g_ped'&&P.pedidos[pan.id]) PP=prPanPed(self,c,P.pedidos[pan.id]);
  prPainel(self,v,PP); }
function prFormReserva(self,c,L,p,fixo){ /* fixo: 'lote' (vem do lote: escolhe o pedido) ou 'ped' (vem do pedido: escolhe o lote) */
  const P=prP(c); let opcPed=[], opcLot=[];
  if(fixo==='lote'){ opcPed=prPedidosPara(c,L); p=P.pedidos[prFval(self,'ped',(opcPed[0]||{}).id||'')]||opcPed[0]||null; }
  else { opcLot=Object.values(P.lotes).filter(x=>prCompat(p,x)&&prCmp(prSaldos(c,x).disp,0)>0); L=P.lotes[prFval(self,'lot',(opcLot[0]||{}).id||'')]||opcLot[0]||null; }
  const S=L?prSaldos(c,L):null; const falta=p?prFalta(c,p):0; const sug=(S&&p)?(prCmp(S.disp,falta)<0?S.disp:falta):0; const cu=(L||p||{}).cultura||'Soja'; const un=prEstUn(cu);
  const fields=[]; if(fixo==='lote') fields.push(prFld(self,'ped','Pedido',{t:'opts',v:p?p.id:'',opts:opcPed.map(x=>({v:x.id,t:x.id+' · '+x.cliente+' · falta '+prEstTxt(x.cultura,prFalta(c,x))+(x.tipo==='futura'?' · futura':'')}))}));
  else fields.push(prFld(self,'lot','Lote apto',{t:'opts',v:L?L.id:'',opts:opcLot.map(x=>({v:x.id,t:x.id+' · disponível '+prEstTxt(x.cultura,prSaldos(c,x).disp)}))}));
  const k='q_'+(L?L.id:'')+'_'+(p?p.id:''); fields.push(prFld(self,k,'Quantidade a reservar',{t:'txt',v:prFmtT(prEstQ(cu,sug),3).replace(/\./g,''),u:un,h:'Sugestão: o menor entre o disponível do lote ('+(S?prEstTxt(cu,S.disp):'—')+') e a falta do pedido ('+prEstTxt(cu,falta)+'). Pode reduzir.'}));
  const go=()=>{ if(!L||!p){ self.setState({pr_err:'Escolha '+(fixo==='lote'?'o pedido':'o lote')+'.'}); return; } const q=prFval(self,k,prFmtT(prEstQ(cu,sug),3).replace(/\./g,''));
    const kg=prNumOk(q)?prEstBase(cu,prNum(q)):NaN; const ch='W-RS-'+L.id+'-'+p.id+'-'+(prResPed(c,p.id).length+1);
    prRun(self,x=>prReservar(x,{pedido:p.id,lote:L.id,kg,chave:ch,quem:prQuem('com')}),{pr_modo:null,pr_form:null}); };
  return {fields,go,L,p}; }
function prPanLote(self,c,L){ const P=prP(c); const S=prSaldos(c,L); const cu=L.cultura; const U=x=>prEstTxt(cu,x); const q=S.esgotado?'Esgotado':S.q; const nx=prLoteProx(c,L,S); const modo=self.state.pr_modo;
  const loc=(PRDC.locais[L.local]||{}); const lcs=prLcs(c,L);
  const orig=(L.origem||[]).map(x=>({c:[[x.carga||'abertura','b'],x.tal||'',x.os||'',x.dcol?'colhido '+prBr(x.dcol):'',U(x.kg)+(x.modo==='estimada'?' (estimada)':''),x.est?['estornada','red']:''].filter(Boolean),l:{t:'Ver carga',h:'CARGA.dc.html#'+(x.carga||'')}}));
  if(L.abertura) orig.push({c:[['Saldo de abertura','b'],'safra '+L.saf+' · anterior ao sistema, sem talhão (não entra na produção por talhão)']});
  const rs=Object.values(P.reservas).filter(r=>r.lote===L.id).map(r=>({c:[[r.id,'b'],r.pedido,U(r.kg),r.st,(r.st==='Ativa'&&S.q!=='Liberado')?['Expedição impedida','red']:'',r.canc?'cancelada: '+r.canc.motivo:''].filter(Boolean)}));
  const mv=P.movs.filter(m=>m.lote===L.id).slice().reverse().map(m=>({c:[[m.id,'b'],prBr(m.d)+' '+(m.at||''),m.tipo,m.fis===false?['sem efeito no físico','mut']:U(m.kg),m.carga||m.pedido||m.reserva||'',m.quem||'',m.obs||''].filter(Boolean)}));
  const dests=[...new Set(Object.values(P.pedidos).filter(p=>prCompat(p,L)).map(p=>p.dest||'MI-BR'))]; const av=[];
  if(typeof carAvaliar==='function') lcs.forEach(lc=>dests.forEach(d=>{ const a=carAvaliar(c,lc,d); av.push({c:[[lc,'b'],[a.rot,a.st==='nao_conforme'?'red':(a.st==='conforme'?'ok':'')],(a.motivos[0]||a.faltas[0]||{}).t||'',((a.motivos[0]||a.faltas[0]||{}).q?'quem resolve: '+(a.motivos[0]||a.faltas[0]).q:'')].filter(Boolean),l:{t:'Ver carência e destino',h:'CO-06.dc.html'}}); }));
  const PPx={title:L.id+' · '+L.prod,chip:[q,PR_QCOR[q]||'gray'],sub:(loc.nome||'')+(L.validade?' · vence '+prBr(L.validade)+(S.vencido?' (vencido: aviso, não trava)':''):'')+' · recebido '+prBr(L.drec),
    next:nx.t+'. Qualidade: '+(S.mot||'')+'.',nred:S.q==='Bloqueado',
    kv:[{l:'Físico',v:U(S.fis)},{l:'Bloqueado',v:U(S.blq)},{l:'Apto',v:U(S.apto)},{l:'Reservado',v:U(S.res)},{l:'Disponível',v:U(S.disp)},{l:'Em processo',v:U(S.proc)}],
    secs:[{t:'Origem',rows:orig},{t:'Avaliação do destino dos pedidos',rows:av,vazio:L.abertura?'Saldo de abertura sem lote de campo: o destino é avaliado na expedição.':'Sem lote de campo ainda (o apontamento da data cria o LC-).'},{t:'Reservas',rows:rs,vazio:'Nenhuma reserva.'},{t:'Movimentos',rows:mv}],
    err:self.state.pr_err};
  if(nx.a==='liberar'){ PPx.prim={t:'Liberar '+L.id,go:()=>prRun(self,x=>prLiberarLote(x,L.id,prQuem('qual')),{pr_modo:null})}; PPx.form={t:'Liberar lote · '+prQuem('qual'),h:'Confira a condição do lote. Liberar reavalia carência e ordem de colheita; com pendência, nada muda e a mensagem diz quem resolve.',fields:[]}; }
  else if(nx.a==='reservar'){ const f=prFormReserva(self,c,L,null,'lote'); PPx.form={t:'Reservar para pedido · '+prQuem('com'),h:'Reserva só de lote apto; a quantidade não passa do disponível nem da falta do pedido.',fields:f.fields}; PPx.prim={t:'Reservar',go:f.go}; }
  return PPx; }
function prPanPed(self,c,p){ const P=prP(c); const cu=p.cultura; const U=x=>prEstTxt(cu,x); const st=prSitPed(c,p); const falta=prFalta(c,p); const cx=self.state.pr_cx;
  const rs=Object.values(P.reservas).filter(r=>r.pedido===p.id).map(r=>{ const L=P.lotes[r.lote]; const imp=r.st==='Ativa'&&L&&prSaldos(c,L).q!=='Liberado';
    return {c:[[r.id,'b'],r.lote,U(r.kg),r.st,imp?['Expedição impedida','red']:'',r.canc?'motivo: '+r.canc.motivo:''].filter(Boolean),a:r.st==='Ativa'?{t:'Cancelar reserva',go:()=>self.setState({pr_cx:r.id,pr_form:null,pr_err:''})}:null}; });
  let ofTxt=''; if(p.tipo==='futura'&&p.sem){ const of=prOfertaSem(c,p.prod,p.sem); ofTxt='Oferta publicada da '+prSemTxt(p.sem)+': '+U(of.pub)+' · vendas futuras '+U(of.futKg)+' · oferta livre '+U(of.livre)+(prCmp(of.livre,0)<0?' (déficit)':''); }
  const PPx={title:p.id+' · '+p.cliente,chip:[st.t,st.c],sub:p.prod+' · '+(p.tipo==='futura'?'venda futura':'pronta entrega')+' · '+p.janela+(p.ref?' · '+p.ref:''),
    kv:[{l:'Quantidade',v:U(p.qtd)},{l:'Expedido',v:U(prExpedido(c,p.id))},{l:'Reservado',v:U(prSoma(prResPed(c,p.id).map(r=>r.kg)))},{l:'Falta',v:U(falta)},{l:'Destino',v:PRDC.dest[p.dest||'MI-BR']||p.dest},{l:'Observação',v:p.obs||'—'}],
    next:ofTxt||(st.t==='Em risco'?'Expedição impedida: o lote reservado deixou de ser apto. '+prQuem('qual')+' confere; '+prQuem('com')+' troca o lote ou cancela a reserva.':(prCmp(falta,0)>0?'Reservar lote apto para cobrir '+U(falta)+'.':'Coberto: aguardar a expedição.')),nred:st.t==='Em risco',
    secs:[{t:'Reservas',rows:rs,vazio:'Nenhuma reserva.'}],err:self.state.pr_err};
  if(cx){ PPx.form={t:'Cancelar '+cx,h:'O motivo fica no histórico; o disponível do lote volta.',fields:[prFld(self,'mot','Motivo do cancelamento',{t:'txt',im:'text',ph:'ex.: cliente adiou a retirada'})]};
    PPx.prim={t:'Cancelar '+cx,go:()=>prRun(self,x=>prCancelarReserva(x,cx,prFval(self,'mot',''),prQuem('com')),{pr_cx:null,pr_form:null})}; PPx.sec=[{t:'Manter reserva',go:()=>self.setState({pr_cx:null,pr_err:''})}]; return PPx; }
  const a=prCmp(falta,0)>0?Object.values(P.lotes).filter(x=>prCompat(p,x)&&prCmp(prSaldos(c,x).disp,0)>0):[];
  if(a.length){ const f=prFormReserva(self,c,null,p,'ped'); PPx.form={t:'Reservar lote para o '+p.id+' · '+prQuem('com'),h:'Só lote apto, do mesmo produto e classe. Venda futura reserva sem tocar a oferta publicada além da dedução.',fields:f.fields}; PPx.prim={t:'Reservar',go:f.go}; }
  return PPx; }
/* entrada por link: PROD.dc.html#L39-133 ou #PV-036 abre o registro */
function prHash(self){ if(self.__prh) return; self.__prh=1; const ab=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||'').slice(1); }catch(e){} const P=prP(cenGet());
  if(P.lotes[h]) setTimeout(()=>self.g2pick('g_lot',h),0); else if(P.pedidos[h]) setTimeout(()=>self.g2pick('g_ped',h),0); }; ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} }
const _EXV=EXTRAVALS; EXTRAVALS=function(self,v){ prHash(self); _EXV(self,v); };
'''

# =====================================================================================================================
# CARGA · Cargas e recebimento
# =====================================================================================================================
def carga():
    fname='CARGA.dc.html'; E._reset_screen(fname)
    g_cg=grid([dict(k='cg',l='Carga · ticket',w=170),dict(k='cult',l='Cultura',w=130),dict(k='orig',l='Origem',w=200),dict(k='dt',l='Colheita · recebimento',t='date',w=170),
               dict(k='liq',l='Líquido',t='num',a='r'),dict(k='com',l='Comercial',t='num',a='r',w=150),dict(k='lote',l='Lote · local',w=200),dict(k='sit',l='Situação · próximo passo',w=240)],
              [],edit=dict(m='pick'),gid='g_cg',total=False,qf=dict(k='sit',cut=' · ',l='Situação',todas='Todas'),so=dict(k='dt',d=True))
    EXTRAJS[0]=_js(CARGA_JS)
    corpo=bloco('Cargas','O que chegou de cada talhão, quanto pesou e em que lote está. Clique numa carga a pesar para pesar; numa recebida, para ver descontos, lote e trilha.',
                g_cg+cartoes('cards_cg'))
    _shell('CARGA','Cargas e recebimento','Pese e receba a carga do campo: o talhão vem da O.S., o lote nasce na hora e a produção do talhão muda só com a carga recebida.',corpo,fname,1000,
           'Produção só nasce de carga recebida; caixas ou kg estimados no campo nunca somam. Ticket repetido não duplica (R-03, R-07).')

CARGA_JS=r'''
const PR_GRIDS={g_cg:1};
const _g2rows0=g2rows; g2rows=function(self,sp){ return PR_GRIDS[sp.id]?sp.rows:_g2rows0(self,sp); };
function prCgSit(c,g){ const P=prP(c); if(g.st==='A pesar') return {t:'A pesar',c:'yellow',nx:'Pesar · '+prRec(g.faz)};
  if(g.st==='Estornada') return {t:'Estornada',c:'gray',nx:'sem efeito · '+((g.estorno||{}).motivo||'')};
  const L=P.lotes[g.lote]; const S=L?prSaldos(c,L):null;
  if(S&&S.q==='Bloqueado') return {t:'Bloqueada',c:'red',nx:S.dono+' decide · carência'};
  if(S&&S.q==='Em inspeção') return {t:'Recebida',c:'yellow',nx:'Qualidade confere · '+(S.dono||prQuem('qual'))};
  if(S&&S.q==='Em processo') return {t:'Recebida',c:'blue',nx:'no beneficiamento'};
  return {t:'Recebida',c:'green',nx:'no estoque de produto'}; }
function prCgOrig(g){ return (g.origem||[]).map(x=>x.tal+' · '+x.os+((g.origem||[]).length>1?' · '+prFmtT(x.pct,2)+' %'+(x.modo==='estimada'?' (estimada)':''):'')); }
function prCgRow(c,g){ const P=prP(c); const s=prCgSit(c,g); const L=P.lotes[g.lote]; const cu=g.cultura||'Mamão Formosa'; const u=prUn(cu); const kg=x=>prFmtT(x,2)+' kg';
  const comT=g.com===null||g.com===undefined?'—':(u.grao?kg(g.com)+' · '+prUnTxt(cu,g.com):(u.campo?prFmtT(g.litros,0)+' L · sc a apurar':(u.base==='frutos'?prFmtT(g.frutos,0)+' frutos':kg(g.com))));
  const orig=prCgOrig(g); const loc=(PRDC.locais[g.local]||{}).nome||'';
  return {id:g.id,ro:true,v:{cg:g.id,cult:cu,dt:g.dcol,liq:g.liq,com:g.com,lote:g.lote||'',sit:s.t},
    s:{cg:g.id+' '+(g.ticket||''),cult:cu,orig:orig.join(' '),liq:g.liq===null?'':kg(g.liq),com:comT,lote:(g.lote||'')+' '+loc,sit:s.t+' · '+s.nx},
    p:{cg:[{k:'b',t:g.id},{k:'mut',t:g.ticket?' · '+g.ticket:(g.via==='app'?' · do app':'')}],cult:[{k:'txt',t:cu}],
       orig:orig.reduce((a,t,i)=>a.concat(i?[{k:'br'},{k:'txt',t}]:[{k:'txt',t}]),[]),
       dt:[{k:'txt',t:'colhida '+prBr(g.dcol)},{k:'br'},{k:'mut',t:g.drec?('recebida '+prBr(g.drec)+' '+(g.horaRec||g.hora||'')):(g.est_cx?'~'+g.est_cx+' caixas (estimativa)':'a pesar')}],
       liq:g.liq===null?[{k:'mut',t:'—'}]:[{k:'txt',t:kg(g.liq)}],com:[{k:g.com===null?'mut':'b',t:comT}],
       lote:g.lote?[{k:'link',t:g.lote,h:'PROD.dc.html#'+g.lote},{k:'br'},{k:'mut',t:loc}]:[{k:'mut',t:'— · '+loc}],
       sit:[{k:'chip',t:s.t,c:s.c},{k:'br'},{k:'mut',t:s.nx}]}}; }
function PREVALS(self,v){ cenOuvir(self); prTopo(self,v); const c=cenGet(); self._c=c; const P=prP(c);
  self.g2pick=(gid,rid)=>self.setState({pr_sel:{g:gid,id:rid},pr_pan:{g:gid,id:rid},pr_form:null,pr_err:'',pr_ferr:null,pr_modo:null});
  const gs=prCargas(c,g=>g.sinc!==false&&prFazOk(self,g.faz)&&prSafOk(self,((PRDC.safras[(PRDC.cult[(g.origem[0]||{}).cult]||{}).saf]||{}).mf)||''));
  GR('g_cg').rows=gs.map(g=>prCgRow(c,g)); self._gs=gs; }
/* origens possíveis da carga (R-06): O.S. de colheita Liberadas, Em execução ou Em conferência, nas fazendas do filtro */
function prOrigens(self,c){ return Object.values(c.ordens||{}).filter(o=>prEhColheita(o)&&PR_FASES_COLH.indexOf(o.etapa)>=0&&prFazOk(self,prFazDaOS(c,o))).sort((a,b)=>a.id.localeCompare(b.id)); }
function prFormPesar(self,c,g){ const P=prP(c); const nova=!g; const ords=prOrigens(self,c);
  const os1=g?g.os:prFval(self,'os',ords.length===1?ords[0].id:''); const o=c.ordens[os1]; const cu=g?g.cultura:(o?(PRDC.cult[prCultDaOS(c,o)]||{}).cultura:''); const u=cu?prUn(cu):{};
  const mix=!g&&prFval(self,'mix','')==='sim'; const os2=prFval(self,'os2','');
  const fs=[];
  if(nova){ fs.push(prFld(self,'os','Origem · O.S. de colheita',{t:'opts',v:os1,opts:ords.map(x=>({v:x.id,t:x.id+' · '+x.talhao+' · '+x.etapa})),h:ords.length?'O talhão, a cultura e o local de recebimento vêm da O.S.':'Nenhuma O.S. de colheita liberada, em execução ou em conferência nesta fazenda.'}));
    fs.push(prFld(self,'mix','Carga de mais de um talhão?',{t:'opts',v:prFval(self,'mix','nao'),opts:[{v:'nao',t:'Um talhão'},{v:'sim',t:'+ talhão'}]}));
    if(mix){ fs.push(prFld(self,'os2','Segundo talhão · O.S.',{t:'opts',v:os2,opts:ords.filter(x=>x.id!==os1).map(x=>({v:x.id,t:x.id+' · '+x.talhao}))}));
      fs.push(prFld(self,'pct','Participação do 1º talhão',{t:'txt',u:'%',h:'O 2º fica com o resto (soma 100 %).'}));
      fs.push(prFld(self,'modo','Participação',{t:'opts',v:prFval(self,'modo','medida'),opts:[{v:'medida',t:'Medida'},{v:'estimada',t:'Estimada'}]})); }
    fs.push(prFld(self,'dcol','Dia da colheita',{t:'txt',im:'numeric',v:prDdMm(prHoje()),u:'dd/mm',h:'Hoje por padrão; informe se a fruta foi colhida antes.'})); }
  fs.push(prFld(self,'tk','Ticket da balança',{t:'txt',im:'text',ph:'ex.: TK-4520'}));
  fs.push(prFld(self,'bruto','Peso bruto',{t:'txt',u:'kg'})); fs.push(prFld(self,'tara','Tara',{t:'txt',u:'kg'}));
  if(u.grao){ fs.push(prFld(self,'u','Umidade',{t:'txt',u:'%',h:'Padrão '+prFmtT(u.u,1)+' %: acima disso desconta por matéria seca.'})); fs.push(prFld(self,'imp','Impureza',{t:'txt',u:'%',h:'Padrão '+prFmtT(u.imp,1)+' %: desconta só o que passa.'})); }
  if(u.campo) fs.push(prFld(self,'lit','Café da roça',{t:'txt',u:'L',h:'A saca sai do rendimento medido no beneficiamento.'}));
  if(u.base==='frutos') fs.push(prFld(self,'fr','Frutos contados',{t:'txt',im:'numeric',u:'frutos'}));
  fs.push(prFld(self,'cond','Condição da carga',{t:'opts',opts:PR_CONDS.map(x=>({v:x,t:x})),h:'Só Íntegra entra liberada; com avaria ou fora do padrão vai para inspeção da Qualidade.'}));
  const faz=g?g.faz:(o?prFazDaOS(c,o):''); const loc0=prLocalRec(faz,cu);
  const locs=Object.values(PRDC.locais).filter(l=>l.faz===faz&&['Galpão','Armazém','Silo','Câmara fria','Packing','Terreiro','Secador'].indexOf(l.tipo)>=0);
  if(locs.length>1) fs.push(prFld(self,'loc','Local de recebimento',{t:'sel',v:loc0,opts:locs.map(l=>({v:l.id,t:l.nome+' · '+l.tipo})),h:'Herdado da fazenda e da cultura. Packing, terreiro e secador: o lote nasce em processo.'}));
  const go=()=>{ const F=self.state.pr_form||{}; const val=k=>prFval(self,k,'');
    const k={ticket:val('tk'),bruto:val('bruto'),tara:val('tara'),cond:val('cond'),local:prFval(self,'loc',loc0),quem:prRec(faz)};
    if(u.grao){ k.u=val('u'); k.imp=val('imp'); } if(u.campo) k.litros=val('lit'); if(u.base==='frutos') k.frutos=val('fr');
    if(g){ k.carga=g.id; k.chave='W-REC-'+g.id; }
    else { if(!os1){ self.setState({pr_err:'Escolha a O.S. de colheita de origem.'}); return; }
      const d=prIsoDe(prFval(self,'dcol',prDdMm(prHoje()))); if(!d){ self.setState({pr_err:'Informe o dia da colheita (dd/mm).'}); return; } k.dcol=d;
      if(mix){ if(!os2){ self.setState({pr_err:'Escolha o segundo talhão.'}); return; } const p1=prNum(val('pct')); if(!(p1>0&&p1<100)){ self.setState({pr_err:'Informe a participação do 1º talhão (entre 0 e 100 %).'}); return; }
        const md=prFval(self,'modo','medida'); k.mix=[{os:os1,pct:p1,modo:md},{os:os2,pct:prSub(100,p1),modo:md}]; } else k.os=os1;
      k.chave='W-REC-'+(self.__nrec=(self.__nrec||0)+1)+'-'+String(k.ticket||'').trim(); }
    const r=prRun(self,x=>prReceber(x,k),{pr_form:null}); if(!r.erro&&r.g) self.setState({pr_sel:{g:'g_cg',id:r.g.id},pr_pan:{g:'g_cg',id:r.g.id}}); };
  return {fields:fs,go,cu}; }
function prPanCarga(self,c,g){ const P=prP(c); const s=prCgSit(c,g); const cu=g.cultura; const u=prUn(cu); const L=P.lotes[g.lote]; const S=L?prSaldos(c,L):null; const kg=x=>prFmtT(x,2)+' kg';
  const sub=prCgOrig(g).join(' + ')+' · colhida '+prBr(g.dcol)+(g.via==='app'?' · do app ('+(g.quem||'campo')+(g.veic?', '+g.veic:'')+')':'');
  if(g.st==='A pesar'){ const f=prFormPesar(self,c,g);
    return {title:g.id+' · a pesar',chip:['A pesar','yellow'],sub:sub+(g.est_cx?' · estimativa ~'+g.est_cx+' caixas (não soma)':''),next:'Pesar na balança e receber: '+prRec(g.faz)+'. A O.S. de colheita só encerra depois desta pesagem.',
      form:{t:'Pesar e receber · '+prRec(g.faz),h:'Bruto e tara em kg, sem valor anterior. O líquido, os descontos e o lote são calculados.',fields:f.fields},err:self.state.pr_err,prim:{t:'Pesar a '+g.id,go:f.go}}; }
  const part=(g.origem||[]).map(x=>({c:[[x.tal,'b'],x.os,prFmtT(x.pct,2)+' %',kg(x.kg),x.modo==='estimada'?'participação estimada':'medida',prLc(c,x.os,g.dcol)||'LC- entra quando o apontamento da data existir']}));
  const mv=P.movs.filter(m=>m.carga===g.id).map(m=>({c:[[m.id,'b'],prBr(m.d)+' '+(m.at||''),m.tipo,prEstTxt(cu,m.kg),m.lote,m.quem||'',m.obs||''].filter(Boolean)}));
  const desc=g.desc?('impureza −'+kg(g.desc.dImp)+' · umidade −'+kg(g.desc.dUmid)+' ('+prFmtT(g.u,1)+' % e '+prFmtT(g.impG,1)+' %)'):(u.campo?'sem desconto: café em L':'sem desconto (fruta: massa líquida pesada)');
  const PPx={title:g.id+' · '+(g.ticket||''),chip:[s.t,s.c],sub:sub+' · recebida '+prBr(g.drec)+(g.horaRec||g.hora?' '+(g.horaRec||g.hora):'')+' · '+(g.quemRec||g.quem||''),
    next:g.st==='Estornada'?'Estornada: '+(g.estorno||{}).motivo+' ('+(g.estorno||{}).quem+'). O ticket '+g.ticket+' ficou livre.':(s.nx+(S?'. Lote '+L.id+': '+S.q+' · '+S.mot:'')+'.'),nred:s.t==='Bloqueada',
    kv:[{l:'Bruto',v:kg(g.bruto)},{l:'Tara',v:kg(g.tara)},{l:'Líquido',v:kg(g.liq)},{l:'Descontos',v:desc},{l:'Comercial',v:u.grao?kg(g.com)+' · '+prUnTxt(cu,g.com):(u.campo?prFmtT(g.litros,0)+' L · sc a apurar':kg(g.com))},
        {l:'Lote · local',v:(g.lote||'—')+' · '+((PRDC.locais[g.local]||{}).nome||'')}],
    secs:[{t:'Participação por talhão',rows:part},{t:'Lote',rows:L?[{c:[[L.id,'b'],L.prod,S.q,S.mot],l:{t:'Abrir no estoque',h:'PROD.dc.html#'+L.id}}]:[]},{t:'Trilha de movimentos',rows:mv},
          {t:'Chave e recibo',rows:[{c:['chave do campo: '+(g.chave||'—')]},{c:['chave da pesagem: '+(g.chaveRec||'—')]}]}],err:self.state.pr_err};
  if(g.st==='Recebida'){ if(self.state.pr_modo==='estorno'){ PPx.form={t:'Estornar '+g.id,h:'Devolve o efeito: sai do '+g.lote+' e da produção do talhão. Recusado se o lote ficar abaixo do reservado.',fields:[prFld(self,'mot','Motivo do estorno',{t:'txt',im:'text',ph:'ex.: ticket trocado na balança'})]};
      PPx.prim={t:'Confirmar estorno',go:()=>prRun(self,x=>prEstornar(x,g.id,prFval(self,'mot',''),prRec(g.faz)),{pr_modo:null,pr_form:null})}; PPx.sec=[{t:'Manter carga',go:()=>self.setState({pr_modo:null,pr_err:''})}]; }
    else PPx.sec=[{t:'Estornar',go:()=>self.setState({pr_modo:'estorno',pr_form:null,pr_err:''})}]; }
  return PPx; }
function EXTRAVALS(self,v){ const c=self._c||cenGet(); const P=prP(c); const st=self.state;
  v.cards_cg=prCards(self,v,'g_cg',id=>{ const g=P.cargas[id]; if(!g) return null; const s=prCgSit(c,g);
    return prCard({t1:g.id+(g.ticket?' · '+g.ticket:''),num:g.liq===null?'a pesar':prFmtT(g.liq,2)+' kg',t2:prCgOrig(g).join(' + ')+' · colhida '+prBr(g.dcol)+(g.lote?' · '+g.lote:''),chip:[s.t,s.c],nx:s.nx,go:()=>self.g2pick('g_cg',id)}); });
  const sel=st.pr_sel; const gs=sel&&P.cargas[sel.id]; let prim;
  if(gs&&gs.st==='A pesar'&&gs.sinc!==false) prim={t:'Pesar a '+gs.id,go:()=>self.setState({pr_pan:{g:'g_cg',id:gs.id},pr_form:null,pr_err:''})};
  else prim={t:'Registrar pesagem',go:()=>self.setState({pr_pan:{g:'nova'},pr_sel:null,pr_form:null,pr_err:''})};
  prPrim(v,prim);
  const ap=(self._gs||[]).filter(g=>g.st==='A pesar').length, rc=(self._gs||[]).filter(g=>g.st==='Recebida').length, bl=(self._gs||[]).filter(g=>prCgSit(c,g).t==='Bloqueada').length;
  prStatus(v,[ap?ap+(ap>1?' cargas a pesar':' carga a pesar'):'nada a pesar',rc+(rc===1?' recebida':' recebidas'),bl?bl+' bloqueada':''].filter(Boolean).join(' · '),bl?'red':(ap?'yellow':'green'));
  const pan=st.pr_pan; let PP=null;
  if(pan&&pan.g==='nova'){ const f=prFormPesar(self,c,null); PP={title:'Registrar pesagem',chip:['Nova carga','gray'],sub:'Carga que chegou sem registro do app: escolha a O.S. de colheita de origem.',
      form:{t:'Pesar e receber',h:'Origem por um toque; bruto e tara em kg, sem valor anterior. Umidade e impureza só para grão.',fields:f.fields},err:st.pr_err,prim:{t:'Registrar pesagem',go:f.go}}; }
  else if(pan&&P.cargas[pan.id]) PP=prPanCarga(self,c,P.cargas[pan.id]);
  prPainel(self,v,PP); }
function prHash(self){ if(self.__prh) return; self.__prh=1; const ab=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||'').slice(1); }catch(e){} const P=prP(cenGet());
  if(P.cargas[h]&&P.cargas[h].sinc!==false) setTimeout(()=>self.g2pick('g_cg',h),0); }; ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} }
const _EXV=EXTRAVALS; EXTRAVALS=function(self,v){ prHash(self); _EXV(self,v); };
'''


def build():
    prod()
    carga()
