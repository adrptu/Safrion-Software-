# -*- coding: utf-8 -*-
"""v5 · CD-02: form de cultivar aberto e a primária da outra aba (Cadastrar rendimento) — quantos painéis, o que o usuário vê."""
import os, importlib.util, time, json
H=os.path.dirname(os.path.abspath(__file__))
def ld(n):
    sp=importlib.util.spec_from_file_location(n,os.path.join(H,n+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
L=ld('ver_cad-culturas-produtos_lib'); M=ld('ver_cad-culturas-produtos_v5m')
v=L.V()
AS="[...document.querySelectorAll('aside[role=dialog]')].map(a=>{const b=a.getBoundingClientRect(); return [(a.querySelector('h2')||{}).innerText, Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height), getComputedStyle(a).zIndex];})"
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    # caso 1: form limpo (sem alteração), troca de aba e primária
    v.clickrow('58 W'); v.clk('Operações e rendimentos'); v.info('1 · form limpo, aba trocada',v.J(AS))
    M.mclick(v,"[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Cadastrar rendimento')"); v.info('1 · após Cadastrar rendimento (mouse)',[v.J(AS),v.J("document.body.innerText.indexOf('Há alterações não salvas')>=0")])
    v.shot('ver_cadc_v5c_1.png')
    v.cancel(); v.cancel(); v.info('1 · após cancelar',v.J(AS))
    # caso 2: form sujo e primária da mesma aba (referência do comportamento do motor)
    v.clk('Culturas e cultivares'); v.clickrow('58 W'); v.fset('dias','121')
    M.mclick(v,"[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Cadastrar cultivar')"); v.info('2 · sujo + Cadastrar cultivar',[v.J(AS),v.J("document.body.innerText.indexOf('Há alterações não salvas')>=0")])
    v.btn('Descartar alterações'); v.cancel(); v.info('2 · fim',v.J(AS))
    # caso 3: rendimento aberto e primária da aba Culturas
    v.clk('Operações e rendimentos'); v.clickrow('Trator 03'); v.clk('Culturas e cultivares')
    M.mclick(v,"[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Cadastrar cultivar')"); v.info('3 · rendimento aberto + Cadastrar cultivar',v.J(AS))
    v.shot('ver_cadc_v5c_3.png')
    v.info('erros',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
