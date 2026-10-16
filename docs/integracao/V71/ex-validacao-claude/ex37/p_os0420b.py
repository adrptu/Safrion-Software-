# EX-01: O.S. completa da OS-0420 (Abrir ordem completa) e busca de KCl / MAP / REC-014 / Trator 02 / aguarda PCP
import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,'OS')
    c.js("""(()=>{const e=[...document.querySelectorAll('main *')].filter(x=>x.children.length===0&&/OS-0420/.test(x.textContent)&&x.getClientRects().length&&!x.closest('select'))[0]; const card=e.closest('[role=row],tr,article,li,[data-card],button,[role=button]')||e; card.click();})()""")
    time.sleep(1)
    r=clica(c,'Abrir ordem completa'); print('clique',r); time.sleep(1.5)
    print('url',c.js('location.href'))
    t=texto(c)
    for rx in [r'[^\n]{0,80}MAP 11-52[^\n]{0,80}',r'[^\n]{0,80}KCl[^\n]{0,80}',r'[^\n]{0,60}REC-0\d\d[^\n]{0,80}',r'[^\n]{0,80}Trator 02[^\n]{0,80}',r'[^\n]{0,80}aguard[^\n]{0,80}PCP[^\n]{0,40}',r'[^\n]{0,80}PCP[^\n]{0,80}']:
        print('##',rx); [print('  ',x) for x in dict.fromkeys(re.findall(rx,t))]
    shot(c,'os0420_completa')
    open('os0420_completa.txt','w').write(t)
finally: c.close()
