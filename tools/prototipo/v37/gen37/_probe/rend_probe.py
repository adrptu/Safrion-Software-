import sys,os,time,subprocess,json
sys.path.insert(0,'.')
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory','_probe/lp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
def toast(): return J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
def fset(label,val):
    return J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith({json.dumps(label)})); if(!l) return 'sem '+{json.dumps(label)}; const i=document.getElementById(l.getAttribute('for')); const pr=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(pr,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event(i.tagName==='SELECT'?'change':'input',{{bubbles:true}})); return 'ok';}})()""")
def fval(label): return J(f"""(()=>{{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith({json.dumps(label)})); return l?document.getElementById(l.getAttribute('for')).value:'sem';}})()""")
try:
  c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
  print('erro js:',J("window.__err||''"))
  J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Abrir safra/.test(b.innerText.trim())); b.click();})()"); time.sleep(.4)
  J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[3].click()"); time.sleep(.4); k4a=J("(document.body.innerText.match(/[\\d.]+ ha trabalhados[^\\n]+/)||[''])[0]")
  J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
  xs=J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); return [...t.querySelectorAll('[role=row]')].slice(1).map(r=>{const c=r.querySelector('[role=cell] .g2pw'); return c?Math.round(c.getBoundingClientRect().left):null;});})()""")
  print('x do texto na 1ª coluna por linha:',xs)
  c.shot('_probe/rend_tabela.png')
  J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>/Trator T1 JD/.test(x.innerText)); r.click();})()"); time.sleep(.4)
  print('campos:',J("[...document.querySelectorAll('aside[role=dialog] label')].map(l=>l.innerText.trim()).join(' | ')"))
  print('rend_c inicial:',fval('Rendimento efetivo'),' custo/h:',fval('Custo por hora'))
  fset('Velocidade de trabalho','8'); time.sleep(.2); print('rend_c com 8 km/h:',fval('Rendimento efetivo'))
  c.shot('_probe/rend_form.png')
  J("(()=>{[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click();})()"); time.sleep(.5); print('toast:',toast())
  J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[3].click()"); time.sleep(.4); k4b=J("(document.body.innerText.match(/[\\d.]+ ha trabalhados[^\\n]+/)||[''])[0]")
  print('k4 antes:',k4a); print('k4 depois:',k4b)
  J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
  J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>/Máquina TSI/.test(x.innerText)); r.click();})()"); time.sleep(.4)
  print('TSI modo:',fval('Como obter'),' campos:',J("[...document.querySelectorAll('aside[role=dialog] label')].map(l=>l.innerText.trim()).join(' | ')"))
  fset('Como obter o rendimento','Largura × velocidade'); time.sleep(.2)
  J("(()=>{[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click();})()"); time.sleep(.4)
  print('erros ao trocar modo sem L/V/E:',J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')"))
finally:
  c.close(); srv.terminate()
