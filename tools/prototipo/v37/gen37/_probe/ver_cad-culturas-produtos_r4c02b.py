# -*- coding: utf-8 -*-
"""r4 · CD-02: renomear cultura (propagação e semente), Outra cultura… (anual e perene), mover cultivar, excluir 64 Z."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    # excluir 64 Z
    r=v.J(f"(()=>{{const r={v.ROW('64 Z')}; const b=[...r.querySelectorAll('button')].pop(); if(!b) return 'sem botão'; b.click(); return b.getAttribute('aria-label')||b.innerText;}})()"); time.sleep(.4)
    v.info('excluir 64 Z',[r,v.J("[...document.querySelectorAll('[role=alertdialog]')].map(x=>x.innerText.replace(/\\s+/g,' '))")])
    v.btn('Excluir'); time.sleep(.3); v.info('depois excluir',[v.rowtxt('64 Z'),v.rowtxt('Soja'),v.header()[:150],v.toast()])
    # renomear Soja
    v.clickrow('Soja 3 cultivares'); v.fset('nome','Soja RR'); v.btn('Salvar'); time.sleep(.3)
    v.info('toast rename',v.toast()); v.info('linhas',[v.rowtxt('Soja RR'),v.rowtxt('58 W')])
    v.clickrow('58 W'); v.info('form 58 W após rename',[v.fv('cult'),v.fv('sem')]); v.fset('dias','119'); v.btn('Salvar'); time.sleep(.3)
    v.chk('58 W salva depois de renomear Soja → Soja RR (sem mexer na semente)',not v.isopen(),[v.alerts(),v.fv('sem')])
    v.cancel()
    # Outra cultura… anual
    v.clk('Cadastrar cultivar'); v.info('nova cultivar',[v.title(),v.labels(),v.fv('cult'),v.fv('sem')])
    v.fset('cult','Outra cultura…'); v.info('outra cultura campos',[v.labels(),v.fv('tipo'),v.fv('unid')])
    v.fset('ncult','Trigo'); v.fset('nome','TBIO Sossego'); v.fset('dias','120'); v.btn('Salvar'); time.sleep(.3)
    v.info('salvou trigo',[v.isopen(),v.alerts(),v.toast()]); v.info('linhas trigo',[v.rowtxt('Trigo'),v.rowtxt('TBIO')])
    v.info('LS',v.J("localStorage.getItem('talhao-os-cadastros-v1')"))
    # Outra cultura… perene
    v.clk('Cadastrar cultivar'); v.fset('cult','Outra cultura…'); v.fset('ncult','Laranja'); v.fset('tipo','Perene'); v.info('perene campos',v.labels())
    v.fset('unid','cx de 20 kg/ha'); v.fset('nome','Pera Rio'); v.btn('Salvar'); time.sleep(.3)
    v.info('salvou laranja',[v.isopen(),v.alerts(),v.toast()]); v.info('linhas laranja',[v.rowtxt('Laranja'),v.rowtxt('Pera Rio')])
    # mover cultivar Pérola → Milho
    v.clickrow('Pérola'); v.fset('cult','Milho'); v.info('pérola → milho campos',[v.labels(),v.fv('sem')]); v.btn('Salvar'); time.sleep(.3)
    v.info('mover pérola',[v.isopen(),v.alerts(),v.toast(),v.rowtxt('Feijão'),v.rowtxt('Milho')])
    v.cancel()
    # aba de rendimentos: opções de cultura
    v.clk('Operações e rendimentos'); v.clk('Cadastrar rendimento'); v.info('opções cultura rendimento',v.fopts('cult')); v.cancel()
    v.info('overflow',v.overflow()); v.info('erros',[e for e in v.errs() if 'g2toast' not in e])
    v.shot('ver_cadc_r4_c02b.png')
finally: v.fim()
