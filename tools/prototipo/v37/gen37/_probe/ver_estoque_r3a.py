# -*- coding: utf-8 -*-
"""Verificador (rodada 3) · Estoque A: varredura das 6 etapas em 1440x1000 com cenário limpo."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
v = V()
try:
    v.abrir()
    print('titulo:', v.J("document.title"), '| h1:', v.J("(document.querySelector('h1')||{}).innerText"))
    print('subtitulo/ctx:', v.J("document.querySelector('header')?document.querySelector('header').innerText.replace(/\\s+/g,' ').slice(0,400):''"))
    print('faixa:', v.J("[...document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ')).join(' | ')"))
    print('filtros topo:', v.J("[...document.querySelectorAll('select')].map(s=>(s.getAttribute('aria-label')||s.id)+'='+s.value+' ['+[...s.options].map(o=>o.value).join(',')+']')"))
    for i in range(1, 7):
        v.etapa(i)
        print(f'--- etapa {i} · prim={v.prim()!r}')
        print('   k:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
        print('   blocos:', v.J("[...document.querySelectorAll('main section h3')].map(h=>h.innerText+' :: '+h.nextElementSibling.innerText)"))
        print('   overflow:', v.overflow())
        print('   heads:', v.J("[...document.querySelectorAll('[role=columnheader]')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ').trim()).join(' | ')"))
        print('   largura tabela:', v.J("[...document.querySelectorAll('[role=table],[role=grid],[role=treegrid]')].filter(t=>t.offsetParent).map(t=>t.scrollWidth+'/'+t.clientWidth+'/'+t.parentElement.clientWidth)"))
        rs = v.rows(); print('   rows:', len(rs))
        for r in rs[:16]: print('     ', r[:260])
        print('   rodape:', v.J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent).slice(-4).map(b=>b.innerText.trim())"))
        v.shot(f'ver_est_r3_e{i}.png')
    print('erros:', v.erros())
finally:
    v.fim()
