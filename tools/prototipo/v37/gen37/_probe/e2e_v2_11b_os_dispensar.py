# -*- coding: utf-8 -*-
"""v2 · 11b · OS-0430 com 60/160 ha: Dispensar saldo (motivo) → Em conferência; encerrar bloqueado pela sobra 200/100/50 L."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS)
r = b.clk('Dispensar saldo', 'aside[role=dialog]'); p = b.aside(); print('   dispensar:', r, '|', p[p.find('PRÓXIMO'):][:420]); print('   botões:', b.btns('aside[role=dialog]'))
cs = campos(b); [print('   campo:', f) for f in cs]
bt = [x for x in b.btns('aside[role=dialog]') if x.startswith('Confirmar')]; print('   confirmar:', bt)
r0 = b.clk(bt[0], 'aside[role=dialog]') if bt else 'sem'; al0 = b.alerts('aside[role=dialog]'); print('   confirmar sem motivo:', r0, '|', al0, '|', b.toast(), '|', b.cen(f"c.ordens['{OS}'].etapa"))
b.ok(b.cen(f"c.ordens['{OS}'].etapa") == 'Em execução', 'Dispensar saldo sem motivo não muda a fase', (al0, b.toast()))
tx = [f for f in cs if f['tag'] in ('TEXTAREA', 'INPUT') and f['type'] in ('text', 'textarea')]
if tx:
    sel = '#' + tx[0]['id'] if tx[0]['id'] else 'aside[role=dialog] textarea'
    print('   motivo:', b.setv(sel, 'Chuva prevista; restante do T1-A vai em nova ordem.'))
bt = [x for x in b.btns('aside[role=dialog]') if x.startswith('Confirmar')]
r1 = b.clk(bt[0], 'aside[role=dialog]') if bt else 'sem'; t = b.toast(); p = b.aside(); pp = p[p.find('PRÓXIMO'):][:460]
st = b.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].saldo, c.ordens['{OS}'].realizado]"); print('   confirmar:', r1, '|', t, '| cenário:', st); print('   próximo:', pp)
bb = b.btns('aside[role=dialog]'); print('   botões:', bb, '| links:', b.links('aside[role=dialog]'))
b.ok(st[0] == 'Em conferência' and 'Encerrar bloqueado' in pp and '200 L' in pp and not any(x.startswith('Conferir e encerrar') for x in bb), 'Em conferência após dispensar: encerrar bloqueado pela sobra (200/100/50 L)', (st, pp))
print('   linha:', b.rowtxt(OS))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
