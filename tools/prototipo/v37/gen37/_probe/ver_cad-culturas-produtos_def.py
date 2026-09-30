# -*- coding: utf-8 -*-
"""Verificador · valores-padrão dos formulários novos depois de renomear a cultura/grupo (CD-02, CD-06) e operação não tocada no rendimento novo."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
DRAFT="(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return [...a.querySelectorAll('select')].map(s=>s.id.replace(/^fx_g_\\w+?_/,'')+'='+s.value);})()"
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    # A rendimento novo sem tocar em Operação
    v.clk('Operações e rendimentos'); v.clk('Cadastrar rendimento'); v.info('selects do rendimento novo',v.J(DRAFT))
    v.fset('conj','Trator 05 + Pulverizador 2'); v.fset('modo','Informado'); v.fset('rend','10'); v.fset('maq','100'); v.fset('pess','1'); v.fset('vig','2027-06-30'); v.btn('Salvar')
    e1=[e for e in v.errs() if 'g2toast' not in e]; v.info('A · salvar sem tocar em Operação',[v.isopen(),v.alerts(),v.toast(),v.rowtxt('Trator 05'),e1])
    v.cancel()
    # B renomear Soja e cadastrar cultivar sem tocar em Cultura
    v.clk('Culturas e cultivares'); v.clickrow('Soja 3 cultivares'); v.fset('nome','Soja RR'); v.btn('Salvar')
    v.clk('Cadastrar cultivar'); v.info('selects da cultivar nova',[v.J(DRAFT),v.labels()])
    v.fset('nome','X1'); v.fset('dias','110'); v.btn('Salvar'); time.sleep(.2)
    e2=[e for e in v.errs() if 'g2toast' not in e]; v.info('B · salvar cultivar sem tocar em Cultura',[v.isopen(),v.alerts(),v.toast(),v.rowtxt('X1'),e2])
    v.chk('B · cultivar nova depois de renomear a cultura salva sem erro de JS',not e2 and not v.isopen(),e2)
    v.cancel()
    v.goto('CD-06.dc.html')
    # C renomear Fertilizantes e cadastrar item sem tocar em Grupo
    v.clickrow('Fertilizantes 6'); v.fset('nome','Fertilizantes minerais'); v.btn('Salvar')
    v.clk('Cadastrar item'); v.info('selects do item novo',v.J(DRAFT))
    v.fset('item','Sulfato de amônio'); v.fset('cont','50'); v.btn('Salvar'); time.sleep(.2)
    e3=[e for e in v.errs() if 'g2toast' not in e]; v.info('C · salvar item sem tocar em Grupo',[v.isopen(),v.alerts(),v.toast(),v.rowtxt('Sulfato'),e3])
    v.chk('C · item novo depois de renomear o grupo-padrão salva sem erro de JS',not e3 and not v.isopen(),e3)
finally: v.fim()
