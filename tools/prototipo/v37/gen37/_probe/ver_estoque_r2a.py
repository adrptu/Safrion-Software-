# -*- coding: utf-8 -*-
"""Verificador (rodada 2) · Estoque A: varredura das 6 etapas em 1440x1000 com cenário limpo: erros, larguras, primária, faixas, fotos."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

v = V()
try:
    v.abrir()
    print('titulo:', v.J("document.title"))
    print('faixa etapas:', v.J("[...document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ')).join(' | ')"))
    for i in range(1, 7):
        v.etapa(i)
        k = v.J("(()=>{const m=document.querySelector('main'); return m.innerText.split('\\n').filter(l=>/·/.test(l)).slice(0,2);})()")
        print(f'--- etapa {i} · prim={v.prim()!r}')
        print('   k:', k)
        print('   overflow:', v.overflow())
        print('   heads:', v.J("[...document.querySelectorAll('[role=columnheader]')].filter(x=>x.offsetParent).map(x=>x.innerText.replace(/\\s+/g,' ').trim()).join(' | ')"))
        print('   rows:', len(v.rows()))
        for r in v.rows()[:14]: print('     ', r[:230])
        v.shot(f'ver_est_r2_e{i}.png')
    print('erros:', v.erros())
finally:
    v.fim()
