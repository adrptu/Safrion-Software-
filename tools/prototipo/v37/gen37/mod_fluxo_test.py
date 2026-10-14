# -*- coding: utf-8 -*-
"""Tela de entrada do Agrícola como fluxo (14/10/2026, proprietário: "faça um teste nesses sub menus como se fosse um fluxograma com setas
de linhas curvas, separando em 3 fases/blocos (input, processamento, output, mas sem escrever isso, apenas para o modo de organizar o fluxo).
Assim o usuario entende onde as coisas começam e terminam e a ordem correta do fluxo de processos ao invés de ficar perdido cheio de
submenus soltos"). Confere no navegador (areas/modulos.py, ui37.FLUXO37):
  F1 três blocos (listas ordenadas), na ordem; os cartões de cada bloco na ordem decidida (oráculo escrito aqui, não lido do gerador)
  F2 os 14 cartões do menu Agrícola, uma vez cada; nome acessível = nome curto (ui37.CURTO37); ícone; alvo ≥ 44 px
  F3 sem título de bloco nem texto novo: nenhuma das palavras Entrada/Processamento/Saída/Input/Output/Processing na página (texto e
     rótulos); o texto do fluxo é só o nome dos cartões; sem numeração visível
  F4 setas: SVG decorativo (aria-hidden, sem interceptar toque), 13 caminhos (cartões − 1), Bezier cúbica e curva de fato (desvio da corda);
     cada seta começa junto do cartão i e termina junto do cartão i+1 (≤ 6 px, e é o cartão mais perto); nenhuma passa por cima de cartão
  F5 1440 × 900: três colunas lado a lado, cada bloco num painel (fundo ou borda, cantos arredondados); cartão no hover do design system
  F6 Tab percorre os cartões na ordem do fluxo, com foco visível
  F7 clique (mouse real, por cima do SVG) abre a tela; "‹ Agrícola" volta com o foco no cartão aberto (modVolta)
  F8 1440 → 800: as setas são redesenhadas (pontas nos cartões), três colunas, nenhum nome estoura o cartão
  F9 390 × 844 (toque): uma coluna, blocos empilhados com respiro, sem rolagem lateral; setas descendo e ligando consecutivos; também a
     700 × 900 (coluna estreita), 1024 × 768 (toque) e 844 × 390 (celular deitado: uma coluna)
  F10 MOD-SUP continua em grade (sem fluxo nem setas); sem erro de JS
Capturas (só na _render vigente): _probe/mod_fluxo_1440.png e _probe/mod_fluxo_390.png (página inteira).
Uso: python3 mod_fluxo_test.py (lê _render ou RENDER_DIR). Contraprova: RENDER_DIR=<_render anterior ao fluxo> reprova."""
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
B3 = [('CARGA.dc.html', 'Recebimento'), ('BEN.dc.html', 'Beneficiamento'), ('PROD.dc.html', 'Estoque de produto'), ('GE-03.dc.html', 'Custos'), ('PAGR.dc.html', 'Painel')]
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
    espera("!document.querySelector('.mod-fluxo') || document.querySelectorAll('svg.mod-setas path.mod-seta').length>0", 3)
    time.sleep(.3)
def pagina_inteira(path, w, h, esc, toque):
    if not SHOT: return
    hh = int(J("Math.ceil(document.querySelector('main').getBoundingClientRect().top + document.querySelector('main').scrollHeight + 24)") or h)
    if hh > h: c.aparelho(w, hh, esc, toque); time.sleep(.6)
    c.shot(path); c.aparelho(w, h, esc, toque); time.sleep(.4)

ESTR = """JSON.stringify((()=>{ const f=document.querySelector('.mod-fluxo'); const N=s=>(s||'').replace(/\\s+/g,' ').trim();
  const bl=f?[...f.querySelectorAll(':scope > ol.mod-bloco')]:[];
  const lab=[...document.querySelectorAll('main [aria-label], main [title], main [alt]')].map(e=>[e.getAttribute('aria-label'),e.getAttribute('title'),e.getAttribute('alt')].filter(Boolean).join(' '));
  const cs=[...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length);
  return { fluxo:!!f, blocos:bl.map(o=>[o.tagName, o.getAttribute('role'), [...o.children].map(li=>[li.tagName, li.children.length===1&&li.firstElementChild.matches('a.mod-cartao')?li.firstElementChild.getAttribute('href'):null, N(li.innerText)])]),
    todos:cs.map(a=>a.getAttribute('href')), nomes:cs.map(a=>[a.getAttribute('href'), N(a.innerText), !!a.querySelector('.mod-ic svg path'), Math.round(a.getBoundingClientRect().width), Math.round(a.getBoundingClientRect().height)]),
    texto:N(document.body.innerText), rotulos:lab.join(' | '), txtFluxo:f?N(f.innerText):'',
    marcas:f?[...f.querySelectorAll('li')].map(li=>getComputedStyle(li).display==='list-item'&&getComputedStyle(li).listStyleType!=='none').filter(Boolean).length:-1,
    titulos:f?f.querySelectorAll('h1,h2,h3,h4,h5,h6,legend,caption,figcaption,[role=heading]').length:-1 }; })())"""

GEO = """JSON.stringify((()=>{ const f=document.querySelector('.mod-fluxo'); if(!f) return null; const svg=f.querySelector('svg.mod-setas'); if(!svg) return {svg:false};
  const cs=[...f.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length), rc=cs.map(a=>a.getBoundingClientRect());
  const dist=(p,r)=>Math.hypot(Math.max(r.left-p.x,0,p.x-r.right), Math.max(r.top-p.y,0,p.y-r.bottom));
  const pt=(p,l)=>{ const q=p.getPointAtLength(l); return new DOMPoint(q.x,q.y).matrixTransform(p.getScreenCTM()); };
  const ps=[...svg.querySelectorAll('path.mod-seta')];
  const setas=ps.map((p,i)=>{ const L=p.getTotalLength(), a=pt(p,0), b=pt(p,L), di=rc.map(r=>dist(a,r)), dj=rc.map(r=>dist(b,r)); let dentro=[], desvio=0;
    for(let k=1;k<40;k++){ const q=pt(p,L*k/40); rc.forEach((r,j)=>{ if(q.x>r.left+1&&q.x<r.right-1&&q.y>r.top+1&&q.y<r.bottom-1) dentro.push(j); });
      const vx=b.x-a.x, vy=b.y-a.y, n=Math.hypot(vx,vy)||1; desvio=Math.max(desvio, Math.abs((q.x-a.x)*vy-(q.y-a.y)*vx)/n); }
    const m=pt(p,L/2), el=(m.y>=0&&m.y<innerHeight&&m.x>=0&&m.x<innerWidth)?document.elementFromPoint(m.x,m.y):null;
    return { de:p.getAttribute('data-de'), para:p.getAttribute('data-para'), cub:/^M[^C]*C[^C]*$/.test(p.getAttribute('d')||''), a:[Math.round(a.x),Math.round(a.y)], b:[Math.round(b.x),Math.round(b.y)],
      dIni:di[i]==null?99:+di[i].toFixed(1), dFim:dj[i+1]==null?99:+dj[i+1].toFixed(1), pertoIni:di.indexOf(Math.min(...di))===i, pertoFim:dj.indexOf(Math.min(...dj))===i+1,
      dentro:[...new Set(dentro)], desvio:+desvio.toFixed(1), meio:el?(el.closest('svg')?'svg':'ok'):'fora', desce:b.y>a.y+2, marca:p.getAttribute('marker-end') }; });
  const cv=getComputedStyle(svg), bl=[...f.querySelectorAll(':scope > ol.mod-bloco')].map(o=>{ const r=o.getBoundingClientRect(), s=getComputedStyle(o); return { r:[r.left,r.top,r.right,r.bottom].map(Math.round), fundo:s.backgroundColor, borda:s.borderTopStyle+' '+s.borderTopWidth, raio:parseFloat(s.borderTopLeftRadius) }; });
  const est=cs.map(a=>{ const t=a.lastElementChild; return a.scrollWidth>a.clientWidth+1||(t&&t.scrollWidth>t.clientWidth+1)?a.getAttribute('href'):null; }).filter(Boolean);
  return { svg:true, oculto:svg.getAttribute('aria-hidden'), pe:cv.pointerEvents, n:ps.length, nCartoes:cs.length, ordem:cs.map(a=>a.getAttribute('href')), setas, bl, est,
    ds:ps.map(p=>p.getAttribute('d')).join('|'), sw:document.documentElement.scrollWidth, iw:innerWidth, marcador:!!svg.querySelector('marker path') }; })())"""

def setas_ok(g, desce=None):
    """lista de problemas das setas (vazia = todas ligam o cartão i ao i+1, junto das bordas, curvas, sem cobrir cartão)."""
    if not g or not g.get('svg'): return ['sem fluxo ou sem SVG das setas']
    ruins = []
    if g['n'] != g['nCartoes'] - 1 or g['n'] != len(ORDEM) - 1: ruins.append(['nº de setas', g['n'], g['nCartoes']])
    for i, s in enumerate(g['setas']):
        prob = []
        if [s['de'], s['para']] != ORDEM[i:i + 2]: prob.append('par')
        if not s['cub']: prob.append('não é Bezier cúbica')
        if s['desvio'] < 2: prob.append('reta')
        if s['dIni'] > 6 or not s['pertoIni']: prob.append('início longe do cartão i')
        if s['dFim'] > 6 or not s['pertoFim']: prob.append('fim longe do cartão i+1')
        if s['dentro']: prob.append('passa por cima de cartão')
        if s['meio'] == 'svg': prob.append('o SVG intercepta o ponteiro')
        if not s['marca']: prob.append('sem ponta')
        if desce is not None and s['desce'] != desce: prob.append('direção')
        if prob: ruins.append([i, s['de'], s['para'], prob, s])
    return ruins

try:
    # ---------- 1440 × 900 ----------
    tela('MOD-AGR.dc.html', 1440, 900, limpa=True)
    st = json.loads(J(ESTR) or '{}'); bl = st.get('blocos') or []
    chk('F1 três blocos, cada um uma lista ordenada (ol), na ordem do processo', st.get('fluxo') and [b[0] for b in bl] == ['OL'] * 3, bl)
    chk('F1 cartões de cada bloco na ordem decidida (Agrofit → … → Orçamento · Pragas e doenças → … → Colheita · Recebimento → … → Painel)',
        [[[x[1], x[2]] for x in b[2]] for b in bl] == [[list(x) for x in b] for b in ESP] and all(x[0] == 'LI' for b in bl for x in b[2]), [[x[1:] for x in b[2]] for b in bl])
    chk('F1 a definição do gerador (ui37.FLUXO37) é a mesma ordem', getattr(ui37, 'FLUXO37', {}).get('Agrícola') == [[h for h, _ in b] for b in ESP], getattr(ui37, 'FLUXO37', None))
    todos = st.get('todos') or []
    chk(f'F2 os {len(MENU_AGR)} cartões do menu Agrícola presentes uma vez cada (nenhum a mais)', len(MENU_AGR) == 14 and sorted(todos) == sorted(MENU_AGR) and len(set(todos)) == len(todos), [len(todos), sorted(set(MENU_AGR) ^ set(todos))])
    nm = st.get('nomes') or []
    chk('F2 nome de cada cartão = nome curto do menu (CURTO37), com ícone, alvo ≥ 44 px', nm and all(x[1] == ui37.CURTO37[x[0]][0] and x[2] and x[3] >= 44 and x[4] >= 44 for x in nm), nm)
    pr = sorted(set(m.lower() for m in re.findall(PROIBIDAS, (st.get('texto') or '') + ' ' + (st.get('rotulos') or ''), re.I)))
    chk('F3 nenhuma das palavras Entrada/Processamento/Saída/Input/Output/Processing na página (texto e rótulos)', not pr, pr)
    chk('F3 o fluxo só tem o nome dos cartões: sem título de bloco, legenda nem numeração visível',
        st.get('txtFluxo') == ' '.join(n for b in ESP for _, n in b) and st.get('titulos') == 0 and st.get('marcas') == 0, [st.get('txtFluxo'), st.get('titulos'), st.get('marcas')])
    g = json.loads(J(GEO) or 'null') or {}
    chk('F4 setas num SVG decorativo: aria-hidden="true", pointer-events none, ponta de seta', g.get('svg') and g.get('oculto') == 'true' and g.get('pe') == 'none' and g.get('marcador'), {k: g.get(k) for k in ('svg', 'oculto', 'pe', 'marcador')})
    r4 = setas_ok(g)
    chk('F4 1440: 13 setas curvas (Bezier cúbica), cada uma do cartão i ao i+1 (≤ 6 px das bordas), sem cobrir cartão nem interceptar o ponteiro', not r4, r4[:3])
    lado = [s for s in (g.get('setas') or []) if s['a'][0] < s['b'][0] - 20 and s['b'][1] < s['a'][1] - 100]
    chk('F4 1440: do último cartão de um bloco ao primeiro do seguinte, a seta atravessa entre as colunas (2 em S, de baixo para cima)',
        [[s['de'], s['para']] for s in lado] == [['GE-02.dc.html', 'AG-01.dc.html'], ['COLH.dc.html', 'CARGA.dc.html']], [[s['de'], s['para'], s['a'], s['b']] for s in lado])
    b5 = g.get('bl') or []
    lado_a_lado = len(b5) == 3 and all(abs(b5[i]['r'][1] - b5[0]['r'][1]) <= 2 for i in range(3)) and all(b5[i]['r'][2] < b5[i + 1]['r'][0] for i in range(2)) and all(b['r'][2] - b['r'][0] > 300 for b in b5)
    painel = all(b['raio'] >= 8 and (b['fundo'] not in ('rgba(0, 0, 0, 0)', 'rgb(244, 246, 243)') or not b['borda'].startswith('none')) for b in b5)
    chk('F5 1440: três colunas lado a lado, cada bloco num painel discreto (fundo próprio ou borda, cantos arredondados)', lado_a_lado and painel, b5)
    chk('F5 1440: sem rolagem lateral e nenhum nome estoura o cartão', g.get('sw', 9999) <= g.get('iw', 0) and not g.get('est'), [g.get('sw'), g.get('iw'), g.get('est')])
    # o Chrome de teste não casa (hover:hover) (como em nav_modulos_test N7): as regras da página sob essa condição são copiadas sem ela,
    # como num computador com mouse; o ponteiro real (CDP) passa por cima do SVG das setas até o cartão
    J(r"""(()=>{ const t=[]; [...document.styleSheets].forEach(ss=>{ let rs=[]; try{ rs=[...ss.cssRules]; }catch(e){} rs.forEach(r=>{ if(r.media&&/hover:\s*hover/.test(r.media.mediaText)) [...r.cssRules].forEach(x=>t.push(x.cssText)); }); });
      const st=document.createElement('style'); st.id='simula-hover'; st.textContent=t.join('\n'); document.head.appendChild(st); })()""")
    xy = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.mod-cartao[href=\"OS.dc.html\"]'); const r=a.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})())"))
    c.mouse(*xy); time.sleep(.25)
    hv = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.mod-cartao[href=\"OS.dc.html\"]'); const s=getComputedStyle(a); return [a.matches(':hover'), s.borderTopColor, s.backgroundColor];})())"))
    chk('F5 hover do design system no cartão (borda verde e fundo claro), também por cima do SVG', hv == [True, 'rgb(30, 122, 76)', 'rgb(242, 248, 244)'], hv)
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
    junta('MOD-AGR.dc.html 1440'); J("try{sessionStorage.clear();}catch(e){}"); c.goto(U('MOD-AGR.dc.html'), 1.0); espera("document.querySelectorAll('svg.mod-setas path.mod-seta').length>0", 3)
    xy = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.mod-cartao[href=\"PROD.dc.html\"]'); const r=a.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})())"))
    topo = J(f"(()=>{{const e=document.elementFromPoint({xy[0]},{xy[1]}); return e&&e.closest('a')?e.closest('a').getAttribute('href'):String(e&&e.tagName);}})()")
    junta('MOD-AGR.dc.html')
    c.mouse(*xy, 'mousePressed', 'left'); c.mouse(*xy, 'mouseReleased', 'left')
    abriu = espera("location.pathname.endsWith('/PROD.dc.html') && document.readyState==='complete' && !!document.querySelector('a.volta37')", 6)
    vv = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.volta37'); if(!a) return null; const r=a.getBoundingClientRect(); return [a.getAttribute('href'), a.innerText.replace(/\\s+/g,' ').trim(), r.left+r.width/2, r.top+r.height/2];})())") or 'null')
    junta('PROD.dc.html')
    if vv: c.mouse(vv[2], vv[3], 'mousePressed', 'left'); c.mouse(vv[2], vv[3], 'mouseReleased', 'left')
    voltou = espera("location.pathname.endsWith('/MOD-AGR.dc.html') && document.readyState==='complete' && (document.activeElement&&document.activeElement.getAttribute('href'))==='PROD.dc.html'", 6)
    chk('F7 o clique no cartão (o ponto é dele, não do SVG) abre a tela; "‹ Agrícola" volta com o foco no cartão aberto',
        topo == 'PROD.dc.html' and abriu and vv and vv[:2] == ['MOD-AGR.dc.html', '‹ Agrícola'] and voltou, [topo, abriu, vv and vv[:2], voltou, J("location.pathname"), J("(document.activeElement&&document.activeElement.getAttribute('href'))||''")])
    # ---------- 1440 → 800 ----------
    espera("document.querySelectorAll('svg.mod-setas path.mod-seta').length>0", 3)
    d1440 = (json.loads(J(GEO) or 'null') or {}).get('ds')
    c.aparelho(800, 900, 1, False)
    espera("(()=>{ const s=document.querySelector('svg.mod-setas'); return !!s && s.getAttribute('data-ds')!==" + json.dumps(d1440 or '') + " ; })()", 3); time.sleep(.3)
    g8 = json.loads(J(GEO) or 'null') or {}; r8 = setas_ok(g8); b8 = g8.get('bl') or []
    tres = len(b8) == 3 and all(abs(b8[i]['r'][1] - b8[0]['r'][1]) <= 2 for i in range(3)) and all(b8[i]['r'][2] < b8[i + 1]['r'][0] for i in range(2))
    chk('F8 1440 → 800: setas redesenhadas (caminhos novos), pontas nos cartões, três colunas, nenhum nome estoura o cartão',
        d1440 and g8.get('ds') and g8['ds'] != d1440 and not r8 and tres and not g8.get('est') and g8.get('sw', 9999) <= g8.get('iw', 0), [bool(d1440), r8[:3], tres, g8.get('est'), b8])
    junta('MOD-AGR.dc.html 800')
    # ---------- 390 × 844 (toque) ----------
    tela('MOD-AGR.dc.html', 390, 844, 2, True)
    g9 = json.loads(J(GEO) or 'null') or {}; b9 = g9.get('bl') or []
    uma = len(b9) == 3 and all(abs(b9[i]['r'][0] - b9[0]['r'][0]) <= 1 and abs(b9[i]['r'][2] - b9[0]['r'][2]) <= 1 for i in range(3)) and all(b9[i + 1]['r'][1] - b9[i]['r'][3] >= 12 for i in range(2))
    chk('F9 390: uma coluna, blocos empilhados com respiro (≥ 12 px) e sem rolagem lateral da página', uma and g9.get('sw', 9999) <= g9.get('iw', 0), [b9, g9.get('sw'), g9.get('iw')])
    r9 = setas_ok(g9, desce=True)
    chk('F9 390: 13 setas curvas descendo, do cartão i ao i+1 (inclusive de um bloco ao outro), sem cobrir cartão; nenhum nome estoura', not r9 and not g9.get('est'), [r9[:3], g9.get('est')])
    pagina_inteira(os.path.join(HERE, '_probe', 'mod_fluxo_390.png'), 390, 844, 2, True)
    junta('MOD-AGR.dc.html 390')
    # ---------- larguras intermediárias: coluna estreita (cartão com o ícone sobre o nome), tablet e celular deitado (uma coluna) ----------
    ruins = []
    for w, h, e, t in ((700, 900, 1, False), (1024, 768, 1, True), (844, 390, 2, True)):
        tela('MOD-AGR.dc.html', w, h, e, t); gx = json.loads(J(GEO) or 'null') or {}; bx = gx.get('bl') or []
        cols = len(bx) == 3 and len({b['r'][1] for b in bx}) == (3 if h <= 560 else 1)
        rx = setas_ok(gx)
        if rx or gx.get('est') or gx.get('sw', 9999) > gx.get('iw', 0) or not cols: ruins.append([w, h, rx[:2], gx.get('est'), gx.get('sw'), gx.get('iw'), bx])
        junta(f'MOD-AGR.dc.html {w}x{h}')
    chk('F9 700 × 900, 1024 × 768 (toque) e 844 × 390 (celular deitado: uma coluna): setas ligando consecutivos, sem estourar nome nem rolar de lado', not ruins, ruins[:2])
    # ---------- outro hub ----------
    tela('MOD-SUP.dc.html', 1440, 900)
    sp = json.loads(J("JSON.stringify([!!document.querySelector('.mod-fluxo'), document.querySelectorAll('svg.mod-setas, path.mod-seta').length, !!document.querySelector('.mod-grade[role=list]'), [...document.querySelectorAll('.mod-grade[role=list] a.mod-cartao')].map(a=>a.getAttribute('href'))])"))
    esp_sup = [h for n, ic, its in ui37.MENU2 if n == 'Suprimentos' for l, h in its]
    chk('F10 MOD-SUP continua em grade, na ordem do menu, sem fluxo nem setas', sp == [False, 0, True, esp_sup], [sp, esp_sup])
    junta('MOD-SUP.dc.html')
    chk('F10 sem erro de JS (MOD-AGR a 1440, 800, 390, 700, 1024 e 844 × 390, PROD e MOD-SUP)', not ERRS, ERRS)
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
