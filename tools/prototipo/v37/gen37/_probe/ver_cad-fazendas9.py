# -*- coding: utf-8 -*-
"""Verificador 9 · formulário longo da fazenda rola dentro do painel? talhão desconhecido em carga nova."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
try:
    s.go('CD-01.dc.html'); s.openrow(0,'Boa Vista')
    print(s.js("(()=>{const a=document.querySelector('aside[role=dialog]'); const cs=getComputedStyle(a); const r=a.getBoundingClientRect(); return {pos:cs.position, oy:cs.overflowY, h:r.height, top:r.top, sh:a.scrollHeight, ch:a.clientHeight, par:getComputedStyle(a.parentElement).position};})()"))
    s.js("(()=>{const a=document.querySelector('aside[role=dialog]'); a.scrollTop=a.scrollHeight;})()"); time.sleep(.3)
    print('após rolar', s.js("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar'); const r=b.getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom),innerHeight];})()"))
    s.shot('ver_cadf_form_faz_fim.png')
    s.go('CD-01.dc.html'); s.go('CD-01det.dc.html#talhao=ZZ'); print('nf head', s.head()); print('nf main', s.js("document.querySelector('main').innerText.replace(/\\s+/g,' ').slice(0,300)"))
    s.shot('ver_cadf_nf.png')
finally: s.close()
