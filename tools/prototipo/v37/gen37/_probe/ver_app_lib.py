# -*- coding: utf-8 -*-
"""Apoio do verificador independente da frente App (ver_app*.py). Serve _render/ SEM copiar nada; Chrome headless 1440x1000."""
import sys, os, time, subprocess, json
GEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GEN)
from cdp import Chrome
from journeys import free
R = os.path.join(GEN, '_render'); SHOTS = os.path.join(GEN, '_probe')
CLK = """((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NAO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NAO ACHEI: '+sel; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
# corte vertical: maior bottom de qualquer descendente visível de <main> contra a borda interna de <main>
CORTE = """(()=>{const m=document.querySelector('main'); if(!m) return null; const mr=m.getBoundingClientRect(); const pb=parseFloat(getComputedStyle(m).paddingBottom)||0; let b=0, who='';
 m.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height>0 && r.width>0 && r.bottom>b){b=r.bottom; who=(e.innerText||e.tagName).slice(0,40);} });
 return {excesso: Math.round(b-(mr.bottom-pb)), who};})()"""
# estouro horizontal: descendentes que passam da borda direita do quadro (390 px) ou texto maior que a caixa
LARG = """(()=>{const root=document.querySelector('main').parentElement; const rr=root.getBoundingClientRect(); const out=[];
 root.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.width>0 && r.right>rr.right+0.5) out.push(e.tagName+':'+(e.innerText||'').replace(/\\s+/g,' ').slice(0,40)+' @'+Math.round(r.right-rr.left));
  if(e.children.length===0 && e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow!=='visible') out.push('TXT '+e.tagName+':'+(e.innerText||'').slice(0,40)); });
 return out.slice(0,6);})()"""


class V:
    def __init__(self, w=1440, h=1000):
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.6)
        self.c = Chrome(port=free(), w=w, h=h); self.c.size(w, h); self.J = self.c.js; self.FAIL = []; self.n = 0; self.errs = []

    def abrir(self, t):
        self.c.goto(f'http://127.0.0.1:{self.p}/{t}.dc.html', wait=0.9)
        self.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")

    def clk(self, t):
        r = self.J(f"({CLK})({json.dumps(t)})"); time.sleep(.35); return r

    def clk_sel(self, sel):
        r = self.J(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return 'NAO ACHEI'; e.click(); return 'ok';}})()"); time.sleep(.35); return r

    def setv(self, sel, val):
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.15); return r

    def cen(self, expr):
        return self.J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")

    def mudar(self, fnbody):
        return self.J(f"(()=>{{const {{cenGet,cenMudar,cenLiberar,cenEntregar,cenConfirmarRecebimento,cenIniciarTurno,cenFecharTurno,cenOcorrencia,cenSinal}}=window.__cen; const r=cenMudar(null,c=>{{{fnbody}}}); return r.erro||r.msg||'';}})()")

    def body(self): return self.J("document.body.innerText")
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def hdr(self): return self.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    def foot(self): return self.J("(()=>{const m=document.querySelector('main'); const f=m&&m.nextElementSibling; return f?[...f.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null).map(e=>e.innerText.trim()).join(' | '):'';})()")
    def alerts(self): return self.J("[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' | ')")
    def corte(self): return self.J(CORTE)
    def larg(self): return self.J(LARG)
    def erros(self): return self.J("window.__errs") or []
    def shot(self, nome): self.c.shot(os.path.join(SHOTS, nome))

    def ok(self, cond, msg):
        self.n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg)
        if not cond: self.FAIL.append(msg)

    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print(f'{self.n - len(self.FAIL)}/{self.n} ok · FALHAS: {len(self.FAIL)}'); [print(' -', f) for f in self.FAIL]
