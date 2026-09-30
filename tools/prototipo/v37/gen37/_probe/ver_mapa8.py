# -*- coding: utf-8 -*-
"""Verificador 8: devolução da sobra da OS-0417 pela interface do Estoque (EST.dc.html) e efeito no Mapa (IN-04)."""
import json, time, sys
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def tap(s,t): s.js(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
def btns(s): return s.js("[...document.querySelectorAll('button,a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim().replace(/\\n/g,' ')).filter(Boolean)")
s=Sess(1440,1000)
try:
    s.go('EST.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('EST.dc.html')
    b=btns(s); print('botões EST:',b[:60])
    cand=[x for x in b if 'evolu' in x]; print('com "devolu":',cand)
    if cand:
        print('clique:',s.click(cand[0])); time.sleep(.3)
        b=btns(s); print('botões depois:',[x for x in b if 'evolu' in x or 'REQ-031' in x][:10])
        prim=[x for x in b if x.startswith('Receber devolução da')]
        if prim: print('clique prim:',s.click(prim[0])); time.sleep(.4)
        form=s.js("(()=>{const d=[...document.querySelectorAll('aside[role=dialog], [role=dialog]')].pop(); if(!d) return null; return [d.innerText.replace(/\\n/g,' / ').slice(0,600), [...d.querySelectorAll('input,select,textarea')].map(i=>[i.tagName,i.id||i.name||'',i.value, i.tagName==='SELECT'?[...i.options].map(o=>o.text):null])];})()")
        print('form:',form)
        print('salvar:',s.click('Salvar','[role=dialog]' if s.js("!!document.querySelector('[role=dialog]')") else None,exact=True)); time.sleep(.5)
        print('toast:',s.js("[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.trim()).filter(Boolean).join(' | ')"))
        print('cenário REQ-031:',s.js("(()=>{const t=localStorage.getItem('talhao-os-cenario-v1'); if(!t) return null; const c=JSON.parse(t); return [c.reqs['REQ-031'].itens[0].custodia, c.ordens['OS-0417'].etapa, JSON.stringify(c.ordens['OS-0417'].selos)];})()"))
        s.c.size(1440,900); s.go('IN-04.dc.html'); tap(s,'P1')
        it=s.js("(()=>{const a=document.querySelector('aside[aria-label]'); const d=[...a.querySelectorAll('div')].find(d=>d.style.borderRadius==='10px'&&d.innerText.startsWith('OS-0417')); return d?d.innerText.replace(/\\n/g,' / '):null;})()")
        print('Mapa · P1 · OS-0417:',it); s.shot('ver_in04_os0417_pos_devolucao.png')
        s.js("localStorage.removeItem('talhao-os-cenario-v1')")
finally:
    s.close()
