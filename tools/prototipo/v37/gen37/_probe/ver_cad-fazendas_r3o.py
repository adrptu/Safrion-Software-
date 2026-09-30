# -*- coding: utf-8 -*-
"""Verificador r3o · após renomear Santa Rita, "Cadastrar talhão" nasce com a fazenda de nome antigo: salva? cria grupo fantasma?"""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
def fresh(u): s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.openrow(0,'Santa Rita Santa Rita Agro'); s.fset('nome','Santa Rita do Sul'); s.btn('Salvar'); time.sleep(.3)
    s.click('Cadastrar talhão','header'); P('faz padrão', s.fv('faz'), s.fopts('faz'))
    s.fset('t','T9'); s.fset('decl','10'); s.btn('Salvar'); time.sleep(.3); P('salvou?', not s.aberto(), s.toast(), s.alerts())
    P('tabela fazendas', [r[:40] for r in s.rows(0)])
    P('árvore', [r[:70] for r in s.rows(1) if r.startswith('▾') or r.startswith('T9') or 'Santa Rita' in r])
    s.shot('ver_cad-fazendas_r3o.png', full=True)
    fresh('CD-01det.dc.html'); P('det opts', s.js("[...document.querySelector('header select').options].map(o=>o.text)"))
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
