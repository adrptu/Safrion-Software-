# -*- coding: utf-8 -*-
"""EX47 · revisão Claude: a coluna de ações estrutural da grade sem exclusão e sem ação (g_cult_S2526, dados sintéticos) ocupa espaço?
Mede, a 1440 e a 390, o número de trilhas, a largura da última trilha e do último columnheader e o nome acessível dele. RENDER_DIR escolhe o _render."""
import os, sys, time, json
GEN = os.environ.get('GEN37') or os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(GEN, '_render')
p, srv = servir(R); c = Chrome(); J = c.js
try:
    for w in (1440, 390):
        c.aparelho(w, 1000 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .3); J("localStorage.clear();sessionStorage.clear()")
        c.goto(f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2526&etapa=2', .6)
        for _ in range(60):
            if J("document.querySelectorAll('[data-g2g=g_cult_S2526] [role=row]').length>=4"): break
            time.sleep(.15)
        m = J(r"""(()=>{ const t=document.querySelector('[role=table][data-g2g=g_cult_S2526]'); const tr=getComputedStyle(t).gridTemplateColumns.split(' ');
          const hd=t.querySelector('[role=row]'); const hs=[...hd.querySelectorAll('[role=columnheader]')].filter(x=>x.closest('[role=row]')===hd); const u=hs[hs.length-1];
          return {trilhas:tr.length, ultimaTrilha:tr[tr.length-1], ultimoCab:Math.round(u.getBoundingClientRect().width*10)/10, nome:(u.getAttribute('aria-label')||u.innerText||'').trim(),
                  cabs:hs.map(h=>(h.innerText||'').replace(/[⇅▾▴▲▼]/g,'').trim()), lado:document.documentElement.scrollWidth>innerWidth+1}; })()""")
        print(w, json.dumps(m, ensure_ascii=False), flush=True)
finally:
    c.close(); srv.terminate()
