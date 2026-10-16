import json,time
from o0lib import S,cen
s=S()
try:
  for perf in ['Ana','Caio']:
    s.reset(perf); s.ir('CA-01.dc.html',1.8)
    print('== perfil',perf)
    print('botoes c/ Selec/Liberar:',[b for b in s.botoes() if 'elecion' in b or 'iberar' in b or 'linhas' in b])
    print('checkboxes:',s.J("[...document.querySelectorAll('input[type=checkbox],[role=checkbox]')].filter(e=>e.getClientRects().length).map(e=>(e.getAttribute('aria-label')||e.title||'')).slice(0,16)"))
    ls0=s.ls()
    r=s.J("(()=>{const e=[...document.querySelectorAll('input[type=checkbox],[role=checkbox],button')].find(x=>/Selecionar as \\d+ linhas/.test(x.getAttribute('aria-label')||x.title||x.innerText||'')); if(!e) return 'sem'; e.click(); return (e.getAttribute('aria-label')||e.title||e.innerText);})()")
    print('selecionar todas:',r); time.sleep(.6)
    print('marcadas:',s.J("[...document.querySelectorAll('input[type=checkbox]')].filter(e=>e.checked).length"))
    print('botoes apos sel:',[b for b in s.botoes() if 'iberar' in b or 'elecion' in b or 'linhas' in b])
    r=s.J("(()=>{const e=[...document.querySelectorAll('button')].filter(x=>x.getClientRects().length).find(x=>/Liberar selecionadas|Liberar para execução as ordens selecionadas/.test((x.innerText||'')+' '+(x.getAttribute('aria-label')||'')+' '+(x.title||''))); if(!e) return 'sem botão'; e.click(); return 'ok '+(e.innerText||e.getAttribute('aria-label'));})()")
    print('liberar selecionadas:',r); time.sleep(.7); print('toast:',s.toast())
    s.shot(f'ex32_ca01_todas_{perf}')
    ls1=s.ls(); print('cenário mudou?',ls0.get('talhao-os-cenario-v1')!=ls1.get('talhao-os-cenario-v1'), list(ls1.keys()))
  # contraprova: só a OS-0415 (encerrada) selecionada
  s.reset('Ana'); s.ir('CA-01.dc.html',1.8)
  r=s.J("(()=>{const tr=[...document.querySelectorAll('[role=row],tr')].find(e=>/OS-0415/.test(e.innerText)); if(!tr) return 'sem linha'; const cb=tr.querySelector('input[type=checkbox],[role=checkbox]'); if(!cb) return 'sem cb'; cb.click(); return 'ok';})()")
  print('sel só OS-0415:',r); time.sleep(.5)
  r=s.J("(()=>{const e=[...document.querySelectorAll('button')].filter(x=>x.getClientRects().length).find(x=>/Liberar selecionadas|Liberar para execução as ordens selecionadas/.test((x.innerText||'')+' '+(x.getAttribute('aria-label')||'')+' '+(x.title||''))); if(!e) return 'sem botão'; e.click(); return 'ok';})()")
  print('liberar:',r); time.sleep(.6); print('toast só OS-0415:',s.toast()); s.shot('ex32_ca01_so0415')
  print('erros',s.erros())
finally: s.fim()
