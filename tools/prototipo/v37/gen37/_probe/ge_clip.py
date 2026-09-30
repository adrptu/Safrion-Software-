import sys,os,time,subprocess
sys.path.insert(0,'.')
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory','_render'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); c.size(1440,1100)
try:
  for t in sys.argv[1:]:
    c.goto(f'http://127.0.0.1:{p}/{t}'); time.sleep(.3)
    print(t, c.js("""[...document.querySelectorAll("[role=table]")].map((g,gi)=>{const R=g.closest("section").getBoundingClientRect().right-12; return [...g.querySelectorAll('button,a,span')].filter(x=>x.getBoundingClientRect().width>0 && x.getBoundingClientRect().right>R-1).map(x=>gi+':'+x.innerText.slice(0,30)+':'+Math.round(x.getBoundingClientRect().right-R))}).flat().slice(0,12)"""))
finally:
  c.close(); srv.terminate()
