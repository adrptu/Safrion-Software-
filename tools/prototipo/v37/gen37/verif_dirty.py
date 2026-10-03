import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
def ROW(ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"
def openrow(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.5)
def kb(ti,txt): J(f"(()=>{{const r={ROW(ti,txt)}; r.focus(); r.dispatchEvent(new KeyboardEvent('keydown',{{key:'Enter',bubbles:true}}));}})()"); time.sleep(.4)
try:
    c.size(1440,1100)
    for f,ti,row in [('CD-02.dc.html',1,'Pulverização'),('CD-02.dc.html',1,'Tratamento de sementes'),('CD-05.dc.html',0,'Sementes Vale'),('CD-01det.dc.html',0,'T1-B')]:
        c.goto(f'http://127.0.0.1:{p}/{f}',wait=1.2)
        openrow(ti,row); J(f"({BTN})('Cancelar')"); time.sleep(.3)
        print(f,row,'cancelar sem mudar → pede confirmação?', J("document.body.innerText.indexOf('Há alterações não salvas')>=0"), 'fechou?', J("!document.querySelector('aside[role=dialog]')"))
        J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
        kb(ti,row); print('  teclado abre?', J("!!document.querySelector('aside[role=dialog]')")); J(f"({BTN})('Cancelar')"); time.sleep(.2); J(f"({BTN})('Descartar alterações')"); time.sleep(.2)
        # salvar sem mudar
        openrow(ti,row); J(f"({BTN})('Salvar')"); time.sleep(.5); print('  salvar sem mudar fecha?', J("!document.querySelector('aside[role=dialog]')"), J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')"))
        print('  linha', J(f"(()=>{{const r={ROW(ti,row)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()"))
finally:
    c.close(); srv.terminate()
