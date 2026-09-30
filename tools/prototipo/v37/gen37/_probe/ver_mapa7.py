# -*- coding: utf-8 -*-
"""Verificador 7: ordens 'Aguardando agrônomo' no mapa × contagem 'Decisões pendentes' × caixa de Aprovações; tela da O.S."""
import time
from ver_mapa_lib import Sess
SV="[...document.querySelectorAll('svg [role=button]')]"
def tap(s,t): s.js(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.35)
def pan(s): return (s.js("(document.querySelector('aside[aria-label]')||{innerText:''}).innerText") or '').replace('\n',' / ')
s=Sess(1440,900)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')"); s.go('IN-04.dc.html')
    print('HEAD:',s.head().split(' | ')[-1])
    print('NUMS:',s.js("document.querySelector('[role=group][aria-label^=\"Indicadores\"]').innerText.replace(/\\n/g,' ')"))
    for t in ['T1','P1']:
        tap(s,t); p=pan(s); print(f'{t}:',p[:900]); tap(s,t)
    s.click('Ordens de serviço','nav[role=tablist]'); s.click('A liberar')
    print('A liberar rótulos:',s.js(f"{SV}.map(x=>x.getAttribute('aria-label'))"))
    tap(s,'T1'); s.shot('ver_in04_T1_os0430.png'); tap(s,'T1')
    s.go('IN-02.dc.html'); print('IN-02 cita OS-0430?', 'OS-0430' in s.body())
    s.go('OS.dc.html'); b=s.body(); i=b.find('OS-0430'); print('OS.dc.html OS-0430:', b[i:i+200].replace('\n',' | ') if i>=0 else 'ausente')
finally:
    s.close()
