# -*- coding: utf-8 -*-
"""Verificador r3 · estado inicial das três telas: erros, cabeçalho, botões visíveis, largura/altura, textos cortados, capturas completas."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    for f in ['CD-02.dc.html','CD-06.dc.html','CD-07.dc.html']:
        v.goto(f); v.J("localStorage.clear()"); v.goto(f)
        v.info(f+' header',v.header()); v.info('botoes',v.visible_btns()); v.info('overflow',v.overflow()); v.info('errs',v.errs())
        h=v.J("document.querySelector('[data-root]').getBoundingClientRect().height")
        v.c.size(1440,int(h)+20); time.sleep(.4); v.shot('ver_cadc_r3_'+f[:5]+'_full.png'); v.c.size(1440,1000)
        if f=='CD-02.dc.html':
            v.clk('Operações e rendimentos'); v.info('aba1 overflow',v.overflow()); v.info('aba1 botoes',v.visible_btns())
            v.c.size(1440,int(h)+20); time.sleep(.4); v.shot('ver_cadc_r3_CD-02_aba1_full.png'); v.c.size(1440,1000)
finally: v.fim()
