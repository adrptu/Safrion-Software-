# -*- coding: utf-8 -*-
"""Verificador 1: carga das duas telas, erros de JS, transbordo, fotos."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    print('ERR', s.errs()); print('HEAD', s.head()); print('OVF', s.overflow())
    print('T0', json.dumps(s.rows(0),ensure_ascii=False)); print('T1', json.dumps(s.rows(1),ensure_ascii=False))
    print('H', s.js("document.documentElement.scrollHeight"))
    s.shot('ver_cadf_cd01_full.png',full=True)
    s.go('CD-01det.dc.html')
    print('ERR', s.errs()); print('HEAD', s.head()); print('OVF', s.overflow())
    for i in range(3): print('T',i, json.dumps(s.rows(i),ensure_ascii=False))
    print('H', s.js("document.documentElement.scrollHeight"))
    print('BODY', s.body()[:3000])
    s.shot('ver_cadf_det_full.png',full=True)
finally: s.close()
