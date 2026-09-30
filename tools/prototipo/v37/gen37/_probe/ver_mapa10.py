# -*- coding: utf-8 -*-
"""Verificador 10: IN-02x-os0420 a 1440×820 (altura do artboard) — depois de aprovar, o link do recibo fica visível ou rolável?"""
import time
from ver_mapa_lib import Sess
s=Sess(1440,820)
try:
    for f,v in [('IN-02x-os0420.dc.html','v3'),('IN-02det.dc.html','v2')]:
        s.c.size(1440,820 if 'os0420' in f else 710); s.go(f); s.click(f'Aprovar versão {v}'); time.sleep(.3)
        r=s.js("""(()=>{const sc=[...document.querySelectorAll('*')].filter(e=>{const cs=getComputedStyle(e); return /(auto|scroll)/.test(cs.overflowY)&&e.scrollHeight>e.clientHeight+1;}).map(e=>e.tagName+'.'+(e.getAttribute('role')||'')+' '+e.clientHeight+'/'+e.scrollHeight);
          const a=[...document.querySelectorAll('[role=status] a')].find(x=>/Fila vazia|Próxima/.test(x.innerText)); const rr=a.getBoundingClientRect();
          const hid=[...document.querySelectorAll('*')].filter(e=>getComputedStyle(e).overflowY==='hidden'&&e.scrollHeight>e.clientHeight+1).map(e=>e.tagName+' '+e.clientHeight+'/'+e.scrollHeight).slice(0,4);
          window.scrollTo(0,99999); const y=window.scrollY;
          return {roláveis:sc, oculto:hid, link_bottom:Math.round(rr.bottom), vh:innerHeight, scrollY_max:y, doc:document.documentElement.scrollHeight};})()""")
        print(f,r)
        s.shot('ver_'+f.replace('.dc.html','')+'_fim.png')
finally:
    s.close()
