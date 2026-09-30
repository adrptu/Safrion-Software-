# -*- coding: utf-8 -*-
"""Verificador r3h · CD-01det no estado inicial (T1), seletor, #talhao=, não encontrado, larguras."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
try:
    s.go('CD-01det.dc.html'); s.clear_ls(); s.go('CD-01det.dc.html')
    P('ERRS', s.errs()); P('HEAD', s.head()); P('title', s.js("document.title"))
    P('sel', s.js("(()=>{const x=document.querySelector('header select'); return [x.value,[...x.options].map(o=>o.value+'='+o.text)];})()"))
    P('BTN head', s.js("[...document.querySelectorAll('header button, header a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim()+' ->'+(e.getAttribute('href')||''))"))
    P('H3', s.js("[...document.querySelectorAll('main h2,main h3')].map(h=>h.innerText)"))
    for i in range(3): P('T'+str(i), json.dumps(s.rows(i),ensure_ascii=False))
    P('MAIN', s.js("document.querySelector('main').innerText").replace('\n',' | ')[-1400:])
    P('main btns', s.js("[...document.querySelectorAll('main button, main a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/\\s+/g,' ').trim()+(e.getAttribute('href')?' ->'+e.getAttribute('href'):''))"))
    P('OVF', s.overflow()); P('SCROLL', s.js("(()=>{const m=document.querySelector('main'); return [m.scrollHeight,m.clientHeight,document.documentElement.scrollHeight];})()"))
    s.shot('ver_cad-fazendas_r3h_T1.png')
    s.go('CD-01det.dc.html#talhao=T2'); P('T2 HEAD', s.head()); P('T2 sel', s.js("document.querySelector('header select').value")); P('T2 rows0', s.rows(0))
    s.go('CD-01det.dc.html#talhao=ZZ'); P('ZZ HEAD', s.head()); P('ZZ sel', s.js("(()=>{const x=document.querySelector('header select'); return [x.value,x.selectedIndex,x.options[x.selectedIndex]&&x.options[x.selectedIndex].text];})()"))
    P('ZZ main', s.js("document.querySelector('main').innerText").replace('\n',' | ')[:300]); P('ZZ ERRS', s.errs())
    s.shot('ver_cad-fazendas_r3h_ZZ.png')
finally: s.close()
