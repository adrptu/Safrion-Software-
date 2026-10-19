# -*- coding: utf-8 -*-
"""Tela de entrada do Agrícola por macro contexto (14/10/2026, proprietário: primeiro um teste com setas curvas em 3 blocos; depois "Tire as
setas, alinhe cada submenu no seu macro contexto e coloque titulos em cima dos blocos visuais de cada macro contexto"). Confere no navegador
(areas/modulos.py, ui37.FLUXO37):
  F1 três blocos (listas ordenadas), na ordem; os cartões de cada bloco na ordem decidida (oráculo escrito aqui, não lido do gerador)
  F2 os 14 cartões do menu Agrícola, uma vez cada; nome acessível = nome curto (ui37.CURTO37); ícone; alvo ≥ 44 px
  F3 título em cima de cada bloco: Planejamento, Execução, Resultados (h2 que nomeia a seção); nenhuma das palavras
     Entrada/Processamento/Saída/Input/Output/Processing; sem numeração visível
  F4 sem setas (nenhum SVG ou caminho de seta) e cartões alinhados no bloco: mesma borda esquerda e mesma largura
  F5 1440 × 900: três colunas lado a lado, cada bloco num painel (fundo ou borda, cantos arredondados), título acima do painel;
     cartão no hover do design system
  F6 Tab percorre os cartões na ordem do processo, com foco visível
  F7 clique (mouse real) abre a tela; "‹ Agrícola" volta com o foco no cartão aberto (modVolta)
  F8 800 × 900: três colunas, nenhum nome estoura o cartão
  F9 390 × 844 (toque): uma coluna, blocos empilhados com respiro e o título de cada um, sem rolagem lateral; também 700 × 900,
     1024 × 768 (toque) e 844 × 390 (celular deitado: uma coluna)
  F10 MOD-SUP continua em grade; sem erro de JS
Capturas (só na _render vigente): _probe/mod_fluxo_1440.png e _probe/mod_fluxo_390.png (página inteira).
Uso: python3 mod_fluxo_test.py (lê _render ou RENDER_DIR). Contraprova: RENDER_DIR=<_render com setas> reprova F3 e F4."""
import os, sys, json, time, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import ui37

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
SHOT = not os.environ.get('RENDER_DIR')
B1 = [('AG-07.dc.html', 'Agrofit'), ('AG-02.dc.html', 'Análises de solo'), ('PA.dc.html', 'Planos agronômicos'), ('SAF.dc.html', 'Planejar safra'), ('GE-02.dc.html', 'Orçamento')]
B2 = [('AG-01.dc.html', 'Pragas e doenças'), ('OS.dc.html', 'Ordens de serviço'), ('IR-01.dc.html', 'Irrigação'), ('COLH.dc.html', 'Colheita')]
B3 = [('CARGA.dc.html', 'Recebimento'), ('BEN.dc.html', 'Beneficiamento'), ('PROD.dc.html', 'Estoque de produto'), ('GE-03.dc.html', 'Custos'), ('PG.dc.html#mod=agr', 'Painel')]   # PAINEL-03 (18/10): o Painel do Agrícola é a aba do painel único
ESP = [B1, B2, B3]; ORDEM = [h for b in ESP for h, _ in b]
MENU_AGR = [h for n, ic, its in ui37.MENU2 if n == 'Agrícola' for l, h in its]
PROIBIDAS = r'\b(entrada|processamento|saída|saida|input|output|processing)\b'

p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def espera(js, ate=4.0):
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.1)
    return False
ERRS = []
def junta(pg):
    e = J("(window.__errs||[]).join(' | ')") or ''
    if e: ERRS.append([pg, e[:400]])
def tela(pg, w, h, esc=1, toque=False, limpa=False):
    c.aparelho(w, h, esc, toque)
    if limpa: c.goto(U('Main.dc.html'), .3); J("try{localStorage.clear(); sessionStorage.clear();}catch(e){}")
    c.goto(U(pg), 1.0); espera("document.readyState==='complete' && document.querySelectorAll('a.mod-cartao').length>0")
    time.sleep(.3)
def pagina_inteira(path, w, h, esc, toque):
    if not SHOT: return
    hh = int(J("Math.ceil(document.querySelector('main').getBoundingClientRect().top + document.querySelector('main').scrollHeight + 24)") or h)
    if hh > h: c.aparelho(w, hh, esc, toque); time.sleep(.6)
    c.shot(path); c.aparelho(w, h, esc, toque); time.sleep(.4)

ESTR = """JSON.stringify((()=>{ const f=document.querySelector('.mod-fluxo'); const N=s=>(s||'').replace(/\\s+/g,' ').trim();
  const bl=f?[...f.querySelectorAll('.mod-sec > ol.mod-bloco')]:[];
  const lab=[...document.querySelectorAll('main [aria-label], main [title], main [alt]')].map(e=>[e.getAttribute('aria-label'),e.getAttribute('title'),e.getAttribute('alt')].filter(Boolean).join(' '));
  const cs=[...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length);
  return { fluxo:!!f, blocos:bl.map(o=>[o.tagName, o.getAttribute('role'), [...o.children].map(li=>[li.tagName, li.children.length===1&&li.firstElementChild.matches('a.mod-cartao')?li.firstElementChild.getAttribute('href'):null, N(li.innerText)])]),
    todos:cs.map(a=>a.getAttribute('href')), nomes:cs.map(a=>[a.getAttribute('href'), N(a.innerText), !!a.querySelector('.mod-ic svg path'), Math.round(a.getBoundingClientRect().width), Math.round(a.getBoundingClientRect().height)]),
    texto:N(document.body.innerText), rotulos:lab.join(' | '), txtFluxo:f?N(f.innerText):'',
    marcas:f?[...f.querySelectorAll('li')].map(li=>getComputedStyle(li).display==='list-item'&&getComputedStyle(li).listStyleType!=='none').filter(Boolean).length:-1,
    titulos:f?[...f.querySelectorAll('.mod-sec')].map(sc=>{ const h=sc.querySelector(':scope > h2'); return [h?N(h.innerText):'', !!h&&sc.getAttribute('aria-labelledby')===h.id]; }):[] }; })())"""

GEO = """JSON.stringify((()=>{ const f=document.querySelector('.mod-fluxo'); if(!f) return null;
  const cs=[...f.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length);
  const secs=[...f.querySelectorAll('.mod-sec')].map(sc=>{ const o=sc.querySelector('ol.mod-bloco'), h=sc.querySelector(':scope > h2'), r=o.getBoundingClientRect(), s=getComputedStyle(o), rh=h?h.getBoundingClientRect():null;
    const cr=[...o.querySelectorAll('a.mod-cartao')].map(a=>a.getBoundingClientRect());
    return { r:[r.left,r.top,r.right,r.bottom].map(Math.round), fundo:s.backgroundColor, borda:s.borderTopStyle, raio:parseFloat(s.borderTopLeftRadius)||0,
      tit:h?h.innerText.trim():'', titAcima:!!rh&&rh.bottom<=r.top+1, esq:[...new Set(cr.map(x=>Math.round(x.left)))], larg:[...new Set(cr.map(x=>Math.round(x.width)))] }; });
  const est=cs.map(a=>{ const t=a.lastElementChild; return a.scrollWidth>a.clientWidth+1||(t&&t.scrollWidth>t.clientWidth+1)?a.getAttribute('href'):null; }).filter(Boolean);
  return { setas:document.querySelectorAll('svg.mod-setas, path.mod-seta, .mod-fluxo svg:not(.mod-ic svg):not(a svg)').length, secs, est,
    sw:document.documentElement.scrollWidth, iw:innerWidth }; })())"""
TIT = ['Planejamento', 'Execução', 'Resultados']
def blocos_ok(g, colunas):
    """problemas da geometria: títulos em cima, cartões alinhados, sem setas, sem estouro, colunas ou pilha"""
    if not g: return ['sem blocos']
    ruins = []
    sc = g.get('secs') or []
    if [x['tit'] for x in sc] != TIT: ruins.append(['títulos', [x['tit'] for x in sc]])
    if not all(x['titAcima'] for x in sc): ruins.append('título não está em cima do painel')
    if not all(len(x['esq']) == 1 and len(x['larg']) == 1 for x in sc): ruins.append(['cartões desalinhados', [[x['esq'], x['larg']] for x in sc]])
    if g.get('setas'): ruins.append(['setas', g['setas']])
    if g.get('est'): ruins.append(['nome estoura', g['est']])
    if g.get('sw', 9999) > g.get('iw', 0): ruins.append(['rolagem lateral', g.get('sw'), g.get('iw')])
    if len(sc) == 3:
        lado = all(abs(sc[i]['r'][1] - sc[0]['r'][1]) <= 2 for i in range(3)) and all(sc[i]['r'][2] < sc[i + 1]['r'][0] for i in range(2))
        pilha = all(abs(sc[i]['r'][0] - sc[0]['r'][0]) <= 1 for i in range(3)) and all(sc[i + 1]['r'][1] - sc[i]['r'][3] >= 12 for i in range(2))
        if colunas and not lado: ruins.append(['não estão lado a lado', [x['r'] for x in sc]])
        if not colunas and not pilha: ruins.append(['não estão empilhados', [x['r'] for x in sc]])
    return ruins

try:
    # ---------- 1440 × 900 ----------
    tela('MOD-AGR.dc.html', 1440, 900, limpa=True)
    st = json.loads(J(ESTR) or '{}'); bl = st.get('blocos') or []
    chk('F1 três blocos, cada um uma lista ordenada (ol), na ordem do processo', st.get('fluxo') and [b[0] for b in bl] == ['OL'] * 3, bl)
    chk('F1 cartões de cada bloco na ordem decidida (Agrofit → … → Orçamento · Pragas e doenças → … → Colheita · Recebimento → … → Painel)',
        [[[x[1], x[2]] for x in b[2]] for b in bl] == [[list(x) for x in b] for b in ESP] and all(x[0] == 'LI' for b in bl for x in b[2]), [[x[1:] for x in b[2]] for b in bl])
    chk('F1 a definição do gerador (ui37.FLUXO37) é a mesma ordem, com os títulos', getattr(ui37, 'FLUXO37', {}).get('Agrícola') == [(t, [h for h, _ in b]) for t, b in zip(TIT, ESP)], getattr(ui37, 'FLUXO37', None))
    todos = st.get('todos') or []
    chk(f'F2 os {len(MENU_AGR)} cartões do menu Agrícola presentes uma vez cada (nenhum a mais)', len(MENU_AGR) == 14 and sorted(todos) == sorted(MENU_AGR) and len(set(todos)) == len(todos), [len(todos), sorted(set(MENU_AGR) ^ set(todos))])
    nm = st.get('nomes') or []
    chk('F2 nome de cada cartão = nome curto do menu (CURTO37), com ícone, alvo ≥ 44 px', nm and all(x[1] == ui37.CURTO37[x[0]][0] and x[2] and x[3] >= 44 and x[4] >= 44 for x in nm), nm)
    pr = sorted(set(m.lower() for m in re.findall(PROIBIDAS, (st.get('texto') or '') + ' ' + (st.get('rotulos') or ''), re.I)))
    chk('F3 nenhuma das palavras Entrada/Processamento/Saída/Input/Output/Processing na página (texto e rótulos)', not pr, pr)
    chk('F3 título em cima de cada bloco (h2 que nomeia a seção): Planejamento, Execução, Resultados; sem numeração visível',
        st.get('titulos') == [[t, True] for t in TIT] and st.get('marcas') == 0, [st.get('titulos'), st.get('marcas')])
    g = json.loads(J(GEO) or 'null') or {}
    r4 = blocos_ok(g, True)
    chk('F4 sem setas; cartões alinhados no bloco (mesma borda esquerda e largura); F5 três colunas lado a lado, sem estouro nem rolagem lateral', not r4, r4)
    painel = all((x['fundo'] not in ('rgba(0, 0, 0, 0)', 'transparent') or x['borda'] != 'none') and x['raio'] >= 8 for x in g.get('secs') or [])
    chk('F5 1440: cada bloco num painel discreto (fundo próprio ou borda, cantos arredondados)', painel and len(g.get('secs') or []) == 3, g.get('secs'))
    # o Chrome de teste não casa (hover:hover) (como em nav_modulos_test N7): as regras da página sob essa condição são copiadas sem ela,
    # como num computador com mouse; o ponteiro real (CDP) passa por cima do SVG das setas até o cartão
    J(r"""(()=>{ const t=[]; [...document.styleSheets].forEach(ss=>{ let rs=[]; try{ rs=[...ss.cssRules]; }catch(e){} rs.forEach(r=>{ if(r.media&&/hover:\s*hover/.test(r.media.mediaText)) [...r.cssRules].forEach(x=>t.push(x.cssText)); }); });
      const st=document.createElement('style'); st.id='simula-hover'; st.textContent=t.join('\n'); document.head.appendChild(st); })()""")
    xy = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.mod-cartao[href=\"OS.dc.html\"]'); const r=a.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})())"))
    c.mouse(*xy); time.sleep(.25)
    hv = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.mod-cartao[href=\"OS.dc.html\"]'); const s=getComputedStyle(a); return [a.matches(':hover'), s.borderTopColor, s.backgroundColor];})())"))
    chk('F5 hover do design system no cartão (borda verde e fundo claro)', hv == [True, 'rgb(30, 122, 76)', 'rgb(242, 248, 244)'], hv)
    c.mouse(1430, 890); J("(document.getElementById('simula-hover')||{remove:()=>0}).remove()"); time.sleep(.2)
    pagina_inteira(os.path.join(HERE, '_probe', 'mod_fluxo_1440.png'), 1440, 900, 1, False)
    # ---------- Tab ----------
    J("(()=>{const a=document.querySelector('.mod-fluxo a.mod-cartao')||document.querySelector('a.mod-cartao'); a&&a.focus();})()")
    seq = [J("(document.activeElement&&document.activeElement.getAttribute('href'))||''")]
    vis = []
    for _ in range(len(ORDEM) - 1):
        c.tab(); seq.append(J("(document.activeElement&&document.activeElement.getAttribute('href'))||''"))
        vis.append(J("(()=>{const s=getComputedStyle(document.activeElement); return s.outlineStyle==='solid'&&s.outlineColor==='rgb(30, 122, 76)';})()"))
    J("(()=>{const a=document.querySelector('.mod-fluxo a.mod-cartao')||document.querySelector('a.mod-cartao'); a&&a.focus();})()"); c.tab(shift=True)   # antes do 1º, nenhum cartão
    antes = J("(document.activeElement&&document.activeElement.matches&&document.activeElement.matches('a.mod-cartao'))||false")
    chk('F6 Tab percorre os 14 cartões na ordem do fluxo, com foco visível; antes do 1º não há cartão', seq == ORDEM and all(vis) and not antes, [seq, vis, antes])
    # ---------- clique e volta ----------
    junta('MOD-AGR.dc.html 1440'); J("try{sessionStorage.clear();}catch(e){}"); c.goto(U('MOD-AGR.dc.html'), 1.0); espera("document.querySelectorAll('a.mod-cartao').length>0", 3)
    xy = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.mod-cartao[href=\"PROD.dc.html\"]'); const r=a.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})())"))
    topo = J(f"(()=>{{const e=document.elementFromPoint({xy[0]},{xy[1]}); return e&&e.closest('a')?e.closest('a').getAttribute('href'):String(e&&e.tagName);}})()")
    junta('MOD-AGR.dc.html')
    c.mouse(*xy, 'mousePressed', 'left'); c.mouse(*xy, 'mouseReleased', 'left')
    abriu = espera("location.pathname.endsWith('/PROD.dc.html') && document.readyState==='complete' && !!document.querySelector('a.volta37')", 6)
    vv = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.volta37'); if(!a) return null; const r=a.getBoundingClientRect(); return [a.getAttribute('href'), a.innerText.replace(/\\s+/g,' ').trim(), r.left+r.width/2, r.top+r.height/2];})())") or 'null')
    junta('PROD.dc.html')
    if vv: c.mouse(vv[2], vv[3], 'mousePressed', 'left'); c.mouse(vv[2], vv[3], 'mouseReleased', 'left')
    voltou = espera("location.pathname.endsWith('/MOD-AGR.dc.html') && document.readyState==='complete' && (document.activeElement&&document.activeElement.getAttribute('href'))==='PROD.dc.html'", 6)
    chk('F7 o clique no cartão abre a tela; "‹ Agrícola" volta com o foco no cartão aberto',
        topo == 'PROD.dc.html' and abriu and vv and vv[:2] == ['MOD-AGR.dc.html', '‹ Agrícola'] and voltou, [topo, abriu, vv and vv[:2], voltou, J("location.pathname"), J("(document.activeElement&&document.activeElement.getAttribute('href'))||''")])
    # ---------- 800 × 900 ----------
    tela('MOD-AGR.dc.html', 800, 900)
    r8 = blocos_ok(json.loads(J(GEO) or 'null') or {}, True)
    chk('F8 800 × 900: três colunas com título em cima, cartões alinhados, sem setas, nenhum nome estoura o cartão', not r8, r8)
    junta('MOD-AGR.dc.html 800')
    # ---------- 390 × 844 (toque) ----------
    tela('MOD-AGR.dc.html', 390, 844, 2, True)
    r9 = blocos_ok(json.loads(J(GEO) or 'null') or {}, False)
    chk('F9 390: uma coluna, blocos empilhados com respiro (≥ 12 px) e título em cima, cartões alinhados, sem rolagem lateral', not r9, r9)
    pagina_inteira(os.path.join(HERE, '_probe', 'mod_fluxo_390.png'), 390, 844, 2, True)
    junta('MOD-AGR.dc.html 390')
    ruins = []
    for w, h, e, t in ((700, 900, 1, False), (1024, 768, 1, True), (844, 390, 2, True)):
        tela('MOD-AGR.dc.html', w, h, e, t); rx = blocos_ok(json.loads(J(GEO) or 'null') or {}, h > 560 and w > 640)
        if rx: ruins.append([w, h, rx])
        junta(f'MOD-AGR.dc.html {w}x{h}')
    chk('F9 700 × 900, 1024 × 768 (toque) e 844 × 390 (celular deitado: uma coluna): títulos em cima, alinhados, sem estouro nem rolagem lateral', not ruins, ruins[:2])
    # ---------- outro hub ----------
    tela('MOD-SUP.dc.html', 1440, 900)
    sp = json.loads(J("JSON.stringify([!!document.querySelector('.mod-fluxo'), document.querySelectorAll('svg.mod-setas, path.mod-seta').length, !!document.querySelector('.mod-grade[role=list]'), [...document.querySelectorAll('.mod-grade[role=list] a.mod-cartao')].map(a=>a.getAttribute('href'))])"))
    esp_sup = [h for n, ic, its in ui37.MENU2 if n == 'Suprimentos' for l, h in its]
    chk('F10 MOD-SUP continua em grade, na ordem do menu, sem blocos', sp == [False, 0, True, esp_sup], [sp, esp_sup])
    junta('MOD-SUP.dc.html')
    chk('F10 sem erro de JS (MOD-AGR a 1440, 800, 390, 700, 1024 e 844 × 390, PROD e MOD-SUP)', not ERRS, ERRS)
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
