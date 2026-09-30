# Verificador rodada 4 · sonda A: visão geral em 1440x1000 (erros, cabeçalho, grades, linhas, cortes, capturas)
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
t=T(); J=t.J
try:
    for f in ('CD-03.dc.html','CD-04.dc.html'):
        t.c.size(1440,1000); t.goto(f); time.sleep(.3)
        print('=====',f,'erros:',t.errs(),'motor:',t.errs_motor())
        print(' header:',t.header()[:500])
        print(' header btns:',J("[...document.querySelectorAll('header button, header a')].map(b=>b.innerText.trim()+'|'+(b.getAttribute('href')||'')+'|'+getComputedStyle(b).backgroundColor)"))
        print(' grades:',J("[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth+' tbl='+t.scrollWidth;})"))
        print(' docW:',J("[document.documentElement.scrollWidth,document.documentElement.clientWidth,document.documentElement.scrollHeight]"))
        rows=J("[...document.querySelectorAll('[role=table]')].map(t=>[...t.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()))")
        for i,rs in enumerate(rows):
            print(' -- grade',i)
            for r in rs: print('   ',r[:300])
        cut=J("""[...document.querySelectorAll('main *')].filter(e=>{const s=getComputedStyle(e); return (s.overflow==='hidden'||s.textOverflow==='ellipsis'||s.overflowX==='hidden') && e.scrollWidth>e.clientWidth+1 && e.innerText && e.innerText.trim().length>0 && e.clientWidth>0;}).map(e=>e.tagName+':'+e.innerText.replace(/\\s+/g,' ').slice(0,80)+' ['+e.scrollWidth+'>'+e.clientWidth+']').slice(0,30)""")
        print(' cortados:',json.dumps(cut,ensure_ascii=False))
        print(' blocos:',J("[...document.querySelectorAll('main section, main h2, main h3')].map(e=>e.tagName+':'+e.innerText.split('\\n')[0].slice(0,120))"))
        t.shot('ver_cad-ativos-pessoas_r4_'+f.replace('.dc.html','')+'_1000.png')
        hh=J("document.documentElement.scrollHeight"); t.c.size(1440,int(max(hh,1000))); time.sleep(.3); t.shot('ver_cad-ativos-pessoas_r4_'+f.replace('.dc.html','')+'_full.png'); t.c.size(1440,1000)
finally:
    t.fim()
