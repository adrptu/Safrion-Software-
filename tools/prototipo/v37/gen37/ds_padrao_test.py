# -*- coding: utf-8 -*-
"""Padronização do design system (proprietário, 15/10/2026: "tem várias tela com design system diferente, padronize tudo de melhor que
definimos e evoluimos"). Confere no navegador as regras dos componentes comuns, não tela a tela:
  T · alvo de toque (DS-ALVO-20261015): a 390 × 844 com toque, botão do componente (BTN_ST/btn, _MINI, ação de célula g2cta) e escolha em
      pílula (chip de filtro rápido, aria-pressed) têm pelo menos 44 px de altura; a 1440 × 900 com mouse nada cresce (compacto < 44 px).
  M · "⋯ Mais ações" único (DS-MAIS-20261015, engine.mais + g2lib): nome e dica "Mais ações de <contexto>", aria-haspopup=menu,
      aria-expanded; menu fechado escondido; itens role=menuitem com verbo; abrir leva o foco ao 1º item, ↓ anda, Esc fecha e devolve o
      foco ao ⋯, clicar fora fecha, escolher um item faz a ação e fecha; restaurar a demonstração (Manutenção) pede confirmação fora do
      menu; a 390 px com toque o ⋯ tem 44 × 44 px e o menu cabe na tela; nenhum ⋯ antigo (sem contexto) sobra. MAIS-01: em cada fileira de
      ações (cabeçalho de bloco, barra do bloco) no máximo uma secundária à vista; as outras estão no ⋯ (6 telas recolhidas).
  V · um verde por contexto, com verbo (BOT-01/03/08): em 6 telas, no máximo um verde à vista por contexto (cabeçalho, bloco, cartão,
      linha, barra de ações); nenhum verde que só navega ("Abrir/Ver/Voltar/Consultar …" em link) e nenhum rótulo "Novo/Nova …";
      botões do engine (raio 10 px), sem o estilo local de raio 9 px.
  F · filtros só na faixa padrão (FIL-02): na O.S. e na Manutenção (Sem ordem, Ordens) nenhum grupo de chips de filtro nem seletor fora
      da faixa .mf-tela (a troca de visão e o filtro rápido da grade não contam); Fase da O.S. e Fase/Rotina/Prazo da Manutenção dentro dela;
      a 390 px os da Manutenção viram seletor, na mesma faixa.
Uso (de gen37/, depois de build.py e montar_render.py): python3 ds_padrao_test.py · RENDER_DIR=<dir> serve outro _render."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
ERRS = []
def erros():
    try:
        e = J("window.__err||''")
        if e: ERRS.append(e)
    except Exception: pass
def abre(pg, w=1.2): erros(); c.goto(U(pg), w); time.sleep(.3)

# ---------- T · alvo de toque ----------
# componente: estilo inline com a variável do alvo (BTN_ST, btn, _MINI, act), a ação de célula (.g2cta) e a escolha em pílula com estado
ALVOS = r"""JSON.stringify((()=>{const vis=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
  const n=s=>(s||'').replace(/\s+/g,' ').trim();
  return [...document.querySelectorAll('main button, main a[href], header button, header a[href]')].filter(vis).filter(e=>!e.closest('[role=dialog],aside,.menu-lat'))
    .filter(e=>/--g2-alvo/.test(e.getAttribute('style')||'')||e.classList.contains('g2cta')||(e.hasAttribute('aria-pressed')&&/border-radius: 999px/.test(e.getAttribute('style')||'')))
    .map(e=>({t:n(e.innerText||e.getAttribute('aria-label')).slice(0,30),h:Math.round(e.getBoundingClientRect().height*10)/10,k:e.classList.contains('g2cta')?'g2cta':(e.hasAttribute('aria-pressed')?'chip':'btn')}));})())"""
PAG_T = ['AG-01.dc.html', 'GE-02.dc.html', 'PL-03.dc.html', 'IR-01.dc.html', 'CO-02.dc.html', 'VE-01.dc.html']
def parte_t():
    c.aparelho(390, 844, 2, True)
    baixos = {}; tipos = set(); total = 0
    for pg in PAG_T:
        abre(pg); a = json.loads(J(ALVOS) or '[]'); total += len(a); tipos |= {x['k'] for x in a}
        b = [x for x in a if x['h'] < 44]
        if b: baixos[pg] = b[:5]
    chk('T1 390 px com toque: botão do componente, ação de célula da grade e chip de filtro rápido com alvo ≥ 44 px (6 telas)',
        total >= 20 and not baixos and {'btn', 'g2cta', 'chip'} <= tipos, [total, sorted(tipos), baixos])
    c.aparelho(1440, 900, 1, False)
    abre('AG-01.dc.html'); a = json.loads(J(ALVOS) or '[]')
    chk('T2 1440 px com mouse: nada cresce (ação de célula e chip continuam compactos, < 44 px)',
        a and min(x['h'] for x in a) < 40 and any(x['k'] == 'g2cta' and x['h'] < 40 for x in a), a[:6])
    st = json.loads(J("JSON.stringify((()=>{const b=document.querySelector('a.g2cta,button.g2cta'); if(!b) return null; const s=getComputedStyle(b); return [s.paddingTop+' '+s.paddingRight,s.borderTopLeftRadius,s.fontSize,s.fontWeight];})())") or 'null')
    chk('T3 ação de célula da grade (g2cta) com o desenho do _MINI do engine: 5px 10px, raio 8 px, 12 px/700', st == ['5px 10px', '8px', '12px', '700'], st)

# ---------- M · "⋯ Mais ações" ----------
VERBO = r"^(\+\s*)?([A-Za-zÀ-ú]+(ar|er|ir|or|ôr)|Faça|Siga|Veja)\b"
MAISV = r"""JSON.stringify([...document.querySelectorAll('button.g2mais')].filter(b=>b.getClientRects().length).map(b=>{const m=b.nextElementSibling;
  return {al:b.getAttribute('aria-label'),dica:b.getAttribute('data-dica'),pop:b.getAttribute('aria-haspopup'),exp:b.getAttribute('aria-expanded'),
    menu:!!m&&m.getAttribute('role')==='menu'&&m.classList.contains('g2mais-menu'),fechado:!!m&&!m.getClientRects().length,
    itens:m?[...m.querySelectorAll('[role=menuitem]')].map(i=>i.textContent.replace(/\s+/g,' ').trim()):[]};}))"""
ANTIGO = "[...document.querySelectorAll('button,summary')].filter(b=>b.getClientRects().length&&b.getAttribute('aria-label')==='Mais ações').length"
FOCO = "(()=>{const a=document.activeElement; return a?[a.getAttribute('role')||'',a.classList.contains('g2mais'),(a.textContent||'').trim().slice(0,40)]:null;})()"
def mais_estado(): return json.loads(J(MAISV) or '[]')
def clica_mais(ctx): return J(f"(()=>{{const b=[...document.querySelectorAll('button.g2mais')].find(b=>b.getClientRects().length&&b.getAttribute('aria-label')==={json.dumps('Mais ações de '+ctx)}); if(!b) return false; b.click(); return true;}})()")
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def parte_m():
    c.aparelho(1440, 900, 1, False)
    import re as _re
    PAG_M = ['MA.dc.html', 'PA.dc.html#plano=SOJA-AT', 'PL-03.dc.html', 'GE-02.dc.html']
    ruins = {}; vistos = 0; antigos = {}
    for pg in PAG_M:
        abre(pg, 1.6); ms = mais_estado(); vistos += len(ms)
        for m in ms:
            if not (m['al'] and m['al'].startswith('Mais ações de ') and m['dica'] == m['al'] and m['pop'] == 'menu' and m['exp'] == 'false' and m['menu'] and m['fechado']
                    and m['itens'] and all(_re.match(VERBO, i) for i in m['itens'])):
                ruins.setdefault(pg, []).append(m)
        n = J(ANTIGO)
        if n: antigos[pg] = n
        if not ms: ruins.setdefault(pg, []).append('sem ⋯')
    chk('M1 ⋯ com nome e dica "Mais ações de <contexto>", aria-haspopup=menu, aria-expanded=false, menu fechado escondido, itens com verbo (Manutenção, Biblioteca de planos, Capacidade, Orçamento)',
        vistos >= 4 and not ruins, [vistos, ruins])
    chk('M2 nenhum ⋯ antigo sem contexto (aria-label "Mais ações") nas mesmas telas', not antigos, antigos)
    abre('PL-03.dc.html', 1.4); ctx = 'Cenários para o déficit de 270 h'
    ok1 = clica_mais(ctx); time.sleep(.3); e1 = mais_estado(); f1 = J(FOCO)
    c.tecla('ArrowDown', 'ArrowDown', 40); f2 = J(FOCO)
    c.tecla('Escape', 'Escape', 27); time.sleep(.2); e3 = mais_estado(); f3 = J(FOCO)
    aberto = [m for m in e1 if m['al'] == 'Mais ações de ' + ctx]
    chk('M3 abrir o ⋯ (PL-03 · Cenários): aria-expanded=true, menu à vista, foco no 1º item; ↓ vai ao 2º; Esc fecha e devolve o foco ao ⋯',
        ok1 and aberto and aberto[0]['exp'] == 'true' and not aberto[0]['fechado'] and f1 and f1[0] == 'menuitem' and f2 and f2[0] == 'menuitem' and f2[2] != f1[2]
        and all(m['exp'] == 'false' for m in e3) and f3 and f3[1], [ok1, aberto, f1, f2, f3])
    clica_mais(ctx); time.sleep(.2); J("document.querySelector('main h1, header h1').click()"); time.sleep(.2); e4 = mais_estado()
    clica_mais(ctx); time.sleep(.2); it = J("(()=>{const m=document.querySelector('button.g2mais[aria-expanded=true]+.g2mais-menu'); const i=m&&[...m.querySelectorAll('[role=menuitem]')].find(x=>/^Planejar pessoal/.test(x.textContent.trim())); if(!i) return ''; i.click(); return i.textContent.trim();})()")
    time.sleep(.5); t5 = toast(); e5 = mais_estado(); f5 = J(FOCO)
    chk('M4 clicar fora fecha; escolher "Planejar pessoal" no ⋯ mostra o resultado e fecha o menu, com o foco de volta no ⋯',
        all(m['exp'] == 'false' for m in e4) and it.startswith('Planejar pessoal') and 'Necessidade de pessoal' in t5 and all(m['exp'] == 'false' for m in e5) and f5 and f5[1], [e4, it, t5[:80], f5])
    abre('MA.dc.html', 1.6); clica_mais('Manutenção'); time.sleep(.3)
    J("[...document.querySelectorAll('.g2mais-menu [role=menuitem]')].find(i=>i.textContent.trim()==='Restaurar demonstração').click()"); time.sleep(.4)
    conf = J("(()=>{const d=document.querySelector('[role=alertdialog][aria-label=\"Restaurar demonstração\"]'); return d&&d.getClientRects().length?d.innerText.replace(/\\s+/g,' ').trim():'';})()")
    J("[...document.querySelectorAll('[role=alertdialog] button')].find(b=>b.innerText.trim()==='Manter').click()"); time.sleep(.3)
    conf2 = J("!!document.querySelector('[role=alertdialog][aria-label=\"Restaurar demonstração\"]')")
    chk('M5 Manutenção: ⋯ › Restaurar demonstração pede confirmação fora do menu (Restaurar / Manter); Manter fecha sem restaurar',
        'Restaurar toda a demonstração' in conf and 'Manter' in conf and not conf2, [conf, conf2])
    c.aparelho(390, 844, 2, True); abre('PL-03.dc.html', 1.4)
    J(f"(()=>{{const b=[...document.querySelectorAll('button.g2mais')].find(b=>b.getAttribute('aria-label')==={json.dumps('Mais ações de '+ctx)}); b.scrollIntoView({{block:'center'}});}})()"); time.sleep(.3)
    clica_mais(ctx); time.sleep(.3)
    g = json.loads(J("JSON.stringify((()=>{const b=document.querySelector('button.g2mais[aria-expanded=true]'); if(!b) return null; const m=b.nextElementSibling; const r=b.getBoundingClientRect(), q=m.getBoundingClientRect(); return {w:r.width,h:r.height,l:q.left,r:q.right,vw:innerWidth,it:Math.min(...[...m.querySelectorAll('[role=menuitem]')].map(i=>i.getBoundingClientRect().height))};})())") or 'null')
    chk('M6 390 px com toque: ⋯ com 44 × 44 px, itens com 44 px e o menu inteiro dentro da tela', g and g['w'] >= 44 and g['h'] >= 44 and g['it'] >= 44 and g['l'] >= 0 and g['r'] <= g['vw'], g)

# MAIS-01: fileira de ações = os botões com borda (secundários) do mesmo contêiner flex, fora de tabela, painel, faixa, menu e grupo de opções
FILEIRAS = r"""JSON.stringify((()=>{const vis=e=>e.getClientRects().length; const n=s=>(s||'').replace(/\s+/g,' ').trim();
 const bs=[...document.querySelectorAll('main button, main a[href], header button, header a[href]')].filter(vis).filter(b=>!b.closest('[role=table],[role=dialog],aside,.mf-tela,nav,.g2mais-menu,.acoes,[role=tablist],[role=group],.menu-lat')&&!b.hasAttribute('aria-pressed')&&!b.matches('.g2mais,.volta37,.g2-info,.g2dica-i,[aria-label=Voltar]')&&!/^‹/.test(n(b.innerText)));
 const sec=b=>{const cs=getComputedStyle(b); return cs.backgroundColor!=='rgb(30, 122, 76)'&&parseFloat(cs.borderTopWidth)>0&&/[a-zà-ú]/i.test(b.innerText)};
 const g=new Map(); for(const b of bs){ if(!sec(b)) continue; let p=b.parentElement; while(p&&getComputedStyle(p).display.indexOf('flex')<0&&p.tagName!=='MAIN') p=p.parentElement; if(!g.has(p)) g.set(p,[]); g.get(p).push(n(b.innerText).slice(0,30)); }
 return [...g.values()].filter(v=>v.length>=2);})())"""
def parte_r():
    c.aparelho(1440, 900, 1, False); ruins = {}
    for pg in ['PL-02.dc.html', 'PL-03.dc.html', 'GE-02.dc.html', 'CA-01.dc.html', 'CO-02det.dc.html', 'MA.dc.html#vis=semordem']:
        abre(pg, 1.4); f = json.loads(J(FILEIRAS) or '[]')
        if f: ruins[pg] = f
    chk('M7 MAIS-01: nenhuma fileira de ações com 2+ secundárias à vista (PL-02, PL-03, GE-02, CA-01, CO-02det, Manutenção › Sem ordem)', not ruins, ruins)

VERDES = r"""JSON.stringify((()=>{const vis=e=>e.getClientRects().length; const n=s=>(s||'').replace(/\s+/g,' ').trim();
 const verde=e=>{const cs=getComputedStyle(e); return cs.backgroundColor==='rgb(30, 122, 76)'&&parseFloat(cs.borderTopLeftRadius)<14&&!e.hasAttribute('aria-pressed');};
 const ctx=e=>{ for(let p=e.parentElement;p;p=p.parentElement){ if(p.matches('[role=row],tr,.acoes,[data-acoes],section,aside,[role=dialog]')) return p;
   if(p.matches('header')&&!p.closest('main')) return p; if(p.tagName==='MAIN') return p;
   const cs=getComputedStyle(p); if(parseFloat(cs.borderTopWidth)>0&&parseFloat(cs.borderTopLeftRadius)>=10&&p.getBoundingClientRect().height>=56) return p; } return document.body; };
 const els=[...document.querySelectorAll('header button,header a[href],main button,main a[href],.acoes button,.acoes a')].filter(vis).filter(e=>!e.closest('.menu-lat,.g2mais-menu'));
 const g=new Map(); const nav=[], novo=[], raio9=[];
 for(const e of els){ const t=n(e.innerText); if(/^\+?\s*Nov[oa]s?\b/.test(t)) novo.push(t); if(getComputedStyle(e).borderTopLeftRadius==='9px'&&parseFloat(getComputedStyle(e).borderTopWidth)>0) raio9.push(t.slice(0,30));
   if(!verde(e)) continue; if(e.tagName==='A'&&/^(Abrir|Ver|Voltar|Consultar)\b/.test(t)) nav.push(t); const c=ctx(e); if(!g.has(c)) g.set(c,[]); g.get(c).push(t.slice(0,40)); }
 return {mais:[...g.values()].filter(v=>v.length>1),nav,novo,raio9,n:[...g.values()].reduce((a,v)=>a+v.length,0)};})())"""
def parte_v():
    c.aparelho(1440, 900, 1, False); ruins = {}; total = 0
    for pg in ['OS.dc.html', 'SAF.dc.html', 'PL-03.dc.html', 'VE-03.dc.html', 'CD-01.dc.html', 'PT-04.dc.html']:
        abre(pg, 1.6); v = json.loads(J(VERDES) or '{}'); total += v.get('n', 0)
        if v.get('mais') or v.get('nav') or v.get('novo') or v.get('raio9'): ruins[pg] = v
    chk('V1 um verde por contexto, sem verde que só navega, sem "Novo/Nova" e sem botão local de raio 9 px (O.S., Planejar safra, Capacidade, Ofertas, Cadastro de fazendas, Crédito)',
        total >= 3 and not ruins, [total, ruins])
    abre('OS.dc.html', 1.6)
    h = J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Criar ordem'); return b?getComputedStyle(b).backgroundColor:'';})()")
    chk('V2 O.S.: "Criar ordem" é a primária do cabeçalho (antes "Nova ordem" com estilo local no bloco)', h == 'rgb(30, 122, 76)', h)

FORA = r"""JSON.stringify((()=>{const vis=e=>e.getClientRects().length;
 const g2bar=e=>{ for(let p=e.parentElement,i=0;p&&i<5;p=p.parentElement,i++) if(p.querySelector(':scope > [data-g2q]')) return true; return false; };
 const grupos=[...document.querySelectorAll('main [role=group]')].filter(g=>vis(g)&&g.querySelector('[aria-pressed]')&&!g.closest('.mf-tela,[role=dialog],aside,[role=table]')&&!g2bar(g)&&!/^vis[aã]o/i.test(g.getAttribute('aria-label')||'')).map(g=>g.getAttribute('aria-label'));
 const sels=[...document.querySelectorAll('main select')].filter(s=>vis(s)&&!s.closest('.mf-tela,[role=dialog],aside,[role=table]')&&!/^vis[aã]o/i.test(s.getAttribute('aria-label')||'')).map(s=>s.getAttribute('aria-label'));
 const dentro=[...document.querySelectorAll('.mf-tela [role=group][aria-label^="Filtrar por"], .mf-tela [role=group][aria-label^="Prazo"], .mf-tela [role=group][aria-label=Rotina], .mf-tela select')].filter(vis).map(g=>g.getAttribute('aria-label'));
 return {grupos,sels,dentro};})())"""
def parte_f():
    c.aparelho(1440, 900, 1, False); r = {}
    for pg in ['OS.dc.html', 'MA.dc.html#vis=ordens', 'MA.dc.html#vis=semordem']:
        abre(pg, 1.6); r[pg] = json.loads(J(FORA) or '{}')
    ok = (all(not v['grupos'] and not v['sels'] for v in r.values()) and 'Filtrar por fase' in r['OS.dc.html']['dentro']
          and {'Filtrar por fase', 'Rotina'} <= set(r['MA.dc.html#vis=ordens']['dentro']) and 'Prazo pelo início da janela' in r['MA.dc.html#vis=semordem']['dentro'])
    chk('F1 1440 px: nenhum grupo de chips de filtro nem seletor fora da faixa (O.S., Manutenção › Ordens e Sem ordem); Fase, Rotina e Prazo dentro dela', ok, r)
    c.aparelho(390, 844, 2, True); abre('MA.dc.html#vis=ordens', 1.6); m = json.loads(J(FORA) or '{}')
    chk('F2 390 px: Manutenção › Ordens com Fase e Rotina como seletores dentro da faixa, nada fora dela',
        not m['grupos'] and not m['sels'] and {'Filtrar por fase', 'Filtrar por rotina'} <= set(m['dentro']), m)

PARTES = set((os.environ.get('DS_PARTES') or 'T,M,V,F').split(','))
try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    if 'T' in PARTES: parte_t()
    if 'M' in PARTES: parte_m(); parte_r()
    if 'V' in PARTES: parte_v()
    if 'F' in PARTES: parte_f()
    erros(); chk('Z sem erro de JS nas telas abertas', not ERRS, ERRS[:3])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
