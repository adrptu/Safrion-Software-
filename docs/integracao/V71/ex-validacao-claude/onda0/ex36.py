import json,time
from o0lib import S,clicaT,VIS
s=S()
def irr(): 
    t=s.J("localStorage.getItem('talhao-os-irrigacao-v1')"); return json.loads(t) if t else None
def osx(st,i):
    o=(st or {}).get('ordens',{}).get(i) if st else None
    return None if not o else {k:o.get(k) for k in ('etapa','conf','passadas')}
def aside(): return s.J("(()=>{"+VIS+"const a=[...document.querySelectorAll('[role=dialog],aside')].filter(vis).filter(e=>/Conferir medição|término|Término|Informar leitura/.test(e.innerText)).pop(); return a?n(a.innerText).slice(0,900):null;})()")
def inputs(): return s.J("(()=>{"+VIS+"return [...document.querySelectorAll('input')].filter(vis).filter(e=>/tm_|cm_/.test(e.id)||e.type==='radio').map(e=>e.id+'|'+e.type+'|'+(e.type==='radio'?e.checked:e.value)+'|'+n((e.closest('label')||{}).innerText||''));})()")
try:
  # IR-01 · OS-0394 em conferência (−3,8 %)
  s.reset('Ana'); s.ir('IR-01.dc.html',2.0); print('== IR-01')
  print('  linha A conferir:',s.J("[...document.querySelectorAll('[role=row]')].filter(e=>/conferir|Conferir|OS-0394/.test(e.innerText)).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,250)).slice(0,3)"))
  print('  clica:',clicaT(s,'Conferir medição')); time.sleep(.5); print('  painel:',aside()); print('  inputs:',inputs()); s.shot('ex36_ir01_painel')
  b=irr(); print('  antes OS-0394:',json.dumps(osx(b,'OS-0394'),ensure_ascii=False)[:400])
  print('  validar:',clicaT(s,'Validar e encerrar')); print('  toast:',s.toast()); a=irr(); print('  depois OS-0394:',json.dumps(osx(a,'OS-0394'),ensure_ascii=False)[:400]); s.shot('ex36_ir01_validado')
  # IR-03det · OS-0419: ponta e término
  s.reset('Ana'); s.ir('IR-03det.dc.html',2.0); print('\n== IR-03det')
  t=s.texto(); print('  menções a ponta antes:',[l for l in t.split('\n') if 'onta' in l][:5]); print('  janela:',[l for l in t.split('\n') if '20:0' in l][:5])
  print('  iniciar:',clicaT(s,'Iniciar irrigação')); print('  toast:',s.toast()); s.shot('ex36_ir03det_iniciada')
  t=s.texto(); print('  menções a ponta depois:',[l for l in t.split('\n') if 'onta' in l][:5])
  print('  botões:',[x for x in s.botoes() if 'érmino' in x or 'vanço' in x or 'ausar' in x])
  print('  término:',clicaT(s,'Confirmar término')); time.sleep(.4); print('  painel:',aside()); print('  inputs:',inputs()); s.shot('ex36_ir03det_termino_painel')
  print('  confirmar padrão:',clicaT(s,'Confirmar término',raiz='[role=dialog]') if s.J("!!document.querySelector('[role=dialog]')") else clicaT(s,'Confirmar término',idx=1)); print('  toast:',s.toast())
  st=irr(); print('  OS-0419:',json.dumps(osx(st,'OS-0419'),ensure_ascii=False)[:600]); s.shot('ex36_ir03det_terminada')
  print('  crédito no balanço P2:',json.dumps(((st or {}).get('setores',{}).get('P2') or {}).get('bal',{}).get('ap',[]),ensure_ascii=False)[:500])
  print('  erros',s.erros())
finally: s.fim()
