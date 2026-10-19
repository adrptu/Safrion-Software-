import os, sys, time, json
GEN=os.environ['GEN37']; sys.path.insert(0,GEN)
from comp_lib import Chrome, servir
R=os.environ['RENDER_DIR']; p,srv=servir(R); c=Chrome(); J=c.js; U=lambda x:f'http://127.0.0.1:{p}/{x}'
SH=os.environ.get('SHOTS'); os.makedirs(SH,exist_ok=True); W=int(os.environ.get('W','1440'))
D="document.querySelector('[role=dialog][aria-label=\"Agrupamento de operações\"]')"
def botoes(): return J("[...(%s).querySelectorAll('button,[role=menuitem]')].filter(b=>b.getClientRects().length).map(b=>b.textContent.trim().slice(0,70)).join(' | ')"%D)
def clica(rx):
    ok=J("(()=>{const b=[...(%s).querySelectorAll('button')].find(b=>new RegExp(%s).test(b.textContent)&&b.getClientRects().length&&!b.disabled); if(!b) return false; b.focus(); return true})()"%(D,json.dumps(rx)))
    if ok: c.tecla('Enter','Enter',13,'\r'); time.sleep(.8)
    return ok
def texto(): return J("(%s||{}).innerText||''"%D).replace('\n',' | ')
try:
  c.aparelho(W,1000 if W>400 else 844,1 if W>400 else 2,W<400)
  c.goto(U('Main.dc.html'),.3); J("localStorage.clear();sessionStorage.clear()"); c.goto(U('OS.dc.html'),1.5)
  J("[...document.querySelectorAll('button,a')].find(b=>/Agrupar operações compatíveis/.test(b.textContent)&&b.getClientRects().length).click()"); time.sleep(1)
  print('E0 botoes:',botoes())
  print('E1 escolher grupo:',(clica('^Agrupar estas') or clica('Sulfato de magnésio'))); c.shot(f'{SH}/e1_grupo_{W}.png'); print('E1 texto:',texto()[:1500]); print('E1 botoes:',botoes())
  print('E1b conferir agrupamento:',clica('^Conferir agrupamento')); print('  botoes:',botoes()[:500]); c.shot(f'{SH}/e1b_conferir_{W}.png')
  print('E1c confirmar agrupamento:',clica('^Confirmar agrupamento')); time.sleep(.6); print('  texto:',texto()[:1800]); print('  botoes:',botoes()[:500]); c.shot(f'{SH}/e1c_criado_{W}.png')
  for i in range(3):
    a=clica('^(Revisar aprovação|Aprovar)'); print(f'E2.{i} revisar:',a); print('  botoes:',botoes()[:400])
    b=clica('^Aprovar OS'); print(f'E2.{i} confirmar:',b); print('  texto:',texto()[:300])
  c.shot(f'{SH}/e2_aprovadas_{W}.png')
  print('E3 conferir liberar:',clica('Conferir liberação|Liberar as')); print('  botoes:',botoes()[:400])
  print('E3 liberar:',clica('^Liberar as')); time.sleep(1); c.shot(f'{SH}/e3_liberadas_{W}.png'); print('E3 texto:',texto()[:2500])
  print('erros JS:',J("(window.__errosJS||[]).length") if J("typeof window.__errosJS!=='undefined'") else 'n/d')
finally:
  c.close(); srv.terminate()
