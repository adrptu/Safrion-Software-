# -*- coding: utf-8 -*-
"""Apoio do verificador independente da frente Estoque: servidor de _render/ (só leitura), Chrome headless 1440x1000 e ações por JS."""
import sys, os, time, subprocess, json
P = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.dirname(P)
sys.path.insert(0, GEN)
from cdp import Chrome
from journeys import free
R = os.path.join(GEN, '_render')

CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NAO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
ROWS = """(()=>[...document.querySelectorAll('[role=row]')].filter(r=>r.querySelector('[role=cell]')))"""


class V:
    def __init__(self, w=1440, h=1000):
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.6)
        self.c = Chrome(port=free()); self.c.size(w, h); self.J = self.c.js; self.res = []

    def abrir(self, f='EST.dc.html', wait=1.0):
        self.c.goto(f'http://127.0.0.1:{self.p}/{f}', wait=wait)
        self.J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }")

    def etapa(self, i):
        self.J(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{i - 1}].click()"); time.sleep(.4)

    def clk(self, t, root=None):
        r = self.J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r

    def setv(self, sel, val):
        if sel[0] not in '#[.' and ' ' not in sel: sel = '#' + sel
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r

    def rows(self):
        return self.J(f"{ROWS}().map(r=>r.innerText.replace(/\\s+/g,' ').trim())")

    def rowtxt(self, *ts):
        return self.J(f"(()=>{{const r={ROWS}().find(r=>{json.dumps(list(ts))}.every(t=>r.innerText.indexOf(t)>=0)); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()")

    def row(self, *ts):
        r = self.J(f"(()=>{{const r={ROWS}().find(r=>{json.dumps(list(ts))}.every(t=>r.innerText.indexOf(t)>=0)); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.4); return r

    def rowbtn(self, ts, b):
        ts = [ts] if isinstance(ts, str) else list(ts)
        r = self.J(f"(()=>{{const r={ROWS}().find(r=>{json.dumps(ts)}.every(t=>r.innerText.indexOf(t)>=0)); if(!r) return 'sem linha'; const x=[...r.querySelectorAll('button')].find(x=>x.innerText.trim().startsWith({json.dumps(b)})); if(!x) return 'sem botao'; x.click(); return 'ok';}})()"); time.sleep(.4); return r

    def aside(self): return self.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    def aberto(self): return self.J("!!document.querySelector('aside[role=dialog]')")
    def err(self): return self.J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')")
    def val(self, i): return self.J(f"(document.querySelector('#{i}')||{{value:null}}).value")
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def main(self): return self.J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")
    def erros(self): return self.J("(window.__errs||[]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText))")
    def cen(self, expr): return self.J(f"(()=>{{const X=window.__cen; const c=X.cenGet(); return ({expr});}})()")
    def mudar(self, body): return self.J(f"(()=>{{const X=window.__cen; with(X){{ const r=cenMudar(null,c=>{{{body}}}); return r.erro||r.msg||''; }} }})()")
    def prim(self):
        return self.J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&getComputedStyle(b).fontSize==='14px'); return b?b.innerText.trim():'';})()")
    def overflow(self):
        """Tabelas/elementos mais largos que a área e textos cortados (scrollWidth > clientWidth com overflow escondido)."""
        return self.J("""(()=>{const out=[]; const W=document.documentElement.clientWidth; if(document.documentElement.scrollWidth>W+1) out.push('pagina rola na horizontal: '+document.documentElement.scrollWidth+'>'+W);
          document.querySelectorAll('[role=table],[role=grid],table').forEach(t=>{ let p=t.parentElement; while(p&&p!==document.body){ const cs=getComputedStyle(p); if(/auto|scroll/.test(cs.overflowX)&&p.scrollWidth>p.clientWidth+1){ out.push('tabela rola: '+p.scrollWidth+'>'+p.clientWidth+' '+(t.innerText||'').slice(0,40).replace(/\\s+/g,' ')); break;} p=p.parentElement; } });
          document.querySelectorAll('main *').forEach(e=>{ if(!e.offsetParent) return; const cs=getComputedStyle(e); if((cs.overflow==='hidden'||cs.textOverflow==='ellipsis'||cs.overflowX==='hidden')&&e.scrollWidth>e.clientWidth+2&&e.children.length===0&&e.innerText.trim()) out.push('cortado: '+e.innerText.trim().slice(0,80)+' ('+e.scrollWidth+'>'+e.clientWidth+')'); });
          return out;})()""")
    def shot(self, nome): self.c.shot(os.path.join(P, nome))

    def ok(self, cond, msg, extra=''):
        self.res.append((bool(cond), msg, extra))
        print(('  OK  ' if cond else '  FALHA ') + msg + ((' · ' + str(extra)[:400]) if (extra != '' and not cond) else ''))

    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
        f = [m for c, m, _ in self.res if not c]
        print(f'RESULTADO: {len(self.res) - len(f)}/{len(self.res)} ok' + (' · FALHAS: ' + '; '.join(f) if f else ''))
