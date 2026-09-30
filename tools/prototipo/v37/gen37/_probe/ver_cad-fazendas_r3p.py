# -*- coding: utf-8 -*-
"""Verificador r3p · nome longo de fazenda e de arrendador: largura das tabelas, texto cortado, cabeçalho do detalhe."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
def fresh(u): s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.click('+ Cadastrar fazenda'); s.fset('nome','Fazenda Nossa Senhora Aparecida do Vale do Araguaia'); s.fset('mun','São Félix do Araguaia'); s.fset('uf','MT'); s.fset('area','2500'); s.fset('posse','Arrendada')
    s.fset('arrend','Agropecuária Irmãos Vasconcelos de Albuquerque Ltda · CNPJ 12.345.678/0001-90'); s.fset('fim','2032-06-30'); s.fset('custo','12'); s.fset('pend','Contrato de arrendamento aguardando reconhecimento de firma do segundo arrendador'); s.btn('Salvar'); time.sleep(.3)
    P('salvo', not s.aberto(), s.alerts())
    s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Aparecida')>=0); [...r.querySelectorAll('button,a,[role=button]')].find(b=>b.innerText.indexOf('Cadastrar talhão')>=0).click();})()"); time.sleep(.4)
    s.fset('t','A12'); s.fset('decl','800'); s.btn('Salvar'); time.sleep(.3)
    P('OVF lista', s.overflow())
    s.shot('ver_cad-fazendas_r3p_lista.png', full=True)
    href=s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('A12')===0); return r.querySelector('a').getAttribute('href');})()")
    fresh(href); P('OVF det', s.overflow()); P('head w', s.js("(()=>{const h=document.querySelector('header'); return [h.scrollWidth,h.clientWidth, document.querySelector('header select').getBoundingClientRect().width];})()"))
    s.shot('ver_cad-fazendas_r3p_det.png')
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
