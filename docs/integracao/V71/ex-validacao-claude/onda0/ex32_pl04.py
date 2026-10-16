import json,time
from o0lib import S,cen
s=S()
try:
  for perf in ['Ana','Caio']:
    s.reset(perf); s.ir('PL-04.dc.html',1.5)
    print('== perfil',perf,s.perfil())
    print('botoes:',[b for b in s.botoes() if 'iber' in b or 'onferir' in b or 'Preparar' in b])
    ls0=s.ls(); print('ls antes:',list(ls0.keys()))
    print('clica Conferir:',s.clica('Conferir prontidão')); print('toast:',s.toast())
    print('clica Liberar prontas:',s.clica('Liberar prontas')); print('toast:',s.toast())
    s.shot(f'ex32_pl04_{perf}')
    ls1=s.ls(); print('ls depois:',list(ls1.keys()), 'mudou cenário?', ls0.get('talhao-os-cenario-v1')!=ls1.get('talhao-os-cenario-v1'))
    # estado da OS-0430 na tela O.S.
    s.ir('OS.dc.html',1.8)
    t=s.J("(()=>{const r=[...document.querySelectorAll('tr,[role=row]')].filter(e=>/OS-0430/.test(e.innerText)); return r.slice(0,3).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,300));})()")
    print('OS.dc linha OS-0430:',t)
    print('erros',s.erros())
finally: s.fim()
