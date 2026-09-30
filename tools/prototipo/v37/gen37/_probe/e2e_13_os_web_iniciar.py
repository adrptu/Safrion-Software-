# -*- coding: utf-8 -*-
"""Passo 13 · OS.dc.html (web): OS-0430 Liberada, nada entregue: "Iniciar execução" e "Registrar apontamento" pela web."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS)
r = b.clk('Iniciar execução', 'aside[role=dialog]'); p = b.aside(); print('   iniciar:', r, '|', p[p.find('PRÓXIMO'):][:400]); print('   botões:', b.btns('aside[role=dialog]'))
for f in campos(b): print('   campo:', f)
cust0 = b.cen(f"c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.entregue+'/'+i.custodia+'/'+(i.confirmado||false)).join(' ')"); print('   antes de confirmar: entregue/custódia/confirmado =', cust0)
r = b.clk('Confirmar início', 'aside[role=dialog]'); t = b.toast(); st = b.cen(f"[c.ordens['{OS}'].etapa]"); print('   confirmar início:', r, '|', t, '|', st)
b.ok(st[0] != 'Em execução' or cust0.count('/0/') < 3, 'web: iniciar execução sem nada entregue nem confirmado deveria ser bloqueado ou avisado', (t, st, cust0))
p = b.aside(); print('   próximo:', p[p.find('PRÓXIMO'):][:300]); print('   botões:', b.btns('aside[role=dialog]'))
r = b.clk('Registrar apontamento', 'aside[role=dialog]'); print('   registrar:', r)
for f in campos(b): print('   campo:', f)
print('   form:', b.aside()[b.aside().find('PRÓXIMO'):][:600])
b.shot('e2e_13_os_web_iniciar.png')
b.fim()
