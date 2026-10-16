# AG-01#VIS-013: painel da vistoria (EX-05 dois verdes; EX-01 Inseticida B 1,0 kg/ha na decisão)
import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,'AG-01','#VIS-013'); time.sleep(1)
    d=paineis(c) or ''
    open('painel_VIS-013.txt','w').write(d); shot(c,'ag01_vis013_painel')
    print(d[:2500])
    print('BOTOES:',c.js("""(()=>{const d=[...document.querySelectorAll('[role=dialog],aside')].filter(e=>e.getClientRects().length); return d.flatMap(x=>[...x.querySelectorAll('button,a')].filter(b=>b.getClientRects().length).map(b=>(b.innerText||'').trim().replace(/\\s+/g,' ').slice(0,50)+(getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'?' [VERDE]':'')+(b.disabled?' [dis]':'')));})()"""))
finally: c.close()
