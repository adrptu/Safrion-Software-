# -*- coding: utf-8 -*-
"""v2 · 14b · Restaurar demonstração pela MB-01 (app) e conferir O.S. e Estoque de volta ao início."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); b.goto('MB-01.dc.html')
r = b.clk('Restaurar demonstração'); bt = b.btns(); print('   ', r, '| botões:', bt[-4:])
if 'Restaurar' in bt: b.clk('Restaurar')
elif any(x.startswith('Confirmar') for x in bt): b.clk([x for x in bt if x.startswith('Confirmar')][0])
t = b.toast(); st = b.cen("[c.ordens['OS-0430'].etapa, c.ordens['OS-0430'].aprov, Object.keys(c.reqs).length, c.app.fila.length, c.app.online]"); print('   toast:', t, '| cenário:', st)
b.size(1440, 1000); b.goto('OS.dc.html'); lin = b.rowtxt('OS-0430'); print('   O.S.:', lin)
b.ok(st[:4] == ['A liberar', False, 6, 0] and 'A liberar' in lin, 'restaurar pelo app volta O.S. e cenário ao início', (st, lin))
b.goto('EST.dc.html'); b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[1].click()"); time.sleep(.4)
m = b.main(); print('   EST entrega:', 'OS-0430' in m)
b.ok('OS-0430' not in m, 'Estoque sem requisição da OS-0430 após restaurar', m[:200])
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
