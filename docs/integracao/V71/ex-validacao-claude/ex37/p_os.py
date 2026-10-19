# Uso: EXCH=CHROME2 python3 p_os.py OS-0418 regex1 regex2 ... -> painel da O.S. no kanban (OS) e trechos
import json,time,sys,re
from lib import *
os_id=sys.argv[1]; c=novo()
try:
    abre(c,'OS')
    r=c.js("""(()=>{const e=[...document.querySelectorAll('main *')].filter(x=>x.children.length===0&&x.textContent.trim()===%s&&x.getClientRects().length&&!x.closest('select'))[0]; if(!e) return null; const card=e.closest('[role=row],tr,article,li,[data-card],button,[role=button]')||e; card.scrollIntoView({block:'center'}); card.click(); return card.innerText.replace(/\\s+/g,' ').slice(0,200);})()""" % json.dumps(os_id))
    print('clique:',r); time.sleep(1)
    d=paineis(c) or ''; open(f'painel_{os_id}.txt','w').write(d); shot(c,'painel_'+os_id)
    for rx in sys.argv[2:]:
        print('##',rx); [print('  ',x) for x in dict.fromkeys(re.findall(rx,d))]
finally: c.close()
