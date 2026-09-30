# -*- coding: utf-8 -*-
"""Auxiliares do verificador independente da frente cad-parceiros (CD-05). Só leitura: serve _render/ e abre Chrome headless 1440x1000."""
import sys, os, time, subprocess, json
GEN=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,GEN)
from cdp import Chrome
from journeys import free
R=os.path.join(GEN,'_render')
CAP="""window.__verr=[];addEventListener('error',e=>window.__verr.push('err:'+(e.message||e.type)));addEventListener('unhandledrejection',e=>window.__verr.push('rej:'+String(e.reason)));
(function(){const o=console.error;console.error=function(){try{window.__verr.push('console:'+[].map.call(arguments,String).join(' ').slice(0,200));}catch(x){} return o.apply(console,arguments);};})();"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
class T:
    def __init__(self,tela='CD-05.dc.html',w=1440,h=1000):
        self.p=free(); self.srv=subprocess.Popen(['python3','-m','http.server',str(self.p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
        self.c=Chrome(port=free(),w=w,h=h); self.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':CAP})
        self.c.size(w,h); self.url=f'http://127.0.0.1:{self.p}/{tela}'; self.ok=[]
    def load(self): self.c.goto(self.url,wait=1.2); time.sleep(.3)
    def J(self,e): return self.c.js(e)
    def chk(self,nome,cond,extra=''):
        self.ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:600] if extra!='' else ''))
    def errs(self): return self.J("(window.__verr||[]).join(' | ')")
    def setk(self,k,val): self.J(f"({SETV})('#fx_g_forn_{k}',{json.dumps(val)})"); time.sleep(.15)
    def btn(self,t):
        r=self.J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(b){{b.click(); return true;}} return false;}})()"); time.sleep(.35); return r
    def anybtn(self,t):
        r=self.J(f"(()=>{{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(t)}); if(b){{b.click(); return true;}} return false;}})()"); time.sleep(.35); return r
    def can(self,t):
        r=self.J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')); if(!l) return false; l.querySelector('input').click(); return true;}})()"); time.sleep(.2); return r
    def on(self,t): return self.J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(t)} && l.querySelector('input[type=checkbox]')); return l?l.querySelector('input').checked:null;}})()")
    def al(self): return self.J("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    def labs(self): return self.J("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
    def st(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).join(' | ')")
    def aberto(self): return self.J("!!document.querySelector('aside[role=dialog]')")
    def aside(self): return self.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText")
    ROWS="[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row].g2ed')]"
    def lin(self,n): return self.J(f"(()=>{{const r={self.ROWS}.find(r=>r.innerText.indexOf({json.dumps(n)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'';}})()")
    def rows(self): return self.J(f"{self.ROWS}.map(r=>r.innerText.replace(/\\s+/g,' '))")
    def abre(self,n): self.J(f"(()=>{{const r={self.ROWS}.find(r=>r.innerText.indexOf({json.dumps(n)})>=0); (r.querySelector('[role=cell] span')||r).click();}})()"); time.sleep(.4)
    def fils(self): return self.J("[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()).join(' | ')")
    def fil(self,t): self.J(f"[...document.querySelectorAll('[role=group][aria-label=\"Filtrar por papel\"] button')].find(b=>b.innerText.trim().startsWith({json.dumps(t)})).click()"); time.sleep(.35)
    def novo(self): self.J("[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Cadastrar parceiro').click()"); time.sleep(.4)
    def chip(self): return self.J("document.querySelector('h1').parentElement.innerText.replace(/\\s+/g,' ')")
    def heads(self,i=0): return self.J(f"(()=>{{const t=document.querySelectorAll('[role=table]')[{i}]; if(!t) return null; return [...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/\\s+/g,' ').trim());}})()")
    def need(self): return self.J("(()=>{const R=document.querySelector('[data-root]'); const h0=R.style.height; R.style.height='auto'; const h=Math.ceil(R.getBoundingClientRect().height); R.style.height=h0; return h;})()")
    def close(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print('RESULTADO:', 'OK' if all(self.ok) else 'FALHOU', f'{sum(self.ok)}/{len(self.ok)}')
