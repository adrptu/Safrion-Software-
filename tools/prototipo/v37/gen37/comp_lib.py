# -*- coding: utf-8 -*-
"""Apoio do componentes_test.py (QUALIDADE-ARTEFATO-20261003 RESPONSIVIDADE, UX-FEEDBACK-INTERACAO e MAPA-ICONES).
Chrome headless por CDP com emulação de aparelho (largura × altura em px CSS, escala, toque, sem hover) e medidas que o
widthcheck não vê: ocultação dos elementos-chave (elementFromPoint), comando principal alcançável, área útil, fonte mínima,
painel lateral dentro da tela. É emulação: não substitui aparelho físico nem o Safari do iPhone."""
import os, sys, time, json, subprocess, tempfile, shutil, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from cdp import WS, CH, Assenta, CONDICAO, _dormir
from journeys import free
from cadc_lib import ERRS
# Caminho único entre as etapas de um processo guiado (UX-ACAO-UNICA-20261003): a faixa só informa; o teste anda pela área de ações,
# como a pessoa: avanço (data-acao=avancar) ou retorno (data-acao=voltar); para a etapa 1 sem retorno, o "Trocar safra" do topo.
IR_ETAPA=r"""(async (n)=>{ const num=()=>{ const c=document.querySelector('.etp-ind [aria-current=step]'); return c?Number((c.innerText.match(/\d+/)||[0])[0]):0; };
  for(let k=0;k<10;k++){ const i=num(); if(i===n) return i;
    let b=document.querySelector(i<n?'[data-acoes] [data-acao=avancar]':'[data-acoes] [data-acao=voltar]');
    if(!b&&i>n&&n===1) b=[...document.querySelectorAll('header button')].find(x=>x.innerText.trim()==='Trocar safra');
    if(!b) return 'sem caminho de '+i+' para '+n; b.click(); await new Promise(r=>setTimeout(r,450)); }
  return 'não chegou: '+num(); })"""

class Chrome(Assenta):
    """Abre um Chrome próprio (CDP_GL=1: WebGL por software para o mapa real) ou anexa a um já aberto (CDP_PORT)."""
    def __init__(self,espera=90):
        self.p=None; self.dir=None; self.alvo=None; porta=os.environ.get('CDP_PORT')
        if porta: self.port=int(porta)
        else:
            self.port=free(); self.dir=tempfile.mkdtemp(prefix='cdp_')
            gl=(['--use-angle=swiftshader','--enable-unsafe-swiftshader'] if os.environ.get('CDP_GL')=='1' else ['--disable-gpu'])
            self.p=subprocess.Popen([CH,'--headless=new']+gl+['--hide-scrollbars',f'--remote-debugging-port={self.port}',f'--user-data-dir={self.dir}','--window-size=1440,900','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        fim=time.time()+espera
        while True:
            try: urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/version',timeout=5); break
            except Exception:
                if time.time()>fim: raise
                time.sleep(.4)
        t=json.load(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{self.port}/json/new?about:blank',method='PUT'),timeout=30)); self.alvo=t['id']
        self.ws=WS(t['webSocketDebuggerUrl']); self.i=0
        self.call('Page.enable'); self.call('Runtime.enable'); self.call('Page.addScriptToEvaluateOnNewDocument',{'source':ERRS}); self._garante_quieto()
        try: self.call('Emulation.setFocusEmulationEnabled',{'enabled':True})   # página com foco, como a janela ativa de quem usa
        except Exception: pass
    def call(self,method,params=None,timeout=60):
        self._usou(); self._antes(method)
        self.i+=1; mid=self.i; self.ws.send(json.dumps({'id':mid,'method':method,'params':params or {}})); fim=time.monotonic()+timeout
        while True:
            m=json.loads(self.ws.recv(timeout=max(.1,fim-time.monotonic())))
            if m.get('id')==mid:
                if 'error' in m: raise RuntimeError(f"{method}: {m['error']}")
                res=m.get('result',{}); self._depois(method,res); return res
    def js(self,expr):
        r=self.call('Runtime.evaluate',{'expression':expr,'awaitPromise':True,'returnByValue':True})
        if 'exceptionDetails' in r: raise RuntimeError(str(r['exceptionDetails'].get('exception',{}).get('description') or r['exceptionDetails'].get('text'))[:400])
        return r['result'].get('value')
    def aparelho(self,w,h,escala=1,toque=False):
        """Janela de w × h px CSS. toque=True: celular/tablet (meta viewport vale, toque, ponteiro grosso e sem hover)."""
        self.call('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':escala,'mobile':bool(toque),
                  'screenOrientation':{'type':'portraitPrimary' if h>=w else 'landscapePrimary','angle':0 if h>=w else 90}})
        self.call('Emulation.setTouchEmulationEnabled',{'enabled':bool(toque),'maxTouchPoints':5 if toque else 1})
        self.call('Emulation.setEmulatedMedia',{'features':[{'name':'hover','value':'none' if toque else 'hover'},{'name':'pointer','value':'coarse' if toque else 'fine'}]})
        time.sleep(.3)
    def goto(self,url,espera=.6):
        # ACELERA (cdp.Assenta): por condição, mesmo teto (espera + laço + 0,4 s); SAFRION_ESPERA=fixa: as esperas fixas de antes
        if CONDICAO: return self._ir(url,espera,.4,60*.2,.2)
        self.call('Page.navigate',{'url':url}); _dormir(espera)
        for _ in range(60):
            try:
                if self.js("document.readyState")=='complete' and self.js("!!document.body && document.body.innerText.length>50"): break
            except Exception: pass
            _dormir(.2)
        _dormir(.4)
    def shot(self,path):
        import base64
        d=self.call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False}); open(path,'wb').write(base64.b64decode(d['data']))
    def tecla(self,key,code=None,vk=0,text=None,mod=0):
        p={'type':'keyDown','key':key,'code':code or key,'windowsVirtualKeyCode':vk,'modifiers':mod}
        if text: p['text']=text
        self.call('Input.dispatchKeyEvent',p); self.call('Input.dispatchKeyEvent',{'type':'keyUp','key':key,'code':code or key,'windowsVirtualKeyCode':vk,'modifiers':mod}); time.sleep(.08)
    def tab(self,n=1,shift=False):
        for _ in range(n): self.tecla('Tab','Tab',9,mod=8 if shift else 0)
    def mouse(self,x,y,tipo='mouseMoved',botao='none'):
        self.call('Input.dispatchMouseEvent',{'type':tipo,'x':x,'y':y,'button':botao,'clickCount':1 if botao!='none' else 0}); time.sleep(.05)
    def toque(self,x,y):
        self.call('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]}); time.sleep(.05)
        self.call('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]}); time.sleep(.35)
    def close(self):
        self._fechado=True   # a espera por condição deixa de usar este navegador
        try:
            if self.alvo: urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/close/{self.alvo}',timeout=10)
        except Exception: pass
        if self.p:
            try: self.p.terminate(); self.p.wait(5)
            except Exception: pass
        if self.dir: shutil.rmtree(self.dir,ignore_errors=True)

def servir(d):
    p=free(); s=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',d],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.5); return p,s

# ---------- medida de responsividade de uma tela ----------
# chave: título, comando principal (botões verdes do cabeçalho/conteúdo), faixa de etapas, botão do menu, área útil do conteúdo.
# "visível" = o ponto central do elemento cai nele (nada por cima); "alcançável" = visível depois de rolar a região que o contém.
MEDE=r"""(()=>{
 const vw=innerWidth, vh=innerHeight, n=s=>(s||'').replace(/\s+/g,' ').trim();
 const vis=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'&&cs.opacity!=='0'; };
 const topo=e=>{ const r=e.getBoundingClientRect(); const x=Math.min(Math.max(r.left+Math.min(r.width/2,24),1),vw-1), y=r.top+r.height/2; if(y<0||y>vh-1||r.right<1||r.left>vw-1) return false; const t=document.elementFromPoint(x,y); return !!t&&(e===t||e.contains(t)); };
 const guarda=e=>{ const sv=[]; for(let p=e.parentElement;p;p=p.parentElement) sv.push([p,p.scrollTop,p.scrollLeft]); return ()=>sv.forEach(([p,t,l])=>{p.scrollTop=t;p.scrollLeft=l;}); };
 const alcanca=e=>{ if(!e) return false; const volta=guarda(e); e.scrollIntoView({block:'center',inline:'nearest'}); const ok=topo(e); volta(); return ok; };
 const verde=e=>{ const cs=getComputedStyle(e); return cs.backgroundColor==='rgb(30, 122, 76)'&&parseFloat(cs.borderTopLeftRadius)<30&&!e.closest('.menu-lat,[role=tablist],[role=group],[role=listbox]'); };
 const out={vw,vh,pagLado:document.documentElement.scrollWidth>vw+1||document.body.scrollWidth>vw+1};
 const raiz=document.querySelector('[data-root]')||document.querySelector('x-dc>div,body>div'); if(raiz){ const r=raiz.getBoundingClientRect(); out.raiz=[Math.round(r.width),Math.round(r.height)]; out.raizFora=r.right>vw+1; }
 const h1=document.querySelector('h1'); if(h1){ const r=h1.getBoundingClientRect(); out.h1=n(h1.innerText).slice(0,50); out.h1ok=vis(h1)&&r.left>=-1&&r.right<=vw+1&&h1.scrollWidth<=h1.clientWidth+1&&alcanca(h1); }
 const prims=[...document.querySelectorAll('header button,header a,main button,main a')].filter(e=>vis(e)&&verde(e));
 out.prim=prims.slice(0,4).map(e=>n(e.innerText).slice(0,30)); out.primRuim=prims.filter(e=>!alcanca(e)).map(e=>n(e.innerText).slice(0,30)).slice(0,4);
 const nav=document.querySelector('.etp'); if(nav&&vis(nav)){ const at=nav.querySelector('.etp-atual'); const comp=!!(at&&vis(at)); const cur=nav.querySelector('.etp-itens [aria-current=step],.etp-itens [aria-current=page],.etp-itens [aria-current=true]');
   out.etapa=comp?n(at.innerText):(cur?n(cur.innerText):''); out.etapaOk=comp?topo(at):(!!cur&&topo(cur)); out.etapaCompacta=comp;
   const its=[...nav.querySelectorAll('.etp-itens>*')].filter(vis); let sob=0; for(let i=0;i<its.length;i++) for(let j=i+1;j<its.length;j++){ const a=its[i].getBoundingClientRect(), b=its[j].getBoundingClientRect(); if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1) sob++; } out.etapaSob=sob; }
 const tog=document.querySelector('.ml-tog'); if(tog) out.menuBtnOk=topo(tog);
 const menu=document.querySelector('.menu-lat'); const m=document.querySelector('main');
 if(menu&&m){ const a=menu.getBoundingClientRect(), b=m.getBoundingClientRect(); out.menu=[Math.round(a.width),getComputedStyle(menu).position]; out.menuCobre=a.right>b.left+1; }
 if(m){ const r=m.getBoundingClientRect(); out.mainW=Math.round(Math.min(r.right,vw)-Math.max(r.left,0)); out.util=Math.round(Math.min(r.bottom,vh)-Math.max(r.top,0));
   const col=m.parentElement; out.rolaJunto=!!col&&col.scrollHeight>col.clientHeight+1;
   const rolavel=e=>{ for(let p=e.parentElement;p&&p!==m;p=p.parentElement){ const ox=getComputedStyle(p).overflowX; if((ox==='auto'||ox==='scroll')&&p.scrollWidth>p.clientWidth) return true; } return false; };
   const corte=[...m.querySelectorAll('button,a,input,select,textarea,h2,h3,b,label')].filter(e=>vis(e)&&!e.closest('[role=dialog],aside')).filter(e=>{ const q=e.getBoundingClientRect(); return (q.right>Math.min(r.right,vw)+1||q.left<Math.max(r.left,0)-1)&&!rolavel(e); });
   out.cortados=corte.slice(0,5).map(e=>n(e.innerText||e.value||e.tagName).slice(0,26)); out.nCortados=corte.length;
   const tx=[...m.querySelectorAll('*')].filter(e=>e.children.length===0&&/[A-Za-zÀ-ÿ0-9]/.test(e.textContent)&&vis(e)); out.fonteMin=tx.length?Math.min(...tx.map(e=>parseFloat(getComputedStyle(e).fontSize))):null; }
 const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog]')].find(vis); if(d){ const r=d.getBoundingClientRect(); out.painel=[Math.round(r.left),Math.round(r.width),Math.round(r.height)]; out.painelFora=r.left<-1||r.right>vw+1;
   const bs=[...d.querySelectorAll('button')].filter(vis); const fe=bs.find(b=>/fechar/i.test(b.getAttribute('aria-label')||'')||n(b.innerText)==='×'); const pv=bs.filter(verde);
   out.painelFechar=!!fe&&alcanca(fe); out.painelPrim=pv.map(e=>n(e.innerText).slice(0,24)); out.painelPrimOk=pv.every(alcanca); }
 const zm=getComputedStyle(document.documentElement).zoom; out.escalaGlobal=(zm&&zm!=='1'&&zm!=='normal')||/scale\(/.test((raiz&&raiz.style.transform)||'');
 return out; })()"""

def resumo(m):
    """Problemas encontrados por MEDE (lista vazia = tela adaptada)."""
    p=[]
    if m.get('pagLado'): p.append('página rola de lado')
    if m.get('raizFora'): p.append('raiz mais larga que a janela')
    if m.get('h1') is not None and not m.get('h1ok'): p.append('título cortado/oculto')
    if m.get('primRuim'): p.append('comando principal inalcançável: '+', '.join(m['primRuim']))
    if 'etapaOk' in m and (not m['etapaOk'] or m.get('etapaSob')): p.append(f"etapa atual oculta/sobreposta ({m.get('etapa','')[:30]})")
    if m.get('menuBtnOk') is False: p.append('botão do menu coberto')
    if m.get('nCortados'): p.append(f"{m['nCortados']} itens cortados: {m['cortados'][:3]}")
    if m.get('util') is not None and m['util']<120 and not m.get('rolaJunto'): p.append(f"área útil {m['util']} px")
    if m.get('fonteMin') is not None and m['fonteMin']<10: p.append(f"fonte mínima {m['fonteMin']} px")
    if m.get('painel'):
        if m.get('painelFora'): p.append('painel fora da tela')
        if not m.get('painelFechar'): p.append('fechar do painel inalcançável')
        if not m.get('painelPrimOk'): p.append('ação do painel inalcançável')
    if m.get('escalaGlobal'): p.append('escala global')
    return p
