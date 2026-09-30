# -*- coding: utf-8 -*-
"""v2 · 4w · OS.dc.html e EST com 60 ha ainda no aparelho (sem sinal): insumos consumidos/custódia já mudaram antes do envio?"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
st = None
b.goto('OS.dc.html'); lin = b.rowtxt(OS); b.row(OS); p = b.aside()
i = p[p.find('INSUMOS'):p.find('RETIRADA')]; print('   linha:', lin); print('   insumos:', i[:620])
st = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado, c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.consumido+'/'+i.custodia).join(' ')]"); print('   cenário:', st)
b.J("(()=>{const a=document.querySelector('aside[role=dialog]'); const h=[...a.querySelectorAll('*')].find(e=>e.innerText&&e.innerText.trim().toUpperCase()==='INSUMOS E DOSES'); if(h) h.scrollIntoView({block:'start'});})()"); b.shot('e2e_v2_consumo_sem_sinal.png')
b.ok(not ('Consumido 120 L' in i and '0 / 160 ha' in lin), 'O.S. web não mostra consumo de 120 L com 0 ha realizados (registro ainda no aparelho)', (lin, i[:300]))
b.goto('EST.dc.html'); RQ = b.cen(f"c.ordens['{OS}'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
g = b.rowtxt(RQ, 'Glifosato 480'); print('   EST devoluções Glifosato:', g)
b.fim()
