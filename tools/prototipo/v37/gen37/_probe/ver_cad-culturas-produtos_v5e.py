# -*- coding: utf-8 -*-
"""v5 · CD-06: renomear grupo, mover item, excluir item e selo, item novo (validações e 'Sem preço'), inativo fora da contagem, locais (tanque/silo/renomear/excluir)."""
import os, importlib.util, time, json
H=os.path.dirname(os.path.abspath(__file__))
def ld(n):
    sp=importlib.util.spec_from_file_location(n,os.path.join(H,n+'.py')); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
L=ld('ver_cad-culturas-produtos_lib'); M=ld('ver_cad-culturas-produtos_v5m')
v=L.V()
SELO="(()=>{const h=document.querySelector('header h1'); const s=h&&h.parentElement.querySelector('span[style*=border-radius]'); return s?[s.innerText.trim(),getComputedStyle(s).backgroundColor,getComputedStyle(s).color]:null;})()"
try:
    v.goto('CD-06.dc.html'); v.J("localStorage.clear()"); v.goto('CD-06.dc.html')
    v.info('selo inicial',v.J(SELO))
    v.clickrow('Fertilizantes 6 itens'); v.fset('nome','Fertilizantes minerais'); v.btn('Salvar'); time.sleep(.3)
    v.info('renomear grupo',[v.isopen(),v.rowtxt('Fertilizantes minerais'),v.toast()])
    v.clickrow('MAP 11-52'); v.info('MAP grupo no form',[v.fv('grupo'),v.fopts('grupo')]); v.cancel()
    v.clk('Cadastrar item'); v.info('novo item padrões',[v.fv('grupo'),v.fv('un'),v.fdis('un'),v.fv('emb'),v.fv('ctrl'),v.fv('local'),v.fv('sit')])
    v.fset('item','Sulfato de amônio'); v.fset('preco','2,15'); v.btn('Salvar'); time.sleep(.3); v.info('novo item sem cont e sem data',[v.isopen(),v.alerts()])
    v.fset('cont','50'); v.fset('preco',''); v.btn('Salvar'); time.sleep(.3)
    v.info('novo item sem preço',[v.isopen(),v.alerts(),v.rowtxt('Sulfato'),v.J(SELO),v.toast()])
    # mover Ureia para Corretivos
    v.clickrow('Ureia 45%'); v.fset('grupo','Corretivos'); v.btn('Salvar'); time.sleep(.3)
    v.info('mover Ureia',[v.isopen(),v.alerts(),v.rowtxt('Corretivos'),v.rowtxt('Fertilizantes minerais')])
    # inativar Calcário (sem preço) → sai da contagem
    v.clickrow('Calcário'); v.fset('sit','Inativo'); v.btn('Salvar'); time.sleep(.3); v.info('Calcário inativo',[v.isopen(),v.alerts(),v.rowtxt('Calcário'),v.J(SELO)])
    # excluir Sulfato (novo, sem saldo)
    r=v.J(f"(()=>{{const r={v.ROW('Sulfato')}; const b=r&&[...r.querySelectorAll('button')].pop(); if(!b) return 'sem botão'; b.click(); return b.getAttribute('aria-label')||b.innerText;}})()"); time.sleep(.3)
    v.info('excluir sulfato',[r,v.J("[...document.querySelectorAll('[role=alertdialog]')].map(x=>x.innerText.replace(/\\s+/g,' '))")]); v.btn('Excluir'); time.sleep(.3)
    v.info('depois excluir',[v.rowtxt('Sulfato'),v.J(SELO)])
    # locais
    v.clk('Cadastrar local'); v.info('novo local',[v.title(),v.labels(),v.fv('faz'),v.fv('tipo')])
    v.fset('nome','Tanque BV'); v.fset('faz','Boa Vista'); v.fset('tipo','Tanque'); v.info('tanque campos',v.labels()); v.btn('Salvar'); time.sleep(.3); v.info('tanque sem cap',[v.isopen(),v.alerts()])
    v.fset('cap','8000'); v.btn('Salvar'); time.sleep(.3); v.info('tanque salvo',[v.isopen(),v.rowtxt('Tanque BV'),v.toast()])
    v.clk('Cadastrar local'); v.fset('nome','Silo BV'); v.fset('tipo','Silo'); v.info('silo novo campos',[v.labels(),v.fv('capa'),v.fdis('capa')]); v.btn('Salvar'); time.sleep(.3); v.info('silo salvo',[v.isopen(),v.rowtxt('Silo BV')])
    v.clickrow('Galpão 2'); v.fset('nome','Galpão 2 SR'); v.btn('Salvar'); time.sleep(.3); v.info('renomear local',[v.isopen(),v.toast(),v.rowtxt('Galpão 2 SR')])
    v.clickrow('MAP 11-52'); v.info('MAP local',[v.fv('local'),v.fopts('local')]); v.cancel()
    v.clk('Cadastrar item'); v.info('novo item local padrão',v.fv('local')); v.cancel()
    v.info('overflow',v.overflow()); v.info('erros',[e for e in v.errs() if 'g2toast' not in e])
    v.shot('ver_cadc_v5e.png')
finally: v.fim()
