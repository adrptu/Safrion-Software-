# -*- coding: utf-8 -*-
"""Passo 9a · sonda dos 7 cadastros: abre cada tela, lista a ação primária do cabeçalho, filtros e erros de JS."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
for t in ['CD-01', 'CD-01det', 'CD-02', 'CD-03', 'CD-04', 'CD-05', 'CD-06', 'CD-07']:
    b.goto(t + '.dc.html')
    hb = b.J("[...document.querySelectorAll('header button, header a')].filter(x=>x.offsetParent!==null).map(x=>x.innerText.trim()).filter(Boolean).slice(-4)")
    grp = b.J("[...document.querySelectorAll('[role=group]')].map(g=>g.getAttribute('aria-label')+': '+[...g.querySelectorAll('button')].map(x=>x.innerText.trim().replace(/\\s+/g,' ')).join(' / '))")
    n = b.J("[...document.querySelectorAll('[role=row].g2ed')].length")
    print(f'== {t}: título={b.J("document.title")} | ações={hb} | linhas={n}\n   grupos={grp[:4]}\n   erros={b.erros()}')
