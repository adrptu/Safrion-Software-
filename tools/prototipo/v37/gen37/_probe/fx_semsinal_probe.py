# -*- coding: utf-8 -*-
"""Sonda (item 1): com o turno de 60 ha no aparelho sem sinal, o que OS, EST e IN-04 mostram."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); print('LIN:', b.rowtxt(OS)); b.row(OS); p = b.aside(); i = p.find('INSUMOS'); print('INS:', p[i:i+800])
b.goto('EST.dc.html'); b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
RQ = b.cen(f"c.ordens['{OS}'].req"); print('EST dev:', b.rowtxt(RQ, 'Glifosato 480')); print('EST k3/main:', b.main()[:900])
b.goto('IN-04.dc.html'); print('IN04:', [x for x in b.main().split('OS-0430')[1:3]])
