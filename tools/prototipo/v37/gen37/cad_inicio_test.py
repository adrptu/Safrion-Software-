# -*- coding: utf-8 -*-
"""Cadastros · tela inicial e "‹ Cadastros" (pedido do proprietário, 13/10/2026: "tire os submenus de cadastro e coloque tudo na tela para o
usuário clicar e cair na tela de cadastro de interesse, com componentes visuais organizados e intuitivos. e botão de voltar fácil para todos
cadastros"). Confere, no navegador, em 1440 × 900 e 390 × 844:
  M1 o menu Cadastros é um link direto para CD.dc.html, sem submenu; dentro de qualquer cadastro o menu continua marcando Cadastros;
  T1 a tela mostra os 8 cadastros em 4 grupos (13/10: Operações e rendimentos saiu de Culturas e cultivares, CD-08), cada cartão só com o nome e as abas (13/10: "elimine esse excesso de texto, somos
     minimalistas e essencialistas"), sem subtítulo nem contador fora da busca, e o link certo; T2 um toque abre o cadastro;
  B1 a busca filtra pelos termos ("trator" → só Máquinas; "embalagem" → só Produtos); sem resultado, diz o que buscar; Esc limpa;
  V1 os 8 cadastros têm "‹ Cadastros" (link para CD.dc.html, alvo ≥ 36 px) e o caminho diz qual é o cadastro; V2 o botão volta;
  R1 (revisão Codex CAD-INICIO-RETORNO-01) buscar "trator", abrir Máquinas e voltar por "‹ Cadastros": volta com o termo, o recorte e o foco no
     cartão aberto; Esc limpa e a próxima volta já vem sem busca;
  A1 (revisão Codex CAD-INICIO-AX-01) cada cartão é link (papel nativo do <a href>) dentro de um item de lista, numa lista;
  C1 sem rolagem lateral no celular e sem erro de JS. Uso: python3 cad_inicio_test.py (lê _render ou RENDER_DIR)."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:600]), flush=True)

CARDS = "JSON.stringify([...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('href'),a.innerText.replace(/\\s+/g,' ').trim()]))"
GRUPOS = "JSON.stringify([...document.querySelectorAll('section.cdi-grupo')].filter(s=>s.getClientRects().length).map(s=>s.getAttribute('aria-label')))"
MENU = "JSON.stringify([...document.querySelectorAll('nav a')].filter(a=>a.getClientRects().length).map(a=>[a.getAttribute('aria-label')||a.innerText.replace(/\\s+/g,' ').trim(),a.getAttribute('href')]))"
import areas.cad_inicio as CI
ESPERADOS = ['CD-01.dc.html', 'CD-02.dc.html', 'CD-08.dc.html', 'CD-03.dc.html', 'CD-04.dc.html', 'CD-05.dc.html', 'CD-06.dc.html', 'CD-07.dc.html']
p, srv = servir(os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
def busca(t):
    J(f"""(()=>{{const i=document.querySelector('input[aria-label="Buscar cadastro"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(t)}); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.4)
try:
    c.aparelho(1440, 900, 1, False); c.goto(U('CD.dc.html'), 1.2); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    mn = json.loads(J(MENU) or '[]')
    chk('M1 menu: "Cadastros" é um link direto para CD.dc.html e nenhum cadastro aparece como submenu', ['Cadastros', 'CD.dc.html'] in mn and not any(h and h.startswith('CD-0') for _, h in mn), mn)
    cs = json.loads(J(CARDS) or '[]'); gs = json.loads(J(GRUPOS) or '[]')
    enx = {c['h']: c['n'] for c in CI.CARTOES}   # o cartão é só ícone + nome curto (13/10: navegação sem submenus; contraprova: o "para que serve" e as abas somem)
    chk('T1 8 cartões em 4 grupos (Propriedade e produção, Recursos, Suprimentos e comercial, Gestão), cada um só com o ícone e o nome curto',
        [h for h, _ in cs] == ESPERADOS and gs == ['Propriedade e produção', 'Recursos', 'Suprimentos e comercial', 'Gestão'] and all(t == enx.get(h) for h, t in cs), [cs, gs])
    sub = J("(()=>{const h=document.querySelector('h1'); const n=h&&h.parentElement&&h.parentElement.nextElementSibling; return n?n.innerText.trim():'';})()") or ''
    cnt = J("(document.querySelector('.cdi [role=status]')||{innerText:''}).innerText.trim()")
    chk('T1 enxuta: sem subtítulo sob o título e sem contador fora da busca', 'Escolha o cadastro' not in (J("document.body.innerText") or '') and cnt == '', [sub[:80], cnt])
    busca('trator'); cs = json.loads(J(CARDS) or '[]')
    chk('B1 busca "trator": só Máquinas, instalações e setores', [h for h, _ in cs] == ['CD-03.dc.html'] and '1 de 8' in (J("document.body.innerText") or ''), cs)
    busca('embalagem'); cs = json.loads(J(CARDS) or '[]')
    chk('B1 busca "embalagem" (sem acento e com acento valem): só Produtos, unidades e locais', [h for h, _ in cs] == ['CD-06.dc.html'], cs)
    busca('xyzw'); cs = json.loads(J(CARDS) or '[]'); b = J("document.body.innerText") or ''
    chk('B1 sem resultado: nenhum cartão e a tela diz "Nenhum cadastro encontrado."', cs == [] and 'Nenhum cadastro encontrado.' in b, [cs, b[-200:]])
    J("(()=>{const i=document.querySelector('input[aria-label=\"Buscar cadastro\"]'); i.focus(); i.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()"); time.sleep(.4)
    chk('B1 Esc limpa a busca e os 8 voltam', len(json.loads(J(CARDS) or '[]')) == 8, J(CARDS))
    J("document.querySelector('a.mod-cartao[href=\"CD-04.dc.html\"]').click()"); time.sleep(1.2)
    chk('T2 um toque no cartão abre o cadastro (Pessoas e equipes)', (J("location.pathname") or '').endswith('/CD-04.dc.html'), J("location.pathname"))
    falhas = []
    for pg in ESPERADOS:
        c.goto(U(pg), 1.0)
        v = json.loads(J("""JSON.stringify((()=>{const a=document.querySelector('a.volta37'); const h1=document.querySelector('h1'); const r=a&&a.getBoundingClientRect();
          const cr=[...document.querySelectorAll('header span, header a')].map(x=>x.innerText).join(' ');
          const nav=[...document.querySelectorAll('nav a')].find(x=>x.getAttribute('aria-label')==='Cadastros');
          return {tem:!!a, href:a&&a.getAttribute('href'), txt:a&&a.innerText.replace(/\\s+/g,' ').trim(), alt:r?Math.round(r.height):0, h1:h1&&h1.innerText, cr, navAtivo:!!nav&&getComputedStyle(nav).backgroundColor!=='rgba(0, 0, 0, 0)'};})())""") or '{}')
        if not (v.get('tem') and v.get('href') == 'CD.dc.html' and v.get('txt') == '‹ Cadastros' and v.get('alt', 0) >= 36 and v.get('h1') and ('Cadastros › ' + v['h1']) in v.get('cr', '') and v.get('navAtivo')):
            falhas.append([pg, v])
    chk('V1 os 8 cadastros têm "‹ Cadastros" (link para a tela inicial, alvo ≥ 36 px), o caminho "Cadastros › <cadastro>" e o menu marcando Cadastros', not falhas, falhas)
    # R1 · volta com a busca e o foco no cartão aberto
    c.goto(U('Main.dc.html'), .3); J("sessionStorage.clear()"); c.goto(U('CD.dc.html'), 1.2); busca('trator')
    J("document.querySelector('a.mod-cartao[href=\"CD-03.dc.html\"]').click()"); time.sleep(1.2); J("document.querySelector('a.volta37').click()"); time.sleep(1.4)
    r1 = json.loads(J("JSON.stringify([document.querySelector('input[aria-label=\"Buscar cadastro\"]').value, (document.activeElement&&document.activeElement.getAttribute('href'))||'', location.pathname])") or '[]')
    cs = json.loads(J(CARDS) or '[]')
    chk('R1 "‹ Cadastros" volta com a busca "trator", só Máquinas e o foco no cartão aberto', r1 and r1[0] == 'trator' and [h for h, _ in cs] == ['CD-03.dc.html'] and r1[1] == 'CD-03.dc.html' and r1[2].endswith('/CD.dc.html'), [r1, cs])
    J("(()=>{const i=document.querySelector('input[aria-label=\"Buscar cadastro\"]'); i.focus(); i.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()"); time.sleep(.4)
    c.goto(U('CD-04.dc.html'), 1.0); J("document.querySelector('a.volta37').click()"); time.sleep(1.2)
    chk('R1 Esc limpa a busca e a volta seguinte já vem com os 8 cadastros', len(json.loads(J(CARDS) or '[]')) == 8 and J("document.querySelector('input[aria-label=\"Buscar cadastro\"]').value") == '', J(CARDS))
    # A1 · semântica: link dentro de item de lista
    ax = json.loads(J("JSON.stringify([...document.querySelectorAll('a.mod-cartao')].map(a=>[a.getAttribute('role'), a.parentElement.getAttribute('role'), !!a.parentElement.closest('[role=list]'), !!a.getAttribute('href')]))") or '[]')
    chk('A1 os 8 cartões são links (sem papel sobrescrito), cada um num item de lista dentro de uma lista', len(ax) == 8 and all(x == [None, 'listitem', True, True] for x in ax), ax)
    c.goto(U('CD-06.dc.html'), 1.0); J("document.querySelector('a.volta37').click()"); time.sleep(1.0)
    chk('V2 "‹ Cadastros" volta para a tela inicial', (J("location.pathname") or '').endswith('/CD.dc.html'), J("location.pathname"))
    c.aparelho(390, 844, 1, True); c.goto(U('CD.dc.html'), 1.2)
    lg = J("document.documentElement.scrollWidth-document.documentElement.clientWidth"); cs = json.loads(J(CARDS) or '[]')
    chk('C1 390 px: os 8 cartões, sem rolagem lateral da página', len(cs) == 8 and (lg or 0) <= 0, [len(cs), lg])
    c.goto(U('CD-03.dc.html'), 1.0)
    chk('C1 390 px: "‹ Cadastros" visível no cadastro', bool(J("(()=>{const a=document.querySelector('a.volta37'); return !!a&&a.getClientRects().length>0;})()")))
    chk('C1 sem erro de JS', not (J("(window.__e||[]).join(' | ')") or ''), J("(window.__e||[]).join(' | ')"))
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
