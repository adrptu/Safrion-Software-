import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R=os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
    J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf('2025/26')>=0); [...r.querySelectorAll('button')].find(b=>/safra/.test(b.innerText)).click();})()"); time.sleep(.5)
    J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.6)
    J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Trator 02/.test(r.innerText)); r.querySelector('[role=cell] span').click();})()"); time.sleep(.6)
    c.shot(sys.argv[1])
finally:
    c.close(); srv.terminate()
