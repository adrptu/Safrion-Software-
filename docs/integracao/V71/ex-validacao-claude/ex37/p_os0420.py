# EX-01: painel da OS-0420 × O.S. completa × REC-014 (insumo e dose)
import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,'OS')
    t=texto(c); print('OS-0420 na tela:', 'OS-0420' in t)
    r=c.js("""(()=>{const e=[...document.querySelectorAll('main *')].filter(x=>x.children.length===0&&/OS-0420/.test(x.textContent)&&x.getClientRects().length&&!x.closest('select'))[0]; if(!e) return null; const card=e.closest('[role=row],tr,article,li,[data-card],button,[role=button]')||e; card.scrollIntoView({block:'center'}); card.click(); return card.tagName+' '+card.innerText.replace(/\\s+/g,' ').slice(0,200);})()""")
    print('clique:',r); time.sleep(1)
    d=paineis(c); print(d[:3500]); shot(c,'os0420_painel')
    for rx in [r'MAP[^\n]{0,60}',r'KCl[^\n]{0,60}',r'REC-0\d\d[^\n]{0,60}']:
        print(rx, re.findall(rx,d or ''))
finally: c.close()
