# Sonda 2: COLH a 390 e 1440: elementos .g2car visíveis, alternador de visão e o primeiro texto da lista.
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
try:
    for w, m in ((390, True), (1440, False)):
        c.aparelho(w, 844 if m else 900, 2 if m else 1, m)
        c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(U('COLH.dc.html'), 1.4); time.sleep(1.5)
        print(w, 'g2car', J("JSON.stringify([...document.querySelectorAll('.g2car')].map(e=>[e.className,e.getClientRects().length,(e.innerText||'').replace(/\\s+/g,' ').slice(0,50)]))"))
        print(w, 'g2cd*', J("document.querySelectorAll('[data-g2cd]').length"), 'role=table vis', J("[...document.querySelectorAll('[role=table]')].filter(t=>t.offsetParent).length"))
        print(w, 'botões visão', J("JSON.stringify([...document.querySelectorAll('button,[role=radio],[role=tab]')].filter(b=>/Tabela|Cartões|Lista|Grade/.test(b.innerText)).map(b=>[b.innerText.trim(),b.getAttribute('aria-pressed')||b.getAttribute('aria-checked')||b.getAttribute('aria-selected')]))"))
        print(w, 'erro', J("window.__err||''"))
finally:
    c.close(); srv.terminate()
