# -*- coding: utf-8 -*-
"""Cliente mínimo do Chrome DevTools Protocol (websocket RFC 6455 em Python puro) para executar jornadas no protótipo."""
import os, sys, math, threading, socket, base64, os, struct, json, subprocess, time, urllib.request, urllib.parse, tempfile, shutil, atexit
def _chrome():
    # portabilidade (CONTINUIDADE-MAC-20261003): CHROME_BIN manda; senão o Chrome do Mac; senão o do PATH (Linux/nuvem)
    import shutil
    for c in [os.environ.get('CHROME_BIN'), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"] + [shutil.which(n) for n in ('google-chrome','google-chrome-stable','chromium','chromium-browser','chrome')]:
        if c and os.path.exists(c): return c
    raise RuntimeError('Chrome não encontrado: defina CHROME_BIN')
CH=_chrome()
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
    def _encher(self):
        deadline=getattr(self,'_deadline',None)
        if deadline is not None:
            remaining=deadline-time.monotonic()
            if remaining<=0: raise TimeoutError('WebSocket receive deadline')
            self.s.settimeout(remaining)
        ch=self.s.recv(1<<20)
        if not ch: raise ConnectionError('fechado')
        self.rest+=ch
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
        # ACELERA: só consome os bytes de uma mensagem inteira (todos os fragmentos). Prazo vencido no meio de um quadro deixa
        # o buffer intacto, e a leitura seguinte continua do ponto certo (antes, o cabeçalho lido se perdia e o fluxo desalinhava).
        while True:
            m=self._mensagem_inteira()
            if m is not None: return m
            self._encher()
    def _mensagem_inteira(self):
        b=self.rest; i=0; out=b''
        while True:
            if len(b)<i+2: return None
            b0,b1=b[i],b[i+1]; fin=b0&0x80; op=b0&0x0f; n=b1&0x7f; i+=2
            if n==126:
                if len(b)<i+2: return None
                n=struct.unpack('>H',b[i:i+2])[0]; i+=2
            elif n==127:
                if len(b)<i+8: return None
                n=struct.unpack('>Q',b[i:i+8])[0]; i+=8
            mk=None
            if b1&0x80:
                if len(b)<i+4: return None
                mk=b[i:i+4]; i+=4
            if len(b)<i+n: return None
            data=b[i:i+n]; i+=n
            if mk: data=bytes(x^mk[j%4] for j,x in enumerate(data))
            if op==9: continue
            out+=data
            if fin: self.rest=b[i:]; return out.decode('utf-8','replace')
# ---------- espera por condição (ACELERA, 13/10/2026) ----------
# SAFRION_ESPERA=condicao (padrão): goto e as esperas longas (time.sleep ≥ 1,0 s chamado de um teste fora de laço) terminam quando a página
# assenta — sem mutação no DOM, quadro de animação, rede ou leitura de arquivo, timer devido, animação CSS, carga de fonte/imagem nem
# navegação pendente por `quieto` s — e nunca depois do teto (o tempo que o teste dormia) mais o crédito (abaixo). Laço que dorme
# (sondagem com orçamento de tempo) e espera < 1 s ficam fixos. SAFRION_ESPERA=fixa: o comportamento antigo inteiro (sem o script
# de observação na página, goto com as esperas fixas e time.sleep original).
#
# Crédito (relógio da espera fixa). Cada espera que volta antes do teto adianta o teste em relação à execução com esperas fixas; o
# crédito é a soma desse adiantamento (segundos, por processo). Timer e pedido de rede guardam o crédito do momento em que nasceram e
# são esperados exatamente quando, no relógio da espera fixa, já teriam vencido antes do fim desta espera: timer de `d` ms criado com
# crédito `c0` é devido se agora + d + c0 ≤ fim desta espera no relógio fixo (início + teto + crédito atual); pedido de rede criado com
# crédito `c0` é esperado enquanto agora + c0 < esse fim. Assim o que a página faria por timer ou rede entre duas ações do teste com
# as esperas fixas acontece também agora, e o que só aconteceria depois da próxima ação continua não acontecendo (o aviso que some em
# 3,5 s some antes do clique que vinha 4 s depois; o aviso criado 1 s antes da leitura continua na tela). Os demais sinais (mutação,
# animação, fonte, imagem, carga) usam só o teto desta espera. A soma das esperas nunca passa da soma dos tetos (o crédito só existe
# porque esperas anteriores voltaram antes).
_dormir = time.sleep
CONDICAO = (os.environ.get('SAFRION_ESPERA') or 'condicao').strip().lower() != 'fixa'
_V37 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NAVEGA = ('Page.navigate', 'Page.reload', 'Page.navigateToHistoryEntry')
_USO = []   # navegadores abertos; o último usado no fim (é ele que o time.sleep do teste espera assentar)
_CRED = [0.0]   # crédito em segundos (por processo): quanto o teste está adiantado em relação às esperas fixas
# Observação instalada em todo documento novo antes do código da página (Page.addScriptToEvaluateOnNewDocument). Só observa:
# os invólucros de setTimeout/setInterval/requestAnimationFrame/fetch/XHR/FileReader/Blob/crypto.subtle.digest/createImageBitmap e
# MessagePort.postMessage (o agendador do React) chamam o original com os mesmos argumentos. window.__sfcred é o crédito em ms,
# posto pelo Python (no documento atual e, por script próprio, em todo documento novo).
QUIETO_JS = r"""(()=>{ try{ if(window.__sfq) return;
 const W=window, P=performance, agora=()=>P.now(), cr=()=>(Number(W.__sfcred)||0);
 const sT=W.setTimeout, cT=W.clearTimeout, sI=W.setInterval, cI=W.clearInterval, rAF=W.requestAnimationFrame;
 const q={id:Math.random().toString(36).slice(2), t:agora(), tm:new Map(), iv:new Map(), rede:0, redeC:[], raf:0, fimRede:0, nav:0};
 Object.defineProperty(W,'__sfq',{value:q,enumerable:false,configurable:true});
 const toca=()=>{ q.t=agora(); };
 try{ new MutationObserver(toca).observe(document,{subtree:true,childList:true,attributes:true,characterData:true}); }catch(e){}
 const roda=(f,a,self)=>(typeof f==='function'?f.apply(self,a):(0,eval)(String(f)));
 W.setTimeout=function(f,ms,...a){ const d=Math.max(0,Number(ms)||0); let id=0; id=sT.call(W,function(){ q.tm.delete(id); return roda(f,a,this); },d); q.tm.set(id,agora()+d+cr()); return id; };
 W.clearTimeout=function(id){ q.tm.delete(id); q.iv.delete(id); return cT.call(W,id); };
 W.setInterval=function(f,ms,...a){ const d=Math.max(0,Number(ms)||0); let id=0; id=sI.call(W,function(){ const r=q.iv.get(id); if(r) r.prox=agora()+d+cr(); return roda(f,a,this); },d); q.iv.set(id,{prox:agora()+d+cr()}); return id; };
 W.clearInterval=function(id){ q.tm.delete(id); q.iv.delete(id); return cI.call(W,id); };
 if(rAF) W.requestAnimationFrame=function(cb){ q.raf=agora(); return rAF.call(W,function(ts){ q.raf=agora(); return cb(ts); }); };
 try{ const mp=W.MessagePort&&W.MessagePort.prototype, pm=mp&&mp.postMessage; if(pm) mp.postMessage=function(){ toca(); return pm.apply(this,arguments); }; }catch(e){}
 const abre=()=>{ const c0=cr(); q.rede++; q.redeC.push(c0); let feito=false; return ()=>{ if(feito) return; feito=true; q.rede--; const i=q.redeC.indexOf(c0); if(i>=0) q.redeC.splice(i,1); q.fimRede=agora(); }; };
 const conta=(p)=>{ const fim=abre(); return p.then(v=>{ fim(); return v; },e=>{ fim(); throw e; }); };
 if(W.fetch){ const of=W.fetch; W.fetch=function(){ return conta(of.apply(this,arguments)); }; }
 if(W.Response) for(const k of ['json','text','arrayBuffer','blob','formData']){ const o=W.Response.prototype[k]; if(o) W.Response.prototype[k]=function(){ return conta(o.apply(this,arguments)); }; }
 const contaEv=(alvo)=>{ const fim=abre(); alvo.addEventListener('loadend',fim); return fim; };
 if(W.FileReader) for(const k of ['readAsText','readAsDataURL','readAsArrayBuffer','readAsBinaryString']){ const o=W.FileReader.prototype[k]; if(o) W.FileReader.prototype[k]=function(){ const fim=contaEv(this); try{ return o.apply(this,arguments); }catch(e){ fim(); throw e; } }; }
 if(W.Blob) for(const k of ['text','arrayBuffer']){ const o=W.Blob.prototype[k]; if(o) W.Blob.prototype[k]=function(){ return conta(o.apply(this,arguments)); }; }
 try{ const cs=W.crypto&&W.crypto.subtle, dg=cs&&cs.digest; if(dg) cs.digest=function(){ return conta(dg.apply(cs,arguments)); }; }catch(e){}
 if(W.createImageBitmap){ const ci=W.createImageBitmap; W.createImageBitmap=function(){ return conta(ci.apply(W,arguments)); }; }
 if(W.XMLHttpRequest){ const xs=W.XMLHttpRequest.prototype.send; W.XMLHttpRequest.prototype.send=function(){ const fim=contaEv(this); try{ return xs.apply(this,arguments); }catch(e){ fim(); throw e; } }; }
 try{ if(W.navigation) W.navigation.addEventListener('navigate',e=>{ if(e.hashChange||e.downloadRequest||(e.destination&&e.destination.sameDocument)){ toca(); return; } q.nav=1; }); }catch(e){}
 W.addEventListener('beforeunload',()=>{ q.nav=1; }); W.addEventListener('pagehide',()=>{ q.nav=1; });
 W.addEventListener('hashchange',toca); W.addEventListener('popstate',toca); W.addEventListener('resize',toca);
 const anima=()=>{ try{ return document.getAnimations().some(a=>{ if(a.playState!=='running') return false; const t=a.effect&&a.effect.getComputedTiming&&a.effect.getComputedTiming(); return !!t&&isFinite(t.endTime); }); }catch(e){ return false; } };
 /* base: ms até o fim desta espera (teto); fixo: ms até o fim dela no relógio da espera fixa (teto + crédito) */
 q.estado=(base,fixo)=>{ const t=agora(), lim=t+fixo; let ocupado='';
   if([...q.tm.values()].some(d=>d<=lim)) ocupado='timer'; else if([...q.iv.values()].some(r=>r.prox<=lim)) ocupado='intervalo';
   else if(q.redeC.some(c0=>t+c0<lim)) ocupado='rede';
   else if(base>0){ if(q.nav) ocupado='navegação'; else if(document.readyState!=='complete') ocupado='carga';
     else if(anima()) ocupado='animação'; else if(document.fonts&&document.fonts.status==='loading') ocupado='fonte';
     else if([...document.images].some(i=>!i.complete)) ocupado='imagem'; }
   return {id:q.id, ocioso:Math.max(0,t-Math.max(q.t,q.raf,q.fimRede)), ocupado};
 };
}catch(e){} })()"""
PRONTO_JS = "!!window.__sfq && !window.__sfq.nav && document.readyState==='complete' && !!document.body && document.body.innerText.length>50"


def _ativo():
    while _USO and getattr(_USO[-1], '_fechado', False): _USO.pop()
    return _USO[-1] if _USO else None


def credito():
    """Crédito atual em segundos (quanto o teste está adiantado em relação às esperas fixas)."""
    return _CRED[0]


class Assenta:
    """Espera por condição, comum ao cdp.Chrome e ao comp_lib.Chrome (e às subclasses que não chamam o __init__ daqui)."""
    _quieto = False
    _cred_pag = None      # crédito (ms) já posto nas páginas deste navegador
    _cred_script = None   # identificador do script que põe o crédito em todo documento novo

    def _usou(self):
        if _USO and _USO[-1] is self: return
        try: _USO.remove(self)
        except ValueError: pass
        _USO.append(self)

    def _garante_quieto(self):
        if self._quieto or not CONDICAO: return
        self._quieto = True
        try:
            self.call('Page.addScriptToEvaluateOnNewDocument', {'source': QUIETO_JS})
            self.call('Runtime.evaluate', {'expression': QUIETO_JS})
        except Exception:
            self._quieto = False

    def _poe_credito(self):
        """Leva o crédito atual (ms) ao documento aberto e a todo documento novo deste navegador."""
        ms = int(round(_CRED[0] * 1000))
        if ms == self._cred_pag or getattr(self, '_fechado', False): return
        try:
            self.call('Runtime.evaluate', {'expression': f'window.__sfcred={ms}'}, timeout=5)
            if self._cred_script: self.call('Page.removeScriptToEvaluateOnNewDocument', {'identifier': self._cred_script}, timeout=5)
            self._cred_script = self.call('Page.addScriptToEvaluateOnNewDocument', {'source': f'window.__sfcred={ms}'}, timeout=5).get('identifier')
            self._cred_pag = ms
        except Exception:
            self._cred_pag = None

    def _antes(self, method):
        """Navegação pelo protocolo: o documento atual fica marcado até ser trocado (o novo nasce sem a marca)."""
        if CONDICAO and self._quieto and method in _NAVEGA:
            try: self.call('Runtime.evaluate', {'expression': 'window.__sfq&&(window.__sfq.nav=1)'}, timeout=5)
            except Exception: pass

    def _depois(self, method, res):
        # Page.navigate sem loaderId = navegação no mesmo documento (só a âncora): nenhum documento novo vai chegar
        if CONDICAO and self._quieto and method == 'Page.navigate' and isinstance(res, dict) and not res.get('loaderId'):
            try: self.call('Runtime.evaluate', {'expression': 'window.__sfq&&(window.__sfq.nav=0)'}, timeout=5)
            except Exception: pass

    def settle(self, quieto=0.3, teto=5):
        """Espera a página assentar: nada acontecendo por `quieto` s (contados a partir desta chamada), no máximo `teto` s. Passa do
        teto só para o timer ou pedido de rede que, no relógio da espera fixa, já teria vencido (crédito, acima), e nunca além de
        teto + crédito. SAFRION_ESPERA=fixa (ou navegador fechado): dorme `teto`, como antes."""
        if teto is None or teto <= 0: return
        if not CONDICAO or getattr(self, '_fechado', False): return _dormir(teto)
        t0 = time.monotonic(); c = _CRED[0]; fim_base = t0 + teto; fim = fim_base + c
        self._garante_quieto(); self._poe_credito()
        base = t0; estendeu = False; livre = None
        try:
            while True:
                agora = time.monotonic()
                if agora >= fim: return
                try:
                    # a resposta não pode levar a espera além do limite: sem resposta até lá, o limite venceu (a atrasada é descartada)
                    r = self.call('Runtime.evaluate', {'expression': f'window.__sfq?window.__sfq.estado({int((fim_base - agora) * 1000)},{int((fim - agora) * 1000)}):null',
                                                       'returnByValue': True}, timeout=max(.02, fim - agora))
                    st = (r.get('result') or {}).get('value')
                except Exception:
                    st = None
                agora = time.monotonic()
                if not st:
                    if agora >= fim_base: return   # sem leitura da página, não passa do teto
                    base = agora
                elif st.get('ocupado'):
                    base = agora; livre = None
                    if agora >= fim_base: estendeu = True
                else:
                    base = max(base, agora - float(st.get('ocioso') or 0) / 1000.0)
                    if agora - base >= quieto: return
                    if agora >= fim_base:
                        if not estendeu: return          # nada do relógio fixo pendente: volta no teto, como antes
                        if livre is None: livre = agora   # o timer que se esperou venceu: até `quieto` s para a página reagir
                        if agora - livre >= quieto: return
                agora = time.monotonic()
                if agora >= fim: return
                _dormir(min(.05, fim - agora))
        finally:
            # o crédito novo vale já para o que a próxima ação do teste criar na página (timer, pedido de rede)
            _CRED[0] = max(0.0, c + teto - (time.monotonic() - t0)); self._poe_credito()

    def espera_acao(self, teto):
        """No lugar do time.sleep(teto) curto depois de clicar ou mudar um campo nos apoios: assenta com a janela quieta
        proporcional (metade do teto, até 0,3 s) e nunca passa do teto (mais o crédito, como no settle). SAFRION_ESPERA=fixa: dorme o teto."""
        return self.settle(min(.3, teto / 2.0), teto)

    def _ir(self, url, espera, depois, laco, passo=0.25):
        """goto por condição com o mesmo teto do goto antigo: navega, espera o documento novo completo e com texto (o laço antigo
        começava depois de `espera`, olhava a cada `passo` s e ia até `laco` s) e assenta até max(início + espera, pronto) + depois,
        com o pronto arredondado para cima ao passo do laço antigo (o momento em que o laço antigo o teria visto)."""
        self._garante_quieto(); self._poe_credito()
        t0 = time.monotonic()
        self.call('Page.navigate', {'url': url})
        limite = t0 + espera + laco; pronto = None
        while True:
            try: ok = self.js(PRONTO_JS)
            except Exception: ok = False
            agora = time.monotonic()
            if ok: pronto = agora; break
            if agora >= limite: break
            _dormir(.05)
        if pronto is not None and pronto > t0 + espera:
            pronto = t0 + espera + math.ceil((pronto - t0 - espera) / passo - 1e-9) * passo
        self.settle(.3, max(t0 + espera, pronto or time.monotonic()) + depois - time.monotonic())


def _do_teste(arq):
    """time.sleep chamado de um teste ou apoio do protótipo (tools/prototipo/v37), não do cdp.py nem da biblioteca padrão."""
    try:
        a = os.path.abspath(arq)
        return a.startswith(_V37 + os.sep) and os.path.basename(a) != 'cdp.py'
    except Exception:
        return False


_ARVORES, _LACO = {}, {}


def _em_laco(arq, linha):
    """O time.sleep está dentro de um laço (for/while/compreensão) no arquivo do teste? Laço que dorme é sondagem com orçamento
    de tempo real (ex.: "espera o aviso sair de cima", até 10 × 1 s): encurtar cada volta encurtaria o orçamento. Fica fixo."""
    k = (arq, linha)
    if k not in _LACO:
        try:
            import ast
            if arq not in _ARVORES: _ARVORES[arq] = ast.parse(open(arq, encoding='utf-8').read())
            laco = (ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
            _LACO[k] = any(isinstance(n, laco) and n.lineno <= linha <= getattr(n, 'end_lineno', n.lineno) for n in ast.walk(_ARVORES[arq]))
        except Exception:
            _LACO[k] = True   # na dúvida, a espera fixa de antes
    return _LACO[k]


def _sono(x):
    try: s = float(x)
    except Exception: return _dormir(x)
    # só no fio principal: o time.sleep de um servidor ou ajudante em outro fio é tempo real (e o navegador não é dele)
    if CONDICAO and s >= 1.0 and threading.current_thread() is threading.main_thread():
        try: f = sys._getframe(1); arq, linha = f.f_code.co_filename, f.f_lineno
        except Exception: arq, linha = '', 0
        if _do_teste(arq) and not _em_laco(arq, linha):
            nav = _ativo()
            if nav is not None: return nav.settle(.3, s)
    return _dormir(x)


if CONDICAO and getattr(time.sleep, '__name__', '') != '_sono':
    time.sleep = _sono


class Chrome(Assenta):
    def __init__(self,port=9333,w=1440,h=1100):
        self.dir=tempfile.mkdtemp(prefix='cdp_'); self.port=port
        # CDP_GL=1: WebGL por software (SwiftShader) para o mapa real (MapLibre); sem a variável, o de sempre (sem GPU)
        gl=(['--use-angle=swiftshader','--enable-unsafe-swiftshader'] if os.environ.get('CDP_GL')=='1' else ['--disable-gpu'])
        self.p=subprocess.Popen([CH,'--headless=new']+gl+['--hide-scrollbars',f'--remote-debugging-port={port}',f'--user-data-dir={self.dir}',f'--window-size={w},{h}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        # 03/10: com a máquina carregada o Chrome pode demorar; espera até 60 s e, se não subir, encerra o processo e apaga o perfil
        # (antes ficava um Chrome órfão por falha e o erro era UnboundLocalError: tabs). atexit fecha o Chrome se o teste cair.
        atexit.register(self.close)
        tabs=None; fim=time.monotonic()+60
        while time.monotonic()<fim:
            try: tabs=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json',timeout=5)); break
            except Exception: time.sleep(0.3)
        pages=[x for x in (tabs or []) if x.get('type')=='page']
        if not pages:
            self.close(); raise RuntimeError(f'Chrome headless não respondeu em 60 s na porta {port} (máquina carregada?)')
        self.ws=WS(pages[0]['webSocketDebuggerUrl']); self.i=0
        self.call('Page.enable'); self.call('Runtime.enable'); self._garante_quieto()
    def call(self,method,params=None,timeout=60):
        self._usou(); self._antes(method)
        self.i+=1; mid=self.i; self.ws.send(json.dumps({'id':mid,'method':method,'params':params or {}}))
        deadline=time.monotonic()+timeout
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0: raise TimeoutError(method)
            try: m=json.loads(self.ws.recv(timeout=remaining))
            except (TimeoutError,socket.timeout) as exc: raise TimeoutError(method) from exc
            if m.get('id')==mid:
                if 'error' in m: raise RuntimeError(f"{method}: {m['error']}")
                res=m.get('result',{}); self._depois(method,res); return res
    def js(self,expr):
        r=self.call('Runtime.evaluate',{'expression':expr,'awaitPromise':True,'returnByValue':True})
        if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'].get('text','js'))
        return r['result'].get('value')
    def goto(self,url,wait=2.5):
        # ACELERA: por condição, mesmo teto (wait + laço + 0,6 s); SAFRION_ESPERA=fixa: as esperas fixas de antes
        if CONDICAO: return self._ir(url,wait,0.6,40*0.25)
        self.call('Page.navigate',{'url':url}); _dormir(wait)
        for _ in range(40):
            if self.js("document.readyState")=='complete' and self.js("document.body && document.body.innerText.length>50"): break
            _dormir(0.25)
        _dormir(0.6)
    def size(self,w,h):
        self.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':w<500})
    def shot(self,path):
        d=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
        open(path,'wb').write(base64.b64decode(d['data']))
    def close(self):
        if getattr(self,'_fechado',False): return
        self._fechado=True
        try: self.p.terminate(); self.p.wait(5)
        except Exception:
            try: self.p.kill(); self.p.wait(5)   # Chrome travado ignora o SIGTERM
            except Exception: pass
        shutil.rmtree(self.dir,ignore_errors=True)
