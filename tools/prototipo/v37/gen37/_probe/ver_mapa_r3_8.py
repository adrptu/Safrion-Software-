# -*- coding: utf-8 -*-
"""Verificador r3-8: depois de aprovar a OS-0418 (IN-02det) e de receber a sobra da OS-0417 (cenário), IN-01 / IN-03 / IN-04 Irrigação acompanham?"""
import time, json, sys, os
from ver_mapa_lib import Sess, GEN
import cenario
s=Sess(1440,1000)
ROWS="[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\n/g,' ; ').slice(0,160))"
try:
    s.go('IN-02det.dc.html'); s.reset(); s.go('IN-02det.dc.html'); print(s.clk('Aprovar versão v2')); time.sleep(.3)
    c=s.cen(); print('cenário OS-0418 selos:',c['ordens']['OS-0418']['selos'],'etapa',c['ordens']['OS-0418']['etapa'])
    s.go('IN-02.dc.html'); print('IN-02:',s.head()[-40:],'|',[r for r in s.J(ROWS) if 'OS-0418' in r])
    s.go('IN-01.dc.html'); print('IN-01 head:',s.head()[-60:]); print('IN-01 OS-0418:',[r for r in s.J(ROWS) if 'OS-0418' in r])
    s.go('IN-04.dc.html'); print('IN-04 head:',s.head()[-60:]); s.clk('Irrigação'); s.clk('Programação de hoje'); print('IN-04 Irrigação P1:',s.lab('P1'))
    s.tap('P1'); s.shot('r3_P1_irrig_aprovada'); p=s.pan('P1'); print('painel P1:',p.replace('\n',' / ')[:420]); s.tap('P1')
    # sobra da OS-0417 recebida no Estoque (mesma mutação do teste da frente)
    c=s.cen(); it=c['reqs']['REQ-031']['itens'][0]; it['devolvido']+=it['custodia']; it['custodia']=0; c['rev']=(c.get('rev') or 0)+1; s.setcen(c)
    s.clk('Ordens de serviço'); s.tap('P1'); print('IN-04 P1 O.S.:',s.pan('P1').replace('\n',' / ')[:420]); s.tap('P1')
    s.go('IN-01.dc.html'); print('IN-01 OS-0417:',[r for r in s.J(ROWS) if 'OS-0417' in r])
    s.go('IN-03.dc.html'); print('IN-03 REQ-031:',[r for r in s.J(ROWS) if 'REQ-031' in r]); print('IN-03 head:',s.head()[-50:])
    print('errs',s.errs()[:200])
finally:
    s.close()
