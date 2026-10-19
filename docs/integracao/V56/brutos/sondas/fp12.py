import sys, os, json, time
G = sys.argv[1]; sys.path.insert(0, G); os.chdir(G)
from cada_lib import T
t = T(); J = t.J
FX = 'aside[aria-label^="Ficha do pivô"]'
try:
    t.goto('CD-03.dc.html'); J("localStorage.removeItem('talhao-os-ficha-pivo-v1'); localStorage.removeItem('talhao-os-irrigacao-v1')")
    t.goto('IR-01.dc.html#P2'); time.sleep(1.2)
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.replace(/\\s+/g,' ').trim()==='Ficha do pivô'); b&&b.click();})()"); time.sleep(.8)
    print('F12', J(f"(document.querySelector('{FX}')||{{}}).innerText||''"))
    print('LK', J(f"(()=>{{const a=[...document.querySelectorAll('{FX} a')].pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()"))
finally:
    t.fim()
