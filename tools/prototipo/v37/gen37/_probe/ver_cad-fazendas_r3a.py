# -*- coding: utf-8 -*-
"""Verificador r3a · CD-01 no estado inicial: erros, cabeçalho, blocos, colunas, subtotais, larguras, mapa."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess(); chk=L.chk
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    print('ERRS', s.errs())
    print('HEAD', s.head())
    print('H2', s.js("[...document.querySelectorAll('main h2,main h3')].map(h=>h.innerText)"))
    print('BLOCOS', s.js("[...document.querySelectorAll('main section, main [data-bloco]')].length"))
    print('T0', json.dumps(s.rows(0),ensure_ascii=False))
    print('T1', json.dumps(s.rows(1),ensure_ascii=False))
    print('HEADERS0', s.js("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=columnheader]')].map(x=>x.innerText.replace(/\\s+/g,' '))"))
    print('HEADERS1', s.js("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=columnheader]')].map(x=>x.innerText.replace(/\\s+/g,' '))"))
    print('OVF', s.overflow())
    print('BTNS', s.js("[...document.querySelectorAll('button,a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/\\s+/g,' ').trim()||('['+(e.getAttribute('aria-label')||'')+']')).filter(Boolean)"))
    print('MAPA', s.js("[...document.querySelectorAll('svg polygon, svg circle')].map(e=>e.getAttribute('fill'))"))
    print('MAIN', s.js("document.querySelector('main').innerText").replace('\n',' | ')[:3000])
    print('SCROLL', s.js("(()=>{const m=document.querySelector('main'); return [m.scrollHeight,m.clientHeight,document.documentElement.scrollHeight,window.innerHeight];})()"))
    s.shot('ver_cad-fazendas_r3a_top.png')
finally: s.close()
