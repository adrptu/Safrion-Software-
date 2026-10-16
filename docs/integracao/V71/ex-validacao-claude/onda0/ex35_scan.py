import sys,json,time
from o0lib import S,VIS
s=S()
LIST="(()=>{"+VIS+"return [...document.querySelectorAll('main button, main [role=button], header button')].filter(vis).filter(e=>!/^(Ordenar|Filtrar|Recolher|Expandir|Colunas|Agrupar)/.test(e.getAttribute('aria-label')||'')&&!e.closest('[role=columnheader],thead,nav,[role=tablist],[role=toolbar]')).map((e,i)=>n(e.innerText)||('['+(e.getAttribute('aria-label')||e.title||'')+']'));})()"
CLICK="((i)=>{"+VIS+"const L=[...document.querySelectorAll('main button, main [role=button], header button')].filter(vis).filter(e=>!/^(Ordenar|Filtrar|Recolher|Expandir|Colunas|Agrupar)/.test(e.getAttribute('aria-label')||'')&&!e.closest('[role=columnheader],thead,nav,[role=tablist],[role=toolbar]')); const e=L[i]; if(!e) return 'sem'; e.click(); return 'ok';})"
SELS="(()=>{"+VIS+"const d=[...document.querySelectorAll('[role=dialog],aside[aria-label]')].filter(vis).filter(x=>x.querySelector('select,input')).pop(); if(!d) return null; return {t:n((d.querySelector('h2,h3')||{}).innerText||''),sel:[...d.querySelectorAll('select')].filter(vis).map(e=>{const lab=e.id&&d.querySelector('label[for=\"'+e.id+'\"]'); return {l:n((lab&&lab.innerText)||e.getAttribute('aria-label')||''),v:e.value,o:[...e.options].map(o=>o.text).filter(x=>!/^─|Buscar no cadastro|\\+ Novo/.test(x))};})};})()"
pg=sys.argv[1]; perf=sys.argv[2] if len(sys.argv)>2 else 'Ana'; filtro=sys.argv[3] if len(sys.argv)>3 else ''
try:
  s.reset(perf); s.ir(pg,1.6); L=s.J(LIST); print('#####',pg,len(L),'botões')
  for i,b in enumerate(L):
    if filtro and filtro not in b: continue
    s.ir(pg,1.0); r=s.J(CLICK+"(%d)"%i); time.sleep(.7)
    d=s.J(SELS)
    if d and d['sel']: print('--',b,'→',json.dumps(d,ensure_ascii=False)[:1600])
finally: s.fim()
