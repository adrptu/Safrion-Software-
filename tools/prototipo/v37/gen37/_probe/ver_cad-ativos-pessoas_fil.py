# Verificador: menus de filtro das colunas (classe em CD-03; habilitações em CD-04) e ordenação por custo.
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cada_lib import T
t=T(); J=t.J; t.c.size(1440,1000)
FM="""((ti,lab)=>{const tb=document.querySelectorAll('[role=table]')[ti]; const b=[...tb.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'')==='Filtrar '+lab); if(!b) return 'sem botão'; b.click(); return 'ok';})"""
def menu(): return J("(()=>{const d=[...document.querySelectorAll('[role=dialog],[role=menu],[role=listbox]')].filter(x=>x.tagName!=='ASIDE'); return d.map(x=>x.innerText.replace(/\\n/g,' | ')).join(' ### ').slice(0,600);})()")
try:
    t.goto('CD-03.dc.html'); print(J(f"({FM})(0,'Classe e capacidade')")); time.sleep(.3); print('menu classe:',menu())
    t.goto('CD-04.dc.html'); print(J(f"({FM})(0,'Habilitações')")); time.sleep(.3); print('menu hab:',menu())
    J("document.querySelectorAll('[role=table]')[0].querySelectorAll('.g2hb')[4].click()"); time.sleep(.3)
    print('ordem custo:',J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')].map(r=>r.querySelector('b').innerText+':'+r.innerText.match(/R\\$ [\\d,.]+/)[0]).join(', ')"))
finally:
    t.fim()
