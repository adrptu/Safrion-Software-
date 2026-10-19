import json,time,re
from o0lib import S,clicaT,VIS
s=S()
try:
  s.reset('Ana'); s.ir('IR-02.dc.html',2.2)
  r=s.J("(()=>{const e=[...document.querySelectorAll('select')].find(x=>[...x.options].some(o=>o.text==='Lagoa Grande')); if(!e) return 'sem'; const o=[...e.options].find(o=>o.text==='Lagoa Grande'); e.value=o.value; e.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})()"); time.sleep(.8); print('filtro LG',r)
  print(clicaT(s,'Programar irrigação')); time.sleep(.6)
  sel=s.J("(()=>{"+VIS+"const d=[...document.querySelectorAll('aside,[role=dialog]')].filter(vis).pop(); const e=d&&d.querySelector('select'); return e?[...e.options].map(o=>o.value+'='+o.text):null;})()")
  print('setores:',sel)
  for alvo in ['Pivô 19','Pivô 22','Pivô 6']:
    v=s.J("((a)=>{"+VIS+"const d=[...document.querySelectorAll('aside,[role=dialog]')].filter(vis).pop(); const e=d&&d.querySelector('select'); if(!e) return 'sem'; const o=[...e.options].find(o=>o.text.indexOf(a+' ')===0); if(!o) return 'sem '+a; e.value=o.value; e.dispatchEvent(new Event('change',{bubbles:true})); return o.text;})(%s)"%json.dumps(alvo)); time.sleep(.5)
    print('--',v); tx=(s.J("(()=>{"+VIS+"const a=[...document.querySelectorAll('aside,[role=dialog]')].filter(vis).pop(); return a?n(a.innerText):null;})()") or ''); i=tx.find('DÉFICIT'); print(tx[i:i+520])
  s.shot('ex36_ir02_lagoa')
finally: s.fim()
