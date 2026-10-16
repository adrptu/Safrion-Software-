import sys,json,time
from o0lib import S,VIS
s=S()
LIST="(()=>{"+VIS+"return [...document.querySelectorAll('main button, main [role=button], header button')].filter(vis).filter(e=>!/^(Ordenar|Filtrar|Recolher|Expandir|Colunas|Agrupar|Trocar perfil|Voltar|Regras)/.test(e.getAttribute('aria-label')||'')&&!e.closest('[role=columnheader],thead,nav,[role=tablist],[role=toolbar]')).map((e,i)=>n(e.innerText)||('['+(e.getAttribute('aria-label')||e.title||'')+']'));})()"
CLICK="((i)=>{"+VIS+"const L=[...document.querySelectorAll('main button, main [role=button], header button')].filter(vis).filter(e=>!/^(Ordenar|Filtrar|Recolher|Expandir|Colunas|Agrupar|Trocar perfil|Voltar|Regras)/.test(e.getAttribute('aria-label')||'')&&!e.closest('[role=columnheader],thead,nav,[role=tablist],[role=toolbar]')); const e=L[i]; if(!e) return 'sem'; e.click(); return 'ok';})"
SELS="(()=>{"+VIS+"return [...document.querySelectorAll('select')].filter(vis).map(e=>{const lab=document.querySelector('label[for=\"'+e.id+'\"]'); return {l:n(lab?lab.innerText:e.getAttribute('aria-label')),v:e.value,o:[...e.options].map(o=>o.text).filter(x=>!/^─|Buscar no cadastro|\\+ Novo/.test(x))};});})()"
pgs=sys.argv[1:]
try:
  for pg in pgs:
    perf='Ana'
    s.reset(perf); s.ir(pg,1.6); base=json.dumps(s.J(SELS)); L=s.J(LIST); print('#####',pg,len(L),'botões')
    vistos=set()
    for i,b in enumerate(L):
      if b in vistos: continue
      vistos.add(b)
      s.ir(pg,0.9); s.J(CLICK+"(%d)"%i); time.sleep(.6)
      d=s.J(SELS); novos=[x for x in d if json.dumps(x) not in base]
      if novos: print('--',b[:60],'→',json.dumps(novos,ensure_ascii=False)[:1500])
finally: s.fim()
