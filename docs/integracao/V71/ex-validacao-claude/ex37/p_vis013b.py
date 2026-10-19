# AG-01#VIS-013 → "Decidir controle": botões verdes visíveis e dose do Inseticida B
import json,time,sys,re
from lib import *
BT="""(()=>{const vis=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'; return [...document.querySelectorAll('button,a')].filter(vis).filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>(b.innerText||'').trim().replace(/\\s+/g,' ').slice(0,60)+(b.closest('[role=dialog],aside')?' @painel':' @tela'));})()"""
c=novo()
try:
    abre(c,'AG-01','#VIS-013'); time.sleep(1)
    print('verdes antes:',c.js(BT))
    print(clica(c,'Decidir controle')); time.sleep(1)
    print('verdes depois:',c.js(BT))
    d=paineis(c) or ''; open('painel_VIS-013_decidir.txt','w').write(d); shot(c,'ag01_vis013_decidir')
    for m in re.finditer(r'Inseticida B',d): print('   …'+d[max(0,m.start()-200):m.end()+200].replace('\n',' ⏎ ')+'…')
    print(json.dumps(resume_dlg(dialogo(c)),ensure_ascii=False))
finally: c.close()
