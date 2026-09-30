# -*- coding: utf-8 -*-
"""v2 · 3x · OS.dc.html depois do recebimento confirmado no app (antes do turno): próximo passo e ações da OS-0430."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); print('   linha:', b.rowtxt(OS)); b.row(OS); p = b.aside()
pp = p[p.find('PRÓXIMO'):][:420]; print('   próximo:', pp); print('   botões:', b.btns('aside[role=dialog]')); print('   links:', b.links('aside[role=dialog]'))
i = p.find('RETIRADA E FICHAS'); print('   retirada:', p[i:i + 300] if i >= 0 else '(sem bloco)')
b.ok('bloqueado' not in pp.lower(), 'recebimento confirmado: iniciar não está bloqueado', pp)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
