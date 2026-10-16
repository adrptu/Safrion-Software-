# -*- coding: utf-8 -*-
"""EX-41 · botões do cabeçalho da página (y < 100 px, fora do menu lateral) em 6 telas a 1440: primária (verde), secundárias (estilo) e ⋯.
Saída: out/p6_ex41_cabecalho.json. Só leitura."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import chrome, server, dump, log, OUT, G
L = open(os.path.join(OUT, 'p6_ex41_cabecalho.log'), 'w', encoding='utf-8'); R = {}
port = server(os.path.join(G, '_render')); c = chrome(); J = c.js; c.aparelho(1440, 900)
for pg in ['OS.dc.html', 'CD-04.dc.html', 'EST.dc.html', 'SAF.dc.html', 'AG-01.dc.html', 'VEN.dc.html', 'PA.dc.html', 'CA-01det.dc.html']:
    c.goto(f'http://127.0.0.1:{port}/Main.dc.html', .2); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(f'http://127.0.0.1:{port}/{pg}', 1.0)
    R[pg] = json.loads(J(r"""JSON.stringify([...document.querySelectorAll('button,a')].filter(b=>{const r=b.getBoundingClientRect(); return r.width>1&&r.height>1&&r.top<100&&r.left>80;}).map(b=>{const cs=getComputedStyle(b);
      return {t:(b.innerText||b.getAttribute('aria-label')||'').replace(/\s+/g,' ').trim().slice(0,40),bg:cs.backgroundColor,borda:cs.borderTopColor,cor:cs.color,h:Math.round(b.getBoundingClientRect().height)};}))"""))
    log(L, pg, json.dumps(R[pg], ensure_ascii=False))
dump('p6_ex41_cabecalho.json', R); log(L, 'FIM')
