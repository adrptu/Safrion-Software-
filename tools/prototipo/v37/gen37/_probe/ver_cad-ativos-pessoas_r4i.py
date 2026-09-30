# Verificador rodada 4 · sonda I: coerência com outras telas — condição técnica no MA-01, conjunto da OS-0424 (ficha) x regra de potência do CD-03
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE); os.chdir(HERE)
from cada_lib import T
T0=time.time()
t=T(); J=t.J
def lg(*a): print(round(time.time()-T0,1),*a, flush=True)
try:
    t.c.size(1440,1000); t.goto('MA-01.dc.html')
    for n in ['Trator T1','Bomba do Pivô 2']:
        lg('MA-01',n,':',J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(n)})>=0); return r?r.innerText.replace(/\\s+/g,' '):null;}})()"))
    lg('MA-01 header cols:',J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]')].map(c=>c.innerText.trim())"))
    t.goto('OS-0424-ficha.dc.html'); tx=J("document.body.innerText.replace(/\\s+/g,' ')"); i=tx.find('Trator 04'); lg('ficha OS-0424:',tx[max(0,i-150):i+120])
    t.goto('CD-03.dc.html')
    lg('CD-03 Bomba 2:',t.rowtxt(0,'Bomba do Pivô 2'))
    t.clk('Montar conjunto'); t.fset('maq','Trator 04'); t.fset('impl','Pulverizador PJ-3030')
    J("(()=>{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(x=>x.innerText.trim()==='Pulverização'); l.querySelector('input').click();})()"); time.sleep(.2)
    lg('pot live:',t.fv('pot_c')); t.btn('Salvar'); time.sleep(.2); lg('alerts:',t.alerts())
    t.cancel()
    lg('erros:',t.errs())
finally:
    t.fim()
