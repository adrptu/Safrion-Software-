# Sonda: COLH a 390 px, depois da carga: quais data-g2cd existem e se estão visíveis; o que o leitor do PR #117 procura.
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
try:
    c.aparelho(390, 844, 2, True)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(U('COLH.dc.html'), 1.4)
    for t in (0, 2, 5):
        time.sleep(t)
        print(t, J("""JSON.stringify([...document.querySelectorAll('[data-g2cd]')].map(e=>[e.getAttribute('data-g2cd'),e.getClientRects().length,e.tagName,(e.innerText||'').slice(0,40)]))"""))
    print('tabelas visíveis', J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length"))
    print('visão', J("JSON.stringify([...document.querySelectorAll('[aria-pressed=true],[aria-checked=true]')].map(e=>e.innerText.trim()).filter(Boolean).slice(0,10))"))
finally:
    c.close(); srv.terminate()
