import json,time
from o0lib import S,cen,clicaT,VIS
s=S()
try:
  s.reset('Rui'); s.ir('EST.dc.html',2.0); print(clicaT(s,'Receba devoluções')); time.sleep(.6)
  r=s.J("(()=>{const rs=[...document.querySelectorAll('[role=row]')].filter(e=>/REQ-031/.test(e.innerText)); if(!rs.length) return 'sem'; const r=rs[0]; (r.querySelector('[role=gridcell]')||r).click(); return r.innerText.replace(/\\s+/g,' ').slice(0,220);})()"); time.sleep(.7)
  print('linha:',r); print('diálogo:',(s.dialogo() or '')[:500]); print('campos:',json.dumps(s.campos(),ensure_ascii=False)[:700])
  c0=cen(s); print('salvar sem mexer:',clicaT(s,'Salvar',raiz='[role=dialog]') if 'Salvar' in (s.dialogo() or '') else clicaT(s,'Receber',raiz='[role=dialog]')); time.sleep(.6); print('toast:',s.toast())
  c1=cen(s)
  if c1: print('movs novos:',json.dumps([m for m in c1.get('movs',[]) if m not in ((c0 or {}).get('movs',[]))],ensure_ascii=False)[:600])
  s.shot('ex34_est_devolucao_salva')
finally: s.fim()
