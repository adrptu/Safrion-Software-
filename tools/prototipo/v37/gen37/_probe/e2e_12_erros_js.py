# -*- coding: utf-8 -*-
"""Passo 12 · varredura de erros de JS nas telas recompiladas (lote passado na linha de comando)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B()
for t in sys.argv[1:]:
    w = 390 if t.startswith('MB-') else 1440
    b.size(w, 1000); b.console = []
    try:
        b.goto(t + '.dc.html', wait=0.6); er = b.erros(); n = len(b.body())
    except Exception as ex: er = [str(ex)]; n = 0
    b.ok(not er and n > 200, f'{t}: carrega sem erro de JS ({n} caracteres)', er)
b.fim()
