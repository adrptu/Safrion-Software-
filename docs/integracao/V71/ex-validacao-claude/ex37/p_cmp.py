# CMP: "Abrir compra" (Safra 2026/27 · SOL-2026-07), etapa 4 (Compare propostas): quantidades da proposta Fertisul
import json,time,sys,re
from lib import *
from comp_lib import IR_ETAPA
c=novo()
try:
    abre(c,'CMP')
    print(clica(c,'Abrir compra')); time.sleep(1)
    for n in (2,3,4,5):
        r=c.js(f"({IR_ETAPA})({n})"); time.sleep(.6)
        t=texto(c); open(f'cmp_etapa{n}.txt','w').write(t); shot(c,f'cmp_etapa{n}')
        print('etapa',n,r, '| 96,99:', re.findall(r'[^\n]{0,80}96,99[^\n]{0,60}',t)[:3], '| 360.905:', re.findall(r'[^\n]{0,80}360\.905[^\n]{0,60}',t)[:3], '| 78,85:', re.findall(r'[^\n]{0,60}78,85[^\n]{0,60}',t)[:3])
finally: c.close()
