# -*- coding: utf-8 -*-
"""Verificador r3n · renomear Santa Rita: título do mapa, detalhe (fazenda, seletor, parcelas); área total com decimal."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
def fresh(u): s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.openrow(0,'Santa Rita Santa Rita Agro'); s.fset('nome','Santa Rita do Sul'); s.fset('area','1480,5'); s.btn('Salvar'); time.sleep(.3); P('toast', s.toast(), s.alerts())
    P('h3', s.js("[...document.querySelectorAll('main h2,main h3')].map(h=>h.innerText)")); P('mapa aria', s.js("document.querySelector('main svg').getAttribute('aria-label')"))
    P('faz row', s.rowtxt(0,'Santa Rita do Sul')); P('g', s.rowtxt(1,'Santa Rita do Sul'))
    P('reabre area', s.openrow(0,'Santa Rita do Sul'), s.fv('area')); s.btn('Cancelar')
    s.click('Cadastrar talhão','header'); P('faz opts', s.fopts('faz')); s.btn('Cancelar')
    fresh('CD-01det.dc.html#talhao=T3'); P('HEAD', s.head()[:200]); P('rows0', s.rows(0)); P('rows1', s.rows(1))
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
