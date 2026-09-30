# -*- coding: utf-8 -*-
"""Verificador · 'Cadastrar rendimento' sem tocar em Operação (atual) × '+ Novo rendimento' da linha de base."""
import os, importlib.util, time, json, sys
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
BASE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','ver_cadc_base_srv')
for rot,root,tab,bt in [('atual',None,True,'Cadastrar rendimento'),('base',os.path.abspath(BASE),False,'+ Novo rendimento')]:
    v=L.V(root=root)
    try:
        v.goto('CD-02.dc.html')
        if tab: v.clk('Operações e rendimentos')
        r=v.clk(bt,exact=False); v.info(rot+' · abrir',[r,v.title(),v.fv('op')])
        v.fset('conj','Trator 05 + Pulverizador 2'); v.fset('modo','Informado'); v.fset('rend','10'); v.fset('maq','100'); v.fset('pess','1'); v.fset('vig','2027-06-30'); v.btn('Salvar')
        v.info(rot+' · salvar sem tocar em Operação',[v.isopen(),v.alerts(),v.toast(),v.fv('op')])
        if rot=='atual':
            v.J("document.querySelector('aside[role=dialog] [id$=\"_op\"]').scrollIntoView({block:'center'})"); time.sleep(.2); v.shot('ver_cadc_cd02_rend_op.png')
    finally: v.fim()
