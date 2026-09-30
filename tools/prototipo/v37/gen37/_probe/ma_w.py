import sys,os,time,subprocess,json
sys.path.insert(0,'.')
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory','_render'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,1000)
    for t in sys.argv[1:]:
        c.goto(f'http://127.0.0.1:{p}/{t}'); time.sleep(.4)
        print(t, J("[...document.querySelectorAll('[role=table]')].map(g=>({cw:g.parentElement.clientWidth, cols:[...g.querySelector('[role=row]').children].map(h=>h.innerText.replace(/\\s+/g,' ').slice(0,14)+':'+Math.round(h.getBoundingClientRect().width))}))"))
finally: c.close(); srv.terminate()
