# -*- coding: utf-8 -*-
"""Apoio do verificador (frente os): segunda aba real no mesmo Chrome (mesma origem, mesmo localStorage) para simular Estoque/App
em outro documento, sem StorageEvent sintético."""
import json, time, urllib.request, sys, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from cdp import WS

class Tab:
    def __init__(self, chrome, url):
        port = chrome.port
        req = urllib.request.Request(f'http://127.0.0.1:{port}/json/new?{url}', method='PUT')
        t = json.load(urllib.request.urlopen(req))
        self.ws = WS(t['webSocketDebuggerUrl']); self.i = 0
        self.call('Page.enable'); self.call('Runtime.enable')
        self.call('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False})
        time.sleep(1.2)
        for _ in range(30):
            if self.js("document.readyState") == 'complete' and self.js("!!window.__cen"): break
            time.sleep(.25)
    def call(self, method, params=None, timeout=30):
        self.i += 1; mid = self.i; self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
        t0 = time.time()
        while True:
            m = json.loads(self.ws.recv())
            if m.get('id') == mid:
                if 'error' in m: raise RuntimeError(f"{method}: {m['error']}")
                return m.get('result', {})
            if time.time() - t0 > timeout: raise TimeoutError(method)
    def js(self, expr):
        r = self.call('Runtime.evaluate', {'expression': expr, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'].get('text', 'js') + ' ' + str(r['exceptionDetails'].get('exception', {}).get('description', ''))[:300])
        return r['result'].get('value')
    def mudar(self, body):
        """cenMudar na outra aba (Estoque/App): grava no localStorage; a aba da O.S. recebe o evento real de storage."""
        return self.js(f"(()=>{{const X=window.__cen; with(X){{ const r=cenMudar(null,c=>{{{body}}}); return r.erro||r.msg||''; }} }})()")
