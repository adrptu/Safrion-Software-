# COLH: abre o painel de cada talhão (clique na linha) e procura valores t/ha diferentes no mesmo painel
import json,time,sys,re
from lib import *
c=novo()
try:
    for nome in ['Pivô 19','Pivô 6']:
        abre(c,'COLH')
        r=clica_linha(c,nome); time.sleep(.5)
        d=paineis(c)
        print('==',nome,r); print((d or '')[:4000]); shot(c,'colh_painel_'+nome.replace(' ','_'))
        print('t/ha:',re.findall(r'[\d.,]+\s*t/ha',d or ''))
finally: c.close()
