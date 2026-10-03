# -*- coding: utf-8 -*-
"""Cliente mínimo do Chrome DevTools Protocol (websocket RFC 6455 em Python puro) para executar jornadas no protótipo."""
import os, socket, base64, os, struct, json, subprocess, time, urllib.request, urllib.parse, tempfile, shutil
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
class WS:
    def __init__(self,url):
        u=urllib.parse.urlparse(url); self.s=socket.create_connection((u.hostname,u.port),timeout=60)
        key=base64.b64encode(os.urandom(16)).decode()
        req=(f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
             f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode()); buf=b''
        try:
            while b'\r\n\r\n' not in buf:
                chunk=self.s.recv(4096)
                if not chunk: raise ConnectionError('WebSocket fechado durante handshake')
                buf+=chunk
            if b' 101 ' not in buf.split(b'\r\n')[0]: raise RuntimeError(buf[:200])
        except Exception:
            self.s.close()
            raise
        self.rest=buf.split(b'\r\n\r\n',1)[1]
    def _read(self,n):
        while len(self.rest)<n:
            deadline=getattr(self,'_deadline',None)
            if deadline is not None:
                remaining=deadline-time.monotonic()
                if remaining<=0: raise TimeoutError('WebSocket receive deadline')
                self.s.settimeout(remaining)
            ch=self.s.recv(1<<20)
            if not ch: raise ConnectionError('fechado')
            self.rest+=ch
        d,self.rest=self.rest[:n],self.rest[n:]; return d
    def send(self,text):
        p=text.encode(); m=os.urandom(4); h=bytes([0x81])
        n=len(p)
        h+= bytes([0x80|n]) if n<126 else (bytes([0x80|126])+struct.pack('>H',n) if n<65536 else bytes([0x80|127])+struct.pack('>Q',n))
        self.s.sendall(h+m+bytes(b^m[i%4] for i,b in enumerate(p)))
    def recv(self,timeout=None):
        previous_timeout=self.s.gettimeout()
        previous_deadline=getattr(self,'_deadline',None)
        self._deadline=None if timeout is None else time.monotonic()+timeout
        try:
            return self._recv_message()
        finally:
            self._deadline=previous_deadline
            self.s.settimeout(previous_timeout)
    def _recv_message(self):
        out=b''
        while True:
            b0,b1=self._read(2); fin=b0&0x80; op=b0&0x0f; n=b1&0x7f
            if n==126: n=struct.unpack('>H',self._read(2))[0]
            elif n==127: n=struct.unpack('>Q',self._read(8))[0]
            if b1&0x80: mk=self._read(4); data=bytes(x^mk[i%4] for i,x in enumerate(self._read(n)))
            else: data=self._read(n)
            if op==9: continue
            out+=data
            if fin: return out.decode('utf-8','replace')
class Chrome:
    def __init__(self,port=9333,w=1440,h=1100):
        self.dir=tempfile.mkdtemp(prefix='cdp_'); self.port=port
        # CDP_GL=1: WebGL por software (SwiftShader) para o mapa real (MapLibre); sem a variável, o de sempre (sem GPU)
        gl=(['--use-angle=swiftshader','--enable-unsafe-swiftshader'] if os.environ.get('CDP_GL')=='1' else ['--disable-gpu'])
        self.p=subprocess.Popen([CH,'--headless=new']+gl+['--hide-scrollbars',f'--remote-debugging-port={port}',f'--user-data-dir={self.dir}',f'--window-size={w},{h}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(100):
            try: tabs=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json')); break
            except Exception: time.sleep(0.2)
        t=[x for x in tabs if x.get('type')=='page'][0]
        self.ws=WS(t['webSocketDebuggerUrl']); self.i=0
        self.call('Page.enable'); self.call('Runtime.enable')
    def call(self,method,params=None,timeout=60):
        self.i+=1; mid=self.i; self.ws.send(json.dumps({'id':mid,'method':method,'params':params or {}}))
        deadline=time.monotonic()+timeout
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0: raise TimeoutError(method)
            try: m=json.loads(self.ws.recv(timeout=remaining))
            except (TimeoutError,socket.timeout) as exc: raise TimeoutError(method) from exc
            if m.get('id')==mid:
                if 'error' in m: raise RuntimeError(f"{method}: {m['error']}")
                return m.get('result',{})
    def js(self,expr):
        r=self.call('Runtime.evaluate',{'expression':expr,'awaitPromise':True,'returnByValue':True})
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'].get('text','js'))
        return r['result'].get('value')
    def goto(self,url,wait=2.5):
        self.call('Page.navigate',{'url':url}); time.sleep(wait)
        for _ in range(40):
            if self.js("document.readyState")=='complete' and self.js("document.body && document.body.innerText.length>50"): break
            time.sleep(0.25)
        time.sleep(0.6)
    def size(self,w,h):
        self.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':w<500})
    def shot(self,path):
        d=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        open(path,'wb').write(base64.b64decode(d['data']))
    def close(self):
        try: self.p.terminate(); self.p.wait(5)
        except Exception: pass
        shutil.rmtree(self.dir,ignore_errors=True)
