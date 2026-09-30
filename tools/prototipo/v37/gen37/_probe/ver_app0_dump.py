# -*- coding: utf-8 -*-
"""Verificador App: despeja texto, cabeçalho, rodapé, corte e largura das telas no estado inicial (1440x1000)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
telas = sys.argv[1:] or ['MB-01', 'MB-02', 'MB-02det', 'MB-03', 'MB-03x-recibo', 'MB-04', 'MB-05', 'OS-0424-app']
v = V()
try:
    for t in telas:
        v.abrir(t)
        print('=' * 20, t, '| title:', v.J('document.title'))
        print('HDR:', v.hdr()); print('FOOT:', v.foot()); print('CORTE:', v.corte(), 'LARG:', v.larg(), 'ERRS:', v.erros())
        print(v.J("document.querySelector('main').innerText"))
        v.shot('ver_app0_' + t + '.png')
finally:
    v.fim()
