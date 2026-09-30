# -*- coding: utf-8 -*-
"""Item 1 · depois do sinal: área e consumo mudam juntos em O.S., Estoque e Mapa (60/160 ha · 120/60/30 L consumidos · 200/100/50 L em custódia)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); lin = b.rowtxt(OS); b.row(OS); p = b.aside(); ins = p[p.upper().find('INSUMOS E DOSES'):][:900]
b.ok('60 / 160 ha' in lin and 'Consumido 120 L' in ins and 'Em custódia 200 L' in ins and 'aguardando sinal' not in ins, 'OS: 60 / 160 ha e 120 L consumidos, 200 L em custódia', (lin, ins[:300]))
b.goto('EST.dc.html'); RQ = b.cen(f"c.ordens['{OS}'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
g = b.rowtxt(RQ, 'Glifosato 480'); print('   EST:', g)
b.ok('320 L 120 L 0 L 200 L' in g and 'Em uso na O.S.' in g, 'EST: consumido 120 L e custódia 200 L', g)
b.goto('IN-04.dc.html', wait=1.2); b.clk('Ordens de serviço')
SV = "[...document.querySelectorAll('svg [role=button]')]"
b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
p = (b.J("(document.querySelector('aside[aria-label^=\"T1\"]')||{innerText:''}).innerText") or '').replace('\n', ' / ')
i = p.find(OS + ' · Dessecação'); o = p[i:i + 240]; print('   Mapa:', o)
b.ok('60/160 ha' in o and '200 L + 100 L + 50 L em custódia' in o and 'aguardando sinal' not in o, 'Mapa: 60/160 ha e 200 + 100 + 50 L em custódia', o)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
