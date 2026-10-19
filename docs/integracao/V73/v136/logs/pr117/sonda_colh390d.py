# Sonda 4: estrutura dos cartões recolhidos da COLH a 390 (cabeçalho do grupo, botão de expandir, cartão de talhão).
import os, sys, time, json
G = os.path.abspath(sys.argv[1]); sys.path.insert(0, G); os.environ.setdefault('CDP_GL', '1')
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
try:
    c.aparelho(390, 844, 2, True)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1"); c.goto(U('COLH.dc.html'), 1.4); time.sleep(1.2)
    print('cab', J("""(()=>{const e=[...document.querySelectorAll('*')].find(x=>x.children.length<4&&/SOJA · 7 TALHÕES/.test(x.textContent)&&x.getClientRects().length);
      if(!e) return 'nada'; const b=e.closest('button,[role=button],[aria-expanded]'); const a=[];let q=e;for(let i=0;i<6&&q;i++){a.push(q.tagName+'['+[...q.attributes].map(t=>t.name+'='+String(t.value).slice(0,30)).join(' ')+']');q=q.parentElement;} return JSON.stringify({b:b?b.outerHTML.slice(0,200):null,anc:a});})()"""))
    print('expandir', J("""(()=>{const b=[...document.querySelectorAll('button')].find(x=>/Expandir tudo/.test(x.innerText)&&x.getClientRects().length); if(!b) return 'sem'; b.click(); return b.outerHTML.slice(0,160);})()"""))
    time.sleep(1)
    print('C1 depois', J("""(()=>{const l=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/^C1$/.test(e.textContent.trim())&&e.getClientRects().length);
      return JSON.stringify(l.slice(0,3).map(e=>{const a=[];let q=e;for(let i=0;i<7&&q;i++){a.push(q.tagName+'.'+(q.className||'')+(q.getAttribute('role')?'@'+q.getAttribute('role'):'')+(q.dataset&&Object.keys(q.dataset).length?JSON.stringify(q.dataset):''));q=q.parentElement;}return a;}));})()"""))
finally:
    c.close(); srv.terminate()
