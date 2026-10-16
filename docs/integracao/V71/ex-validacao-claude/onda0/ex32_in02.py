import json,time
from o0lib import S,cen
s=S()
SEL="(()=>{const e=[...document.querySelectorAll('input[type=checkbox],[role=checkbox],button')].filter(x=>x.getClientRects().length).find(x=>/Selecionar as \\d+ linhas/.test(x.getAttribute('aria-label')||x.title||x.innerText||'')); if(!e) return 'sem'; e.click(); return (e.getAttribute('aria-label')||'');})()"
try:
  for perf in ['Caio','Ana']:
    s.reset(perf); s.ir('IN-02.dc.html',1.6)
    print('== perfil',perf)
    print('linhas:',s.J("[...document.querySelectorAll('[role=row]')].map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,140)).slice(0,8)"))
    ls0=s.ls()
    print('sel todas:',s.J(SEL)); time.sleep(.5)
    print(s.clica('Aprovar selecionados')); print('toast:',s.toast())
    print('linhas depois:',s.J("[...document.querySelectorAll('[role=row]')].map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,140)).slice(1,6)"))
    s.shot(f'ex32_in02_{perf}')
    ls1=s.ls(); print('keys:',list(ls1.keys()))
    for k in ls1:
      if ls0.get(k)!=ls1.get(k): print('  mudou',k,str(ls1[k])[:300])
    s.ir('IN-02.dc.html',1.6)
    print('apos recarga:',s.J("[...document.querySelectorAll('[role=row]')].map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,140)).slice(1,6)"))
    # SU-09: ajuste de inventário segue pendente?
    s.ir('SU-09.dc.html',1.6)
    t=s.texto(); import re
    print('SU-09 trechos:', [l for l in t.split('\n') if 'Galpão 2' in l or 'Aguardando' in l or 'AJ-' in l][:8])
  print('erros',s.erros())
finally: s.fim()
