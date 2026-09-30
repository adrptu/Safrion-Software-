import sys,os,time,subprocess,json
sys.path.insert(0,'.')
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory','_render'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/MA-01.dc.html'); time.sleep(.4)
    print(J("(()=>{const g=document.querySelectorAll('[role=table]')[0]; const r=[...g.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Colhedora')>=0); r.querySelectorAll('[role=cell]')[1].click(); return r.querySelectorAll('[role=cell]').length;})()"))
    time.sleep(.4); print(J("(document.querySelector('aside[role=dialog]')||{}).innerText"))
    c.goto(f'http://127.0.0.1:{p}/MA-02.dc.html'); time.sleep(.4)
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Registrar inspeção').click()"); time.sleep(.4)
    print(J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(i=>i.id+'='+i.value)"))
finally: c.close(); srv.terminate()
