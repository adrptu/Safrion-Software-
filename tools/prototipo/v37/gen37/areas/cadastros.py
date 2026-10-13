# -*- coding: utf-8 -*-
"""Cadastros (menu vigente) — CD-01 Fazendas, áreas e talhões (+ CD-01det talhão T1) · CD-02 Culturas, cultivares e operações ·
CD-03 Máquinas, instalações e setores · CD-04 Pessoas e equipes · CD-05 Parceiros e fornecedores · CD-06 Produtos, unidades e locais ·
CD-07 Estrutura gerencial.
Padrão G2: cada tabela é grid(); clicar na linha abre o formulário lateral tipado (listas com cadastros existentes, números com unidade e
mínimo, datas, campos condicionais); exclusão confirmada só onde permitido; registros protegidos abrem em consulta.
Dados: dados2 (processos: cultivos, conjuntos/rendimentos, fornecedores, estoque/lotes, pedidos) e dados (mundo DEMO: talhões, lote bloqueado)."""
import json, os
from engine import grid, esc, _MINI, BTN_ST, EXTRAJS, INK, MUTED, LINE, BG, SURF
import engine as E
import ui37
from ui37 import shell37, continuity, HEIGHTS37, PARENT37, farm_map
import dados as D
import dados2 as D2
import dados_cad as DC   # item caixa do packing com massa e tara (BEN-1)

H=lambda s: '{{'+s+'}}'
# alturas antigas medidas pelo qa37 valiam para o layout anterior; as telas novas definem a própria altura
for _f in ('CD-01.dc.html','CD-01det.dc.html','CD-06.dc.html'): ui37.H_OVR.pop(_f,None)

# ---------------- blocos e botões (padrão do exemplar processo_safra) ----------------
def bloco(titulo,desc,corpo,acao=''):
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; gap: 8px; flex-shrink: 0;">{acao}</div></div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def novo(gid,rotulo):
    """botão primário da tela: abre o formulário de novo registro da grade (buraco {{gid_new}})."""
    return f'<button type="button" onClick="{H(gid+"_new")}" style="{BTN_ST(True)}">{esc(rotulo)}</button>'
def mini(fn,rotulo,dica=''):
    t=f' title="{esc(dica)}"' if dica else ''
    return f'<button type="button" onClick="{H(fn)}"{t} style="{_MINI}">{esc(rotulo)}</button>'
def nota(t): return f'<div style="font-size: 12px; color: {MUTED}; padding: 8px 4px 0;">{esc(t)}</div>'
def sel(k,l,opts,req=True,**kw): return dict(k=k,l=l,t='sel',opts=list(opts),req=req,**kw)
def num(k,l,u=None,req=True,**kw):
    d=dict(k=k,l=l,t='num',req=req,**kw)
    if u: d['u']=u
    return d
def txt(k,l,req=True,**kw): return dict(k=k,l=l,t='txt',req=req,**kw)
def dat(k,l,req=True,**kw): return dict(k=k,l=l,t='date',req=req,**kw)
def cond(k,eq): return dict(k=k,eq=eq)
def R(id,v,**kw): return dict(id=id,v=v,s={},p={},**kw)

# ---------------- JS comum às telas de cadastro ----------------
CDJS=r'''
function GR(id){ return GRIDS.find(g=>g.id===id); }
function RW(self,id){ return g2rows(self,GR(id)); }
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function nfa(n){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:2}); }
function br(s){ if(!s) return '—'; const a=String(s).split('-'); return a.length===3? a[2]+'/'+a[1]+'/'+a[0] : String(s); }
function ml(s){ return String(s||'').split(';').map(x=>x.trim()).filter(Boolean); }
const HOJE='2026-09-23';
function ddiff(a,b){ return Math.round((new Date(b+'T12:00:00')-new Date(a+'T12:00:00'))/86400000); }
function addd(s,n){ const d=new Date(s+'T12:00:00'); d.setDate(d.getDate()+Number(n||0)); return d.toISOString().slice(0,10); }
function leaves(list){ const o=[]; const w=l=>l.forEach(r=>{ if(r.kids&&r.kids.length) w(r.kids); else o.push(r); }); w(list); return o; }
function isnum(x){ return x!==''&&x!==null&&x!==undefined&&!isNaN(Number(x)); }
// exclusão só onde permitido: linha protegida (ro/nd) mostra o motivo no lugar da lixeira; linha-grupo fica vazia
function protege(self,v,gid){ const rows=RW(self,gid); (v[gid+'_rows']||[]).forEach(rr=>{ const r=g2find(rows,rr.id); if(!r) return;
  const grp=!!(r.kids&&r.kids.length); const why=grp?'':(r.ro?'somente consulta':(r.nd||'')); if(!grp&&!why) return;
  rr.cells.forEach(c=>{ if(c.isDel){ c.isDel=false; c.isData=true; c.hasCaret=false; c.parts=why?[g2part({k:'mut',t:why},v)]:[]; } }); }); }
// validação do motor + regras do cadastro; erros junto ao campo, preenchimento preservado
function basic(sp,fm){ const e={}; (sp.edit.fields||[]).filter(f=>!f.cond||String(fm.draft[f.cond.k])===String(f.cond.eq)).forEach(f=>{ if(f.ro) return; const val=String(fm.draft[f.k]||'').trim();
  if(f.req&&!val){ e[f.k]=(f.t==='multi'?'Escolha ao menos uma opção.':'Informe '+f.l.toLowerCase().replace(/ \(.*\)$/,'')+'.'); return; }
  if(f.t==='email'&&val&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val)){ e[f.k]='E-mail inválido (ex.: compras@empresa.com.br).'; return; }
  if(f.t==='tel'&&val){ const dg=val.replace(/\D/g,''); if(dg.length<10||dg.length>13){ e[f.k]='Informe DDD e número (ex.: 65 99999-0000).'; return; } }
  if(f.t==='num'&&val){ const n=g2num(val); if(isNaN(n)){ e[f.k]='Use um número (ex.: 12,5).'; return; } if(f.min!==undefined&&n<f.min){ e[f.k]='Mínimo '+String(f.min).replace('.',',')+(f.u?' '+f.u:'')+'.'; return; } if(f.max!==undefined&&n>f.max){ e[f.k]='Máximo '+String(f.max).replace('.',',')+(f.u?' '+f.u:'')+'.'; return; } } }); return e; }
function valida(self,v,gid,fn){ const F=v[gid+'_F']; if(!F||!F.open||!F.edit) return; const sp=GR(gid);
  F.save=()=>{ const fm=g2st(self,gid).fm; if(!fm) return; const e=Object.assign(basic(sp,fm),fn(fm.draft,fm)||{});
    if(Object.keys(e).length){ g2set(self,gid,{fm:Object.assign({},fm,{errs:e,warn:false})}); return; } g2save(self,sp); }; }
function unico(self,gid,fm,key,val){ const k=String(val||'').trim().toLowerCase(); if(!k) return null; return leaves(RW(self,gid)).find(r=>r.id!==fm.rid && key(r)===k)||null; }
function simv(self,v){ Object.keys(SIMS).forEach(k=>{ v['sim_'+k]=()=>self.setState({g2toast:SIMS[k]}); }); }
function chipc(t,c){ return {k:'chip',t:t,c:c}; }
'''+open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'cadls.js'),encoding='utf-8').read()+r'''
'''
def js(sims,code):
    EXTRAJS[0]='const SIMS = '+json.dumps(sims,ensure_ascii=False)+';\n'+CDJS+CADXJS+code

# =====================================================================================
# Padrão visual dos cadastros (redesenho de 01/10/2026, pedido do Adrianus: "mais moderno, organizado, bonito e intuitivo").
# Um bloco por tela (section.cadx): abas por entidade na 1ª linha; em cada aba, a faixa "precisa de atenção" (cartões com
# verbo), a barra da grade (busca, contagem, filtro rápido Todos · A resolver, ações da aba com a primária por último) e os
# dados. Só a área de dados rola (cabeçalho da tabela fixo); título, abas, filtros e ações ficam parados.
# Estado do cabeçalho em uma linha (ponto + texto na cor do estado), sem botão de ação de entidade no cabeçalho da página.
CADX_CSS=(
    "main:has(>.cadx){gap:0}"
    ".cadx{flex:1 1 0;min-height:0;display:flex;flex-direction:column;min-width:0;background:#FFFFFF;border:1px solid #E4E9E5;border-radius:14px;overflow:hidden}"
    ".cadx-topo{display:flex;align-items:center;gap:12px;padding:12px 16px 0;flex-wrap:wrap}"
    ".cadx-abas{display:inline-flex;gap:2px;padding:3px;border-radius:999px;background:#EEF1EE;max-width:100%;overflow-x:auto}"
    # I33 (achado 11): abaixo de 1024 px as abas ficam inteiras (sem rolagem lateral escondida): menos folga e, se faltar largura, outra linha
    "@media (max-width:1023px){.cadx-abas{flex-wrap:wrap;overflow-x:visible;border-radius:14px}.cadx-abas>[role=tab]{padding-left:7px!important;padding-right:7px!important;gap:4px!important}}"
    ".cadx-dados{flex:1 1 0;min-height:0;display:flex;flex-direction:column}.cadx-ident{border-bottom:1px solid #E4E9E5}"
    ".cadx-dados .g2caixa{flex:1 1 0;min-height:0}.cadx-dados .g2rola{flex:1 1 0;min-height:0;overflow:auto}"
    ".cadx-rola{flex:1 1 0;min-height:0;overflow:auto}"
    # barra da grade: busca e contagem, filtro rápido, filtros ativos ... ações da aba, expandir/recolher, primária por último
    ".cadx .g2caixa>div:first-child:has(>span),.cadx-barra{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:10px 16px;border-bottom:1px solid #E4E9E5}"
    ".cadx .g2caixa>div:first-child>label:has(input[type=search]),.cadx .g2caixa>div:first-child>label:has(input[type=search])+span{order:-2}"
    ".cadx-qf{order:-1;display:flex;flex-wrap:wrap;gap:6px}.cadx-prim{order:1;display:inline-flex;margin-left:auto}"
    ".cadx-seg{display:inline-flex;gap:2px;padding:3px;border-radius:999px;background:#EEF1EE}"
    # cabeçalho da coluna em caixa normal, numa linha; ordenação sempre visível
    ".cadx .g2hb{text-transform:none;letter-spacing:0;font-size:12px;white-space:nowrap;max-width:none;line-height:1.2;padding:10px 2px 10px 0}"
    # linhas de uma altura (44 px), texto 13,5 px; links e ações da célula em tinta, não em verde
    ".cadx .g2rola [role=row]{font-size:13.5px!important}.cadx [role=cell]{min-height:44px;box-sizing:border-box}"
    ".cadx .g2pw{flex-wrap:nowrap;white-space:nowrap;overflow:hidden}"
    # texto que não cabe na largura da coluna termina em reticências (o complemento apagado encolhe primeiro; nome, chip e verbo não;
    # o motor envolve cada texto num span.sc-interp, por isso o chip é o span com outro span dentro)
    ".cadx .g2pw span{min-width:0;overflow:hidden;text-overflow:ellipsis}.cadx .g2pw b,.cadx .g2pw span:has(>span:not(.sc-interp)),.cadx .g2pw a,.cadx .g2pw button{flex-shrink:0}"
    ".cadx .g2pw a,.cadx .g2pw button{color:#15201A!important;font-weight:700}@media (hover:hover){.cadx .g2pw a:hover,.cadx .g2pw button:hover{text-decoration:underline!important}}"
    ".cadx .g2kid{background:#FFFFFF}@media (hover:hover){.cadx .g2ed:hover{background:#F4F6F3}}"
    # árvore: a linha do grupo ganha faixa clara (hierarquia sem precisar de caixa)
    ".cadx-arv .g2r:not(.g2kid) [role=cell]{background:#F7F9F6!important}@media (hover:hover){.cadx-arv .g2r.g2ed:not(.g2kid):hover [role=cell]{background:#EEF3EE!important}}"
    # faixa "precisa de atenção": cartões brancos com borda esquerda na cor do estado
    ".cadx-faixa{display:flex;gap:12px;flex-wrap:wrap;padding:12px 16px 2px}"
    ".cadx-aviso{flex:0 1 330px;min-width:240px;display:flex;flex-direction:column;align-items:flex-start;gap:6px;text-align:left;background:#FFFFFF;"
    "border:1px solid #E4E9E5;border-radius:12px;padding:10px 14px;cursor:pointer;font-family:inherit;color:#15201A}"
    "@media (hover:hover){.cadx-aviso:hover{background:#F9FBF8}.cadx-aviso:hover .cadx-verbo{text-decoration:underline}}.cadx-aviso:focus-visible,.cadx-cartao:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}"
    ".cadx-verbo{font-weight:700;color:#15201A;white-space:nowrap}"
    # cartões de entidade contêiner (fazendas, equipes, conjuntos)
    ".cadx-cartoes{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;padding:16px;align-content:start}"
    ".cadx-cartao{display:flex;flex-direction:column;align-items:stretch;gap:10px;text-align:left;background:#FFFFFF;border:1px solid #E4E9E5;border-radius:14px;"
    "padding:16px;cursor:pointer;font-family:inherit;color:#15201A;min-width:0}"
    "@media (hover:hover){.cadx-cartao:hover{border-color:#1E7A4C}.cadx-cartao:hover .cadx-verbo{text-decoration:underline}}"
    ".cc-num{font-family:'Sora','Manrope',sans-serif;font-size:20px;font-weight:800;letter-spacing:-.01em}"
    "@media (max-width:767px){.cadx-faixa,.cadx-cartoes{grid-template-columns:1fr}.cadx-aviso{flex:1 1 100%}}"
)
TAB_ON=E.SEG_ON().replace('font-size: 12.5px','font-size: 13px')
TAB_OFF=E.SEG_OFF().replace('font-size: 12.5px','font-size: 13px')
def cadx_css():
    """estilo do padrão dos cadastros (vale só dentro de .cadx e da faixa; demais telas não mudam)."""
    E.EXTRA.append('<style>'+CADX_CSS+'</style>')
def abas(pre,nomes,rotulo='Cadastros desta tela'):
    """abas por entidade: rótulo + contagem + ponto de pendência (buracos pre+i+'_st|_go|_sel|_n|_dot', ver cadAbas)."""
    bs=''.join(f'<button type="button" role="tab" aria-selected="{H(pre+str(i)+"_sel")}" onClick="{H(pre+str(i)+"_go")}" style="{H(pre+str(i)+"_st")}">{esc(n)}'
               f'<span style="font-size: 12px; font-weight: 600; color: {MUTED};">{H(pre+str(i)+"_n")}</span>'
               f'<span aria-hidden="true" style="{H(pre+str(i)+"_dot")}"></span><span class="g2sr">{H(pre+str(i)+"_sr")}</span></button>' for i,n in enumerate(nomes))
    return f'<div role="tablist" aria-label="{esc(rotulo)}" class="cadx-abas">{bs}</div>'
def pane(pre,i,html,ativo=0):
    return f'<sc-if value="{H(pre+str(i)+"_on")}" hint-placeholder-val="{H("true" if i==ativo else "false")}">{html}</sc-if>'
def se(hole,html,dflt=False):
    return f'<sc-if value="{H(hole)}" hint-placeholder-val="{H("true" if dflt else "false")}">{html}</sc-if>'
def faixa(key):
    """faixa "precisa de atenção" da aba: cartões com número, o que falta, o registro e o verbo (buracos de cadFaixa)."""
    return se(key+'_tem',
        f'<div class="cadx-faixa" role="group" aria-label="Precisa de atenção"><sc-for list="{H(key)}" as="fx" hint-placeholder-count="1">'
        f'<button type="button" class="cadx-aviso" onClick="{H("fx.go")}" style="{H("fx.st")}">'
        f'<span style="display: flex; align-items: baseline; gap: 8px;"><span style="{H("fx.nst")}">{H("fx.n")}</span><span style="font-size: 13px; font-weight: 600;">{H("fx.rot")}</span></span>'
        f'<span style="display: flex; align-items: baseline; flex-wrap: wrap; column-gap: 8px; row-gap: 2px; font-size: 12.5px; min-width: 0;"><span style="color: {MUTED}; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px;">{H("fx.reg")}</span>'
        f'<span class="cadx-verbo">{H("fx.verbo")} ›</span></span></button></sc-for></div>')
PRIM_ST=('padding: 7px 14px; border-radius: 9px; font-size: 13px; font-weight: 700; font-family: inherit; cursor: pointer; white-space: nowrap; line-height: 1.25; '
         f'background: {E.ACC}; color: #fff; border: 1px solid {E.ACC}; box-shadow: 0 1px 2px rgba(30,122,76,.25);')
SEC_ST=('padding: 7px 12px; border-radius: 9px; font-size: 13px; font-weight: 700; font-family: inherit; cursor: pointer; white-space: nowrap; line-height: 1.25; '
        f'background: {SURF}; color: {INK}; border: 1px solid {LINE};')
def prim(fn,rotulo,hole=False):
    """primária da aba (uma por aba), dentro do bloco onde age; fica por último na barra."""
    t=H(rotulo) if hole else esc(rotulo)
    return f'<span class="cadx-prim"><button type="button" onClick="{H(fn)}" style="{PRIM_ST}">{t}</button></span>'
def secbtn(fn,rotulo,dica='',hole=False):
    t=H(rotulo) if hole else esc(rotulo); d=f' title="{esc(dica)}"' if dica else ''
    return f'<button type="button" onClick="{H(fn)}"{d} style="{SEC_ST}">{t}</button>'
def qf_chips(gid):
    """filtro rápido do bloco (Todos · A resolver · ...), à esquerda da barra (buraco gid+'_cqf', ver cadQf)."""
    return (f'<div class="cadx-qf" role="group" aria-label="Filtro rápido"><sc-for list="{H(gid+"_cqf")}" as="qc" hint-placeholder-count="2">'
            f'<button type="button" aria-pressed="{H("qc.on")}" onClick="{H("qc.go")}" style="{H("qc.st")}">{H("qc.t")} <span style="opacity: .75;">{H("qc.n")}</span></button></sc-for></div>')
def filtro_sel(key,rotulo):
    """filtro de classificação do bloco (lista com contagem), ao lado do filtro rápido de estado; buracos key, key_set, key_opts."""
    return (f'<label class="cadx-qf" style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: {MUTED};">{esc(rotulo)}'
            f'<select aria-label="{esc(rotulo)}" value="{H(key)}" onChange="{H(key+"_set")}" style="{H(key+"_st")}">'
            f'<sc-for list="{H(key+"_opts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>')
def seg(pre,opcoes,rotulo):
    """alternância de visão dentro da aba (ex.: Lista | Mapa); buracos pre+i+'_st' e pre+i+'_go'."""
    bs=''.join(f'<button type="button" aria-pressed="{H(pre+str(i)+"_on")}" onClick="{H(pre+str(i)+"_go")}" style="{H(pre+str(i)+"_st")}">{esc(o)}</button>' for i,o in enumerate(opcoes))
    return f'<div role="group" aria-label="{esc(rotulo)}" class="cadx-seg">{bs}</div>'
def barra(esq,dir=''):
    """barra de uma aba sem grade (cartões, mapa): mesmo desenho da barra da grade."""
    return f'<div class="cadx-barra">{esq}<span style="flex-grow: 1;"></span>{dir}</div>'
def cartoes(key,rotulo):
    """cartões de entidade contêiner: nome, chip só com exceção, identificação, 2-3 números e rodapé com a situação (buracos de cadCartoes)."""
    num=(f'<sc-for list="{H("c.nums")}" as="n" hint-placeholder-count="3"><span style="display: flex; flex-direction: column; gap: 2px; min-width: 0;">'
         f'<span style="white-space: nowrap;"><span class="cc-num">{H("n.v")}</span> <span style="font-size: 12px; color: {MUTED};">{H("n.u")}</span></span>'
         f'<span style="font-size: 11.5px; font-weight: 600; color: {MUTED};">{H("n.l")}</span></span></sc-for>')
    return (f'<div class="cadx-rola"><div class="cadx-cartoes" role="list" aria-label="{esc(rotulo)}"><sc-for list="{H(key)}" as="c" hint-placeholder-count="2">'
            f'<button type="button" role="listitem" class="cadx-cartao" aria-label="{H("c.lab")}" onClick="{H("c.open")}">'
            f'<span style="display: flex; align-items: flex-start; gap: 8px;"><b style="font-size: 15px; font-weight: 800; flex-grow: 1; min-width: 0; line-height: 1.3;">{H("c.nome")}</b>'
            + se('c.temChip',f'<span style="{H("c.chSt")}"><span style="{H("c.chDot")}"></span>{H("c.chT")}</span>') + '</span>'
            f'<span style="font-size: 12.5px; color: {MUTED}; margin-top: -6px;">{H("c.sub")}</span>'
            f'<span style="display: flex; gap: 24px; flex-wrap: wrap;">{num}</span>'
            f'<span style="display: flex; align-items: center; gap: 8px; border-top: 1px solid {LINE}; padding-top: 10px; font-size: 12.5px;">'
            f'<span style="color: {MUTED}; flex-grow: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{H("c.rod")}</span>'
            + se('c.ok',f'<span style="display: inline-flex; align-items: center; gap: 6px; color: {MUTED};"><span style="width: 8px; height: 8px; border-radius: 999px; background: {E.ACC};"></span>{H("c.sitT")}</span>')
            + se('c.neutro',f'<span style="color: {MUTED};">{H("c.sitT")}</span>')
            + se('c.exc',f'<span class="cadx-verbo">{H("c.verbo")} ›</span>')
            + '</span></button></sc-for></div></div>')
def arv(html):
    """marca uma grade em árvore (linhas de grupo com faixa clara) sem criar caixa nova."""
    return f'<div class="cadx-arv" style="display: contents;">{html}</div>'
def bloco_cad(topo,dados,rotulo):
    """o único bloco da tela: 1ª linha (abas) e a área de dados que estica até o fim da janela."""
    return (f'<section class="cadx" aria-label="{esc(rotulo)}">' + (f'<div class="cadx-topo">{topo}</div>' if topo else '')
            + f'<div class="cadx-dados">{dados}</div></section>')
# =====================================================================================
# CADUX (09/10/2026, pedido do Adrianus: "use seleção para abrir detalhes... como clicar na fazenda e abrir talhões cadastrados nela na tela").
# Três camadas em toda tela de Cadastros: mestre (lista curta dos grupos, com a busca da tela) → detalhe do grupo (cabeçalho, Próximo passo e os
# filhos já listados numa grade G2) → painel do item (o aside do _g2form em consulta, engine.py). ≥ 1024 px: mestre de 280 px à esquerda e
# detalhe ao lado; abaixo disso, um nível por vez (mestre em cartões → detalhe em tela cheia com "‹ {Mestre}"). Valores: g2end.js.
MD_CSS=(
    "div.cmd{display:flex;flex:1 1 0;min-height:0;min-width:0}"
    ".cmd{flex-direction:row!important}.cmd-m{width:280px;flex-shrink:0;border-right:1px solid #E4E9E5;display:flex;flex-direction:column;min-height:0;background:#FAFBF9}"
    ".cmd-d{flex:1 1 0;min-width:0;display:flex;flex-direction:column;min-height:0}"
    ".cmd-busca{padding:12px 12px 8px}.cmd-busca label{display:flex;align-items:center;gap:6px;padding:7px 11px;border:1px solid #E4E9E5;border-radius:999px;background:#FFFFFF}"
    ".cmd-busca input{font-family:inherit;font-size:13px;border:0;background:transparent;outline:none;width:100%;min-width:0}"
    ".cmd-lista{flex:1 1 0;min-height:0;overflow-y:auto;padding:4px 8px 8px}.cmd-lista>[role=list]{display:flex;flex-direction:column;gap:2px}"
    ".cmd-tit{font-size:11px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#65736A;padding:10px 8px 4px}"
    ".cmd-it{display:grid;grid-template-columns:1fr auto;align-items:baseline;column-gap:8px;row-gap:1px;width:100%;text-align:left;padding:9px 10px;border:1px solid transparent;"
    "border-radius:10px;background:transparent;font-family:inherit;color:#15201A;cursor:pointer;min-height:44px;box-sizing:border-box}"
    ".cmd-it-t{font-size:13.5px;font-weight:800;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.cmd-it-n{font-size:12px;font-weight:700;color:#65736A;font-variant-numeric:tabular-nums}"
    ".cmd-it-s{grid-column:1/-1;font-size:12px;color:#65736A;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.cmd-it-e{grid-column:1/-1;font-size:12px;font-weight:700}"
    "@media (hover:hover){.cmd-it:hover{background:#F2F8F4;border-color:#CFE3D6}}"
    ".cmd-it[aria-current=true]{background:#E4F3E9;border-color:#1E7A4C;box-shadow:inset 3px 0 0 #1E7A4C}.cmd-it[aria-current=true] :is(.cmd-it-n,.cmd-it-s){color:#3F4A44}.cmd-inat-it .cmd-it-t{color:#65736A}"   # contraste ≥ 4,5:1 no escolhido (I37)
    ".cmd-inat{margin:0 12px 6px;border:0;background:transparent;padding:6px 0;font-family:inherit;font-size:12.5px;font-weight:700;color:#5B6660;cursor:pointer;text-align:left}"
    ".cmd-rod{padding:10px 12px;border-top:1px solid #E4E9E5;display:flex;flex-wrap:wrap;gap:8px}"
    ".cmd-res{padding:0 12px 8px;display:flex;flex-direction:column;gap:4px}.cmd-res button{display:flex;flex-direction:column;align-items:flex-start;gap:1px;width:100%;padding:8px 10px;border:1px solid #E4E9E5;"
    "border-radius:10px;background:#FFFFFF;font-family:inherit;font-size:13px;color:#15201A;cursor:pointer;text-align:left;min-height:44px;box-sizing:border-box}.cmd-res button span{font-size:12px;color:#65736A}"
    ".cmd-dc{display:flex;flex-direction:column;gap:10px;padding:14px 16px 12px;border-bottom:1px solid #E4E9E5}"
    ".cmd-dt{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.cmd-dt h2{margin:0;font-family:'Sora','Manrope',sans-serif;font-size:19px;font-weight:700;letter-spacing:-.02em;min-width:0}"
    ".cmd-dt h2:focus{outline:none}.cmd-dt h2:focus-visible{outline:2px solid #1E7A4C;outline-offset:3px;border-radius:4px}"
    ".cmd-ds{margin:0;font-size:13px;color:#4B5A51;line-height:1.45}.cmd-dsec{display:inline-flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-left:auto}"
    ".cmd-volta{display:none;align-self:flex-start;border:0;background:transparent;padding:4px 0;font-family:inherit;font-size:13.5px;font-weight:700;color:#1E7A4C;cursor:pointer;min-height:44px}"
    ".cmd-aviso{margin:12px 16px 0;padding:10px 12px;border-radius:10px;background:#FFF3D6;color:#5B4300;font-size:13px;font-weight:700;display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center}"
    ".cmd-aviso button{border:0;background:transparent;padding:0;font-family:inherit;font-size:13px;font-weight:800;color:#1E7A4C;cursor:pointer;text-decoration:underline;text-underline-offset:3px}"
    ".cmd-vazio{padding:18px 16px;font-size:13.5px;color:#4B5A51;line-height:1.5}.cmd-vazio a,.cmd-vazio button{color:#1E7A4C;font-weight:700}"
    ".cmd-vazio button{border:0;background:transparent;padding:0;font-family:inherit;font-size:13.5px;cursor:pointer;text-decoration:underline;text-underline-offset:3px}"
    ".cmd-conta{font-size:12px;font-weight:600;color:#65736A;white-space:nowrap}"
    # uma busca por tela, no mestre: a caixa de busca da grade filha some (o filtro e a ordenação por coluna continuam)
    ".cmd .g2caixa>div:first-child>label:has(input[type=search]),.cmd .g2caixa>div:first-child>label:has(input[type=search])+span{display:none}"
    "@media (max-width:1023px){.cmd{flex-direction:column!important}.cmd-m{width:auto;border-right:0;background:#FFFFFF}.cmd[data-nivel=m] .cmd-d,.cmd[data-nivel=d] .cmd-m{display:none!important}"
    # achado 11 (I32): a regra da casca "main section:only-of-type:has(.g2caixa,.rola)>div:last-child{display:flex}" (engine.py) é mais
    # específica e mostrava o detalhe embaixo do mestre a 390 px, com a lista de cartões espremida em 16 px; no mestre, a lista tem a altura dela
    ".cmd[data-nivel=m] .cmd-m{flex:1 0 auto}.cmd[data-nivel=m] .cmd-lista{flex:0 0 auto;overflow:visible}"
    # I32 a 390 px: o cabeçalho do detalhe mais justo (menos folga entre título, ações, resumo e Próximo passo), para a 1ª linha da grade
    # caber na tela mesmo com o Próximo passo longo (Lagoa Grande); nenhum texto sai
    ".cmd-dc{gap:6px;padding:10px 14px 8px}.cmd-ds{line-height:1.35}.cmd-d>.cadx-topo{padding-top:8px}"
    ".cmd-volta{display:inline-flex;align-items:center}.cmd-lista{padding:4px 12px 12px}.cmd-lista>[role=list]{gap:8px}"
    ".cmd-it{border:1px solid #E4E9E5;background:#FFFFFF;padding:12px 14px}.cmd-it[aria-current=true]{box-shadow:none}.cmd-dsec{margin-left:0}"
    # BOT-01 e C24 abaixo de 1024 px (achado 11): o "+ Criar {item}" do cabeçalho e o Próximo passo do detalhe ficam na mesma tela; só o do
    # cabeçalho fica verde (BOT-02), e a ação do Próximo passo vira secundária, no mesmo lugar e com o mesmo verbo
    ".cmd-dc .g2prox-prim{background:#FFFFFF!important;color:#15201A!important;border:1px solid #E4E9E5!important;box-shadow:none!important}}"
)
def md_css():
    E.EXTRA.append('<style>'+MD_CSS+'</style>')
_LUPA=(f'<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{MUTED}" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
       '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>')
def mestre(rotulo,busca,rodape=''):
    """mestre: a busca da tela (casa nome, código, sinônimo e o pai, sem acento nem caixa), o anúncio da seleção, os resultados da busca abaixo
    de 1024 px, a lista de grupos (um ponto de Tab; ↑/↓, Enter) e o rodapé (criar o grupo, secundário). Buracos mx_* (cadMestreVals)."""
    return (se('mx_temAviso',f'<div role="alert" class="cmd-aviso"><span>{H("dx_aviso")}</span>'+se('dx_temAvisoSaida',f'<button type="button" onClick="{H("dx_avisoGo")}">{H("dx_avisoT")}</button>')+'</div>')
            + f'<div class="cmd-busca"><label>{_LUPA}<input type="search" id="mx-q" aria-label="{esc(busca)}" placeholder="{esc(busca)}" value="{H("mx_q")}" onChange="{H("mx_setq")}" onKeyDown="{H("mx_qkey")}"></label></div>'
            f'<div role="status" aria-live="polite" class="g2sr">{H("mx_anuncio")}</div>'
            + se('mx_temRes',f'<div class="cmd-res" role="list" aria-label="Resultados da busca"><sc-for list="{H("mx_res")}" as="x" hint-placeholder-count="2"><div role="listitem">'
                 f'<button type="button" onClick="{H("x.go")}"><b>{H("x.t")}</b><span>{H("x.sub")}</span></button></div></sc-for></div>')
            + f'<nav class="cmd-lista" aria-label="{esc(rotulo)}" onKeyDown="{H("mx_key")}"><div role="list"><sc-for list="{H("mx_itens")}" as="m" hint-placeholder-count="4">'
            + se('m.tit',f'<div class="cmd-tit">{H("m.t")}</div>')
            + se('m.item',f'<div role="listitem"><button type="button" class="{H("m.cls")}" aria-current="{H("m.cur")}" aria-label="{H("m.lab")}" tabIndex="{H("m.tab")}" onClick="{H("m.go")}">'
                 f'<span class="cmd-it-t">{H("m.t")}</span><span class="cmd-it-n">{H("m.n")}</span><span class="cmd-it-s">{H("m.sub")}</span>'
                 f'<span class="cmd-it-e" style="{H("m.est")}">{H("m.res")}</span></button></div>',True)
            + '</sc-for></div></nav>'
            + se('mx_temInat',f'<button type="button" class="cmd-inat" aria-pressed="{H("mx_inatOn")}" onClick="{H("mx_inat")}">{H("mx_inatT")}</button>')
            + (f'<div class="cmd-rod">{rodape}</div>' if rodape else ''))
def det_cab(extra=''):
    """cabeçalho do detalhe do grupo (DS-58: o que é · onde · estado): "‹ {Mestre}" abaixo de 1024 px, título (recebe o foco), estado, "Ver ficha"
    e links de saída (secundários), linha de contexto, aviso de registro indisponível (SEL-02) e o Próximo passo. Buracos dx_* (cadDetVals)."""
    lk=f'color: {E.ACC}; font-weight: 700; font-size: 13px; text-decoration: none;'
    return (se('dx_temAviso',f'<div role="alert" class="cmd-aviso"><span>{H("dx_aviso")}</span>'+se('dx_temAvisoSaida',f'<button type="button" onClick="{H("dx_avisoGo")}">{H("dx_avisoT")}</button>')+'</div>')
            + f'<div class="cmd-dc"><button type="button" class="cmd-volta" onClick="{H("dx_volta")}">{H("dx_voltaT")}</button>'
            f'<div class="cmd-dt"><h2 id="dx-t" tabIndex="-1">{H("dx_t")}</h2>'
            + se('dx_temChip',f'<span style="{H("dx_chSt")}">{H("dx_chT")}</span>')
            + f'<span class="cmd-dsec">'
            + se('dx_temFicha',f'<button type="button" onClick="{H("dx_ficha")}" style="{E.BTN_ST(False,True)}">{H("dx_fichaT")}</button>')
            + se('dx_temLks',f'<sc-for list="{H("dx_lks")}" as="k" hint-placeholder-count="1">'+se('k.isA',f'<a href="{H("k.h")}" style="{lk}">{H("k.t")} ›</a>')
                 + se('k.isB',f'<button type="button" class="g2lk" onClick="{H("k.go")}">{H("k.t")} ›</button>')+'</sc-for>')
            + f'</span></div><p class="cmd-ds">{H("dx_sub")}</p>'
            + E.g2prox_tpl(lambda k: H('dx_p.'+k)) + extra + '</div>')
def vazio(key):
    """vazio com próximo passo (4.3, DS-45): diz o que fazer em texto; link só para outra tela; nunca um 2º verde (BOT-01)."""
    return se(key+'_tem',f'<div class="cmd-vazio" role="status"><span>{H(key+"_t")}</span> '
              + se(key+'_temLk',f'<a href="{H(key+"_lkH")}">{H(key+"_lkT")} ›</a>') + se(key+'_temGo',f'<button type="button" onClick="{H(key+"_go")}">{H(key+"_goT")}</button>') + '</div>')
def md(mestre_html,det_html,rotulo,topo=''):
    """o bloco único da tela em mestre → detalhe (o painel do item é o aside do _g2form). topo: abas da tela acima das duas colunas (CD-02:
    Culturas · Operações, duas árvores independentes, C17)."""
    if topo:
        return (f'<section class="cadx" aria-label="{esc(rotulo)}"><div class="cadx-topo" style="padding-bottom: 10px; border-bottom: 1px solid {LINE};">{topo}</div>'
                f'<div class="cmd" data-nivel="{H("mx_nivel")}"><div class="cmd-m">{mestre_html}</div><div class="cmd-d">{det_html}</div></div></section>')
    return (f'<section class="cadx cmd" aria-label="{esc(rotulo)}" data-nivel="{H("mx_nivel")}"><div class="cmd-m">{mestre_html}</div>'
            f'<div class="cmd-d">{det_html}</div></section>')
def criar_cab(fn,rotulo):
    """'+ Criar {item}' (BOT-02/03/05): a primária da tela do menu, no cabeçalho, à direita do título; herda o grupo escolhido no mestre.
    Some quando a tela não é a fonte do que o grupo escolhido lista (buraco cab_criar_on) e diz o item no rótulo (cab_criarT)."""
    return se('cab_criar_on',f'<button type="button" onClick="{H(fn)}" style="{E.BTN_ST(True)}">{H("cab_criarT")}</button>',True)
def estado_cab(fname,titulo,key):
    """estado da tela ao lado do título, em uma linha (ponto + texto na cor do estado; buracos key, key_stst, key_stdot via cadEstado)."""
    import os
    p=os.path.join(E.P,fname); s=open(p).read(); alvo=f'>{esc(titulo)}</h1>'
    assert s.count(alvo)==1, (fname,alvo)
    open(p,'w').write(s.replace(alvo,alvo+estado_html(key),1))
def ncol_dinamico(fname,holes):
    """grade cujas colunas mudam no navegador (ex.: colunas do papel no CD-05; Fazenda só em "Todas" na Irrigação): troca o nº fixo de
    colunas da i-ésima grade da página (ordem do HTML) pelo buraco holes[i] (None mantém), para a trilha do grid acompanhar as colunas."""
    import os
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); alvo='grid-template-columns: var(--g2cols, repeat('
    partes=s.split(alvo); assert len(partes)-1>=len(holes), (fname,len(partes)-1,holes)
    for i,h in enumerate(holes):
        if h is None: continue
        q=partes[i+1]; j=q.index(','); assert q[:j].isdigit(), (fname,q[:20]); partes[i+1]='{{'+h+'}}'+q[j:]
    open(p,'w',encoding='utf-8').write(alvo.join(partes))
def estado_html(key):
    return f'<span class="cadx-estado" style="{H(key+"_stst")}"><span style="{H(key+"_stdot")}"></span>{H(key)}</span>'
def acoes_form(gid):
    """ações do painel lateral (Excluir, Abrir talhão…) com estilo vindo do estado (fa.st): destrutiva em vermelho, bloqueada esmaecida."""
    old=f'onClick="{{{{fa.go}}}}" style="{BTN_ST(False,True)}"'
    for i,x in enumerate(E.EXTRA):
        if f'{gid}_F.open' in x and old in x:
            E.EXTRA[i]=x.replace(old,'onClick="{{fa.go}}" style="{{fa.st}}"'); return
    raise AssertionError('formulário sem bloco de ações: '+gid)

CADXJS=r'''
// ===== padrão visual dos cadastros =====
const CADT={yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],green:['#1E7A4C','#E4F3E9']};
const CAD_TAB=[__TABOFF__,__TABON__];
// situação da linha como chip (TABELAS-FOCO, proprietário 04/10/2026): verde quando ok, cinza quando neutro; exceção em chip com o próximo passo
function sitOk(t){ return [chipc(t,'green')]; }
function sitInfo(t){ return [chipc(t,'gray')]; }   // estado neutro (nem ok nem pendência)
function sitX(t,c,verbo,h){ return [chipc(t,c)].concat(verbo?[h?{k:'link',t:verbo+' ›',h:h}:{k:'b',t:verbo+' ›'}]:[]); }
// estado da tela ao lado do título
function cadEstado(v,key,t,cor){ const c=(CADT[cor]||CADT.gray)[0]; v[key]=t;
  v[key+'_stst']='display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:700;white-space:nowrap;color:'+c+';';
  v[key+'_stdot']='width:8px;height:8px;border-radius:999px;flex-shrink:0;background:'+c+';'; }
// abas: a ativa fica no estado (self.state[key]) e no endereço (#aba=slug), para voltar do detalhe na mesma aba
function cadAbas(self,v,pre,key,info){ let a=self.state[key];
  if(a===undefined){ a=0; try{ const m=/[#&]aba=([^&]+)/.exec(location.hash||''); if(m){ const i=info.findIndex(x=>x.slug===decodeURIComponent(m[1])); if(i>=0) a=i; } }catch(e){} }
  info.forEach((x,i)=>{ const on=a===i; v[pre+i+'_on']=on; v[pre+i+'_sel']=on?'true':'false'; v[pre+i+'_st']=CAD_TAB[on?1:0];
    v[pre+i+'_n']=(x.n===undefined||x.n===null)?'':String(x.n);
    v[pre+i+'_dot']=x.cor?('width:7px;height:7px;border-radius:999px;flex-shrink:0;background:'+(CADT[x.cor]||CADT.gray)[0]+';'):'display:none;';
    v[pre+i+'_sr']=x.sr||'';   /* o ponto é só visual: o leitor de tela ouve o que ele quer dizer (ex.: ", 6 a resolver") */
    v[pre+i+'_go']=()=>{ cadHash(x.slug); self.setState({[key]:i}); }; });
  return a; }
// guarda a aba no endereço sem perder os outros parâmetros (ex.: #talhao=T1&aba=geometria)
function cadHash(slug){ try{ const h=String(location.hash||'').replace(/^#/,''); const ps=h?h.split('&').filter(x=>x&&x.indexOf('aba=')!==0):[]; ps.push('aba='+slug); history.replaceState(null,'','#'+ps.join('&')); }catch(e){} }
function cadIrAba(self,key,i,slug,extra){ cadHash(slug); self.setState(Object.assign({[key]:i},extra||{})); }
// alternância de visão (Lista | Mapa)
function cadSeg(v,pre,n,cur,go){ for(let i=0;i<n;i++){ const on=i===cur; v[pre+i+'_on']=on?'true':'false'; v[pre+i+'_go']=()=>go(i);
  v[pre+i+'_st']='font-family:inherit;font-size:12.5px;font-weight:700;padding:5px 12px;border-radius:999px;border:0;cursor:pointer;'+(on?'background:#FFFFFF;color:#15201A;box-shadow:0 1px 2px rgba(21,32,26,.12);':'background:transparent;color:#65736A;'); } }
// registros de uma grade (em árvore, só as folhas; o grupo tem kids)
function cadRegs(rows){ const o=[]; const w=l=>l.forEach(r=>{ if(Array.isArray(r.kids)) w(r.kids); else o.push(r); }); w(rows); return o; }
// filtro rápido do bloco: Todos · A resolver · (Inativos só com N>0). Chama no PREVALS (esconde pelo r.sh) e cadQfPos no EXTRAVALS.
// opc.extra: outro filtro do bloco (ex.: Função) que vale junto; as contagens dos chips respeitam ele
function cadQf(self,v,gid,key,defs,opc){ const q=self.state[key]||''; const rows=RW(self,gid); const regs=cadRegs(rows); const d=defs.find(x=>x.k===q); const SH='cadqf_'+gid;
  const ex=(opc&&opc.extra)||null; const passa=r=>(!d||d.f(r))&&(!ex||ex(r));
  regs.forEach(r=>{ if(r.sh===SH) delete r.sh; if(!passa(r)&&!r.sh) r.sh=SH; });
  const grp=l=>l.forEach(r=>{ if(Array.isArray(r.kids)){ if(r.sh===SH) delete r.sh; if((d||ex)&&!r.sh) r.sh=SH; grp(r.kids); } }); grp(rows);
  const vis=regs.filter(r=>(!r.sh||r.sh===SH)&&(!ex||ex(r)));
  const ch=[{k:'',t:defs.todos||'Todos',n:vis.length}].concat(defs.map(x=>({k:x.k,t:x.t,n:vis.filter(x.f).length,oz:x.oz}))).filter(c=>!(c.oz&&!c.n&&q!==c.k));
  v[gid+'_cqf']=ch.map(c=>{ const on=q===c.k; return {t:c.t,n:String(c.n),on:on?'true':'false',go:()=>self.setState({[key]:(on&&c.k)?'':c.k}),
    st:'font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;'+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')}; });
  return q; }
// "X de Y" da árvore conta registros (folhas) que passam na busca e nos filtros, não grupos
function cadConta(self,v,gid){ const sp=GR(gid), st=g2st(self,gid), ad=self.state.added||{}; const regs=cadRegs(RW(self,gid));
  v[gid+'_all']=regs.filter(r=>!r.sh||String(r.sh).indexOf('cadqf_')===0).length; v[gid+'_count']=regs.filter(r=>g2match(r,sp,st,null,ad)).length; }
function cadSel(self,v,key,opts){ const cur=self.state[key]||''; v[key]=cur; v[key+'_opts']=opts; v[key+'_set']=(e)=>self.setState({[key]:e.target.value});
  v[key+'_st']='font-family:inherit;font-size:12.5px;font-weight:700;padding:4px 8px;border-radius:999px;cursor:pointer;color:#15201A;'+(cur?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;'); return cur; }
function cadQfPos(self,v,gid,key){ if(!(self.state[key]||'')) return; v[gid+'_filtered']=true; v[gid+'_clear']=()=>{ g2set(self,gid,{q:'',f:{}}); self.setState({[key]:''}); }; }
// faixa "precisa de atenção": até 3 cartões; com mais, o 3º vira "Mais N pendências"
function cadFaixa(v,key,itens,mais){ let it=(itens||[]).filter(Boolean);
  if(it.length>3){ const resto=it.slice(2).reduce((s,x)=>s+(Number(x.n)||1),0); it=it.slice(0,2).concat([{n:resto,rot:resto>1?'outras pendências':'outra pendência',reg:'',verbo:'Ver todas',cor:'yellow',go:mais}]); }
  v[key]=it.map(x=>{ const c=(CADT[x.cor]||CADT.yellow)[0]; return {n:String(x.n),rot:x.rot,reg:x.reg||'',verbo:x.verbo,go:x.go||(()=>{}),
    st:'border-left:3px solid '+c+';', nst:"font-family:'Sora','Manrope',sans-serif;font-size:20px;font-weight:800;line-height:1;color:"+c+';'}; });
  v[key+'_tem']=it.length>0; }
// cartões de entidade contêiner; clicar (ou Enter) abre o mesmo painel da grade
function cadCartoes(self,v,key,gid,itens){ v[key]=itens.map(x=>{ const c=x.chip?(CADT[x.chip.c]||CADT.gray):null;
  return {nome:x.nome,sub:x.sub||'',lab:'Abrir '+x.nome,nums:x.nums||[],rod:x.rod||'',ok:!x.verbo&&!x.neutro,neutro:!x.verbo&&!!x.neutro,exc:!!x.verbo,sitT:x.sitT||'Em dia',verbo:x.verbo||'',
    temChip:!!c,chT:x.chip?x.chip.t:'',chSt:c?'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;flex-shrink:0;color:'+c[0]+';background:'+c[1]+';':'',
    chDot:c?'width:6px;height:6px;border-radius:999px;background:'+c[0]+';':'',open:()=>g2open(self,GR(gid),x.id,null)}; }); }
// ações do painel lateral (Excluir com confirmação; bloqueada mostra a causa)
const CAD_ACTS={};
const CAD_BTN='padding:7px 14px;border-radius:10px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;line-height:1.25;white-space:nowrap;';
const CAD_BTN_SEC=CAD_BTN+'background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;';
const CAD_BTN_DEL=CAD_BTN+'background:#FFFFFF;color:#B42318;border:1px solid #B42318;';
const CAD_BTN_DEL2=CAD_BTN+'background:#B42318;color:#FFFFFF;border:1px solid #B42318;';
const CAD_BTN_OFF=CAD_BTN+'background:#F4F6F3;color:#8A968E;border:1px solid #E4E9E5;cursor:not-allowed;';
function cadActsIni(self){ self.g2formActs=(gid,r,fm)=>{ const f=CAD_ACTS[gid]; return f?(f(self,r,fm)||[]).filter(Boolean).map(a=>Object.assign({st:CAD_BTN_SEC,h:''},a)):[]; }; }
function cadApaga(self,gid,id){ const sp=GR(gid); const r0=g2find(RW(self,gid),id); const nome=r0?g2text(r0,sp.cols[0]):''; const rs=g2clone(RW(self,gid));
  const rm=(l)=>{ const i=l.findIndex(x=>x.id===id); if(i>=0){ l.splice(i,1); return true; } return l.some(x=>x.kids&&rm(x.kids)); }; rm(rs);
  g2set(self,gid,{rows:rs,fm:null,cfp:null}); self.setState({g2toast:'Excluído: '+nome}); if(self.g2after) self.g2after(gid,rs,null); }
// ent: 'cultivar'; motivo: por que não pode (vazio = pode); fazer: exclusão própria da tela (ex.: rascunho da estrutura)
function cadExcluir(self,gid,r,ent,motivo,fazer){
  if(motivo) return {t:'Excluir '+ent,h:'Não dá para excluir: '+motivo+'.',st:CAD_BTN_OFF,go:()=>self.setState({g2toast:'Não dá para excluir: '+motivo+'.'})};
  if(g2st(self,gid).cfp!==r.id) return {t:'Excluir '+ent,h:'Pede confirmação antes de tirar do cadastro.',st:CAD_BTN_DEL,go:()=>g2set(self,gid,{cfp:r.id})};
  return {t:'Confirmar exclusão',h:'Não dá para desfazer.',st:CAD_BTN_DEL2,go:()=>{ if(fazer){ g2set(self,gid,{fm:null,cfp:null}); fazer(); } else cadApaga(self,gid,r.id); }}; }
// ===== CADUX: seleção do mestre, busca da tela e filtro rápido como marcas nas linhas (r.sh), na ordem mestre → busca → filtro =====
// cada passo tira a sua marca e marca o que esconde; a 1ª marca vale (a linha some). grp: na árvore, o grupo só aparece com filho visível
function cmdPasse(rows,SH,ok,grp,regsDe){ const regs=(regsDe||cadRegs)(rows); regs.forEach(r=>{ if(r.sh===SH) delete r.sh; if(!ok(r)&&!r.sh) r.sh=SH; });
  rows.forEach(g=>{ if(Array.isArray(g.kids)){ if(g.sh===SH) delete g.sh; if(grp&&!g.sh) g.sh=SH; } }); return regs; }
// filtro rápido dos Cadastros (Todos · A resolver · Inativos): conta só o que o mestre e a busca deixam ver; "Todos" não mostra o que é
// "oculta" (inativo só aparece com o filtro Inativos, esmaecido e consultável: R08). defs: [{k,t,f,oz,oculta}]
function cmdQf(self,v,gid,key,defs,rows,regsDe){ const q=self.state[key]||''; const SH='cadqf_'+gid; const d=defs.find(x=>x.k===q); const regs=(regsDe||cadRegs)(rows);
  const oc=defs.filter(x=>x.oculta); const passa=r=>d?d.f(r):!oc.some(x=>x.f(r));
  regs.forEach(r=>{ if(r.sh===SH) delete r.sh; }); const base=regs.filter(r=>!r.sh); base.forEach(r=>{ if(!passa(r)) r.sh=SH; });
  rows.forEach(g=>{ if(Array.isArray(g.kids)){ if(g.sh===SH) delete g.sh; if((d||oc.length)&&!g.sh) g.sh=SH; } });
  const ch=[{k:'',t:defs.todos||'Todos',n:base.filter(r=>!oc.some(x=>x.f(r))).length}].concat(defs.map(x=>({k:x.k,t:x.t,n:base.filter(x.f).length,oz:x.oz||x.oculta}))).filter(c=>!(c.oz&&!c.n&&q!==c.k));
  v[gid+'_cqf']=ch.map(c=>{ const on=q===c.k; return {t:c.t,n:String(c.n),on:on?'true':'false',go:()=>{ self.setState({[key]:(on&&c.k)?'':c.k}); },
    st:'font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;color:#1E6B47;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')}; });
  return q; }
// ===== CADUX: controlador comum das telas em mestre → detalhe → painel (CD-02 a CD-07; o CD-01 tem o seu, com mapa) =====
// C: {gp: parâmetro do grupo no endereço ('eq'); ip: {gid: parâmetro do item} ({g_pes:'pes'}); abas/abaKey (opcional); grupoDe(self,gid,r) → id do grupo
// do item ('' = Todos); existeGrupo(self,id); reg(self,id) → {gid,rid} ou {grupo} (#reg= da NAV); indisp(id) → aviso; cons:{gid:(self,r)=>conteúdo}; grpPre: prefixo
// do id das linhas-grupo da árvore (não abrem painel); abaDe(gid) → patch da aba do item; inativo(gid,r) → patch do filtro (R08); inicial(self) → grupo inicial}
function cmdSel(self){ const s=self.state.mx_sel; return (s===undefined||s===null)?'':s; }
// parâmetro do grupo no endereço: fixo ('eq') ou pela aba da tela (CD-02: 'cul' em Culturas, 'op' em Operações)
function cmdGp(self){ const C=self.__cmd; return typeof C.gp==='function'?C.gp(self):C.gp; }
// valor do item no endereço: o id; C.endItem troca pela chave de negócio quando outra frente já usa ela (CD-07: cod=3.1.02)
function cmdIdEnd(self,gid,rid){ const C=self.__cmd; return C.endItem?C.endItem(self,gid,rid):rid; }
function cmdEnd(self,extra){ const C=self.__cmd; const o={}; const s=cmdSel(self); if(s) o[cmdGp(self)]=s; if(C.abas&&C.abaKey){ const a=self.state[C.abaKey]||0; if(a) o.aba=C.abas[a]; } return Object.assign(o,extra||{}); }
function cmdIni(self,C){ if(self.__cmd) return; self.__cmd=C;
  /* linha-grupo da árvore (tem kids) não abre painel; C.grupoLinha decide quando o registro também tem filhos (CD-07: código › subcódigo) */
  self.g2cons=(gid,r,v)=>{ const f=C.cons&&C.cons[gid]; if(!f||!r||(C.grupoLinha?C.grupoLinha(gid,r):Array.isArray(r.kids))) return null; return v?f(self,r):true; };
  self.g2aberto=(gid,rid,o)=>{ if(o&&o.end) return; self.setState({mx_mk:rid}); if(!C.ip[gid]) return; cadHashPoe(self,cmdEnd(self,{[C.ip[gid]]:cmdIdEnd(self,gid,rid)}),(o&&(o.nav||o.pai||o.salvo))?null:'i'); };
  // criar abre um nível (#…&novo=1, pushState) quando não há painel aberto; com painel, troca a entrada (o voltar volta à lista, uma vez)
  self.g2criou=(gid)=>{ if(!C.ip[gid]) return; let st=null; try{ st=history.state; }catch(e){} const ja=/(^|&)novo=1/.test(String(location.hash||'').replace(/^#/,''));
    cadHashPoe(self,cmdEnd(self,{novo:'1'}),((st&&st.cadux==='i')||ja)?null:'i'); };
  self.g2fechou=(gid,fm)=>{ if(!fm) return; if(!fm.rid){ if(C.ip[gid]) cadEndFechaItem(self,cmdEnd(self,{})); return; } const rid=fm.rid; if(C.ip[gid]) cadEndFechaItem(self,cmdEnd(self,{})); g2set(self,gid,{fl:rid});
    setTimeout(()=>{ try{ const a=document.activeElement; if(!a||a===document.body){ const b=document.querySelector('[data-rid="'+rid+'"] .g2alvo'); if(b) b.focus(); } }catch(e){} },160); };
  cadEndIni(self,(o,pop,set)=>cmdAplica(self,o,pop,set));
  try{ document.addEventListener('keydown',(e)=>{ if(e.key!=='Escape'||e.defaultPrevented||cadLarga()||self.state.mx_nivel!=='d') return; if(document.querySelector('aside[role=dialog]')) return;
    const t=e.target; if(t&&/^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName)) return; e.preventDefault(); cmdVolta(self); }); }catch(e){} }
// escolher no mestre só mostra; abaixo de 1024 px abre um nível (o voltar sobe); o leitor de tela ouve o grupo e a contagem
function cmdEscolhe(self,id,o){ o=o||{}; const C=self.__cmd; const larga=cadLarga();
  self.setState({mx_sel:id,mx_nivel:'d',mx_ind:null,mx_anuncio:C.anuncio?C.anuncio(self,id):'',mx_mk:null});
  if(!o.semEnd){ const h={}; if(id) h[cmdGp(self)]=id; if(C.abas&&C.abaKey){ const a=self.state[C.abaKey]||0; if(a) h.aba=C.abas[a]; } cadHashPoe(self,h,larga?null:'g'); }
  if(!larga) cadFoco('#dx-t',90); }
function cmdVolta(self){ let st=null; try{ st=history.state; }catch(e){} self.setState({mx_nivel:'m'});
  if(st&&st.cadux==='g'){ self.__cadHash=''; try{ history.back(); }catch(e){} } else cadHashPoe(self,{}); cadFoco('.cmd-lista .cmd-it[aria-current=true]',90); }
function cmdAbre(self,gid,rid,grupo){ self.setState({mx_sel:grupo,mx_nivel:'d',mx_q:''}); cadKeepPoe('q',''); setTimeout(()=>g2open(self,GR(gid),rid,null),0); }
function cmdAplica(self,o,pop,set){ const C=self.__cmd; set=set||(p=>self.setState(p)); let alvo=null, reescreve=false;
  Object.keys(C.ip).forEach(gid=>{ const k=C.ip[gid]; if(o[k]&&!alvo) alvo={gid:gid,rid:C.normItem?C.normItem(gid,o[k],self,o):o[k],cru:o[k]}; });
  const GP=(C.gps||[]).find(k=>o[k])||(typeof C.gp==='function'?(C.gps||[])[0]:C.gp);
  if(C.normGrupo&&o[GP]) o[GP]=C.normGrupo(self,o[GP]);
  if(!alvo&&o.reg){ const x=C.reg?C.reg(self,o.reg):null; reescreve=true; if(x&&x.gid) alvo={gid:x.gid,rid:x.rid}; else if(x&&x.grupo!==undefined) o[GP]=x.grupo; else alvo={gid:null,rid:o.reg}; }
  const patch={mx_ind:null}; if(C.abas&&C.abaKey){ const ab=C.abas.indexOf(o.aba||''); if(ab>=0) patch[C.abaKey]=ab; else if(pop) patch[C.abaKey]=0; }
  if(pop) GRIDS.forEach(sp=>{ const fm=g2st(self,sp.id).fm; if(fm&&!(alvo&&alvo.gid===sp.id&&fm.rid===alvo.rid)) g2set(self,sp.id,{fm:null}); });
  if(alvo){ const r=alvo.gid?g2find(RW(self,alvo.gid),alvo.rid):null;
    if(!r){ const g=o[GP]&&C.existeGrupo(self,o[GP])?o[GP]:''; patch.mx_ind={t:C.indisp(alvo.cru!==undefined?alvo.cru:alvo.rid,alvo.gid)}; patch.mx_sel=g; patch.mx_nivel=g?'d':'m'; set(patch); cadHashPoe(self,g?{[GP]:g}:{}); return; }
    const g=C.grupoDe(self,alvo.gid,r,o[GP]); patch.mx_sel=g;   /* o[GP]: o grupo pedido no endereço (#papel=fornecedor&par=F03), que vale se o item for dele */ patch.mx_nivel='d'; if(C.abaDe) Object.assign(patch,C.abaDe(alvo.gid)||{}); if(C.inativo) Object.assign(patch,C.inativo(alvo.gid,r)||{});
    set(patch); const fm=g2st(self,alvo.gid).fm; if(!fm||fm.rid!==alvo.rid) setTimeout(()=>g2open(self,GR(alvo.gid),alvo.rid,null,{end:true}),0);
    if(reescreve||(o[GP]!==undefined&&o[GP]!==g)||(C.endSempre&&(o[GP]===undefined||o[C.ip[alvo.gid]]!==cmdIdEnd(self,alvo.gid,alvo.rid)))){ const h={}; if(g) h[C.gpDe?C.gpDe(alvo.gid):GP]=g; if(patch[C.abaKey]&&C.abas) h.aba=C.abas[patch[C.abaKey]]; h[C.ip[alvo.gid]]=cmdIdEnd(self,alvo.gid,alvo.rid); cadHashPoe(self,h); } return; }
  const gs=o[GP]||''; if(gs&&C.abaDoGp&&C.abaKey&&C.abaDoGp[GP]!==undefined) patch[C.abaKey]=C.abaDoGp[GP];
  // novo=1 (ex.: Irrigação → CD-03#classe=irrigacao&novo=1; CD-03 → CD-02#cj=&novo=1): abre a criação com o grupo herdado, uma vez
  if(o.novo==='1'&&C.novo&&!self.__cmdNovo){ self.__cmdNovo=1; setTimeout(()=>{ const nh=C.novo(self,o); try{ let h=nh; if(!h){ h=Object.assign({},o); delete h.novo; } cadHashPoe(self,h); }catch(e){} },0); }
  if(gs){ if(C.existeGrupo(self,gs)){ patch.mx_sel=gs; patch.mx_nivel='d'; } else { patch.mx_ind={t:C.indispGrupo?C.indispGrupo(gs):C.indisp(gs)}; patch.mx_sel=''; patch.mx_nivel='m'; set(patch); cadHashPoe(self,{}); return; } }
  else if(!pop){ const ini=C.inicial?C.inicial(self):''; patch.mx_sel=ini; patch.mx_nivel=ini?'d':'m'; }
  else { patch.mx_sel=cadLarga()?'':cmdSel(self); patch.mx_nivel='m'; }
  set(patch); }
// texto do registro indisponível (SEL-02, A02): a entidade é a do parâmetro do endereço (#cj= é conjunto, #local= é local) e o valor é o do
// endereço, sem prefixo interno; fem: "liberada"
function cmdIndisp(ent,id,fem){ return ent+' “'+id+'” indisponível: não existe neste cadastro ou não está '+(fem?'liberada':'liberado')+' para o seu perfil. Nada foi aberto.'; }
// aviso de registro indisponível (SEL-02) com a saída "Ver todos"
function cmdAviso(self,todosT){ const ind=self.state.mx_ind; return ind?{aviso:ind.t,avisoSaida:{t:todosT,go:()=>{ self.setState({mx_ind:null,mx_sel:'',mx_nivel:cadLarga()?'d':'m'}); cadHashPoe(self,{}); }}}:{}; }
// busca da tela sem acento nem caixa: todas as palavras precisam aparecer no texto do registro (nome, código, sinônimo e o pai)
function cmdCasa(txt,q){ if(!q) return true; const h=g2norm(txt); return g2norm(q).split(/\s+/).filter(Boolean).every(w=>h.indexOf(w)>=0); }
// "N de M": M = filhos do grupo escolhido no mestre; N = os que passam na busca, no filtro rápido e nos filtros de coluna
function cmdConta(self,gid,rows,regsDe){ const sp=GR(gid), st=g2st(self,gid), ad=self.state.added||{}; const regs=(regsDe||cadRegs)(rows);
  return {tot:regs.filter(r=>!r.sh||String(r.sh).indexOf('cadm_')!==0).length, n:regs.filter(r=>g2match(r,sp,st,null,ad)).length}; }
'''.replace('__TABOFF__',json.dumps(TAB_OFF)).replace('__TABON__',json.dumps(TAB_ON))

# =====================================================================================
# Cada tela está no seu módulo (areas/cad_*.py, que importa os auxiliares daqui); o legado cd01…cd07 daqui saiu no CADUX P9.
CAD_MODS=(('areas.cad_fazendas',('cd01','cd01det')),('areas.cad_culturas',('cd02',)),('areas.cad_ativos_pessoas',('cd03','cd04')),
          ('areas.cad_parceiros',('cd05',)),('areas.cad_produtos_estrutura',('cd06','cd07')))
def build():
    import importlib
    for mod,fns in CAD_MODS:
        m=importlib.import_module(mod)
        for fn in fns: getattr(m,fn)()

# ---- dados e trechos que outros módulos importam daqui (o resto das telas está em areas/cad_*.py) ----
# CD-02 · Culturas, cultivares e operações
def _uso_cultivar():
    u={}
    for sid,cs in D2.CULTIVOS.items():
        for c in cs: u[(c['cultura'],c['variedade'])]=u.get((c['cultura'],c['variedade']),0)+1
    return u
CULTIVARES=[('cv1','Soja','58 W','Anual',118,'RNC · referência'),('cv2','Soja','62 X','Anual',112,'RNC · referência'),('cv3','Soja','64 Z','Anual',125,'RNC · referência'),
            ('cv4','Milho','Híbrido AG 8700','Anual',140,'RNC · referência'),('cv5','Feijão','Pérola','Anual',90,'RNC · referência'),
            ('cv6','Café','Catuaí 144','Perene','','RNC · referência'),('cv7','Mamão Formosa','Formosa','Perene','','Cadastro próprio')]
# modo de cálculo do rendimento por conjunto (coerente com dados2.CONJ: largura × velocidade × eficiência = rendimento efetivo)
MODO={c['id']:(c['larg'],c['vel'],c['efic']) for c in D2.CONJ if c.get('larg')}
FONTE={'r1':'Medição local','r2':'Fabricante','r3':'Referência','r4':'Ensaio da fazenda','r5':'Medição local','r6':'Premissa a validar','r7':'Referência','r8':'Ensaio da fazenda'}
# ---- formulário do rendimento: mesmos campos, rótulos e cálculo da etapa 3 do Planejar safra (processo_safra.py · safra.js) ----
# REND_CAMPOS e REND_JS ficam prontos para o Planejar safra importar (from areas.cadastros import REND_CAMPOS, REND_JS).
REND_CALC=cond('modo','Largura × velocidade'); REND_INF=cond('modo','Informado')
REND_CAMPOS=[sel('modo','Como obter o rendimento',['Largura × velocidade','Informado'],**{'def':'Largura × velocidade'}),
             num('larg','Largura de trabalho','m',min=0.5,max=60,cond=REND_CALC),
             num('vel','Velocidade de trabalho','km/h',min=0.5,max=30,cond=REND_CALC),
             num('efic','Eficiência de campo','%',min=10,max=100,cond=REND_CALC,help='Descontadas manobras, abastecimento e paradas no campo. Manutenção e quebras entram na disponibilidade da máquina.'),
             dict(k='rend_c',l='Rendimento efetivo',ro=True,live=True,u='ha/h',cond=REND_CALC,help='Largura × velocidade ÷ 10 × eficiência.'),
             num('rend','Rendimento efetivo','ha/h',min=0.01,cond=REND_INF,help='Use quando não há largura de trabalho (ex.: tratamento de sementes, colheita manual, gotejo).'),
             num('maq','Máquina','R$/h',min=0,help='Inclua combustível, manutenção e depreciação; o operador entra em Pessoas.'),num('impl','Implemento','R$/h',req=False,min=0),
             num('pess','Pessoas na equipe','pessoas',min=0),num('pess_rs','Custo por pessoa','R$/h',req=False,min=0),
             dict(k='custo_c',l='Custo por hora',ro=True,live=True,u='R$/h',help='Máquina + implemento + pessoas × custo por pessoa.')]
REND_JS=r'''
function r2(n){ return Math.round(Number(n)*100)/100; }
// campos ao vivo do formulário (iguais ao Planejar safra): rendimento = L × V ÷ 10 × E; custo/h = máquina + implemento + pessoas × R$
function rendLive(k,d){ const n=(f)=>{ const x=g2num(d[f]); return isNaN(x)?0:x; };
  if(k==='rend_c'){ const L=n('larg'),V=n('vel'),E=n('efic'); return (L&&V&&E)?nf(r2(L*V/10*E/100),2):'—'; }
  if(k==='custo_c') return nf(n('maq')+n('impl')+n('pess')*n('pess_rs'),2);
  return null; }
// recálculo ao salvar (mesma conta do rendAfter do Planejar safra)
function rendCalc(x){ if(x.modo!=='Informado'){ x.rend=r2((Number(x.larg)||0)*(Number(x.vel)||0)/10*(Number(x.efic)||0)/100); } else { x.larg=''; x.vel=''; x.efic=''; }
  x.custo_h=r2((Number(x.maq)||0)+(Number(x.impl)||0)+(Number(x.pess)||0)*(Number(x.pess_rs)||0));
  x.custo_ha=x.rend?r2(x.custo_h/x.rend):0; return x; }
function rendParam(x){ return x.modo==='Informado'?'rendimento informado':(nfa(x.larg)+' m · '+nfa(x.vel)+' km/h · '+nfa(x.efic)+' %'); }
'''
# CD-03 · locais dos ativos (cad_ativos_pessoas.py)
LOC_ATV=['Oficina Sede','Galpão 1','Santa Rita · T1','Santa Rita · T4','Pivô 2','Talhão T7','Armazém Sede']
# CD-06 · itens do cadastro (cad_produtos_estrutura.py, cad_parceiros.py, producao_unit_test.py)
def _itens():
    """itens do cadastro: produtos dos planos (dados2) + sementes das cultivares + itens fora do plano."""
    it={}
    for p in D2.PLANOS:
        for a in p['atividades']:
            for x in a['prods']:
                if 'do cultivo' in x['prod']: continue
                it[x['prod']]=dict(grupo=x['grupo'],un=x['un'])
    for n in ['Semente de soja 58 W','Semente de soja 62 X','Semente de milho AG 8700','Semente de feijão Pérola']: it[n]=dict(grupo='Sementes',un='kg')
    it['Diesel S10']=dict(grupo='Combustível',un='L'); it['Soja em grão']=dict(grupo='Produto agrícola',un='sc 60 kg')
    it['Café beneficiado']=dict(grupo='Produto agrícola',un='sc 60 kg'); it[DC.CX_MAMAO]=dict(grupo='Embalagem',un='un')
    return it
