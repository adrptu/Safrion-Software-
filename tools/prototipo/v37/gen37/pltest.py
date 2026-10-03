# -*- coding: utf-8 -*-
"""Teste CDP do módulo Planejamento: PL-02 Decidir pendência (NEC-019) · PL-06 recálculo da janela de colheita · PL-04 programar pela linha."""
import sys, os, time, subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
SETV="""((sel,val)=>{const i=document.querySelector(sel); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""
BTN="""((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return true;} return false;})"""
LBL="""((l)=>{const d=[...document.querySelectorAll('aside[role=dialog] label, aside[role=dialog] div')].find(x=>x.childElementCount<=3 && (x.innerText||'').trim().startsWith(l)); if(!d) return null; const i=d.querySelector('input,select,textarea')||(d.parentElement&&d.parentElement.querySelector('input,select,textarea')); return i?('#'+i.id):null;})"""
def fid(J,k,gid): return f"#fx_{gid}_{k}"
def run(p):
    c=Chrome(port=free()); J=c.js; R={}
    try:
        c.size(1440,1100)
        # ---- PL-02 · Decidir pendência
        c.goto(f'http://127.0.0.1:{p}/PL-02.dc.html'); time.sleep(.6)
        J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Decidir pendência').click()"); time.sleep(.5)
        R['dec_abre']=J("!!document.querySelector('aside[role=dialog]') && document.querySelector('aside[role=dialog]').innerText.indexOf('Decisão da pendência')>=0")
        R['dec_sem_evid_antes']=J("!document.getElementById('fx_g_op_evid')")
        J(f"({SETV})('#fx_g_op_dec','Realizada')"); time.sleep(.3)
        R['cond_evid']=J("!!document.getElementById('fx_g_op_evid')")
        J(f"({BTN})('Salvar')"); time.sleep(.3)
        R['exige_evid']=J("document.querySelector('aside[role=dialog]').innerText.indexOf('Informe evidência')>=0")
        J(f"({SETV})('#fx_g_op_evid','Apontamento AP-2231 · 12/09')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
        R['dec_salva']=J("!document.querySelector('aside[role=dialog]') && document.body.innerText.indexOf('Realizada · evidência registrada')>=0 && ![...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Decidir pendência')")
        R['dec_aviso']=J("document.body.innerText.indexOf('NEC-019 baixada')>=0")
        # T1-A: link do talhão não edita
        R['link_talhao']=J("[...document.querySelectorAll('a')].filter(a=>a.innerText.trim()==='Ver plano do talhão').every(a=>a.getAttribute('href')==='PL-02det.dc.html')")
        R['nec028']=J("document.body.innerText.indexOf('NEC-028')>=0 && document.body.innerText.indexOf('Convertida · OS-0420')>=0")
        # ---- PL-06 · recálculo da janela
        c.goto(f'http://127.0.0.1:{p}/PL-06.dc.html'); time.sleep(.6)
        J("(()=>{const r=[...document.querySelectorAll('.g2ed')].find(x=>x.innerText.indexOf('T1-B')>=0); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
        J(f"({SETV})('#fx_g_par_plant','2026-10-28')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
        R['janela_recalc']=J("document.body.innerText.indexOf('18/02–28/02')>=0")
        # ---- PL-04 · programar pela linha
        c.goto(f'http://127.0.0.1:{p}/PL-04.dc.html'); time.sleep(.6)
        J("(()=>{const r=[...document.querySelectorAll('.g2ed')].find(x=>x.innerText.indexOf('OS-0430')>=0); r.querySelector('[role=cell]').click();})()"); time.sleep(.4)
        J(f"({SETV})('#fx_g_ord_jan','26/09')"); time.sleep(.2); J(f"({BTN})('Salvar')"); time.sleep(.5)
        R['programa']=J("document.body.innerText.indexOf('Programação de OS-0430 salva')>=0")
        R['sem_ids_colididos']=J("document.body.innerText.indexOf('dessecação T1-A')>=0 && document.body.innerText.indexOf('OS-0422')>=0 && document.body.innerText.indexOf('água Pivô 2 · próximo ciclo')>=0")
    finally: c.close()
    return R
if __name__=='__main__':
    RD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
    srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',RD],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        r=run(p); print(r); print('OK' if all(v is True for v in r.values()) else 'FALHOU')
    finally: srv.terminate()
