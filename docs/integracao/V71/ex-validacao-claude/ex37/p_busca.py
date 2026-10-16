# Uso: EXCH=CHROME2 python3 p_busca.py 'regex' TELA1 TELA2 ... -> trechos no texto inicial de cada tela
import json,time,sys,re
from lib import *
c=novo(); rx=sys.argv[1]
try:
    for t in sys.argv[2:]:
        abre(c,t); s=texto(c).replace('\n',' ⏎ ')
        ms=[s[max(0,m.start()-160):m.end()+120] for m in re.finditer(rx,s)]
        print('==',t,len(ms)); [print('   …'+x+'…') for x in ms[:6]]
finally: c.close()
