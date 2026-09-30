# -*- coding: utf-8 -*-
"""Verificador r3-4: capturas e medidas (1440×1000) das telas da frente · erros, largura, rolagem, altura do artboard."""
import time, re
from ver_mapa_lib import Sess
s=Sess(1440,1000)
try:
    s.go('IN-04.dc.html'); s.reset()
    for f in ['IN-04','IN-01','IN-02','IN-02det','IN-02x-os0420','IN-03']:
        s.go(f+'.dc.html')
        pv=re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}',open(s.url(f+'.dc.html').replace(f'http://127.0.0.1:{s.p}/',__import__('ver_mapa_lib').R+'/'),encoding='utf-8').read())
        m=s.J("""(()=>{const all=[...document.querySelectorAll('body *')].filter(e=>e.getClientRects().length); let mb=0,last=''; all.forEach(e=>{const r=e.getBoundingClientRect(); if(r.bottom>mb&&r.height>0&&e.innerText&&e.innerText.trim()&&getComputedStyle(e).position!=='fixed'){mb=r.bottom; last=e.innerText.trim().slice(0,50);} }); return {sh:document.documentElement.scrollHeight,sw:document.documentElement.scrollWidth,maxbottom:Math.round(mb),last};})()""")
        print(f,'preview',pv.groups(),m,'ovf',s.overflow(),'errs',s.errs()[:200])
        print('   head:',s.head()[:200])
        s.shot('r3_'+f)
finally:
    s.close()
