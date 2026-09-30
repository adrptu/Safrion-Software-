import sys,os,time,subprocess
sys.path.insert(0,'.')
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory','_render'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); c.size(1440,1100)
try:
  for t in sys.argv[1:]:
    c.goto(f'http://127.0.0.1:{p}/{t}'); time.sleep(.3)
    print(t, c.js("[...document.querySelectorAll('[role=table]')].map(g=>{let e=g; while(e&&e.scrollWidth<=e.clientWidth+1&&e.parentElement) e=e.parentElement; const sc=[...g.querySelectorAll('*')].concat([g]).filter(x=>x.scrollWidth>x.clientWidth+2 && getComputedStyle(x).overflowX!='visible'); return sc.map(x=>x.className+':'+x.scrollWidth+'/'+x.clientWidth).join(',')})"))
finally:
  c.close(); srv.terminate()
