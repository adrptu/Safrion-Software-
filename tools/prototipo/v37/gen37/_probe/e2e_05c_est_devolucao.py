# -*- coding: utf-8 -*-
"""Passo 5c · EST.dc.html: receber a devolução da sobra de Glifosato (20 L) da OS-0430, conferida e apta."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('EST.dc.html')
RQ = b.cen(f"c.ordens['{OS}'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
g = b.rowtxt(RQ, 'Glifosato 480'); d = b.rowtxt(RQ, '2,4-D 806'); print('   Glifosato:', g); print('   2,4-D:', d)
b.ok('20 L' in g and g != 'sem linha', f'{RQ}: Glifosato com 20 L em custódia aparece para devolução', g)
r = b.row(RQ, 'Glifosato 480'); a = b.aside(); print('   form:', a[:500]); print('   padrão:', b.val('#fx_g_dev_qtd'), b.val('#fx_g_dev_cond'))
b.ok(b.val('#fx_g_dev_qtd') == '20', 'formulário de devolução já vem com os 20 L em custódia', b.val('#fx_g_dev_qtd'))
s = b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); print('   salvar:', s, '|', t, '| erro:', b.alerts('aside[role=dialog]'))
st = b.cen(f"[c.reqs['{RQ}'].itens[0].custodia, c.reqs['{RQ}'].itens[0].devolvido, c.lotes['Glifosato 480|G26-14'].fisico, c.lotes['Glifosato 480|G26-14'].quarentena, window.__cen.cenPodeEncerrar(c,'{OS}')]"); print('   cenário:', st)
b.ok(st[0] == 0 and st[1] == 20 and st[2] == 900 and st[3] == 0 and st[4] == '', 'devolução apta: custódia 0, devolvido 20 L, G26-14 volta a 900 L; nada bloqueia o encerramento', st)
print('   linha depois:', b.rowtxt(RQ, 'Glifosato 480'))
b.shot('e2e_05c_est_dev.png')
er = b.erros(); b.ok(not er, 'sem erro de JS no Estoque', er)
b.fim()
