# SU-04: abre a cotação SOL-2026-07 · Fertilizantes e lê itens/quantidades da proposta de R$ 360.905
import json,time,sys,re
from lib import *
c=novo()
try:
    abre(c,'SU-04')
    r=clica_linha(c,'SOL-2026-07 · Fertilizantes'); print('linha',r); time.sleep(.6)
    d=paineis(c) or ''
    if not d:
        t=texto(c); i=t.find('Aprovar contratação'); d=t[i-3000:i+3000]
    open('su04_fert.txt','w').write(d); shot(c,'su04_sol07_fert')
    for rx in [r'[^\n]*\d+(?:[.,]\d+)?\s*(?:t|kg)\b[^\n]*',r'[^\n]*360\.905[^\n]*',r'[^\n]*96,99[^\n]*']:
        print('##',rx); [print('  ',x) for x in list(dict.fromkeys(re.findall(rx,d)))[:30]]
finally: c.close()
