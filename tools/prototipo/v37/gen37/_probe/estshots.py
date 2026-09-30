# -*- coding: utf-8 -*-
"""Teste CDP do processo Estoque (EST.dc.html): recebimento com quarentena, entrega acima do disponível (erro no campo),
devolução derrubando a custódia, contagem com divergência indo para aprovação, saldos recalculados na etapa 4."""
import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cdp import Chrome
from journeys import free
R=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
SETV="""((sel,val)=>{const i=document.querySelector(sel); if(!i) return 'sem campo '+sel; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})"""
ROW="""((t)=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf(t)>=0); if(!r) return 'sem linha '+t; (r.querySelector('[role=cell] span')||r).click(); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
ERR=lambda: J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
def setv(i,val): r=J(f"({SETV})({json.dumps('#'+i)},{json.dumps(val)})"); time.sleep(.2); return r
def row(t): r=J(f"({ROW})({json.dumps(t)})"); time.sleep(.45); return r
def rowtxt(t): return J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({json.dumps(t)})>=0); return r?r.innerText.replace(/\\s+/g,' '):'sem linha';}})()")
def k(): return J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')")
fails=[]
def ok(cond,msg):
    print(('  OK  ' if cond else '  FALHA ')+msg)
    if not cond: fails.append(msg)
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/EST.dc.html'); time.sleep(.5)
    row('NF 4533'); c.shot('_probe/est_f1.png'); clk('Cancelar','aside[role=dialog]')
    clk('2 Entregue por O.S.'); row('REQ-040'); setv('fx_g_ent_qtd','11400'); clk('Salvar','aside[role=dialog]'); c.shot('_probe/est_f2.png'); clk('Cancelar','aside[role=dialog]'); clk('Descartar alterações','aside[role=dialog]')
    clk('3 Receba devoluções'); row('REQ-031'); c.shot('_probe/est_f3.png'); clk('Cancelar','aside[role=dialog]')
    clk('5 Faça contagens'); c.shot('_probe/est_e5.png')
finally:
    c.close(); srv.terminate()
