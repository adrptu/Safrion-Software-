# -*- coding: utf-8 -*-
"""Verificador 1: erros de JS, altura do artboard × conteúdo, rolagem horizontal, palavras proibidas nas 6 telas da frente."""
import re, json, time
from ver_mapa_lib import Sess, R
import os
TELAS=['IN-01.dc.html','IN-02.dc.html','IN-02det.dc.html','IN-02x-os0420.dc.html','IN-03.dc.html','IN-04.dc.html']
PROIB=['política','Política de água','PA-07','PA-08','exceção de água','Exceção de água','os0422','fora da política','Fora da política']
def prevh(f):
    s=open(os.path.join(R,f)).read(); m=re.search(r'"\$preview":\{"width":(\d+),"height":(\d+)\}',s); return int(m.group(2))
MEAS="""(()=>{const d=document.documentElement; const over=[...document.querySelectorAll('div,section,table,[role=grid],[role=table]')].filter(e=>e.scrollWidth>e.clientWidth+2 && getComputedStyle(e).overflowX!=='hidden' && e.clientWidth>0).slice(0,6).map(e=>(e.getAttribute('role')||e.tagName)+' '+e.clientWidth+'→'+e.scrollWidth+' '+(e.innerText||'').slice(0,40).replace(/\\n/g,' '));
 const bs=[...document.querySelectorAll('section')].map(s=>s.getBoundingClientRect().bottom+window.scrollY); const bot=bs.length?Math.max(...bs):-1;
 return {sh:d.scrollHeight, sw:d.scrollWidth, cw:d.clientWidth, over, bot};})()"""
s=Sess()
try:
    for f in TELAS:
        h=prevh(f); s.c.size(1440,h); s.go(f)
        m=s.js(MEAS); b=s.body(); hits=[w for w in PROIB if w in b]
        print(f'{f} preview={h} sh={m["sh"]} sw={m["sw"]}/{m["cw"]} últimobloco={m["bot"]:.0f} erros={s.errs()} proibidas={hits}')
        if m['over']: print('   overflow horizontal:',m['over'])
        print('   header:',s.head()[:200])
        if f in ('IN-02det.dc.html','IN-02x-os0420.dc.html'):
            v='v2' if 'det' in f else 'v3'
            print('   clique aprovar:',s.click(f'Aprovar versão {v}'))
            m2=s.js(MEAS); rb=s.js("(()=>{const e=[...document.querySelectorAll('[role=status]')].find(x=>x.innerText.includes('Recibo')); if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.top+scrollY),Math.round(r.bottom+scrollY),e.innerText.replace(/\\n/g,' / ')];})()")
            print(f'   após aprovar: sh={m2["sh"]} recibo(top,bottom)={rb and rb[:2]} preview={h}')
            print('   recibo:',rb and rb[2][:300])
            print('   erros:',s.errs())
            lk=s.js("(()=>{const a=[...document.querySelectorAll('[role=status] a')].find(x=>/Fila vazia|Próxima pendência/.test(x.innerText)); if(!a) return null; const r=a.getBoundingClientRect(); return [Math.round(r.top+scrollY),Math.round(r.bottom+scrollY),a.innerText.trim(),a.getAttribute('href'),document.documentElement.clientHeight,getComputedStyle(document.body).overflow, document.scrollingElement.scrollHeight];})()")
            print('   link próxima (top,bottom,texto,href,viewportH,overflow,sh):',lk)
            s.shot('ver_'+f.replace('.dc.html','')+'_aprovada.png')
finally:
    s.close()
