# Contraexemplos do PR #127 (só leitura): (a) M3 com a13 Apto; (c) EP-390 na visão Tabela
import os, sys, json, time
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
port, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda p: f'http://127.0.0.1:{port}/{p}'
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
try:
    c.aparelho(1440, 1000); c.goto(U('Main.dc.html'), .3); J("localStorage.clear()")
    c.goto(U('MA.dc.html#ativo=a13'), 1.4)
    b = J(f"{N}(document.body.innerText)") or ''
    cond = J("window.__man.manGet().ativos.a13.cond")
    i = b.find('Bloqueado')
    print('a) a13 cond =', cond, '| "Bloqueado" no corpo:', i >= 0, '|', b[max(0, i - 120):i + 60] if i >= 0 else '')
    for W, H in ((390, 844), (1440, 1000)):
     c.aparelho(W, H)
     for v in ('cartoes', 'tabela'):
        c.goto(U('PROD.dc.html?view=' + v), 1.4)
        m = J("({lado:document.documentElement.scrollWidth>innerWidth+1, cards:[...document.querySelectorAll('[role=list][aria-label=\"Lista em cartões\"] [role=listitem]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>1&&r.height>1}).length, prcard:document.querySelectorAll('.pr-card').length})")
        print('c)', W, 'view=' + v, m, J("(document.querySelector('[data-visao].ativo,[data-visao][aria-pressed=true],[data-visao][aria-current]')||{}).getAttribute?.('data-visao')"))
finally:
    c.close(); srv.terminate()
