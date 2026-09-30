# -*- coding: utf-8 -*-
"""Verificador r3d · o erro 'reading g2toast' no CD-01: quando aparece e se o toast some depois de 4,5 s."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
f=sys.argv[1] if len(sys.argv)>1 else 'CD-01.dc.html'
try:
    s.go(f); s.clear_ls(); s.go(f)
    s.js('(()=>{const rs=[...document.querySelectorAll("[role=table] [role=row]")]; for(const r of rs.slice(1,12)){ (r.querySelector("[role=cell] span")||r).click(); if(document.querySelector("aside[role=dialog]")) break; }})()'); time.sleep(.4)
    print(f,'aberto',s.aberto(), s.aside()[:80], flush=True)
    s.btn('Salvar'); time.sleep(.4)
    print(f,'toast', s.toast(), 'errs', s.errs(), flush=True)
    for i in range(11): time.sleep(.5)
    print(f,'toast após 5,9 s', repr(s.toast()), flush=True)
finally: s.close()
