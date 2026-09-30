# -*- coding: utf-8 -*-
"""v2 · 7d · IN-04 com Fazenda = Boa Vista: cabeçalho, camadas e painel lateral não mostram dados da Santa Rita; Todas mostra as duas."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 900); FZ = 'select[aria-label="Filtrar por fazenda"]'
b.goto('IN-04.dc.html', wait=1.2)
H = lambda: b.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
print('   SR cabeçalho:', H()[-120:])
b.setv(FZ, 'Boa Vista'); time.sleep(.4); h = H(); m = b.main(); print('   BV cabeçalho:', h[-120:]); print('   BV main:', m[:600])
b.ok('OS-0420' not in h and 'OS-0431' not in h, 'Mapa · Boa Vista: cabeçalho não fala das ordens impedidas da Santa Rita', h[-120:])
for cam in ('Ordens de serviço', 'Irrigação'):
    r = b.clk(cam); m = b.main(); print(f'   BV {cam}:', r, m[:300]); b.ok('OS-04' not in m, f'Mapa · Boa Vista · {cam}: sem ordens da Santa Rita', m[:300])
b.setv(FZ, 'Todas'); time.sleep(.4); n = b.J("document.querySelectorAll('svg [role=button]').length"); print('   Todas polígonos:', n, H()[-100:])
b.setv(FZ, 'Santa Rita'); time.sleep(.3)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
