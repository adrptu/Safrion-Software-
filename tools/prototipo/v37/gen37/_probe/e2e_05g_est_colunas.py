# -*- coding: utf-8 -*-
"""Passo 5g · EST etapa 3 (Receba devoluções): cabeçalho das colunas e linhas da REQ da OS-0430 com sobra só no Glifosato."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); b.goto('EST.dc.html'); RQ = b.cen("c.ordens['OS-0430'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
hdr = b.J("[...document.querySelectorAll('[role=columnheader]')].filter(h=>h.offsetParent!==null).map(h=>h.innerText.replace(/\\s+/g,' ').replace(/ ⇅.*$/,''))"); print('   colunas:', hdr)
for p in ('Glifosato 480', '2,4-D 806', 'Óleo mineral'):
    cells = b.J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('{RQ}')>=0&&r.innerText.indexOf('{p}')>=0); return r?[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.replace(/\\s+/g,' ')):null;}})()")
    print(f'   {p}:', cells)
print('   OS-0417:', b.rowtxt('OS-0417'))
b.shot('e2e_05g_est_dev_colunas.png')
