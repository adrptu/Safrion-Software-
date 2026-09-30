# -*- coding: utf-8 -*-
"""v2 · 12d · Kanban da O.S.: texto visível depois de clicar em Kanban, para achar a coluna da OS-0430."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); b.goto('OS.dc.html'); print('   clk:', b.clk('Kanban'))
m = b.J("(document.querySelector('main')||document.body).innerText") or ''
i = m.find('Kanban'); print(m[i:i + 2600])
b.clk('Lista'); b.fim()
