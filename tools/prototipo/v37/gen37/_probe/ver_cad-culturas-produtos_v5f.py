# -*- coding: utf-8 -*-
"""v5 · confirmação de exclusão na linha: rolagem lateral nas três telas? e a exclusão efetiva + selo."""
import os, importlib.util, time, json
H=os.path.dirname(os.path.abspath(__file__))
def ld(n):
    sp=importlib.util.spec_from_file_location(n,os.path.join(H,n+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
L=ld('ver_cad-culturas-produtos_lib'); M=ld('ver_cad-culturas-produtos_v5m')
v=L.V()
SELO="(()=>{const h=document.querySelector('header h1'); const s=h&&h.parentElement.querySelector('span[style*=border-radius]'); return s?[s.innerText.trim(),getComputedStyle(s).backgroundColor]:null;})()"
TW="[...document.querySelectorAll('[role=table]')].map(t=>{let e=t; while(e&&e!==document.body){ if(e.scrollWidth>e.clientWidth+1&&['auto','scroll'].includes(getComputedStyle(e).overflowX)) return [e.scrollWidth,e.clientWidth]; e=e.parentElement;} return 'sem rolagem';})"
def lixo(txt):
    return M.mclick(v,f"(()=>{{const r={v.ROW(txt)}; return r&&[...r.querySelectorAll('button')].pop();}})()")
def confirma(txt,b='Excluir'):
    return M.mclick(v,f"(()=>{{const r={v.ROW(txt)}; return r&&[...r.querySelectorAll('button')].find(x=>x.innerText.trim()==={json.dumps(b)});}})()")
try:
    for f,row in [('CD-06.dc.html','Calcário'),('CD-02.dc.html','64 Z'),('CD-07.dc.html','PRJ-PIVO3')]:
        v.goto(f); v.J("localStorage.clear()"); v.goto(f)
        v.info(f+' antes',[v.J(TW),v.J(SELO)])
        lixo(row); v.info(f+' confirmação aberta',[v.rowtxt(row),v.J(TW)])
        v.shot('ver_cadc_v5f_'+f[:5]+'.png')
        confirma(row); v.info(f+' depois de Excluir',[v.rowtxt(row),v.J(TW),v.J(SELO),v.toast()])
    v.info('erros',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
