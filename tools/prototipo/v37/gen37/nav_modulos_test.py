# -*- coding: utf-8 -*-
"""Navegação sem submenus (13/10/2026, proprietário: "tire todos submenus de todos os módulos e coloque na tela como fizemos com cadastros e
deixe a barra lateral dos menus somente recolhido com os ícones e tooltip sem opção de expandir ... reduza texto ao mínimo essencial ...
sempre com opção de voltar rápido e fácil. use sempre ícones mais intuitivos"; "elimine essa tela e já caia direto no sistema"; "tire esse
retângulo estranho de todos campos de busca"). Confere no navegador:
  N1 barra lateral: um ícone por módulo (+ Outros acessos), sem submenu, sem botão de expandir, recolhida (≤ 72 px), sem texto visível;
     cada ícone com nome acessível e dica com o nome (hover); o módulo da tela aberta marcado (aria-current)
  N2 cada módulo com mais de uma tela abre a tela de entrada: cartões só com ícone e nome curto (ui37.CURTO37), na ordem do menu
     (o módulo com fluxo, ui37.FLUXO37, na ordem do fluxo: 14/10/2026, mod_fluxo_test.py);
     o Mapa abre direto; a Manutenção (uma tela com visões) tem um cartão por visão (13/10, proprietário: "o menu de manutenção está
     sem os submenus na tela igual os demais"); o caminho não repete o título
  N3 cada cartão abre a tela; cada tela do módulo tem "‹ Módulo" (alvo ≥ 36 px) que volta à tela de entrada
  N4 Outros acessos: app de campo, portal, onboarding e backoffice
  N5 o índice saiu: nenhuma tela aponta para Main.dc.html; o logotipo leva ao Mapa
  N6 perfil: o avatar troca o perfil de demonstração (o seletor continua acessível) e a dica diz o perfil
  N7 busca em pílula: o campo de dentro não desenha caixa no hover nem no foco; o contorno arredondado dá o retorno
  N8 O.S.: tabela larga na largura natural (rola de lado) e os selos de Fase numa linha só (sem quebrar letra a letra)
  N9 390 px: barra e tela de entrada sem rolagem lateral; sem erro de JS
Uso: python3 nav_modulos_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
import ui37

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:700]), flush=True)

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
NAV = """JSON.stringify((()=>{ const n=document.querySelector('nav[aria-label=Menu]'); const as=[...n.querySelectorAll('a')].filter(a=>a.getClientRects().length);
  const vis=a=>{ let t=''; const w=document.createTreeWalker(a,NodeFilter.SHOW_TEXT); while(w.nextNode()){ const x=w.currentNode; const r=x.parentElement.getBoundingClientRect(); if(x.textContent.trim()&&r.width>2&&r.height>2) t+=x.textContent.trim(); } return t; };
  return {w:Math.round(n.getBoundingClientRect().width), sub:n.querySelectorAll('.ml-sub,[aria-expanded]').length, tog:[...document.querySelectorAll('.ml-tog')].filter(x=>x.getClientRects().length).length,
    itens:as.map(a=>({h:a.getAttribute('href'),al:a.getAttribute('aria-label'),t:a.getAttribute('title'),cur:a.getAttribute('aria-current'),vis:vis(a)}))}; })())"""
CARDS = "JSON.stringify([...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim(),!!a.querySelector('svg path')]))"
def espera(js, ate=4.0):
    t0 = time.time()
    while time.time() - t0 < ate:
        if J(js): return True
        time.sleep(.1)
    return False
try:
    c.aparelho(1440, 900, 1, False); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(U('OS.dc.html'), 1.4); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    nv = json.loads(J(NAV) or '{}'); its = nv.get('itens', [])
    esp = [ui37.INICIO37] + [ui37.HUB37.get(n) or items[0][1].split('#')[0] for n, ic, items in ui37.MENU2] + [ui37.OUTROS37[2]]
    nomes = ['Início (Mapa)'] + [n for n, ic, items in ui37.MENU2] + [ui37.OUTROS37[0]]
    chk('N1 barra: logotipo + um ícone por módulo + Outros acessos, sem submenu nem expandir, ≤ 72 px, sem texto visível, nome acessível e dica',
        [x['h'] for x in its] == esp and [x['al'] for x in its] == nomes and all(x['t'] == x['al'] and x['vis'] == '' for x in its)
        and nv.get('sub') == 0 and nv.get('tog') == 0 and nv.get('w', 999) <= 72, nv)
    chk('N1 O.S. aberta: o ícone Agrícola marcado (aria-current) e só ele', [x['al'] for x in its if x['cur'] == 'page'] == ['Agrícola'], [(x['al'], x['cur']) for x in its])
    xy = json.loads(J("JSON.stringify((()=>{const a=[...document.querySelectorAll('nav[aria-label=Menu] a')].find(a=>a.getAttribute('aria-label')==='Suprimentos'); const r=a.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})())"))
    c.mouse(*xy); espera("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden&&d.innerText.trim()==='Suprimentos';})()")
    chk('N1 hover no ícone Suprimentos: a dica mostra "Suprimentos"', J("(()=>{const d=document.getElementById('g2-dica'); return !!d&&!d.hidden&&d.innerText.trim()==='Suprimentos';})()"), J("(document.getElementById('g2-dica')||{}).innerText"))
    c.mouse(900, 880); time.sleep(.3)
    # N2/N3 telas de entrada, cartões e volta
    ruins, voltas = [], []
    for nome, ic, items in ui37.MENU2:
        hub = ui37.HUB37.get(nome)
        if not hub: continue
        c.goto(U(hub), 1.0); cs = json.loads(J(CARDS) or '[]')
        es = []; vistos = set()
        for l, h in items:
            k = h if h in ui37.CURTO37 else h.split('#')[0]   # visão com nome próprio (Manutenção: MA.dc.html#vis=…) tem o seu cartão
            if k in vistos: continue
            vistos.add(k); es.append([h, ui37.CURTO37[k][0], True])
        if nome in ui37.FLUXO37:   # 14/10/2026 (proprietário: fluxograma nos submenus): a ordem dos cartões é a do processo (blocos de FLUXO37)
            pos = {h: i for i, h in enumerate(h for b in ui37.FLUXO37[nome] for h in b)}; es.sort(key=lambda x: pos[x[0]])
        cr = J("(document.querySelector('header span')||{innerText:''}).innerText.trim()") or ''
        if cs != es or J("document.querySelector('h1').innerText") != nome or cr == nome: ruins.append([nome, cs, es, cr])
        for h, curto, _ in es:
            c.goto(U(h), 1.0)
            v = json.loads(J("JSON.stringify((()=>{const a=document.querySelector('a.volta37'); const r=a&&a.getBoundingClientRect(); return a?[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim(),Math.round(r.height)]:null;})())") or 'null')
            if not v or v[0] != hub or v[1] != '‹ ' + nome or v[2] < 36: voltas.append([h, v])
    chk(f'N2 {len(ui37.HUB37)} telas de entrada ({", ".join(ui37.HUB37)}): cartões só com ícone e nome curto, na ordem do menu (Agrícola: do fluxo); caminho sem repetir o título', not ruins, ruins[:2])
    chk('N3 cada tela dos módulos tem "‹ Módulo" (≥ 36 px) para a tela de entrada', not voltas, voltas[:4])
    c.goto(U('MOD-AGR.dc.html'), 1.0); J("[...document.querySelectorAll('a.mod-cartao')].find(a=>a.innerText.trim()==='Ordens de serviço').click()"); time.sleep(1.2)
    p1 = J("location.pathname"); J("document.querySelector('a.volta37').click()"); time.sleep(1.0); p2 = J("location.pathname")
    fo = J("(document.activeElement&&document.activeElement.getAttribute('href'))||''")
    chk('N3 um toque no cartão abre a tela e "‹ Agrícola" volta, com o foco no cartão aberto (ponto útil da volta)', (p1 or '').endswith('/OS.dc.html') and (p2 or '').endswith('/MOD-AGR.dc.html') and fo == 'OS.dc.html', [p1, p2, fo])
    # item de lista: role="listitem" na grade ou <li> nativo da lista ordenada do fluxo (14/10/2026: <ol role="list"> por bloco, sem role redundante no <li>)
    ax = json.loads(J("JSON.stringify([...document.querySelectorAll('a.mod-cartao')].map(a=>{ const it=a.parentElement; return [a.getAttribute('role'), it.getAttribute('role')||(it.tagName==='LI'&&it.parentElement.matches('ol,ul')?'listitem':null), !!it.closest('[role=list],ol,ul')]; }))") or '[]')
    chk('N3 cartões das telas de entrada: link nativo dentro de item de lista', ax and all(x == [None, 'listitem', True] for x in ax), ax)
    dir_ = {}
    for nome, ic, items in ui37.MENU2:
        if nome in ('Mapa', 'Manutenção'):
            c.goto(U('OS.dc.html'), 1.0); J(f"[...document.querySelectorAll('nav[aria-label=Menu] a')].find(a=>a.getAttribute('aria-label')=={json.dumps(nome)}).click()"); time.sleep(1.2); dir_[nome] = J("location.pathname")
    cman = json.loads(J(CARDS) or '[]')
    chk('N2 o Mapa abre direto; a Manutenção abre a sua tela de entrada com um cartão por visão (Painel · Sem ordem · Ordens · Ativos · Planos)',
        (dir_.get('Mapa') or '').endswith('/IN-04.dc.html') and (dir_.get('Manutenção') or '').endswith('/MOD-MAN.dc.html')
        and [x[:2] for x in cman] == [['PMAN.dc.html', 'Painel'], ['MA.dc.html#vis=semordem', 'Sem ordem'], ['MA.dc.html#vis=ordens', 'Ordens'], ['MA.dc.html#vis=ativos', 'Ativos'], ['MA.dc.html#vis=planos', 'Planos']], [dir_, cman])
    c.goto(U(ui37.OUTROS37[2]), 1.0); cs = json.loads(J(CARDS) or '[]')
    chk('N4 Outros acessos: app de campo, portal do parceiro, onboarding e backoffice', [x[0] for x in cs] == [h for n, h, i in ui37.OUTROS37[3]] and all(x[2] for x in cs), cs)
    # N5 índice fora
    apont = sorted(os.path.basename(f) for f in glob.glob(os.path.join(R, '*.dc.html')) if os.path.basename(f) != 'Main.dc.html' and 'href="Main.dc.html' in open(f, encoding='utf-8', errors='ignore').read())
    c.goto(U('CD.dc.html'), 1.0); lg = J("(document.querySelector('.ml-topo a')||{getAttribute:()=>''}).getAttribute('href')")
    chk('N5 nenhuma tela aponta para o índice (Main.dc.html); o logotipo leva ao Mapa', not apont and lg == ui37.INICIO37, [apont[:5], lg])
    # N6 perfil no avatar
    c.goto(U('OS.dc.html'), 1.0)
    J("(()=>{const s=document.querySelector('select[aria-label=\"Trocar perfil de demonstração\"]'); s.value='Rui'; s.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.6)
    pf = json.loads(J("JSON.stringify((()=>{const s=document.querySelector('select[aria-label=\"Trocar perfil de demonstração\"]'); const l=s.closest('label'); const r=s.getBoundingClientRect(); return [localStorage.getItem('safrion.perfilDemo'), l.getAttribute('title'), Math.round(r.width), Math.round(r.height), l.innerText.trim()];})())") or '[]')
    chk('N6 o avatar troca o perfil (seletor por cima do avatar, ≥ 32 px) e a dica diz o perfil', pf and pf[0] == 'Rui' and 'Rui' in (pf[1] or '') and pf[2] >= 32 and pf[3] >= 32 and pf[4].startswith('R'), pf)
    J("localStorage.removeItem('safrion.perfilDemo')")
    # N7 busca em pílula
    c.goto(U('OS.dc.html'), 1.0)
    # o Chrome de teste não tem ponteiro com hover (matchMedia('(hover:hover)') falso): as regras de @media (hover:hover) da página são copiadas
    # para uma folha sem a condição, como num computador com mouse (contraprova: na montagem anterior o campo de dentro ganha a caixa)
    J(r"""(()=>{ const t=[]; [...document.styleSheets].forEach(ss=>{ let rs=[]; try{ rs=[...ss.cssRules]; }catch(e){} rs.forEach(r=>{ if(r.media&&/hover:\s*hover/.test(r.media.mediaText)) [...r.cssRules].forEach(x=>t.push(x.cssText)); }); });
      const st=document.createElement('style'); st.id='simula-hover'; st.textContent=t.join('\n'); document.head.appendChild(st); })()""")
    bx = json.loads(J("JSON.stringify((()=>{const i=[...document.querySelectorAll('label>input[type=search]')].find(i=>i.getClientRects().length); const r=i.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2];})())"))
    c.mouse(*bx); time.sleep(.3)
    hv = json.loads(J("JSON.stringify((()=>{const i=[...document.querySelectorAll('label>input[type=search]')].find(i=>i.getClientRects().length); return [getComputedStyle(i).boxShadow, getComputedStyle(i.parentElement).boxShadow];})())"))
    J("(()=>{const i=[...document.querySelectorAll('label>input[type=search]')].find(i=>i.getClientRects().length); i.focus();})()"); c.tecla('a', 'KeyA', 65, text='a'); time.sleep(.2)
    fc = json.loads(J("JSON.stringify((()=>{const i=document.activeElement; const s=getComputedStyle(i), l=getComputedStyle(i.parentElement); return [i.type, s.outlineStyle, s.boxShadow, l.outlineStyle];})())"))
    chk('N7 busca em pílula: sem caixa no campo de dentro (hover e foco); o contorno da pílula dá o retorno',
        hv[0] == 'none' and hv[1] != 'none' and fc[0] == 'search' and fc[1] == 'none' and fc[2] == 'none' and fc[3] == 'solid', [hv, fc])
    # N8 O.S. sem selo quebrado
    c.goto(U('OS.dc.html'), 1.2)
    t8 = json.loads(J("""JSON.stringify((()=>{ const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const fx=t.parentElement;
      const ch=[...t.querySelectorAll('[role=cell]')].filter(c=>/^(Encerradas|Em execução|Liberadas|A liberar|Em conferência)$/.test(c.innerText.trim())).map(c=>{ const s=[...c.querySelectorAll('span')].pop(); return s?s.getClientRects().length:0; });
      return [Math.round(t.getBoundingClientRect().width), fx.clientWidth, ch]; })())"""))
    chk('N8 O.S.: tabela na largura natural (rola de lado) e cada selo de Fase em uma linha', t8[0] > t8[1] and t8[2] and max(t8[2]) == 1, t8)
    # N9 celular
    c.aparelho(390, 844, 2, True)
    lgs = {}
    for pg in ('MOD-AGR.dc.html', 'CD.dc.html', 'OS.dc.html'):
        c.goto(U(pg), 1.2); lgs[pg] = J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    chk('N9 390 px: sem rolagem lateral da página (telas de entrada e O.S.)', all((v or 0) <= 0 for v in lgs.values()), lgs)
    chk('N9 sem erro de JS', not (J("(window.__e||[]).join(' | ')") or ''), J("(window.__e||[]).join(' | ')"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
