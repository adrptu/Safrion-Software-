import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); PR=os.path.join(HERE,'_probe')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
    r=J("(()=>{const g=document.querySelector('[aria-label=\"Filtrar por fase\"]'); const bs=[...g.querySelectorAll('button')].map(b=>{const r=b.getBoundingClientRect(); return [b.innerText.replace(/\\s+/g,' ').trim(), Math.round(r.left), Math.round(r.right), Math.round(r.top)];}); const gr=g.getBoundingClientRect(); return {g:[Math.round(gr.left),Math.round(gr.right),g.scrollWidth,g.clientWidth], bs};})()")
    print(json.dumps(r,ensure_ascii=False))
    c.shot(os.path.join(PR,'verif_chips.png'))
finally:
    c.close(); srv.terminate()
