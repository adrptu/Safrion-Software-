import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R=os.path.join(HERE,'_render')
W=int(sys.argv[1]) if len(sys.argv)>1 else 1440; ET=int(os.environ.get('ETAPA','3')); SAF=os.environ.get('SAF','2026/27')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(W,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
    J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>x.innerText.indexOf(%s)>=0); const b=[...r.querySelectorAll('button')].find(b=>/safra/.test(b.innerText)); b.click();})()" % json.dumps(SAF)); time.sleep(.5)
    J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[%d].click()" % (ET-1)); time.sleep(.6)
    if os.environ.get('EXP'): J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Expandir tudo' && b.offsetParent).click()"); time.sleep(.5)
    print(J(r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const box=t.parentElement; const a=Math.round(t.getBoundingClientRect().width);
      const old=t.style.minWidth; t.style.minWidth='0'; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>Math.round(h.getBoundingClientRect().width)); const nat=Math.round(t.getBoundingClientRect().width); t.style.minWidth=old;
      return JSON.stringify({vw:innerWidth, doc:document.documentElement.scrollWidth, box:box.clientWidth, boxScroll:box.scrollWidth, tab:a, natural:nat, naturalCols:hs});})()"""))
    if len(sys.argv)>2: c.shot(sys.argv[2])
finally:
    c.close(); srv.terminate()
