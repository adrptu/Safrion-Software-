# -*- coding: utf-8 -*-
"""Passo 8d · resíduos da regra antiga fora das telas da lista: GE-06 (indicador de água) e o quadro órfão IN-02x-os0422; CF (política de irrigação atual)."""
import sys, os, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
b.goto('GE-06.dc.html'); x = b.body().replace('\n', ' / '); i = x.find('Uso de água'); print('   GE-06:', x[max(0, i - 40):i + 260])
b.ok('PA-07' not in x and 'autorizados' not in x, 'GE-06: indicador de água sem "política PA-07" nem "mm autorizados"', x[max(0, i - 40):i + 260])
b.goto('IN-02x-os0422.dc.html'); x = b.body().replace('\n', ' / '); print('   IN-02x-os0422:', x[:300]); print('   exceção:', re.findall(r'.{50}xceç.{50}', x)[:3])
b.ok('xceç' not in x, 'IN-02x-os0422 (quadro não gerado mais) não deveria continuar servido com "exceção de água"', re.findall(r'.{50}xceç.{50}', x)[:2])
for t in ('CF-01', 'CF-02', 'CF-03', 'CF-04', 'CF-05'):
    b.goto(t + '.dc.html'); x = b.body().replace('\n', ' '); m = re.findall(r'.{60}(?:IR-LIM|PA-07|irrigação \(só água\)).{80}', x)
    if m: print(f'   {t}:', m[:2])
b.fim()
