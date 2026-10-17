# -*- coding: utf-8 -*-
"""Agrícola › Análises de solo (AG-02 · SOLO-01; docs/analise-solo/ESPECIFICACAO.md §3.1 e §3.3).
Laudos de solo (e o foliar do MIP, só consulta): lista → painel do laudo (original ao lado do extraído, índices com 'não calculável',
uso no plano, validar) → painel "Por quê" (memória da sugestão). Água no solo por talhão ou zona: capacidade de campo, ponto de murcha e
CAD (referência para a Irrigação; não é a lâmina). Uma ação primária na tela: Registrar laudo. Regras e comandos em solo.js; dados em
dados_solo.py; estado em c.solo do cenário compartilhado (a mesma fonte do Planejar safra e da O.S.). Dados sintéticos."""
import json
from engine import (grid,esc,icon,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37, MACRO
import cenario, dados_solo as DS, ocupacao_cen as OCEN
import re as _re
def _ik(i): return 'i_'+_re.sub(r'\W','_',i['k'],flags=_re.ASCII)   # chave da coluna do indicador (a mesma do JS: ind.k com \W → _)

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
MACRO['AG-02.dc.html']=dict(faz='filtro')
LAB=lambda t: f'<div style="font-size: 10.5px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'

CSS=('.so-met-summary{min-height:24px;box-sizing:border-box;padding:3px 0}.so-met-label{font-size:12px;font-weight:700;color:#5B6660}'
     '@media(max-width:640px){.so-met-summary{min-height:44px;padding:12px 0}}'
     '.so-lado{display:grid;grid-template-columns:minmax(0,.75fr) minmax(0,1.7fr);gap:12px;align-items:start}'
     '.so-orig-m{display:none}'
     '.so-kv{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 16px}'
     '@media (max-width:899px){.so-lado{grid-template-columns:minmax(0,1fr)}.so-orig-d{display:none}.so-orig-m{display:block}}'
     '@media (max-width:640px){.so-kv{grid-template-columns:repeat(2,minmax(0,1fr))}.so-pan{padding:16px 14px!important}'
     '.so-pe{margin:0 -14px -16px!important;padding:12px 14px!important}.so-pe button,.so-pe a{min-height:44px!important}.so-sug button{min-height:44px}}')

def bloco(titulo,desc,corpo,acao=''):
    acao=E.recolhe_acoes(titulo,acao)   # MAIS-01 (15/10/2026): uma secundária à vista, as outras no "⋯ Mais ações" do bloco
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')

def _overlay(pre,w,corpo,z=60):
    return (f'<sc-if value="{H(pre+"open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: {z}; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar painel" tabIndex="-1" onClick="{H(pre+"close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-modal="true" aria-label="{H(pre+"titulo")}" onKeyDown="{H(pre+"key")}" class="so-pan" style="position: relative; width: {w}px; max-width: 100%; height: 100%; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 20px 22px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            + corpo + '</aside></div></sc-if>')

def _cabeca(pre,chip=True):
    ch=(f'<span style="{H(pre+"cst")}"><span style="{H(pre+"cdot")}"></span>{H(pre+"ct")}</span>' if chip else '')
    return (f'<div style="display: flex; align-items: flex-start; gap: 10px;"><div style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px;">'
            f'<h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em;">{H(pre+"titulo")}</h2>'
            f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-size: 12.8px; color: {MUTED};">{ch}<span>{H(pre+"sub")}</span></div></div>'
            f'<button type="button" id="{pre}x" aria-label="Fechar" title="Fechar" onClick="{H(pre+"close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>')

def _rodape(pre):
    """rodapé preso: Fechar (secundário) e uma primária (botão ou link) quando houver"""
    return (f'<div class="so-pe" style="position: sticky; bottom: -20px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 0 -22px -20px; padding: 12px 22px; background: {SURF}; border-top: 1px solid {LINE};">'
            f'<sc-for list="{H(pre+"sec")}" as="b" hint-placeholder-count="0"><button type="button" onClick="{H("b.go")}" style="{BTN_ST(False,True)}">{H("b.t")}</button></sc-for>'
            f'<span style="flex-grow: 1;"></span><button type="button" onClick="{H(pre+"close")}" style="{BTN_ST(False,True)}">{H(pre+"closeT")}</button>'
            f'<sc-if value="{H(pre+"hasPB")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H(pre+"pgo")}" style="{BTN_ST(True,True)}">{H(pre+"pt")}</button></sc-if>'
            f'<sc-if value="{H(pre+"hasPA")}" hint-placeholder-val="{F()}"><a href="{H(pre+"ph")}" style="{BTN_ST(True,True)} text-decoration: none;">{H(pre+"pt")}</a></sc-if></div>')

def porque_html(z=70):
    """painel "Por quê" (memória da sugestão, que antes ficava no AG-04det): laudo, entradas, regra rotulada, conta e efeito; sobre o painel
    em que está; uma primária pelo contexto (Usar X no painel de insumos, Marcar no lote, nenhuma no AG-02)."""
    lst=lambda hole,ttl: (f'<section aria-label="{ttl}" style="display: flex; flex-direction: column; gap: 4px;">{LAB(ttl)}'
                          f'<sc-for list="{H(hole)}" as="q" hint-placeholder-count="2"><div style="font-size: 13px; line-height: 1.45; padding: 5px 0; border-top: 1px solid {LINE};">{H("q.t")}</div></sc-for></section>')
    corpo=(_cabeca('pq_',chip=False)
           + lst('pq_lau','Laudo')
           + f'<sc-if value="{H("pq_hasVer")}" hint-placeholder-val="{F()}"><a href="{H("pq_ver")}" style="color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px;">Ver laudo ›</a></sc-if>'
           + lst('pq_ent','Entradas usadas')
           + f'<section aria-label="Regra" style="display: flex; flex-direction: column; gap: 4px;">{LAB("Regra")}<div style="display: inline-flex; align-self: flex-start; padding: 3px 10px; border-radius: 999px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">{H("pq_rot")}</div>'
             f'<div style="font-size: 12.8px; color: {MUTED};">{H("pq_regra")}</div></section>'
           + lst('pq_conta','Conta')
           + lst('pq_ef','Efeito')
           + f'<div style="flex-grow: 1;"></div>' + _rodape('pq_'))
    return _overlay('pq_',440,corpo,z)

# JS comum (AG-02 e Planejar safra): painel "Por quê" a partir de uma sugestão de soloSugestoes
SOLO_UI_JS=r'''
/* ===== Análise de solo · peças de tela comuns (AG-02 e Planejar safra); regras em solo.js ===== */
function soChs(c){ const k=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
function soDot(c){ const k=G2C[c]||G2C.gray; return 'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+k[0]+';'; }
/* SOLO_SITC (cor da situação do laudo) está em solo.js: o Mapa usa a mesma */
function soDiaCol(r,k,iso){ const ok=/^\d{4}-\d{2}-\d{2}/.test(String(iso||'')); r.v[k]=ok?Number(String(iso).slice(0,10).replace(/-/g,'')):''; const t=ok?soloBr(iso):'—'; r.p[k]=[{k:'txt',t}]; r.s[k]=ok?t:''; }
function soSugTxt(s){ return s.tipo==='retirar'?(s.incl0?'retirar a inclusão ('+(s.motivo||'pela análise')+')':'retirar ('+(s.motivo||'pela análise')+')'):(s.tipo==='incluir'?'incluir '+soloDoseTxt(s.sug,s.un):soloDoseTxt(s.sug,s.un)+(s.desf?' (padrão do plano)':'')); }
function soEfeito(s,cu){ const out=[]; const area=Number((cu&&cu.area)||0);
  if(s.tipo==='retirar') out.push('Dose: '+soloDoseTxt(s.ef===null||s.ef==='-'?s.padrao:s.ef,s.un)+' → retirar'+(s.unico?' · a '+s.atv.nome+' sai do '+((cu&&cu.local)||'')+' (único insumo)':''));
  else out.push('Dose: '+(s.ef===null||s.ef==='-'?(s.tipo==='incluir'?'—':soloDoseTxt(s.padrao,s.un)):soloDoseTxt(s.ef,s.un))+' → '+soloDoseTxt(s.sug,s.un)+(s.padrao!==null&&s.padrao!==undefined&&s.tipo!=='incluir'?' (padrão '+soloDoseTxt(s.padrao,s.un)+')':''));
  out.push('Quantidade no '+((cu&&cu.local)||'talhão')+' ('+cenNum(area)+' ha): '+soloQtdTxt(s.dif,s.un,true));
  out.push('Custo de insumos: '+(s.custo>0?'+':(s.custo<0?'−':''))+'R$ '+cenNum(Math.abs(s.custo),2)+' (preço R$ '+cenNum(s.preco,2)+'/'+s.un+')');
  out.push('Data: '+soloBr(s.dt)+(s.nega?' · não aplicável: '+s.nega:''));
  return out; }
/* opts: {cu, prim:{t,go}|null, ver:href|'', fechar()} */
function soloPqVals(self,v,s,o){ v.pq_open=!!s; if(!s) return; o=o||{}; const L=s.laudo||{};
  v.pq_titulo='Por quê · '+s.atv.nome+' · '+s.prod; v.pq_sub=((o.cu&&o.cu.local)||'')+' · análise sugere '+soSugTxt(s);
  v.pq_lau=[{t:L.id+' · '+L.tal+' · '+L.prof+' cm · coleta '+soloBr(L.coleta)},{t:L.lab+' · extrator '+L.ext},{t:'Validado por '+(L.por||'—')+(L.em?' em '+soloBr(L.em):'')}];
  v.pq_ver=o.ver||''; v.pq_hasVer=!!o.ver; v.pq_ent=(s.ent||[]).map(t=>({t})); v.pq_rot=s.rot||SOLO0.regra.rotulo;
  v.pq_regra={'calagem':'Calagem por saturação por bases (CAL-10), V₂ por cultura','potássio':'Adubação potássica por classe de teor de K e meta de produtividade','gessagem':'Gessagem pelo diagnóstico de subsuperfície (20–40 cm)'}[s.regra]||s.regra;
  v.pq_conta=(s.conta||[]).map(t=>({t})); v.pq_ef=soEfeito(s,o.cu).map(t=>({t}));
  v.pq_sec=[]; v.pq_closeT='Fechar'; v.pq_hasPA=false; v.pq_ph='#';
  v.pq_hasPB=!!o.prim; v.pq_pt=o.prim?o.prim.t:''; v.pq_pgo=o.prim?o.prim.go:(()=>{});
  v.pq_close=()=>{ o.fechar&&o.fechar(); setTimeout(()=>{ try{ const e=document.getElementById(self.__pqFoco||''); if(e) e.focus(); }catch(x){} },60); };
  v.pq_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); v.pq_close(); } }; }
'''

JS=r'''
function GR(id){ return GRIDS.find(g=>g.id===id); }
const SO_UN={'pH':['CaCl₂','H₂O'],'P':['mg/dm³'],'MO':['g/dm³'],'Ca':['cmolc/dm³','mmolc/dm³','mg/dm³'],'Mg':['cmolc/dm³','mmolc/dm³','mg/dm³'],'K':['mg/dm³','cmolc/dm³','mmolc/dm³'],'H+Al':['cmolc/dm³','mmolc/dm³'],'Al':['cmolc/dm³','mmolc/dm³'],'S':['mg/dm³'],'B':['mg/dm³'],'Cu':['mg/dm³'],'Fe':['mg/dm³'],'Mn':['mg/dm³'],'Zn':['mg/dm³'],'Argila':['%','g/kg']};
const SO_AN=['pH','P','MO','Ca','Mg','K','H+Al','Al','S','B','Cu','Fe','Mn','Zn','Argila'];
function soRlAnalito(a,q){ return {a,v:q&&q.v!==undefined&&q.v!==null?String(q.v).replace('.',','):'',un:q&&q.un||SO_UN[a][0],met:q&&q.met||'',ld:q&&q.ld!==undefined&&q.ld!==null?String(q.ld):'',q:q&&q.q||''}; }
function soRlErroAnalitos(an){ for(const x of an){
  if(x.q&&x.q!=='<') return x.a+': selecione Valor medido ou Abaixo do limite de detecção.';
  const detalhes=(x.a!=='P'&&x.a!=='K'&&String(x.met||'').trim())||String(x.ld==null?'':x.ld).trim()||x.q;
  if(String(x.v==null?'':x.v).trim()===''&&detalhes) return x.a+': informe o valor do laudo (para < 0,1: valor 0,1 e qualificador <) ou limpe os detalhes.';
} return ''; }
function soRlEnviarAnalitos(an,ext){ const erro=soRlErroAnalitos(an); if(erro) throw new Error(erro);
  return an.filter(x=>String(x.v==null?'':x.v).trim()!=='').map(x=>({a:x.a,v:x.v,un:x.un,met:(x.a==='P'||x.a==='K')?ext:(x.met||''),ld:x.ld===undefined||x.ld===null?'':String(x.ld),q:x.q||''})); }
function soFazOk(self,f){ const x=self.state.mf_faz||'Todas'; return x==='Todas'||f===x; }
function soFz(self){ const x=self.state.mf_faz||'Todas'; return x==='Todas'?'Santa Rita':x; }
function soAtor(){ return g2perfil().k; }
/* soloUsoCont e soloNoPlano ("No plano" do laudo) estão em solo.js: o Mapa (camada Análises de solo) usa os mesmos */
function soTalTxt(l){ return l.tal+(l.area?' · '+cenNum(Number(l.area))+' ha':'')+(l.zona?' · '+l.zona:''); }
function soSafraDe(u){ const x=(u||[]).find(z=>z.s&&!/^não aplicável/.test(z.st)); return x?x.cu.saf:''; }
function soPlanoHref(saf){ return 'SAF.dc.html#saf='+encodeURIComponent(saf)+'&passo=cultivos&sug=1'; }
function PREVALS(self,v){ cenOuvir(self); if(self.state.mf_faz===undefined) self.state.mf_faz='Todas';
  const c=cenGet(); const ls=soloLaudos(c,SOLO0); self.__ls=ls; self.__uso={};
  /* ---- laudos ---- */
  GR('g_lau').rows=ls.filter(l=>soFazOk(self,l.faz)).map(l=>{ const u=soloUsoNoPlano(c,SOLO0,l); self.__uso[l.id]=u; const np=soloNoPlano(l,u); const ix=l.idx; const K=soloAn(l,'K');
    const r={id:l.id,ro:true,v:{},s:{},p:{}};
    r.p.lau=[{k:'b',t:l.id},{k:'mut',t:l.tipo}]; r.s.lau=l.id+' '+l.tipo;
    r.p.tal=[{k:'txt',t:l.tal+(l.area?' · '+cenNum(Number(l.area))+' ha':'')}].concat(l.zona?[{k:'br'},{k:'mut',t:l.zona}]:[]); r.s.tal=soTalTxt(l);
    r.p.prof=[{k:'txt',t:l.prof?l.prof+' cm':'—'}]; r.s.prof=l.prof?l.prof+' cm':'';
    soDiaCol(r,'coleta',l.coleta);
    if(ix){ const V=ix.V; r.v.V=V.v===null?'':V.v; r.p.V=V.v===null?[{k:'mut',t:'não calculável'}]:[{k:'txt',t:prFmtT(V.v,2)+' %'}].concat(V.difere?[{k:'br'},{k:'chip',t:'difere do laboratório',c:'yellow'}]:[]); r.s.V=V.v===null?'não calculável':prFmtT(V.v,2)+' %'; }
    else { r.v.V=''; r.p.V=[{k:'mut',t:'—'}]; r.s.V=''; }
    if(K){ const t=prFmtT(K.v,2)+(K.un?' '+K.un:''); r.p.K=K.un?[{k:'txt',t}]:[{k:'txt',t:prFmtT(K.v,2)},{k:'chip',t:'sem unidade',c:'red'}]; r.s.K=K.un?t:prFmtT(K.v,2)+' sem unidade'; r.v.K=Number(K.v); } else { r.p.K=[{k:'mut',t:'—'}]; r.s.K=''; r.v.K=''; }
    // os demais indicadores do laudo (15/10/2026, proprietário: "falta vários indicadores chave... pegar automático do que vier"): coluna por indicador
    (SOLO0.ind||[]).forEach(ind=>{ if(ind.k==='V'||ind.k==='K') return; const k='i_'+ind.k.replace(/\W/g,'_'); const x=l.tipo==='solo'?soloIndVal(l,ind):null;
      if(x===null||!isFinite(x)){ r.v[k]=''; r.p[k]=[{k:'mut',t:'—'}]; r.s[k]=''; return; }
      const t=cenNum(x,ind.dec)+(ind.un==='%'?' %':(ind.un==='CaCl₂'?'':' '+ind.un)); r.v[k]=x; r.p[k]=[{k:'txt',t}]; r.s[k]=t; });
    r.p.sit=[{k:'chip',t:l.sit,c:SOLO_SITC[l.sit]||'gray'}].concat(l.motivo?[{k:'br'},{k:'mut',t:l.motivo}]:[]); r.s.sit=l.sit;
    r.p.plano=np.c?[{k:'chip',t:np.t,c:np.c}]:[{k:'mut',t:np.t}]; r.s.plano=np.t; return r; });
  /* ---- água no solo ---- */
  const S=(c.solo||{}); const ms=(SOLO0.agua||[]).concat(Object.values(S.agua||{})).filter(m=>soFazOk(self,m.faz));
  GR('g_agua').rows=ms.map(m=>{ const cad=soloCAD(m); const r={id:m.id,ro:true,v:{},s:{},p:{}};
    r.p.med=[{k:'b',t:m.id}]; r.s.med=m.id; r.p.tal=[{k:'txt',t:m.tal}].concat(m.zona?[{k:'br'},{k:'mut',t:m.zona}]:[]); r.s.tal=m.tal+(m.zona?' · '+m.zona:'');
    soDiaCol(r,'data',m.data); r.p.prof=[{k:'txt',t:m.prof+' cm'},{k:'br'},{k:'mut',t:'raízes até '+prFmtT(m.z,1)+' cm'}]; r.s.prof=m.prof+' cm · raízes '+prFmtT(m.z,1)+' cm';
    r.p.met=[{k:'txt',t:m.met}]; r.s.met=m.met;
    const vu=(x)=>x===''||x===null||x===undefined?'—':prFmtT(x,2)+' '+(m.un==='% volume'?'% vol.':m.un);
    r.p.cc=[{k:'txt',t:vu(m.cc)}]; r.s.cc=vu(m.cc); r.v.cc=Number(m.cc); r.p.pmp=m.pmp===''?[{k:'mut',t:'não medido'}]:[{k:'txt',t:vu(m.pmp)}]; r.s.pmp=m.pmp===''?'não medido':vu(m.pmp); r.v.pmp=m.pmp===''?'':Number(m.pmp);
    r.p.cad=cad.v===null?[{k:'mut',t:'não calculável'},{k:'br'},{k:'mut',t:cad.nc}]:[{k:'b',t:prFmtT(cad.v,1)+' mm'}]; r.s.cad=cad.v===null?'não calculável':prFmtT(cad.v,1)+' mm'; r.v.cad=cad.v===null?'':cad.v;
    r.p.fonte=[{k:'txt',t:m.fonte},{k:'br'},{k:'mut',t:m.resp}]; r.s.fonte=m.fonte+' · '+m.resp;
    Object.assign(r.v,{faz:m.faz,talv:m.tal,zona:m.zona,datav:m.data,profv:m.prof,z:m.z,metv:m.met,un:m.un,ccv:m.cc,pmpv:m.pmp,fontev:m.fonte,resp:m.resp,cadT:cad.v===null?'não calculável: '+cad.nc:cad.e});
    return r; });
  /* ---- painel do laudo: extraído e uso no plano ---- */
  const l=ls.find(x=>x.id===self.state.lau)||null; self.__l=l;
  if(l){ const rows=l.an.map(x=>{ const r={id:'a:'+x.a,v:{atr:x.a,val:Number(x.v),un:x.un,orig:'medido'},s:{},p:{}};
      r.p.atr=[{k:'b',t:x.a}]; r.s.atr=x.a; r.p.val=x.un?[{k:'txt',t:prFmtT(x.v,3)+' '+x.un}]:[{k:'txt',t:prFmtT(x.v,3)},{k:'chip',t:'sem unidade',c:'red'}]; r.s.val=prFmtT(x.v,3)+' '+(x.un||'sem unidade');
      r.p.met=[{k:'txt',t:x.met||'—'}]; r.s.met=x.met||''; r.p.ld=[{k:'txt',t:(x.q==='<'?'< ':'')+(x.ld||'—')}]; r.s.ld=x.ld||'';
      r.p.orig=[{k:'mut',t:'medido'}].concat(x.corrigido?[{k:'chip',t:'corrigido',c:'yellow'}]:[]); r.s.orig='medido'+(x.corrigido?' corrigido':''); return r; });
    if(l.idx) ['SB','T','t','V','m'].forEach(k=>{ const q=l.idx[k]; const un=(k==='V'||k==='m')?'%':'cmolc/dm³'; const r={id:'i:'+k,ro:true,v:{atr:k,un,orig:'calculado',f:q.f,e:q.v===null?'não calculável: '+q.nc:(q.e||'')},s:{},p:{}};
      r.p.atr=[{k:'b',t:k}]; r.s.atr=k; r.p.val=q.v===null?[{k:'mut',t:'não calculável'}]:[{k:'txt',t:prFmt(q.v,2)+' '+un}]; r.s.val=q.v===null?'não calculável':prFmt(q.v,2)+' '+un; r.v.valT=r.s.val;
      if(q.lab!==undefined){ r.p.val=r.p.val.concat([{k:'br'},{k:'mut',t:'laboratório '+prFmtT(q.lab,2)+' '+un}]).concat(q.difere?[{k:'chip',t:'difere do laboratório',c:'yellow'}]:[]); r.s.val+=' laboratório '+q.lab; }
      r.p.met=[{k:'mut',t:q.f}]; r.s.met=q.f; r.p.ld=[{k:'mut',t:'—'}]; r.s.ld=''; r.p.orig=[{k:'mut',t:'calculado'}]; r.s.orig='calculado'; rows.push(r); });
    GR('g_ext').rows=rows;
    const u=self.__uso[l.id]||soloUsoNoPlano(c,SOLO0,l); self.__ul=u;
    GR('g_uso').rows=u.map((x,i)=>{ const r={id:'u'+i,ro:true,v:{},s:{},p:{}}; const cu=x.cu; const sn=(SOLO0.safras[cu.saf]||{}).nome||cu.saf;
      r.p.sp=[{k:'txt',t:sn},{k:'br'},{k:'mut',t:cu.local+' · '+cenNum(Number(cu.area))+' ha'}]; r.s.sp=sn+' '+cu.local;
      if(!x.s){ r.p.item=[{k:'mut',t:x.info}]; r.s.item=x.info; r.p.dose=[{k:'mut',t:'—'}]; r.s.dose=''; r.p.st=[{k:'chip',t:'sem regra: '+cu.cultura,c:'gray'}]; r.s.st='sem regra'; return r; }
      const s=x.s; r.p.item=[{k:'txt',t:s.atv.nome},{k:'br'},{k:'mut',t:s.prod}]; r.s.item=s.atv.nome+' '+s.prod;
      const pd=s.padrao===null||s.padrao===undefined?'—':soloDoseTxt(s.padrao,s.un); r.p.dose=[{k:'txt',t:pd+' → '+soSugTxt(s)}]; r.s.dose=pd+' → '+soSugTxt(s);
      r.v.dif=s.dif||0; r.p.dif=s.dif?[{k:'txt',t:soloQtdTxt(s.dif,s.un,true)}]:[{k:'mut',t:'—'}]; r.s.dif=s.dif?soloQtdTxt(s.dif,s.un,true):'';
      const c0=/^em uso/.test(x.st)?'green':(/^não aplicável/.test(x.st)?'gray':'blue'); r.p.st=[{k:'chip',t:x.st,c:c0}]; r.s.st=x.st; return r; }); }
  else { GR('g_ext').rows=[]; GR('g_uso').rows=[]; }
}
function soLdVals(self,v){ const l=self.__l; v.ld_open=!!l; if(!l) return; const c=cenGet(); const u=self.__ul||[];
  const cor=SOLO_SITC[l.sit]||'gray'; v.ld_titulo=l.id+' · '+l.tal+(l.prof?' · '+l.prof+' cm':' · folha'); v.ld_ct=l.sit+(l.motivo?' · '+l.motivo:''); v.ld_cst=soChs(cor); v.ld_cdot=soDot(cor);
  v.ld_sub=l.lab+' · coleta '+soloBr(l.coleta)+(l.zona?' · '+l.zona:'');
  v.ld_kv=[{l:'Fazenda · talhão',v:l.faz+' · '+soTalTxt(l)},{l:'Profundidade',v:l.prof?l.prof+' cm':'— (folha)'},{l:'Extrator',v:l.ext},{l:'Coleta',v:soloBr(l.coleta)},
    {l:'Validação',v:l.por?(l.por+' em '+soloBr(l.em)):'—'},{l:'Validade para sugerir',v:l.tipo==='solo'?'até '+soloBr(l.val):'—'}];
  v.ld_arq=l.arq||'laudo.pdf'; const nu=soloUsoCont(u); const saf=soSafraDe(u);
  let next='', pa=null, pb=null;
  if(l.sit==='Aguardando validação'){ const ag=g2papel(g2perfil(),'agronomo');   /* revisão A8: sem o papel, nada de primário; a tela diz quem decide (o comando recusa igual) */
    next=(ag?'':'Decisão de '+g2quem('agronomo')+': só o agrônomo valida. ')+'Confira o extraído com o original e valide. O OCR nunca valida.'; if(ag) pb={t:'Validar laudo',go:()=>soValidar(self,l.id)}; }
  else if(l.sit==='Inconsistente') next='Corrija a unidade de '+l.motivo.replace(/ sem unidade$/,'')+' na linha do extraído: o laudo volta a aguardar validação.';
  else if(l.sit==='Validado'&&l.tipo==='folha') next='Laudo foliar: consulta e correção de unidade; sem regra de dose.';
  else if(l.sit==='Validado'&&nu.n){ next=nu.n+(nu.n>1?' sugestões':' sugestão')+' no plano'+(nu.e?' · '+nu.e+' em uso':'')+'. Use no Planejar safra; ignorar não pede motivo.'; pa={t:'Ver no plano',h:soPlanoHref(saf)}; }
  else if(l.sit==='Validado') next=u.filter(x=>!x.s).map(x=>x.info)[0]||(nu.e?nu.e+' em uso no plano.':(l.zona?'Laudo por zona: não sugere dose (taxa variável fora do escopo).':'Sem sugestão: o plano já está na dose indicada ou não há plano no talhão.'));
  else next=l.sit==='Substituído'?'Substituído '+l.motivo+': vale o laudo mais recente do talhão e profundidade.':'Laudo vencido ('+l.motivo+'): continua visível, mas não sugere dose.';
  v.ld_next=next; v.ld_hasNext=!!next;
  v.ld_hasPB=!!pb; v.ld_hasPA=!!pa; v.ld_pt=pb?pb.t:(pa?pa.t:''); v.ld_pgo=pb?pb.go:(()=>{}); v.ld_ph=pa?pa.h:'#'; v.ld_sec=[]; v.ld_closeT='Fechar';
  v.ld_err=self.state.ld_err||''; v.ld_hasErr=!!v.ld_err;
  v.ld_hasExt=true; v.ld_hasUso=l.tipo==='solo'&&u.length>0; v.ld_semUso=l.tipo==='solo'&&!u.length; v.ld_semUsoT='Nenhum cultivo com plano neste talhão'+(l.sit==='Validado'?'.':' ou o laudo ainda não vale para sugerir.');
  v.ld_vinc=(l.id==='LAU-2043'||l.id==='LAU-2044')?[{t:'DIA-007 · nematoide no T4 (diagnóstico do MIP)',h:'AG-03det.dc.html'}]:[]; v.ld_hasVinc=v.ld_vinc.length>0;
  v.ld_close=()=>{ self.setState({lau:null,ld_err:'',pqi:null}); }; v.ld_key=(e)=>{ if(e&&e.key==='Escape'&&!self.state.pqi&&self.state.pqi!==0){ e.preventDefault(); v.ld_close(); } }; }
function soValidar(self,id){ const ch='VAL-'+id+'-'+Date.now(); const r=cenMudar(null,c=>soloValidar(c,id,ch,soAtor()));
  if(r.erro){ self.setState({ld_err:r.erro,g2toast:r.erro}); return; }
  const c=cenGet(); const l=soloLaudos(c,SOLO0).find(x=>x.id===id); const u=l?soloUsoNoPlano(c,SOLO0,l):[]; const n=soloUsoCont(u).n;
  self.setState({cenrev:Date.now(),ld_err:'',g2toast:r.msg+(n?' '+n+(n>1?' sugestões aparecem':' sugestão aparece')+' no Planejar safra.':' Sem sugestão de dose para este talhão.')}); }
/* ---- registrar laudo ---- */
/* faz/tal: contexto herdado (Mapa › Análises de solo, talhão sem análise: AG-02.dc.html#registrar=<fazenda>/<talhão>); visível e corrigível no formulário */
function soRlNovo(self,faz,tal){ const f=(faz&&SOLO_TAL[faz])?faz:soFz(self); const t=(tal&&(SOLO_TAL[f]||[]).some(x=>x[0]===tal))?tal:'';
  self.setState({rl:{chave:'REG-'+Date.now()+'-'+Math.floor(Math.random()*1e4),faz:f,tal:t,tal0:t,prof:'0–20',coleta:'',lab:'',ext:'Mehlich-1',arq:'',an:SO_AN.map(a=>soRlAnalito(a)),err:'',warn:false,orig:''}}); }
function soRlVals(self,v){ const rl=self.state.rl; v.rl_open=!!rl; if(!rl) return;
  const upd=(p)=>self.setState({rl:Object.assign({},self.state.rl,p,{err:'',warn:false})});
  v.rl_titulo='Registrar laudo de solo'; v.rl_sub='O laudo nasce aguardando validação do agrônomo; o OCR nunca valida.';
  const inSt='font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;';
  const pill=(on)=>'font-family:inherit;font-size:13px;font-weight:700;padding:7px 12px;border-radius:999px;cursor:pointer;white-space:nowrap;min-height:40px;border:1px solid '+(on?'#1E7A4C':'#E4E9E5')+';background:'+(on?'#E4F3E9':'#FFFFFF')+';color:'+(on?'#1E6B47':'#15201A')+';';
  v.rl_inst=inSt; v.rl_faz=rl.faz; v.rl_fazs=['Santa Rita','Lagoa Grande','Boa Vista'].map(x=>({v:x,t:x})); v.rl_setfaz=(e)=>upd({faz:e.target.value,tal:''});
  v.rl_tal=rl.tal; v.rl_tals=[{v:'',t:'Escolha o talhão'}].concat((SOLO_TAL[rl.faz]||[]).map(x=>({v:x[0],t:x[0]+' · '+cenNum(x[1])+' ha'}))); v.rl_settal=(e)=>upd({tal:e.target.value});
  v.rl_profs=['0–20','20–40'].map(p=>({t:p+' cm',on:String(rl.prof===p),st:pill(rl.prof===p),go:()=>upd({prof:p})}));
  v.rl_exts=['Mehlich-1','Resina'].map(p=>({t:p,on:String(rl.ext===p),st:pill(rl.ext===p),go:()=>upd({ext:p})}));
  v.rl_coleta=rl.coleta; v.rl_setcol=(e)=>upd({coleta:e.target.value}); const hoje=soloHoje();
  v.rl_atalhos=[['Hoje',hoje],['Ontem',soloMaisDias(hoje,-1)],['Há 5 dias',soloMaisDias(hoje,-5)]].map(a=>({t:a[0],st:pill(rl.coleta===a[1]),on:String(rl.coleta===a[1]),go:()=>upd({coleta:a[1]})}));
  v.rl_lab=rl.lab; v.rl_labs=[{v:'',t:'Escolha o laboratório'}].concat(SOLO0.labs.map(x=>({v:x,t:x}))); v.rl_setlab=(e)=>upd({lab:e.target.value});
  v.rl_arq=rl.arq; v.rl_setarq=(e)=>upd({arq:e.target.value});
  v.rl_ans=rl.an.map((x,i)=>({a:x.a,v:x.v,id:'rl_v'+i,lab:'Valor de '+x.a,ulab:'Unidade de '+x.a,un:x.un,met:(x.a==='P'||x.a==='K')?rl.ext:(x.met||''),metfix:x.a==='P'||x.a==='K',metrot:(x.a==='P'||x.a==='K')?'Extrator do laudo':'Método',ld:x.ld===undefined||x.ld===null?'':String(x.ld),q:x.q||'',mlab:'Método de '+x.a,llab:'Limite de detecção de '+x.a,qlab:'Qualificador de '+x.a,uns:Array.from(new Set(SO_UN[x.a].concat(x.un||[]))).map(u=>({v:u,t:u})),st:inSt+'max-width:130px;text-align:right;',ust:inSt+'max-width:150px;',
    set:(e)=>{ const an=self.state.rl.an.slice(); an[i]=Object.assign({},an[i],{v:e.target.value}); upd({an}); },
    setu:(e)=>{ const an=self.state.rl.an.slice(); an[i]=Object.assign({},an[i],{un:e.target.value}); upd({an}); },
    setm:(e)=>{ const an=self.state.rl.an.slice(); an[i]=Object.assign({},an[i],{met:e.target.value}); upd({an}); },
    setld:(e)=>{ const an=self.state.rl.an.slice(); an[i]=Object.assign({},an[i],{ld:e.target.value}); upd({an}); },
    setq:(e)=>{ const an=self.state.rl.an.slice(); an[i]=Object.assign({},an[i],{q:e.target.value}); upd({an}); }}));
  v.rl_ex=()=>{ const x=SOLO0.exemplo; upd({faz:x.faz,tal:x.tal,prof:x.prof,coleta:x.coleta,lab:x.lab,ext:x.ext,arq:x.arq,an:SO_AN.map(a=>{ const q=x.an.find(z=>z.a===a); return soRlAnalito(a,q); })}); };
  v.rl_err=rl.err||''; v.rl_hasErr=!!rl.err; v.rl_warn=!!rl.warn;
  const sujo=()=>{ const r=self.state.rl; return !!((r.tal&&r.tal!==r.tal0)||r.coleta||r.lab||r.arq||r.an.some(x=>x.v||x.met||x.ld||x.q)); };   /* o talhão herdado do Mapa não conta como alteração */
  v.rl_close=()=>{ if(sujo()&&!self.state.rl.warn){ self.setState({rl:Object.assign({},self.state.rl,{warn:true})}); return; } self.setState({rl:null}); };
  v.rl_discard=()=>self.setState({rl:null}); v.rl_keep=()=>self.setState({rl:Object.assign({},self.state.rl,{warn:false})});
  v.rl_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.rl_close(); } };
  v.rl_closeT='Cancelar'; v.rl_sec=[]; v.rl_hasPB=true; v.rl_hasPA=false; v.rl_ph='#'; v.rl_pt='Registrar laudo';
  v.rl_pgo=()=>{ const r=self.state.rl; const area=((SOLO_TAL[r.faz]||[]).find(x=>x[0]===r.tal)||[])[1]||'';
    const erro=soRlErroAnalitos(r.an); if(erro){ self.setState({rl:Object.assign({},r,{err:erro})}); return; }
    const d={faz:r.faz,tal:r.tal,prof:r.prof,coleta:r.coleta,lab:r.lab,ext:r.ext,arq:r.arq,area,an:soRlEnviarAnalitos(r.an,r.ext)};
    const res=cenMudar(null,c=>soloRegistrar(c,d,r.chave,soAtor()));
    if(res.erro){ self.setState({rl:Object.assign({},self.state.rl,{err:res.erro})}); return; }
    self.setState({rl:null,lau:res.id,cenrev:Date.now(),g2toast:res.msg}); }; }
'''

def _painel_laudo(g_ext,g_uso):
    kv=(f'<div class="so-kv" style="padding: 10px 12px; background: {BG}; border-radius: 12px;"><sc-for list="{H("ld_kv")}" as="x" hint-placeholder-count="6"><div style="min-width: 0;">'
        f'<div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div>'
        f'<div style="font-size: 13px; font-weight: 600; margin-top: 2px; overflow-wrap: anywhere;">{H("x.v")}</div></div></sc-for></div>')
    orig=(f'<div style="border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px; background: {BG};">{LAB("Original · PDF do laboratório")}'
          f'<div style="height: 180px; margin-top: 8px; background: {BG}; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; color: {MUTED}; font-size: 12.5px; text-align: center; padding: 8px;">{icon("doc",20,MUTED)}<span>{H("ld_arq")}</span><span>o original não muda; a correção vale no extraído</span></div></div>')
    corpo=(_cabeca('ld_')
           + f'<sc-if value="{H("ld_hasNext")}" hint-placeholder-val="{F()}"><div role="note" style="display: flex; flex-direction: column; gap: 3px; padding: 10px 12px; border-radius: 12px; background: {ACCS};">{LAB("Próximo passo")}<div style="font-size: 13.5px; line-height: 1.45; font-weight: 600;">{H("ld_next")}</div></div></sc-if>'
           + f'<sc-if value="{H("ld_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("ld_err")}</div></sc-if>'
           + kv
           + f'<div class="so-lado"><div class="so-orig-d">{orig}</div><div style="min-width: 0; display: flex; flex-direction: column; gap: 6px;">{LAB("Extraído · valores e índices")}'
             f'<div style="font-size: 12.5px; color: {MUTED};">Clique na linha para corrigir valor ou unidade; os índices calculados mostram a fórmula e as entradas.</div>{g_ext}</div>'
             f'<details class="so-orig-m" style="border: 1px solid {LINE}; border-radius: 12px; padding: 8px 12px;"><summary class="g2seta-nome" style="cursor: pointer; font-weight: 700; font-size: 13px; min-height: 32px;">{E.seta()}Ver original</summary>{orig}</details></div>'
           + f'<sc-if value="{H("ld_hasUso")}" hint-placeholder-val="{F()}"><section aria-label="Uso no plano" style="display: flex; flex-direction: column; gap: 6px;">{LAB("Uso no plano")}'
             f'<div style="font-size: 12.5px; color: {MUTED};">Clique na linha para ver o porquê. Usar a sugestão é no Planejar safra.</div>{g_uso}</section></sc-if>'
           + f'<sc-if value="{H("ld_semUso")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {MUTED};">{H("ld_semUsoT")}</div></sc-if>'
           + f'<sc-if value="{H("ld_hasVinc")}" hint-placeholder-val="{F()}"><section aria-label="Registros vinculados" style="display: flex; flex-direction: column; gap: 4px;">{LAB("Registros vinculados")}'
             f'<sc-for list="{H("ld_vinc")}" as="q" hint-placeholder-count="1"><a href="{H("q.h")}" style="color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px;">{H("q.t")} ›</a></sc-for></section></sc-if>'
           + f'<div style="flex-grow: 1;"></div>' + _rodape('ld_'))
    return _overlay('ld_',1000,corpo,55)   # abaixo dos formulários G2 (z 60) das grades que ele contém; o Por quê fica acima (z 70)

def _painel_registro():
    pills=lambda hole: (f'<div role="group" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H(hole)}" as="o" hint-placeholder-count="2">'
                        f'<button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></div>')
    campo=lambda lbl,fid,inner: f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="{fid}" style="font-size: 12px; font-weight: 700; color: {MUTED};">{lbl}</label>{inner}</div>'
    sel=lambda fid,val,lst,fn: f'<select id="{fid}" value="{H(val)}" onChange="{H(fn)}" style="{H("rl_inst")}"><sc-for list="{H(lst)}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
    linha=(f'<div style="padding: 6px 0; border-top: 1px solid {LINE};">'
           f'<div style="display: grid; grid-template-columns: 48px minmax(0,1fr) minmax(0,1fr); gap: 8px; align-items: center;">'
           f'<b style="font-size: 13px;">{H("x.a")}</b><input id="{H("x.id")}" aria-label="{H("x.lab")}" inputMode="decimal" autoComplete="off" value="{H("x.v")}" onChange="{H("x.set")}" style="{H("x.st")}">'
           f'<select aria-label="{H("x.ulab")}" value="{H("x.un")}" onChange="{H("x.setu")}" style="{H("x.ust")}"><sc-for list="{H("x.uns")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></div>'
           f'<details style="margin-top:4px;"><summary class="so-met-summary" style="cursor:pointer;font-size:12px;">Método e limites · {H("x.a")}</summary>'
           f'<div style="display:flex;flex-direction:column;gap:6px;padding:6px 0;">'
           f'<label class="so-met-label">{H("x.metrot")}<input aria-label="{H("x.mlab")}" readOnly="{H("x.metfix")}" placeholder="Conforme o laudo" value="{H("x.met")}" onChange="{H("x.setm")}" style="{H("rl_inst")}"></label>'
           f'<label class="so-met-label">Limite de detecção<input aria-label="{H("x.llab")}" placeholder="Conforme o laudo" value="{H("x.ld")}" onChange="{H("x.setld")}" style="{H("rl_inst")}"></label>'
           f'<label class="so-met-label">Qualificador<select aria-label="{H("x.qlab")}" value="{H("x.q")}" onChange="{H("x.setq")}" style="{H("rl_inst")}"><option value="">Valor medido</option><option value="&lt;">Abaixo do limite de detecção (&lt;)</option></select></label></div></details></div>')
    corpo=(_cabeca('rl_',chip=False)
           + f'<div style="display: flex;"><button type="button" onClick="{H("rl_ex")}" style="{_MINI}">Preencher com o laudo de exemplo</button></div>'
           + campo('Fazenda','rl_faz',sel('rl_faz','rl_faz','rl_fazs','rl_setfaz'))
           + campo('Talhão','rl_tal',sel('rl_tal','rl_tal','rl_tals','rl_settal'))
           + f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 700; color: {MUTED};">Profundidade</span>{pills("rl_profs")}</div>'
           + campo('Coleta','rl_col',f'<input id="rl_col" type="date" value="{H("rl_coleta")}" onChange="{H("rl_setcol")}" style="{H("rl_inst")} max-width: 200px;">'+pills('rl_atalhos'))
           + campo('Laboratório','rl_lab',sel('rl_lab','rl_lab','rl_labs','rl_setlab'))
           + f'<div style="display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 12px; font-weight: 700; color: {MUTED};">Extrator de P e K</span>{pills("rl_exts")}</div>'
           + campo('Arquivo do laudo (PDF)','rl_arq',f'<input id="rl_arq" placeholder="laudo.pdf" value="{H("rl_arq")}" onChange="{H("rl_setarq")}" style="{H("rl_inst")}">')
           + f'<section aria-label="Valores do laudo" style="display: flex; flex-direction: column; gap: 2px;">{LAB("Valores do laudo")}<sc-for list="{H("rl_ans")}" as="x" hint-placeholder-count="6">{linha}</sc-for></section>'
           + f'<sc-if value="{H("rl_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("rl_err")}</div></sc-if>'
           + f'<sc-if value="{H("rl_warn")}" hint-placeholder-val="{F()}"><div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("rl_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("rl_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
           + f'<div style="flex-grow: 1;"></div>' + _rodape('rl_'))
    return _overlay('rl_',560,corpo)

def build():
    fname='AG-02.dc.html'; E._reset_screen(fname)
    g_lau=grid([dict(k='lau',l='Laudo',w=120),dict(k='tal',l='Fazenda · talhão',w=170),dict(k='prof',l='Profundidade',w=110),dict(k='coleta',l='Coleta',t='num',w=110),
                *[dict(k='V',l='V %',t='num',a='r',w=120) if i['k']=='V' else (dict(k='K',l='K',t='num',a='r',w=140) if i['k']=='K' else dict(k=_ik(i),l=i['l'],t='num',a='r',w=100)) for i in DS.IND],
                dict(k='sit',l='Situação',w=190),dict(k='plano',l='No plano',w=170)],[],
               edit=dict(m='pick'),gid='g_lau',total=False,so=dict(k='coleta',d=True),qf=dict(k='sit',l='situação',todas='Todos'))
    g_agua=grid([dict(k='med',l='Medição',w=100),dict(k='tal',l='Talhão · zona',w=120),dict(k='data',l='Data',t='num',w=110),dict(k='prof',l='Profundidade',w=150),
                 dict(k='met',l='Método',w=200),dict(k='cc',l='Capacidade de campo',t='num',a='r',w=140),dict(k='pmp',l='Ponto de murcha',t='num',a='r',w=130),
                 dict(k='cad',l='CAD',t='num',a='r',w=130),dict(k='fonte',l='Fonte · responsável',w=170)],[],
                edit=dict(m='form',title='Medição de água no solo',newTitle='Registrar medição de água no solo',
                          sub='Propriedade do solo por talhão ou zona. A CAD é referência para a Irrigação; não é a lâmina, que segue a política de água e o responsável técnico.',
                          fields=[dict(k='faz',l='Fazenda',t='sel',opts=['Santa Rita','Lagoa Grande','Boa Vista'],req=True,**{'def':'Santa Rita'}),
                                  dict(k='talv',l='Talhão',t='sel',dyn=True,opts=[],req=True),dict(k='zona',l='Zona (opcional)',t='txt',help='Ex.: Z1 (baixada). Vazio = talhão inteiro.'),
                                  dict(k='datav',l='Data da medição',t='date',req=True),dict(k='profv',l='Profundidade amostrada',t='sel',opts=['0–20','0–30','0–40','20–40'],req=True,u='cm'),
                                  dict(k='z',l='Profundidade efetiva das raízes',t='num',req=True,min=1,max=200,u='cm'),
                                  dict(k='metv',l='Método',t='sel',opts=DS.METODOS_AGUA,req=True),dict(k='un',l='Unidade',t='sel',opts=DS.UN_AGUA,req=True,**{'def':'% volume'}),
                                  dict(k='ccv',l='Capacidade de campo (CC)',t='num',req=True,min=0,max=100),dict(k='pmpv',l='Ponto de murcha permanente (PMP)',t='num',min=0,max=100,help='Sem PMP medido, a CAD fica "não calculável".'),
                                  dict(k='fontev',l='Fonte ou laboratório',t='sel',opts=DS.LABS+['Equipe da fazenda'],req=True),dict(k='resp',l='Responsável',t='sel',opts=DS.RESP_AGUA,req=True,**{'def':'Ana (agrônoma)'}),
                                  dict(k='cadT',l='Água disponível (CAD)',ro=True,live=True,help='CAD = (CC − PMP) × profundidade efetiva; unidades explícitas.')]),
                add='Registrar medição',gid='g_agua',total=False,so=dict(k='data',d=True))
    g_ext=grid([dict(k='atr',l='Atributo',w=70),dict(k='val',l='Valor',w=150),dict(k='met',l='Método · extrator',w=140),dict(k='ld',l='Qualificador · LD',w=90),dict(k='orig',l='Origem',w=90)],[],
               edit=dict(m='form',title='Valor do laudo',sub='Corrija o valor ou a unidade lidos do PDF; o original não muda e o laudo volta à validação do agrônomo.',
                         fields=[dict(k='atr',l='Atributo',ro=True),dict(k='orig',l='',t='txt',cond=dict(k='orig',eq='__nunca')),
                                 dict(k='val',l='Valor',t='num',req=True,min=0,cond=dict(k='orig',eq='medido')),
                                 dict(k='un',l='Unidade',t='sel',opts=['','cmolc/dm³','mmolc/dm³','mg/dm³','g/kg','mg/kg','%'],req=True,cond=dict(k='orig',eq='medido')),
                                 dict(k='valT',l='Valor calculado',ro=True,cond=dict(k='orig',eq='calculado')),dict(k='f',l='Fórmula',ro=True,cond=dict(k='orig',eq='calculado')),
                                 dict(k='e',l='Entradas',ro=True,cond=dict(k='orig',eq='calculado'))]),
               gid='g_ext',total=False,search=True)
    g_uso=grid([dict(k='sp',l='Safra · talhão',w=150),dict(k='item',l='Atividade · produto',w=170),dict(k='dose',l='Padrão → sugestão',w=190),dict(k='dif',l='No talhão',t='num',a='r',w=120),
                dict(k='st',l='Estado',w=210)],[],edit=dict(m='pick'),gid='g_uso',total=False,search=True)
    talf={f:[[t,ha] for t,ha in lst] for f,lst in OCEN.talhoes().items()}
    EXTRAJS[0]=(cenario.js_prefixo()+DS.js_prefixo()+'const SOLO_TAL='+json.dumps(talf,ensure_ascii=False)+';\n'+SOLO_UI_JS+JS+r'''
function EXTRAVALS(self,v){ try{ window.__soloSelf=self; window.__solo={get:()=>cenGet().solo||{},cen:()=>cenGet(),exemplo:()=>cenClone(SOLO0.exemplo),salvar:(c)=>{ cenSave(c); self.setState({cenrev:Date.now()}); },registrar:(d,ch,a)=>cenMudar(null,c=>soloRegistrar(c,d,ch,a||'Ana')),validar:(id,ch,a)=>cenMudar(null,c=>soloValidar(c,id,ch,a||'Ana'))}; }catch(e){}
  const c=cenGet(); const ls=self.__ls||[];
  const nI=ls.filter(l=>l.sit==='Inconsistente'&&soFazOk(self,l.faz)).length, nA=ls.filter(l=>l.sit==='Aguardando validação'&&soFazOk(self,l.faz)).length;
  v.st_t=(nI||nA)?[nI?nI+(nI>1?' inconsistentes':' inconsistente'):'',nA?nA+' aguardando validação':''].filter(Boolean).join(' · '):'Laudos em dia'; const sc=nI?'red':(nA?'yellow':'green'); v.st_st=soChs(sc); v.st_dot=soDot(sc);
  v.prim_t='Registrar laudo'; v.prim_go=()=>soRlNovo(self);
  soLdVals(self,v); soRlVals(self,v);
  /* Por quê (da linha do Uso no plano) */
  const u=self.__ul||[]; const pi=self.state.pqi; const x=(pi!==null&&pi!==undefined)?u[pi]:null;
  soloPqVals(self,v,x&&x.s?x.s:null,{cu:x?x.cu:null,prim:null,ver:'',fechar:()=>self.setState({pqi:null})});
  if(x&&x.s){ const saf=x.cu.saf; v.pq_sec=[]; v.pq_hasPA=!x.s.nega; v.pq_ph=soPlanoHref(saf); v.pq_pt='Ver no plano'; v.pq_hasPB=false; }
  self.g2pick=(gid,rid)=>{ if(gid==='g_lau'){ self.__pqFoco=''; self.setState({lau:rid,ld_err:'',pqi:null}); }
    if(gid==='g_uso'){ const i=Number(String(rid).slice(1)); if((self.__ul||[])[i]&&self.__ul[i].s){ self.__pqFoco='ld_x'; self.setState({pqi:i}); } } };
  /* correção de valor ou unidade (extraído) */
  self.g2after=(gid,rows,r,isNew)=>{
    if(gid==='g_ext'&&r&&self.__l){ const l=self.__l; const a=r.v.atr; const x0=l.an.find(q=>q.a===a); g2set(self,'g_ext',{rows:null});
      if(!x0||(Number(x0.v)===Number(r.v.val)&&(x0.un||'')===(r.v.un||''))){ self.setState({g2toast:'Nada mudou em '+a+'.'}); return; }
      if(!r.v.un){ self.setState({g2toast:'Informe a unidade de '+a+'.'}); return; }
      const res=cenMudar(null,cc=>soloCorrigir(cc,l.id,a,r.v.val,r.v.un,'COR-'+l.id+'-'+Date.now(),soAtor()));
      self.setState({cenrev:Date.now(),g2toast:res.erro||res.msg}); }
    if(gid==='g_agua'&&r){ g2set(self,'g_agua',{rows:null}); const d=soAgDados(r.v); const ch=self.__agK||('AGS-'+Date.now()); self.__agK=null;
      const res=cenMudar(null,cc=>soloMedir(cc,d,ch,soAtor())); self.setState({cenrev:Date.now(),g2toast:res.erro||(res.repetido?res.msg:res.msg+' A lâmina segue a política de água e o responsável técnico.')}); } };
  self.g2check=(gid,rows,r,d,isNew)=>{ if(gid==='g_ext'){ if(d.orig==='medido'&&!d.un) return {un:'Escolha a unidade: sem unidade o laudo fica inconsistente.'}; return {}; }
    if(gid!=='g_agua') return {}; if(!self.__agK) self.__agK='AGS-'+Date.now(); const k=cenClone(cenGet()); try{ soloMedir(k,soAgDados(d),'PREVIA-'+Date.now(),soAtor()); return {}; }
    catch(e){ const m=String(e.message||e); const f=/capacidade de campo/.test(m)?'ccv':(/ponto de murcha|Ponto de murcha/.test(m)?'pmpv':(/profundidade efetiva/.test(m)?'z':(/data|depois de hoje/i.test(m)?'datav':(/já está registrada/.test(m)?'datav':'talv')))); const o={}; o[f]=m.replace(' Nada foi gravado.',''); return o; } };
  self.g2opts=(gid,k,d)=>{ if(gid==='g_agua'&&k==='talv') return [{v:'',t:'Escolha o talhão'}].concat((SOLO_TAL[d.faz||'Santa Rita']||[]).map(x=>({v:x[0],t:x[0]+' · '+cenNum(x[1])+' ha'}))); return null; };
  self.g2live=(gid,k,d)=>{ if(gid==='g_agua'&&k==='cadT'){ const cad=soloCAD({cc:d.ccv,pmp:d.pmpv,z:d.z,un:d.un}); return cad.v===null?'não calculável: '+cad.nc:cad.e; } return null; };
  /* abrir pelo endereço: AG-02.dc.html#LAU-2061 (laudo) · AG-02.dc.html#registrar=Santa Rita/T3 (Registrar laudo com fazenda e talhão, vindo do Mapa) ·
     AG-02.dc.html#registrar=Lagoa Grande (ícone Importar laudo do Mapa › Solo sem talhão escolhido: só a fazenda vem preenchida) */
  if(!self.__hashIni){ self.__hashIni=1; const ab=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||'').replace('#',''); }catch(e){} if(/^LAU-\d+$/.test(h)) setTimeout(()=>self.setState({lau:h,mf_faz:'Todas'}),0);
      const m=/^registrar=([^/]+)(?:\/(.+))?$/.exec(h); if(m) setTimeout(()=>{ self.setState({lau:null,mf_faz:'Todas'}); soRlNovo(self,m[1],m[2]||''); },0); }; ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} } }
function soAgDados(x){ return {faz:x.faz,tal:x.talv,zona:x.zona||'',data:x.datav,prof:x.profv,z:x.z,met:x.metv,un:x.un,cc:x.ccv,pmp:x.pmpv,fonte:x.fontev,resp:x.resp}; }
''')
    EXTRA.append('<style>'+CSS+'</style>')
    EXTRA.append(_painel_laudo(g_ext,g_uso)); EXTRA.append(_painel_registro()); EXTRA.append(porque_html())
    corpo=(bloco('Laudos','Clique no laudo para conferir valores e índices, validar e ver o uso no plano.',g_lau)
           + bloco('Água no solo','Registre capacidade de campo e ponto de murcha por talhão; a CAD é referência para a Irrigação, não a lâmina.',g_agua))
    HEIGHTS37[fname]=1100
    prim=f'<button type="button" class="pr-prim" onClick="{H("prim_go")}" style="{BTN_ST(True)}">{H("prim_t")}</button>'
    shell37('AG-02','Análises de solo',corpo,fname=fname,subtitle='Laudos e água no solo por talhão. O que a análise indica entra como sugestão nas doses do plano.',
            status=(H('st_t'),'yellow'),primary_html=prim,search=False,
            footer='Sem laudo vale a dose do plano. O OCR nunca valida; só o agrônomo valida. Regra de demonstração: tabela regional a decidir pelo proprietário.')
    import os
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H('st_t'),'yellow')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H("st_st")}"><span style="{H("st_dot")}"></span>{H("st_t")}</span>'))


