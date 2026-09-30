import sys, os, time, subprocess, json, base64
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R=os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Abrir safra/.test(b.innerText.trim())); b.click();})()"); time.sleep(.5)
    J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.6)
    for extra in sys.argv[2:]: J(extra); time.sleep(.5)
    d=c.call('Page.captureScreenshot',{'format':'png','clip':{'x':270,'y':330,'width':1130,'height':360,'scale':1.4}})
    open(sys.argv[1],'wb').write(base64.b64decode(d['data']))
finally:
    c.close(); srv.terminate()
