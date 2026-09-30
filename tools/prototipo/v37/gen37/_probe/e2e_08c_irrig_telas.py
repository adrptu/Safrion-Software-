# -*- coding: utf-8 -*-
"""Passo 8c · IR-02, PL-04 e MB-08: OS-0422 (13,5 mm em 2 × 6,75 mm, janela a definir), OS-0423 (B3 14:00–15:00, ET), OS-0418 fertirrigação ao agrônomo."""
import sys, os, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B()
for t, w in (('IR-02.dc.html', 1440), ('PL-04.dc.html', 1440), ('MB-08.dc.html', 390)):
    b.size(w, 1400); b.goto(t); x = b.body().replace('\n', ' ')
    def ctx(k): i = x.find(k); return x[max(0, i - 80):i + 220] if i >= 0 else '(ausente)'
    print(f'== {t}\n   0422: {ctx("OS-0422")}\n   0423: {ctx("OS-0423")}\n   0418: {ctx("OS-0418")}\n   agrônomo: {[m for m in re.findall(r".{80}agrônom.{60}", x)][:4]}')
    print('   erros:', b.erros())
