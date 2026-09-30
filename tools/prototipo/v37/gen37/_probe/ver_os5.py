# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 5: qual DIV transborda na CA-04 (4 px)."""
import sys, os, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
try:
    T.c.goto(f'http://127.0.0.1:{T.p}/CA-04.dc.html', wait=0.9)
    print(J("""(()=>{const out=[]; document.querySelectorAll('div').forEach(e=>{ if(e.scrollWidth>e.clientWidth+2 && e.offsetParent!==null){ const cs=getComputedStyle(e); out.push([e.scrollWidth,e.clientWidth,cs.overflowX,(e.getAttribute('aria-label')||''),e.innerText.slice(0,80).replace(/\\s+/g,' ')]); } }); return out.slice(0,5);})()"""))
    T.shot('ver_os5_ca04.png')
finally:
    T.fim()
