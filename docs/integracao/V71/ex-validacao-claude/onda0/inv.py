import sys,json
from o0lib import S
s=S()
try:
  for pg in sys.argv[1:]:
    s.reset('Ana'); s.ir(pg,1.6)
    b=s.J("[...document.querySelectorAll('button,a,[role=button]')].filter(e=>e.getClientRects().length&&!e.closest('nav,.menu-lat,header [role=navigation]')).map(e=>((e.innerText||'').replace(/\\s+/g,' ').trim()||'')+(e.getAttribute('aria-label')?' [al='+e.getAttribute('aria-label')+']':'')+(e.title?' [t='+e.title+']':'')).filter(x=>x.trim())")
    print('#####',pg); print(' | '.join(x[:110] for x in b))
finally: s.fim()
