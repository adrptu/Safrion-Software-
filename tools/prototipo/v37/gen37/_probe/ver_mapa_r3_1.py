# -*- coding: utf-8 -*-
"""Verificador r3-1: IN-04 a 1440×1000 · abertura, camada Irrigação, painéis T7/P2/P1, Integrado, erros de JS."""
import time, json
from ver_mapa_lib import Sess
s=Sess(1440,1000)
try:
    s.go('IN-04.dc.html'); s.reset(); s.go('IN-04.dc.html')
    print('HEAD:',s.head()[:300])
    print('NUMS:',s.J("(document.querySelector('[role=group][aria-label^=\"Indicadores\"]')||{innerText:''}).innerText.replace(/\\n/g,' ')"))
    print('errs0:',s.errs(),'| sh',s.J("document.documentElement.scrollHeight"),'| ovf',s.overflow())
    print('Integrado labels:',[s.lab(t) for t in ['T1','T2','T4','T3','P1','P2','T7','C1']])
    print(s.clk('Irrigação')); print(s.clk('Programação de hoje'))
    print('Irrig labels:',[s.lab(t) for t in ['P1','P2','T7','T1']])
    print('NUMS irrig:',s.J("(document.querySelector('[role=group][aria-label^=\"Indicadores\"]')||{innerText:''}).innerText.replace(/\\n/g,' ')"))
    s.tap('T7'); print('PAN T7:',s.pan('T7').replace('\n',' / ')); s.shot('r3_irrig_T7')
    print('links T7:',s.J("[...document.querySelectorAll('aside a')].map(a=>a.innerText.trim()+'->'+a.getAttribute('href'))"))
    s.tap('T7'); s.tap('P2'); print('PAN P2:',s.pan('P2').replace('\n',' / ')); s.shot('r3_irrig_P2')
    print('links P2:',s.J("[...document.querySelectorAll('aside a')].map(a=>a.innerText.trim()+'->'+a.getAttribute('href'))"))
    s.tap('P2'); s.tap('P1'); print('PAN P1:',s.pan('P1').replace('\n',' / '))
    print('links P1:',s.J("[...document.querySelectorAll('aside a')].map(a=>a.innerText.trim()+'->'+a.getAttribute('href'))"))
    s.tap('P1')
    print(s.clk('Balanço hídrico')); print('Bal labels:',[s.lab(t) for t in ['P1','P2','T7']])
    print('clipped:',s.clipped('main') if s.J("!!document.querySelector('main')") else s.clipped())
    print('errs fim:',s.errs())
finally:
    s.close()
