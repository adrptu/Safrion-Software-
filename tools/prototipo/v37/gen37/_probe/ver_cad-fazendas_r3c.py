# -*- coding: utf-8 -*-
"""Verificador r3c · CD-01 · Fazenda (posse Parceria agrícola), grupo novo com "Cadastrar talhão", rastreio de erro JS a cada passo."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess(); chk=L.chk
def E(tag): e=s.errs(); print('  [errs '+tag+']', e) if e else None
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html'); E('load')
    print('h2 load', s.js("[...document.querySelectorAll('main h2')].map(h=>h.innerText)"))
    s.click('+ Cadastrar fazenda'); E('abrir')
    s.fset('nome','Nova Esperança'); s.fset('mun','Sinop'); s.fset('uf','MT'); s.fset('area','600'); s.fset('posse','Parceria agrícola'); E('preench')
    print('LABELS parceria', s.labels())
    s.fset('arrend','Ana Prado'); s.fset('fim','2026-01-01'); s.fset('custo','7'); s.btn('Salvar'); print('ALERT fim vencido', s.alerts()); E('salvar1')
    s.fset('fim','2031-01-01'); s.fset('posse','Própria'); print('LABELS propria', s.labels())
    s.fset('posse','Parceria agrícola'); print('volta parceria', s.fv('arrend'), s.fv('fim'), s.fv('custo'))
    s.btn('Salvar'); time.sleep(.3); E('salvar2')
    print('aberto', s.aberto(), 'TOAST', s.toast())
    print('T0', json.dumps(s.rows(0)[-1:],ensure_ascii=False))
    print('T1', json.dumps(s.rows(1)[-3:],ensure_ascii=False))
    print('HEAD', s.head())
    print('h2 after', s.js("[...document.querySelectorAll('main h2')].map(h=>h.innerText)"))
    print('clk tal', s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Nova Esperança')>=0); const b=r&&[...r.querySelectorAll('button,a,[role=button]')].find(b=>b.innerText.indexOf('Cadastrar talhão')>=0); if(!b) return 'sem botão '+(r?r.innerHTML.slice(0,400):''); b.click(); return 'ok';})()")); time.sleep(.4); E('tal_new')
    print('ASIDE tal', s.aside()[:300]); print('faz', s.fv('faz'), s.fopts('faz'))
    s.btn('Cancelar'); time.sleep(.3); print('após cancelar aberto', s.aberto(), s.aside()[:200]); E('cancel')
    if s.aberto(): s.btn('Descartar alterações')
    s.openrow(0,'Santa Rita Santa Rita Agro'); E('open SR')
    s.fset('nome','Santa Rita do Sul'); s.btn('Salvar'); time.sleep(.3); E('rename')
    print('TOAST', s.toast())
    print('h2 after rename', s.js("[...document.querySelectorAll('main h2')].map(h=>h.innerText)"))
    print('MAPA', s.js("[...document.querySelectorAll('svg polygon, svg circle')].map(e=>e.getAttribute('fill'))"))
    s.shot('ver_cad-fazendas_r3c.png')
finally: s.close()
