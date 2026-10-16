import json,time
from o0lib import S,cen,clicaT,preenche
s=S()
try:
  s.reset('Ana'); s.ir('CD-04.dc.html',1.8)
  rows=s.J("[...document.querySelectorAll('[role=row]')].map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,160)).slice(0,20)"); print('\n'.join(rows))
  ls0=s.ls()
  # abrir Caio (ou Carlos)
  alvo=s.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(e=>/^\\s*(Caio|Carlos)\\b/.test(e.innerText)); if(!r) return null; const c=r.querySelector('[role=gridcell],td')||r; c.click(); return r.innerText.split('\\n')[0];})()")
  time.sleep(.8); print('abriu:',alvo); print('diálogo:',(s.dialogo() or '')[:900])
  cb=s.J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); if(!d) return 'sem'; const l=[...d.querySelectorAll('label,[role=checkbox],[role=option],button')].filter(e=>e.getClientRects().length&&/Liberar O\\.S\\. \\(agrônomo\\)/.test(e.innerText||e.getAttribute('aria-label')||'')); if(!l.length) return 'sem opção'; l[0].click(); return 'marcou: '+(l[0].tagName)+' '+(l[0].getAttribute('aria-checked')||l[0].getAttribute('aria-selected')||'');})()")
  time.sleep(.6); print('checkbox agrônomo:',cb); print('diálogo depois:',(s.dialogo() or '')[:1200]); s.shot('ex33_cd04_marcado')
  print('salvar:',clicaT(s,'Salvar',raiz='[role=dialog]')); print('toast:',s.toast()); time.sleep(.5)
  print('linha:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/^\\s*(Caio|Carlos)\\b/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,300))"))
  s.shot('ex33_cd04_salvo')
  ls1=s.ls(); print('chaves mudadas:',[k for k in ls1 if ls0.get(k)!=ls1.get(k)])
  s.ir('CD-04.dc.html',1.8); print('após recarga:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/^\\s*(Caio|Carlos)\\b/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,300))"))
  # CF-01: papéis de Caio
  s.ir('CF-01.dc.html#pessoa=Caio',2.0)
  t=s.texto(); print('CF-01 trechos agrônomo:',[l for l in t.split('\n') if 'grônom' in l or 'CREA' in l][:10])
  dis=s.J("[...document.querySelectorAll('input[type=checkbox],[role=switch],[role=checkbox]')].filter(e=>e.getClientRects().length).map(e=>{const L=(e.closest('label')||e.parentElement).innerText.replace(/\\s+/g,' ').slice(0,80); return L+' · dis='+(e.disabled||e.getAttribute('aria-disabled'))+' · on='+(e.checked||e.getAttribute('aria-checked'))+' · t='+(e.title||(e.closest('label')||{}).title||'');}).slice(0,30)")
  print('CF-01 controles:',json.dumps(dis,ensure_ascii=False)[:2500]); s.shot('ex33_cf01_caio')
  print('erros',s.erros())
finally: s.fim()
