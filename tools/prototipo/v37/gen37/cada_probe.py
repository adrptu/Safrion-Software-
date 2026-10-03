# -*- coding: utf-8 -*-
"""Sonda rápida (não é teste): erros de JS, cabeçalho, altura do conteúdo e rolagem lateral das grades em CD-03/CD-04."""
import sys, time
from cada_lib import T
t=T(); J=t.J
try:
    for f in sys.argv[1:]:
        t.goto(f); hh=J("document.querySelector('[data-root]').getBoundingClientRect().height"); t.c.size(1440,int(hh)); time.sleep(.3)
        print(f,'erros:',t.errs())
        print(' header:',t.header()[:300])
        print(' altura main:',J("(()=>{const m=document.querySelector('main'); return [m.scrollHeight, m.getBoundingClientRect().top, document.querySelector('[data-root]').getBoundingClientRect().height];})()"))
        print(' grades (scrollW/clientW):',J("[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth;})"))
        t.shot(f.replace('.dc.html','_probe.png'))
finally:
    t.fim()
