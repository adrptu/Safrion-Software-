# -*- coding: utf-8 -*-
"""Verificador · CD-02 parte C: Cadastrar rendimento, Outra operação, trocar operação de um conjunto, formulário da operação nova."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    v.clk('Operações e rendimentos')
    v.clk('Cadastrar rendimento'); v.info('novo rendimento',[v.title(),v.labels(),v.fv('op'),v.fv('cult'),v.fv('modo'),v.fv('fonte')])
    v.fset('op','Outra operação…'); v.info('outra operação',[v.labels(),v.fv('nproc'),v.fopts('nproc')])
    v.fset('nop','Irrigação'); v.fset('conj','Pivô central 1'); v.fset('cult','Café')
    v.fset('modo','Informado'); v.fset('rend','3'); v.fset('maq','50'); v.fset('impl','0'); v.fset('pess','1'); v.fset('pess_rs','30'); v.fset('vig','2027-06-30')
    v.btn('Salvar'); v.info('salvou? alerts',[v.isopen(),v.alerts(),v.toast()])
    v.info('linhas Irrigação',[v.rowtxt('Irrigação'),v.rowtxt('Pivô central 1')])
    v.clickrow('Irrigação'); v.info('form operação nova',[v.title(),v.labels(),v.fv('nome'),v.fv('proc'),v.fv('atvs')])
    v.fset('atvs','Irrigação de salvamento; Irrigação de plantio'); v.btn('Salvar'); v.info('toast op',v.toast())
    # trocar operação de um conjunto existente (Trator 04 · Poda → Adubação a lanço)
    v.clickrow('Trator 04'); v.fset('op','Adubação a lanço'); v.btn('Salvar'); time.sleep(.3)
    v.info('poda/adubação depois',[v.rowtxt('Poda'),v.rowtxt('Adubação a lanço')])
    v.info('cabeçalho',v.header())
    v.info('overflow',v.overflow())
    v.shot('ver_cadc_cd02_rend2.png')
    v.info('erros (fora g2toast)',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
