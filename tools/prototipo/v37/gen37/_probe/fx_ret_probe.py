# -*- coding: utf-8 -*-
"""Sonda (item 2): OS-0430 com os 3 itens entregues e confirmados; bloco Retirada e fichas."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS); p = b.aside()
i = p.find('RETIRADA'); print('RET:', p[i-50:i+500] if i >= 0 else 'sem bloco')
print('LINKS', [l for l in b.links('aside[role=dialog]')])
i = p.find('INSUMOS'); print('INS:', p[i:i+700])
i = p.find('Conjunto'); print('CONJ:', p[i:i+120]); i = p.find('RECURSOS'); print('REC:', p[i:i+250])
