# -*- coding: utf-8 -*-
"""Evidência do estado ANTES (UX-ACAO-UNICA v2): faixa clicável, setas e ações concorrentes no Planejar safra e nos outros processos."""
import sys, os, time, json
HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,HERE)
from cadc_lib import T
t=T(); J=t.J
EST="""(()=>{const nav=document.querySelector('[aria-label="Etapas do processo"]'); const vis=e=>!!e&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden';
 const steps=nav?[...nav.querySelectorAll('button,a')].filter(b=>!b.getAttribute('aria-label')):[];
 const setas=nav?[...nav.querySelectorAll('button,a')].filter(b=>/Etapa anterior|Próxima etapa/.test(b.getAttribute('aria-label')||'')).filter(vis).map(b=>b.getAttribute('aria-label')):[];
 const prim=[...document.querySelectorAll('button,a')].filter(vis).filter(b=>{const c=getComputedStyle(b); return c.backgroundColor==='rgb(30, 122, 76)'&&!b.closest('.menu-lat')&&!b.closest('[aria-label="Etapas do processo"]');}).map(b=>b.innerText.trim());
 const cur=document.querySelector('[aria-current=step]');
 return {tag:nav&&nav.tagName, passosClicaveis:steps.length, tabStops:steps.filter(b=>b.tabIndex>=0).length, setas, primarios:prim, atual:cur&&cur.innerText.replace(/\\s+/g,' '),
  blocoAcoes:[...document.querySelectorAll('main section h3')].filter(vis).map(h=>h.parentElement.parentElement.innerText.split('\\n').slice(-3).join(' / '))};})()"""
try:
    for w,h,nome in [(1440,900,'desk'),(360,800,'cel')]:
        t.c.size(w,h)
        for pag,hash_ in [('SAF.dc.html','#saf=S2627&etapa=2'),('CMP.dc.html','#saf=S2627'),('PA.dc.html',''),('EST.dc.html',''),('PM.dc.html','')]:
            t.goto(pag+hash_); time.sleep(.6)
            print(nome,pag+hash_,json.dumps(J(EST),ensure_ascii=False))
            if pag=='SAF.dc.html': t.shot(f'acao_antes_saf2_{nome}.png')
    print('erros:',t.errs())
finally:
    t.fim()
