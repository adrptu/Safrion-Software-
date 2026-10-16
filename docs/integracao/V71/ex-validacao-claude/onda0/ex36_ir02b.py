import json,time,re
from o0lib import S,clicaT,VIS
s=S()
try:
  s.reset('Ana'); s.ir('IR-02.dc.html',2.2)
  print(s.texto()[:3000])
  print('----- programar')
  print(clicaT(s,'Programar irrigação')); time.sleep(.6)
  print((s.dialogo() or s.J("(()=>{"+VIS+"const a=[...document.querySelectorAll('aside,[role=dialog]')].filter(vis).pop(); return a?n(a.innerText):null;})()") or '')[:2500])
  s.shot('ex36_ir02_programar')
finally: s.fim()
