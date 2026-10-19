import json,time
from o0lib import S,cen,clicaT,preenche
s=S()
def dlg(tag):
    print('  diálogo:',(s.dialogo() or '')[:600]); print('  campos:',json.dumps(s.campos(),ensure_ascii=False)[:1500])
try:
  # LO-02det lacre
  s.reset('Ana'); s.ir('LO-02det.dc.html',1.6); print('\n== LO-02det')
  print('  clica:',clicaT(s,'Registrar lacre')); dlg('lacre'); s.shot('ex34_lo02det_form')
  print('  preenche:',preenche(s,{'Nº do lacre':'LC-000001'}))
  print('  salvar:',clicaT(s,'Salvar',raiz='[role=dialog]')); print('  toast:',s.toast())
  print('  linha:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/Lacre/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,240))")); s.shot('ex34_lo02det_salvo')
  # SU-07det quantidade medida
  s.reset('Rui'); s.ir('SU-07det.dc.html',1.6); print('\n== SU-07det (Rui)')
  print('  clica:',clicaT(s,'Receber devolução')); dlg('rec'); s.shot('ex34_su07det_form')
  print('  confirmar sem mexer:',clicaT(s,'Confirmar recebimento',raiz='[role=dialog]')); print('  toast:',s.toast()); s.shot('ex34_su07det_confirmado')
  # PL-02 pendência vencida
  s.reset('Ana'); s.ir('PL-02.dc.html',1.6); print('\n== PL-02')
  print('  clica:',clicaT(s,'Decidir pendência')); dlg('pend'); s.shot('ex34_pl02_form')
  print('  salvar sem evidência:',clicaT(s,'Salvar',raiz='[role=dialog]')); print('  toast:',s.toast()); print('  diálogo ainda:',(s.dialogo() or '')[:300])
  # MB-04
  s.reset('Ana'); s.ir('MB-04.dc.html',1.6); print('\n== MB-04')
  print('  estado tipo:',s.J("[...document.querySelectorAll('button')].filter(e=>/^Tipo: /.test(e.title)).map(e=>e.innerText.trim()+'='+(e.getAttribute('aria-pressed')||e.getAttribute('aria-checked')||e.getAttribute('aria-selected')||''))"))
  print('  estado máquina:',s.J("[...document.querySelectorAll('button')].filter(e=>/^Máquina: /.test(e.title)).map(e=>e.innerText.trim()+'='+(e.getAttribute('aria-pressed')||e.getAttribute('aria-checked')||e.getAttribute('aria-selected')||''))"))
  t=s.texto(); print('  textos:',[l for l in t.split('\n') if 'máquina' in l.lower() or 'Manutenção' in l][:6]); s.shot('ex34_mb04_inicial')
  print('  registrar sem nada:',clicaT(s,'Registrar ocorrência')); print('  toast:',s.toast())
  print('  erros',s.erros())
finally: s.fim()
