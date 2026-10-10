# -*- coding: utf-8 -*-
"""Irrigação (menu Agrícola › Irrigação) — processo em 4 telas ligadas pela faixa de etapas, todas lendo o MESMO estado gravado
(dados_irrigacao.py + irrigacao_estado.js, localStorage 'talhao-os-irrigacao-v1') que a camada Irrigação do Mapa (IN-04):
IR-01 Irrigação (setores: necessidade e situação) › IR-02 Programação (agenda por captação) › IR-03 Ordens (+ IR-03det, detalhe de
qualquer ordem pelo hash #OS-xxxx[:janela|:conflito|:termino|:conferir]) › IR-04 Clima e sensores (fontes e outorgas).

Regras (decisões do proprietário, 26/09 e 01/10; PRD cap. 63, CAL-09, AGUA-01..08):
- Água sem produto não passa pelo agrônomo: a necessidade vem do balanço e a ordem é liberada pela prontidão (janela definida, bomba livre,
  sem parada do PCM, dentro da outorga), com recibo. Ponta de energia, intervalo curto, sonda e outorga em renovação são só avisos.
- Acima do limite por passada a lâmina vira passadas iguais; sonda suspeita ou sem dado = estimativa por ET (≈), sem bloquear.
- Término físico → Em conferência; hidrômetro × estimativa na área coberta: até 3 % encerra sozinho; acima ou sem leitura, a pessoa confere.
  O balanço recebe a irrigação líquida uma vez por passada, só pelo volume medido. Passagem parcial = crédito só na faixa coberta (o déficit
  do pivô fica com a área não coberta) até as parciais da mesma ordem completarem a volta (v1 + saldo da v2).
- Adicionar produtos cria a v2 da mesma ordem (fertirrigação), que o agrônomo libera na O.S. (OS.dc.html, cenário compartilhado): só com a
  janela pronta (bomba, parada e outorga); a janela da v2 segura a bomba; depois da liberação a ordem segue a etapa e o passo da O.S., e a
  água apontada na O.S. entra no balanço. Em execução, a passada para na área coberta (v1) e o saldo vai para a v2.
- Fertirrigação parada na O.S. (falta de insumo, bomba): mesma situação e dono da O.S.; a água do setor pode ir sem o produto.
- "Restaurar demonstração" do cenário da O.S. volta a irrigação à semente. Links diretos #OS-xxxx:acao só abrem o painel quando valem.
- Ordens só de água vivem só aqui (fora de OS.dc.html). Fertirrigações aparecem em leitura, com a etapa do cenário da O.S.
- Fazenda: filtro do topo (Santa Rita · Lagoa Grande · Todas), lembrado na sessão; abre na fazenda vinda do Mapa.
IDs de requisito ficam fora da interface."""
import json
from engine import (grid,section,esc,icon,chip,btn,Pt,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,
                    BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, HEIGHTS37, PARENT37, MACRO, secoes_nav, secao_item
import cenario
import dados_irrigacao as DI
from areas.cadastros import ncol_dinamico

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
for _f in ('IR-01.dc.html','IR-02.dc.html','IR-03.dc.html','IR-04.dc.html'): MACRO[_f]=dict(faz='filtro')
for _f in ('IR-02.dc.html','IR-03.dc.html','IR-04.dc.html'): PARENT37[_f]='IR-01.dc.html'
PARENT37['IR-03det.dc.html']='IR-03.dc.html'

# ---------------- telas da Irrigação: navegação entre telas irmãs, com a pendência de cada uma calculada do estado ----------------
# UX-ACAO-UNICA-20261003: as quatro telas são trabalho paralelo (qualquer ordem), não etapas de um processo guiado: a faixa é a
# navegação entre elas (único caminho; IR-02…04 não estão no menu), sem número de etapa e sem setas ‹ ›; a pendência fica escrita.
ETAPAS=[('Confira a necessidade','IR-01.dc.html'),('Programe a irrigação','IR-02.dc.html'),('Execute e confira','IR-03.dc.html'),('Acompanhe clima e sensores','IR-04.dc.html')]
def faixa(cur):
    itens=''.join(secao_item(t,i==cur,href=h,why_hole=f'st{i}') for i,(t,h) in enumerate(ETAPAS,1))
    return secoes_nav(itens,len(ETAPAS),cur,ETAPAS[cur-1][0],'Telas da irrigação')

def ic(name,size=15):
    P={'play':'M8 5v14l11-7z','pause':'M7 5h3v14H7zM14 5h3v14h-3z','plus':'M12 5v14M5 12h14','flag':'M5 21V4h11l-2 4 2 4H5','gauge':'M12 14l4-5M3 14a9 9 0 1 1 18 0'}
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{P[name]}"/></svg>')
_IST='display: inline-flex; align-items: center; gap: 6px; text-decoration: none; '
def sbtn(show,text_hole,fn,ico,title):
    """ação secundária da seção, só quando vale no estado (sem botão inválido)."""
    return (f'<sc-if value="{H(show)}" hint-placeholder-val="{F()}"><button type="button" onClick="{H(fn)}" title="{esc(title)}" style="{_IST}{BTN_ST(False,True)}">{ic(ico)}{text_hole}</button></sc-if>')

def R(id,ro=False,o=None,**cells):
    v={}; s={}; p={}
    for k,c in cells.items():
        if isinstance(c,tuple): v[k]=c[0]; p[k]=c[1]; s[k]=' '.join(x.get('t','') for x in c[1] if x.get('k')!='br')
        elif isinstance(c,list): p[k]=c; s[k]=' '.join(x.get('t','') for x in c if x.get('k')!='br')
        else: v[k]=c
    d=dict(id=id,v=v,s=s,p=p)
    if ro: d['ro']=True
    if o: d['o']=[dict(t=t) if isinstance(t,str) else t for t in o]
    return d

# painel lateral (processo): título, subtítulo, corpo, rodapé
def painel(pre,corpo,rodape,w=480):
    return (f'<sc-if value="{H(pre+"_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
            f'<button type="button" aria-label="Fechar" onClick="{H(pre+"_cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
            f'<aside role="dialog" aria-modal="true" tabindex="-1" data-painel="{pre}" aria-label="{H(pre+"_titulo")}" style="position: relative; width: {w}px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
            f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H(pre+"_titulo")}</h2>'
            f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(pre+"_cancel")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
            f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">{H(pre+"_sub")}</div>{corpo}<div style="flex-grow: 1;"></div>'
            f'<sc-if value="{H(pre+"_warn")}" hint-placeholder-val="{F()}"><div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
            f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H(pre+"_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H(pre+"_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
            f'<div class="pe-form" style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">{rodape}</div></aside></div></sc-if>')
def campo(lbl,fid,inner,err_pre):
    return (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="{fid}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{lbl}</label>{inner}'
            f'<sc-if value="{H(err_pre+"_has")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H(err_pre)}</span></sc-if></div>')
INP='font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; box-sizing: border-box; width: 100%; border: 1px solid '+LINE+'; background: #fff; color: '+INK+';'
def kvfor(hole,cols=3):
    """pares rótulo/valor calculados no cliente ({{hole}} = [{l,t}])."""
    return (f'<div style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: 10px 18px;">'
            f'<sc-for list="{H(hole)}" as="k" hint-placeholder-count="6"><div style="display: flex; flex-direction: column; gap: 2px; min-width: 0;">'
            f'<span style="font-size: 11px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("k.l")}</span>'
            f'<span style="font-size: 13.5px; font-weight: 600; overflow-wrap: anywhere;">{H("k.t")}</span></div></sc-for></div>')
def chipsfor(hole):
    return (f'<div style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H(hole)}" as="a" hint-placeholder-count="0"><span style="{H("a.st")}">{H("a.t")}</span></sc-for></div>')
def checks(hole):
    return (f'<div role="list" style="display: flex; flex-direction: column; gap: 4px;"><sc-for list="{H(hole)}" as="ck" hint-placeholder-count="0">'
            f'<div role="listitem" style="{H("ck.st")}">{H("ck.t")}</div></sc-for></div>')
def vazio(hole_show,texto_hole,link_t,link_h):
    return (f'<sc-if value="{H(hole_show)}" hint-placeholder-val="{F()}"><div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; padding: 28px; display: flex; align-items: center; gap: 14px;">'
            f'<span style="font-size: 14px; font-weight: 600;">{H(texto_hole)}</span><a href="{link_h}" style="{BTN_ST(False,True)} text-decoration: none;">{esc(link_t)}</a></div></sc-if>')
def prefixo(): return cenario.js_prefixo()+DI.js_prefixo()
def _corrige(fname,trocas):
    p=E.P+'/'+fname; t=open(p,encoding='utf-8').read()
    for a,b in trocas:
        assert a in t, ('trecho não encontrado em '+fname,a[:80]); t=t.replace(a,b)
    open(p,'w',encoding='utf-8').write(t)

JS_COMUM=r'''
function IRG(id){ return GRIDS.find(g=>g.id===id); }
const G2CC={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],blue:['#1E5F8F','#E3F0FB']};
function chipSt(c){ const cc=G2CC[c]||G2CC.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:4px 11px;border-radius:999px;font-size:12.5px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; }
function tagSt(){ return 'display:inline-flex;align-items:center;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:600;color:#65736A;border:1px solid #E4E9E5;white-space:nowrap;'; }
const PRIM='display:inline-flex;align-items:center;gap:6px;padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;text-decoration:none;background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;';
const SEC='display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:10px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;text-decoration:none;background:#fff;color:#15201A;border:1px solid #E4E9E5;';
// cor da situação do setor (mesmos códigos da camada Irrigação do Mapa) → chip
const SITC={red:'red',yellow:'yellow',blue:'blue',lime:'green',ok:'green',cloud:'gray',gray:'gray'};
const FAZK={'Santa Rita':'SR','Lagoa Grande':'LG'};
// fazenda do topo: a última escolhida, aqui ou no Mapa (vale a mudança mais recente); senão Santa Rita
function irrMapaFaz(){ try{ const m=JSON.parse(sessionStorage.getItem('mapa-ctx')||'null'); return (m&&m.mf_faz)||''; }catch(e){ return ''; } }
function irrFazNome(self){ const f=self.state.irrfaz; if(f) return f; let raw=null, r=null; try{ raw=sessionStorage.getItem('irr-faz'); }catch(e){}
  if(raw){ try{ r=JSON.parse(raw); }catch(e){ r=null; } if(!r||typeof r!=='object') r={f:raw}; }
  const m=irrMapaFaz(); if(r&&r.f&&(r.m===undefined||!m||r.m===m)) return r.f;   // o Mapa não mudou de fazenda depois da escolha feita aqui
  return m||'Santa Rita'; }
function irrFazK(self){ const f=irrFazNome(self); return f==='Todas'?null:(FAZK[f]||'BV'); }
function irrFazSet(self,f,msg){ let m=irrMapaFaz();
  if(f==='Santa Rita'||f==='Lagoa Grande'){ try{ const c=JSON.parse(sessionStorage.getItem('mapa-ctx')||'null')||{}; if(c.mf_faz!==f){ c.mf_faz=f; c.tsel=[]; c.osel={}; c.px=null; sessionStorage.setItem('mapa-ctx',JSON.stringify(c)); } m=f; }catch(e){} }
  try{ sessionStorage.setItem('irr-faz',JSON.stringify({f,m})); }catch(e){} self.setState({irrfaz:f,g2toast:msg===undefined?'Fazenda: '+f:msg}); }
// painéis de processo: o foco entra ao abrir, Esc fecha de qualquer ponto da tela e o foco volta ao botão de origem
function irrPaineis(self,ps){ self.__pn=self.__pn||{}; const ab=ps.find(z=>z[1]); self.__esc=ab?ab[2]:null;
  if(!self.__escOuvindo){ self.__escOuvindo=true; try{ document.addEventListener('keydown',(e)=>{ if(e.key==='Escape'&&self.__esc){ e.preventDefault(); self.__esc(); } }); }catch(e){} }
  ps.forEach(z=>{ const k=z[0], on=!!z[1], era=!!self.__pn[k]; self.__pn[k]=on;
    if(on&&!era){ try{ const a=document.activeElement; if(a&&!(a.closest&&a.closest('aside[role=dialog]'))) self.__ret=a; }catch(e){}
      setTimeout(()=>{ try{ const a=document.querySelector('aside[data-painel="'+k+'"]'); if(!a||a.contains(document.activeElement)) return;
        const f=a.querySelector('input:not([type=radio]),select,textarea,input[type=radio]:checked,input[type=radio],button:not([aria-label="Fechar"])')||a; f.focus(); }catch(e){} },60); }
    if(!on&&era&&!ps.some(y=>y[1])){ const r=self.__ret; setTimeout(()=>{ try{ if(r&&document.body.contains(r)&&!document.querySelector('aside[role=dialog]')) r.focus(); }catch(e){} },40); } }); }
// filtro rápido, busca, filtros e ordem da grade lembrados na sessão (voltar do registro não perde o recorte)
function irrVista(self,gid){ const k='irr-vista-'+location.pathname.split('/').pop()+'-'+gid; const st=g2st(self,gid); const cur=JSON.stringify({qv:st.qv||'',q:st.q||'',f:st.f||{},so:st.so||null});
  if(!self.__vista) self.__vista={}; if(self.__vista[gid]===undefined){ self.__vista[gid]=cur; let sv=null; try{ sv=JSON.parse(sessionStorage.getItem(k)||'null'); }catch(e){ sv=null; }
    if(sv&&JSON.stringify(sv)!==cur){ self.__vista[gid]=JSON.stringify(sv); setTimeout(()=>g2set(self,gid,{qv:sv.qv||'',q:sv.q||'',f:sv.f||{},so:sv.so||undefined}),0); } return; }
  if(cur!==self.__vista[gid]){ self.__vista[gid]=cur; try{ sessionStorage.setItem(k,cur); }catch(e){} } }
function irrFazVals(self,v){ v.mf_faz=irrFazNome(self); v.mf_setfaz=(e)=>irrFazSet(self,e.target.value); }
function irrFazDe(self,fz){ const nome=fz==='LG'?'Lagoa Grande':'Santa Rita'; const cur=irrFazNome(self); if(cur!=='Todas'&&cur!==nome) irrFazSet(self,nome,''); }
function irrFaixa(v,s,fz){ const c=irrContagem(s,fz);
  const W={1:c.aprog?c.aprog+' a programar':'',2:[c.conf?c.conf+(c.conf>1?' conflitos':' conflito'):'',c.jan?c.jan+(c.jan>1?' janelas a definir':' janela a definir'):''].filter(Boolean).join(' · '),3:c.confer?c.confer+' a conferir':'',4:c.sensT};
  for(let i=1;i<=4;i++){ v['st'+i+'_why']=W[i]||''; v['st'+i+'_has']=!!W[i];
    v['st'+i+'_bst']='width:22px;height:22px;border-radius:999px;display:inline-flex;align-items:center;justify-content:center;font-size:11.5px;font-weight:800;flex-shrink:0;'+(W[i]?'background:#FDE8E6;color:#B42318;':'background:#EEF1EE;color:#15201A;'); }
  return c; }
// hash da tela (#P2, #programar=PV02, #OS-0423:conflito): lido na abertura e a cada troca
function irrHash(){ try{ return decodeURIComponent((location.hash||'').replace(/^#/,'')); }catch(e){ return ''; } }
function irrHashOuvir(self,fn){ if(self.__hashOuvindo) return; self.__hashOuvindo=true; setTimeout(()=>fn(irrHash()),0);
  try{ window.addEventListener('hashchange',()=>fn(irrHash())); }catch(e){} }
function irrGo(h){ try{ location.href=h; }catch(e){} }
function nfx(n,d){ return irrN(n,d); }
// TABELAS-FOCO (proprietário, 04/10/2026): uma variável por coluna. Instante que ordena como data ('aaaa-mm-dd hh:mm'); a célula mostra "hoje 20:00"
function irrIsoM(m){ return (m===null||m===undefined)?'':irrIso(irrDiaN(m))+' '+irrHm(m); }
// cultura e estádio em colunas próprias: "Milho V10" → Milho | V10; "Mamão · produção" (Lagoa Grande) → Mamão | fase do setor
function irrCultEst(x){ const t=String(x.cult||''); const m=/^(.*\S)\s+([VR]\d+(?:\.\d+)?)$/.exec(t); if(m) return {c:m[1],e:m[2]};
  const i=t.indexOf(' · '); return i>0?{c:t.slice(0,i),e:x.fase||t.slice(i+3)}:{c:t,e:x.fase||''}; }
// coluna Fazenda só com "Todas" no topo (com uma fazenda ela repetiria o mesmo nome em todas as linhas); hole = nº de trilhas da grade
function irrColsFaz(gid,fz,v,hole){ const sp=IRG(gid); if(!sp.colsAll) sp.colsAll=sp.cols.slice(); sp.cols=fz?sp.colsAll.filter(c=>c.k!=='faz'):sp.colsAll; v[hole]=sp.cols.length; }
// célula de texto (vazio = "—"), de lista (filtro por item: r.m) e de instante
function irrTxt(r,k,t,b){ r.p[k]=[t?{k:b?'b':'txt',t:t}:{k:'mut',t:'—'}]; r.s[k]=t||''; }
function irrLst(r,k,a,kind){ r.m=r.m||{}; r.m[k]=a.map(x=>({id:x.t,l:x.t})); r.s[k]=a.map(x=>x.t).join(', ');
  r.p[k]=!a.length?[{k:'mut',t:'—'}]:(kind==='chip'?a.map(x=>({k:'chip',t:x.t,c:x.c||'gray',dica:x.dica||''})):[{k:'txt',t:r.s[k]}]); }
// coluna Pendência: o que segura a ordem, uma variável por chip (revisão TABR A11): o tipo no chip ("Divergência", "Falta insumo", "Conflito")
// e o detalhe na dica e no detalhe da ordem ("−3,8 %", "Ureia 45%", "parada da B3 · 14:00–15:00"); sem repetir "Impedida" (já é a
// Situação/Etapa ao lado) e sem os selos informativos de ordem encerrada (mut, revisão A6: "Encerrada automaticamente" não segura nada).
// ref: a ordem da pendência quando ela não é a da coluna Ordem da linha (revisão A2: "Divergência na OS-0394" ao lado da OS-0419)
function irrPend(a,ref){ return (a||[]).filter(x=>!x.mut).map(x=>{ const t=String(x.t||'').replace(/^Impedida · /,''); const i=t.indexOf(' · ');
  const cat=i>0?t.slice(0,i):t, det=i>0?t.slice(i+3):''; return Object.assign({},x,{t:cat.charAt(0).toUpperCase()+cat.slice(1)+(ref?' na '+ref:''),dica:[det,x.h].filter(Boolean).join(' · ')}); }); }
function irrPendFert(fb,ref){ return irrPend(fb?[{t:fb.t,c:'red'}]:[],ref); }
// Responsável: só a pessoa ("Caio"); a função ("· PCP") fica no cadastro de pessoas (revisão A11)
function irrQuem(d){ return String(d||'').split(' · ')[0]; }
// duração da passada na linha do detalhe: o intervalo entre o Início e o Fim da mesma linha (reais quando a passada já rodou, previstos quando
// não); sem início, a duração prevista. Antes a coluna mostrava a prevista ao lado do horário real (OS-0394: 14,5 h ao lado de 20:00–22:06)
function irrDurP(o,p){ const temI=p.ini!==null&&p.ini!==undefined; if(!temI) return p.dur; const i0=(p.iniReal!==undefined&&p.iniReal!==null)?p.iniReal:p.ini; const f=irrFimP(o,p); return f===null?p.dur:f-i0; }
function irrQ(r,k,m,vazio){ r.v[k]=irrIsoM(m); r.p[k]=[m===null||m===undefined?{k:'mut',t:vazio||'—'}:{k:'txt',t:irrQuando(m)}]; r.s[k]=m===null||m===undefined?(vazio||''):irrQuando(m); }
'''

# =====================================================================================
def ir01():
    fname='IR-01.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    # uma variável por coluna (TABELAS-FOCO, 04/10/2026). Revisão TABR (A1, 09/10): estado e próximo passo logo depois do setor, para ficarem
    # à vista sem rolar; depois a necessidade (déficit, lâmina bruta), a ordem que cobre, quanto cobre e a próxima passada dela. O secundário
    # vai para o painel do setor: fonte do déficit, cultura e estádio, área, passadas necessárias, o que resta e o responsável.
    # Fazenda só com "Todas" no topo
    g_set=grid([dict(k='setor',l='Setor',w=100),dict(k='faz',l='Fazenda',w=110),dict(k='sit',l='Situação',w=150),dict(k='pend',l='Pendência',multi=True,w=190),
                dict(k='prox',l='Próximo passo',w=150),dict(k='def',l='Déficit hoje',t='num',a='r',un='mm',d=1),dict(k='nec',l='Necessidade bruta',t='num',a='r',un='mm',d=2,dmin=1),
                dict(k='ord',l='Ordem',w=90),dict(k='cob',l='Cobertura',t='num',a='r',un='%'),dict(k='pps',l='Próxima passada',t='date',w=130)],[],
               edit=dict(m='form',title='Setor',sub='Os limites valem para a próxima programação; ordens liberadas não mudam.',
                   fields=[dict(k='defT',l='Déficit hoje',ro=True),dict(k='necT',l='Necessidade',ro=True),dict(k='ordT',l='Ordem que cobre',ro=True),
                           dict(k='donoT',l='Responsável pelo próximo passo',ro=True),dict(k='cultT',l='Cultura e estádio',ro=True),dict(k='eqT',l='Equipamento',ro=True),
                           dict(k='lmax',l='Lâmina máxima por passada',t='num',req=True,min=1,max=40,u='mm'),dict(k='imin',l='Intervalo mínimo entre inícios',t='num',req=True,min=6,max=96,u='h'),
                           dict(k='efic',l='Eficiência do sistema',t='num',req=True,min=50,max=100,u='%')]),
               gid='g_set',total=False,qf=dict(k='sit',l='Situação',todas='Todos'))
    EXTRAJS[0]=prefixo()+JS_COMUM+r"""
const RK={'Impedida':1,'A conferir':2,'A programar':3,'A liberar':3,'Irrigando':4,'Programada':5,'Sem necessidade':6,'Sem irrigação':7};
function PREVALS(self,v){ irrOuvir(self); const s=irrGet(); const fz=irrFazK(self); irrFazVals(self,v); irrFaixa(v,s,fz);
  irrHashOuvir(self,(h)=>{ if(h.indexOf('faz=')===0){ const f=h.slice(4); if(['Santa Rita','Lagoa Grande','Boa Vista','Todas'].indexOf(f)>=0) irrFazSet(self,f,''); try{ history.replaceState(null,'',location.pathname); }catch(e){} return; }
    const sid=h.split(':')[0]; const x=irrGet().setores[sid]; if(!x) return; irrFazDe(self,x.faz);
    // abre o painel do setor quando a linha já estiver na grade (a troca de fazenda redesenha antes)
    let n=0; const abre=()=>{ const sp=IRG('g_set'); if(g2find(g2rows(self,sp),sid)) g2open(self,sp,sid,null); else if(n++<8) setTimeout(abre,120); }; setTimeout(abre,0); });
  const sids=Object.keys(s.setores).filter(k=>!fz||s.setores[k].faz===fz);
  irrColsFaz('g_set',fz,v,'set_ncol');
  const rows=sids.map(k=>{ const x=s.setores[k]; const si=irrSituacao(s,k); const n=si.n; const top=si.top; const o=top&&top.o; const F=s.faz[x.faz]; const CE=irrCultEst(x);
    const temD=si.d!==null; const def=temD?[{k:'b',t:(si.est?'≈':'')+irrN(si.d,1)+' mm'}]:[{k:'mut',t:'—'}];
    const fon=!temD?'':(si.est?'Estimativa por ET':(F.demo?'Demonstrativo':'Medido'));
    // ordem da linha (coluna Ordem): a aberta que vai cobrir o déficit (fora da conferência); senão a da situação; senão a fertirrigação da O.S.
    // Cobertura e Próxima passada são dessa mesma ordem; a pendência de outra ordem diz qual é (revisão TABR A2)
    const temN=!!(n&&n.liq>0.05); const oa=((si.ords||[]).find(z=>z.etapa!=='Em conferência'))||o||null; const cb=(temN&&oa)?irrCobre(s,oa):null;
    const ordId=oa?oa.id:(top&&top.fert?top.fert:''); const cobN=cb&&cb.cob!==null?Math.round(cb.cob):''; const restaN=cobN===''?'':(cb.resta>0.05?Math.round(cb.resta*10)/10:0);
    const b=x.bal; const o2=[];
    if(b){ const net=irrCreditos(s,k).gov;
      o2.push(F.demo?('Memória (demonstrativa): déficit 0 na reposição de '+irrDdmm(irrDiaN(b.repos))+' + ETc de '+b.dias+(b.dias>1?' dias':' dia')+' (ETo 5,5 × Kc '+irrN(x.kc,2)+') = '+irrN(si.d,1)+' mm')
        :('Memória: déficit em 15/09 '+irrN(b.d0,1)+' + ETc 7 dias '+irrN(b.etc,1)+' − chuva efetiva '+irrN(b.pef,1)+' − irrigação líquida '+irrN(net,1)+' = '+(si.est?'≈':'')+irrN(si.d,1)+' mm'));
      if(!F.demo) o2.push('Chuva efetiva: '+b.chuva+' · ETc = ET₀ Penman-Monteith (Estação Santa Rita) × Kc do estádio');
      const se=irrSerie(s,k).filter(z=>z.v!==null); if(se.length) o2.push('Déficit no fim do dia: '+se.map(z=>z.t+' '+(z.est?'≈':'')+irrN(z.v,1)).join(' · ')+' · hoje '+(si.est?'≈':'')+irrN(si.d,1));
      if(si.faixa) o2.push('Passagem parcial · '+si.faixa);
      irrApsSetor(s,k).slice().sort((p,q)=>q.q-p.q).forEach(a=>{ const pc=irrApParc(a,x.ha); o2.push('Aplicado · '+irrDdmm(irrDiaN(a.q))+' · '+a.os+' · '+a.txt+' · '+irrN(a.vol)+' m³ em '+irrN(irrApCob(a),pc?1:0)+' ha = '+irrMm(irrApBr(a))+' mm brutos'+(pc?' na faixa':'')+' × '+a.ef+' % = '+irrMm(irrApNet(a))+' mm líquidos'+(pc?' · fora do déficit do pivô':'')+(a.prov?' · provisório':'')); }); }
    irrOrdensSetor(s,k).filter(z=>irrAberta(z)||z.etapa==='Encerradas').slice(-4).forEach(z=>o2.push({t:z.id+' · '+irrEtapa(s,z)+' · '+irrJanO(z),h:'IR-03det.dc.html#'+z.id}));
    const so=irrSonda(s,x); o2.push({t:'Fontes: '+(F.demo?'ETo de referência (demonstrativa)':'Estação Santa Rita')+(so?' · '+so.nome+' '+so.st.toLowerCase()+(so.motivo?' ('+so.motivo+')':''):''),h:'IR-04.dc.html'});
    const eq=(x.tipo==='gotejo'?'Gotejo':'Pivô')+' · '+irrN(x.ha)+' ha · '+irrN(x.vazao)+' L/s · '+x.bnome+' · '+((s.capt[x.capt]||{}).nome||'');
    const r={id:k,rk:RK[si.sit]||9,ro:!b,ac:si.acao,acId:(o?o.id:(top&&top.fert&&!/^Programar/.test((si.acao||[''])[0])?top.fert:x.nome)),fe:!!(top&&top.fert),o:o2.map(z=>typeof z==='string'?{t:z}:z),
      v:{def:temD?si.d:'',nec:temN?n.br:'',cob:cobN,lmax:x.lmax,imin:x.imin,efic:x.efic,defT:si.d===null?'—':((si.est?'≈':'')+irrN(si.d,1)+' mm · '+(si.fon||fon)),
         necT:temN?('líquida '+irrN(n.liq,1)+' mm · bruta '+irrMm(n.br)+' mm · '+n.np+(n.np>1?' passadas necessárias de ':' passada necessária de ')+irrMm(n.por)+' mm'):'sem lâmina hoje',
         ordT:ordId?(ordId+(cobN!==''?' · cobre '+cobN+' %'+(restaN>0?' · resta '+irrN(restaN,1)+' mm':''):(cb&&cb.prox?' · próximo ciclo':''))):'sem ordem',
         donoT:si.acao?(si.dono||'—'):'—',cultT:CE.c+(CE.e?' · '+CE.e:''),eqT:eq},
      s:{},p:{def}};
    irrTxt(r,'setor',x.nome,true); irrTxt(r,'faz',F.nome); r.s.def=temD?(si.est?'≈':'')+irrN(si.d,1)+' mm':'';
    r.p.nec=[temN?{k:'txt',t:irrMm(n.br)}:{k:'mut',t:'—'}]; r.s.nec=temN?irrMm(n.br):''; irrTxt(r,'ord',ordId);
    // cobertura da ordem sobre o déficit de hoje; ordem do próximo ciclo não cobre o de hoje (a célula diz isso)
    r.p.cob=[cobN!==''?{k:'txt',t:String(cobN)}:(cb&&cb.prox?{k:'mut',t:'próximo ciclo'}:{k:'mut',t:'—'})]; r.s.cob=cobN!==''?String(cobN):(cb&&cb.prox?'próximo ciclo':'');
    r.p.sit=[{k:'chip',t:si.sit,c:SITC[si.c]||'gray'}]; r.s.sit=si.sit;
    // pendência do item que dá a situação e o próximo passo; se ele não é a ordem da linha, a pendência diz qual ordem é
    const pid=top?(top.o?top.o.id:(top.fert||'')):''; const ref=(pid&&pid!==ordId)?pid:'';
    let pen=[], pps=null, ppsV='—';
    if(top&&top.o) pen=irrPend(irrSelos(s,top.o),ref); else if(top&&top.fert) pen=irrPendFert(irrFertBloq(top.fert),ref);
    // próxima passada da ordem da coluna Ordem (antes vinha da ordem da situação e misturava duas ordens na linha)
    if(oa){ const pp=irrPassProx(oa); if(pp){ pps=pp.ini; ppsV='a definir'; } }
    else if(ordId&&s.fert[ordId]){ const f=s.fert[ordId]; const e2=irrFertEtapa(ordId); if(f.ini&&(e2==='A liberar'||e2==='Liberadas')) pps=f.ini; }
    irrLst(r,'pend',pen,'chip'); irrQ(r,'pps',pps,ppsV);
    r.p.prox=si.acao?[{k:'link',t:si.acao[0],h:si.acao[1]}]:[{k:'mut',t:'—'}]; r.s.prox=si.acao?si.acao[0]:'';
    return r; });
  rows.sort((a,b)=>(a.rk-b.rk)||((a.fe?1:0)-(b.fe?1:0))||String(a.id).localeCompare(String(b.id),'pt-BR',{numeric:true}));
  IRG('g_set').rows=rows;
  const imp=rows.filter(r=>r.rk===1).length, pen=rows.filter(r=>r.rk>=2&&r.rk<=3).length;
  const urg=rows.filter(r=>r.rk<=3&&r.ac).sort((a,b)=>(a.rk-b.rk)||((a.fe?1:0)-(b.fe?1:0)))[0];
  v.prim_has=!!urg; v.prim_h=urg?urg.ac[1]:'#'; v.prim_t=urg?(urg.ac[0].indexOf(urg.acId)>=0?urg.ac[0]:urg.ac[0]+' · '+urg.acId):'';
  v.hs_t=imp||pen?[imp?imp+(imp>1?' impedidos':' impedido'):'',pen?pen+(pen>1?' pendentes':' pendente'):''].filter(Boolean).join(' · '):'Sem pendências'; v.hs_st=chipSt(imp?'red':(pen?'yellow':'green'));
  v.tem=fz!=='BV'; v.vazio=fz==='BV'; v.vazioT='Boa Vista não tem setor irrigado cadastrado.'; }
function EXTRAVALS(self,v){ irrVista(self,'g_set');
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_set'||!r) return; g2set(self,'g_set',{rows:null,fl:r.id});
    irrMudar(self,s=>irrLimites(s,r.id,{lmax:Number(r.v.lmax),imin:Number(r.v.imin),efic:Number(r.v.efic)})); };
  self.g2formActs=(gid,r)=>{ if(gid!=='g_set') return []; const s=irrGet(); const si=irrSituacao(s,r.id); const out=[];
    if(si.acao) out.push({t:si.acao[0],h:si.hoje,go:()=>irrGo(si.acao[1])});
    if(s.setores[r.id].bal&&(!si.acao||si.acao[0]!=='Programar irrigação')&&!(si.ords||[]).length) out.push({t:'Programar irrigação',h:'Abre a programação com a necessidade e a janela sugerida.',go:()=>irrGo('IR-02.dc.html#programar='+r.id)});
    return out; }; }
"""
    corpo=(vazio('vazio','vazioT','Cadastrar setores','CD-03.dc.html')
           + f'<sc-if value="{H("tem")}" hint-placeholder-val="{T()}">'+section('Setores','','',g_set)+'</sc-if>')
    prim=(f'<span style="{H("hs_st")}">{H("hs_t")}</span><span style="width: 8px;"></span>'
          f'<sc-if value="{H("prim_has")}" hint-placeholder-val="{T()}"><a href="{H("prim_h")}" style="{BTN_ST(True)} text-decoration: none;">{H("prim_t")}</a></sc-if>')
    shell37('IR-01','Irrigação',corpo,fname=fname,primary_html=prim,steps=faixa(1),search=False)
    ncol_dinamico(fname,['set_ncol'])

# =====================================================================================
def ir02():
    fname='IR-02.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    x0={'c-'+k:True for k in DI.CAPT}
    # árvore captação › ordem, uma variável por coluna (TABELAS-FOCO, 04/10/2026). Revisão TABR (A1, A4, 09/10): etapa, pendência e próximo
    # passo logo depois da ordem; depois setor, início e fim (ordenam como data), lâmina e avisos. Tipo, bomba, vazão do setor, passadas e
    # responsável ficam no detalhe da ordem (IR-03det). A linha da captação não põe o pico do dia numa coluna de vazão das ordens (seriam duas
    # grandezas na mesma coluna): o pico e a outorga em renovação são avisos da captação, e o pico acima da outorga é pendência dela
    g_ag=grid([dict(k='item',l='Captação › ordem',w=150),dict(k='etapa',l='Etapa',w=110),dict(k='pend',l='Pendência',multi=True,w=190),dict(k='prox',l='Próximo passo',w=140),
               dict(k='setor',l='Setor',w=90),dict(k='ini',l='Início',t='date',w=110),dict(k='fim',l='Fim',t='date',w=110),
               dict(k='lam',l='Lâmina',t='num',a='r',un='mm',d=2,dmin=1),dict(k='avs',l='Avisos',multi=True,w=200)],[],
              edit=dict(m='ro',title='Programação',leafOnly=True,fields=[]),gid='g_ag',total=False,tree=True,x0=x0,search=False)
    pg_corpo=(campo('Setor','pg_sel',f'<select id="pg_sel" value="{H("pg_sid")}" onChange="{H("pg_setsid")}" style="{INP}"><sc-for list="{H("pg_opts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>','pg_err')
              + kvfor('pg_kv',2) + checks('pg_ck')
              + f'<sc-if value="{H("pg_tem")}" hint-placeholder-val="{F()}"><div role="status" style="padding: 10px 12px; border-radius: 10px; background: {ACCS}; color: {ACC}; font-size: 13px; font-weight: 700;">{H("pg_temT")}</div></sc-if>')
    pg_rod=(f'<button type="button" onClick="{H("pg_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<sc-if value="{H("pg_tem")}" hint-placeholder-val="{F()}"><a href="{H("pg_href")}" style="{BTN_ST(True,True)} text-decoration: none;">{H("pg_abrirT")}</a></sc-if>'
            f'<sc-if value="{H("pg_nova")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("pg_ok")}" style="{BTN_ST(True,True)}">{H("pg_okT")}</button></sc-if>')
    EXTRA.append(painel('pg',pg_corpo,pg_rod))
    EXTRAJS[0]=prefixo()+JS_COMUM+r"""
function irrUsoDia(s,cid,k){ const cp=s.capt[cid]; const ws=irrComprometidas(s,null).filter(w=>w.capt===cid); const d0=k*1440,d1=d0+1440; let vol=0,pico=0;
  ws.forEach(w=>{ const a=Math.max(d0,w.ini),b=Math.min(d1,w.fim); if(b>a) vol+=w.ls*(b-a)*0.06; });
  ws.filter(w=>w.fim>d0&&w.ini<d1).forEach(w=>{ const t=Math.max(w.ini,d0); const q=ws.filter(z=>z.ini<=t&&z.fim>t).reduce((a,z)=>a+z.ls,0); if(q>pico) pico=q; });
  return {vol,pico,pct:cp?vol/(cp.ls*cp.h*3.6)*100:0}; }
function PREVALS(self,v){ irrOuvir(self); const s=irrGet(); const fz=irrFazK(self); irrFazVals(self,v); const c=irrFaixa(v,s,fz);
  irrHashOuvir(self,(h)=>{ if(h.indexOf('programar')!==0) return; const sid=h.split('=')[1]||''; const x=irrGet().setores[sid]; if(x) irrFazDe(self,x.faz); self.setState({pg:{sid:x?sid:''}}); });
  const sids=Object.keys(s.setores).filter(k=>!fz||s.setores[k].faz===fz);
  const caps=Object.keys(s.capt).filter(cid=>sids.some(k=>s.setores[k].capt===cid));
  const rows=caps.map(cid=>{ const cp=s.capt[cid]; const kids=[];
    Object.values(s.ordens).filter(o=>s.setores[o.setor].capt===cid&&['A liberar','Liberadas','Em execução'].indexOf(irrEtapa(s,o))>=0).sort((a,b)=>(irrIni(a)===null?1e9:irrIni(a))-(irrIni(b)===null?1e9:irrIni(b))).forEach(o=>{
      const x=s.setores[o.setor]; const et=irrEtapa(s,o); const sel=irrSelos(s,o); const av=irrAvisos(s,o).filter(a=>a.k!=='renov'); const p=irrProx(s,o);   /* outorga em renovação: aviso da captação */
      // início da 1ª passada e fim da última; passada sem janela deixa o fim "a definir" (a janela de cada passada fica no detalhe da ordem)
      const ps=o.passadas; const def=ps.every(q=>q.ini!==null&&q.ini!==undefined); const fim=def?Math.max.apply(null,ps.map(q=>irrFimP(o,q))):null;
      const r={id:o.id,dr:'go_'+o.id,v:{lam:o.lam,href:'IR-03det.dc.html#'+o.id},s:{},p:{}};
      irrTxt(r,'item',o.id,true); irrTxt(r,'setor',x.nome);
      irrQ(r,'ini',irrIni(o),'a definir'); irrQ(r,'fim',fim,'a definir');
      r.p.etapa=[{k:'chip',t:et,c:IRR_COR[et]||'gray'}]; r.s.etapa=et; irrLst(r,'pend',irrPend(sel),'chip');
      irrTxt(r,'prox',p?p.t:'',true); irrLst(r,'avs',av);
      kids.push(r); });
    Object.keys(s.fert).filter(k=>!s.ordens[k]&&s.setores[s.fert[k].setor].capt===cid).forEach(k=>{ const f=s.fert[k]; const et=irrFertEtapa(k); if(!et||['Encerradas','Canceladas'].indexOf(et)>=0) return; const x=s.setores[f.setor]; const fb=irrFertBloq(k);
      const r={id:k,dr:'go_'+k,v:{lam:f.lam||'',href:'OS.dc.html#'+k},s:{},p:{}};
      irrTxt(r,'item',k,true); irrTxt(r,'setor',x.nome);
      irrQ(r,'ini',f.ini?f.ini:null); irrQ(r,'fim',f.ini?f.fim:null);
      r.p.etapa=[{k:'chip',t:et,c:IRR_COR[et]||'gray'}]; r.s.etapa=et; irrLst(r,'pend',irrPendFert(fb),'chip');
      irrTxt(r,'prox',fb?fb.passo:(et==='A liberar'?'Liberar na O.S.':'Abrir na O.S.'),true); irrLst(r,'avs',[]);
      kids.push(r); });
    const u=irrUsoDia(s,cid,0);
    // linha da captação: o nome e quantas ordens; o pico de vazão de hoje e a outorga em renovação são avisos dela (o pico acima da vazão
    // outorgada é pendência); as colunas das ordens ficam vazias
    const g={id:'c-'+cid,v:{},s:{item:cp.nome},kids,p:{item:[{k:'b',t:cp.nome},{k:'mut',t:kids.length+(kids.length===1?' ordem':' ordens')}]}};
    ['setor','ini','fim','lam','etapa','prox'].forEach(z=>{ g.p[z]=[{k:'mut',t:''}]; g.s[z]=''; });
    const acima=u.pico>cp.ls+1e-9;
    irrLst(g,'pend',acima?[{t:'Pico acima da outorga',c:'red',dica:irrN(u.pico)+' de '+irrN(cp.ls)+' L/s'}]:[],'chip');
    irrLst(g,'avs',(u.pico>0?[{t:'Pico hoje '+irrN(u.pico)+' de '+irrN(cp.ls)+' L/s'}]:[]).concat(cp.st==='Em renovação'?[{t:'Outorga em renovação'}]:[]));
    if(!acima){ g.p.pend=[{k:'mut',t:''}]; }
    return g; });
  IRG('g_ag').rows=rows;
  const t=[]; if(c.conf) t.push(c.conf+(c.conf>1?' conflitos':' conflito')); if(c.jan) t.push(c.jan+(c.jan>1?' janelas a definir':' janela a definir'));
  v.hs_t=t.length?t.join(' · '):'Programação sem pendências'; v.hs_st=chipSt(c.conf?'red':(t.length?'yellow':'green'));
  v.tem=fz!=='BV'; v.vazio=fz==='BV'; v.vazioT='Boa Vista não tem setor irrigado cadastrado.';
  v.pg_btn=sids.some(k=>s.setores[k].bal); }
function EXTRAVALS(self,v){ const s=irrGet(); const fz=irrFazK(self);
  IRG('g_ag').rows.forEach(c=>(c.kids||[]).forEach(k=>{ v['go_'+k.id]=()=>irrGo(k.v.href); }));
  // painel "Programar irrigação": necessidade preenchida, janela sugerida e tarefa única recuperada
  const pg=self.state.pg; v.pg_open=!!pg; v.pg_warn=false; v.pg_err=''; v.pg_err_has=false;
  v.pg_new=()=>self.setState({pg:{sid:''}}); v.pg_cancel=()=>{ self.setState({pg:null}); try{ if(location.hash) history.replaceState(null,'',location.pathname); }catch(e){} };
  v.pg_key=(e)=>{ if(e&&e.key==='Escape') v.pg_cancel(); };
  const ops=Object.keys(s.setores).filter(k=>s.setores[k].bal&&(!fz||s.setores[k].faz===fz)).map(k=>{ const x=s.setores[k]; const d=irrDef(s,k); return {v:k,t:x.nome+' · '+x.cult+' · '+(irrEst(s,x)?'≈':'')+irrN(d,1)+' mm',d,lim:x.limiar||0}; })
    .sort((a,b)=>((b.d>=b.lim)-(a.d>=a.lim))||(b.d-a.d));
  v.pg_opts=ops; v.pg_titulo='Programar irrigação'; v.pg_kv=[]; v.pg_ck=[]; v.pg_tem=false; v.pg_nova=!!ops.length; v.pg_okT='Programar'; v.pg_temT=''; v.pg_href='#'; v.pg_abrirT='';
  irrPaineis(self,[['pg',!!pg,()=>v.pg_cancel()]]);
  if(pg){ const sid=(pg.sid&&s.setores[pg.sid])?pg.sid:((ops[0]||{}).v||''); v.pg_sid=sid; v.pg_setsid=(e)=>self.setState({pg:{sid:e.target.value}});
    const x=s.setores[sid]; v.pg_sub=x?(s.faz[x.faz].nome+' · '+x.nome+' · '+x.cult+' · '+irrN(x.ha)+' ha'):'Nenhum setor com balanço nesta fazenda.';
    if(x){ const n=irrNec(s,sid); const ab=irrOrdensSetor(s,sid).filter(irrAberta).filter(o=>irrEt(o)!=='Em conferência'); const fp=ab.length?null:irrFertParadaSetor(s,sid); const fe=fp?[]:irrFertAbertaSetor(s,sid);
      v.pg_kv=[{l:'Déficit hoje',t:(irrEst(s,x)?'≈':'')+irrN(n.liq,1)+' mm'+(irrEst(s,x)?' · estimativa por ET':'')},{l:'Lâmina bruta',t:irrMm(n.br)+' mm (eficiência '+x.efic+' %)'},
               {l:'Passadas',t:n.np+(n.np>1?' de ':' de ')+irrMm(n.por)+' mm · limite '+irrMm(x.lmax)+' mm'},{l:'Volume e duração',t:irrN(n.vol)+' m³ · '+irrH(n.dur)+(n.np>1?' por passada':'')}];
      if(ab.length||fe.length){ const id=ab.length?ab[0].id:fe[0]; v.pg_tem=true; v.pg_nova=false; v.pg_href=ab.length?'IR-03det.dc.html#'+id:'OS.dc.html#'+id; v.pg_abrirT='Abrir '+id;
        v.pg_temT='Tarefa única '+id+' já existe'+(ab.length?' · '+irrEtapa(s,ab[0])+' · '+irrJanO(ab[0]):' · fertirrigação na O.S.')+' · nenhuma ordem nova.'; }
      else if(n.liq<0.05){ v.pg_kv.push({l:'Situação',t:'sem déficit hoje'}); v.pg_nova=false; }
      else { if(fp) v.pg_okT='Programar só água'; const durs=Array.from({length:n.np},()=>n.dur); const inis=irrSugerir(s,sid,durs,s.agora,'novo');
        v.pg_kv.push({l:'Janela sugerida',t:inis.every(q=>q!==null)?inis.map((q,i)=>irrJan(q,q+durs[i])).join(' · '):'sem janela livre em 5 dias'});
        const tmp={id:'novo',faz:x.faz,setor:sid,passadas:inis.map((q,i)=>({n:i+1,ini:q,dur:n.dur,lam:n.por,st:'Programada'})),exec:{pausas:[]}};
        const ck=irrChecar(s,tmp); v.pg_ck=ck.bloq.map(b=>({t:'Bloqueia · '+b.t+(b.h?' '+b.h:'')+' · '+b.dono,st:'font-size:12.5px;font-weight:700;padding:6px 10px;border-radius:8px;background:#FDE8E6;color:#B42318;'}))
          .concat(ck.av.map(a=>({t:'Aviso · '+a.t,st:'font-size:12.5px;font-weight:600;padding:6px 10px;border-radius:8px;background:#FFF3D6;color:#8A5A00;'})));
        if(fp) v.pg_ck.unshift({t:fp.id+' parada na O.S. · '+fp.b.t+' · '+fp.b.dono+' · a água vai sem o produto',st:'font-size:12.5px;font-weight:600;padding:6px 10px;border-radius:8px;background:#FFF3D6;color:#8A5A00;'});
        if(!ck.bloq.length) v.pg_ck.push({t:'Pronta: libera ao programar, sem aprovação (água sem produto)',st:'font-size:12.5px;font-weight:700;padding:6px 10px;border-radius:8px;background:#E4F3E9;color:#1E7A4C;'}); } }
    v.pg_ok=()=>{ if(!x) return; const r=irrMudar(self,s0=>irrProgramar(s0,sid)); if(!r.erro){ self.setState({pg:null}); try{ history.replaceState(null,'',location.pathname); }catch(e){} } }; }
  else { v.pg_sid=''; v.pg_sub=''; v.pg_setsid=()=>{}; v.pg_ok=()=>{}; } }
"""
    corpo=(vazio('vazio','vazioT','Cadastrar setores','CD-03.dc.html')
           + f'<sc-if value="{H("tem")}" hint-placeholder-val="{T()}">'+section('Agenda por captação','','',g_ag)+'</sc-if>')
    prim=(f'<span style="{H("hs_st")}">{H("hs_t")}</span><span style="width: 8px;"></span>'
          f'<sc-if value="{H("pg_btn")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("pg_new")}" style="{BTN_ST(True)}">Programar irrigação</button></sc-if>')
    shell37('IR-02','Programação',corpo,fname=fname,crumbs_extra=['Programação'],primary_html=prim,steps=faixa(2),search=False)

# =====================================================================================
def ir03():
    fname='IR-03.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    # uma variável por coluna (TABELAS-FOCO, 04/10/2026). Revisão TABR (A1, 09/10): etapa (as 5 fases), pendência, próximo passo e responsável
    # logo depois da ordem; depois tipo, setor, início e fim (ordenam como data) e lâmina. Cultura, passadas, avisos, medido e área coberta
    # ficam no detalhe da ordem. Fazenda só com "Todas" no topo
    g_os=grid([dict(k='ordem',l='Ordem',w=90),dict(k='faz',l='Fazenda',w=110),dict(k='etapa',l='Etapa',w=120),dict(k='pend',l='Pendência',multi=True,w=190),
               dict(k='prox',l='Próximo passo',w=150),dict(k='dono',l='Responsável',w=110),dict(k='tipo',l='Tipo',w=120),dict(k='setor',l='Setor',w=90),
               dict(k='ini',l='Início',t='date',w=110),dict(k='fim',l='Fim',t='date',w=110),dict(k='lam',l='Lâmina',t='num',a='r',un='mm',d=2,dmin=1)],[],
              edit=dict(m='ro',title='Ordem',fields=[]),gid='g_os',total=False,qf=dict(k='etapa',l='Etapa',todas='Todas'))
    EXTRAJS[0]=prefixo()+JS_COMUM+r"""
const ORD=['A liberar','Em conferência','Em execução','Liberadas','Encerradas','Canceladas'];
function PREVALS(self,v){ irrOuvir(self); const s=irrGet(); const fz=irrFazK(self); irrFazVals(self,v); irrFaixa(v,s,fz);
  irrColsFaz('g_os',fz,v,'os_ncol');
  const rows=[];
  Object.values(s.ordens).filter(o=>!fz||o.faz===fz).forEach(o=>{ const x=s.setores[o.setor]; const et=irrEtapa(s,o); const sel=irrSelos(s,o); const p=irrProx(s,o);
    const ps=o.passadas; const i0=(q)=>(q.iniReal!==undefined&&q.iniReal!==null)?q.iniReal:q.ini; const def=ps.every(q=>q.ini!==null&&q.ini!==undefined);
    const ini=ps.filter(q=>q.ini!==null&&q.ini!==undefined).map(i0); const fim=def?Math.max.apply(null,ps.map(q=>irrFimP(o,q))):null;
    const r={id:o.id,dr:'go_'+o.id,rk:ORD.indexOf(et),q:irrIni(o),v:{lam:o.lam,href:'IR-03det.dc.html#'+o.id},s:{},p:{}};
    irrTxt(r,'ordem',o.id,true); irrTxt(r,'tipo',o.fert?'Fertirrigação':'Água'); irrTxt(r,'faz',s.faz[x.faz].nome); irrTxt(r,'setor',x.nome);
    irrQ(r,'ini',ini.length?Math.min.apply(null,ini):null,'a definir'); irrQ(r,'fim',fim,'a definir');
    r.p.etapa=[{k:'chip',t:et,c:IRR_COR[et]||'gray'}]; r.s.etapa=et; irrLst(r,'pend',irrPend(sel),'chip');
    irrTxt(r,'prox',p?p.t:'',true); irrTxt(r,'dono',p?irrQuem(p.dono):''); rows.push(r); });
  // fertirrigações da O.S. (cenário compartilhado): só leitura aqui
  Object.keys(s.fert).filter(k=>!s.ordens[k]&&(!fz||s.setores[s.fert[k].setor].faz===fz)).forEach(k=>{ const f=s.fert[k]; const et=irrFertEtapa(k)||'—'; const x=s.setores[f.setor]; const fb=irrFertBloq(k);
    const px=fb?[fb.passo,fb.dono]:(et==='A liberar'?['Liberar na O.S.','Ana (agrônoma)']:['Abrir na O.S.',irrFertResp(k)||'']);
    const r={id:k,dr:'go_'+k,rk:ORD.indexOf(et),q:f.ini,v:{lam:f.lam||'',href:'OS.dc.html#'+k},s:{},p:{}};
    irrTxt(r,'ordem',k,true); irrTxt(r,'tipo','Fertirrigação'); irrTxt(r,'faz',s.faz[x.faz].nome); irrTxt(r,'setor',x.nome);
    irrQ(r,'ini',f.ini?f.ini:null); irrQ(r,'fim',f.ini?f.fim:null);
    r.p.etapa=[{k:'chip',t:et,c:IRR_COR[et]||'gray'}]; r.s.etapa=et; irrLst(r,'pend',irrPendFert(fb),'chip');
    irrTxt(r,'prox',px[0],true); irrTxt(r,'dono',irrQuem(px[1])); rows.push(r); });
  rows.sort((a,b)=>(a.rk-b.rk)||((a.q===null||a.q===undefined?1e9:a.q)-(b.q===null||b.q===undefined?1e9:b.q)));
  IRG('g_os').rows=rows;
  const conf=rows.filter(r=>r.s.etapa==='Em conferência').length, lib=rows.filter(r=>r.s.etapa==='A liberar').length;
  v.hs_t=[conf?conf+' em conferência':'',lib?lib+' a liberar':''].filter(Boolean).join(' · ')||'Sem pendências'; v.hs_st=chipSt(conf||lib?'yellow':'green');
  // ordem de hoje: a que está em execução; senão a próxima liberada
  const hoje=rows.filter(r=>r.s.etapa==='Em execução'&&s.ordens[r.id])[0]||rows.filter(r=>r.s.etapa==='Liberadas'&&s.ordens[r.id]).sort((a,b)=>a.q-b.q)[0]||null;
  v.hoje_has=!!hoje; v.hoje_h=hoje?'IR-03det.dc.html#'+hoje.id:'#'; v.hoje_t=hoje?'Abrir ordem de hoje · '+hoje.id:'';
  v.tem=fz!=='BV'; v.vazio=fz==='BV'; v.vazioT='Boa Vista não tem ordem de irrigação.'; }
function EXTRAVALS(self,v){ irrVista(self,'g_os'); IRG('g_os').rows.forEach(r=>{ v['go_'+r.id]=()=>irrGo(r.v.href); }); }
"""
    corpo=(vazio('vazio','vazioT','Abrir programação','IR-02.dc.html')
           + f'<sc-if value="{H("tem")}" hint-placeholder-val="{T()}">'+section('Ordens por etapa','','',g_os)+'</sc-if>')
    prim=(f'<span style="{H("hs_st")}">{H("hs_t")}</span><span style="width: 8px;"></span>'
          f'<sc-if value="{H("hoje_has")}" hint-placeholder-val="{T()}"><a href="{H("hoje_h")}" style="{BTN_ST(True)} text-decoration: none;">{H("hoje_t")}</a></sc-if>')
    shell37('IR-03','Ordens de irrigação',corpo,fname=fname,crumbs_extra=['Ordens'],primary_html=prim,steps=faixa(3),search=False)
    ncol_dinamico(fname,['os_ncol'])

# =====================================================================================
def ir03det():
    fname='IR-03det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    # passadas (sub-detalhe) com filtro e ordem; uma variável por coluna (TABELAS-FOCO, 04/10/2026): início e fim (ordenam como data), lâmina,
    # duração (h), estado (chip), área coberta (ha) e volume medido (m³); o saldo da v2 vai para Execução e conferência
    g_pas=grid([dict(k='n',l='Passada',t='num',a='r'),dict(k='ini',l='Início',t='date',w=110),dict(k='fim',l='Fim',t='date',w=110),dict(k='lam',l='Lâmina',t='num',a='r',un='mm',d=2,dmin=1),
                dict(k='dur',l='Duração',t='num',a='r',un='h',d=1),dict(k='st',l='Estado',w=140),dict(k='cob',l='Área coberta',t='num',a='r',un='ha',d=2,dmin=1),
                dict(k='vol',l='Volume medido',t='num',a='r',un='m³')],[],edit=dict(m='none'),gid='g_pas',total=False,search=False)
    g_trl=grid([dict(k='hora',l='Quando',t='date',w=120),dict(k='rec',l='Recibo'),dict(k='ev',l='Evento',w=560),dict(k='quem',l='Quem')],[],
               edit=dict(m='ro',title='Evento',fields=[dict(k='quando',l='Quando',ro=True),dict(k='rec',l='Recibo',ro=True),dict(k='ev',l='Evento',ro=True),dict(k='quem',l='Quem',ro=True)]),
               gid='g_trl',total=False,search=False)
    # ---------- painéis da ordem ----------
    jn_corpo=(f'<sc-for list="{H("jn_ps")}" as="p" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 12px;">'
              f'<b style="font-size: 13px;">{H("p.t")}</b><div style="display: flex; gap: 8px;">'
              f'<label style="display: flex; flex-direction: column; gap: 3px; flex: 1 1 0; font-size: 12px; font-weight: 600; color: {MUTED};">Data<input type="date" id="{H("p.idd")}" value="{H("p.d")}" onChange="{H("p.setD")}" style="{INP}"></label>'
              f'<label style="display: flex; flex-direction: column; gap: 3px; flex: 1 1 0; font-size: 12px; font-weight: 600; color: {MUTED};">Início<input type="time" id="{H("p.idh")}" value="{H("p.h")}" onChange="{H("p.setH")}" style="{INP}"></label></div>'
              f'<span style="font-size: 12.5px; color: {MUTED};">{H("p.fim")}</span></div></sc-for>'
              + checks('jn_ck')
              + f'<div><button type="button" onClick="{H("jn_sug")}" style="{BTN_ST(False,True)}">Usar janela sugerida</button></div>')
    jn_rod=(f'<button type="button" onClick="{H("jn_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("jn_ok")}" style="{BTN_ST(True,True)}">Salvar janela</button>')
    cf_corpo=(checks('cf_ck')
              + f'<div role="radiogroup" aria-label="Opções calculadas" style="display: flex; flex-direction: column; gap: 6px;"><sc-for list="{H("cf_opts")}" as="op" hint-placeholder-count="2">'
              f'<label style="display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 12px; cursor: pointer; font-size: 13px;">'
              f'<input type="radio" name="cf_op" checked="{H("op.on")}" onChange="{H("op.pick")}" style="accent-color: {ACC}; margin-top: 2px;"><span style="display: flex; flex-direction: column; gap: 2px;"><b>{H("op.t")}</b><span style="font-size: 12px; color: {MUTED};">{H("op.sub")}</span></span></label></sc-for></div>'
              + f'<sc-if value="{H("cf_semop")}" hint-placeholder-val="{F()}"><div role="status" style="font-size: 13px; color: {MUTED};">{H("cf_semopT")}</div></sc-if>'
              + f'<div><button type="button" onClick="{H("cf_outra")}" style="{BTN_ST(False,True)}">Definir outra janela</button></div>')
    cf_rod=(f'<button type="button" onClick="{H("cf_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("cf_ok")}" style="{BTN_ST(True,True)}">Aplicar janela</button>')
    tm_corpo=(f'<div role="radiogroup" aria-label="Área coberta" style="display: flex; flex-direction: column; gap: 6px;">'
              f'<label style="display: flex; gap: 8px; align-items: center; font-size: 13.5px; cursor: pointer;"><input type="radio" name="tm_t" checked="{H("tm_full")}" onChange="{H("tm_setfull")}" style="accent-color: {ACC};">{H("tm_fullT")}</label>'
              f'<label style="display: flex; gap: 8px; align-items: center; font-size: 13.5px; cursor: pointer;"><input type="radio" name="tm_t" checked="{H("tm_parc")}" onChange="{H("tm_setparc")}" style="accent-color: {ACC};">Parou antes · informar a área coberta</label></div>'
              + f'<sc-if value="{H("tm_parc")}" hint-placeholder-val="{F()}">'+campo('Área coberta (ha)','tm_cob',f'<input id="tm_cob" inputMode="decimal" value="{H("tm_cob")}" onChange="{H("tm_setcob")}" style="{INP}">','tm_ecob')+'</sc-if>'
              + campo('Leitura do hidrômetro (m³)','tm_vol',f'<input id="tm_vol" inputMode="decimal" value="{H("tm_vol")}" onChange="{H("tm_setvol")}" placeholder="vazio = sem leitura" style="{INP}">','tm_evol')
              + f'<div style="font-size: 12.5px; color: {MUTED};">{H("tm_hint")}</div>')
    tm_rod=(f'<button type="button" onClick="{H("tm_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("tm_ok")}" style="{BTN_ST(True,True)}">Confirmar término</button>')
    cm_corpo=(kvfor('cm_kv',2)
              + campo('Leitura do hidrômetro (m³)','cm_vol',f'<input id="cm_vol" inputMode="decimal" value="{H("cm_vol")}" onChange="{H("cm_setvol")}" style="{INP}">','cm_evol'))
    cm_rod=(f'<button type="button" onClick="{H("cm_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("cm_ok")}" style="{BTN_ST(True,True)}">Validar e encerrar</button>')
    av_corpo=campo('Área coberta até agora (ha)','av_cob',f'<input id="av_cob" inputMode="decimal" value="{H("av_cob")}" onChange="{H("av_setcob")}" style="{INP}">','av_ecob')
    av_rod=(f'<button type="button" onClick="{H("av_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("av_ok")}" style="{BTN_ST(True,True)}">Salvar avanço</button>')
    rc_corpo=(campo('Produto','rc_prod',f'<select id="rc_prod" value="{H("rc_prod")}" onChange="{H("rc_setprod")}" style="{INP}"><option value="Ureia 45%">Ureia 45%</option><option value="Nitrato de cálcio">Nitrato de cálcio</option><option value="Nitrato de potássio">Nitrato de potássio</option></select>','rc_eprod')
              + campo('Dose (kg/ha)','rc_dose',f'<input id="rc_dose" inputMode="decimal" value="{H("rc_dose")}" onChange="{H("rc_setdose")}" style="{INP}">','rc_edose')
              + campo('Motivo agronômico','rc_mot',f'<textarea id="rc_mot" value="{H("rc_mot")}" onChange="{H("rc_setmot")}" placeholder="Ex.: deficiência de N no estádio V10" style="{INP} min-height: 64px; resize: vertical;"></textarea>','rc_emot')
              + f'<div style="padding: 10px 12px; border-radius: 10px; background: {BG}; font-size: 12.8px; line-height: 1.5;"><b>Efeito</b> · {H("rc_prev")}</div>')
    rc_rod=(f'<button type="button" onClick="{H("rc_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
            f'<button type="button" onClick="{H("rc_ok")}" style="{BTN_ST(True,True)}">Criar versão v2</button>')
    for pre,c,r in (('jn',jn_corpo,jn_rod),('cf',cf_corpo,cf_rod),('tm',tm_corpo,tm_rod),('cm',cm_corpo,cm_rod),('av',av_corpo,av_rod),('rc',rc_corpo,rc_rod)): EXTRA.append(painel(pre,c,r))
    EXTRAJS[0]=prefixo()+JS_COMUM+r'''
const CK_RED='font-size:12.5px;font-weight:700;padding:6px 10px;border-radius:8px;background:#FDE8E6;color:#B42318;';
const CK_YEL='font-size:12.5px;font-weight:600;padding:6px 10px;border-radius:8px;background:#FFF3D6;color:#8A5A00;';
const CK_OK='font-size:12.5px;font-weight:700;padding:6px 10px;border-radius:8px;background:#E4F3E9;color:#1E7A4C;';
function ckList(ck,okT){ const l=ck.bloq.map(b=>({t:'Bloqueia · '+b.t+(b.h?' '+b.h:'')+(b.dono?' · '+b.dono:''),st:CK_RED})).concat(ck.av.map(a=>({t:'Aviso · '+a.t,st:CK_YEL})));
  if(!ck.bloq.length&&okT) l.push({t:okT,st:CK_OK}); return l; }
function detId(self){ const h=(self.state.det||'').split(':')[0]; return h||'OS-0419'; }
function hm2min(d,h){ const k=irrDeIso(d); const m=/^(\d{1,2}):(\d{2})$/.exec(String(h||'')); if(k===null||!m) return null; return k*1440+Number(m[1])*60+Number(m[2]); }
function fechar(self,k){ const p={}; p[k]=null; self.setState(p); try{ if(location.hash.indexOf(':')>0) history.replaceState(null,'',location.pathname+'#'+detId(self)); }catch(e){} }
function abrirAcao(self,ac){ const s=irrGet(); const o=s.ordens[detId(self)]; if(!o) return; const x=s.setores[o.setor];
  const nv=irrAcaoVale(s,o,ac); if(nv){ self.setState({g2toast:nv}); try{ if(location.hash.indexOf(':')>0) history.replaceState(null,'',location.pathname+'#'+o.id); }catch(e){} return; }
  if(ac==='janela'){ const ps=o.passadas.filter(p=>p.st==='Programada'); const sug=irrSugerir(s,o.setor,ps.map(p=>p.dur),s.agora,o.id);
    self.setState({jn:{ps:ps.map((p,i)=>{ const q=p.ini!==null?p.ini:sug[i]; return {n:p.n,d:q===null?'':irrIso(irrDiaN(q)),h:q===null?'':irrHm(q)}; })}}); }
  else if(ac==='conflito') self.setState({cf:{i:0}});
  else if(ac==='termino'){ const p=irrPassAtual(o); if(!p) return; self.setState({tm:{full:true,cob:'',vol:String(irrTele(s,o,p,x.ha))}}); }
  else if(ac==='conferir') self.setState({cm:{vol:o.conf&&o.conf.med?String(o.conf.med):''}}); }
function PREVALS(self,v){ irrOuvir(self);
  irrHashOuvir(self,(h)=>{ const id=h.split(':')[0]||'OS-0419'; self.setState({det:h||'OS-0419',jn:null,cf:null,tm:null,cm:null,av:null,rc:null}); const ac=h.split(':')[1]; if(ac) setTimeout(()=>abrirAcao(self,ac),0); });
  const s=irrGet(); const id=detId(self); const o=s.ordens[id]; v.achou=!!o; v.nao=!o; v.det_id=id; v.naoT='Ordem '+id+' não encontrada na irrigação.';
  irrFaixa(v,s,o?o.faz:null);
  if(!o){ v.det_titulo='Ordem não encontrada'; IRG('g_pas').rows=[]; IRG('g_trl').rows=[]; v.res_kv=[]; v.ex_kv=[]; v.avs=[]; return; }
  const x=s.setores[o.setor]; const F=s.faz[x.faz]; const et=irrEtapa(s,o); const sel=irrSelos(s,o); const av=irrAvisos(s,o); const cb=irrCobre(s,o); const cp=s.capt[x.capt];
  v.det_titulo=id+' · Irrigação · '+x.nome;
  const ef=o.ef||x.efic; const liq=o.lam*ef/100;
  v.res_kv=[{l:'Setor',t:x.nome+' · '+x.cult+' · '+irrN(x.ha)+' ha · '+F.nome},
    {l:'Lâmina',t:irrMm(o.lam)+' mm brutos em '+o.passadas.length+(o.passadas.length>1?' passadas de '+irrMm(o.passadas[0].lam)+' mm':' passada')+' · '+irrMm(liq)+' mm líquidos'},
    {l:'Necessidade',t:'déficit '+irrN(o.orig.d,1)+' mm · '+o.orig.t+(cb&&cb.cob!==null?' · cobre '+irrN(cb.cob,0)+' %'+(cb.resta>0.05?' · resta '+irrN(cb.resta,1)+' mm':''):(cb&&cb.prox?' · próximo ciclo':''))},
    {l:'Janela',t:irrJanO(o)},{l:'Bomba e captação',t:x.bnome+' · '+irrN(x.vazao)+' L/s · '+(cp?cp.nome+' ('+cp.st.toLowerCase()+')':'')},
    {l:'Liberação',t:o.fert?('v2 com produto · '+(irrFertEtapa(id)&&irrFertEtapa(id)!=='A liberar'?irrFertEtapa(id)+' na O.S.':'Ana (agrônoma) libera na O.S.')):(o.lib?o.lib+' · automática pela prontidão':'pendente · '+(irrChecar(s,o).bloq.map(b=>b.t+' ('+b.dono+')').join(', ')||'—'))}];
  v.avs=av.map(a=>({t:a.t,st:tagSt()}));
  // passadas (sub-detalhe)
  IRG('g_pas').rows=o.passadas.map(p=>{ const temI=p.ini!==null&&p.ini!==undefined; const i0=temI?((p.iniReal!==undefined&&p.iniReal!==null)?p.iniReal:p.ini):null;
    const sv=(o.fert&&p.st==='Programada')?['Na O.S. · v2','yellow']:(p.st==='Parcial'&&o.fert&&o.fert.exec&&o.fert.v1===p.cob?['Parcial · v1','yellow']:[p.st,{'Programada':'gray','Em execução':'green','Feita':'gray','Parcial':'yellow'}[p.st]||'gray']);
    const tc=p.cob!==null&&p.cob!==undefined, tv=p.vol!==null&&p.vol!==undefined;
    const dm=irrDurP(o,p);   /* Início, Fim e Duração da mesma janela */
    const r={id:'p'+p.n,v:{n:p.n,lam:p.lam,dur:Math.round(dm/6)/10,cob:tc?p.cob:'',vol:tv?p.vol:''},s:{n:p.n+'ª',st:sv[0]},p:{n:[{k:'txt',t:p.n+'ª'}],st:[{k:'chip',t:sv[0],c:sv[1]}]}};
    irrQ(r,'ini',i0,'a definir'); irrQ(r,'fim',temI?irrFimP(o,p):null,'a definir');
    r.p.dur=[{k:'txt',t:irrN(dm/60,1)}]; r.s.dur=irrN(dm/60,1);
    r.p.cob=[tc?{k:'txt',t:irrN(p.cob,2,1)}:{k:'mut',t:'—'}]; r.s.cob=tc?irrN(p.cob,2,1):''; r.p.vol=[tv?{k:'txt',t:irrN(p.vol)}:{k:'mut',t:'—'}]; r.s.vol=tv?irrN(p.vol):'';
    return r; });
  // execução e conferência
  const pa=irrPassAtual(o); const pz=(o.exec.pausas||[]); const pzm=pz.filter(z=>z.fim!==null&&z.fim!==undefined).reduce((a,z)=>a+(z.fim-z.ini),0);
  const ex=[{l:'Início',t:o.exec.ini!==undefined?irrQuando(o.exec.ini):'—'},{l:'Pausas',t:pz.length?pz.length+' · '+irrN(pzm)+' min'+(irrPausada(o)?' · pausada agora':''):'nenhuma'}];
  if(pa) ex.push({l:'Avanço',t:(pa.cob?irrN(pa.cob,2,1)+' de '+irrN(x.ha,2,0)+' ha ('+irrN(pa.cob/x.ha*100,0)+' %)':'sem leitura de área')+' · término previsto '+irrQuando(irrFimP(o,pa))});
  else ex.push({l:'Término',t:o.exec.fim!==undefined?irrQuando(o.exec.fim):(o.passadas.some(p=>p.ini!==null)?'previsto '+irrQuando(Math.max.apply(null,o.passadas.filter(p=>p.ini!==null).map(p=>irrFimP(o,p)))):'—')});
  const cf=o.conf; ex.push({l:'Hidrômetro',t:cf&&cf.med?irrN(cf.med)+' m³ medidos':(cf&&cf.st==='Sem leitura'?'sem leitura':'telemetria ao terminar')},
    {l:'Conferência',t:cf?(cf.med?irrN(cf.med)+' × '+irrN(cf.est)+' m³ estimados na área coberta · '+irrPct(cf.dv!==undefined?cf.dv:(cf.med-cf.est)/cf.est*100)+' (tolerância '+s.tol+' %)':'aguardando a leitura'):'automática até '+s.tol+' % de desvio'});
  const aps=x.bal?irrApsSetor(s,o.setor).filter(a=>a.os===id):[];
  ex.push({l:'Crédito no balanço',t:aps.length?aps.map(a=>irrMm(irrApNet(a))+' mm líquidos '+(irrApParc(a,x.ha)?'na faixa de '+irrN(irrApCob(a),2,1)+' ha':'no '+x.nome)+(a.osc?' (O.S.)':'')).join(' + ')+(aps.some(a=>a.prov)?' · provisório':' · definitivo'):(o.fert?'quando a O.S. apontar a área':'só com leitura do hidrômetro')});
  // saldo da passagem parcial que foi para a v2 (antes ficava na célula da área coberta das passadas)
  if(o.fert&&o.fert.exec&&o.passadas.some(p=>p.st==='Parcial'&&o.fert.v1===p.cob)) ex.push({l:'Saldo na v2',t:irrN(o.fert.area,2,0)+' ha'});
  v.ex_kv=ex;
  // Quando ordena pelo instante (ISO); a célula e o painel mostram "hoje 06:12"
  IRG('g_trl').rows=o.trilha.slice().sort((a,b)=>a.q-b.q).map((t,i)=>{ const r={id:'e'+i,v:{quando:irrQuando(t.q),rec:t.rec,ev:t.ev,quem:t.quem},s:{},p:{}}; irrQ(r,'hora',t.q); return r; });
}
function EXTRAVALS(self,v){ const s=irrGet(); const id=detId(self); const o=s.ordens[id];
  const run=(fn,after)=>{ const r=irrMudar(self,fn); if(!r.erro&&after) after(r); return r; };
  ['jn','cf','tm','cm','av','rc'].forEach(k=>{ v[k+'_open']=false; v[k+'_warn']=false; v[k+'_cancel']=()=>fechar(self,k); v[k+'_key']=(e)=>{ if(e&&e.key==='Escape') fechar(self,k); }; v[k+'_discard']=()=>fechar(self,k); v[k+'_keep']=()=>{}; });
  irrPaineis(self,['jn','cf','tm','cm','av','rc'].map(k=>[k,!!self.state[k],()=>(k==='rc'?v.rc_cancel():fechar(self,k))]));
  if(!o){ v.hs_t='Ordem não encontrada'; v.hs_st=chipSt('gray'); v.prim_btn=false; v.prim_link=true; v.prim_href='IR-03.dc.html'; v.prim_lt='Voltar às ordens'; v.pz_show=false; v.av_show=false; v.rc_show=false; return; }
  const x=s.setores[o.setor]; const et=irrEtapa(s,o); const sel=irrSelos(s,o); const p=irrProx(s,o);
  v.hs_t=[et].concat(sel.filter(z=>!z.mut).map(z=>z.t)).join(' · '); v.hs_st=chipSt(sel.some(z=>z.c==='red')?'red':(sel.some(z=>z.c==='yellow')?'yellow':IRR_COR[et]||'gray'));
  // ação primária pelo estado
  v.prim_btn=false; v.prim_link=false; v.prim_href='#'; v.prim_lt=''; v.prim_t=''; v.prim_fn=()=>{};
  if(!p){ }
  else if(p.h.indexOf('IR-03det')!==0){ v.prim_link=true; v.prim_href=p.h; v.prim_lt=p.t; }
  else { v.prim_btn=true; v.prim_t=p.t; const ac=(p.h.split(':')[1]||'');
    v.prim_fn=ac?(()=>abrirAcao(self,ac)):(/^Retomar/.test(p.t)?(()=>run(s0=>irrRetomar(s0,id))):(()=>run(s0=>irrIniciar(s0,id)))); }
  // ações secundárias válidas no estado
  v.pz_show=et==='Em execução'&&!!irrPassAtual(o)&&!o.fert; v.pz_t=irrPausada(o)?'Retomar':'Pausar'; v.pz_fn=()=>run(s0=>irrPausada(s0.ordens[id])?irrRetomar(s0,id):irrPausar(s0,id));
  v.av_show=v.pz_show&&!irrPausada(o); v.av_fn=()=>{ const pa=irrPassAtual(o); self.setState({av:{cob:pa&&pa.cob?String(pa.cob).replace('.',','):''}}); };
  v.rc_show=['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0&&!o.fert; v.rc_fn=()=>{ const d={prod:'Ureia 45%',dose:'12',mot:''}; self.setState({rc:{d,o:Object.assign({},d),err:{},warn:false}}); };
  v.jn_t='Janela'; v.det_sub='';
  // ---- painel: definir janela (data e hora por passada; fim e checagens calculados) ----
  const jn=self.state.jn;
  if(jn){ v.jn_open=true; v.jn_titulo='Definir janela · '+id; v.jn_sub=x.nome+' · '+x.bnome+' · '+irrMm(o.lam)+' mm em '+o.passadas.length+(o.passadas.length>1?' passadas':' passada')+' · intervalo mínimo '+irrN(x.imin)+' h';
    const tmp=irrClone(o); const pend=tmp.passadas.filter(p=>p.st==='Programada'); let falta=false;
    v.jn_ps=jn.ps.map((q,i)=>{ const ini=hm2min(q.d,q.h); const pp=pend[i]; if(ini===null) falta=true; if(pp) pp.ini=ini;
      const set=(k)=>(e)=>{ const cur=self.state.jn; const ps=cur.ps.map((z,j)=>j===i?Object.assign({},z,{[k]:e.target.value}):z); self.setState({jn:{ps}}); };
      return {t:'Passada '+q.n+' · '+irrMm(pp?pp.lam:0)+' mm · '+irrH(pp?pp.dur:0),d:q.d,h:q.h,idd:'jn_d'+q.n,idh:'jn_h'+q.n,setD:set('d'),setH:set('h'),
        fim:ini===null?'Informe data e hora de início.':'Termina '+irrQuando(ini+(pp?pp.dur:0))+(ini<s.agora?' · começa antes de agora':'')}; });
    const oe=falta?'':irrOrdemErro(tmp); v.jn_ck=falta?[]:(oe?[{t:'Corrija · '+oe,st:CK_RED}]:ckList(irrChecar(s,tmp),'Pronta: libera ao salvar, sem aprovação (água sem produto)'));
    v.jn_sug=()=>{ const sug=irrSugerir(s,o.setor,pend.map(p=>p.dur),s.agora,id); self.setState({jn:{ps:jn.ps.map((z,i)=>sug[i]===null?z:Object.assign({},z,{d:irrIso(irrDiaN(sug[i])),h:irrHm(sug[i])}))}}); };
    v.jn_ok=()=>{ const inis=self.state.jn.ps.map(z=>hm2min(z.d,z.h)); run(s0=>irrDefinirJanela(s0,id,inis),()=>fechar(self,'jn')); }; }
  else { v.jn_ps=[]; v.jn_ck=[]; v.jn_sug=()=>{}; v.jn_ok=()=>{}; v.jn_titulo=''; v.jn_sub=''; }
  // ---- painel: resolver conflito (opções calculadas) ----
  const cf=self.state.cf;
  if(cf){ const ck=irrChecar(s,o); const ops=irrOpcoes(s,id); v.cf_open=true; v.cf_titulo='Resolver conflito · '+id; v.cf_sub=x.nome+' · '+x.bnome+' · janela atual '+irrJanO(o);
    v.cf_ck=ck.bloq.map(b=>({t:b.t+(b.h?' '+b.h:'')+(b.dono?' · '+b.dono:''),st:CK_RED}));
    v.cf_opts=ops.map((z,i)=>{ const tmp=irrClone(o); tmp.passadas.filter(p=>p.st==='Programada').forEach((p,j)=>{ p.ini=z.inis[j]; }); const c2=irrChecar(s,tmp);
      return {t:z.t,sub:c2.av.length?'Avisos: '+c2.av.map(a=>a.t).join(', '):'Sem aviso',on:(cf.i||0)===i,pick:()=>self.setState({cf:{i}})}; });
    v.cf_semop=!ops.length; v.cf_semopT='Nenhuma janela livre em 5 dias nesta bomba e captação.';
    v.cf_outra=()=>{ self.setState({cf:null}); abrirAcao(self,'janela'); };
    v.cf_ok=()=>{ const z=ops[(self.state.cf||{}).i||0]; if(!z) return; run(s0=>irrDefinirJanela(s0,id,z.inis),()=>fechar(self,'cf')); }; }
  else { v.cf_ck=[]; v.cf_opts=[]; v.cf_semop=false; v.cf_semopT=''; v.cf_outra=()=>{}; v.cf_ok=()=>{}; v.cf_titulo=''; v.cf_sub=''; }
  // ---- painel: confirmar término (área coberta + hidrômetro preenchido pela telemetria) ----
  const tm=self.state.tm;
  if(tm){ const pa=irrPassAtual(o); v.tm_open=true; v.tm_titulo='Confirmar término · '+id; v.tm_sub=x.nome+' · '+(pa?'passada '+pa.n+' · início '+irrQuando(pa.iniReal):'');
    v.tm_full=!!tm.full; v.tm_parc=!tm.full; v.tm_fullT=(x.tipo==='gotejo'?'Turno completo':'Volta completa')+' · '+irrN(x.ha,2,0)+' ha';
    v.tm_cob=tm.cob; v.tm_vol=tm.vol; const er=tm.err||{}; v.tm_ecob=er.cob||''; v.tm_ecob_has=!!er.cob; v.tm_evol=er.vol||''; v.tm_evol_has=!!er.vol;
    v.tm_hint='Leitura da telemetria da '+x.bnome+' · vazio = sem leitura, nada é creditado';
    const set=(k,val)=>(e)=>{ const cur=self.state.tm; const d=Object.assign({},cur,{[k]:val===undefined?e.target.value:val,err:{}});
      if(k==='full'&&pa){ const cob=val?x.ha:(g2num(cur.cob)||0); d.vol=val?String(irrTele(s,o,pa,x.ha)):(cob?String(irrTele(s,o,pa,cob)):''); }
      if(k==='cob'&&pa){ const c2=g2num(e.target.value); if(c2>0) d.vol=String(irrTele(s,o,pa,c2)); }
      self.setState({tm:d}); };
    v.tm_setfull=set('full',true); v.tm_setparc=set('full',false); v.tm_setcob=set('cob'); v.tm_setvol=set('vol');
    v.tm_ok=()=>{ const cur=self.state.tm; const er={}; const cob=cur.full?x.ha:irr2(g2num(cur.cob)); const vs=String(cur.vol||'').trim(); const vol=vs?g2num(vs):null;
      if(!cur.full&&!(cob>0&&cob<=x.ha)) er.cob='Área entre 0 e '+irrN(x.ha,2,0)+' ha (ex.: 11,6).'; if(vs&&!(vol>0)) er.vol='Use um número em m³ (ex.: 8.480) ou deixe vazio.';
      if(Object.keys(er).length){ self.setState({tm:Object.assign({},cur,{err:er})}); return; }
      run(s0=>irrTerminar(s0,id,cob,vol),()=>fechar(self,'tm')); }; }
  else { v.tm_full=true; v.tm_parc=false; v.tm_cob=''; v.tm_vol=''; v.tm_ecob=''; v.tm_ecob_has=false; v.tm_evol=''; v.tm_evol_has=false; v.tm_hint=''; v.tm_fullT=''; v.tm_setfull=()=>{}; v.tm_setparc=()=>{}; v.tm_setcob=()=>{}; v.tm_setvol=()=>{}; v.tm_ok=()=>{}; v.tm_titulo=''; v.tm_sub=''; }
  // ---- painel: conferir medição / informar leitura (hidrômetro validado prevalece) ----
  const cm=self.state.cm;
  if(cm){ const c=o.conf||{}; v.cm_open=true; v.cm_titulo=(c.st==='Sem leitura'?'Informar leitura · ':'Conferir medição · ')+id; v.cm_sub=x.nome+' · hidrômetro × estimativa na área coberta · tolerância '+s.tol+' %';
    const ps=o.passadas.filter(p=>p.st==='Feita'||p.st==='Parcial'); const cob=ps.reduce((a,p)=>Math.max(a,p.cob||0),0);
    v.cm_kv=[{l:'Estimado',t:irrN(c.est||0)+' m³ · '+irrMm(o.passadas[0].lam)+' mm em '+irrN(cob,2,1)+' ha'},{l:'Medido',t:c.med?irrN(c.med)+' m³ · '+irrPct((c.med-c.est)/c.est*100):'sem leitura'},
             {l:'Crédito',t:'volume medido ÷ área coberta × '+(o.ef||x.efic)+' %'+(cob<x.ha-1e-9?' · só na faixa coberta':'')},{l:'Área coberta',t:irrN(cob,2,1)+' de '+irrN(x.ha,2,0)+' ha'}];
    v.cm_vol=cm.vol; v.cm_evol=(cm.err||''); v.cm_evol_has=!!cm.err; v.cm_setvol=(e)=>self.setState({cm:{vol:e.target.value,err:''}});
    v.cm_ok=()=>{ const vs=String(self.state.cm.vol||'').trim(); const vol=g2num(vs); if(!(vol>0)){ self.setState({cm:{vol:vs,err:'Informe a leitura em m³ (ex.: 1.206).'}}); return; }
      run(s0=>irrConferir(s0,id,vol),()=>fechar(self,'cm')); }; }
  else { v.cm_kv=[]; v.cm_vol=''; v.cm_evol=''; v.cm_evol_has=false; v.cm_setvol=()=>{}; v.cm_ok=()=>{}; v.cm_titulo=''; v.cm_sub=''; }
  // ---- painel: registrar avanço (telemetria e manual do mesmo evento = um registro) ----
  const avs=self.state.av;
  if(avs){ v.av_open=true; v.av_titulo='Registrar avanço · '+id; v.av_sub=x.nome+' · passada '+((irrPassAtual(o)||{}).n||'')+' em execução · área pelo ângulo do pivô ou app de campo';
    v.av_cob=avs.cob; v.av_ecob=avs.err||''; v.av_ecob_has=!!avs.err; v.av_setcob=(e)=>self.setState({av:{cob:e.target.value,err:''}});
    v.av_ok=()=>{ const c2=irr2(g2num(self.state.av.cob)); if(!(c2>=0&&c2<=x.ha)){ self.setState({av:{cob:self.state.av.cob,err:'Área entre 0 e '+irrN(x.ha,2,0)+' ha.'}}); return; } run(s0=>irrAvanco(s0,id,c2),()=>fechar(self,'av')); }; }
  else { v.av_cob=''; v.av_ecob=''; v.av_ecob_has=false; v.av_setcob=()=>{}; v.av_ok=()=>{}; v.av_titulo=''; v.av_sub=''; }
  // ---- painel: adicionar produtos (v2 da mesma ordem, liberada pelo agrônomo na O.S.) ----
  const rc=self.state.rc;
  if(rc){ const exec=(o.etapa==='Em execução'); v.rc_open=true; v.rc_titulo='Adicionar produtos · '+id; v.rc_sub=x.nome+' · versão v2 (fertirrigação) · mesmo setor, janela e saldo';
    v.rc_prod=rc.d.prod; v.rc_dose=rc.d.dose; v.rc_mot=rc.d.mot; const n=g2num(rc.d.dose); const pa=irrPassAtual(o); const area=irrAreaV2(x,pa);   /* a mesma área da v2 (irrReclassificar) */
    const bq=pa?[]:irrChecar(s,o).bloq;
    const zv=(n>0&&n<=50)?irrV2Zero(o,x,pa,n):''; v.rc_prev=zv?zv:bq.length?('Resolva antes: '+bq.map(b=>b.t+(b.h?' '+b.h:'')).join(', ')+'.'):((exec?'A ordem continua Em execução com selo Revisão de saldo pendente; '+(pa?irrN(pa.cob||0,2,0)+' ha já cobertos ficam na v1 e o saldo de '+irrN(area,2,0)+' ha para até a liberação.':'as próximas passadas esperam a liberação.'):'A ordem volta a A liberar e a liberação da água é revogada.')+' Ana (agrônoma) libera na O.S.; a liberação reserva '+((n>0&&n<=50)?irrN(cenQtd(n,area),2):'—')+' kg no estoque (falta bloqueia).');
    const set=(k)=>(e)=>{ const cur=self.state.rc; const d=Object.assign({},cur.d,{[k]:e.target.value}); const er=Object.assign({},cur.err); delete er[k]; self.setState({rc:Object.assign({},cur,{d,err:er,warn:false})}); };
    v.rc_setprod=set('prod'); v.rc_setdose=set('dose'); v.rc_setmot=set('mot');
    ['prod','dose','mot'].forEach(k=>{ v['rc_e'+k]=(rc.err||{})[k]||''; v['rc_e'+k+'_has']=!!(rc.err||{})[k]; });
    const dirty=()=>{ const cur=self.state.rc; return Object.keys(cur.d).some(k=>String(cur.d[k])!==String(cur.o[k])); };
    v.rc_warn=!!rc.warn; v.rc_cancel=()=>{ if(dirty()) self.setState({rc:Object.assign({},self.state.rc,{warn:true})}); else self.setState({rc:null}); };
    v.rc_discard=()=>self.setState({rc:null}); v.rc_keep=()=>self.setState({rc:Object.assign({},self.state.rc,{warn:false})});
    v.rc_ok=()=>{ const cur=self.state.rc; const er={}; const dn=g2num(cur.d.dose); if(isNaN(dn)||dn<=0) er.dose='Use um número maior que zero (ex.: 12).'; else if(dn>50) er.dose='Máximo 50 kg/ha por evento.';
      if(!String(cur.d.mot||'').trim()) er.mot='Informe o motivo agronômico.'; if(Object.keys(er).length){ self.setState({rc:Object.assign({},cur,{err:er})}); return; }
      const r=irrReclassTudo(self,id,{prod:cur.d.prod,dose:dn,mot:cur.d.mot}); if(!r.erro) self.setState({rc:null}); }; }
  else { v.rc_prod=''; v.rc_dose=''; v.rc_mot=''; v.rc_prev=''; v.rc_setprod=()=>{}; v.rc_setdose=()=>{}; v.rc_setmot=()=>{}; ['prod','dose','mot'].forEach(k=>{ v['rc_e'+k]=''; v['rc_e'+k+'_has']=false; }); v.rc_ok=()=>{}; v.rc_titulo=''; v.rc_sub=''; }
}
'''
    acoes=[sbtn('pz_show',H('pz_t'),'pz_fn','pause','Pausar ou retomar a passada em execução (a pausa vira selo)'),
           sbtn('av_show','Registrar avanço','av_fn','flag','Área coberta até agora (telemetria ou app de campo)'),
           sbtn('rc_show','Adicionar produtos','rc_fn','plus','Cria a versão v2 desta ordem como fertirrigação')]
    corpo=(f'<sc-if value="{H("nao")}" hint-placeholder-val="{F()}"><div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; padding: 28px; font-size: 14px; font-weight: 600;">{H("naoT")}</div></sc-if>'
           + f'<sc-if value="{H("achou")}" hint-placeholder-val="{T()}">'
           + section('Resumo','','',kvfor('res_kv')+f'<div style="margin-top: 12px;">{chipsfor("avs")}</div>')
           + section('Passadas','','',g_pas)
           + section('Execução e conferência','',acoes,kvfor('ex_kv'))
           + section('Trilha e recibos','','',g_trl) + '</sc-if>')
    prim=(f'<span style="{H("hs_st")}">{H("hs_t")}</span><span style="width: 8px;"></span>'
          f'<sc-if value="{H("prim_btn")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("prim_fn")}" style="{BTN_ST(True)}">{H("prim_t")}</button></sc-if>'
          f'<sc-if value="{H("prim_link")}" hint-placeholder-val="{F()}"><a href="{H("prim_href")}" style="{BTN_ST(True)} text-decoration: none;">{H("prim_lt")}</a></sc-if>')
    shell37('IR-03','{{det_titulo}}',corpo,fname=fname,crumbs_extra=['Ordens','{{det_id}}'],primary_html=prim,steps=faixa(3),search=False)
    # título da aba do navegador é fixo; a trilha leva às Ordens (3º nível)
    _corrige(fname,[('<title>{{det_titulo}}</title>','<title>Ordem de irrigação</title>'),
                    (f'<span style="color: {MUTED};">Ordens</span>',f'<a href="IR-03.dc.html" style="color: {MUTED}; text-decoration: none;">Ordens</a>')])

# =====================================================================================
def ir04():
    fname='IR-04.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000
    # uma variável por coluna (TABELAS-FOCO, 04/10/2026): grandezas e unidades da fonte (listas na mesma ordem: a estação mede ET₀, chuva e vento), atualização (ordena como data), calibração (chip) e a
    # validade dela (data), cobertura, estado (chip; o motivo da suspeita vai para o painel) e efeito no balanço. Fazenda só com "Todas"
    # revisão TABR (A1, 09/10): o estado logo depois da fonte (à vista sem rolar)
    g_src=grid([dict(k='nome',l='Fonte',w=130),dict(k='faz',l='Fazenda',w=110),dict(k='estado',l='Estado',w=120),dict(k='gr',l='Grandeza',multi=True,w=110),dict(k='un',l='Unidade',multi=True,w=90),
                dict(k='at',l='Atualização',t='date',w=110),dict(k='calst',l='Calibração',w=120),dict(k='cal',l='Validade da calibração',t='date'),dict(k='cob',l='Cobertura',w=100),
                dict(k='efe',l='Efeito no balanço',w=110)],[],
               edit=dict(m='form',title='Fonte',newTitle='Cadastrar sensor',sub='O estado vem das leituras validadas.',
                   fields=[dict(k='nome',l='Nome',t='txt',req=True),dict(k='gr',l='Grandeza',t='sel',req=True,newOnly=True,opts=['Umidade do solo','Volume','ET₀ / chuva / vento'],**{'def':'Umidade do solo'}),
                           dict(k='cob',l='Cobertura',t='sel',req=True,newOnly=True,opts=['Pivô 1','Pivô 2','Gotejo T7','Fazenda'],**{'def':'Pivô 2'}),
                           dict(k='cal',l='Próxima calibração',t='date')]),
               gid='g_src',total=False,add='Cadastrar sensor',search=False)
    # captação: outorga, vazão outorgada (L/s) e regime (h/dia), vencimento, situação, volume de hoje (m³) e uso do dia (%), setores ligados (lista)
    g_cap=grid([dict(k='nome',l='Captação',w=200),dict(k='faz',l='Fazenda',w=110),dict(k='st',l='Situação',w=120),dict(k='outorga',l='Outorga',w=130),dict(k='ls',l='Vazão outorgada',t='num',a='r',un='L/s'),
                dict(k='h',l='Regime',t='num',a='r',un='h/dia'),dict(k='venc',l='Vencimento',t='date'),
                dict(k='vol',l='Volume hoje',t='num',a='r',un='m³'),dict(k='pct',l='Uso do dia',t='num',a='r',un='%'),dict(k='set',l='Setores ligados',multi=True,w=150)],[],
               edit=dict(m='ro',title='Captação',fields=[dict(k='nome',l='Captação',ro=True),dict(k='outT',l='Outorga',ro=True),dict(k='obs',l='Observação',ro=True)]),gid='g_cap',total=False,search=False)
    # desempenho: cultura em coluna própria; a variação da eficiência sobre a quinzena anterior é número (%); a sonda sem dado aparece em Fontes
    drows=[R('p2',o=['Hidrômetro · Pivô 2 · 32.480 m³ (09–22/09)','Medidor de energia · bomba B2 · 23.370 kWh','Eficiência = volume ÷ energia · lâmina = volume ÷ 80 ha'],
             setor=[Pt.b('Pivô 2')],cult='Milho',vol=32480,kwh=23370,lam=40.6,ef=1.39,var=(4,[Pt.cn('+4','green')])),
           R('p1',o=['Hidrômetro · Pivô 1 · 34.580 m³ (09–22/09)','Medidor de energia · bomba B1 · 25.610 kWh','Lâmina = volume ÷ 95 ha'],
             setor=[Pt.b('Pivô 1')],cult='Feijão',vol=34580,kwh=25610,lam=36.4,ef=1.35,var=(0,[Pt.txt('0')])),
           R('t7',o=['Hidrômetro · Gotejo T7 · 10.080 m³ (09–22/09)','Medidor de energia · bomba B3 · 5.760 kWh','Lâmina = volume ÷ 42 ha','Variação: sem quinzena anterior comparável (sonda sem dado desde 20/09)'],
             setor=[Pt.b('Gotejo T7')],cult='Mamão',vol=10080,kwh=5760,lam=24.0,ef=1.75,var='')]
    g_des=grid([dict(k='setor',l='Setor'),dict(k='cult',l='Cultura'),dict(k='vol',l='Volume',t='num',a='r',un='m³',agg='sum'),dict(k='kwh',l='Energia',t='num',a='r',un='kWh',agg='sum'),
                dict(k='lam',l='Lâmina aplicada',t='num',a='r',un='mm',d=1),dict(k='ef',l='Eficiência',t='num',a='r',un='m³/kWh',d=2),
                dict(k='var',l='Variação da eficiência',t='num',a='r',un='%')],drows,
               edit=dict(m='origin',title='Desempenho',fields=[dict(k='setor',l='Setor',ro=True),dict(k='cult',l='Cultura',ro=True),dict(k='vol',l='Volume (m³)',ro=True),dict(k='kwh',l='Energia (kWh)',ro=True),dict(k='ef',l='Eficiência (m³/kWh)',ro=True)]),
               gid='g_des',search=False)
    EXTRAJS[0]=prefixo()+JS_COMUM+r'''
function br(s){ const a=String(s||'').split('-'); return a.length===3?a[2]+'/'+a[1]+'/'+a[0]:s; }
const ESTC={'Ativa':'green','Suspeita':'red','Sem dado':'yellow','Aguardando 1ª leitura':'gray','Previsão':'gray'};
// a unidade vem da grandeza (não se pede de novo e não diverge dela): uma unidade por grandeza, na mesma ordem
const UN_GR={'Umidade do solo':'% vol.','Volume':'m³','ET₀ / chuva / vento':'mm/dia · mm · km/h'};
function PREVALS(self,v){ irrOuvir(self); const s=irrGet(); const fz=irrFazK(self); irrFazVals(self,v); const c=irrFaixa(v,s,fz);
  const fs=Object.keys(s.fontes).filter(k=>!fz||s.fontes[k].faz===fz);
  irrColsFaz('g_src',fz,v,'src_ncol'); irrColsFaz('g_cap',fz,v,'cap_ncol');
  IRG('g_src').rows=fs.map(k=>{ const f=s.fontes[k]; let cs; if(!f.cal) cs=['Não se aplica','gray']; else { const d=irrDeIso(f.cal); cs=d<0?['Vencida','red']:(d<=7?[(f.calAg?'Agendada':'Vence em 7 dias'),'yellow']:['Em dia','green']); }
    const stT=f.st==='Previsão'?'Só previsão':f.st;
    const x=f.setor?s.setores[f.setor]:null; const efe=f.st==='Previsão'?'não entra como chuva':(f.gr==='Volume'?'crédito das irrigações':(f.gr.indexOf('ET')===0?'ETc dos setores':(x?(f.st==='Ativa'?x.nome+' medido':x.nome+' por estimativa de ET (≈)'):(f.st==='Aguardando 1ª leitura'?'nada sem leitura validada':'balanço da fazenda'))));
    const r={id:k,ro:!!f.ro,v:{nome:f.nome,gr:f.gr,un:f.un,cob:f.cob,cal:f.cal||''},s:{},p:{}};
    irrTxt(r,'nome',f.nome,true); irrTxt(r,'faz',s.faz[f.faz].nome); irrLst(r,'gr',String(f.gr||'').split(' / ').filter(Boolean).map(t=>({t:t.charAt(0).toUpperCase()+t.slice(1)}))); irrLst(r,'un',String(f.un||'').split(' · ').filter(Boolean).map(t=>({t}))); irrQ(r,'at',(f.at===null||f.at===undefined)?null:f.at);
    r.p.calst=[cs[0]==='Não se aplica'?{k:'tag',t:cs[0]}:{k:'chip',t:cs[0],c:cs[1]}]; r.s.calst=cs[0];
    r.p.cal=[f.cal?{k:'txt',t:br(f.cal)}:{k:'mut',t:'—'}]; r.s.cal=f.cal?br(f.cal):''; irrTxt(r,'cob',f.cob);
    r.p.estado=[{k:'chip',t:stT,c:ESTC[f.st]||'gray'}]; r.s.estado=stT; r.p.efe=[{k:f.st==='Ativa'?'mut':'txt',t:efe}]; r.s.efe=efe;
    return r; });
  const cs=Object.keys(s.capt).filter(k=>!fz||s.capt[k].faz===fz);
  IRG('g_cap').rows=cs.map(k=>{ const cp=s.capt[k]; const ss=Object.keys(s.setores).filter(z=>s.setores[z].capt===k&&s.setores[z].bal);
    const ws=irrComprometidas(s,null).filter(w=>w.capt===k); let vol=0; ws.forEach(w=>{ const a=Math.max(0,w.ini),b=Math.min(1440,w.fim); if(b>a) vol+=w.ls*(b-a)*0.06; }); const pct=vol/(cp.ls*cp.h*3.6)*100;
    const r={id:k,v:{ls:cp.ls,h:cp.h,venc:cp.venc,nome:cp.nome,vol:Math.round(vol),pct:Math.round(pct),outT:cp.outorga+' · '+irrN(cp.ls)+' L/s × '+cp.h+' h/dia',obs:cp.obs||'—'},s:{},p:{}};
    irrTxt(r,'nome',cp.nome,true); irrTxt(r,'faz',s.faz[cp.faz].nome); irrTxt(r,'outorga',cp.outorga);
    r.p.st=[{k:'chip',t:cp.st,c:{'Vigente':'green','Em renovação':'yellow','Vencida':'red'}[cp.st]||'gray'}]; r.s.st=cp.st;
    r.p.vol=[{k:'txt',t:irrN(vol)}]; r.s.vol=irrN(vol); r.p.pct=[{k:'txt',t:irrN(pct,0)}]; r.s.pct=irrN(pct,0);
    irrLst(r,'set',ss.map(z=>({t:s.setores[z].nome}))); return r; });
  v.hs_t=c.sensT||'Fontes em dia'; v.hs_st=chipSt(c.sens?'yellow':'green');
  v.des=fz!=='LG'&&fz!=='BV'; v.tem=fz!=='BV'; v.vazio=fz==='BV'; v.vazioT='Boa Vista não tem fonte de clima ou sensor cadastrado.'; }
function EXTRAVALS(self,v){ const fz=irrFazK(self);
  // painel da fonte: o motivo do estado (suspeita, sem dado desde) no subtítulo, fora da célula
  const FS=v.g_src_F, fs0=g2st(self,'g_src').fm; if(FS&&FS.open&&fs0&&fs0.rid){ const f=irrGet().fontes[fs0.rid]; if(f&&f.st!=='Ativa') FS.sub=(f.st==='Previsão'?'Só previsão':f.st)+(f.motivo?' · '+f.motivo:'')+(f.desde!==undefined?' · desde '+irrQuando(f.desde):'')+'. O estado vem das leituras validadas.'; }
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_src'||!r) return; g2set(self,'g_src',{rows:null,fl:isNew?null:r.id});
    if(isNew) irrMudar(self,s=>irrFonteNova(s,{faz:fz||'SR',nome:r.v.nome,gr:r.v.gr,un:UN_GR[r.v.gr]||'',cob:r.v.cob,cal:r.v.cal}));
    else irrMudar(self,s=>{ const f=s.fontes[r.id]; if(!f) throw new Error('Fonte não encontrada.'); f.nome=String(r.v.nome||f.nome).trim(); const mudouCal=(r.v.cal||'')!==(f.cal||''); if(mudouCal&&r.v.cal) return irrCalibrar(s,r.id,r.v.cal); return {msg:'Cadastro de '+f.nome+' salvo.'}; }); };
  self.g2formActs=(gid,r)=>{ if(gid!=='g_src') return []; const s=irrGet(); const f=s.fontes[r.id]; if(!f||f.ro) return []; const out=[]; const fechar=()=>g2set(self,'g_src',{fm:null});
    if(f.st==='Ativa'&&f.gr==='Umidade do solo') out.push({t:'Marcar leitura suspeita',h:'Sai do balanço até a inspeção; o setor passa a estimativa por ET em todas as telas.',go:()=>{ fechar(); irrMudar(self,s0=>irrSondaMarcar(s0,r.id,'Suspeita','marcada na conferência')); }});
    if(f.st==='Suspeita') out.push({t:'Validar leitura',h:'Volta ao balanço com a medição.',go:()=>{ fechar(); irrMudar(self,s0=>irrSondaMarcar(s0,r.id,'Ativa')); }});
    return out; }; }
'''
    corpo=(vazio('vazio','vazioT','Cadastrar sensores','CD-03.dc.html')
           + f'<sc-if value="{H("tem")}" hint-placeholder-val="{T()}">'
           + section('Fontes e sensores','','',g_src) + section('Captações e outorgas','','',g_cap)
           + f'<sc-if value="{H("des")}" hint-placeholder-val="{T()}">'+section('Desempenho por setor · 09–22/09','','',g_des)+'</sc-if></sc-if>')
    prim=f'<span style="{H("hs_st")}">{H("hs_t")}</span>'
    shell37('IR-04','Clima e sensores',corpo,fname=fname,crumbs_extra=['Clima e sensores'],primary_html=prim,steps=faixa(4),search=False)
    ncol_dinamico(fname,['src_ncol','cap_ncol'])

def build():
    ir01(); ir02(); ir03(); ir03det(); ir04()
