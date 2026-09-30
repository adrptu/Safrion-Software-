# -*- coding: utf-8 -*-
"""Passo 5f (2ª passada) · OS.dc.html: sem sobra, Enviar para conferência e encerrar direto; Mapa acompanha."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS)
b.clk('Enviar para conferência', 'aside[role=dialog]'); b.clk('Confirmar envio', 'aside[role=dialog]'); lin = b.rowtxt(OS); p = b.aside()
print('   linha:', lin); print('   próximo:', p[p.find('PRÓXIMO'):][:260]); bt = b.btns('aside[role=dialog]'); print('   botões:', bt)
b.ok('Em conferência' in lin and 'Conferir e encerrar' in bt and 'Encerrar bloqueado' not in p, 'sem sobra: Em conferência com Conferir e encerrar liberado', (lin, bt))
b.clk('Conferir e encerrar', 'aside[role=dialog]'); b.clk('Confirmar encerramento', 'aside[role=dialog]'); t = b.toast(); st = b.cen(f"c.ordens['{OS}'].etapa"); print('   ', t, st)
b.ok(st == 'Encerradas' and 'encerrada' in t, 'OS-0430 encerrada sem devolução', (t, st))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
