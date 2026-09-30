# -*- coding: utf-8 -*-
"""Passo 7a · sonda dos filtros do topo (Fazenda/Safra): quais telas têm os seletores e quais opções oferecem."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
for t in ['OS.dc.html', 'EST.dc.html', 'IN-04.dc.html', 'SAF.dc.html', 'CMP.dc.html']:
    b.goto(t)
    sel = b.J("[...document.querySelectorAll('select')].map(s=>[s.getAttribute('aria-label'), s.value, [...s.options].map(o=>o.value+'|'+o.text).join(', '), s.disabled, !!s.offsetParent])")
    hdr = b.J("(document.querySelector('header')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    print(t, '\n   selects:', sel, '\n   header:', (hdr or '')[:300], '\n   erros:', b.erros())
