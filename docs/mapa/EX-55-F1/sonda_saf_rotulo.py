# Sonda: no SAF-MAPA, a 2ª linha do rótulo vem da camada HTML (.sm-l2), visível e sobre o talhão certo
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
try:
    c.aparelho(1440, 1000, 1, False)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear(); 1")
    c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&passo=cultivos', 2.0)
    J("(()=>{const b=[...document.querySelectorAll('button,a')].find(x=>x.getClientRects().length&&/Planejar no mapa/.test(x.innerText)); b&&b.click();})()")
    for _ in range(80):
        if J("!!document.querySelector('#sl-painel .sm-svg')"): break
        time.sleep(.1)
    time.sleep(.5)
    print(J("""JSON.stringify({l2:[...document.querySelectorAll('#sl-painel .sm-l2')].filter(e=>e.getClientRects().length).slice(0,6).map(e=>{const r=e.getBoundingClientRect();
      const g=document.elementsFromPoint(r.left+r.width/2,r.top+r.height/2).find(x=>x.classList&&x.classList.contains('sm-t'));return [e.innerText,Math.round(r.width),Math.round(r.height),getComputedStyle(e).color,g?g.dataset.t:null];}),
      n:[...document.querySelectorAll('#sl-painel .sm-l2')].filter(e=>e.getClientRects().length).length, txt:[...document.querySelectorAll('#sl-painel .sm-t text')].length,
      err:(window.__err||[]).slice(0,3)})"""))
    J("document.querySelector('#sl-painel .sm-svg').scrollIntoView({block:'center'})"); time.sleep(.3); c.shot(OUT)
finally:
    c.close(); srv.terminate()
