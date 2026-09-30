# -*- coding: utf-8 -*-
"""Verificador · Estoque 1: percorre as 6 etapas no cenário inicial, lê faixa, primária, linhas, larguras e erros; tira fotos."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

v = V()
try:
    v.abrir()
    print('titulo:', v.J("document.title"), '| faz:', v.J("(document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||{}).value"))
    for i in range(1, 7):
        v.etapa(i)
        cur = v.J("document.querySelector('[aria-current=step]').innerText.replace(/\\s+/g,' ')")
        print(f'\n===== etapa {i}: {cur} · primária: {v.prim()!r}')
        print('faixa:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
        for r in v.rows()[:40]: print('   |', r[:260])
        print('overflow:', v.overflow())
        v.J("window.scrollTo(0,0)"); v.shot(f'ver_est_e{i}.png')
        h = v.J("document.documentElement.scrollHeight"); print('altura:', h)
    print('\nerros:', v.erros())
finally:
    v.fim()
