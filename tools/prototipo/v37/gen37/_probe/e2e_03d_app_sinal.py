# -*- coding: utf-8 -*-
"""Passo 3d (2ª passada) · MB-01: Com sinal envia uma vez; alternar de novo não duplica."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-01.dc.html'); print('   antes:', b.main()[:120])
b.clk('Com sinal'); t = b.toast(); st = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado, c.ordens['{OS}'].ap.length]"); print('   com sinal:', t, st)
b.clk('Sem sinal'); b.clk('Com sinal'); st2 = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado, c.ordens['{OS}'].ap.length]"); print('   de novo:', b.toast(), st2)
b.ok(st == [0, 60, 1] and st2 == [0, 60, 1] and 'registro enviado' in t, 'MB-01: envio único ao voltar o sinal (60 ha, 1 apontamento)', (t, st, st2))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
