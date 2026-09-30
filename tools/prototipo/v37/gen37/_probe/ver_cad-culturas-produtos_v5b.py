# -*- coding: utf-8 -*-
"""v5 · CD-02 aba Culturas: clique real do mouse nas linhas-pai/filhas, inativar/excluir 64 Z e cabeçalho, unidade da cultura, abas com formulário aberto, Comparar."""
import os, importlib.util, time, json
H=os.path.dirname(os.path.abspath(__file__))
def ld(n):
    sp=importlib.util.spec_from_file_location(n,os.path.join(H,n+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
L=ld('ver_cad-culturas-produtos_lib'); M=ld('ver_cad-culturas-produtos_v5m')
v=L.V()
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    for ci in (1,2,4):
        M.mclick(v,M.cell(v,'Soja 3 cultivares',ci)); v.info(f'mouse Soja cel {ci}',[v.isopen(),v.title(),v.rowtxt('Soja 3 cultivares')]); v.cancel()
    M.mclick(v,M.cell(v,'58 W',1)); v.info('mouse 58 W ciclo',[v.isopen(),v.title()]); v.cancel()
    M.mclick(v,M.cell(v,'Catuaí',3)); v.info('mouse Catuaí uso',[v.isopen(),v.title(),v.labels()]); v.cancel()
    # inativar 64 Z
    v.clickrow('64 Z'); v.fset('sit','Inativa'); v.btn('Salvar'); time.sleep(.3)
    v.info('64 Z inativa',[v.isopen(),v.alerts(),v.rowtxt('64 Z'),v.header()[:140],v.toast()])
    # unidade da cultura Milho
    v.clickrow('Milho 1 cultivar'); v.fset('unid','t/ha'); v.btn('Salvar'); time.sleep(.3)
    v.info('Milho t/ha',[v.isopen(),v.rowtxt('Milho 1'),v.toast()])
    v.clickrow('Feijão 1 cultivar'); v.fset('nome','Soja'); v.btn('Salvar'); time.sleep(.3); v.info('Feijão→Soja',[v.isopen(),v.alerts()]); v.cancel()
    # abas com formulário aberto e alterado
    v.clickrow('58 W'); v.fset('dias','121'); v.clk('Operações e rendimentos'); time.sleep(.3)
    v.info('troca aba com form sujo',[v.isopen(),v.title(),v.visible_btns()[:5]])
    v.clk('Cadastrar rendimento'); time.sleep(.3); v.info('primária com form sujo',[v.isopen(),v.title(),v.J("document.body.innerText.indexOf('Há alterações não salvas')>=0")])
    v.btn('Descartar alterações'); time.sleep(.3); v.info('depois descartar',[v.isopen(),v.title()]); v.cancel()
    v.clk('Comparar com o realizado'); time.sleep(.3); v.info('comparar',[v.toast(),v.J("document.body.innerText.indexOf('19,8')")])
    v.clk('Culturas e cultivares'); 
    v.J("(()=>{const i=document.querySelector('input[placeholder^=Buscar]'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'Pérola'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.4)
    v.info('busca Pérola',v.J("[...document.querySelectorAll('[role=table] [role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()).slice(0,6)"))
    v.info('erros',[e for e in v.errs() if 'g2toast' not in e])
    v.shot('ver_cadc_v5b.png')
finally: v.fim()
