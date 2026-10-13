# roda um teste e, a cada settle que volta antes do teto, mostra os timers pendentes (vencimento e código) da página
import sys, os, time, runpy
teste=sys.argv[1]; sys.argv=[teste]+sys.argv[2:]
sys.path.insert(0, os.path.dirname(os.path.abspath(teste)))
import cdp
LOG=r"""(()=>{ const st=window.setTimeout; window.__tsrc=new Map(); window.setTimeout=function(f,ms,...a){ const id=st.call(window,f,ms,...a); window.__tsrc.set(id,[Math.round(performance.now()+(+ms||0)),String(f).replace(/\s+/g,' ').slice(0,100)]); return id; }; })()"""
og=cdp.Assenta._garante_quieto
def gq(self):
    novo=not self._quieto; og(self)
    if novo and self._quieto: self.call('Page.addScriptToEvaluateOnNewDocument',{'source':LOG})
cdp.Assenta._garante_quieto=gq
orig=cdp.Assenta.settle; n=[0]
def settle(self, quieto=0.3, teto=5):
    f=sys._getframe(1); g=f.f_back
    a=time.monotonic(); r=orig(self, quieto, teto); d=time.monotonic()-a; n[0]+=1
    try:
        pend=self.js("(()=>{ const q=window.__sfq, now=performance.now(); if(!q||!window.__tsrc) return []; return [...q.tm.entries()].map(([id,due])=>[Math.round(due-now),(window.__tsrc.get(id)||[0,'?'])[1]]).filter(x=>x[0]<8000); })()")
    except Exception as e: pend=str(e)[:60]
    print(f'   [settle {n[0]} {os.path.basename(g.f_code.co_filename)}:{g.f_lineno} teto={teto:.2f} real={d:.2f}] pendentes={pend}', flush=True)
    return r
cdp.Assenta.settle=settle
runpy.run_path(teste, run_name='__main__')
