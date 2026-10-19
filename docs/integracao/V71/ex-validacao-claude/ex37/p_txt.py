# Uso: EXCH=CHROME2 python3 p_txt.py TELA [hash] [regex]  -> trechos do innerText e captura
import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,sys.argv[1],sys.argv[2] if len(sys.argv)>2 else '')
    t=texto(c)
    rx=sys.argv[3] if len(sys.argv)>3 else None
    if rx:
        for m in re.finditer(rx,t): print('…'+t[max(0,m.start()-150):m.end()+100].replace('\n',' ⏎ ')+'…\n')
    else: print(t[:5000])
    shot(c,sys.argv[1]+'_inicial')
finally: c.close()
