# Verificador rodada 3: visão geral CD-03 e CD-04 em 1440x1000 (erros, cabeçalho, largura das grades, texto das linhas, capturas)
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
t=T(); J=t.J
try:
    for f in ('CD-03.dc.html','CD-04.dc.html'):
        t.goto(f); t.c.size(1440,1000); time.sleep(.4)
        print('=====',f,'erros:',t.errs(),'motor:',t.errs_motor())
        print(' header:',t.header()[:400])
        print(' grades:',J("[...document.querySelectorAll('[role=table]')].map(t=>{const w=t.parentElement; return w.scrollWidth+'/'+w.clientWidth+' tbl='+t.scrollWidth;})"))
        print(' docW:',J("document.documentElement.scrollWidth"),'bodyH',J("document.documentElement.scrollHeight"),'root',J("(document.querySelector('[data-root]')||{getBoundingClientRect:()=>({height:0})}).getBoundingClientRect().height"))
        print(' main:',J("(()=>{const m=document.querySelector('main'); return m?[m.scrollHeight,m.clientHeight,m.scrollWidth,m.clientWidth]:null})()"))
        rows=J("[...document.querySelectorAll('[role=table]')].map(t=>[...t.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()))")
        for i,rs in enumerate(rows):
            print(' -- grade',i)
            for r in rs: print('   ',r[:260])
        # texto cortado: elementos com overflow escondido cujo scrollWidth > clientWidth
        cut=J("""[...document.querySelectorAll('main *')].filter(e=>{const s=getComputedStyle(e); return (s.overflow==='hidden'||s.textOverflow==='ellipsis'||s.overflowX==='hidden') && e.scrollWidth>e.clientWidth+1 && e.innerText && e.innerText.trim().length>0 && e.clientWidth>0;}).map(e=>e.tagName+':'+e.innerText.replace(/\\s+/g,' ').slice(0,80)+' ['+e.scrollWidth+'>'+e.clientWidth+']').slice(0,30)""")
        print(' cortados:',json.dumps(cut,ensure_ascii=False))
        print(' texto:',J("document.querySelector('main').innerText.replace(/\\s+/g,' ').slice(0,1200)"))
        t.shot('ver_cad-ativos-pessoas_v3_'+f.replace('.dc.html','')+'_1000.png')
        hh=J("document.documentElement.scrollHeight"); t.c.size(1440,int(max(hh,1000))); time.sleep(.3); t.shot('ver_cad-ativos-pessoas_v3_'+f.replace('.dc.html','')+'_full.png'); t.c.size(1440,1000)
finally:
    t.fim()
