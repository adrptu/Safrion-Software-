# -*- coding: utf-8 -*-
"""Verificador r3f · CD-01 · motivo da diferença, inativar/reativar talhão e fazenda, mapa (clique e cor), estado do cabeçalho."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
def P(*a): print(*a, flush=True)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.openrow(1,'T4 Sequeiro'); s.fset('decl','212'); P('LABELS', s.labels()); s.btn('Salvar'); P('ALERT', s.alerts())
    s.fset('motivo','APP ou reserva'); s.btn('Salvar'); time.sleep(.3); P('aberto', s.aberto(), 'toast', s.toast())
    P('T4 row', s.rowtxt(1,'T4 Sequeiro')); P('SR', s.rowtxt(1,'Santa Rita 8')); P('FazSR', s.rowtxt(0,'Santa Rita Santa Rita Agro'))
    P('MAPA', s.js("[...document.querySelectorAll('svg polygon, svg circle')].map(e=>e.getAttribute('fill'))"))
    # mapa: clicar no T3
    s.js("(()=>{const e=[...document.querySelectorAll('svg polygon')][3]; e.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()"); time.sleep(.4)
    P('mapa→', s.aside()[:60]); s.btn('Cancelar')
    # inativar B1 e Boa Vista, depois reativar
    s.openrow(1,'B1 Sequeiro'); s.fset('sit','Inativo'); s.btn('Salvar'); time.sleep(.3); P('toast B1', s.toast()); P('B1', s.rowtxt(1,'B1 Sequeiro')); P('BV g', s.rowtxt(1,'Boa Vista'))
    P('HEAD', s.head()[:200])
    s.openrow(0,'Boa Vista Boa Vista Ltda'); s.fset('sit','Inativa'); s.btn('Salvar'); time.sleep(.3); P('toast BV', s.toast(), s.alerts()); P('BV faz', s.rowtxt(0,'Boa Vista')); P('BV g', s.rowtxt(1,'Boa Vista'))
    P('HEAD', s.head()[:200])
    s.click('Cadastrar talhão','header'); P('faz opts com BV inativa', s.fopts('faz')); s.btn('Cancelar')
    s.openrow(1,'B1 Sequeiro'); P('B1 form', s.aside()[:80], 'faz opts', s.fopts('faz')); s.fset('sit','Ativo'); s.btn('Salvar'); P('ALERT reativar B1 com BV inativa', s.alerts()); s.btn('Cancelar'); s.btn('Descartar alterações')
    s.openrow(0,'Boa Vista Boa Vista Ltda'); s.fset('sit','Ativa'); s.btn('Salvar'); time.sleep(.3); P('reativa BV', s.toast(), s.alerts())
    s.openrow(1,'B1 Sequeiro'); s.fset('sit','Ativo'); s.btn('Salvar'); time.sleep(.3); P('reativa B1', s.toast(), s.alerts()); P('B1', s.rowtxt(1,'B1 Sequeiro'))
    # ordenação/filtro na árvore
    s.shot('ver_cad-fazendas_r3f.png')
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
