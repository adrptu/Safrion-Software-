import json,time
from o0lib import S,clicaT,VIS
s=S()
SELS="(()=>{"+VIS+"return [...document.querySelectorAll('select')].filter(vis).filter(e=>!/perfil/.test(e.getAttribute('aria-label')||'')).map(e=>{const lab=document.querySelector('label[for=\"'+e.id+'\"]'); return (lab?lab.innerText:e.getAttribute('aria-label'))+' = '+e.value+' :: '+[...e.options].map(o=>o.text).join(' | ');});})()"
try:
  for pg in ['PT-05det.dc.html']:
    s.reset('Ana'); s.ir(pg,1.6); print(pg,'ctx:',s.J("(document.querySelector('header')||{}).innerText.replace(/\\s+/g,' ').slice(0,120)"))
    print(clicaT(s,'Enviar documento da carga 3')); print(json.dumps(s.J(SELS),ensure_ascii=False)); s.shot('ex35_pt05det_tipo')
finally: s.fim()
