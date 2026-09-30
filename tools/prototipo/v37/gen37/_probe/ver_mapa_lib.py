# -*- coding: utf-8 -*-
"""Apoio do verificador independente da frente mapa (IN-01..IN-04). Chrome real via cdp.py, _render/ servido por http.server."""
import sys, os, time, subprocess, json
HERE=os.path.dirname(os.path.abspath(__file__)); GEN=os.path.dirname(HERE); sys.path.insert(0,GEN)
from cdp import Chrome
from journeys import free
R=os.path.join(GEN,'_render'); KEY='talhao-os-cenario-v1'
ERRJS=r"""window.__errs=[];window.addEventListener('error',e=>window.__errs.push('err: '+e.message));
window.addEventListener('unhandledrejection',e=>window.__errs.push('rej: '+(e.reason&&e.reason.message||e.reason)));
(()=>{const ce=console.error.bind(console); console.error=(...a)=>{window.__errs.push('console: '+a.map(String).join(' ').slice(0,200)); ce(...a);};})();"""
class Sess:
    def __init__(self,w=1440,h=1000):
        self.p=free(); self.srv=subprocess.Popen(['python3','-m','http.server',str(self.p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        time.sleep(0.7); self.c=Chrome(port=free()); self.c.call('Page.addScriptToEvaluateOnNewDocument',{'source':ERRJS}); self.c.size(w,h)
        self.OK=[]; self.FAIL=[]
    def url(self,f): return f'http://127.0.0.1:{self.p}/{f}'
    def go(self,f,wait=1.2): self.c.goto(self.url(f),wait=wait); time.sleep(.2)
    def J(self,e): return self.c.js(e)
    def errs(self): return self.J("(window.__errs||[]).join(' | ')") or ''
    def body(self): return self.J("document.body.innerText") or ''
    def head(self): return (self.J("(document.querySelector('header')||document.body).innerText.replace(/\\n/g,' | ')") or '')
    def clk(self,t,root=None,exact=False):
        js="""((t,root,ex)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim();
         const els=[...r.querySelectorAll('button,a,[role=button],[role=tab],[role=option]')].filter(e=>e.getClientRects().length);
         const e=els.find(x=>n(x.innerText)===t)||(!ex&&els.find(x=>n(x.innerText).startsWith(t)))||els.find(x=>n(x.getAttribute('aria-label'))===t); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok:'+e.tagName+':'+(e.getAttribute('href')||'');})"""
        r=self.J(f"({js})({json.dumps(t)},{json.dumps(root)},{json.dumps(exact)})"); time.sleep(.35); return r
    def setsel(self,sel,val):
        self.J(f"""((sel,val)=>{{const i=document.querySelector(sel); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,val); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})({json.dumps(sel)},{json.dumps(val)})"""); time.sleep(.4)
    def faz(self,v): self.setsel('select[aria-label="Filtrar por fazenda"]',v)
    SV="[...document.querySelectorAll('svg [role=button]')]"
    def lab(self,t): return self.J(f"(()=>{{const e={self.SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')); return e?[e.getAttribute('aria-label'),e.getAttribute('fill')]:[null,null];}})()")
    def tap(self,t): self.J(f"{self.SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
    def pan(self,t): return self.J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{}}).innerText||''") or ''
    def cen(self): return self.J(f"JSON.parse(localStorage.getItem('{KEY}')||'null')")
    def setcen(self,s): self.J(f"localStorage.setItem('{KEY}',{json.dumps(json.dumps(s,ensure_ascii=False))}); window.dispatchEvent(new StorageEvent('storage',{{key:'{KEY}'}}))"); time.sleep(.4)
    def reset(self): self.J(f"localStorage.removeItem('{KEY}')")
    def overflow(self):
        return self.J(r"""(()=>{const out=[]; const W=document.documentElement.clientWidth;
          if(document.documentElement.scrollWidth>W+1) out.push('página '+document.documentElement.scrollWidth+'>'+W);
          document.querySelectorAll('[role=grid],[role=table],table').forEach(g=>{const p=g.parentElement; if(g.scrollWidth>p.clientWidth+2) out.push('tabela '+(g.getAttribute('aria-label')||g.className).slice(0,40)+' '+g.scrollWidth+'>'+p.clientWidth);});
          return out;})()""")
    def clipped(self,root='body'):
        return self.J(r"""((root)=>{const out=[]; document.querySelectorAll(root+' *').forEach(e=>{ if(!e.getClientRects().length) return; const cs=getComputedStyle(e);
          if((cs.overflow==='hidden'||cs.overflowX==='hidden'||cs.overflowY==='hidden') && cs.textOverflow!=='ellipsis' && e.innerText && e.innerText.trim() && e.children.length<3){
            if(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2) out.push(e.tagName+' '+e.scrollWidth+'x'+e.scrollHeight+'>'+e.clientWidth+'x'+e.clientHeight+' '+e.innerText.replace(/\s+/g,' ').slice(0,70)); } });
          return out.slice(0,15);})(""" + json.dumps(root) + ")")
    def chk(self,nome,cond,info=''):
        (self.OK if cond else self.FAIL).append(nome); print(('OK   ' if cond else 'FALHA'),nome,'' if cond else str(info)[:700]); sys.stdout.flush()
    def shot(self,nome): self.c.shot(os.path.join(HERE,nome if nome.endswith('.png') else 'ver_mapa_'+nome+'.png'))
    def js(self,e): return self.J(e)
    def click(self,t,root=None): return self.clk(t,root)
    def close(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print(f'\n{len(self.OK)} ok · {len(self.FAIL)} falhas', self.FAIL)
