# -*- coding: utf-8 -*-
"""Verificador 2 (IN-04): rótulos dos talhões cabem no foreignObject em todas as camadas e opções de filtro; rolagem ≤ 900;
cabeçalho do cartão sem quebra excessiva; erros de JS."""
import json, time
from ver_mapa_lib import Sess
LAB="""(()=>{const out=[]; document.querySelectorAll('svg foreignObject').forEach(fo=>{ const d=fo.firstElementChild; if(!d) return; const h=+fo.getAttribute('height'), w=+fo.getAttribute('width');
  if(d.scrollHeight>h+1||d.scrollWidth>w+1) out.push([d.innerText.replace(/\\n/g,' '),w+'x'+h,d.scrollWidth+'x'+d.scrollHeight]); }); return out;})()"""
s=Sess(1440,900)
try:
    s.go('IN-04.dc.html'); s.js("localStorage.removeItem('talhao-os-cenario-v1')")
    lays=s.js("[...document.querySelectorAll('nav[role=tablist] button')].map(b=>b.innerText.trim())")
    print('camadas:',lays)
    probs=[]
    for L in lays:
        s.click(L,'nav[role=tablist]')
        groups=s.js("[...document.querySelectorAll('span[role=group]')].map(g=>[g.getAttribute('aria-label'),[...g.querySelectorAll('button')].map(b=>b.innerText.trim())])") or []
        combos=[None]+[(g,o) for g,os_ in groups for o in os_[1:]]
        for cb in combos:
            if cb: s.js(f"[...document.querySelector('span[role=group][aria-label=\"{cb[0]}\"]').querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(cb[1])}).click()"); time.sleep(.3)
            bad=s.js(LAB); sh=s.js("document.documentElement.scrollHeight")
            hdr=s.js("(()=>{const b=[...document.querySelectorAll('b')].find(x=>x.parentElement&&x.parentElement.querySelector('[role=group][aria-label^=\"Indicadores\"]')); return b?b.parentElement.getBoundingClientRect().height:0;})()")
            if bad or sh>900: probs.append((L,cb,bad,sh))
            print(f'{L:24s} {str(cb):40s} sh={sh} cabeçalho={hdr:.0f}px rótulos_cortados={bad}')
        # volta o filtro ao padrão
        for g,os_ in groups:
            s.js(f"[...document.querySelector('span[role=group][aria-label=\"{g}\"]').querySelectorAll('button')].find(b=>b.innerText.trim()==={json.dumps(os_[0])}).click()"); time.sleep(.2)
    print('PROBLEMAS:',probs)
    print('erros:',s.errs())
finally:
    s.close()
