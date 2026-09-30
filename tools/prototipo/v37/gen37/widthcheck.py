# -*- coding: utf-8 -*-
"""Mede grades mais largas que sua área (rolagem horizontal) em cada tela, inclusive em todas as etapas dos processos."""
import sys, os, time, subprocess, json, glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render')
JS0="""[...document.querySelectorAll('[role=table]')].map((t,i)=>{const w=t.parentElement; return [i, w.scrollWidth-w.clientWidth];}).filter(x=>x[1]>2)"""
JS="(()=>{const g="+JS0+"; const n=document.querySelector('nav[aria-label=\"Etapas do processo\"]'); const s=n?[...n.querySelectorAll('button,a')].filter(b=>b.getBoundingClientRect().right>n.getBoundingClientRect().right+1).length:0; const pg=document.documentElement.scrollWidth-document.documentElement.clientWidth; return (g.length||s||pg>2)?{grades:g,etapas_cortadas:s,pagina:pg}:null;})()"
def run(files,width=1440):
    p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
    c=Chrome(port=free()); out={}
    try:
        c.size(width,1000)
        for f in files:
            c.goto(f'http://127.0.0.1:{p}/{f}',wait=1.2)
            c.js(f"(()=>{{const r=document.querySelector('[data-root]'); if(r) r.style.width='{width}px';}})()"); time.sleep(.3)
            n=c.js("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button').length") or 0
            res={}
            if n and f in ('SAF.dc.html',):
                c.js("(()=>{const b=[...document.querySelectorAll('button')].find(b=>/Abrir safra/.test(b.innerText)); if(b) b.click();})()"); time.sleep(.4)
            for s in range(max(1,n)):
                if n: c.js(f"document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[{s}].click()"); time.sleep(.35)
                r=c.js(JS)
                if r: res[f'etapa{s+1}' if n else 'tela']=r
            if os.environ.get('SHOT'): c.shot(f'_probe/w{width}_'+f.replace('.dc.html','.png'))
            if res: out[f]=res
    finally:
        c.close(); srv.terminate()
    return out
if __name__=='__main__':
    w=int(os.environ.get('W','1440'))
    fs=sys.argv[1:] or sorted(os.path.basename(x) for x in glob.glob(R+'/*.dc.html'))
    o=run(fs,w); print(json.dumps(o,ensure_ascii=False)); print(len(o),'telas com grade mais larga que a área')
