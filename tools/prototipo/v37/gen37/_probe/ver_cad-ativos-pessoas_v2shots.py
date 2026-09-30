# Verificador rodada 2: fotos 1440x1000 e altura total + medidas (largura, texto cortado, altura do conteúdo vs HEIGHTS37).
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J
MED=r"""(()=>{const out={};
 out.docW=[document.documentElement.scrollWidth, document.documentElement.clientWidth];
 out.grades=[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth;});
 const cut=[]; document.querySelectorAll('body *').forEach(e=>{ if(e.children.length||!e.innerText) return; const cs=getComputedStyle(e);
   if((e.scrollWidth>e.clientWidth+1&&(cs.overflow!=='visible'||cs.textOverflow==='ellipsis'))||(e.scrollHeight>e.clientHeight+2&&cs.overflow==='hidden')) cut.push(e.tagName+':'+e.innerText.slice(0,80)); });
 out.cut=cut.slice(0,30);
 const m=document.querySelector('main'); out.main=m?[m.scrollHeight,m.clientHeight,Math.round(m.getBoundingClientRect().top)]:null;
 out.root=document.querySelector('[data-root]')?Math.round(document.querySelector('[data-root]').getBoundingClientRect().height):null;
 out.bodyH=document.documentElement.scrollHeight;
 return out;})()"""
try:
    for f in sys.argv[1:]:
        t.c.size(1440,1000); t.goto(f)
        print(f,'erros:',t.errs(),'motor:',t.errs_motor())
        print(json.dumps(J(MED),ensure_ascii=False))
        t.shot('ver2_cap_'+f.replace('.dc.html','_1000.png'))
        hh=J("Math.max(document.documentElement.scrollHeight, (document.querySelector('main')||document.body).scrollHeight+100)")
        t.c.size(1440,int(hh)); time.sleep(.4); t.shot('ver2_cap_'+f.replace('.dc.html','_full.png'))
        print('full h',hh, json.dumps(J(MED),ensure_ascii=False))
finally:
    t.fim()
