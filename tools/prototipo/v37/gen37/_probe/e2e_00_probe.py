# -*- coding: utf-8 -*-
"""Sonda: abre uma tela no navegador compartilhado e lista botões, links e o texto principal. Uso: python3 e2e_00_probe.py OS.dc.html [w h]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B()
w, h = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1440, 1000)
b.size(w, h)
b.goto(sys.argv[1])
print('PATH', b.path())
print('BTNS', b.btns())
print('LINKS', b.links()[:40])
print('MAIN', b.main()[:int(sys.argv[4]) if len(sys.argv) > 4 else 2500])
print('ERROS', b.erros())
