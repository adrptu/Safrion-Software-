# -*- coding: utf-8 -*-
"""Verificador App 10: MB-04 com 2 ordens na fila e 3 ocorrências registradas pela própria tela (formulário aberto de novo)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    v.abrir('MB-04')
    for txt in ('Bico entupido na seção 2.', 'Vento forte; parei 20 min.', 'Chuva fraca às 11:00.'):
        v.setv('#oc_txt', txt); v.clk('Registrar ocorrência'); v.clk('Nova ocorrência')
    c = v.corte(); print('   MB-04 (2 ordens, 3 ocorrências curtas, formulário):', c)
    v.ok(c['excesso'] <= 0, 'MB-04 cabe: ' + str(c))
    v.abrir('MB-04'); c = v.corte(); print('   reaberta:', c)
    v.c.size(1440, 1300); time.sleep(.3); v.shot('ver_app10_mb04.png'); v.c.size(1440, 1000)
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
