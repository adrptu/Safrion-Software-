# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 4: telas de campo CA-01..CA-04 (erros, overflow, mapa, Liberar selecionadas, termos)."""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
PROIB = re.compile(r'política|PA-07|exceção|revisão individual', re.I)
OVF = r"""(()=>{const out=[]; const W=document.documentElement.clientWidth; out.push('doc '+document.documentElement.scrollWidth+'/'+W);
  document.querySelectorAll('[role=table],[role=grid],section').forEach(e=>{ if(e.scrollWidth>e.clientWidth+2) out.push('ovf '+(e.getAttribute('aria-label')||e.tagName)+' '+e.scrollWidth+'>'+e.clientWidth); });
  return out;})()"""
try:
    for f in ('CA-01', 'CA-01det', 'CA-01x-os0420', 'CA-02', 'CA-03', 'CA-03det', 'CA-04'):
        T.c.goto(f'http://127.0.0.1:{T.p}/{f}.dc.html', wait=0.9)
        b = J("document.body.innerText") or ''
        print('==', f, '| erro', J("window.__err||''"), J("[...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText).join('|')"), '|', J(OVF), '| proib', PROIB.findall(b)[:3])
    T.c.goto(f'http://127.0.0.1:{T.p}/CA-01.dc.html', wait=1.0)
    # linhas OS-0422 e OS-0423 na lista
    for oid in ('OS-0419', 'OS-0422', 'OS-0423', 'OS-0418'):
        print('  ', J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.trim().startsWith('{oid}')); return r?r.innerText.replace(/\\s+/g,' '):'';}})()"))
    # seleção + Liberar selecionadas
    sel = J("""(()=>{const out=[]; ['OS-0422','OS-0423'].forEach(id=>{ const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.trim().startsWith(id)); const cb=r&&r.querySelector('input[type=checkbox]'); if(cb){cb.click(); out.push(id);} }); return out;})()""")
    time.sleep(.4); print('   sel', sel, J("[...document.querySelectorAll('button')].filter(b=>/selecionad/.test(b.innerText)).map(b=>b.innerText.trim())"))
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Liberar selecionadas'); b&&b.click();})()"); time.sleep(.4)
    print('   msg', J("[...document.querySelectorAll('[role=status],[role=alert],[role=dialog]')].map(e=>e.innerText.replace(/\\s+/g,' ')).filter(Boolean).join(' || ')")[:700])
    T.shot('ver_os4_ca01_msg.png')
    # mapa: textos dentro das caixas
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Mapa'); b&&b.click();})()"); time.sleep(.4)
    m = J("""(()=>{const s=document.querySelector('svg[aria-label="Mapa das ordens abertas por talhão"]'); if(!s) return 'sem mapa';
      const rects=[...s.querySelectorAll('rect[stroke],circle')]; const out=[];
      [...s.querySelectorAll('text')].forEach(t=>{ const b=t.getBBox(); const inside=rects.some(r=>{ if(r.tagName==='rect'){ const x=+r.getAttribute('x'),w=+r.getAttribute('width'),y=+r.getAttribute('y'),h=+r.getAttribute('height'); return b.x>=x-1&&b.x+b.width<=x+w+1&&b.y>=y-1&&b.y+b.height<=y+h+1; } const cx=+r.getAttribute('cx'),cy=+r.getAttribute('cy'),rr=+r.getAttribute('r'); return b.x>=cx-rr&&b.x+b.width<=cx+rr&&b.y>=cy-rr&&b.y+b.height<=cy+rr; });
        if(!inside) out.push(t.textContent+' x='+Math.round(b.x)+' w='+Math.round(b.width)); }); return out;})()""")
    print('   mapa fora das caixas', m)
    T.shot('ver_os4_ca01_mapa.png')
    T.c.goto(f'http://127.0.0.1:{T.p}/CA-02.dc.html', wait=0.9)
    b = J("document.body.innerText") or ''
    for k in ('OS-0418', 'OS-0422', 'OS-0423', 'água'):
        i = b.find(k); print('   CA-02', k, '|', b[max(0, i - 80):i + 160].replace('\n', ' ') if i >= 0 else '-')
finally:
    T.fim()
