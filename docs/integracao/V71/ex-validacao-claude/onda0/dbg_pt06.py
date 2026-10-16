import json,time
from o0lib import S,clicaT,VIS
s=S()
try:
  for pg,b in [('PT-06.dc.html','Criar ação interna'),('PL-06.dc.html','Simular parcelas')]:
    s.reset('Ana'); s.ir(pg,1.6)
    print(pg,'clica',clicaT(s,b))
    print(s.J("(()=>{"+VIS+"return [...document.querySelectorAll('select')].filter(vis).map(e=>{const lab=document.querySelector('label[for=\"'+e.id+'\"]'); return (lab?lab.innerText:e.getAttribute('aria-label'))+' = '+e.value+' :: '+[...e.options].map(o=>o.text).join(' | ');});})()"))
    print('ctx:',s.J("(()=>{const h=document.querySelector('header'); return h?h.innerText.replace(/\\s+/g,' ').slice(0,300):'';})()"))
    s.shot('ex35_'+pg.split('.')[0]+'_drawer')
  s.reset('Ana'); s.ir('AG-01.dc.html',1.6); print('AG-01 ctx:',s.J("(()=>{const h=document.querySelector('header'); return h?h.innerText.replace(/\\s+/g,' ').slice(0,300):'';})()"))
  print('AG-01 título/linhas:',s.J("[...document.querySelectorAll('[role=row]')].slice(0,5).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,140))"))
  print(clicaT(s,'Programar vistoria')); s.shot('ex35_AG-01_programar')
  print('fazenda no topo:',s.J("[...document.querySelectorAll('button,select')].filter(e=>/Fazenda|Santa Rita|Boa Vista|Lagoa/.test((e.innerText||'')+(e.getAttribute('aria-label')||'')+(e.value||''))).map(e=>(e.innerText||e.value||'').replace(/\\s+/g,' ').slice(0,60)+' ['+(e.getAttribute('aria-label')||'')+']').slice(0,6)"))
finally: s.fim()
