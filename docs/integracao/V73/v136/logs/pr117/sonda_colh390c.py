# Sonda 3: captura da COLH a 390 e o texto visível do corpo (o que a persona vê), para saber onde estão as linhas.
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
try:
    c.aparelho(390, 844, 2, True)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(U('COLH.dc.html'), 1.4); time.sleep(1.5)
    c.shot(OUT)
    print(J("document.body.innerText.replace(/\\n+/g,' | ').slice(0,1500)"))
    print('C1 em algum lugar visível:', J("[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/\\bC1\\b/.test(e.textContent)&&e.getClientRects().length).slice(0,5).map(e=>e.tagName+'.'+e.className+' '+e.closest('[class]').className).join(' ;; ')"))
finally:
    c.close(); srv.terminate()
