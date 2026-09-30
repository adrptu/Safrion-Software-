# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · A: varredura das 6 etapas em 1440x1000 com cenário limpo."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
v = V()
try:
    v.abrir()
    print('titulo:', v.J("document.title"), '| h1:', v.J("(document.querySelector('h1')||{}).innerText"))
    print('header:', v.J("document.querySelector('header')?document.querySelector('header').innerText.replace(/\\s+/g,' ').slice(0,500):''"))
    print('faixa:', v.J("[...document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ')).join(' | ')"))
    print('selects:', v.J("[...document.querySelectorAll('select')].map(s=>(s.getAttribute('aria-label')||s.id)+'='+s.value+' ['+[...s.options].map(o=>o.value).join(',')+']')"))
    for i in range(1, 7):
        v.etapa(i)
        print(f'--- etapa {i} · prim={v.prim()!r}')
        print('   k:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
        print('   blocos:', v.J("[...document.querySelectorAll('main section h3')].filter(h=>h.offsetParent).map(h=>h.innerText+' :: '+h.nextElementSibling.innerText)"))
        print('   overflow:', v.overflow())
        print('   heads:', v.J("[...document.querySelectorAll('[role=columnheader]')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ').trim()).join(' | ')"))
        rs = v.rows(); print('   rows:', len(rs))
        for r in rs[:20]: print('     ', r[:300])
        print('   rodape:', v.J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent).slice(-4).map(b=>b.innerText.trim())"))
        print('   pag h:', v.J("document.documentElement.scrollHeight"))
        v.shot(f'ver_est_r4_e{i}.png')
    print('erros:', v.erros())
finally:
    v.fim()
