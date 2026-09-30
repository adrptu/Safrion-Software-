# -*- coding: utf-8 -*-
"""Verificador 8 · fotos a 1440×1000 dos formulários e do painel; alcance do Salvar; textos dos formulários novos."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
SAL="(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar'||b.innerText.trim()==='Salvar polígono'); if(!b) return 'sem Salvar'; const r=b.getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom),innerHeight];})()"
try:
    s.go('CD-01.dc.html')
    s.openrow(0,'Boa Vista'); print('fazenda BV salvar', s.js(SAL)); s.shot('ver_cadf_form_faz.png')
    s.btn('Fechar') or s.btn('Cancelar')
    s.click('+ Cadastrar fazenda'); print('nova fazenda sub:', s.aside()[:160])
    s.btn('Fechar') or s.btn('Cancelar'); s.btn('Descartar alterações')
    s.click('Cadastrar talhão','header'); print('novo talhão sub:', s.aside()[:220]); s.shot('ver_cadf_form_tal_novo.png')
    s.btn('Fechar') or s.btn('Cancelar'); s.btn('Descartar alterações')
    s.go('CD-01det.dc.html#talhao=T1'); s.click('Definir polígono da T1-B','header'); s.click('Desenhar no mapa','aside'); s.click('Gerar prévia','aside'); s.click('Salvar polígono','aside')
    print('painel salvar', s.js(SAL)); s.shot('ver_cadf_painel.png')
    s.go('CD-01det.dc.html#talhao=ZZ'); s.shot('ver_cadf_nf.png'); print('nf head', s.head())
    print('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
