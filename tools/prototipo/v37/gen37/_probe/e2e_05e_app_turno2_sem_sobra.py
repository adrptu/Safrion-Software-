# -*- coding: utf-8 -*-
"""Passo 5e (2ª passada) · MB-03: turno de 100 ha com o consumo pela dose (sem sobra) e Estoque sem nada a devolver."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-03.dc.html')
b.clk_sel(f'button[title="Iniciar turno na {OS}"]'); b.setv('#ft_ha', '100'); b.setv('#ft_h', '8'); b.clk('Fechar turno'); t = b.toast()
st = b.cen(f"[c.ordens['{OS}'].realizado, c.ordens['{OS}'].saldo, c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.custodia).join('/'), window.__cen.cenPodeEncerrar(c,'{OS}')]"); print('   ', t, st)
b.ok(st[:3] == [160, 0, '0/0/0'] and st[3] == '', 'turno 2 de 100 ha pela dose: 160/160 ha, custódia 0/0/0, nada bloqueia o encerramento', st)
b.goto('MB-05.dc.html'); m = b.main(); print('   MB-05:', m[:400])
b.ok('OS-0430' not in m, 'MB-05: nada da OS-0430 com o operador', m[:300])
b.size(1440, 1000); b.goto('EST.dc.html'); RQ = b.cen(f"c.ordens['{OS}'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
g = b.rowtxt(RQ, 'Glifosato 480'); print('   EST devoluções:', g)
b.ok('Receber devolução' not in g, 'Estoque: REQ da OS-0430 sem devolução a receber', g)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
