# -*- coding: utf-8 -*-
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
HERE=os.path.dirname(os.path.abspath(__file__)); R=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'_render')
p=free(); srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(.8)
c=Chrome(port=free()); J=c.js
try:
    for w in [1440,1366,1280]:
        c.size(w,900); c.goto(f'http://127.0.0.1:{p}/OS.dc.html',wait=1.2)
        ov=J("(()=>{const t=document.querySelector('[role=table]').parentElement; return [t.scrollWidth,t.clientWidth, document.documentElement.scrollWidth, window.innerWidth];})()")
        cells=J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('OS-0431')===0); return [...r.querySelectorAll('[role=cell]')].map(c=>[c.clientWidth,c.scrollWidth]);})()")
        print(w, 'lista', ov, 'OS-0431 cells', cells)
        J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('OS-0431')===0); r.click();})()"); time.sleep(.5)
        pw=J("(()=>{const a=document.querySelector('aside[role=dialog]'); return [a.scrollWidth,a.clientWidth];})()"); print('   painel', pw)
        if w==1280: c.shot(os.path.join(HERE,'_probe','verif_os_1280.png'))
finally:
    c.close(); srv.terminate()
