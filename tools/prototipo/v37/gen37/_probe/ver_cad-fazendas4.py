# -*- coding: utf-8 -*-
"""Verificador 4 · CD-01 · localizar o console.error 'reading g2toast' passo a passo."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
n0=[0]
def step(nome):
    e=s.errs(); novo=e[n0[0]:]; n0[0]=len(e); print(f'{nome:45s}', novo if novo else '-', flush=True)
try:
    s.go('CD-01.dc.html'); step('carga')
    s.click('Cadastrar talhão','header'); step('abrir talhão novo')
    s.fset('t','Z5'); step('digitar t')
    s.fset('sis','Pivô central'); step('sis pivô')
    s.fset('decl','50'); step('decl')
    s.btn('Salvar'); step('salvar com erro')
    s.fset('sis','Sequeiro'); step('sis sequeiro')
    s.fset('faz','Cadastrar fazenda…'); step('escolher Cadastrar fazenda…')
    s.fset('nome','Rascunho'); step('nome fazenda')
    s.btn('Cancelar'); step('cancelar fazenda')
    s.btn('Descartar alterações'); step('descartar')
    s.btn('Cancelar'); step('cancelar talhão'); s.btn('Descartar alterações'); step('descartar talhão')
    s.openrow(1,'T2 Sequeiro'); step('abrir T2')
    s.fset('decl','310'); step('decl 310')
    s.fset('motivo','Carreador ou estrada'); step('motivo')
    s.btn('Salvar'); step('salvar T2')
    s.js("(()=>{const p=[...document.querySelectorAll('svg polygon')][3]; p.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()"); time.sleep(.4); step('clique mapa T3')
    s.btn('Fechar') or s.btn('Cancelar'); step('fechar')
    s.click('Importar geometrias'); step('importar geometrias'); print('toast', s.toast())
    s.click('Expandir tudo'); step('expandir'); s.click('Recolher'); step('recolher')
    s.js("document.querySelectorAll('[role=table]')[1].querySelectorAll('.g2hb')[0].click()"); time.sleep(.3); step('ordenar talhões')
    print(json.dumps(s.rows(1),ensure_ascii=False))
finally: s.close()
