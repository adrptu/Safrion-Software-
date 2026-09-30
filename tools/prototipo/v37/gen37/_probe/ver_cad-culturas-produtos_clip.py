# -*- coding: utf-8 -*-
"""Verificador · linha recém-cadastrada fica abaixo do limite do artboard (overflow: clip)? CD-02 (nova operação) e CD-06 (novo local)."""
import os, importlib.util, time, json
sp=importlib.util.spec_from_file_location('vlib',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-culturas-produtos_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
v=L.V()
POS=lambda txt: f"(()=>{{const root=document.querySelector('[data-root]').getBoundingClientRect(); const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.replace(/\\s+/g,' ').indexOf({json.dumps(txt)})>=0); if(!r) return null; const b=r.getBoundingClientRect(); return {{topo:Math.round(b.top-root.top), base:Math.round(b.bottom-root.top), altura_artboard:Math.round(root.height), doc:document.documentElement.scrollHeight}};}})()"
try:
    v.goto('CD-02.dc.html'); v.J("localStorage.clear()"); v.goto('CD-02.dc.html')
    v.clk('Operações e rendimentos')
    v.info('antes · Fertirrigação',v.J(POS('Sistema de gotejo T7')))
    v.clk('Cadastrar rendimento'); v.fset('op','Outra operação…'); v.fset('nop','Irrigação'); v.fset('conj','Pivô central 1')
    v.fset('modo','Informado'); v.fset('rend','3'); v.fset('maq','50'); v.fset('pess','1'); v.fset('vig','2027-06-30'); v.btn('Salvar')
    v.info('toast',v.toast())
    a=v.J(POS('Irrigação Tratos')); b=v.J(POS('Pivô central 1')); v.info('nova operação / conjunto',[a,b])
    v.J("window.scrollTo(0,99999)"); time.sleep(.3); v.shot('ver_cadc_clip_cd02.png')
    v.chk('CD-02: operação recém-criada visível dentro do artboard',a and b and b['base']<=b['altura_artboard'],[a,b])
    v.goto('CD-06.dc.html')
    v.info('antes · último local',v.J(POS('Galpão Boa Vista')))
    v.clk('Cadastrar local'); v.fset('nome','Galpão BV 2'); v.fset('faz','Boa Vista'); v.btn('Salvar'); v.info('toast',v.toast())
    c=v.J(POS('Galpão BV 2')); v.info('novo local',c)
    v.J("window.scrollTo(0,99999)"); time.sleep(.3); v.shot('ver_cadc_clip_cd06.png')
    v.chk('CD-06: local recém-criado visível dentro do artboard',c and c['base']<=c['altura_artboard'],c)
finally: v.fim()
