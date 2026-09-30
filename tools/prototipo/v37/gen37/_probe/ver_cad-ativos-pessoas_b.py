# -*- coding: utf-8 -*-
"""Verificador · sonda B: vocabulário da condição técnica no MA-01 e no OS (T1) para comparar com o CD-03."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cada_lib import T
t=T(); J=t.J
try:
    for f in ['MA-01.dc.html','MA-04det.dc.html']:
        t.goto(f)
        tx=J("document.querySelector('main').innerText.replace(/\\n+/g,' | ')")
        i=tx.find('T1'); print('==',f, tx[:200]); 
        import re
        for m in re.finditer('T1',tx):
            print('  ...',tx[max(0,m.start()-120):m.start()+220]); 
        print(' header:',t.header()[:300])
finally:
    t.fim()
