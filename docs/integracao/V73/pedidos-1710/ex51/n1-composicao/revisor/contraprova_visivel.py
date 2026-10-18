# Contraprova N-1 pelo que a pessoa vê (sem ganchos de teste): emissão no AG-01, coleta no MB-06 e AG-01 com a cópia antiga ilegível.
import sys, os, time, subprocess, json
G=sys.argv[1]; sys.path.insert(0,G)
from cdp import Chrome
from journeys import free
R=G+'/_render'; p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js; c.size(1440,900); U=f'http://127.0.0.1:{p}/'
c.call('Page.addScriptToEvaluateOnNewDocument',{'source':"window.__errs=[];window.addEventListener('error',e=>window.__errs.push(String(e.message)));"})
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo'; const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
out={}
try:
    c.goto(U+'Main.dc.html',wait=0.8); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(U+'AG-01.dc.html#VIS-013:decidir',wait=1.8); time.sleep(.4)
    J("[...document.querySelectorAll('aside input[name=dc_prod]')][0].click()"); time.sleep(.3)
    J(f"({SETV})('aside #dc_dose','0,5')"); time.sleep(.3); J(f"({SETV})('aside input[aria-label=\"Data da aplicação\"]','2026-09-24')"); time.sleep(.3)
    J("[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==='Emitir receituário e gerar O.S.').click()"); time.sleep(.8)
    out['emitir_aviso']=T(); out['emitir_os']=J("Object.keys(JSON.parse(Object.keys(localStorage).filter(k=>/cenario-v1$/.test(k)).map(k=>localStorage.getItem(k))[0]||'{\"ordens\":{}}').ordens).filter(k=>k>='OS-0440'&&k<'OS-0500')")
    J("localStorage.clear()"); c.size(390,940); c.goto(U+'MB-06.dc.html#VIS-017',wait=1.6); J(f"({SETV})('#mb_cont','3,5')"); time.sleep(.3)
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Registrar e ir ao ponto 2').click()"); time.sleep(.6); out['app_aviso']=T(); c.size(1440,900)
    J("localStorage.clear(); localStorage.setItem('talhao-os-mip'+'-v1','{ilegivel')"); c.goto(U+'AG-01.dc.html',wait=1.8)
    out['ileg_header']=(J("(document.querySelector('header')||{innerText:''}).innerText") or '')[:120]; out['ileg_erros']=J("window.__errs")
finally:
    c.close(); srv.terminate()
print(json.dumps(out,ensure_ascii=False,indent=1))
