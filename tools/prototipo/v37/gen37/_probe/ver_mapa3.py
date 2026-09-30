# -*- coding: utf-8 -*-
"""Verificador 3 (IN-04): capturas e textos dos painéis na camada Irrigação e Integrado, Todas/Boa Vista, sobreposição do aviso."""
import json, time
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def tap(s,t): s.js(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
def pan(s): return (s.js("(document.querySelector('aside[aria-label]')||{innerText:''}).innerText") or '').replace('\n',' / ')
def links(s): return s.js("[...document.querySelectorAll('aside[aria-label] a, aside[aria-label] button')].map(a=>a.innerText.trim()+' → '+(a.getAttribute('href')||'fn'))")
def labs(s): return s.js(f"{SV}.map(x=>x.getAttribute('aria-label')+' '+x.getAttribute('fill'))")
def faz(s,v):
    s.js("""((v)=>{const i=document.querySelector('select[aria-label="Filtrar por fazenda"]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})"""+f"({json.dumps(v)})"); time.sleep(.4)
s=Sess(1440,900)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('IN-04.dc.html')
    print('HEAD:',s.head()); print('LABS Integrado:',labs(s))
    print('NUMS:',s.js("document.querySelector('[role=group][aria-label^=\"Indicadores\"]').innerText.replace(/\\n/g,' ')"))
    print('LEG:',s.js("(([...document.querySelectorAll('div')].filter(d=>d.innerText.trim().endsWith('Geometria e valores demonstrativos.')).pop())||{innerText:''}).innerText.replace(/\\n/g,' / ')"))
    for t in ['P2','T7','P1','T4']:
        tap(s,t); print(f'--- Integrado {t}:',pan(s)[:900]); print('    ações:',links(s)); tap(s,t)
    s.shot('ver_in04_integrado.png')
    s.click('Irrigação','nav[role=tablist]'); print('LABS Irrig balanço:',labs(s))
    print('FONTE:',s.js("[...document.querySelectorAll('div[title]')].map(d=>d.title).filter(Boolean)[0]"))
    s.click('Programação de hoje'); print('LABS Irrig prog:',labs(s))
    print('NUMS:',s.js("document.querySelector('[role=group][aria-label^=\"Indicadores\"]').innerText.replace(/\\n/g,' ')"))
    for t in ['P2','T7','P1']:
        tap(s,t); print(f'--- Irrigação {t}:',pan(s)[:900]); print('    ações:',links(s))
        if t=='T7': s.shot('ver_in04_irrig_T7.png')
        if t=='P2': s.shot('ver_in04_irrig_P2.png')
        tap(s,t)
    s.click('Ordens de serviço','nav[role=tablist]')
    for t in ['P2','P1','T7','T4']:
        tap(s,t); print(f'--- OS {t}:',pan(s)[:900]); print('    ações:',links(s)); tap(s,t)
    faz(s,'Todas'); s.click('Integrado','nav[role=tablist]'); s.shot('ver_in04_todas.png')
    print('Todas HEAD:',s.head()); print('Todas NUMS:',s.js("document.querySelector('[role=group][aria-label^=\"Indicadores\"]').innerText.replace(/\\n/g,' ')"))
    ov=s.js("""(()=>{const a=[...document.querySelectorAll('span[role=note]')].find(x=>x.innerText.includes('Boa Vista')); const h=[...document.querySelectorAll('span')].find(x=>x.innerText.includes('clique no talhão para ver detalhes')&&x.style.position==='absolute'); if(!a||!h) return [!!a,!!h]; const r1=a.getBoundingClientRect(), r2=h.getBoundingClientRect(); return [[r1.top,r1.bottom,r1.left,r1.right],[r2.top,r2.bottom,r2.left,r2.right]];})()""")
    print('aviso × dica (top,bottom,left,right):',ov)
    faz(s,'Boa Vista'); s.shot('ver_in04_boavista.png'); print('BV HEAD:',s.head()); print('BV body trecho:',s.body()[-600:].replace('\n',' / '))
    for L in ['Satélite','Irrigação','Pragas e doenças']:
        s.click(L,'nav[role=tablist]'); print(f'BV {L}: fonte=',s.js("[...document.querySelectorAll('div[title]')].map(d=>d.title).filter(Boolean)[0]"),' botões=',s.js("[...document.querySelectorAll('main button, main a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim()).filter(Boolean).slice(0,30)"))
    s.shot('ver_in04_boavista_pragas.png')
    print('erros:',s.errs())
finally:
    s.close()
