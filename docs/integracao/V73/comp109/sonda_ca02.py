import sys, os, time, json
G=os.environ['GEN37']; sys.path.insert(0,G)
from cada_lib import T
t=T(); J=t.J
def rows(): return J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,150))")
def selo(): return J("(()=>{const h=document.querySelector('h1'); const s=h&&h.parentElement?h.parentElement.innerText:''; return s.replace(/\\s+/g,' ').slice(0,160)})()")
try:
  t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Paula'); 1")
  t.goto('CA-02.dc.html'); time.sleep(.6)
  r=rows(); print('A primeiras linhas:'); [print('   ',x) for x in r[:4]]; print('A últimas:', r[-1][:120])
  print('A cabeçalho:', t.header()[-140:]); print('A sem kpis:', 'PROVISÓRIOS' not in t.bloco().upper()[:200] and 'Sobras a receber' not in t.bloco())
  print('B primária:', t.clk('Revisar próximo apontamento')); time.sleep(.4); print('B form:', t.title())
  t.fset('decisao','Conferir dia'); t.btn('Salvar'); time.sleep(.6); print('B toast:', t.toast()); print('B cabeçalho:', t.header()[-100:])
  print('B primeiras:', rows()[:3])
  t.c.size(390,844); t.goto('CA-02.dc.html'); time.sleep(.5); print('C 390 rolagem horizontal:', J("document.documentElement.scrollWidth>document.documentElement.clientWidth+1"), '| primária visível:', J("[...document.querySelectorAll('button')].some(b=>/Revisar próximo/.test(b.innerText)&&b.getClientRects().length)"))
  t.c.size(1440,1100); t.goto('CA-02.dc.html'); time.sleep(.4)
  f=J("(()=>{const b=[...document.querySelectorAll('header button')].find(x=>/Revisar próximo/.test(x.innerText)); if(!b) return 'sem'; b.focus(); return document.activeElement===b})()"); print('D foco:', f)
  [t.c.call('Input.dispatchKeyEvent',dict(type=tp,key='Enter',code='Enter',windowsVirtualKeyCode=13,nativeVirtualKeyCode=13,**({'text':'\r'} if tp=='keyDown' else {}))) for tp in ('keyDown','keyUp')]; time.sleep(.4); print('D Enter abre:', t.title())
  print('erros JS:', t.errs())
finally:
  try: t.c.close()
  except Exception: pass
  t.srv.terminate()
