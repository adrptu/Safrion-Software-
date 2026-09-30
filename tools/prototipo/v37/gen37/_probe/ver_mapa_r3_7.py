# -*- coding: utf-8 -*-
"""Verificador r3-7: IN-02 → Decidir de cada linha (destino); cadeia OS-0418 → OS-0420 → OS-0430; OS.dc.html abre na OS-0430?"""
import time, json
from ver_mapa_lib import Sess
s=Sess(1440,1000)
NX="(()=>{const a=[...document.querySelectorAll('a')].find(a=>/Fila vazia|Próxima pendência/.test(a.innerText)); return a?[a.innerText.trim().replace(/\\n/g,' '),a.getAttribute('href')]:null;})()"
try:
    s.go('IN-02.dc.html'); s.reset(); s.go('IN-02.dc.html')
    print('decidir:',s.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0]+' -> '+([...r.querySelectorAll('a')].map(a=>a.getAttribute('href')).join(',')||'(botão)'))"))
    # clica Decidir na linha OS-0430
    r=s.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(x=>/OS-0430/.test(x.innerText)); const b=[...r.querySelectorAll('a,button')].find(x=>/Decidir/.test(x.innerText)); if(!b) return 'sem'; b.click(); return b.tagName+' '+(b.getAttribute('href')||'');})()"); time.sleep(1.5)
    print('clicou Decidir OS-0430:',r,'| url:',s.J("location.pathname"))
    print('OS.dc.html head:',s.head()[:300]); b=s.body(); i=b.find('OS-0430'); print('OS-0430 visível no texto:',i>=0, b[max(0,i-100):i+200].replace('\n',' / ') if i>=0 else '')
    print('painel/detalhe aberto?',s.J("(()=>{const d=document.querySelector('[role=dialog],aside[aria-label]'); return d?d.innerText.slice(0,200).replace(/\\n/g,' / '):'nenhum';})()"))
    s.shot('r3_os_de_in02')
    # cadeia de decisões
    s.go('IN-02det.dc.html'); s.clk('Aprovar versão v2'); print('após OS-0418:',s.J(NX))
    s.go('IN-02x-os0420.dc.html'); print('0420 head:',s.head()[:200]); s.clk('Aprovar versão v3'); print('após OS-0420:',s.J(NX))
    s.go('IN-02.dc.html'); print('IN-02 depois de 2 decisões:',s.head()[-60:])
    print('situação linhas:',s.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\n/g,' ; ').slice(0,40)+' … '+r.innerText.split('\\n').slice(-2).join(' ; '))"))
    s.go('IN-04.dc.html'); print('IN-04 head:',s.head()[-70:]); print('T4:',s.lab('T4'),'T1:',s.lab('T1'))
    print('errs',s.errs()[:300])
finally:
    s.close()
