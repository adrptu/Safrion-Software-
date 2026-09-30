import sys,os,time,subprocess,json
sys.path.insert(0,'.')
from cdp import Chrome
from journeys import free
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory','_probe/lp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
try:
  c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html',wait=1.3)
  J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/^Abrir safra/.test(b.innerText.trim())); b.click();})()"); time.sleep(.5)
  J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>/^T4/.test(x.innerText.trim())); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Dividir em parcelas').click();})()"); time.sleep(.4)
  for _ in range(3): J("(()=>{[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='+ Adicionar parcela').click();})()"); time.sleep(.25)
  J("(()=>{const i=[...document.querySelectorAll('aside input')].find(x=>x.getAttribute('aria-label')==='Variedade de T4-C'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'62 X'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.2)
  J("(()=>{const i=[...document.querySelectorAll('aside select')].find(x=>x.getAttribute('aria-label')==='Cultura de T4-E'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'Milho'); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
  c.shot('_probe/dv_painel.png')
  J("(()=>{[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Distribuir área igualmente').click();})()"); time.sleep(.3)
  J("(()=>{[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Salvar divisão').click();})()"); time.sleep(.6)
  c.shot('_probe/dv_tabela.png')
  c.size(1024,800); time.sleep(.3)
  J("(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>/^[▾▸]? ?T4 5 parcelas/.test(x.innerText.trim())); [...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Dividir em parcelas').click();})()"); time.sleep(.4)
  print(J("(()=>{const a=document.querySelector('aside[role=dialog]'); return {w:a.clientWidth, sw:a.scrollWidth, docsw:document.documentElement.scrollWidth};})()"))
  c.shot('_probe/dv_1024.png')
finally:
  c.close(); srv.terminate()
