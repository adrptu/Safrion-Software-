import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); PR=os.path.join(HERE,'_probe')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
try:
    c.size(1440,900); c.goto(f'http://127.0.0.1:{p}/IN-04.dc.html',wait=1.2)
    labs=J("[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')].map(x=>x.innerText.trim())")
    for full in [False,True]:
        if full:
            J("[...document.querySelectorAll('[role=toolbar] button')].find(b=>b.innerText.trim()==='Tela cheia').click()"); time.sleep(.5)
        root='[role=dialog][aria-label="Mapa em tela cheia"] ' if full else ''
        SN=json.dumps(root+'nav[aria-label="Funcionalidades do mapa"] [role=tab]'); SI=json.dumps(root+'[role=group][aria-label^="Indicadores de"]')
        for l in labs:
            J(f"(()=>{{const e=[...document.querySelectorAll({SN})].find(x=>x.innerText.trim()==={json.dumps(l)}); e.click();}})()"); time.sleep(.35)
            ind=J(f"(()=>{{const g=document.querySelector({SI}); return g?[g.getAttribute('aria-label'),g.innerText.replace(/\\s+/g,' ')]:null;}})()")
            bar=J(f"(()=>{{const g=document.querySelector({SI}); if(!g) return ''; let p=g; for(let i=0;i<3;i++) p=p.parentElement; return p.innerText.replace(/\\s+/g,' ').slice(0,260);}})()")
            sh=J("document.documentElement.scrollHeight")
            print(('FULL ' if full else 'NORM ')+l, '|', ind, '| sh', sh)
            print('      barra:', bar)
finally:
    c.close(); srv.terminate()
