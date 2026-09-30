# -*- coding: utf-8 -*-
"""Verificador · CD-07 parte B: código já cadastrado à mão e depois 'Importar do ERP'; publicar e importar depois; corte com a prévia aberta."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
POS=lambda txt: f"(()=>{{const root=document.querySelector('[data-root]').getBoundingClientRect(); const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); if(!r) return null; const b=r.getBoundingClientRect(); return {{topo:Math.round(b.top-root.top), base:Math.round(b.bottom-root.top), artboard:Math.round(root.height)}};}})()"
try:
    v.goto('CD-07.dc.html')
    # 1 cadastra à mão o 3.1.07 que o ERP também traz
    v.clk('Cadastrar código'); v.fset('cod','3.1.07'); v.fset('nome','Serviços de terceiros'); v.fset('sup','3.1'); v.fset('ini','2026-07-01'); v.fset('conta','4.1.1.07'); v.btn('Salvar')
    v.info('salvo à mão',[v.isopen(),v.toast()])
    v.clk('Importar do ERP'); time.sleep(.2)
    v.info('prévia ainda lista 3.1.07 como novo?',v.J("(document.querySelector('[aria-label=\"Prévia da importação do ERP\"]')||{}).innerText"))
    v.info('PRJ-PIVO3 com a prévia aberta (1 código a mais)',v.J(POS('PRJ-PIVO3')))
    v.clk('Trazer 3 mudanças para o rascunho'); v.info('toast',v.toast())
    n=v.J("[...document.querySelectorAll('[role=row]')].filter(r=>/^3\\.1\\.07\\b/.test(r.innerText.replace(/\\s+/g,' ').trim())).length")
    v.info('linhas com código 3.1.07',[n,v.J("[...document.querySelectorAll('[role=row]')].filter(r=>r.innerText.indexOf('3.1.07')>=0).map(r=>r.innerText.replace(/\\s+/g,' ').trim())")])
    v.chk('importar não duplica código já existente na mesma dimensão',n==1,n)
    v.info('cabeçalho',v.header())
    v.clk('Publicar estrutura'); v.info('publicar',[v.toast(),v.header()])
    v.info('erros (fora g2toast)',[e for e in v.errs() if 'g2toast' not in e])
finally: v.fim()
