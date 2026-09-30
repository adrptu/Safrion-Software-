# -*- coding: utf-8 -*-
"""Verificador r3-2: decidir OS-0418 na IN-02det → próxima pendência, IN-02 e IN-04 (Integrado, Irrigação) leem o mesmo estado."""
import time, json
from ver_mapa_lib import Sess
s=Sess(1440,1000)
NX="(()=>{const a=[...document.querySelectorAll('a')].find(a=>/Fila vazia|Próxima pendência/.test(a.innerText)); return a?[a.innerText.trim(),a.getAttribute('href')]:null;})()"
try:
    s.go('IN-02.dc.html'); s.reset(); s.go('IN-02.dc.html')
    print('IN-02 head:',s.head()[:250]); print('rows:',s.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0])"))
    print('ovf:',s.overflow(),'sh',s.J("document.documentElement.scrollHeight"),'errs',s.errs())
    s.go('IN-02det.dc.html'); print('det head:',s.head()[:250])
    print('antes:',s.J(NX)); print(s.clk('Aprovar versão v2')); time.sleep(.3)
    print('status:',s.J("[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.replace(/\\n/g,' / ')).join(' || ')")[:500])
    print('depois:',s.J(NX)); print('det head2:',s.head()[:250]); print('errs',s.errs())
    s.go('IN-02.dc.html'); print('IN-02 head pós:',s.head()[:250]); print('rows pós:',s.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0]+' | '+r.innerText.split('\\n').slice(1,4).join(' ; '))"))
    s.go('IN-04.dc.html'); print('IN-04 head pós:',s.head()[:250])
    print('NUMS:',s.J("(document.querySelector('[role=group][aria-label^=\"Indicadores\"]')||{innerText:''}).innerText.replace(/\\n/g,' ')"))
    print('P1 integ:',s.lab('P1'))
    s.clk('Irrigação'); s.clk('Programação de hoje'); print('P1 irrig:',s.lab('P1'))
    s.tap('P1'); print('PAN P1:',s.pan('P1').replace('\n',' / ')); s.shot('r3_irrig_P1_pos_aprov')
    s.tap('P1'); s.clk('Ordens de serviço'); s.tap('P1'); print('PAN P1 OS:',s.pan('P1').replace('\n',' / '))
    print('errs',s.errs())
finally:
    s.close()
