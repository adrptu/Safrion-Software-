# Sonda 5: depois de "Expandir tudo" na COLH a 390: captura e o contêiner dos cartões que mostram o talhão C1.
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); OUT = sys.argv[2]; sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
try:
    c.aparelho(390, 844, 2, True)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(U('COLH.dc.html'), 1.4); time.sleep(1.2)
    J("""[...document.querySelectorAll('button')].find(x=>/Expandir tudo/.test(x.innerText)&&x.getClientRects().length).click()"""); time.sleep(1.2)
    J("""(()=>{const e=[...document.querySelectorAll('*')].find(x=>x.children.length===0&&/(^|\\s)C1(\\s|$|·)/.test(x.textContent)&&x.getClientRects().length); if(e) e.scrollIntoView({block:'center'});})()"""); time.sleep(.5)
    c.shot(OUT)
    print(J("""(()=>{const l=[...document.querySelectorAll('*')].filter(x=>x.children.length===0&&/(^|\\s)C1(\\s|$|·)/.test(x.textContent)&&x.getClientRects().length);
      return JSON.stringify(l.slice(0,2).map(e=>{const a=[];let q=e;for(let i=0;i<8&&q;i++){a.push(q.tagName+'.'+(q.className&&q.className.baseVal===undefined?q.className:'')+(q.getAttribute('role')?'@'+q.getAttribute('role'):'')+(q.id?'#'+q.id:''));q=q.parentElement;}return [e.textContent.slice(0,60),a];}));})()"""))
finally:
    c.close(); srv.terminate()
