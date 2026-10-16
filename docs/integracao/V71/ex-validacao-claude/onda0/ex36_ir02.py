import json,time,re
from o0lib import S,clicaT,VIS
s=S()
try:
  s.reset('Ana'); s.ir('IR-02.dc.html',2.2)
  rows=s.J("[...document.querySelectorAll('[role=row]')].map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,260))")
  for r in rows:
    if re.search(r'\b[0-5],\d+ mm|\b2 mm|percent|%', r): print(' ',r)
  s.shot('ex36_ir02_lista')
  t=s.texto(); print('linhas com mm/%:',[l for l in t.split('\n') if re.search(r'mm',l) and re.search(r'%|passad',l)][:15])
finally: s.fim()
