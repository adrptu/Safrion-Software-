# -*- coding: utf-8 -*-
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.join(HERE,'_render'); PR=os.path.join(HERE,'_probe')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
def setv(sel,val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.25)
def btn(t): J(f"(()=>{{const b=[...document.querySelectorAll('aside button')].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.4)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
    J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem').click()"); time.sleep(.4)
    setv('#nv_saf','S2627'); setv('#nv_cult','c1'); setv('#nv_atv','a1'); setv('#nv_jan','2026-09-25'); btn('Emitir ordem')
    info=J("(()=>{const s=document.querySelector('#nv_atv'); const d=s.getAttribute('aria-describedby'); const inv=s.getAttribute('aria-invalid'); const e=d?document.getElementById(d):null; return {d,inv,txt:e?e.innerText:null};})()")
    print('atv field:', info)
    c.shot(os.path.join(PR,'verif_dup.png'))
    # trocar cultivo tira o botão?
    setv('#nv_cult','c2'); has=J("[...document.querySelectorAll('aside button')].some(b=>b.innerText.trim().startsWith('Abrir OS-'))"); print('após trocar cultivo, botão Abrir ainda?', has)
    print('atv após trocar cultivo:', J("document.querySelector('#nv_atv').value"))
finally:
    c.close(); srv.terminate()
