# -*- coding: utf-8 -*-
"""Verificador · CD-06 parte B: item sem preço (campo Preço), local novo/renomeado x Local padrão, estado completo, inativar com saldo."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    v.goto('CD-06.dc.html'); v.J("localStorage.clear()"); v.goto('CD-06.dc.html')
    # 1 Calcário sem preço: só troca o local padrão e salva
    v.clickrow('Calcário dolomítico'); pv=v.fv('preco'); v.info('valor do campo Preço ao abrir Calcário',repr(pv))
    v.chk('campo Preço de referência abre vazio no item sem preço',pv=='',repr(pv))
    v.fset('local','Galpão 2'); v.btn('Salvar'); time.sleep(.2)
    al=v.alerts(); v.info('salvar Calcário só trocando o local',[v.isopen(),al,v.J("[...document.querySelectorAll('aside [id$=_err], aside .g2err, aside [role=alert]')].map(e=>e.innerText)"),v.toast()])
    v.chk('salvar item sem preço sem mexer no preço não dá erro',not v.isopen(),al)
    v.shot('ver_cadc_cd06_calcario.png')
    v.cancel()
    # 2 local novo aparece no Local padrão do item?
    v.clk('Cadastrar local'); v.fset('nome','Galpão BV 2'); v.fset('faz','Boa Vista'); v.btn('Salvar')
    v.clickrow('MAP 11-52'); op=v.fopts('local'); v.info('Local padrão depois do local novo',op)
    v.chk('local recém-cadastrado é oferecido como Local padrão do item','Galpão BV 2' in (op or []),op)
    v.cancel()
    # 3 renomear local com itens
    v.clickrow('Galpão 1 Santa Rita',1,'span'); v.fset('nome','Galpão Norte'); v.btn('Salvar'); time.sleep(.2)
    v.info('linha do local renomeado',[v.rowtxt('Galpão Norte',1)])
    v.clickrow('Calcário dolomítico'); v.info('Local padrão do Calcário e opções após renomear',[v.fv('local'),v.fopts('local')]); v.cancel()
    v.clickrow('KCl 60%'); v.info('KCl local',[v.fv('local')]); v.cancel()
    # 4 inativar item com saldo
    v.clickrow('Glifosato 480'); v.fset('sit','Inativo'); v.btn('Salvar'); v.info('toast inativar com saldo',[v.toast(),v.rowtxt('Glifosato 480')])
    v.info('cabeçalho',v.header())
    v.info('erros (fora g2toast)',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
