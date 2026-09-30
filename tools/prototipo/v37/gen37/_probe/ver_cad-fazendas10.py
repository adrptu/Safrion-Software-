# -*- coding: utf-8 -*-
"""Verificador 10 · link de ORIGEM da parcela, Esc no cadastro de fazenda aberto a partir do talhão, safra encerrada após editar a área."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
try:
    s.go('CD-01det.dc.html#talhao=T1'); s.openrow(1,'T1-B'); print('origem', s.js("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>[a.innerText.trim(),a.getAttribute('href')])"))
    s.btn('Fechar')
    s.go('CD-01.dc.html'); s.click('Cadastrar talhão','header'); s.fset('t','Q1'); s.fset('decl','12'); s.fset('faz','Cadastrar fazenda…'); s.fset('nome','X')
    s.js("document.querySelector('aside[role=dialog]').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
    print('esc 1', s.aside()[:60], '|', s.alerts()[:80])
    s.btn('Descartar alterações'); time.sleep(.2); print('após descartar', s.aside()[:40], s.fv('t'), s.fv('decl'), s.fv('faz'))
    # safra encerrada após aumentar a área cultivável do T3 (talhão inteiro 96 ha em 2025/26)
    s.btn('Cancelar'); s.btn('Descartar alterações')
    s.openrow(1,'T3 Sequeiro'); s.fset('decl','100'); s.fset('motivo','Documento desatualizado'); s.btn('Salvar'); time.sleep(.3)
    s.go('CD-01det.dc.html#talhao=T3'); s.click('Expandir tudo'); print('T3 safras', s.rows(1))
    s.shot('ver_cadf_t3_encerrada.png')
finally: s.close()
