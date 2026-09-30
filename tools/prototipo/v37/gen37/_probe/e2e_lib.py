# -*- coding: utf-8 -*-
"""Verificação ponta a ponta: UM Chrome headless (porta 9777, perfil fixo) e UM http.server (porta 8777, _render/) já em execução.
Cada script e2e_*.py se conecta à mesma aba, então o localStorage do cenário é o mesmo entre as telas (mesma origem)."""
import sys, os, json, time, socket, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.dirname(HERE)
sys.path.insert(0, GEN)
from cdp import WS
BASE = 'http://127.0.0.1:8777/'; CP = 9777
SHOTS = os.path.join(HERE, 'e2e')
CLK = """((t,root)=>{const r=root?document.querySelector(root):document; if(!r) return 'SEM RAIZ '+root; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a,[role=tab]')].filter(e=>e.offsetParent!==null||e.getClientRects().length); const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t))||els.find(x=>n(x.getAttribute('aria-label'))===t)||els.find(x=>n(x.getAttribute('title'))===t); if(!e) return 'NÃO ACHEI: '+t; e.scrollIntoView({block:'center'}); e.click(); return 'ok';})"""
SETV = """((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
FIND = """((ts)=>[...document.querySelectorAll('[role=row]')].find(r=>ts.every(t=>r.innerText.indexOf(t)>=0)))"""


class B:
    def __init__(self):
        self.FAIL = []; self.n = 0; self.console = []
        tabs = json.load(urllib.request.urlopen(f'http://127.0.0.1:{CP}/json', timeout=10))
        t = [x for x in tabs if x.get('type') == 'page'][0]
        self.ws = WS(t['webSocketDebuggerUrl']); self.i = 0
        self.call('Page.enable'); self.call('Runtime.enable')
        try: self.call('Network.enable'); self.call('Network.setCacheDisabled', {'cacheDisabled': True})  # telas recompiladas: nunca a cópia em cache
        except Exception: pass

    def call(self, method, params=None, timeout=30):
        self.i += 1; mid = self.i; self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0: raise TimeoutError(method)
            try: m = json.loads(self.ws.recv(timeout=remaining))
            except (TimeoutError, socket.timeout) as exc: raise TimeoutError(method) from exc
            if m.get('method') == 'Runtime.exceptionThrown':
                self.console.append(m['params']['exceptionDetails'].get('exception', {}).get('description', m['params']['exceptionDetails'].get('text')))
            if m.get('id') == mid:
                if 'error' in m: raise RuntimeError(f"{method}: {m['error']}")
                return m.get('result', {})

    def J(self, expr):
        r = self.call('Runtime.evaluate', {'expression': expr, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'].get('exception', {}).get('description') or r['exceptionDetails'].get('text', 'js'))
        return r['result'].get('value')

    def size(self, w, h):
        self.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': w < 500})

    def goto(self, tela, wait=1.0):
        self.call('Page.navigate', {'url': BASE + tela}); time.sleep(wait)
        for _ in range(30):
            try:
                if self.J("document.readyState") == 'complete' and self.J("!!(document.body && document.body.innerText.length>50)"): break
            except Exception: pass
            time.sleep(0.25)
        time.sleep(0.5)
        self.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message)); window.addEventListener('unhandledrejection',e=>window.__errs.push(String(e.reason)));")

    def path(self): return self.J("location.pathname")
    def clk(self, t, root=None, w=.4):
        r = self.J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(w); return r
    def clk_sel(self, sel, w=.4):
        r = self.J(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return 'NÃO ACHEI '+{json.dumps(sel)}; e.scrollIntoView({{block:'center'}}); e.click(); return 'ok';}})()"); time.sleep(w); return r
    def setv(self, sel, val):
        if sel[0] not in '#[.' and ' ' not in sel: sel = '#' + sel
        r = self.J(f"({SETV})({json.dumps(sel)},{json.dumps(val)})"); time.sleep(.2); return r
    def val(self, sel): return self.J(f"(document.querySelector({json.dumps(sel)})||{{value:null}}).value")
    def body(self): return self.J("document.body.innerText") or ''
    def main(self): return self.J("(document.querySelector('main')||document.body).innerText.replace(/\\s+/g,' ')") or ''
    def aside(self): return self.J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
    def toast(self): return self.J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def alerts(self, root='body'): return self.J(f"[...document.querySelectorAll({json.dumps(root + ' [role=alert]')})].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
    def rowtxt(self, *ts): return self.J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()")
    def row(self, *ts):
        r = self.J(f"(()=>{{const r=({FIND})({json.dumps(list(ts))}); if(!r) return 'sem linha'; r.scrollIntoView({{block:'center'}}); (r.querySelector('[role=cell] span')||r).click(); return 'ok';}})()"); time.sleep(.45); return r
    def rowbtn(self, ts, b):
        ts = [ts] if isinstance(ts, str) else list(ts)
        r = self.J(f"(()=>{{const r=({FIND})({json.dumps(ts)}); if(!r) return 'sem linha'; const x=[...r.querySelectorAll('button')].find(x=>x.innerText.trim().startsWith({json.dumps(b)})); if(!x) return 'sem botão'; x.click(); return 'ok';}})()"); time.sleep(.45); return r
    def btns(self, root='body'): return self.J(f"[...document.querySelectorAll({json.dumps(root + ' button')})].filter(b=>b.offsetParent!==null).map(b=>b.innerText.trim()).filter(Boolean)") or []
    def links(self, root='body'): return self.J(f"[...document.querySelectorAll({json.dumps(root + ' a')})].filter(b=>b.offsetParent!==null).map(b=>b.innerText.trim()+' → '+b.getAttribute('href'))") or []
    def cen(self, expr): return self.J(f"(()=>{{const X=window.__cen; const c=X.cenGet(); return ({expr});}})()")
    def ls(self): return self.J("localStorage.getItem('talhao-os-cenario-v1')")
    def erros(self): return (self.J("(window.__errs||[]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText)).concat(window.__err?[String(window.__err)]:[])") or []) + self.console
    def shot(self, nome):
        import base64
        os.makedirs(SHOTS, exist_ok=True)
        d = self.call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
        open(os.path.join(SHOTS, nome), 'wb').write(base64.b64decode(d['data']))

    def ok(self, cond, msg, extra=''):
        self.n += 1
        print(('  OK  ' if cond else '  FALHA ') + msg + ((' · ' + str(extra)[:500]) if (extra != '' and not cond) else ''))
        if not cond: self.FAIL.append(msg)

    def fim(self):
        print(f'RESULTADO: {self.n - len(self.FAIL)}/{self.n} ok' + (' · FALHAS: ' + '; '.join(self.FAIL) if self.FAIL else ''), flush=True)
        if self.FAIL: raise AssertionError('; '.join(self.FAIL))


FIELDS = """(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null;
 return [...a.querySelectorAll('input,select,textarea')].filter(i=>i.offsetParent!==null).map(i=>{const l=i.id?a.querySelector('label[for="'+i.id+'"]'):null;
 const lab=l?l.innerText.trim().replace(/\\s+/g,' '):(i.closest('label')?i.closest('label').innerText.trim():'');
 return {id:i.id, tag:i.tagName, type:i.type, lab, val:(i.type==='checkbox'?i.checked:i.value), ro:i.readOnly||i.disabled, opts:i.tagName==='SELECT'?[...i.options].map(o=>o.value).slice(0,12):undefined};});})()"""


def campos(b): return b.J(FIELDS) or []


def fid(b, lab):
    """id do campo cujo rótulo começa com lab."""
    for f in campos(b):
        if f['lab'].startswith(lab) and f['id']: return '#' + f['id']
    return None


def marcar(b, texto):
    return b.J(f"(()=>{{const l=[...document.querySelectorAll('aside[role=dialog] label')].find(l=>l.innerText.trim()==={json.dumps(texto)} && l.querySelector('input[type=checkbox]')); if(!l) return 'sem '+{json.dumps(texto)}; l.querySelector('input').click(); return 'ok';}})()")


def alerta_campo(b, sel):
    return b.J(f"(()=>{{const i=document.querySelector({json.dumps(sel)}); if(!i) return 'sem campo'; let n=i; for(let k=0;k<4&&n;k++){{ n=n.parentElement; const a=n&&n.querySelector('[role=alert]'); if(a) return a.innerText; }} return ''; }})()")
