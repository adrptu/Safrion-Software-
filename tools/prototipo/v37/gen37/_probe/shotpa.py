import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R=os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/PA.dc.html',wait=1.3)
    J("document.querySelector('button[aria-label=\"Abrir plano Soja alta tecnologia\"]').click()"); time.sleep(.5)
    J("[...document.querySelectorAll('main button')].find(b=>b.innerText==='Dessecação pré-plantio').click()"); time.sleep(.5)
    c.shot(sys.argv[1])
finally:
    c.close(); srv.terminate()
