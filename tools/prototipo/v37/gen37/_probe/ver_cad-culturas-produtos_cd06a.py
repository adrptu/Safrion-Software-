# -*- coding: utf-8 -*-
"""Verificador · CD-06 parte A: estado inicial, linhas, cortes, layout, formulários de item/grupo/local."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    v.goto('CD-06.dc.html'); v.J("localStorage.clear()"); v.goto('CD-06.dc.html')
    v.info('cabeçalho',v.header())
    v.info('botões',v.visible_btns())
    rows=v.J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
    for r in rows: print('   ',r)
    v.info('locais',v.J("[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())"))
    body=v.J("document.body.innerText")
    for w in ['quarentena','Conversões','fabricação','bloqueado','PC-088','+ Novo local']: v.info('texto cortado presente? '+w, w in body)
    v.info('overflow',v.overflow())
    v.info('links de saldo',v.J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('a')].slice(0,3).map(a=>a.getAttribute('href')+' '+a.innerText)"))
    # item com saldo
    v.clickrow('Glifosato 480'); v.info('form Glifosato',[v.title(),v.labels(),v.fdis('un'),v.dlg()[:900]]); v.cancel()
    v.clickrow('Fungicida C'); v.info('form Fungicida C',[v.fdis('un'),v.dlg()[:300]]); v.cancel()
    v.clickrow('Calcário dolomítico'); v.info('form Calcário',[v.fdis('un'),v.labels(),v.fv('emb'),v.fv('ctrl'),v.fv('preco'),v.fv('pdata'),v.fv('local'),v.fopts('local')]); v.cancel()
    v.clickrow('Produto agrícola'); v.info('form grupo Produto agrícola',[v.title(),v.labels(),v.fv('nat'),v.fopts('nat')]); v.cancel()
    v.clickrow('Peças'); v.info('form grupo Peças',[v.title(),v.fv('nat')]); v.cancel()
    v.clickrow('Tanque Sede',1,'span'); v.info('form Tanque',[v.title(),v.labels(),v.fv('cap')]); v.cancel()
    v.clickrow('Silo 01',1,'span'); v.info('form Silo',[v.title(),v.labels(),v.fv('capa'),v.fdis('capa')]); v.cancel()
    v.clickrow('Galpão 1',1,'span'); v.info('form Galpão',[v.title(),v.labels()]); v.cancel()
    v.info('erros (fora g2toast)',[e for e in v.errs() if 'g2toast' not in e])
    v.shot('ver_cadc_cd06_topo.png')
finally: v.fim()
