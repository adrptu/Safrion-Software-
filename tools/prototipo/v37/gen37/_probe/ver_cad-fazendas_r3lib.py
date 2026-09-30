# -*- coding: utf-8 -*-
"""Apoio dos verificadores ver_cad-fazendas_r3*.py (rodada 3) (frente Cadastros · Fazendas e talhões): serve _render/, abre o Chrome real (1440×1000) e captura erros de JS."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); GEN=os.path.dirname(HERE); sys.path.insert(0,GEN)
from cdp import Chrome
from journeys import free
R=os.path.join(GEN,'_render')
HOOK=r"""window.__errs=[]; window.addEventListener('error',e=>window.__errs.push('error: '+(e.message||e.type)+' @'+(e.filename||'')+':'+(e.lineno||'')));
window.addEventListener('unhandledrejection',e=>window.__errs.push('rejection: '+String(e.reason)));
(function(){const ce=console.error; console.error=function(){ try{ window.__errs.push('console.error: '+[...arguments].map(String).join(' ').slice(0,300)); }catch(e){} return ce.apply(console,arguments); };})();"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'SEM CAMPO '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
class Sess:
    def __init__(self,w=1440,h=1000):
        self.p=free(); self.srv=subprocess.Popen(['python3','-m','http.server',str(self.p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(0.8); self.c=Chrome(port=free()); self.c.size(w,h)
        self.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':HOOK})
        self.base=f'http://127.0.0.1:{self.p}/'
    def go(self,f,wait=1.2): self.c.goto(self.base+f,wait=wait)
    def js(self,e): return self.c.js(e)
    def errs(self): return (self.js("window.__errs||[]") or [])+[x for x in (self.js("[...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText)") or []) if x]
    def body(self): return self.js("document.body.innerText") or ''
    def head(self): return (self.js("(document.querySelector('header')||{innerText:''}).innerText") or '').replace('\n',' | ')
    def aside(self): return (self.js("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').replace('\n',' | ')
    def aberto(self): return self.js("!!document.querySelector('aside[role=dialog]')")
    def alerts(self): return self.js("[...document.querySelectorAll('aside [role=alert]')].map(x=>x.innerText).join(' | ')")
    def toast(self): return self.js("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def labels(self): return self.js("[...document.querySelectorAll('aside[role=dialog] label[for]')].map(l=>l.innerText.trim())")
    def fv(self,k): return self.js(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i?i.value:null;}})()")
    def fopts(self,k): return self.js(f"(()=>{{const i=document.querySelector('aside[role=dialog] [id$=\"_{k}\"]'); return i&&i.options?[...i.options].map(o=>o.value):null;}})()")
    def fset(self,k,v): r=self.js(f"({SETV})('aside[role=dialog] [id$=\"_{k}\"]',{json.dumps(v)})"); time.sleep(.2); return r
    def btn(self,t): r=self.js(f"({BTN})({json.dumps(t)})"); time.sleep(.35); return r
    def row(self,ti,txt): return f"[...document.querySelectorAll('[role=table]')[{ti}].querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0)"
    def rowtxt(self,ti,txt): return self.js(f"(()=>{{const r={self.row(ti,txt)}; return r?r.innerText.replace(/\\s+/g,' '):null;}})()")
    def openrow(self,ti,txt): r=self.js(f"(()=>{{const r={self.row(ti,txt)}; if(!r) return 'SEM LINHA'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.35); return r
    def rows(self,ti): return self.js(f"(()=>{{const t=document.querySelectorAll('[role=table]')[{ti}]; return t?[...t.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()):null;}})()")
    def click(self,t,root=None,exact=False):
        r=self.js("""((t,root,ex)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ';
          const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a,[role=button]')].filter(e=>e.getClientRects().length);
          const e=els.find(x=>n(x.innerText)===t)||(!ex&&els.find(x=>n(x.innerText).startsWith(t)))||els.find(x=>n(x.getAttribute('aria-label'))===t);
          if(!e) return 'NÃO ACHEI: '+t; e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true})); return 'ok';})"""+f"({json.dumps(t)},{json.dumps(root)},{json.dumps(exact)})")
        time.sleep(.35); return r
    def clear_ls(self): self.js("(()=>{try{localStorage.clear();}catch(e){}})()")
    def overflow(self):
        """tabelas/elementos mais largos que o contêiner e textos cortados com reticências."""
        return self.js(r"""(()=>{const o=[];
          document.querySelectorAll('[role=table]').forEach((t,i)=>{ let p=t.parentElement; while(p&&p!==document.body){ if(p.scrollWidth>p.clientWidth+2){ o.push('tabela '+i+' rola: '+p.scrollWidth+'>'+p.clientWidth); break;} p=p.parentElement; } });
          if(document.documentElement.scrollWidth>window.innerWidth+1) o.push('página rola na horizontal: '+document.documentElement.scrollWidth);
          document.querySelectorAll('main *').forEach(e=>{ const cs=getComputedStyle(e); if(e.children.length===0&&e.innerText&&e.scrollWidth>e.clientWidth+1&&(cs.overflow==='hidden'||cs.textOverflow==='ellipsis'||cs.overflowX==='hidden')) o.push('cortado: '+e.innerText.slice(0,60)+' ('+e.scrollWidth+'>'+e.clientWidth+')'); });
          return o;})()""")
    def shot(self,name,full=False):
        if full:
            h=self.js("Math.min(Math.max(document.documentElement.scrollHeight,1000),4000)"); self.c.size(1440,h); time.sleep(.3)
        self.c.shot(os.path.join(HERE,name))
        if full: self.c.size(1440,1000); time.sleep(.2)
    def close(self):
        try: self.c.close()
        finally: self.srv.terminate()
res=[]
def chk(nome,cond,extra=''):
    res.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ')+nome+(' · '+str(extra)[:600] if extra!='' else ''), flush=True)
