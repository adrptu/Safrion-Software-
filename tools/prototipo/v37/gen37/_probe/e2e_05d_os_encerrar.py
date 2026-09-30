# -*- coding: utf-8 -*-
"""Passo 5d · OS.dc.html: após a devolução, encerrar é permitido (apontamentos sincronizados e nada em custódia)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html')
b.row(OS); p = b.aside(); pp = p[p.find('PRÓXIMO'):][:350]; bt = b.btns('aside[role=dialog]'); print('   próximo:', pp, '| botões:', bt)
i = p[p.find('INSUMOS'):p.find('RETIRADA')]; print('   insumos:', i[:700])
b.ok('Encerrar bloqueado' not in pp and 'Conferir e encerrar' in bt, 'sem bloqueio: botão Conferir e encerrar', (pp, bt))
b.ok('Devolvido 20 L' in i, 'trilha do Glifosato mostra Devolvido 20 L', i[:400])
r = b.clk('Conferir e encerrar', 'aside[role=dialog]'); print('   ', r, b.btns('aside[role=dialog]'))
r = b.clk('Confirmar encerramento', 'aside[role=dialog]'); t = b.toast(); print('   encerrar:', r, '|', t)
st = b.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].ap.map(a=>a.st).join(',')]"); print('   cenário:', st)
b.ok(st == ['Encerradas', 'Conferido,Conferido'] and 'Encerradas' in b.rowtxt(OS) and 'somente consulta' in b.aside(), 'OS-0430 encerrada: apontamentos conferidos, painel somente consulta', (st, t))
b.shot('e2e_05d_os_encerrada.png')
er = b.erros(); b.ok(not er, 'sem erro de JS na O.S.', er)
b.fim()
