# -*- coding: utf-8 -*-
"""Verificador App (rodada final) 11: estado inicial de cada tela da frente — cabeçalho, rodapé, corte, largura, erros JS, texto."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    for t in ['MB-01', 'MB-02', 'MB-02det', 'MB-03', 'MB-03x-recibo', 'MB-04', 'MB-05', 'OS-0424-app']:
        v.abrir(t); time.sleep(.2)
        print('=====', t, '| title:', v.J("document.title"))
        print('  hdr:', v.hdr()); print('  foot:', v.foot()); print('  corte:', v.corte(), '| larg:', v.larg(), '| erros:', v.erros())
        print('  main:', v.J("document.querySelector('main').innerText").replace('\n', ' / ')[:2500])
        v.shot(f'ver_app11_{t}.png')
finally:
    v.fim()
