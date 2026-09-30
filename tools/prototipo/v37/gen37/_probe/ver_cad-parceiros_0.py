# -*- coding: utf-8 -*-
"""Exploração: estrutura do cabeçalho da grade e controles (sem verificações)."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T()
try:
    t.load()
    print('errs', t.errs())
    print('chip', t.chip())
    print('heads', t.heads())
    print(t.J("(()=>{const t=document.querySelectorAll('[role=table]')[0]; const h=t.querySelector('[role=columnheader]'); return h.outerHTML.slice(0,1500);})()"))
    print(t.J("(()=>{const t=document.querySelectorAll('[role=table]')[0]; let p=t.parentElement; return p.parentElement.innerText.slice(0,400);})()"))
    print('buttons', t.J("[...document.querySelectorAll('main button, [data-root] button')].map(b=>(b.getAttribute('aria-label')||b.innerText).replace(/\\s+/g,' ').trim()).slice(0,80)"))
    print('need', t.need(), 'docW', t.J("document.documentElement.scrollWidth"))
    print('text', t.J("document.querySelector('[data-root]').innerText.slice(0,1500)"))
finally: t.close()
