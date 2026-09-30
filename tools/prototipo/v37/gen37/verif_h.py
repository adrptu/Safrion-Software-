import sys, os, time, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free())
try:
    c.size(1440,1100)
    for f in ['CD-01.dc.html','CD-01det.dc.html','CD-02.dc.html','CD-05.dc.html']:
        c.goto(f'http://127.0.0.1:{p}/{f}',wait=1.2)
        print(f, c.js("(()=>{const R=document.querySelector('[data-root]'); const h0=R.getBoundingClientRect().height; R.style.height='auto'; const h=Math.ceil(R.getBoundingClientRect().height); return [h0,h];})()"))
finally:
    c.close(); srv.terminate()
