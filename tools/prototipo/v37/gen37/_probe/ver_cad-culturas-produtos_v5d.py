# -*- coding: utf-8 -*-
"""v5 · CD-02 aba Operações: fonte → selo, selo verde, mover conjunto de operação, renomear operação, Outra operação vazia, rendimento por cultura e renomear cultura."""
import os, importlib.util, time, json
H=os.path.dirname(os.path.abspath(__file__))
def ld(n):
    sp=importlib.util.spec_from_file_location(n,os.path.join(H,n+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
L=ld('ver_cad-culturas-produtos_lib'); M=ld('ver_cad-culturas-produtos_v5m')
v=L.V()
SELO="(()=>{const s=[...document.querySelectorAll('header span')].find(x=>/pend|premissa|semente/i.test(x.innerText)&&x.children.length); return s?[s.innerText.trim(),getComputedStyle(s).backgroundColor]:null;})()"
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    v.clk('Operações e rendimentos')
    v.clickrow('Derriçadeiras'); v.info('form rend labels',[v.title(),v.labels(),v.fv('cult'),v.fv('fonte')])
    v.fset('fonte','Medição local'); v.btn('Salvar'); time.sleep(.3); v.info('fonte salva',[v.isopen(),v.alerts(),v.J(SELO)])
    v.clk('Culturas e cultivares'); v.clickrow('64 Z'); v.btn('Salvar'); time.sleep(.3); v.info('64 Z salvo → selo',[v.isopen(),v.J(SELO),v.header()[:120]])
    v.clk('Operações e rendimentos')
    # mover Trator 04 da Poda para Pulverização
    v.clickrow('Trator 04'); v.fset('op','Pulverização'); v.btn('Salvar'); time.sleep(.3)
    v.info('mover conjunto',[v.isopen(),v.alerts(),v.rowtxt('Poda'),v.rowtxt('Pulverização'),v.toast()])
    # renomear operação
    v.clickrow('Plantio Implantação'); v.fset('nome','Plantio direto'); v.btn('Salvar'); time.sleep(.3)
    v.info('renomear op',[v.isopen(),v.rowtxt('Plantio direto'),v.toast()])
    v.clickrow('Trator T1'); v.info('op no form do conjunto',[v.fv('op'),v.fopts('op')]); v.cancel()
    # Outra operação vazia
    v.clk('Cadastrar rendimento'); v.info('novo rend padrões',[v.fv('op'),v.fv('cult'),v.fv('fonte'),v.fv('modo'),v.fv('vig')])
    v.fset('op','Outra operação…'); v.fset('conj','Trator 05 + roçadeira'); v.btn('Salvar'); time.sleep(.3); v.info('outra op vazia',[v.isopen(),v.alerts()])
    v.cancel()
    # rendimento só para Soja na colheita e renomear Soja
    v.clk('Cadastrar rendimento'); v.fset('op','Colheita de grãos'); v.fset('conj','Colhedora Axial-Flow 7250 + trator com graneleiro'); v.fset('cult','Soja')
    v.info('campos',[v.labels()]); 
    v.fset('modo','Informado'); v.fset('rend','6'); v.fset('maq','950'); v.fset('impl','120'); v.fset('pess','2'); v.fset('pess_rs','38'); v.fset('vig','2027-06-30')
    v.btn('Salvar'); time.sleep(.3); v.info('rend soja',[v.isopen(),v.alerts(),v.rowtxt('Colheita de grãos'),v.toast()])
    v.clk('Culturas e cultivares'); v.clickrow('Soja 3 cultivares'); v.fset('nome','Soja RR'); v.btn('Salvar'); time.sleep(.3); v.info('Soja→Soja RR',[v.isopen(),v.toast()])
    v.clk('Operações e rendimentos'); v.info('linhas colheita',v.J("[...document.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()).filter(t=>/Colhedora/.test(t))"))
    v.info('overflow',v.overflow())
    v.info('erros',[e for e in v.errs() if 'g2toast' not in e])
    v.shot('ver_cadc_v5d.png')
finally: v.fim()
