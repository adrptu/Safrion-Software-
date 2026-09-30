# -*- coding: utf-8 -*-
"""r4 · CD-02 aba Culturas: formulário da cultura, cultivar perene/anual, semente (validações), 64 Z, localStorage → CD-06."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    v.info('tabs',v.J("[...document.querySelectorAll('[role=tab]')].map(t=>t.innerText+'='+t.getAttribute('aria-selected'))"))
    # cultura
    v.clickrow('Café 1 cultivar'); v.info('form Café',[v.isopen(),v.title(),v.labels(),v.fdis('tipo'),v.fv('tipo'),v.fv('unid'),v.fopts('unid')])
    v.cancel()
    # cultivar perene
    v.clickrow('Catuaí'); v.info('form Catuaí',[v.title(),v.labels()]); v.cancel()
    # cultivar anual 58 W
    v.clickrow('58 W'); v.info('form 58 W',[v.title(),v.labels(),v.fv('sem'),v.fopts('sem')])
    v.fset('sem','Semente de milho AG 8700'); v.btn('Salvar'); v.chk('58 W · semente de outra cultura barrada',v.isopen() and 'soja' in v.alerts().lower(),v.alerts())
    v.fset('sem','Semente de soja 62 X'); v.btn('Salvar'); v.chk('58 W · semente já vinculada barrada',v.isopen() and '62 X' in v.alerts(),v.alerts())
    v.cancel(); v.info('fechou',v.isopen())
    # 64 Z
    v.info('linha 64 Z',v.rowtxt('64 Z'))
    v.clickrow('64 Z'); v.info('form 64 Z',[v.labels(),v.fv('sem')]); v.fset('dias','126'); v.btn('Salvar'); time.sleep(.3)
    v.info('toast 64 Z',v.toast()); v.info('linha 64 Z depois',v.rowtxt('64 Z')); v.info('cabeçalho',v.header())
    v.info('LS',v.J("localStorage.getItem('talhao-os-cadastros-v1')"))
    v.chk('64 Z · semente criada e cabeçalho sem "sem semente"',('Semente de soja 64 Z' in (v.rowtxt('64 Z') or '')) and 'sem semente' not in v.header())
    v.goto('CD-06.dc.html')
    v.info('CD-06 Sementes',[v.rowtxt('Sementes'),v.rowtxt('Semente de soja 64 Z')]); v.info('CD-06 cabeçalho',v.header())
    v.clickrow('Semente de soja 64 Z'); v.info('form item 64 Z',[v.title(),v.dlg()[:900]]); v.cancel()
    v.info('erros',v.errs())
finally: v.fim()
