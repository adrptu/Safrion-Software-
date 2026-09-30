# -*- coding: utf-8 -*-
"""Verificador 9: o atalho 'Receber sobras' do Mapa (OS-0417) leva a uma tela que atualiza o cenário?"""
import json, time
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def tap(s,t): s.js(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
def btns(s): return s.js("[...document.querySelectorAll('button,a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim().replace(/\\n/g,' ')).filter(Boolean)")
s=Sess(1440,1000)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('IN-04.dc.html'); tap(s,'P1')
    h=s.js("[...document.querySelectorAll('aside[aria-label] a')].find(a=>a.innerText.trim()==='Receber sobras').getAttribute('href')"); print('Receber sobras →',h)
    s.go(h); print('título:',s.js("document.title"),'| cabeçalho:',s.head()[:200])
    b=btns(s); dv=[x for x in b if 'evolu' in x.lower() or 'sobra' in x.lower()]; print('botões com devolução/sobra:',dv)
    if dv:
        print('clique:',s.click(dv[0])); time.sleep(.4)
        dlg=s.js("(()=>{const d=[...document.querySelectorAll('[role=dialog]')].pop(); return d?d.innerText.replace(/\\n/g,' / ').slice(0,300):null;})()"); print('diálogo:',dlg)
        for lab in ['Salvar','Confirmar','Receber devolução','Registrar devolução']:
            r=s.click(lab,'[role=dialog]',exact=True)
            if r=='ok': print('confirmou com',lab); break
        time.sleep(.4); print('toast:',s.js("[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.trim()).filter(Boolean).join(' | ')"))
    print('cenário gravado?',s.js("localStorage.getItem('talhao-os-cenario-v1')!==null"))
    s.c.size(1440,900); s.go('IN-04.dc.html'); tap(s,'P1')
    print('Mapa OS-0417:',s.js("(()=>{const a=document.querySelector('aside[aria-label]'); const d=[...a.querySelectorAll('div')].find(d=>d.style.borderRadius==='10px'&&d.innerText.startsWith('OS-0417')); return d?d.innerText.replace(/\\n/g,' / '):null;})()"))
finally:
    s.close()
