# -*- coding: utf-8 -*-
"""Passo 5b · OS.dc.html: saldo zero → Enviar para conferência; encerrar bloqueado pela sobra de 20 L com atalho ao Estoque."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html')
lin = b.rowtxt(OS); print('   linha:', lin)
b.ok('160 / 160 ha' in lin, 'lista: 160 / 160 ha', lin)
b.row(OS); p = b.aside(); print('   próximo:', p[p.find('PRÓXIMO'):][:350]); bt = b.btns('aside[role=dialog]'); print('   botões:', bt)
b.ok('Enviar para conferência' in bt, 'saldo 0: botão Enviar para conferência', bt)
r = b.clk('Enviar para conferência', 'aside[role=dialog]'); print('   ', r, b.btns('aside[role=dialog]'))
r = b.clk('Confirmar envio', 'aside[role=dialog]'); t = b.toast(); print('   confirmar envio:', r, '|', t)
p = b.aside(); pp = p[p.find('PRÓXIMO'):][:450]; print('   próximo:', pp); bt = b.btns('aside[role=dialog]'); lk = b.links('aside[role=dialog]'); print('   botões:', bt, '| links:', lk)
b.ok('Em conferência' in b.rowtxt(OS) and 'Encerrar bloqueado' in pp and 'Glifosato 480 20 L' in pp and not any(x.startswith('Conferir e encerrar') for x in bt),
     'Em conferência: encerrar bloqueado pela sobra de 20 L de Glifosato', pp)
b.ok(any(l.startswith('Receber devolução no Estoque') and l.endswith('EST.dc.html') for l in lk), 'atalho "Receber devolução no Estoque" → EST.dc.html', lk)
print('   linha em conferência:', b.rowtxt(OS)); print('   OS-0417 (semente):', b.rowtxt('OS-0417'))
b.shot('e2e_05b_os_conf_bloq.png')
er = b.erros(); b.ok(not er, 'sem erro de JS na O.S.', er)
b.fim()
