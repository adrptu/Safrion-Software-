import json,time
from o0lib import S,clicaT,preenche,cen,VIS
s=S()
try:
  s.reset('Rui'); s.ir('EST.dc.html',2.0)
  print('linhas NF:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/NF \\d+/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,200)).slice(0,6)"))
  r=s.J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(e=>/NF 4533/.test(e.innerText)); if(!r) return 'sem'; (r.querySelector('[role=gridcell]')||r).click(); return 'ok';})()"); time.sleep(.8)
  print('abriu NF 4533:',r); print('diálogo:',(s.dialogo() or '')[:500])
  print('campos:',json.dumps(s.campos(),ensure_ascii=False)[:1800]); s.shot('ex35_est_nf4533_form')
  c0=cen(s)
  opt=s.J("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].filter(e=>e.getClientRects().length).pop(); const sel=[...d.querySelectorAll('select')].find(e=>[...e.options].some(o=>/PC-096/.test(o.text))); if(!sel) return 'sem PC-096'; const o=[...sel.options].find(o=>/PC-096/.test(o.text)); sel.value=o.value; sel.dispatchEvent(new Event('change',{bubbles:true})); return o.text;})()")
  time.sleep(.5); print('troca pedido →',opt); print('campos depois:',json.dumps(s.campos(),ensure_ascii=False)[:1800])
  print('preenche:',preenche(s,{'Quantidade na nota':'1000','Quantidade conferida':'1000','Apta para uso':'1000','Em quarentena':'0','Lote':'S58-0926','Validade':'06/2027'}))
  time.sleep(.3); print('salvar:',clicaT(s,'Salvar',raiz='[role=dialog]')); time.sleep(.6); print('toast:',s.toast()); print('diálogo:',(s.dialogo() or '')[:400])
  s.shot('ex35_est_nf4533_pc096')
  c1=cen(s)
  if c1:
    novos=[m for m in c1.get('movs',[]) if m not in (c0 or {}).get('movs',[])]
    print('movs novos:',json.dumps(novos,ensure_ascii=False)[:800])
    print('lotes S58-0926:',{k:v for k,v in c1.get('lotes',{}).items() if 'S58-0926' in k})
  else: print('cenário não gravado')
  print('erros',s.erros())
finally: s.fim()
