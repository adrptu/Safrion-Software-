# -*- coding: utf-8 -*-
"""Verificador r3-3: filtro Fazenda do topo no IN-04 (Boa Vista / Todas), barra lateral em Boa Vista, toast que não some."""
import time, json
from ver_mapa_lib import Sess
s=Sess(1440,1000)
NUMS="(document.querySelector('[role=group][aria-label^=\"Indicadores\"]')||{innerText:''}).innerText.replace(/\\n/g,' ')"
try:
    s.go('IN-04.dc.html'); s.reset(); s.go('IN-04.dc.html')
    # toast: Medir liga, espera 5,5 s, toast continua?
    print(s.clk('Medir')); t0=s.J("[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.trim()).filter(Boolean).join(' | ')")
    time.sleep(5.5); t1=s.J("[...document.querySelectorAll('[role=status]')].map(e=>e.innerText.trim()).filter(Boolean).join(' | ')")
    print('toast antes:',t0,'| depois de 5,5 s:',t1,'| errs:',s.errs()); s.clk('Medir')
    s.clk('Irrigação'); s.tap('T7')
    s.faz('Boa Vista'); print('BV head:',s.head()); print('BV nums:',s.J(NUMS)); s.shot('r3_bv_irrig')
    b=s.body(); print('BV body:',b[:900].replace('\n',' / '))
    print('BV links:',s.J("[...document.querySelectorAll('a')].filter(a=>a.getClientRects().length).map(a=>a.innerText.trim().slice(0,30)+'->'+a.getAttribute('href'))"))
    print('BV buttons:',s.J("[...document.querySelectorAll('button')].filter(a=>a.getClientRects().length).map(a=>(a.innerText.trim()||a.getAttribute('aria-label')||'').slice(0,30))"))
    print('BV svg talhões:',s.J(f"{s.SV}.length"),'sh',s.J("document.documentElement.scrollHeight"),'errs',s.errs())
    # troca de camada em Boa Vista
    print(s.clk('Satélite')); print('BV sat body:',s.body()[:400].replace('\n',' / '))
    s.faz('Todas'); print('Todas head:',s.head()); print('Todas nums:',s.J(NUMS)); print('Todas aviso:', 'Boa Vista sem geometria' in s.body())
    s.shot('r3_todas_sat')
    print('pan aberto?',s.J("!!document.querySelector('aside[aria-label]')"))
    s.faz('Santa Rita'); print('SR head:',s.head()); print('lay ativo labels:',[s.lab(t) for t in ['P1','T7']])
    print('errs fim:',s.errs())
finally:
    s.close()
