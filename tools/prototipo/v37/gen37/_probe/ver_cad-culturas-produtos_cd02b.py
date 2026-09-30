# -*- coding: utf-8 -*-
"""Verificador · CD-02 parte B: cultura, cultivar perene, nova cultivar, exclusão, estado sem pendências e cor do chip."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
CHIP="(()=>{const h=document.querySelector('header'); const el=[...h.querySelectorAll('span')].find(s=>/pend|premissa|semente/i.test(s.innerText)&&s.children.length<=2&&getComputedStyle(s).borderRadius!=='0px'); if(!el) return null; const cs=getComputedStyle(el); return [el.innerText.trim(),cs.backgroundColor,cs.color];})()"
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    v.info('chip inicial',v.J(CHIP))
    # 1 cultura
    v.clickrow('Café 1 cultivar'); v.info('form cultura Café',[v.title(),v.labels(),v.fdis('tipo'),v.fv('unid'),v.fopts('unid')])
    v.fset('unid','t/ha'); v.btn('Salvar'); v.info('toast/linha',[v.toast(),v.rowtxt('Café')])
    # 2 cultivar perene
    v.clickrow('Catuaí'); v.info('form Catuaí',[v.title(),v.labels(),v.dlg()[:400]]); v.cancel()
    # 3 nova cultivar
    v.clk('Cadastrar cultivar'); v.info('nova cultivar',[v.title(),v.labels(),v.fv('cult'),v.fv('tipo'),v.fv('sem')])
    v.fset('cult','Café'); v.info('nova cultivar · Café',[v.labels(),v.fv('tipo')])
    v.fset('cult','Milho'); v.info('nova cultivar · Milho',[v.labels(),v.fv('tipo'),v.fopts('sem')])
    v.cancel(); v.info('fechou?',v.isopen())
    # 4 exclusão da 64 Z (sem uso)
    v.info('células 64 Z',v.J(f"(()=>{{const r={v.ROW('64 Z')}; return [...r.querySelectorAll('button')].map(b=>(b.getAttribute('aria-label')||b.innerText))}})()"))
    # 5 chegar a sem pendências: 64 Z com semente criada + café com fonte medida
    v.clickrow('64 Z'); v.info('form 64 Z',[v.labels(),v.fv('sem')]); v.btn('Salvar'); v.info('toast 64Z',v.toast())
    v.clk('Operações e rendimentos'); v.clickrow('Derriçadeiras'); v.fset('fonte','Medição local'); v.btn('Salvar'); time.sleep(.3)
    v.info('cabeçalho sem pendências',v.header()); v.info('chip final',v.J("(()=>{const h=document.querySelector('header'); const el=[...h.querySelectorAll('span')].find(s=>/Sem pend/.test(s.innerText)&&s.children.length<=2); if(!el) return null; let e=el; const out=[]; while(e&&e!==h){const cs=getComputedStyle(e); out.push([e.tagName,cs.backgroundColor,cs.color]); e=e.parentElement;} return out;})()"))
    v.shot('ver_cadc_cd02_sempend.png')
    # 6 renomear cultura e checar listas
    v.clk('Culturas e cultivares'); v.clickrow('Soja 3 cultivares'); v.fset('nome','Soja RR'); v.btn('Salvar')
    v.clk('Operações e rendimentos'); v.clickrow('Trator 03'); v.info('opções cultura no rendimento',v.fopts('cult')); v.cancel()
    v.clk('Culturas e cultivares'); v.info('linhas Soja RR',[v.rowtxt('Soja RR'),v.rowtxt('58 W')])
    v.info('erros',v.errs())
finally: v.fim()
