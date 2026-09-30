# -*- coding: utf-8 -*-
"""Passo 4b (2ª passada) · OS.dc.html com o turno de 60 ha ainda no aparelho: realizado não soma e a linha diz que aguarda sinal."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); lin = b.rowtxt(OS); print('   linha:', lin)
b.row(OS); p = b.aside(); a = p[p.find('APONTAMENTOS'):][:400]; print('   apontamentos:', a); print('   próximo:', p[p.find('PRÓXIMO'):][:300])
b.ok('Em execução' in lin and '0 / 160 ha' in lin and 'Aguardando sinal' in a and '60 ha no aparelho aguardando sinal' in p, 'O.S.: 0 / 160 ha, "Dia 1 · app · Aguardando sinal" e 60 ha no aparelho', (lin, a))
b.ok('aguardando sinal' in lin.lower() or 'sinal' in lin.lower(), 'lista da O.S. sinaliza o apontamento aguardando sinal (condição)', lin)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
