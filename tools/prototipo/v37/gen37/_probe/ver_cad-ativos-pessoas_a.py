# -*- coding: utf-8 -*-
"""Verificador independente · sonda A: capturas 1440x1000, erros de JS, rolagem lateral, texto cortado nas duas telas."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cada_lib import T
t=T(); J=t.J
CLIP="""(()=>{const out=[]; document.querySelectorAll('main *').forEach(e=>{ if(e.children.length>0 && !['SPAN','B','A','BUTTON','LABEL'].includes(e.tagName)) return; const cs=getComputedStyle(e);
 if((e.scrollWidth>e.clientWidth+1 && (cs.overflow!='visible'||cs.overflowX!='visible'||cs.textOverflow=='ellipsis')) || (e.scrollHeight>e.clientHeight+2 && cs.overflowY=='hidden')) out.push(e.tagName+':'+(e.innerText||'').slice(0,60)+' ['+e.scrollWidth+'/'+e.clientWidth+','+e.scrollHeight+'/'+e.clientHeight+']'); }); return out.slice(0,30);})()"""
try:
    for f in ['CD-03.dc.html','CD-04.dc.html']:
        t.c.size(1440,1000); t.goto(f)
        print('==',f,'erros:',t.errs(),'motor:',t.errs_motor())
        print(' header:',t.header()[:400])
        print(' docW:',J("[document.documentElement.scrollWidth,document.documentElement.clientWidth]"))
        print(' grades:',J("[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth;})"))
        print(' cortado:',J(CLIP))
        t.shot('ver_cap_'+f.replace('.dc.html','_1000.png'))
        hh=J("document.querySelector('[data-root]').getBoundingClientRect().height"); print(' altura root:',hh)
        t.c.size(1440,int(hh)); time.sleep(.4); t.shot('ver_cap_'+f.replace('.dc.html','_full.png')); t.c.size(1440,1000)
        print(' texto:',J("document.querySelector('main').innerText.replace(/\\n+/g,' | ')")[:3000])
finally:
    t.fim()
