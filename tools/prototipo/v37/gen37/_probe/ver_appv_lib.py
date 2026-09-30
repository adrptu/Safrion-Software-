# -*- coding: utf-8 -*-
"""Apoio do verificador independente (rodada v) da frente App. Serve _render/ SEM copiar nada; Chrome headless 1440x1000."""
import sys, os, time, subprocess, json
GEN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GEN)
from cdp import Chrome
from journeys import free
R = os.path.join(GEN, '_render'); SHOTS = os.path.join(GEN, '_probe')
CLK = """((t)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...document.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NAO ACHEI: '+t; if(e.tagName==='A'&&e.getAttribute('href')){window.__lastHref=e.getAttribute('href');} e.click(); return 'ok '+e.tagName+' '+(e.getAttribute('href')||'');})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NAO ACHEI: '+sel; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
CORTE = """(()=>{const m=document.querySelector('main'); if(!m) return null; const mr=m.getBoundingClientRect(); const pb=parseFloat(getComputedStyle(m).paddingBottom)||0; let b=0, who='';
 m.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height>0 && r.width>0 && r.bottom>b){b=r.bottom; who=(e.innerText||e.tagName).replace(/\\s+/g,' ').slice(0,50);} });
 return {excesso: Math.round(b-(mr.bottom-pb)), who};})()"""
LARG = """(()=>{const root=document.querySelector('main').parentElement; const rr=root.getBoundingClientRect(); const out=[];
 root.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect(); if(r.width>0 && r.right>rr.right+0.5) out.push(e.tagName+':'+(e.innerText||'').replace(/\\s+/g,' ').slice(0,40)+' @'+Math.round(r.right-rr.left));
  if(e.children.length===0 && e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflow!=='visible') out.push('TXT '+e.tagName+':'+(e.innerText||'').slice(0,40)); });
 return out.slice(0,6);})()"""


class V:
    def __init__(self, w=1440, h=1000):
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.6)
        self.c = Chrome(port=free(), w=w, h=h); self.c.size(w, h); self.J = self.c.js; self.FAIL = []; self.n = 0

    def abrir(self, t):
        self.c.goto(f'http://127.0.0.1:{self.p}/{t}.dc.html', wait=0.9)
        self.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message)); window.addEventListener('unhandledrejection',e=>window.__errs.push(String(e.reason)));")

    def path(self): return self.J("location.pathname")
    def clk(self, t, wait=.4):
        r = self.J(f"({CLK})({json.dumps(t)})"); time.sleep(wait); return r
    def clk_sel(self, sel, wait=.4):
        r = self.J(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return 'NAO ACHEI'; e.click(); return 'ok';}})()"); time.sleep(wait); return r
    def setv(self, sel, val):
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r
    def cen(self, expr):
        return self.J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")
    def mudar(self, fnbody):
        return self.J(f"(()=>{{const {{cenGet,cenMudar,cenLiberar,cenEntregar,cenConfirmarRecebimento,cenIniciarTurno,cenFecharTurno,cenOcorrencia,cenSinal}}=window.__cen; const r=cenMudar(null,c=>{{{fnbody}}}); return r.erro||r.msg||'';}})()")
    def body(self): return self.J("document.body.innerText")
    def main(self): return self.J("document.querySelector('main').innerText")
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def hdr(self): return self.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    def foot(self): return self.J("(()=>{const m=document.querySelector('main'); const f=m&&m.nextElementSibling; return f?[...f.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null).map(e=>e.innerText.trim()).join(' | '):'';})()")
    def alerts(self): return self.J("[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' | ')")
    def corte(self): return self.J(CORTE)
    def larg(self): return self.J(LARG)
    def erros(self): return self.J("window.__errs") or []
    def shot(self, nome):
        h = self.J("Math.max(document.documentElement.scrollHeight,1000)"); self.c.size(1440, min(h, 2600)); time.sleep(.3)
        self.c.shot(os.path.join(SHOTS, nome)); self.c.size(1440, 1000)
    def ok(self, cond, msg):
        self.n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg, flush=True)
        if not cond: self.FAIL.append(msg)
    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print(f'{self.n - len(self.FAIL)}/{self.n} ok · FALHAS: {len(self.FAIL)}'); [print(' -', f) for f in self.FAIL]


def precarga(a, os_id='OS-0430'):
    """Aprova e libera a OS-0430 e entrega os 3 itens por cenMudar na própria página (como O.S./Estoque fariam)."""
    a.abrir('MB-01')
    r1 = a.mudar(f"c.ordens['{os_id}'].aprov=true; return cenLiberar(c,'{os_id}');")
    rid = a.cen(f"c.ordens['{os_id}'].req")
    rs = [a.mudar(f"return cenEntregar(c,'{rid}','{p}',{q},'Marcos');") for p, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80))]
    print('   pré-carga:', r1[:100], '|', rid, '|', [x[:50] for x in rs], flush=True)
    return rid
