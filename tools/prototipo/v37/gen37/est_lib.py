# -*- coding: utf-8 -*-
"""Apoio dos testes do Estoque (esttest.py, est_*.py): servidor local de _render/, Chrome headless (cdp.py) e ações curtas na EST.dc.html.
O cenário compartilhado vive no localStorage da origem; cada execução usa um perfil novo do Chrome (cenário limpo)."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ'; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')].filter(e=>e.offsetParent!==null); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
FIND = """((ts)=>[...document.querySelectorAll('[role=row]')].find(r=>ts.every(t=>r.innerText.indexOf(t)>=0)))"""


class Est:
    def __init__(self, copiar=True):
        if copiar:
            open(os.path.join(R, 'EST.dc.html'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'project', 'EST.dc.html'), encoding='utf-8').read())
        self.p = free()
        self.srv = subprocess.Popen(['python3', '-m', 'http.server', str(self.p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.6)
        self.c = Chrome(port=free()); self.c.size(1440, 1000); self.J = self.c.js; self.FAIL = []; self.n = 0

    def abrir(self, wait=1.0):
        self.c.goto(f'http://127.0.0.1:{self.p}/EST.dc.html', wait=wait)
        self.J("window.__errs=window.__errs||[]; if(!window.__ouve){ window.__ouve=1; window.addEventListener('error',e=>window.__errs.push(e.message)); }")

    def etapa(self, i):
        # Estoque é trabalho paralelo: as visões ficam na navegação "Seções do estoque" (mesma ordem 1…5), não em etapas (UX-ACAO-UNICA-20261003)
        self.J(f"document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[{i - 1}].click()"); time.sleep(.4)

    def clk(self, t, root=None):
        r = self.J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.4); return r

    def setv(self, i, val):
        sel = i if i[0] in '#[.' or ' ' in i else '#' + i
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r

    def row(self, *ts):
        r = self.J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); if(!r) return 'sem linha'; (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.4); return r

    def rowtxt(self, *ts):
        return self.J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()")

    def rowbtn(self, ts, b):
        ts = [ts] if isinstance(ts, str) else list(ts)
        r = self.J(f"(()=>{{const r=({FIND})({json.dumps(ts)}); if(!r) return 'sem linha'; const x=[...r.querySelectorAll('button')].find(x=>x.innerText.trim().startsWith({json.dumps(b)})); if(!x) return 'sem botão'; x.click(); return 'ok';}})()"); time.sleep(.4); return r

    def salvar(self): return self.clk('Salvar', 'aside[role=dialog]')
    def fechar(self): return self.clk('Fechar', 'aside[role=dialog]')
    def aside(self): return self.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
    def aberto(self): return self.J("!!document.querySelector('aside[role=dialog]')")
    def err(self): return self.J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')")
    def val(self, i): return self.J(f"(document.querySelector('#{i}')||{{value:null}}).value")
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
    def k(self): return self.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')")
    def main(self): return self.J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")
    def prim(self):
        """Ação primária da tela (botão verde do cabeçalho)."""
        return self.J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'&&getComputedStyle(b).fontSize==='14px'); return b?b.innerText.trim():'';})()")
    def erros(self): return self.J("(window.__errs||[]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText))")

    def cen(self, expr):
        """Lê o cenário na própria página (cenGet) — expr recebe c."""
        return self.J(f"(()=>{{const X=window.__cen; const c=X.cenGet(); return ({expr});}})()")

    def mudar(self, fnbody):
        """Muda o cenário na própria página por cenMudar (API do cenário) — fnbody recebe c e os cen* em escopo."""
        return self.J(f"(()=>{{const X=window.__cen; with(X){{ const r=cenMudar(null,c=>{{{fnbody}}}); return r.erro||r.msg||''; }} }})()")

    def shot(self, nome): self.c.shot(os.path.join(HERE, '_probe', nome))

    def ok(self, cond, msg, extra=''):
        self.n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg + ((' · ' + str(extra)[:300]) if (extra != '' and not cond) else ''))
        if not cond: self.FAIL.append(msg)

    def fim(self):
        try: self.c.close()
        finally: self.srv.terminate()
        print(f'RESULTADO: {self.n - len(self.FAIL)}/{self.n} ok' + (' · FALHAS: ' + '; '.join(self.FAIL) if self.FAIL else ''))
        return not self.FAIL
