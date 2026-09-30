# -*- coding: utf-8 -*-
"""Estado inicial das telas do app ligadas ao cenário: texto, cabeçalho, rodapé, corte, largura, erros JS."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_appv_lib import V
a = V()
try:
    for t in sys.argv[1:] or ['MB-01','MB-02','MB-02det','MB-03','MB-03x-recibo','MB-04','MB-05','OS-0424-app']:
        a.abrir(t)
        print('=====', t, '| title:', a.J('document.title'), '| hdr:', a.hdr())
        print('FOOT:', a.foot(), '| CORTE:', a.corte(), '| LARG:', a.larg(), '| ERR:', a.erros())
        print(a.main()[:3000])
        a.shot(f'ver_appv1_{t}.png')
finally:
    a.fim()
