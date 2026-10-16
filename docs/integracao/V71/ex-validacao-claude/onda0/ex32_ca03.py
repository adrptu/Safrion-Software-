import json,time
from o0lib import S,cen
s=S()
SEL="(()=>{const e=[...document.querySelectorAll('input[type=checkbox],[role=checkbox],button')].filter(x=>x.getClientRects().length).find(x=>/Selecionar as \\d+ linhas/.test(x.getAttribute('aria-label')||x.title||x.innerText||'')); if(!e) return 'sem'; e.click(); return (e.getAttribute('aria-label')||'');})()"
def selrow(oc): return s.J("(()=>{const cb=[...document.querySelectorAll('input[type=checkbox]')].find(e=>/%s/.test(e.getAttribute('aria-label')||'')); if(!cb) return 'sem'; cb.click(); return cb.getAttribute('aria-label');})()"%oc)
BULK="(()=>{const e=[...document.querySelectorAll('button')].filter(x=>x.getClientRects().length).find(x=>/Encerrar tratamento/.test((x.innerText||'')+' '+(x.getAttribute('aria-label')||'')+' '+(x.title||''))); if(!e) return 'sem botão'; e.click(); return 'ok';})()"
ROWS="[...document.querySelectorAll('[role=row]')].map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,200)).slice(1,7)"
try:
  s.reset('Ana'); s.ir('CA-03.dc.html',1.6)
  print('cbs:',s.J("[...document.querySelectorAll('input[type=checkbox]')].map(e=>e.getAttribute('aria-label'))"))
  print('sel todas:',s.J(SEL)); time.sleep(.4); print('bulk:',s.J(BULK)); time.sleep(.6); print('toast todas:',s.toast())
  print('linhas:',s.J(ROWS)); s.shot('ex32_ca03_todas')
  s.reset('Ana'); s.ir('CA-03.dc.html',1.6)
  print('sel OC-114:',selrow('OC-114')); time.sleep(.4); print('bulk:',s.J(BULK)); time.sleep(.6); print('toast só OC-114:',s.toast()); s.shot('ex32_ca03_so114')
  print('linhas:',s.J(ROWS))
  # EX-34: Registrar ocorrência
  s.reset('Ana'); s.ir('CA-03.dc.html',1.6)
  print('registrar:',s.clica('Registrar ocorrência')); time.sleep(.5)
  print('dialogo:',(s.dialogo() or '')[:600])
  print('campos:',json.dumps(s.campos(),ensure_ascii=False)[:1500])
  s.shot('ex34_ca03_form')
  # preencher o mínimo: local e relato
  r=s.J("""(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const set=(el,v)=>{const p=Object.getPrototypeOf(el); Object.getOwnPropertyDescriptor(p,'value').set.call(el,v); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));};
   const ins=[...d.querySelectorAll('input,textarea')].filter(e=>e.getClientRects().length&&!e.readOnly&&e.type!=='checkbox');
   const out=[]; ins.forEach(e=>{ if(!e.value){ set(e, e.tagName==='TEXTAREA'?'Teste de relato sintético':'T4 · OS-0420'); out.push(e.getAttribute('aria-label')||e.name||e.tagName);} }); return out;})()""")
  print('preenchidos:',r); time.sleep(.3)
  print('salvar:',s.J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const b=[...d.querySelectorAll('button')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim()); return b;})()"))
  for t in ['Registrar','Salvar','Registrar ocorrência']:
    r=s.clica(t,raiz='[role=dialog]')
    if r=='ok': print('clicou',t); break
  time.sleep(.6); print('toast:',s.toast()); print('linhas:',s.J(ROWS)); s.shot('ex34_ca03_salvo')
  # CA-03det
  s.ir('CA-03det.dc.html',1.6)
  r=s.J("(()=>{const e=[...document.querySelectorAll('button')].filter(x=>x.getClientRects().length).find(x=>/Encerrar tratamento|Encerrar o tratamento/.test((x.innerText||'')+' '+(x.getAttribute('aria-label')||'')+' '+(x.title||''))); if(!e) return 'sem botão'; e.click(); return 'ok';})()")
  time.sleep(.6); print('CA-03det encerrar:',r,s.toast())
  print('erros',s.erros())
finally: s.fim()
