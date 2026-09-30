# -*- coding: utf-8 -*-
"""Passo 11a (2ª passada, caminho alternativo) · OS-0430 com 60/160 ha: Dispensar saldo → Em conferência; encerrar bloqueado pela sobra."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS)
r = b.clk('Dispensar saldo', 'aside[role=dialog]'); p = b.aside(); print('   dispensar:', r, '|', p[p.find('PRÓXIMO'):][:500]); print('   botões:', b.btns('aside[role=dialog]'))
for f in campos(b): print('   campo:', f)
