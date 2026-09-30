# -*- coding: utf-8 -*-
"""v2 · 3n · App MB-05: voltar o sinal envia o registro uma única vez; alternar de novo não duplica; recibo em MB-03x."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-05.dc.html'); print('   antes:', b.main()[:140])
Q = f"[c.app.fila.length, c.ordens['{OS}'].realizado, c.ordens['{OS}'].ap.length, (c.app.recibos||[]).length]"
s0 = b.cen(Q); b.clk('Com sinal'); t = b.toast(); s1 = b.cen(Q)
b.clk('Sem sinal'); b.clk('Com sinal'); t2 = b.toast(); s2 = b.cen(Q); print('   ', s0, '→', s1, t, '→', s2, t2)
b.ok(s1[:3] == [0, 60, 1] and s2 == s1, 'MB-05: envio único ao voltar o sinal', (s0, s1, s2))
b.goto('MB-03x-recibo.dc.html'); m = b.main(); print('   recibo:', m[:500])
b.ok('OS-0430' in m and '60 ha' in m, 'MB-03x-recibo lista o envio da OS-0430 (60 ha)', m[:300])
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
