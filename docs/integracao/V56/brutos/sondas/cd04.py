# sonda: CD-04 Pessoas a 1440 px — largura da grade, de cada coluna e a célula mais larga de cada coluna
import sys, os, json, time
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
p, srv = servir(os.path.join(G, '_render')); c = Chrome(); J = c.js
try:
    c.aparelho(1440, 900, 1, False); c.goto(f'http://127.0.0.1:{p}/CD-04.dc.html', 1.4)
    J("(()=>{const b=[...document.querySelectorAll('[role=tab]')].find(b=>b.offsetParent&&b.innerText.trim().startsWith('Pessoas')); b&&b.click();})()"); time.sleep(.8)
    r = J(r"""(()=>[...document.querySelectorAll('.g2rola')].filter(r=>r.offsetParent).map(r=>{const t=r.querySelector('[role=table]');
      const hs=[...t.querySelectorAll('[role=columnheader]')]; const rows=[...t.querySelectorAll('[role=row]')].filter(x=>x.querySelector('[role=cell]'));
      return {cw:r.clientWidth, sw:r.scrollWidth, cols:getComputedStyle(t).gridTemplateColumns||getComputedStyle(rows[0]||t).gridTemplateColumns,
        heads:hs.map((h,i)=>{ const w=Math.round(h.getBoundingClientRect().width); let mx=['',0]; rows.forEach(x=>{ const c=x.querySelectorAll('[role=cell]')[i]; if(!c) return; const sp=document.createRange(); sp.selectNodeContents(c); const ww=Math.round(sp.getBoundingClientRect().width); if(ww>mx[1]) mx=[c.innerText.replace(/\s+/g,' ').trim().slice(0,60),ww]; });
          return [h.textContent.replace(/[⇅▾▴▼▲]/g,'').replace(/\s+/g,' ').trim(), w, mx]; }),
        nomes: rows.map(x=>(x.querySelector('[role=cell]')||{}).innerText||'').map(s=>s.replace(/\s+/g,' ').trim().slice(0,40))};}))()""")
    print(json.dumps(r, ensure_ascii=False, indent=1))
finally:
    c.close() if hasattr(c, 'close') else None
