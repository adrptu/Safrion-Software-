# -*- coding: utf-8 -*-
"""Cadastros (menu vigente) — CD-01 Fazendas, áreas e talhões (+ CD-01det talhão T1) · CD-02 Culturas, cultivares e operações ·
CD-03 Máquinas, instalações e setores · CD-04 Pessoas e equipes · CD-05 Parceiros e fornecedores · CD-06 Produtos, unidades e locais ·
CD-07 Estrutura gerencial.
Padrão G2: cada tabela é grid(); clicar na linha abre o formulário lateral tipado (listas com cadastros existentes, números com unidade e
mínimo, datas, campos condicionais); exclusão confirmada só onde permitido; registros protegidos abrem em consulta.
Dados: dados2 (processos: cultivos, conjuntos/rendimentos, fornecedores, estoque/lotes, pedidos) e dados (mundo DEMO: talhões, lote bloqueado)."""
import json
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
    acao=E.recolhe_acoes(titulo,acao)   # MAIS-01 (15/10/2026): uma secundária à vista, as outras no "⋯ Mais ações" do bloco
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
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
'''
def js(sims,code):
    EXTRAJS[0]='const SIMS = '+json.dumps(sims,ensure_ascii=False)+';\n'+CDJS+CADXJS+code

# =====================================================================================
# Padrão comum dos cadastros (16/10/2026, proprietário: "todas telas de cadastro estao fora do nosso padrão"; skill padrao-safrion).
# O redesenho de 01/10 (anterior ao design system de 09/10) punha uma camada de estilo da área (CADX_CSS) sobre o componente comum: cabeçalho
# da tabela em caixa normal, tabela sem moldura e encostada no bloco, linhas e hover próprios, barra da grade montada à mão e o "Cadastrar"
# verde na barra. Toda melhoria do motor ficava anulada aqui. Agora cada cadastro usa só o componente comum, como a O.S. e o Estoque:
# - o bloco do motor: abas por entidade na 1ª linha (ou o título do bloco) e a grade (engine.grid) com a barra na ordem da TAB-01 (busca e
#   filtros rápidos à esquerda; ferramentas da tela, Expandir tudo, Agrupar por, Colunas e Tabela | Cartões à direita, nesta ordem);
# - a primária no cabeçalho da tela, à direita do título (BOT-01), com o verbo Criar e o "+" (BOT-03 e BOT-05); com abas, o rótulo segue
#   a aba ativa e a aba sem criação fica sem verde;
# - o que pede atenção fica na linha (TAB-06) e no filtro rápido "A resolver", com a contagem; sem faixa de cartões sobre a lista (TAB-07);
# - Equipes e Conjuntos, que eram só cartões próprios, passam à grade do motor com Tabela | Cartões (VIS-05).
# Não há mais CSS da área: nenhuma regra mira classe do motor (ds_inventario.py). As classes cadx-* que sobraram são só ganchos de teste.
from areas.processo_planos import MAIS, ICO   # o "+" de Criar e Incluir (BOT-05), o mesmo do "Criar plano"
SEG_TRILHO=f'display: inline-flex; flex-wrap: wrap; padding: 3px; border-radius: 999px; background: {E.GRAYS}; gap: 2px; max-width: 100%;'   # trilho do engine.seg
QF_CAD=dict(k='_cadqf')   # abre na barra da grade o espaço do filtro rápido do motor; os chips vêm da tela (cadQf → cadQfPos)
def abas(pre,nomes,rotulo='Cadastros desta tela'):
    """abas por entidade no seletor segmentado do motor (engine.seg, SEG_ON/SEG_OFF): rótulo + contagem + ponto de pendência
    (buracos pre+i+'_st|_go|_sel|_n|_dot', ver cadAbas)."""
    bs=''.join(f'<button type="button" role="tab" aria-selected="{H(pre+str(i)+"_sel")}" onClick="{H(pre+str(i)+"_go")}" style="{H(pre+str(i)+"_st")}">{esc(n)}'
               f'<span style="font-size: 12px; font-weight: 600; color: {MUTED};">{H(pre+str(i)+"_n")}</span>'
               f'<span aria-hidden="true" style="{H(pre+str(i)+"_dot")}"></span></button>' for i,n in enumerate(nomes))
    # as abas não quebram linha (o trilho arredondado em duas linhas vira um bloco): no estreito, a fileira rola de lado, como antes
    return f'<div role="tablist" aria-label="{esc(rotulo)}" class="cadx-abas" style="{SEG_TRILHO.replace("flex-wrap: wrap;","flex-wrap: nowrap; overflow-x: auto;")}">{bs}</div>'
def pane(pre,i,html,ativo=0):
    return f'<sc-if value="{H(pre+str(i)+"_on")}" hint-placeholder-val="{H("true" if i==ativo else "false")}">{html}</sc-if>'
def se(hole,html,dflt=False):
    return f'<sc-if value="{H(hole)}" hint-placeholder-val="{H("true" if dflt else "false")}">{html}</sc-if>'
def prim_cab(rotulo=None,fn=None):
    """primária da tela no cabeçalho, à direita do título (BOT-01): verbo Criar com o "+" (BOT-03 e BOT-05), o mesmo desenho do "Criar plano".
    Com rótulo fixo, chama o buraco fn (ex.: 'g_cv_new'). Sem rótulo, segue a aba ativa: buracos cadp_t, cadp_go e cadp_tem (cadPrim)."""
    if rotulo: return f'<button type="button" data-acao="criar" onClick="{H(fn)}" style="{E.BTN_ST(True)} {ICO}">{MAIS(15)}{esc(rotulo)}</button>'
    return se('cadp_tem',f'<button type="button" data-acao="criar" onClick="{H("cadp_go")}" style="{E.BTN_ST(True)} {ICO}">{MAIS(15)}{H("cadp_t")}</button>',True)
def secbtn(fn,rotulo,dica='',hole=False):
    t=H(rotulo) if hole else esc(rotulo); d=f' title="{esc(dica)}"' if dica else ''
    return f'<button type="button" onClick="{H(fn)}"{d} style="{E.BTN_ST(False,True)}">{t}</button>'
def filtro_sel(key,rotulo):
    """filtro de classificação da lista (lista com contagem), logo depois da busca (TAB-01); buracos key, key_set, key_opts."""
    return (f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: {MUTED};">{esc(rotulo)}'
            f'<select aria-label="{esc(rotulo)}" value="{H(key)}" onChange="{H(key+"_set")}" style="{H(key+"_st")}">'
            f'<sc-for list="{H(key+"_opts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>')
def seg(pre,opcoes,rotulo):
    """alternância de visão da tela (ex.: Lista | Mapa) no seletor segmentado do motor; buracos pre+i+'_st' e pre+i+'_go'."""
    bs=''.join(f'<button type="button" aria-pressed="{H(pre+str(i)+"_on")}" onClick="{H(pre+str(i)+"_go")}" style="{H(pre+str(i)+"_st")}">{esc(o)}</button>' for i,o in enumerate(opcoes))
    return f'<div role="group" aria-label="{esc(rotulo)}" style="{SEG_TRILHO}">{bs}</div>'
def barra(esq,dir=''):
    """barra de um painel sem grade (mapa, geometria): o mesmo desenho e a mesma ordem da barra da grade do motor (engine.grid)."""
    return f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; flex-wrap: wrap;">{esq}<span style="flex-grow: 1;"></span>{dir}</div>'
def bloco_cad(topo,dados,rotulo,titulo=None):
    """bloco do motor (o mesmo da O.S. e do Estoque): 1ª linha com as abas (ou o título do bloco) e o corpo; sendo o único bloco da tela, a
    tabela estica até o fim da janela e só ela rola, com o cabeçalho fixo (regras do engine.G2_CSS para main section:only-of-type)."""
    cab=topo or f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo or rotulo)}</h3>'
    return (f'<section aria-label="{esc(rotulo)}" style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px 10px; flex-wrap: wrap;">{cab}</div>'
            f'<div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{dados}</div></section>')
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
        q=partes[i+1]; j=q.index(',')
        if q.startswith('{{') and q[:j].endswith('_ncols}}'): continue   # VISOES-2 V2-3: grade com colunas essenciais já segue as colunas visíveis (g2lib)
        assert q[:j].isdigit(), (fname,q[:20]); partes[i+1]='{{'+h+'}}'+q[j:]
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
// ===== padrão comum dos cadastros (16/10/2026) =====
const CADT={yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE'],green:['#1E7A4C','#E4F3E9']};
const CAD_TAB=[__SEGOFF__,__SEGON__];   // engine.SEG_OFF e engine.SEG_ON: abas e alternâncias no seletor segmentado do motor
// situação da linha como chip (TABELAS-FOCO, proprietário 04/10/2026): verde quando ok, cinza quando neutro; exceção em chip com o próximo passo
function sitOk(t){ return [chipc(t,'green')]; }
function sitInfo(t){ return [chipc(t,'gray')]; }   // estado neutro (nem ok nem pendência)
function sitX(t,c,verbo,h){ return [chipc(t,c)].concat(verbo?[h?{k:'link',t:verbo+' ›',h:h}:{k:'b',t:verbo+' ›'}]:[]); }
// estado da tela ao lado do título
function cadEstado(v,key,t,cor){ const c=(CADT[cor]||CADT.gray)[0]; v[key]=t;
  v[key+'_stst']='display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:700;white-space:nowrap;color:'+c+';';
  v[key+'_stdot']='width:8px;height:8px;border-radius:999px;flex-shrink:0;background:'+c+';'; }
// primária da tela no cabeçalho (BOT-01): com abas, o rótulo e a ação seguem a aba ativa; sem rótulo, a aba não cria (sem verde)
function cadPrim(v,t,go){ v.cadp_t=t||''; v.cadp_go=go||(()=>{}); v.cadp_tem=!!t; }
// abas: a ativa fica no estado (self.state[key]) e no endereço (#aba=slug), para voltar do detalhe na mesma aba
function cadAbas(self,v,pre,key,info){ let a=self.state[key];
  if(a===undefined){ a=0; try{ const m=/[#&]aba=([^&]+)/.exec(location.hash||''); if(m){ const i=info.findIndex(x=>x.slug===decodeURIComponent(m[1])); if(i>=0) a=i; } }catch(e){} }
  info.forEach((x,i)=>{ const on=a===i; v[pre+i+'_on']=on; v[pre+i+'_sel']=on?'true':'false'; v[pre+i+'_st']=CAD_TAB[on?1:0];
    v[pre+i+'_n']=(x.n===undefined||x.n===null)?'':String(x.n);
    v[pre+i+'_dot']=x.cor?('width:7px;height:7px;border-radius:999px;flex-shrink:0;background:'+(CADT[x.cor]||CADT.gray)[0]+';'):'display:none;';
    v[pre+i+'_go']=()=>{ cadHash(x.slug); self.setState({[key]:i}); }; });
  return a; }
// guarda a aba no endereço sem perder os outros parâmetros (ex.: #talhao=T1&aba=geometria)
function cadHash(slug){ try{ const h=String(location.hash||'').replace(/^#/,''); const ps=h?h.split('&').filter(x=>x&&x.indexOf('aba=')!==0):[]; ps.push('aba='+slug); history.replaceState(null,'','#'+ps.join('&')); }catch(e){} }
function cadIrAba(self,key,i,slug,extra){ cadHash(slug); self.setState(Object.assign({[key]:i},extra||{})); }
// alternância de visão da tela (Lista | Mapa) no seletor segmentado do motor
function cadSeg(v,pre,n,cur,go){ for(let i=0;i<n;i++){ const on=i===cur; v[pre+i+'_on']=on?'true':'false'; v[pre+i+'_go']=()=>go(i); v[pre+i+'_st']=CAD_TAB[on?1:0]; } }
// registros de uma grade (em árvore, só as folhas; o grupo tem kids)
function cadRegs(rows){ const o=[]; const w=l=>l.forEach(r=>{ if(Array.isArray(r.kids)) w(r.kids); else o.push(r); }); w(rows); return o; }
// chip do filtro rápido no desenho do motor (g2lib.g2qvals): o cadastro só calcula a contagem e o que passa; o motor desenha na barra
const CAD_QF_ST='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;min-height:var(--g2-alvo,0px);box-sizing:border-box;';
function cadChip(t,n,on,go,todos){ return {t:t,n:String(n),on:on?'true':'false',go:go,lab:(on||todos)?'Mostrar todas as linhas':'Mostrar só '+t,
  st:CAD_QF_ST+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')}; }
// filtro rápido da lista: Todos · A resolver · (Inativos só com N>0). Chama no PREVALS (esconde pelo r.sh) e cadQfPos no EXTRAVALS.
// opc.extra: outro filtro da lista (ex.: Função) que vale junto; as contagens dos chips respeitam ele
function cadQf(self,v,gid,key,defs,opc){ const q=self.state[key]||''; const rows=RW(self,gid); const regs=cadRegs(rows); const d=defs.find(x=>x.k===q); const SH='cadqf_'+gid;
  const ex=(opc&&opc.extra)||null; const passa=r=>(!d||d.f(r))&&(!ex||ex(r));
  regs.forEach(r=>{ if(r.sh===SH) delete r.sh; if(!passa(r)&&!r.sh) r.sh=SH; });
  const grp=l=>l.forEach(r=>{ if(Array.isArray(r.kids)){ if(r.sh===SH) delete r.sh; if((d||ex)&&!r.sh) r.sh=SH; grp(r.kids); } }); grp(rows);
  const vis=regs.filter(r=>(!r.sh||r.sh===SH)&&(!ex||ex(r)));
  const ch=[{k:'',t:defs.todos||'Todos',n:vis.length}].concat(defs.map(x=>({k:x.k,t:x.t,n:vis.filter(x.f).length,oz:x.oz}))).filter(c=>!(c.oz&&!c.n&&q!==c.k));
  v[gid+'_cqf']=ch.map(c=>{ const on=q===c.k; return cadChip(c.t,c.n,on,()=>self.setState({[key]:(on&&c.k)?'':c.k}),!c.k); });
  return q; }
// os chips entram no lugar do filtro rápido do motor (TAB-01: logo depois da busca; TAB-02: sem "x de y" com filtro rápido)
function cadQfMotor(v,gid,ch,rot){ if(!ch||!ch.length) return; v[gid+'_qf']=ch; v[gid+'_hasqf']=true; v[gid+'_qfl']=rot||'Filtro rápido'; }
function cadQfPos(self,v,gid,key){ cadQfMotor(v,gid,v[gid+'_cqf']); if(!(self.state[key]||'')) return;
  v[gid+'_filtered']=true; v[gid+'_clear']=()=>{ g2set(self,gid,{q:'',f:{}}); self.setState({[key]:''}); }; }
// "X de Y" da árvore conta registros (folhas) que passam na busca e nos filtros, não grupos
function cadConta(self,v,gid){ const sp=GR(gid), st=g2st(self,gid), ad=self.state.added||{}; const regs=cadRegs(RW(self,gid));
  v[gid+'_all']=regs.filter(r=>!r.sh||String(r.sh).indexOf('cadqf_')===0).length; v[gid+'_count']=regs.filter(r=>g2match(r,sp,st,null,ad)).length; }
function cadSel(self,v,key,opts){ const cur=self.state[key]||''; v[key]=cur; v[key+'_opts']=opts; v[key+'_set']=(e)=>self.setState({[key]:e.target.value});
  v[key+'_st']='font-family:inherit;font-size:12.5px;font-weight:700;padding:4px 8px;border-radius:999px;cursor:pointer;color:#15201A;'+(cur?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;'); return cur; }
// ações do painel lateral (Excluir com confirmação; bloqueada mostra a causa)
const CAD_ACTS={};
const CAD_BTN='padding:7px 14px;border-radius:10px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;line-height:1.25;white-space:nowrap;';
const CAD_BTN_SEC=CAD_BTN+'background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;';
const CAD_BTN_DEL=CAD_BTN+'background:#FFFFFF;color:#B42318;border:1px solid #B42318;';
const CAD_BTN_DEL2=CAD_BTN+'background:#B42318;color:#FFFFFF;border:1px solid #B42318;';
const CAD_BTN_OFF=CAD_BTN+'background:#F4F6F3;color:#8A968E;border:1px solid #E4E9E5;cursor:not-allowed;';
function cadActsIni(self){ self.g2formActs=(gid,r,fm)=>{ const f=CAD_ACTS[gid]; return f?(f(self,r,fm)||[]).filter(Boolean).map(a=>Object.assign({st:CAD_BTN_SEC,h:''},a)):[]; }; }
function cadApaga(self,gid,id){ const sp=GR(gid); const r0=g2find(RW(self,gid),id); const nome=r0?g2text(r0,sp.cols[0]):''; const rs=g2clone(RW(self,gid));
  const g2_0=self.state.g2, fm0=g2st(self,gid).fm;   // gravação falhou (CD08-GRAVA-01): a linha volta e o registro reabre com o motivo
  const rm=(l)=>{ const i=l.findIndex(x=>x.id===id); if(i>=0){ l.splice(i,1); return true; } return l.some(x=>x.kids&&rm(x.kids)); }; rm(rs);
  g2set(self,gid,{rows:rs,fm:null,cfp:null}); self.setState({g2toast:'Excluído: '+nome}); if(self.g2after) self.g2after(gid,rs,null);
  g2persiste(self,gid,g2_0,fm0?{fm:Object.assign({},fm0,{errs:{},warn:false}),cfp:null}:{cfp:null},'Não excluído'); }
// ent: 'cultivar'; motivo: por que não pode (vazio = pode); fazer: exclusão própria da tela (ex.: rascunho da estrutura)
function cadExcluir(self,gid,r,ent,motivo,fazer){
  if(motivo) return {t:'Excluir '+ent,h:'Não dá para excluir: '+motivo+'.',st:CAD_BTN_OFF,go:()=>self.setState({g2toast:'Não dá para excluir: '+motivo+'.'})};
  if(g2st(self,gid).cfp!==r.id) return {t:'Excluir '+ent,h:'Pede confirmação antes de tirar do cadastro.',st:CAD_BTN_DEL,go:()=>g2set(self,gid,{cfp:r.id})};
  return {t:'Confirmar exclusão',h:'Não dá para desfazer.',st:CAD_BTN_DEL2,go:()=>{ if(fazer){ g2set(self,gid,{fm:null,cfp:null}); fazer(); } else cadApaga(self,gid,r.id); }}; }
'''.replace('__SEGOFF__',json.dumps(E.SEG_OFF())).replace('__SEGON__',json.dumps(E.SEG_ON()))


# =====================================================================================
# Cada tela pode ser reescrita num módulo próprio (areas/cad_*.py, que importa os auxiliares daqui); se ele existir, é o que vale.
CAD_MODS=(('areas.cad_fazendas',('cd01','cd01det')),('areas.cad_culturas',('cd02','cd08')),('areas.cad_ativos_pessoas',('cd03','cd04')),
          ('areas.cad_parceiros',('cd05',)),('areas.cad_produtos_estrutura',('cd06','cd07')))
def build():
    import importlib, importlib.util
    for mod,fns in CAD_MODS:
        m=importlib.import_module(mod) if importlib.util.find_spec(mod) else None
        for fn in fns: (getattr(m,fn) if m is not None and hasattr(m,fn) else globals()[fn])()

# ================= CD-01 · Fazendas, áreas e talhões =================
CALC={'T1':312.4,'T2':298.1,'T3':96.0,'T4':203.6,'P1':94.7,'P2':80.2,'T7':42.0,'C1':38.3}   # área do polígono validado (ha)
TIPO={'sequeiro':'Sequeiro','pivô 1':'Pivô central','pivô 2':'Pivô central','gotejo':'Gotejo'}
DOCS=['Matrícula 12.401','Contrato de arrendamento BV-03','Pendente']
def _parcelas(t):  # parcelas da safra atual (dados2) por talhão
    return [c for c in D2.CULTIVOS['S2627'] if c['local']==t or c['local'].startswith(t+'-')]
def cd01():
    fname='CD-01.dc.html'; E._reset_screen(fname)
    rows=[R(t,dict(t=t,faz='Santa Rita',tipo=TIPO.get(obs,'Sequeiro'),decl=float(ha),calc=CALC[t],doc='Matrícula 12.401',pend='',vig='2024-09-01',
                   parc=len(_parcelas(t)))) for t,ha,cult,fase,obs in D.TALHOES]
    rows.append(R('B1',dict(t='B1',faz='Boa Vista',tipo='Sequeiro',decl=120.0,calc='',doc='Pendente',pend='Contrato de arrendamento sem registro em cartório',vig='2026-09-01',parc=0)))
    g=grid([dict(k='t',l='Talhão',w=220),dict(k='decl',l='Área declarada',t='num',a='r',u='ha',d=1,agg='sum'),dict(k='calc',l='Área do polígono',t='num',a='r',u='ha',d=1,agg='sum'),
            dict(k='dif',l='Diferença',t='num',a='r',u='ha',d=1),dict(k='geo',l='Geometria'),dict(k='doc',l='Documento',w=260),dict(k='parc',l='Parcelas na safra')],
        rows,gid='g_tal',total=True,
        edit=dict(m='form',title='Talhão',newTitle='Cadastrar talhão',
            sub='Altere identificação, área declarada e documento. A área do polígono só muda com nova geometria validada; a identidade do talhão é preservada.',
            fields=[txt('t','Identificação do talhão',help='Ex.: T8. Não pode repetir na mesma fazenda.'),
                    sel('faz','Fazenda',['Santa Rita','Boa Vista'],**{'def':'Santa Rita'}),
                    sel('tipo','Sistema',['Sequeiro','Pivô central','Gotejo'],**{'def':'Sequeiro'}),
                    num('decl','Área útil declarada','ha',min=0.1,max=5000,help='Área do documento de origem.'),
                    num('calc','Área do polígono','ha',req=False,ro=True,help='Calculada da geometria validada; em branco enquanto não houver polígono.'),
                    sel('doc','Documento de origem',DOCS,**{'def':'Pendente'}),
                    txt('pend','O que falta no documento',cond=cond('doc','Pendente'),help='A pendência bloqueia só o crédito rural; o planejamento segue pela área declarada.'),
                    dat('vig','Início da vigência')]))
    corpo=(bloco('Talhões','Confira a área declarada contra o polígono e o documento de cada talhão; clique na linha para editar.',
                 g+nota('Diferença acima de 1% da área declarada vira pendência de revisão, nunca ajuste silencioso (tolerância a validar com o gestor de dados).'),
                 acao=mini('sim_imp','Importar geometrias','Simulação: nenhum arquivo real é lido')+mini('sim_val','Validar geometrias'))
           + bloco('Mapa da fazenda Santa Rita','Confira a posição dos talhões com polígono validado; talhão sem polígono não aparece no mapa.',
                   farm_map(300,camada='Estádio')))
    js(dict(imp='Prévia simulada: talhoes_boavista.kml traria o polígono de B1 com 119,6 ha (declarado 120,0 ha, dentro da tolerância). Nada foi importado · nenhum arquivo real é lido.'),r'''
function PREVALS(self,v){ RW(self,'g_tal').forEach(r=>{ const V=r.v; const dec=Number(V.decl)||0; const tem=isnum(V.calc);
  r.p.t=[{k:'b',t:V.t||''},{k:'mut',t:(V.faz||'')+' · '+(V.tipo||'')}]; r.s.t=(V.t||'')+' '+(V.faz||'');
  if(tem){ V.dif=Math.round((Number(V.calc)-dec)*10)/10; const fora=dec&&Math.abs(V.dif)/dec>0.01; r.p.dif=fora?[chipc((V.dif>0?'+':'')+nf(V.dif,1)+' ha · revisar','yellow')]:[{k:'txt',t:(V.dif>0?'+':'')+nf(V.dif,1)+' ha'}]; r.s.dif=String(V.dif); }
  else { V.dif=''; r.p.dif=[{k:'mut',t:'—'}]; r.s.dif=''; }
  r.p.geo=[tem?chipc('Validada','green'):chipc('Sem polígono','yellow')]; r.s.geo=tem?'Validada':'Sem polígono';
  r.p.doc=V.doc==='Pendente'?[chipc('Pendente','yellow'),{k:'mut',t:V.pend||''}]:[{k:'txt',t:V.doc||''}]; r.s.doc=V.doc||'';
  const n=Number(V.parc)||0; r.p.parc=(r.id==='T1')?[{k:'link',t:n+' parcelas ›',h:'CD-01det.dc.html'}]:[{k:(n?'txt':'mut'),t:(n?(n===1?'talhão inteiro':n+' parcelas'):'sem cultivo')}]; r.s.parc=String(n); }); }
function EXTRAVALS(self,v){ simv(self,v);
  valida(self,v,'g_tal',(d,fm)=>{ const e={}; const dup=unico(self,'g_tal',fm,r=>(String(r.v.faz)+'|'+String(r.v.t)).toLowerCase(),d.faz+'|'+d.t); if(dup) e.t='Já existe '+d.t+' em '+d.faz+'.'; return e; });
  v.sim_val=()=>{ const rs=RW(self,'g_tal'); const sem=rs.filter(r=>!isnum(r.v.calc)); const fora=rs.filter(r=>isnum(r.v.calc)&&Number(r.v.decl)&&Math.abs(Number(r.v.calc)-Number(r.v.decl))/Number(r.v.decl)>0.01);
    self.setState({g2toast:(rs.length-sem.length)+' de '+rs.length+' talhões com polígono válido'+(sem.length?' · sem polígono: '+sem.map(r=>r.v.t).join(', ')+' (planeja pela área declarada; mapa de taxa variável bloqueado)':'')+(fora.length?' · revisar diferença: '+fora.map(r=>r.v.t).join(', '):' · diferenças dentro da tolerância')}); }; }
''')
    HEIGHTS37[fname]=1180
    shell37('CD-01','Fazendas, áreas e talhões',corpo,fname=fname,subtitle='Cadastre talhões com área, documento e vigência; geometria e documento podem ficar pendentes sem bloquear o planejamento.',
            status=('B1 sem polígono e documento','yellow'),primary_html=novo('g_tal','Cadastrar talhão'),search=False)

# ---- CD-01det · Talhão T1: parcelas por safra, mapa, identificação e geometria ----
SAFRA_NOME={s['id']:s['nome'] for s in D2.SAFRAS}
VARS={'Soja':['58 W','62 X','64 Z'],'Milho':['Híbrido AG 8700'],'Feijão':['Pérola']}
def _br(n): return f'{n:,.2f}'.replace(',','X').replace('.',',').replace('X','.').rstrip('0').rstrip(',')
def cd01det():
    fname='CD-01det.dc.html'; E._reset_screen(fname); PARENT37[fname]='CD-01.dc.html'
    # a soma das parcelas segue a área declarada (mesma regra do Planejar safra), não a do polígono
    decl=float(dict((t,ha) for t,ha,*_ in D.TALHOES)['T1'])
    geo={'c1':'Validada','c2':'Sem polígono','d1':'Validada','e1':'Validada'}
    rows=[]
    for sid in ['S2627','S27SF','S2526']:
        for c in D2.CULTIVOS[sid]:
            if not (c['local']=='T1' or c['local'].startswith('T1-')): continue
            v=dict(parc=c['local'],safra=SAFRA_NOME[sid],cult=c['cultura'],area=c['area'],plantio=c['plantio'],geo=geo.get(c['id'],'Sem polígono'))
            v[{'Soja':'var_s','Milho':'var_m','Feijão':'var_f'}[c['cultura']]]=c['variedade']
            rows.append(R(c['id'],v,ro=(sid=='S2526')))
    g=grid([dict(k='parc',l='Parcela'),dict(k='safra',l='Safra'),dict(k='cult',l='Cultura'),dict(k='var',l='Variedade'),dict(k='area',l='Área',t='num',a='r',u='ha',d=1),
            dict(k='plantio',l='Plantio',t='date'),dict(k='geo',l='Geometria')],rows,gid='g_parc',dele=True,total=False,
        edit=dict(m='form',title='Parcela',newTitle='Cadastrar parcela',
            sub='Altere a parcela da safra. Mudar o plantio de uma parcela recalcula só os gatilhos dela; safra encerrada fica em consulta.',
            fields=[txt('parc','Parcela',help='Ex.: T1-C. Use o talhão inteiro (T1) quando não houver divisão.'),
                    sel('safra','Safra',[SAFRA_NOME['S2627'],SAFRA_NOME['S27SF']],**{'def':SAFRA_NOME['S2627']}),
                    sel('cult','Cultura',['Soja','Milho','Feijão'],**{'def':'Soja'}),
                    sel('var_s','Variedade de soja',VARS['Soja'],cond=cond('cult','Soja')),
                    sel('var_m','Híbrido de milho',VARS['Milho'],cond=cond('cult','Milho')),
                    sel('var_f','Variedade de feijão',VARS['Feijão'],cond=cond('cult','Feijão')),
                    num('area','Área da parcela','ha',min=0.1,max=decl,help=f'A soma das parcelas da mesma safra não passa dos {_br(decl)} ha declarados do T1.'),
                    dat('plantio','Plantio previsto')]))
    ident=(f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px;">'
           + ''.join(f'<div style="border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px; background: {BG};"><div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .04em;">{esc(a)}</div>'
                     f'<div style="font-size: 13.5px; font-weight: 700; margin-top: 3px;">{esc(b)}</div><div style="font-size: 12px; color: {MUTED};">{esc(c)}</div></div>'
                     for a,b,c in [('ÁREA DECLARADA','312,0 ha','Matrícula 12.401'),('POLÍGONO','312,4 ha · v3','validado em 12/09/2026 · +0,13%'),
                                   ('LOCALIZAÇÃO','SIRGAS 2000 · UTM 22S','fuso América/São Paulo'),('VIGÊNCIA','desde 01/09/2024','sequeiro · ativo')])
           + '</div>')
    corpo=(continuity('Fazendas, áreas e talhões','Talhão T1 · Santa Rita','polígono da parcela T1-B','Importar polígono da T1-B')
           + bloco('Parcelas por safra','Divida o talhão em parcelas com cultura, variedade e plantio próprios; clique na linha para editar.',g,
                   acao=mini('sim_div','Unir parcelas','Simulação: gera nova versão da geometria preservando o histórico'))
           + bloco('Identificação','Confira a identificação do talhão; para alterar, edite a linha do T1 em Fazendas, áreas e talhões.',ident)
           + bloco('Geometria','Importe o polígono da T1-B para liberar o mapa de taxa variável; a versão v2 continua consultável para as O.S. antigas.',
                   farm_map(260,camada='Estádio',sel='T1'),acao=mini('sim_geo','Importar polígono da T1-B','Simulação: nenhum arquivo real é lido')))
    js(dict(div='Prévia simulada: unir T1-A e T1-B geraria a versão v4 do T1 (312,0 ha) · v3 e as O.S. emitidas continuam consultáveis · nada foi alterado.',
            geo='Prévia simulada: t1_parcela_b.kml traria 152,3 ha para a T1-B (declarado 152,0 ha) · identidade e saldos preservados · nenhum arquivo real é lido.'),
       f'const DECL_T1={decl};\n'+r'''
function PREVALS(self,v){ RW(self,'g_parc').forEach(r=>{ const V=r.v; const vr=V.cult==='Soja'?V.var_s:(V.cult==='Milho'?V.var_m:V.var_f);
  r.p.parc=[{k:'b',t:V.parc||''}]; r.s.parc=V.parc||''; r.p.var=[{k:'txt',t:vr||'—'}]; r.s.var=vr||'';
  const g=V.geo||'Sem polígono'; r.p.geo=[chipc(g,g==='Validada'?'green':'yellow')]; r.s.geo=g;
  r.p.safra=[{k:'txt',t:V.safra||''}].concat(r.ro?[{k:'mut',t:'encerrada'}]:[]); r.s.safra=V.safra||''; }); }
function EXTRAVALS(self,v){ simv(self,v); protege(self,v,'g_parc');
  valida(self,v,'g_parc',(d,fm)=>{ const e={}; const a=g2num(d.area); const out=RW(self,'g_parc').filter(r=>r.id!==fm.rid&&r.v.safra===d.safra).reduce((s,r)=>s+(Number(r.v.area)||0),0);
    if(!isNaN(a)&&out+a>DECL_T1+0.005) e.area='As parcelas de '+d.safra+' somariam '+nfa(out+a)+' ha; o talhão tem '+nfa(DECL_T1)+' ha (livre: '+nfa(Math.max(0,DECL_T1-out))+' ha).';
    const dup=unico(self,'g_parc',fm,r=>(r.v.safra+'|'+r.v.parc).toLowerCase(),d.safra+'|'+d.parc); if(dup) e.parc=d.parc+' já existe em '+d.safra+'.'; return e; });
  self.g2after=(gid,rows,r)=>{ if(gid==='g_parc'&&r&&!r.v.geo){ r.v.geo='Sem polígono'; } }; }
''')
    HEIGHTS37[fname]=1100
    shell37('CD-01','Talhão T1 · Santa Rita',corpo,fname=fname,crumbs_extra=['T1 · 312 ha'],
            subtitle='Organize as parcelas do talhão por safra sem recadastrar fazenda ou talhão.',
            status=('T1-B sem polígono','yellow'),primary_html=novo('g_parc','Cadastrar parcela'),search=False)

# ================= CD-02 · Culturas, cultivares e operações =================
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
OPS=sorted({c['op'] for c in D2.CONJ})
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
def cd02():
    fname='CD-02.dc.html'; E._reset_screen(fname)
    uso=_uso_cultivar()
    cv=grid([dict(k='cult',l='Cultura'),dict(k='var',l='Cultivar'),dict(k='ciclo',l='Ciclo'),dict(k='reg',l='Registro'),dict(k='uso',l='Uso nos cultivos'),dict(k='sit',l='Situação')],
        [R(i,dict(cult=c,var=vr,tipo=tp,dias=dd,reg=rg,sit='Ativa',uso=uso.get((c,vr),0))) for i,c,vr,tp,dd,rg in CULTIVARES],
        gid='g_cv',dele=True,total=False,
        edit=dict(m='form',title='Cultivar',newTitle='Cadastrar cultivar',sub='Altere a cultivar. Registro no RNC é referência, não prova de adaptação local.',
            fields=[txt('var','Cultivar ou híbrido'),sel('cult','Cultura',['Soja','Milho','Feijão','Café','Mamão Formosa'],**{'def':'Soja'}),
                    sel('tipo','Tipo de ciclo',['Anual','Perene'],**{'def':'Anual'}),
                    num('dias','Ciclo até a colheita','dias',min=30,max=250,cond=cond('tipo','Anual')),
                    sel('reg','Registro',['RNC · referência','Cadastro próprio'],**{'def':'RNC · referência'}),sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})]))
    rrows=[]
    for c in D2.CONJ:
        v=dict(op=c['op'],conj=c['conj'],maq=c['maq'],impl=c['impl'],pess=c['pess'],pess_rs=c['pess_rs'],fonte=FONTE.get(c['id'],'Equipe da fazenda'),vig='2027-06-30',rend=c['rend'])
        if c['id'] in MODO: v.update(modo='Largura × velocidade',larg=MODO[c['id']][0],vel=MODO[c['id']][1],efic=MODO[c['id']][2])
        else: v.update(modo='Informado',larg='',vel='',efic='')
        ch=D2.custo_h(c); v.update(custo_h=round(ch,2),custo_ha=round(ch/c['rend'],2))
        rrows.append(R(c['id'],v,nd='em uso'))
    # operação quebra linha (a linha já tem duas) para a tabela caber sem rolagem lateral a 1440 px
    rend=grid([dict(k='op',l='Operação',w=110),dict(k='conj',l='Conjunto ou equipe',w=300),dict(k='rend',l='Rendimento efetivo',t='num',a='r',u='ha/h',d=2),
               dict(k='custo_h',l='Custo por hora',t='num',a='r',pre='R$ ',d=2),dict(k='custo_ha',l='Custo por hectare',t='num',a='r',pre='R$ ',d=2),
               dict(k='fonte',l='Fonte'),dict(k='vig',l='Vigente até',t='date')],rrows,gid='g_rend',dele=False,total=False,add='Novo rendimento',
        edit=dict(m='form',title='Rendimento',newTitle='Novo rendimento',
            sub='Informe como o conjunto trabalha e quanto custa por hora; rendimento e custo por hectare são recalculados. Planejar safra parte deste padrão.',
            fields=[sel('op','Operação',OPS),txt('conj','Conjunto ou equipe',help='Máquina + implemento, ou equipe (ex.: 6 pessoas + carreta).')]
                   + REND_CAMPOS
                   + [sel('fonte','Fonte do dado',['Medição local','Ensaio da fazenda','Fabricante','Referência','Premissa a validar'],**{'def':'Premissa a validar'}),
                      dat('vig','Vigente até')]))
    corpo=(bloco('Culturas e cultivares','Cadastre as cultivares que a fazenda planta; cultivar em uso num cultivo não pode ser excluída, só inativada.',cv)
           + bloco('Rendimentos operacionais','Confira o rendimento e o custo de cada conjunto por operação; clique na linha para ajustar.',rend,
                   acao=mini('sim_cmp','Comparar com o apontado','Compara o padrão com os apontamentos de campo')))
    js(dict(cmp='Pulverização: padrão 21,6 ha/h × apontado 19,8 ha/h (OS-0421, 4 dias) · revisão sugerida, nada alterado.'),REND_JS+r'''
function PREVALS(self,v){
  RW(self,'g_cv').forEach(r=>{ const V=r.v; r.p.cult=[{k:'b',t:V.cult||''}]; r.s.cult=V.cult||'';
    r.p.ciclo=[{k:'txt',t:V.tipo==='Perene'?'Perene':('Anual · '+(isnum(V.dias)?nf(V.dias)+' dias':'—'))}]; r.s.ciclo=V.tipo||'';
    r.p.reg=[{k:'tag',t:V.reg||'—'}]; r.s.reg=V.reg||''; const n=Number(V.uso)||0; r.p.uso=[{k:(n?'txt':'mut'),t:n?(n+(n>1?' cultivos':' cultivo')):'sem uso'}]; r.s.uso=String(n);
    r.nd=n?'em uso':''; r.p.sit=[chipc(V.sit||'Ativa',V.sit==='Inativa'?'gray':'green')]; r.s.sit=V.sit||''; });
  RW(self,'g_rend').forEach(r=>{ const V=r.v; r.p.op=[{k:'b',t:V.op||''}]; r.s.op=V.op||'';
    r.p.conj=[{k:'txt',t:V.conj||''},{k:'br'},{k:'mut',t:rendParam(V)}]; r.s.conj=V.conj||'';
    r.p.fonte=[V.fonte==='Premissa a validar'?chipc('Premissa a validar','yellow'):{k:'tag',t:V.fonte||'—'}]; r.s.fonte=V.fonte||''; }); }
function EXTRAVALS(self,v){ simv(self,v); protege(self,v,'g_cv');
  valida(self,v,'g_cv',(d,fm)=>{ const e={}; const dup=unico(self,'g_cv',fm,r=>(r.v.cult+'|'+r.v.var).toLowerCase(),d.cult+'|'+d.var); if(dup) e.var=d.var+' já está cadastrada em '+d.cult+'.'; return e; });
  valida(self,v,'g_rend',()=>({}));
  self.g2live=(gid,k,d)=>(gid==='g_rend'?rendLive(k,d):null);
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_rend'||!r) return; const V=rendCalc(r.v); g2set(self,'g_rend',{rows:g2clone(rows)});
    self.setState({g2toast:'Salvo: '+V.op+' rende '+nf(V.rend,2)+' ha/h a R$ '+nf(V.custo_h,2)+'/h e R$ '+nf(V.custo_ha,2)+'/ha. Novos planejamentos usam este padrão.'}); }; }
''')
    HEIGHTS37[fname]=1280
    shell37('CD-02','Culturas, cultivares e operações',corpo,fname=fname,subtitle='Cadastre cultivares e o rendimento de cada conjunto por operação, com fonte e vigência.',
            status=('1 premissa a validar','yellow'),primary_html=novo('g_cv','Cadastrar cultivar'),search=False)

# ================= CD-03 · Máquinas, instalações e setores =================
CLASSES=['Trator','Pulverizador','Plantadeira','Distribuidor','Colhedora','Implemento','Tratamento de sementes','Irrigação','Beneficiamento','Armazenagem']
CAPU=['cv','m de barra','linhas','t','m de plataforma','kg/h','m³/h','sc 60 kg']
LOC_ATV=['Oficina Sede','Galpão 1','Santa Rita · T1','Santa Rita · T4','Pivô 2','Talhão T7','Armazém Sede']
# (id, nome, modelo, classe, cap, capu, contador h, exige calibração, última, intervalo dias, local, fonte, valor R$, usado em)
# cd03() de reserva (vale só sem areas/cad_ativos_pessoas.py): capacidade dos equipamentos de irrigação lida do cadastro (dados_cad), sem valor antigo (revisão de 10/10, A8)
import dados_cad as _DC
_VZ={a['id']:a.get('vazao') for a in _DC.ATIVOS}
ATIVOS=[('a01','Trator T1','JD 6M 155','Trator',155,'cv',4312,'Não','',None,'Oficina Sede','Fabricante',412000,'r2'),
        ('a02','Trator 02','MF 7719','Trator',190,'cv',2988,'Não','',None,'Santa Rita · T4','Fabricante',486000,'r1'),
        ('a03','Trator 03','MF 4292','Trator',110,'cv',5120,'Não','',None,'Galpão 1','Fabricante',268000,'r3'),
        ('a04','Trator 04','JD 5078E','Trator',78,'cv',3410,'Não','',None,'Galpão 1','Fabricante',214000,'r7'),
        ('a05','Pulverizador PJ-3030','barra 36 m · 3.000 L','Pulverizador',36,'m de barra',1542,'Sim','2026-09-15',90,'Santa Rita · T1','Ensaio da fazenda',1100000,'r1'),
        ('a06','Plantadeira 24 linhas','PD-12 · espaçamento 0,5 m','Plantadeira',24,'linhas',886,'Sim','2026-09-10',180,'Galpão 1','Ensaio da fazenda',680000,'r2'),
        ('a07','Distribuidor 3 t','lanço · 24 m','Distribuidor',3,'t',640,'Sim','2026-08-01',90,'Galpão 1','Fabricante',96000,'r3'),
        ('a08','Colhedora Axial-Flow 7250','plataforma 10 m','Colhedora',10,'m de plataforma',2150,'Não','',None,'Galpão 1','Fabricante',2450000,'r5'),
        ('a09','Máquina TSI','tratamento de sementes na sede','Tratamento de sementes',2400,'kg/h',720,'Sim','2026-07-20',60,'Oficina Sede','Ensaio da fazenda',180000,'r4'),
        ('a10','Esqueletadeira','café · 1 linha','Implemento',1,'linhas',310,'Não','',None,'Galpão 1','Fabricante',58000,'r7'),
        ('a11','Bomba do Pivô 2',next(a['modelo'] for a in _DC.ATIVOS if a['id']=='a11'),'Irrigação',_VZ['a11'],'m³/h',8914,'Sim','',30,'Pivô 2','Ensaio da fazenda',96000,''),
        ('a12','Gotejo T7','cabeçal + injetora de fertilizante','Irrigação',_VZ['a12'],'m³/h',5210,'Sim','2026-09-05',60,'Talhão T7','Ensaio da fazenda',210000,'r8'),
        ('a13','Packing linha 1','esteira + balança','Beneficiamento',2400,'kg/h',12301,'Sim','2026-09-01',30,'Armazém Sede','Ensaio da fazenda',310000,''),
        ('a14','Silo 01','aeração + termometria','Armazenagem',60000,'sc 60 kg',0,'Sim','2026-09-18',90,'Armazém Sede','Fabricante',890000,'')]
def cd03():
    fname='CD-03.dc.html'; E._reset_screen(fname)
    conj={c['id']:c['op'] for c in D2.CONJ}
    rows=[R(i,dict(nome=n,modelo=m,classe=cl,cap=cap,capu=cu,cont=ct,exige=ex,calib=ca,interv=(iv if iv else ''),local=lo,fonte=fo,valor=va,sit='Ativo',uso=conj.get(u,''))) for i,n,m,cl,cap,cu,ct,ex,ca,iv,lo,fo,va,u in ATIVOS]
    g=grid([dict(k='nome',l='Ativo',w=210),dict(k='classe',l='Classe'),dict(k='cap',l='Capacidade',a='r'),dict(k='cont',l='Contador',t='num',a='r',u='h'),
            dict(k='calib',l='Calibração'),dict(k='local',l='Local'),dict(k='uso',l='Usado em')],rows,gid='g_atv',total=False,
        edit=dict(m='form',title='Ativo',newTitle='Cadastrar ativo',
            sub='Altere identidade, capacidade e calibração. Troca de medidor: informe a leitura inicial do novo; o histórico continua. Inative em vez de excluir.',
            fields=[txt('nome','Nome do ativo'),txt('modelo','Modelo ou descrição',req=False),sel('classe','Classe',CLASSES,**{'def':'Trator'}),
                    num('cap','Capacidade',min=0),sel('capu','Unidade da capacidade',CAPU,**{'def':'cv'}),
                    num('cont','Contador atual','h',min=0,help='Horímetro ou medidor; não pode ser menor que a última leitura.'),
                    sel('exige','Exige calibração ou aferição?',['Sim','Não'],**{'def':'Não'}),
                    dat('calib','Última calibração',cond=cond('exige','Sim')),num('interv','Intervalo entre calibrações','dias',min=7,max=730,cond=cond('exige','Sim')),
                    sel('local','Local',LOC_ATV,**{'def':'Galpão 1'}),sel('fonte','Fonte da capacidade',['Fabricante','Ensaio da fazenda'],**{'def':'Fabricante'}),
                    num('valor','Valor do ativo','R$',min=0,req=False),sel('sit','Situação',['Ativo','Inativo'],**{'def':'Ativo'})]))
    corpo=bloco('Ativos e instalações','Mantenha capacidade, contador e calibração de cada ativo em dia; clique na linha para editar.',g)
    js({},r'''
const CONT0={}; GR('g_atv').rows.forEach(r=>{ CONT0[r.id]=Number(r.v.cont)||0; });
function PREVALS(self,v){ RW(self,'g_atv').forEach(r=>{ const V=r.v;
  r.p.nome=[{k:'b',t:V.nome||''}].concat(V.modelo?[{k:'mut',t:V.modelo}]:[]).concat(V.sit==='Inativo'?[chipc('Inativo','gray')]:[]); r.s.nome=(V.nome||'')+' '+(V.modelo||'')+(V.sit==='Inativo'?' inativo':'');
  const cu=(Number(V.cap)===1&&V.capu==='linhas')?'linha':(V.capu||''); r.p.cap=[{k:'txt',t:isnum(V.cap)?nf(V.cap,Number(V.cap)%1?2:0)+' '+cu:'—'}]; r.s.cap=String(V.cap||'');
  let cp,cs; if(V.exige!=='Sim'){ cp=[{k:'mut',t:'não exige'}]; cs='não exige'; }
  else if(!V.calib){ cp=[chipc('Aferir','yellow'),{k:'mut',t:'sem registro'}]; cs='Aferir'; }
  else { const venc=addd(V.calib,V.interv||0); const d=ddiff(HOJE,venc); if(d<0){ cp=[chipc('Vencida em '+br(venc),'red')]; cs='Vencida'; } else if(d<=15){ cp=[chipc('Vence '+br(venc),'yellow')]; cs='Vence'; } else { cp=[chipc('Em dia até '+br(venc),'green')]; cs='Em dia'; } }
  r.p.calib=cp; r.s.calib=cs; r.p.uso=[{k:(V.uso?'txt':'mut'),t:V.uso||'—'}]; r.s.uso=V.uso||'';
  }); }
function EXTRAVALS(self,v){
  valida(self,v,'g_atv',(d,fm)=>{ const e={}; const c=g2num(d.cont); if(fm.rid&&CONT0[fm.rid]!==undefined&&!isNaN(c)&&c<CONT0[fm.rid]) e.cont='A última leitura foi '+nf(CONT0[fm.rid])+' h. Se o medidor foi trocado, registre a troca na manutenção.';
    if(d.exige==='Sim'&&d.calib&&d.calib>HOJE) e.calib='A calibração não pode ser em data futura.';
    const dup=unico(self,'g_atv',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe um ativo com este nome.'; return e; }); }
''')
    HEIGHTS37[fname]=900
    shell37('CD-03','Máquinas, instalações e setores',corpo,fname=fname,subtitle='Cadastre máquinas, implementos e instalações fixas com capacidade, contador e calibração.',
            status=('2 calibrações a resolver','yellow'),primary_html=novo('g_atv','Cadastrar ativo'),search=False)

# ================= CD-04 · Pessoas e equipes =================
EQUIPES=[('e1','Agronomia','Ana','seg–sex · 07–17h'),('e2','Campo 1','Marcos','seg–sáb · 06–15h'),('e3','Campo 2','Lucas','seg–sáb · 06–15h'),
         ('e4','Irrigação','João','escala 6×2'),('e5','Administração','Paula','seg–sex · 08–18h'),('e6','Suprimentos','Rui','seg–sex · 07–17h'),('e7','Oficina','Zé','seg–sex · 07–17h')]
CALS=['seg–sex · 07–17h','seg–sex · 08–18h','seg–sáb · 06–15h','escala 6×2']
HABS=['NR-31','NR-10','NR-12','CREA','Empilhadeira']
# (id, nome, função, equipe, vínculo, exige hab., habilitação, validade, calendário, custo R$/h, tem login)
PESSOAS=[('p1','Ana','Agrônoma e gestora','Agronomia','CLT','Sim','CREA','2027-12-31','seg–sex · 07–17h',84,True),
         ('p2','Marcos','Operador de pulverização','Campo 1','CLT','Sim','NR-31','2026-09-30','seg–sáb · 06–15h',28,True),
         ('p3','Carlos','Operador de plantio','Campo 1','CLT','Sim','NR-31','2027-08-31','seg–sáb · 06–15h',28,True),
         ('p4','Lucas','Operador de colheita','Campo 2','Safrista','Sim','NR-31','2026-08-15','seg–sáb · 06–15h',30,True),
         ('p5','João','Irrigacionista','Irrigação','CLT','Sim','NR-10','2027-03-31','escala 6×2',30,True),
         ('p6','Paula','Conferente','Administração','CLT','Não','','','seg–sex · 08–18h',32,True),
         ('p7','Rui','Almoxarife','Suprimentos','CLT','Sim','Empilhadeira','2027-02-28','seg–sex · 07–17h',26,True),
         ('p8','Zé','Mecânico','Oficina','CLT','Sim','NR-12','2027-05-31','seg–sex · 07–17h',34,True),
         ('p9','Beto','Operador (admissão 22/09)','Campo 1','CLT','Sim','NR-31','','seg–sáb · 06–15h',28,False)]
def cd04():
    fname='CD-04.dc.html'; E._reset_screen(fname)
    eqn=[e[1] for e in EQUIPES]
    pes=grid([dict(k='nome',l='Pessoa',w=240),dict(k='equipe',l='Equipe'),dict(k='vinc',l='Vínculo'),dict(k='hab',l='Habilitação'),dict(k='cal',l='Calendário'),
              dict(k='custo',l='Custo-hora',t='num',a='r',pre='R$ ',d=2),dict(k='acesso',l='Acesso ao sistema')],
        [R(i,dict(nome=n,funcao=f,equipe=eq,vinc=vi,exh=ex,hab=hb,habv=hv,cal=ca,custo=cu,sit='Ativa',login=lg)) for i,n,f,eq,vi,ex,hb,hv,ca,cu,lg in PESSOAS],
        gid='g_pes',total=False,
        edit=dict(m='form',title='Pessoa',newTitle='Cadastrar pessoa',
            sub='Altere os dados da pessoa. O acesso ao sistema é pedido à parte; cadastrar não cria login. Inative em vez de excluir.',
            fields=[txt('nome','Nome'),txt('funcao','Função'),sel('equipe','Equipe',eqn,**{'def':'Campo 1'}),sel('vinc','Vínculo',['CLT','Safrista','Diarista','Terceiro'],**{'def':'CLT'}),
                    sel('exh','A função exige habilitação?',['Sim','Não'],**{'def':'Sim'}),
                    sel('hab','Habilitação',HABS,cond=cond('exh','Sim'),**{'def':'NR-31'}),dat('habv','Validade da habilitação',cond=cond('exh','Sim'),help='Alocação em O.S. é barrada com habilitação vencida.'),
                    sel('cal','Calendário de trabalho',CALS,**{'def':'seg–sáb · 06–15h'}),
                    num('custo','Custo-hora','R$/h',min=0,help='Visível só para perfis com permissão de custos.'),sel('sit','Situação',['Ativa','Inativa'],**{'def':'Ativa'})]))
    eq=grid([dict(k='nome',l='Equipe'),dict(k='lider',l='Líder'),dict(k='membros',l='Pessoas ativas',t='num',a='r'),dict(k='cal',l='Calendário')],
        [R(i,dict(nome=n,lider=l,cal=c)) for i,n,l,c in EQUIPES],gid='g_eq',dele=True,total=False,add='Nova equipe',search=False,
        edit=dict(m='form',title='Equipe',newTitle='Nova equipe',sub='Altere o nome, o líder e o calendário padrão da equipe. Membros entram pelo cadastro da pessoa.',
            fields=[txt('nome','Nome da equipe'),sel('lider','Líder',[p[1] for p in PESSOAS]),sel('cal','Calendário padrão',CALS,**{'def':'seg–sáb · 06–15h'})]))
    corpo=(bloco('Pessoas','Mantenha equipe, habilitação e calendário de cada pessoa em dia; clique na linha para editar.',pes)
           + bloco('Equipes','Defina líder e calendário padrão de cada equipe; equipe com pessoas ativas não pode ser excluída.',eq))
    js({},r'''
function PREVALS(self,v){ const ps=RW(self,'g_pes');
  ps.forEach(r=>{ const V=r.v; r.p.nome=[{k:'b',t:V.nome||''},{k:'mut',t:V.funcao||''}].concat(V.sit==='Inativa'?[chipc('Inativa','gray')]:[]); r.s.nome=(V.nome||'')+' '+(V.funcao||'')+(V.sit==='Inativa'?' inativa':'');
    let hp,hs; if(V.exh!=='Sim'){ hp=[{k:'mut',t:'não exige'}]; hs='não exige'; }
    else if(!V.habv){ hp=[chipc((V.hab||'')+' pendente','yellow')]; hs='pendente'; }
    else { const d=ddiff(HOJE,V.habv); if(d<0){ hp=[chipc((V.hab||'')+' vencida em '+br(V.habv),'red')]; hs='vencida'; } else if(d<=30){ hp=[chipc((V.hab||'')+' vence '+br(V.habv),'yellow')]; hs='vence'; } else { hp=[chipc((V.hab||'')+' até '+br(V.habv),'green')]; hs='válida'; } }
    r.p.hab=hp; r.s.hab=hs;
    r.p.acesso=V.login?[chipc('Com login','green')]:[chipc('Sem login','yellow'),{k:'link',t:'Solicitar acesso',h:'CF-01.dc.html'}]; r.s.acesso=V.login?'Com login':'Sem login';
  });
  RW(self,'g_eq').forEach(r=>{ const n=ps.filter(p=>p.v.equipe===r.v.nome&&p.v.sit!=='Inativa').length; r.v.membros=n; r.nd=n?'tem pessoas':''; r.p.nome=[{k:'b',t:r.v.nome||''}]; r.s.nome=r.v.nome||''; }); }
function EXTRAVALS(self,v){ protege(self,v,'g_eq');
  valida(self,v,'g_pes',(d,fm)=>{ const e={}; if(d.sit!=='Inativa'&&d.exh==='Sim'&&d.habv&&d.habv<HOJE) e.habv='Habilitação vencida: renove antes de salvar ou marque a pessoa como inativa.'; return e; });
  valida(self,v,'g_eq',(d,fm)=>{ const e={}; const dup=unico(self,'g_eq',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe a equipe '+d.nome+'.'; return e; });
  self.g2after=(gid,rows,r)=>{ if(gid==='g_pes'&&r&&!r.v.login&&String(r.id).indexOf('n')===0){ self.setState({g2toast:'Pessoa cadastrada sem login. Para dar acesso, use Solicitar acesso na linha.'}); } }; }
''')
    HEIGHTS37[fname]=1080
    shell37('CD-04','Pessoas e equipes',corpo,fname=fname,subtitle='Cadastre pessoas e equipes com habilitações, calendário e custo-hora; o custo aparece só para quem tem permissão.',
            status=('3 habilitações a resolver','yellow'),primary_html=novo('g_pes','Cadastrar pessoa'),search=False)

# ================= CD-05 · Parceiros e fornecedores =================
PAPEIS=['Fornecedor','Cliente','Transportador','Prestador','Credor']
CANAIS=['E-mail','WhatsApp']
OUTROS=[dict(id='P08',nome='Coopergrão',cnpj='98.765.432/0001-98',papeis=['Cliente'],grupos=[],email='originacao@coopergrao.coop.br',whats='65 99210-4455',homologado=False,
             contato='Renata Paiva',canais=['E-mail','WhatsApp']),
        dict(id='P09',nome='TransVale Transportes',cnpj='44.222.111/0001-18',papeis=['Transportador'],grupos=[],email='fretes@transvale.com.br',whats='65 99321-7788',homologado=False,
             contato='Edson Lima',canais=['E-mail','WhatsApp']),
        dict(id='P10',nome='Banco Terra',cnpj='11.000.222/0001-20',papeis=['Credor'],grupos=[],email='agro@bancoterra.com.br',whats='',homologado=False,
             contato='Gerente agro',canais=['E-mail']),
        dict(id='P11',nome='Adão Ferreira',cnpj='123.456.789-09',papeis=['Prestador'],grupos=[],email='',whats='65 99102-3344',homologado=False,
             contato='Adão Ferreira',canais=['WhatsApp'])]
# contato e canais vêm de dados2.FORNECEDORES (acréscimos de Compras v3.8); sem eles, valores padrão coerentes.
# CPF/CNPJ exibido e comparado = f['cnpj'], o mesmo que o Portal do parceiro (PT-07) mostra; o campo doc do dados2 não é usado aqui.
CONTATO=getattr(D2,'CONTATO_FORN',{})
def _canais(f):
    """canais autorizados: usa o campo do cadastro; sem ele, autoriza os canais que o parceiro informou (e-mail e/ou WhatsApp)."""
    if f.get('canais') is not None: return [c for c in f['canais'] if c in CANAIS]
    return [c for c,k in (('E-mail','email'),('WhatsApp','whats')) if f.get(k)]
def cd05():
    fname='CD-05.dc.html'; E._reset_screen(fname)
    rows=[]
    for f in D2.FORNECEDORES+OUTROS:
        pp=f.get('papeis') or (['Fornecedor','Cliente'] if f['id']=='F06' else ['Fornecedor'])
        rows.append(R(f['id'],dict(nome=f['nome'],cnpj=f['cnpj'],papeis='; '.join(pp),grupos='; '.join(f['grupos']),contato=f.get('contato') or CONTATO.get(f['id'],''),
                                   email=f.get('email',''),whats=f.get('whats',''),canais='; '.join(_canais(f)),homol='Sim' if f['homologado'] else 'Não')))
    g=grid([dict(k='nome',l='Parceiro · CPF/CNPJ',w=230),dict(k='grupos',l='Grupos homologados',w=300),dict(k='email',l='E-mail'),
            dict(k='whats',l='WhatsApp',w=110),dict(k='homol',l='Homologado')],rows,gid='g_forn',total=False,
        edit=dict(m='form',title='Parceiro',newTitle='Cadastrar parceiro',
            sub='Marque os papéis e os grupos homologados. Mesmo CPF ou CNPJ com outro papel não vira novo cadastro: marque o papel aqui.',
            fields=[txt('nome','Nome ou razão social'),txt('cnpj','CPF ou CNPJ',help='CPF com 11 dígitos ou CNPJ com 14; a duplicidade é verificada ao salvar.'),
                    dict(k='papeis',l='Papéis',t='multi',opts=PAPEIS,req=True),
                    dict(k='grupos',l='Grupos homologados',t='multi',opts=D2.GRUPOS,help='Grupos de insumo em que o fornecedor pode receber cotação.'),
                    txt('contato','Nome do contato',req=False,help='Obrigatório para homologar.'),
                    dict(k='email',l='E-mail para cotação',t='email',help='Obrigatório para homologar: a cotação é enviada por e-mail (simulado).'),
                    dict(k='whats',l='WhatsApp',t='tel',help='Com DDD. Usado para avisar do envio da cotação (simulado).'),
                    dict(k='canais',l='Canais autorizados',t='multi',opts=CANAIS,help='O parceiro autorizou receber cotação por este canal (simulado).'),
                    sel('homol','Homologado',['Sim','Não'],**{'def':'Não'},help='Fornecedor não homologado não recebe cotação, mesmo com grupo marcado.')]))
    cob=grid([dict(k='g',l='Grupo de insumo'),dict(k='n',l='Fornecedores que recebem cotação',t='num',a='r'),dict(k='sit',l='Situação')],[],gid='g_cob',total=False,search=False,
        edit=dict(m='origin',title='Grupo',fields=[dict(k='g',l='Grupo',t='txt',ro=True),dict(k='n',l='Fornecedores que recebem cotação',t='num',ro=True)]))
    corpo=(bloco('Parceiros','Marque os grupos homologados de cada fornecedor e mantenha contato, canais autorizados, e-mail e WhatsApp válidos; clique na linha para editar.',
                 g+nota('Não homologado não recebe cotação. Cotação só vai para fornecedor homologado, com e-mail autorizado, no grupo do insumo.'))
           + bloco('Cobertura de cotação por grupo','Confira quantos fornecedores recebem cotação em cada grupo; clique no grupo para ver quais.',cob))
    js({},'const GRUPOS_ = '+json.dumps(D2.GRUPOS,ensure_ascii=False)+';'+r'''
// canal preenchido sem autorização aparece com o aviso discreto "não autorizado"
function canal(val,aut,vazio,falta){ if(!val) return [falta?chipc(vazio,'red'):{k:'mut',t:vazio}]; return aut?[{k:'txt',t:val}]:[{k:'txt',t:val},{k:'br'},{k:'mut',t:'não autorizado'}]; }
function PREVALS(self,v){ const rows=RW(self,'g_forn');
  rows.forEach(r=>{ const V=r.v; const pp=ml(V.papeis), gg=ml(V.grupos), cc=ml(V.canais); const forn=pp.indexOf('Fornecedor')>=0; const hom=V.homol==='Sim';
    const outros=pp.filter(t=>t!=='Fornecedor').map(t=>({k:'tag',t:t}));
    r.p.nome=[{k:'b',t:V.nome||''}].concat(outros).concat([{k:'br'},{k:'mut',t:V.cnpj||'sem CPF/CNPJ'}]); r.s.nome=(V.nome||'')+' '+(V.cnpj||'')+' '+pp.join(' ');
    r.p.papeis=pp.map(t=>({k:'tag',t:t})); r.s.papeis=pp.join(', ');
    r.p.grupos=gg.length?gg.map(t=>({k:'tag',t:t})):[{k:'mut',t:forn?'nenhum grupo':'—'}]; r.s.grupos=gg.join(', ');
    r.p.email=canal(V.email,cc.indexOf('E-mail')>=0,'sem e-mail',forn&&hom); r.s.email=V.email||'';
    r.p.whats=canal(V.whats,cc.indexOf('WhatsApp')>=0,'sem WhatsApp',false); r.s.whats=V.whats||'';
    r.p.homol=!forn?[{k:'mut',t:'não é fornecedor'}]:(hom?[chipc('Sim','green')]:[chipc('Não','gray'),{k:'mut',t:'não recebe cotação'}]); r.s.homol=!forn?'não se aplica':(hom?'Sim':'Não'); });
  const ok=rows.filter(r=>ml(r.v.papeis).indexOf('Fornecedor')>=0&&r.v.homol==='Sim'&&r.v.email&&ml(r.v.canais).indexOf('E-mail')>=0);
  GR('g_cob').rows=GRUPOS_.map(g=>{ const fs=ok.filter(r=>ml(r.v.grupos).indexOf(g)>=0); const n=fs.length;
    return {id:'c_'+g,v:{g:g,n:n},s:{sit:(n===0?'Sem fornecedor':(n===1?'Só 1':'ok'))},
      p:{g:[{k:'b',t:g}],sit:[n===0?chipc('Sem fornecedor que receba cotação','red'):(n===1?chipc('Só 1 fornecedor · sem concorrência','yellow'):chipc(n+' fornecedores concorrem','green'))]},
      o:n?fs.map(r=>({t:r.v.nome+' · '+(r.v.contato?r.v.contato+' · ':'')+r.v.email})):[{t:'Nenhum fornecedor homologado com e-mail autorizado neste grupo. Marque o grupo num fornecedor e homologue.'}]}; }); }
function EXTRAVALS(self,v){
  valida(self,v,'g_forn',(d,fm)=>{ const e={}; const dg=String(d.cnpj||'').replace(/\D/g,''); const cc=ml(d.canais);
    if(d.cnpj&&dg.length!==11&&dg.length!==14) e.cnpj='Informe CPF (11 dígitos) ou CNPJ (14 dígitos).';
    else if(dg){ const dup=RW(self,'g_forn').find(r=>r.id!==fm.rid&&String(r.v.cnpj||'').replace(/\D/g,'')===dg); if(dup) e.cnpj=(dg.length===11?'CPF':'CNPJ')+' já cadastrado em '+dup.v.nome+'. Abra esse parceiro e marque o novo papel.'; }
    if(cc.indexOf('WhatsApp')>=0&&!String(d.whats||'').trim()&&!e.whats) e.whats='Informe o WhatsApp ou desmarque o canal.';
    if(d.homol==='Sim'){ if(ml(d.papeis).indexOf('Fornecedor')<0) e.papeis='Para homologar, marque o papel Fornecedor.';
      if(!ml(d.grupos).length) e.grupos='Marque ao menos um grupo para homologar.';
      if(!String(d.contato||'').trim()) e.contato='Informe o nome do contato para homologar.';
      if(!String(d.email||'').trim()&&!e.email) e.email='Informe o e-mail: a cotação é enviada por ele.';
      if(cc.indexOf('E-mail')<0) e.canais='Marque E-mail: sem autorização o fornecedor não recebe cotação.'; }
    // mesma regra do WhatsApp: canal autorizado exige o contato correspondente (homologação já pediu o e-mail acima)
    if(cc.indexOf('E-mail')>=0&&!String(d.email||'').trim()&&!e.email) e.email='Informe o e-mail ou desmarque o canal.';
    return e; });
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_forn'||!r) return; const forn=ml(r.v.papeis).indexOf('Fornecedor')>=0;
    self.setState({g2toast:!forn?('Salvo: '+r.v.nome+'.'):(r.v.homol==='Sim'?('Salvo: '+r.v.nome+' recebe cotação de '+ml(r.v.grupos).join(', ')+'.'):('Salvo: '+r.v.nome+' não recebe cotação enquanto não for homologado.'))}); }; }
''')
    HEIGHTS37[fname]=1560
    shell37('CD-05','Parceiros e fornecedores',corpo,fname=fname,subtitle='Cadastre parceiros uma única vez, com papéis; homologue fornecedores por grupo de insumo para que recebam cotação.',
            status=('2 grupos sem fornecedor','yellow'),primary_html=novo('g_forn','Cadastrar parceiro'),search=False)

# ================= CD-06 · Produtos, unidades e locais =================
LOCAIS=[('l1','Galpão 1','Galpão',8000,'t','Por lote'),('l2','Galpão 2','Galpão',1200,'t','Por lote'),('l3','Almox. defensivos','Almoxarifado',120,'m²','Por lote e validade'),
        ('l4','Câmara fria','Câmara fria',40,'t','Por lote e temperatura'),('l5','Tanque Sede','Tanque',15000,'L','Medidor de nível'),('l6','Silo 01','Silo',60000,'sc 60 kg','Por lote'),
        ('l7','Armazém Sede','Armazém',8000,'sc 60 kg','Por lote'),('l8','Packing','Armazém',400,'m²','Por lote'),('l9','Galpão 3','Galpão',600,'t','Por lote')]
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
CONV_ITEM={'Diesel S10':'1 m³ = 1.000 L'}
CONV={'kg':'1 sc = 50 kg · 1 t = 1.000 kg','L':'1 frasco = 5 L · 1 cx = 4 frascos','sc 60 kg':'1 sc = 60 kg · 1 t = 16,67 sc','un':'1 pallet = 60 cx'}
def cd06():
    fname='CD-06.dc.html'; E._reset_screen(fname)
    it=_itens(); lotes={l['item']:l for l in D2.LOTES}
    emplano={x['prod'] for p in D2.PLANOS for a in p['atividades'] for x in a['prods']}|{'Semente de soja 58 W','Semente de soja 62 X','Semente de milho AG 8700','Semente de feijão Pérola'}
    def loc(n,g):
        if n in lotes: return lotes[n]['local'].replace('Almox. defensivos','Almox. defensivos')
        return {'Herbicidas':'Almox. defensivos','Fungicidas':'Almox. defensivos','Inseticidas':'Almox. defensivos','Adjuvantes':'Almox. defensivos','Inoculantes':'Câmara fria',
                'Sementes':'Câmara fria','Fertilizantes':'Galpão 2','Combustível':'Tanque Sede','Embalagem':'Packing'}.get(g,'Armazém Sede')
    saldo={}
    for n in it:
        if n=='Café beneficiado': saldo[n]=(D.LOTE_BLOQ['sc'],'sc 60 kg',f'{D.LOTE_BLOQ["id"]} bloqueado')
        elif n=='Diesel S10': saldo[n]=(9800,'L','')
        elif n in D2.ESTOQUE and D2.ESTOQUE[n]>0:
            l=lotes.get(n); extra=''
            if l and l['quarentena']: extra=f'+ {l["quarentena"]/1000:.0f} t quarentena · {next(p["id"] for p in D2.PEDIDOS if p["item"]==n)}'.replace('.',',')
            elif l and l['reservado']: extra=f'+ {l["reservado"]} {l["un"]} reservados'
            saldo[n]=(D2.ESTOQUE[n],it[n]['un'],extra)
        else: saldo[n]=(0,it[n]['un'],'')
    val={'Sementes':12,'Herbicidas':24,'Fungicidas':24,'Inseticidas':24,'Adjuvantes':36,'Inoculantes':6}
    gar={'MAP 11-52':'11% N · 52% P₂O₅','KCl 60%':'60% K₂O','Ureia 45%':'45% N','NPK 20-05-20':'20-05-20','Nitrato de cálcio':'15,5% N · 19% Ca','Nitrato de potássio':'13% N · 44% K₂O',
         'Diesel S10':'densidade 0,85 kg/L a 20 °C','Soja em grão':'umidade-base 14%','Café beneficiado':'umidade-base 12%',DC.CX_MAMAO:'tara '+DC.EMB_PACK[DC.CX_MAMAO]['tara'].replace('.',',')+' kg'}
    grupos={}; saldo_ids=[]
    for n,d in sorted(it.items(),key=lambda x:(x[1]['grupo'],x[0])):
        g=d['grupo']; lote='Sim' if g not in ('Embalagem',) and n!='Diesel S10' else 'Não'
        s=saldo[n]
        why='com saldo' if s[0]>0 else ('em plano' if n in emplano else '')
        grupos.setdefault(g,[]).append(R(f'i{len(saldo_ids)}',
            dict(item=n,grupo=g,un=d['un'],conv=CONV_ITEM.get(n,CONV.get(d['un'],'')),lote=lote,val=(val.get(g,24) if g!='Produto agrícola' else '') if lote=='Sim' else '',gar=gar.get(n,''),local=loc(n,g),
                 saldo=s[0],sun=s[1],sx=s[2]),nd=why)); saldo_ids.append(n)
    rows=[dict(id='G_'+g,ro=True,v=dict(item=g),s={},p={},kids=ks) for g,ks in grupos.items()]
    gi=grid([dict(k='item',l='Grupo · item'),dict(k='saldo',l='Saldo em estoque',t='num',a='r'),dict(k='un',l='Unidade-base · conversão'),dict(k='lote',l='Rastreio'),
             dict(k='local',l='Local padrão')],rows,gid='g_itm',tree=True,dele=True,total=False,
        x0={r['id']:True for r in rows},
        edit=dict(m='form',title='Item',newTitle='Cadastrar item',leafOnly=True,
            sub='Altere o item. O saldo não se edita aqui: nasce de recebimentos e movimentos no Estoque.',
            fields=[txt('item','Nome do item'),sel('grupo','Grupo',D2.GRUPOS+['Produto agrícola','Embalagem'],**{'def':'Fertilizantes'}),
                    sel('un','Unidade-base',['kg','L','un','sc 60 kg','t'],**{'def':'kg'},help='Insumo, produto e embalagem não compartilham unidade implícita.'),
                    txt('conv','Conversões',req=False,help='Ex.: 1 sc = 50 kg. Fator específico (por lote ou contrato) fica versionado.'),
                    sel('lote','Controle por lote',['Sim','Não'],**{'def':'Sim'}),num('val','Validade a partir da fabricação','meses',req=False,min=1,max=120,cond=cond('lote','Sim'),help='Em branco quando o lote não vence (ex.: grão armazenado).'),
                    txt('gar','Garantia ou densidade',req=False),sel('local','Local padrão',[l[1] for l in LOCAIS],**{'def':'Galpão 2'})]))
    gl=grid([dict(k='nome',l='Local'),dict(k='tipo',l='Tipo'),dict(k='cap',l='Capacidade',a='r'),dict(k='ctrl',l='Controle'),dict(k='itens',l='Itens',t='num',a='r')],
        [R(i,dict(nome=n,tipo=t,cap=c,capu=u,ctrl=ct)) for i,n,t,c,u,ct in LOCAIS],gid='g_loc',dele=True,total=False,add='Novo local',search=False,
        edit=dict(m='form',title='Local',newTitle='Novo local',sub='Altere o local de estoque. Local com itens não pode ser excluído.',
            fields=[txt('nome','Nome do local'),sel('tipo','Tipo',['Galpão','Almoxarifado','Câmara fria','Tanque','Silo','Armazém'],**{'def':'Galpão'}),
                    num('cap','Capacidade',min=0),sel('capu','Unidade da capacidade',['t','m²','L','sc 60 kg'],**{'def':'t'}),
                    sel('ctrl','Controle',['Por lote','Por lote e validade','Por lote e temperatura','Medidor de nível'],**{'def':'Por lote'})]))
    corpo=(bloco('Itens por grupo','Cadastre cada item com unidade-base, conversão e rastreio; item com saldo ou usado em plano não pode ser excluído.',gi)
           + bloco('Locais de estoque','Cadastre os locais com capacidade e regra de controle; o saldo por local fica no Estoque.',gl))
    js({},r'''
function PREVALS(self,v){ const all=RW(self,'g_itm'); const its=leaves(all);
  all.forEach(g=>{ if(g.kids){ g.p.item=[{k:'b',t:g.v.item},{k:'mut',t:g.kids.length+(g.kids.length>1?' itens':' item')}]; g.s.item=g.v.item; } });
  its.forEach(r=>{ const V=r.v; r.p.item=[{k:'txt',t:V.item||''}].concat(V.gar?[{k:'mut',t:V.gar}]:[]); r.s.item=V.item||'';
    r.p.lote=V.lote==='Sim'?[{k:'txt',t:'Lote'},{k:'mut',t:isnum(V.val)?'validade '+V.val+' meses':'sem validade'}]:[{k:'mut',t:'sem lote'}]; r.s.lote=V.lote||'';
    r.p.un=[{k:'b',t:V.un||''}].concat(V.conv?[{k:'mut',t:V.conv}]:[]); r.s.un=V.un||''; r.p.gar=V.gar?[{k:'txt',t:V.gar}]:[{k:'mut',t:'—'}];
    const s=Number(V.saldo)||0; r.p.saldo=s?[{k:'txt',t:nf(s)+' '+(V.sun||V.un)}].concat(V.sx?[{k:'br'},{k:(V.sx.indexOf('bloqueado')>=0?'chip':'mut'),t:V.sx,c:'red'}]:[]):[{k:'mut',t:'sem saldo'}]; r.s.saldo=String(s); });
  RW(self,'g_loc').forEach(r=>{ const n=its.filter(i=>i.v.local===r.v.nome).length; r.v.itens=n; r.nd=n?'com itens':''; r.p.nome=[{k:'b',t:r.v.nome||''}]; r.s.nome=r.v.nome||'';
    r.p.cap=[{k:'txt',t:nf(r.v.cap)+' '+(r.v.capu||'')}]; r.s.cap=String(r.v.cap); }); }
function EXTRAVALS(self,v){ protege(self,v,'g_itm'); protege(self,v,'g_loc');
  valida(self,v,'g_itm',(d,fm)=>{ const e={}; const dup=unico(self,'g_itm',fm,r=>String(r.v.item).toLowerCase(),d.item); if(dup) e.item='Já existe o item '+d.item+' em '+dup.v.grupo+'.'; return e; });
  valida(self,v,'g_loc',(d,fm)=>{ const e={}; const dup=unico(self,'g_loc',fm,r=>String(r.v.nome).toLowerCase(),d.nome); if(dup) e.nome='Já existe o local '+d.nome+'.'; return e; });
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_itm'||!r) return; if(!r.v.saldo){ r.v.saldo=0; }
    // item fica sempre dentro do seu grupo (novo ou com grupo alterado)
    const rm=(list)=>{ const i=list.findIndex(x=>x.id===r.id); if(i>=0){ list.splice(i,1); return true; } return list.some(x=>x.kids&&rm(x.kids)); };
    const cur=rows.find(g=>g.kids&&g.kids.some(k=>k.id===r.id)); if(cur&&cur.v.item===r.v.grupo) return;
    rm(rows); let g=rows.find(x=>x.kids&&x.v.item===r.v.grupo); if(!g){ g={id:'G_'+r.v.grupo,ro:true,v:{item:r.v.grupo},s:{},p:{},kids:[]}; rows.push(g); }
    g.kids.push(r); const x=Object.assign({},(g2st(self,'g_itm').x)||GR('g_itm').x0||{}); x[g.id]=true; g2set(self,'g_itm',{rows:rows,x:x,fl:r.id}); }; }
''')
    HEIGHTS37[fname]=2180
    shell37('CD-06','Produtos, unidades e locais',corpo,fname=fname,subtitle='Cadastre itens com unidade, conversão e rastreio, e os locais onde ficam; saldos e movimentos vivem no Estoque.',
            status=('10 t de KCl em quarentena','yellow'),primary_html=novo('g_itm','Cadastrar item'),search=False)

# ================= CD-07 · Estrutura gerencial =================
DIMS=['Empresa','Natureza','Centro de resultado','Centro de responsabilidade','Cultura','Processo','Projeto']
TRAD=['Conta do ERP','Dimensão própria']
# (id, dimensão, código, nome, início, fim, tradução, conta, TOP, tem lançamentos)
ESTR=[('d1','Empresa','01','Santa Rita Agro','2024-07-01','','Conta do ERP','empresa 1','',True),
      ('d2','Natureza','3.1.01','Fertilizantes · custo direto','2026-07-01','2027-06-30','Conta do ERP','4.1.1.01','1201',True),
      ('d3','Natureza','3.1.02','Defensivos · custo direto','2026-07-01','2027-06-30','Conta do ERP','4.1.1.02','1201',True),
      ('d4','Natureza','3.1.03','Sementes · custo direto','2026-07-01','2027-06-30','Conta do ERP','4.1.1.03','1201',True),
      ('d5','Centro de resultado','CR-SOJA','Soja 2026/27','2026-07-01','2027-06-30','Conta do ERP','centro 201','',True),
      ('d6','Centro de resultado','CR-MILHO','Milho safrinha 2027','2027-01-01','2027-08-31','Conta do ERP','centro 202','',False),
      ('d7','Centro de responsabilidade','CC-OFI','Oficina · apoio','2024-07-01','','Conta do ERP','centro 310','',True),
      ('d8','Cultura','SOJA','Soja','2024-07-01','','Dimensão própria','','',True),
      ('d9','Processo','PULV','Pulverização','2024-07-01','','Dimensão própria','','',True),
      ('d10','Projeto','PRJ-PIVO3','Expansão pivô 3 · investimento','2026-08-01','2027-12-31','Conta do ERP','','',False)]
def cd07():
    fname='CD-07.dc.html'; E._reset_screen(fname)
    g=grid([dict(k='dim',l='Dimensão'),dict(k='cod',l='Código · nome',w=280),dict(k='vig',l='Vigência'),dict(k='conta',l='Tradução no ERP (Sankhya)'),dict(k='est',l='Estado')],
        [R(i,dict(dim=d,cod=c,nome=n,ini=a,fim=b,trad=t,conta=ct,top=tp),nd=('com lançamentos' if l else '')) for i,d,c,n,a,b,t,ct,tp,l in ESTR],
        gid='g_dim',dele=True,total=False,so={'k':'dim','d':False},
        edit=dict(m='form',title='Código',newTitle='Cadastrar código',
            sub='Altere o código e a tradução. A mudança vale para novos lançamentos; fatos já gravados mantêm as dimensões da época.',
            fields=[txt('cod','Código'),txt('nome','Nome'),sel('dim','Dimensão',DIMS,**{'def':'Natureza'}),dat('ini','Início da vigência'),
                    dat('fim','Fim da vigência',req=False,help='Deixe em branco se não houver fim previsto.'),
                    sel('trad','Como a integração traduz',TRAD,**{'def':'Conta do ERP'},help='Dimensão própria segue no lançamento e é traduzida pela integração, sem conta fixa.'),
                    txt('conta','Conta ou centro no ERP',req=False,cond=cond('trad','Conta do ERP'),help='Em branco, o código fica fora da publicação até ser mapeado.'),
                    txt('top','TOP do ERP',req=False,cond=cond('trad','Conta do ERP'))]))
    corpo=bloco('Dimensões e códigos','Cadastre cada código na sua dimensão e traduza para o ERP; nunca combine fazenda, cultura e processo num único centro.',
                g+nota('Um lançamento de pulverização na soja do T1 leva empresa 01 + natureza 3.1.02 + CR-SOJA + cultura SOJA + processo PULV + talhão T1; a integração traduz para a conta 4.1.1.02 · TOP 1201.'),
                acao=mini('sim_pub','Publicar estrutura v6','Publica para novos lançamentos; a v5 fica preservada'))
    js({},r'''
function PREVALS(self,v){ RW(self,'g_dim').forEach(r=>{ const V=r.v;
  r.p.cod=[{k:'b',t:V.cod||''},{k:'mut',t:V.nome||''}]; r.s.cod=(V.cod||'')+' '+(V.nome||'');
  r.p.vig=[{k:'txt',t:V.fim?(br(V.ini)+' – '+br(V.fim)):('desde '+br(V.ini))}]; r.s.vig=V.ini||'';
  const prop=V.trad==='Dimensão própria';
  r.p.conta=prop?[{k:'mut',t:'traduzida na integração'}]:(V.conta?[{k:'txt',t:V.conta+(V.top?' · TOP '+V.top:'')}]:[{k:'mut',t:'sem conta'}]); r.s.conta=V.conta||'';
  const est=prop?['Dimensão própria','gray']:(V.conta?['Mapeado','green']:['Tradução pendente','yellow']); r.p.est=[chipc(est[0],est[1])]; r.s.est=est[0]; }); }
function EXTRAVALS(self,v){ protege(self,v,'g_dim');
  valida(self,v,'g_dim',(d,fm)=>{ const e={}; if(d.fim&&d.ini&&d.fim<d.ini) e.fim='O fim da vigência não pode ser antes do início ('+br(d.ini)+').';
    const dup=unico(self,'g_dim',fm,r=>(r.v.dim+'|'+r.v.cod).toLowerCase(),d.dim+'|'+d.cod); if(dup) e.cod='O código '+d.cod+' já existe em '+d.dim+'.'; return e; });
  v.sim_pub=()=>{ const rs=RW(self,'g_dim'); const pend=rs.filter(r=>r.v.trad!=='Dimensão própria'&&!r.v.conta);
    self.setState({g2toast:'Simulação: v6 publicada para novos lançamentos com '+(rs.length-pend.length)+' de '+rs.length+' códigos · v5 preservada'+(pend.length?' · fora até ter conta: '+pend.map(r=>r.v.cod).join(', '):'')+'.'}); }; }
''')
    HEIGHTS37[fname]=880
    shell37('CD-07','Estrutura gerencial',corpo,fname=fname,subtitle='Cadastre as dimensões independentes que orçamento e fechamento usam e a tradução de cada código para o ERP.',
            status=('1 tradução pendente','yellow'),primary_html=novo('g_dim','Cadastrar código'),search=False)
