# -*- coding: utf-8 -*-
"""Verificador r3b · CD-01 · entidade Fazenda: cadastrar (validação, fuso, posse), grupo novo, editar, inativar, renomear."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess(); chk=L.chk
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    print('click', s.click('+ Cadastrar fazenda'))
    print('ASIDE', s.aside()[:900]); print('LABELS', s.labels()); print('uf,fuso', s.fv('uf'), s.fv('fuso'), s.fopts('fuso'))
    s.shot('ver_cad-fazendas_r3b_form.png')
    s.btn('Salvar'); print('ALERTS vazio', s.alerts())
    s.fset('nome','Santa Rita'); s.btn('Salvar'); print('ALERT dup', s.alerts())
    s.fset('nome','Nova Esperança'); s.fset('mun','Sinop'); s.fset('uf','MT'); print('fuso MT', s.fv('fuso'))
    s.fset('uf','BA'); print('fuso BA', s.fv('fuso')); s.fset('uf','MT')
    s.fset('area','600'); s.fset('posse','Parceria'); print('LABELS parceria', s.labels())
    s.fset('arrend','Ana Prado'); s.fset('fim','2026-01-01'); s.fset('custo','7'); s.btn('Salvar'); print('ALERT fim vencido', s.alerts())
    s.fset('fim','2031-01-01'); s.fset('posse','Própria'); print('LABELS propria', s.labels(), 'arrend', s.fv('arrend'))
    s.fset('posse','Parceria'); print('volta parceria arrend', s.fv('arrend'), s.fv('fim'), s.fv('custo'))
    s.btn('Salvar'); time.sleep(.3)
    print('aberto', s.aberto(), 'TOAST', s.toast())
    print('T0', json.dumps(s.rows(0),ensure_ascii=False))
    print('T1', json.dumps(s.rows(1),ensure_ascii=False)[-600:])
    print('HEAD', s.head())
    # grupo novo: ação Cadastrar talhão
    print('clk tal', s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('Nova Esperança')>=0); const b=r&&[...r.querySelectorAll('button,a')].find(b=>b.innerText.indexOf('Cadastrar talhão')>=0); if(!b) return 'sem botão'; b.click(); return 'ok';})()")); time.sleep(.4)
    print('ASIDE tal', s.aside()[:400]); print('faz', s.fv('faz'), s.fopts('faz'))
    s.btn('Cancelar'); time.sleep(.3); print('após cancelar aberto', s.aberto(), s.aside()[:200])
    if s.aberto(): s.btn('Descartar alterações')
    # editar Santa Rita
    print('open SR', s.openrow(0,'Santa Rita Santa Rita Agro')); print('ASIDE SR', s.aside()[:300]); print('LABELS SR', s.labels())
    s.fset('area','1000'); s.fset('sit','Inativa'); s.btn('Salvar'); print('ALERT SR', s.alerts())
    s.fset('area','1480'); s.fset('sit','Ativa'); s.fset('nome','Santa Rita do Sul'); s.btn('Salvar'); time.sleep(.3)
    print('aberto', s.aberto(), 'TOAST', s.toast())
    print('T1 após renomear', json.dumps(s.rows(1),ensure_ascii=False)[:500])
    print('MAPA', s.js("[...document.querySelectorAll('svg polygon, svg circle')].map(e=>e.getAttribute('fill'))"))
    print('mapa titulo', s.js("[...document.querySelectorAll('main h2')].map(h=>h.innerText)"))
    print('ERRS', s.errs())
finally: s.close()
