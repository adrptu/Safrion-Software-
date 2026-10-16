import json,time
from o0lib import S,clicaT,VIS
s=S()
SELS="(()=>{"+VIS+"return [...document.querySelectorAll('select')].filter(vis).map(e=>{const lab=document.querySelector('label[for=\"'+e.id+'\"]'); return (lab?lab.innerText:e.getAttribute('aria-label'))+' = '+e.value+' :: '+[...e.options].map(o=>o.text).slice(0,8).join(' | ');});})()"
try:
  s.reset('Ana'); s.ir('AG-01.dc.html',1.6)
  print('filtro fazenda:',s.J("(()=>{const e=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||[...document.querySelectorAll('[aria-label=\"Filtrar por fazenda\"]')][0]; return e?(e.value||e.innerText):null;})()"))
  b=s.J("(()=>{const e=document.querySelector('header')&&[...document.querySelectorAll('header button, main > div button')].find(x=>x.innerText.trim()==='Programar vistoria'); return e?'header':'?';})()")
  print('primária:',clicaT(s,'Programar vistoria')); print(json.dumps(s.J(SELS),ensure_ascii=False)); s.shot('ex35_ag01_prim_todas')
  # filtro Santa Rita
  s.ir('AG-01.dc.html',1.6)
  r=s.J("(()=>{const e=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); if(!e) return 'sem select'; const o=[...e.options].find(o=>o.text==='Santa Rita'); e.value=o.value; e.dispatchEvent(new Event('change',{bubbles:true})); return e.value;})()")
  time.sleep(.6); print('filtro→',r); print('linhas:',s.J("[...document.querySelectorAll('[role=row]')].slice(1,4).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,120))"))
  print('primária:',clicaT(s,'Programar vistoria')); print(json.dumps(s.J(SELS),ensure_ascii=False)); s.shot('ex35_ag01_prim_santarita')
finally: s.fim()
