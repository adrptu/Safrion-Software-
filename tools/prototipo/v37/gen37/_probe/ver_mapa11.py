# -*- coding: utf-8 -*-
"""Verificador 11: as 6 telas a 1440×1000 (erros de JS, rolagem horizontal, altura)."""
import time
from ver_mapa_lib import Sess
s=Sess(1440,1000)
try:
    for f in ['IN-01.dc.html','IN-02.dc.html','IN-02det.dc.html','IN-02x-os0420.dc.html','IN-03.dc.html','IN-04.dc.html']:
        s.go(f); m=s.js("({sh:document.documentElement.scrollHeight,sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
        print(f,m,'erros:',s.errs())
    s.go('IN-02x-os0420.dc.html'); s.click('Aprovar versão v3')
    print('1000px · link do recibo bottom:',s.js("Math.round([...document.querySelectorAll('[role=status] a')].find(x=>/Fila vazia/.test(x.innerText)).getBoundingClientRect().bottom)"))
finally:
    s.close()
