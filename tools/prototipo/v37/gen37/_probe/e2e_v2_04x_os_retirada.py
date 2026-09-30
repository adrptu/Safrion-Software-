# -*- coding: utf-8 -*-
"""v2 · 4x · OS.dc.html com OS-0430 Em execução (tudo entregue e confirmado): o bloco Retirada e fichas ainda manda "Retirar no almoxarifado"?"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS); p = b.aside()
i = p.find('RETIRADA E FICHAS'); print('   bloco:', p[i:i + 700])
st = b.cen(f"c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.prod+' sol '+i.solicitado+' ent '+i.entregue+' conf '+i.confirmado+' cust '+i.custodia)"); print('   cenário:', st)
lk = b.links('aside[role=dialog]'); print('   links:', lk)
b.J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog] a')].find(a=>a.innerText.startsWith('Retirar no almoxarifado')); if(a) a.scrollIntoView({block:'center'});})()"); b.shot('e2e_v2_retirar_pos_entrega.png')
b.ok(not any(l.startswith('Retirar no almoxarifado') for l in lk), 'tudo entregue e confirmado: painel não pede "Retirar no almoxarifado"', lk)
b.fim()
