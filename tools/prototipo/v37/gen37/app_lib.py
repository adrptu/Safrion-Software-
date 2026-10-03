# -*- coding: utf-8 -*-
"""Apoio dos testes do App de campo × cenário (app_*.py): servidor local de _render/, Chrome headless (cdp.py) e ações curtas.
Cada teste abre as telas pelo http.server; o cenário vive no localStorage da origem (um perfil novo do Chrome por execução)."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')
CLK = """((t,scope)=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const root=scope?document.querySelector(scope):document; const els=[...root.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'NÃO ACHEI: '+sel; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""


def copiar(telas):
    for t in telas:
        open(os.path.join(R, t + '.dc.html'), 'w').write(open(os.path.join(HERE, 'project', t + '.dc.html')).read())


class App:
    def __init__(self, telas=()):
        copiar(telas)
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.6)
        self.c = Chrome(port=free()); self.c.size(390, 1800); self.J = self.c.js; self.FAIL = []; self.n = 0

    def abrir(self, t):
        self.c.goto(f'http://127.0.0.1:{self.p}/{t}.dc.html', wait=1.0)
        self.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")

    def clk(self, t, scope=None):
        r = self.J(f"({CLK})({json.dumps(t)},{json.dumps(scope)})"); time.sleep(.35); return r

    def clk_sel(self, sel):
        r = self.J(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return 'NÃO ACHEI'; e.click(); return 'ok';}})()"); time.sleep(.35); return r

    def setv(self, sel, val):
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.15); return r

    def cen(self, expr):
        """Lê o cenário na própria página (cenGet) — expr recebe c."""
        return self.J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")

    def mudar(self, fnbody):
        """Muda o cenário na própria página por cenMudar (como as telas O.S./Estoque fariam) e recarrega."""
        r = self.J(f"(()=>{{const {{cenGet,cenMudar,cenLiberar,cenEntregar,cenConfirmarRecebimento,cenIniciarTurno,cenFecharTurno,cenOcorrencia,cenSinal}}=window.__cen; const r=cenMudar(null,c=>{{{fnbody}}}); return r.erro||r.msg||'';}})()"); return r

    def body(self): return self.J("document.body.innerText")
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def hdr(self): return self.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    def foot(self): return self.J("(()=>{const f=[...document.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null&&/font-size: 17px/.test(e.getAttribute('style')||'')); return f.map(e=>e.innerText.trim()).join(' | ');})()")
    def erros(self): return self.J("window.__errs")
    def over(self):
        return self.J("(()=>{const m=document.querySelector('main'); let b=0; m.querySelectorAll(':scope > *, :scope > sc-if > *, :scope > sc-if > sc-if > *, :scope > sc-for > *').forEach(e=>{const r=e.getBoundingClientRect(); if(r.height) b=Math.max(b,r.bottom);}); const mr=m.getBoundingClientRect(); return Math.round(b+16-mr.bottom);})()")

    def ok(self, cond, msg):
        self.n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg)
        if not cond: self.FAIL.append(msg)

    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print(f'{self.n - len(self.FAIL)}/{self.n} ok · FALHAS: {len(self.FAIL)}'); [print(' -', f) for f in self.FAIL]
