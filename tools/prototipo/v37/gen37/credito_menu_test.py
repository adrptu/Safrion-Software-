# -*- coding: utf-8 -*-
"""Crédito com submenus como os demais módulos (proprietário, 14/10/2026: "coloque os submenus de crédito como os demais"), no navegador:
o ícone do Crédito na barra abre a tela de entrada (MOD-CRE) com um cartão por visão da GE-08; cada cartão abre só a sua parte (a ficha não mostra indicadores de contratos); sem visão no endereço a GE-08 mostra tudo (links de outras telas); "‹ Crédito" volta. Dados sintéticos."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:500], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda x: f'http://127.0.0.1:{p}/{x}'
# 16/10/2026 (proprietário: "documentos para credito podemos deixar tudo separado em outro lugar"): 4ª visão, Documentos para crédito
BLOCOS = ['Solicitações e contratos', 'Acompanhamento do CRE-0102', 'Dossiê e consentimento', 'Documentos para crédito']
FICHA = 'Ficha do grupo · Bens e avaliações'
VISOES = [FICHA, BLOCOS[2], BLOCOS[0], BLOCOS[1]]
CARTOES = [['Ficha do grupo', 'GE-08.dc.html#vis=ficha'], ['Dossiês', 'GE-08.dc.html#vis=dossie'], ['Pedidos e contratos', 'GE-08.dc.html#vis=contratos'], ['Liberações e garantias', 'GE-08.dc.html#vis=liberacoes']]
def espera(cond, lim=8.0):
    # espera a condição observável (AGENTS §3.6), com limite explícito: sob carga, 1,2 s fixos não bastavam para a tela renderizar
    t0 = time.time()
    while time.time() - t0 < lim:
        # o clique navega: avaliar durante a troca de página dá "Inspected target navigated or closed" (falha da ferramenta, três vezes em 17/10
        # sob carga). Conta como "ainda não" e espera de novo; o limite e as asserções não mudam
        try:
            if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        except RuntimeError as e:
            if 'navigated or closed' not in str(e): raise
        time.sleep(.15)
    return False
def blocos(): return [b for b in [FICHA] + BLOCOS if J("[...document.querySelectorAll('main h2,main h3')].some(h=>h.offsetParent&&h.innerText.trim()===%s)" % json.dumps(b))]
def kpis(): return J("[...document.querySelectorAll('main')].some(m=>/DÍVIDA ATIVA/i.test(m.innerText))")
try:
    for w, toque in [(1440, False), (390, True)]:
        c.aparelho(w, 900 if w > 400 else 844, 1 if w > 400 else 2, toque)
        c.goto(U('IN-04.dc.html'), 1.2)
        J("(()=>{const a=[...document.querySelectorAll('nav[aria-label=Menu] a')].find(a=>(a.getAttribute('aria-label')||a.title||a.innerText).trim().startsWith('Crédito')); a.click();})()"); espera("location.pathname.endsWith('MOD-CRE.dc.html')&&[...document.querySelectorAll('main a.mod-cartao')].filter(a=>a.offsetParent).length>=3")
        cards = J("[...document.querySelectorAll('main a.mod-cartao')].filter(a=>a.offsetParent).map(a=>[a.innerText.trim(),a.getAttribute('href')])") or []
        chk(f'C1 {w}: o Crédito na barra abre a tela de entrada com um cartão por visão da GE-08',
            J("location.pathname").endswith('MOD-CRE.dc.html') and cards == CARTOES, [J("location.pathname"), cards])
        for i, (nome, href) in enumerate(cards):
            c.goto(U('MOD-CRE.dc.html'), 1.0); espera("[...document.querySelectorAll('main a.mod-cartao')].filter(a=>a.offsetParent).length>%d" % i)
            J("[...document.querySelectorAll('main a.mod-cartao')].filter(a=>a.offsetParent)[%d].click()" % i)
            # espera a parte do cartão e o "‹ Crédito" renderizarem (§3.6); o chk abaixo continua reprovando conteúdo errado
            espera("location.href.indexOf(%s)>=0&&[...document.querySelectorAll('main h2,main h3')].some(h=>h.offsetParent&&h.innerText.trim()===%s)&&[...document.querySelectorAll('a')].some(a=>a.offsetParent&&/Crédito/.test(a.innerText)&&/MOD-CRE/.test(a.getAttribute('href')||''))" % (json.dumps(href.split('#')[1]), json.dumps(VISOES[i])))
            vol = J("[...document.querySelectorAll('a')].some(a=>a.offsetParent&&/Crédito/.test(a.innerText)&&/MOD-CRE/.test(a.getAttribute('href')||''))")
            chk(f'C2 {w} {nome}: só a parte do cartão ({VISOES[i]}), com indicadores pertinentes e "‹ Crédito"', blocos() == [VISOES[i]] and kpis() == (i != 0) and vol, [blocos(), kpis(), vol])
            if i == 0:
                docs = J("[...document.querySelectorAll('main a')].filter(a=>a.offsetParent&&/vis=documentos/.test(a.getAttribute('href')||'')) .map(a=>a.getAttribute('href'))")
                chk(f'C2D {w}: documentos acessíveis pela ficha', bool(docs), docs)
            J("[...document.querySelectorAll('a')].find(a=>a.offsetParent&&/Crédito/.test(a.innerText)&&/MOD-CRE/.test(a.getAttribute('href')||'')).click()")
            espera("location.pathname.endsWith('MOD-CRE.dc.html')&&document.activeElement&&document.activeElement.getAttribute('href')===%s" % json.dumps(href))
            chk(f'C2F {w} {nome}: retorno preserva foco no cartão de origem', J("document.activeElement.getAttribute('href')") == href)
        c.goto(U('GE-08.dc.html#vis=contratos'), 1.2)
        J("location.hash='vis=dossie'"); espera("[...document.querySelectorAll('main h2,main h3')].filter(h=>h.offsetParent).length===1")
        chk(f'C3 {w}: trocar a visão pelo endereço troca a parte sem recarregar', blocos() == [BLOCOS[2]], blocos())
        c.goto(U('GE-08.dc.html'), 1.2)
        chk(f'C4 {w}: GE-08 sem visão no endereço (links de outras telas) mostra as quatro partes', blocos() == BLOCOS, blocos())
        chk(f'C5 {w}: sem rolagem lateral e sem erro de JS', J("document.documentElement.scrollWidth<=innerWidth") and not J("(window.__e||[]).length"), [J("[document.documentElement.scrollWidth,innerWidth]"), J("window.__e")])
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
