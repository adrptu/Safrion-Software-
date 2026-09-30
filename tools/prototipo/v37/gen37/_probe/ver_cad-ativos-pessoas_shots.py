# Verificador: fotos 1440 de largura (altura total) de CD-03 e CD-04 + medidas de corte de texto e largura.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J
MED=r"""(()=>{const out={};
 out.docW=[document.documentElement.scrollWidth, document.documentElement.clientWidth];
 out.grades=[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth;});
 // texto cortado: elementos com overflow hidden/ellipsis cujo scrollWidth > clientWidth
 const cut=[]; document.querySelectorAll('main *').forEach(e=>{ if(!e.children.length && e.innerText && e.scrollWidth>e.clientWidth+1){ const cs=getComputedStyle(e); if(cs.overflow!=='visible'||cs.textOverflow==='ellipsis') cut.push(e.innerText.slice(0,80)); }});
 out.cut=cut.slice(0,30);
 out.root=document.querySelector('[data-root]')?document.querySelector('[data-root]').getBoundingClientRect().height:null;
 return out;})()"""
try:
    for f in sys.argv[1:]:
        t.c.size(1440,1000); t.goto(f)
        print(f,'erros:',t.errs(),'motor:',t.errs_motor())
        print(json.dumps(J(MED),ensure_ascii=False))
        hh=J("Math.max(document.documentElement.scrollHeight, document.querySelector('[data-root]').getBoundingClientRect().height)")
        t.c.size(1440,int(hh)); time.sleep(.4); t.shot('ver_cap_'+f.replace('.dc.html','_full.png')); t.c.size(1440,1000); time.sleep(.2)
        t.shot('ver_cap_'+f.replace('.dc.html','_1000.png'))
finally:
    t.fim()
