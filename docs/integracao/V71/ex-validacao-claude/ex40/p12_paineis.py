# -*- coding: utf-8 -*-
"""EX-26 (parte comum) · nos painéis do menu: o número abre a lista filtrada? há soma repetida? há linha "nada a fazer agora"? (executado)"""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S
s = S(1440, 1400); s.reset('Ana')
for f in ('PAGR', 'PMAN', 'PSUP', 'PCOM'):
    s.go(f + '.dc.html', espera=1.6); time.sleep(.5)
    d = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); const vis=e=>e.getClientRects().length>0;
      const cards=[...document.querySelectorAll('.pn-card')].filter(vis).map(c=>({t:n((c.querySelector('h2')||{}).innerText), v:n((c.querySelector('.pn-value')||{}).innerText), link:!!(c.querySelector('a[href]')||c.closest('a[href]')), href:(c.querySelector('a[href]')||c.closest('a[href]')||{getAttribute:()=>''}).getAttribute('href')}));
      const chart=[...document.querySelectorAll('.pn-row')].filter(vis).map(r=>n(r.innerText));
      const kpi=[...document.querySelectorAll('[role=group][aria-label=Indicadores] > div')].filter(vis).map(c=>({t:n(c.innerText).slice(0,80), link:!!c.querySelector('a[href]')}));
      const nums=[...document.querySelectorAll('main *')].filter(e=>vis(e)&&e.children.length===0&&/^\\s*[\\d.,]+( ?%| ?ha| ?sc| ?kg| R\\$\\/ha)?\\s*$/.test(e.textContent)&&!e.closest('table,[role=grid],[role=table]'));
      const numLink=nums.filter(e=>e.closest('a[href],button')).length;
      return {cards,chart,kpi,nums:nums.length,numLink,nada:(document.body.innerText.match(/nada a fazer agora/g)||[]).length};})()""")
    s.p(f'## {f}: ' + json.dumps(d, ensure_ascii=False))
s.p(f"erros JS: {s.errs()}")
s.fim('p12_paineis.log')
