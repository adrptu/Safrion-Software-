# -*- coding: utf-8 -*-
"""Passo 4 · OS.dc.html: OS-0430 Em execução com 60 ha vindos do app, insumos consumidos; encerrar bloqueado (saldo/sobra)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html')
lin = b.rowtxt(OS); print('   linha:', lin)
b.ok('Em execução' in lin and '60 / 160 ha' in lin and 'saldo 100 ha' in lin, 'lista: OS-0430 Em execução, 60 / 160 ha, saldo 100 ha', lin)
b.row(OS); p = b.aside()
i = p[p.find('INSUMOS'):p.find('APONTAMENTOS')]; a = p[p.find('APONTAMENTOS'):][:600]
print('   próximo passo:', p[p.find('PRÓXIMO'):][:400]); print('   insumos:', i[:900]); print('   apontamentos:', a)
print('   botões:', b.btns('aside[role=dialog]')); print('   links:', b.links('aside[role=dialog]'))
b.ok('Consumido 120 L' in i and 'Em custódia 200 L' in i and 'Confirmado no app' in i, 'insumos: Glifosato consumido 120 L, em custódia 200 L, confirmado no app', i[:500])
b.ok('Dia 1' in a and 'app' in a and '60' in a, 'apontamento do app (dia 1, 60 ha) aparece no painel', a)
podeb = b.cen(f"window.__cen.cenPodeEncerrar(c,'{OS}')"); print('   cenPodeEncerrar:', podeb)
bt = b.btns('aside[role=dialog]')
b.ok(not any(x.startswith('Conferir e encerrar') or x.startswith('Encerrar') for x in bt), 'sem botão de encerrar com saldo 100 ha e sobra em custódia', bt)
# tentar o caminho de encerrar: Enviar para conferência não deve aparecer com saldo > 0
b.ok('Enviar para conferência' not in bt, 'Enviar para conferência não aparece com saldo de 100 ha', bt)
b.shot('e2e_04_os_exec.png')
er = b.erros(); b.ok(not er, 'sem erro de JS na O.S.', er)
b.fim()
