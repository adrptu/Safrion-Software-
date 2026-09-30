# -*- coding: utf-8 -*-
"""Verificador · CD-07 parte C: exclusão de código entra no rascunho? (publicar → excluir → publicar)."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
try:
    v.goto('CD-07.dc.html')
    v.clk('Publicar estrutura'); v.info('publicou v6',[v.toast(),v.header()])
    btns=v.J(f"(()=>{{const r={v.ROW('PRJ-PIVO3')}; return r?[...r.querySelectorAll('button')].map(b=>b.getAttribute('aria-label')||b.innerText):null;}})()"); v.info('botões da linha PRJ-PIVO3',btns)
    v.J(f"(()=>{{const r={v.ROW('PRJ-PIVO3')}; const b=[...r.querySelectorAll('button')].find(b=>/Excluir/.test(b.getAttribute('aria-label')||'')); b&&b.click();}})()"); time.sleep(.4)
    v.info('depois do clique em excluir',[v.J("[...document.querySelectorAll('[role=alertdialog],[role=dialog]')].map(d=>d.innerText.replace(/\\s+/g,' ').slice(0,200))"),v.toast()])
    v.J(f"(()=>{{const r={v.ROW('PRJ-PIVO3')}; const b=[...r.querySelectorAll('button')].find(b=>b.innerText.trim()==='Excluir'); b&&b.click();}})()"); time.sleep(.4)
    for t in []: v.J(f"(()=>{{const b=[...document.querySelectorAll('[role=alertdialog] button,[role=dialog] button')].find(b=>b.innerText.trim()==={json.dumps(t)}); b&&b.click();}})()"); time.sleep(.2)
    time.sleep(.3)
    v.info('PRJ-PIVO3 ainda existe?',v.rowtxt('PRJ-PIVO3'))
    h=v.header(); v.info('cabeçalho após excluir',h)
    v.clk('Publicar estrutura'); t=v.toast(); v.info('publicar após excluir',t)
    v.chk('excluir código entra no rascunho (cabeçalho e Publicar reconhecem a alteração)',('rascunho' in h) and ('Nada a publicar' not in t),[h,t])
    v.info('erros (fora g2toast)',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
