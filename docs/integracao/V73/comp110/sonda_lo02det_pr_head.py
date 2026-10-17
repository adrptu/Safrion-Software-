import sys, os, time, json
G=os.environ['GEN37']; sys.path.insert(0,G)
from cada_lib import T
t=T(); J=t.J
CLK="""((t,root)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const sc=root?document.querySelector(root+'[role=dialog]')||document.querySelector(root):document; if(!sc) return 'sem raiz'; const els=[...sc.querySelectorAll('button,a,[role=radio],label')].filter(e=>e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
def clk(x,root=None): r=J(f"({CLK})({json.dumps(x)},{json.dumps(root)})"); time.sleep(.5); return r
def setv(sel,val): return J(f"(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return 'sem '+{json.dumps(sel)}; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return i.value}})()")
CG="(()=>{const k=Object.keys(localStorage).find(k=>/cenario/.test(k)); return k?JSON.parse(localStorage.getItem(k)):null})()"
def cg(expr): return J(f"(()=>{{const c={CG}; if(!c) return 'sem estado salvo'; return ({expr}); }})()")
def dlg(): return (J("(document.querySelector('[role=dialog]')||{}).innerText||'(fechado)'") or '')[:300].replace('\n',' | ')
try:
  t.goto('Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','Rui'); 1")
  t.goto('LO-02det.dc.html'); time.sleep(.6)
  print('A sem RM: cabeçalho:', t.header()[-160:]); print('A corpo:', t.bloco()[:300])
  print('A erros:', t.errs())
  J("localStorage.setItem('safrion.perfilDemo','Ana'); 1"); t.goto('VEN.dc.html'); time.sleep(1)
  print('B linha PV-030:', J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>/PV-030/.test(r.innerText)); if(!r) return 'sem'; (r.querySelector('.g2pw')||r).click(); return 'ok'})()")); time.sleep(.8)
  print('B 60kg:', clk('60 kg','aside'), 'registrar:', clk('Registrar a saca','aside')); time.sleep(.6); print('B toast saca:', t.toast()[:160])
  print('B reservar:', clk('Reservar','aside')); time.sleep(.6); print('B toast reserva:', t.toast()[:160])
  print('B ir programar:', clk('Programar carga do PV-030')); time.sleep(1.2)
  print('B veic:', clk('Bitrem graneleiro 37 t','aside'), 'placa:', setv('#pf_pl','QZA1B23'))
  print('B programar:', clk('Programar carga','aside')); time.sleep(.8); print('B toast:', t.toast()[:200])
  print('B RMs:', cg("JSON.stringify(Object.values((c.com||c.comercial||{}).expedicoes||{}).map(r=>[r.id,r.st]))"))
  J("localStorage.setItem('safrion.perfilDemo','Caio'); 1"); t.goto('LO-02det.dc.html'); time.sleep(.6)
  print('C Caio cabeçalho:', t.header()[-160:])
  print('C linhas ps:', J("[...document.querySelectorAll('[role=table]')].map(tb=>[...tb.querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,140)))"))
  rid=J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/RM-0/.test(r.innerText)); return r?r.innerText.replace(/\\s+/g,' ').slice(0,10):''})()")
  print('C RM linha:', rid)
  print('C abrir:', t.openrow(1, 'RM-0')); print('C form:', t.title(), '|', J("[...document.querySelectorAll('aside[role=dialog] input')].map(e=>e.id+'='+e.value)"))
  t.fset('bruto','15000'); t.fset('tara','5000'); t.btn('Salvar'); time.sleep(.6); print('C Caio salvar: alerts=', t.alerts()[:200], '| aberto=', t.isopen())
  J("localStorage.setItem('safrion.perfilDemo','Rui'); 1"); t.goto('LO-02det.dc.html'); time.sleep(.6)
  t.openrow(1,'RM-0'); campos=J("[...document.querySelectorAll('aside[role=dialog] input')].map(e=>e.id)"); print('D campos:', campos)
  t.fset('bruto','10'); t.fset('tara','20'); t.btn('Salvar'); time.sleep(.4); print('D tara>bruto: alerts=', t.alerts()[:160])
  # líquido = soma das reservas? usar líquido igual ao previsto
  prev=cg("(()=>{const r=Object.values((c.com||c.comercial||{}).expedicoes||{}).find(r=>r.st==='Programada'); return r?JSON.stringify(r.lotes):''})()"); print('D lotes previstos:', prev)
  lotes=json.loads(prev) if prev and prev.startswith('[') else []
  liq=sum(l.get('prev',0) for l in lotes)
  t.fset('bruto','52000'); t.fset('tara','15000')
  for i,l in enumerate(lotes):
    if len(lotes)>1: t.fset(f'kg_{i}', str(l.get('prev',0)))
  t.btn('Salvar'); time.sleep(.6); print('D Rui salvar: toast=', t.toast()[:220], '| alerts=', t.alerts()[:160], '| aberto=', t.isopen())
  print('D RMs:', cg("JSON.stringify(Object.values((c.com||c.comercial||{}).expedicoes||{}).map(r=>[r.id,r.st,r.saida&&r.saida.liq]))"))
  print('D cabeçalho:', t.header()[-160:])
  print('D movimentos:', J("[...document.querySelectorAll('[role=table]')][3]?[...document.querySelectorAll('[role=table]')[3].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,140)):'sem tabela'"))
  t.goto('LO-02det.dc.html'); time.sleep(.6); print('E recarregar cabeçalho:', t.header()[-120:]); print('E tabelas:', J("[...document.querySelectorAll('[role=table]')].map(tb=>[...tb.querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,120)))"))
  t.openrow(1,'RM-0'); print('E reabrir após saída:', t.isopen(), t.title())
  t.goto('Main.dc.html'); t.goto('LO-02det.dc.html#rm=RM-0002'); time.sleep(.6); print('F hash cabeçalho:', t.header()[-120:]); print('F tabelas:', J("[...document.querySelectorAll('[role=table]')].map(tb=>[...tb.querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,120)))"))
  t.openrow(1,'RM-0'); print('F abrir RM saída:', t.isopen(), t.title(), dlg()[:200])
  print('F movs RM-0002 no estado:', J("(()=>{const s=JSON.stringify(Object.fromEntries(Object.keys(localStorage).map(k=>[k,localStorage.getItem(k)]))); return (s.match(/MP-10\\d\\d/g)||[]).filter((x,i,a)=>a.indexOf(x)===i)})()"))
  for w,h in ((390,844),):
    t.c.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':True}); t.goto('Main.dc.html'); t.goto('LO-02det.dc.html#rm=RM-0002'); time.sleep(.6)
    print('G',w,'overflow:', J("document.documentElement.scrollWidth-document.documentElement.clientWidth"), 'botões fora:', J("[...document.querySelectorAll('button,a')].filter(e=>{const r=e.getBoundingClientRect(); return r.width&&(r.right>innerWidth+1)&&!e.closest('[style*=overflow]')}).map(e=>e.innerText.trim().slice(0,30)).slice(0,8)"))
  print('erros JS:', t.errs())
finally:
  try: t.c.close()
  except Exception: pass
  t.srv.terminate()
