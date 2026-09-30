# -*- coding: utf-8 -*-
"""Verificador · CD-02 → CD-06 (semente criada), Outro grupo, renomear grupo, estado 'Cadastro completo' e cor do chip."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
CHIP="(()=>{const h=document.querySelector('header'); const els=[...h.querySelectorAll('*')].filter(e=>e.children.length<=3&&/%s/.test(e.innerText||'')); const out=els.map(e=>{const cs=getComputedStyle(e); return [e.tagName,(e.innerText||'').trim().slice(0,40),cs.backgroundColor,cs.color];}).filter(x=>x[2]!=='rgba(0, 0, 0, 0)'); return out;})()"
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    v.clickrow('64 Z'); v.btn('Salvar'); v.info('toast CD-02',v.toast())
    v.goto('CD-06.dc.html')
    v.info('semente vinda do CD-02',[v.rowtxt('Semente de soja 64 Z'),v.rowtxt('Sementes 5')])
    v.clickrow('Semente de soja 64 Z'); v.info('form semente 64 Z',[v.fv('preco'),v.fv('emb'),v.fv('cont'),v.fdis('un')]); v.cancel()
    v.info('cabeçalho',v.header())
    # Outro grupo
    v.clk('Cadastrar item'); v.fset('item','Trichoderma WP'); v.fset('grupo','Outro grupo…'); v.info('outro grupo',[v.labels(),v.fv('nnat')])
    v.fset('ngrupo','Biológicos'); v.fset('nnat','3.1.02 · Defensivos'); v.fset('un','kg'); v.fset('emb','Saco'); v.fset('cont','1'); v.fset('preco','80'); v.fset('pdata','2026-09-20'); v.btn('Salvar')
    v.info('salvou',[v.isopen(),v.alerts(),v.toast(),v.rowtxt('Biológicos'),v.rowtxt('Trichoderma')])
    # renomear grupo Fertilizantes
    v.clickrow('Fertilizantes 6'); v.fset('nome','Fertilizantes minerais'); v.btn('Salvar')
    v.info('grupo renomeado',[v.rowtxt('Fertilizantes minerais'),v.toast()])
    v.clickrow('MAP 11-52'); v.info('MAP grupo',[v.fv('grupo'),v.fopts('grupo')]); v.cancel()
    # completar pendências: limpar o texto 'Sem preço' e preencher
    for nome,preco in [('Calcário dolomítico','480'),('Semente de soja 64 Z','9,5')]:
        v.clickrow(nome); v.fset('preco',preco); v.fset('pdata','2026-09-20')
        if nome.startswith('Semente'): v.fset('cont','40')
        v.btn('Salvar'); v.info('salvo '+nome,[v.isopen(),v.alerts(),v.toast()])
    v.info('cabeçalho final',v.header()); v.info('chip Cadastro completo',v.J(CHIP%'Cadastro completo'))
    v.J("window.scrollTo(0,0)"); v.shot('ver_cadc_cd06_completo.png')
    v.info('erros (fora g2toast)',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
