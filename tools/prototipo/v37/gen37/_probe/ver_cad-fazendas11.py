# -*- coding: utf-8 -*-
"""Verificador 11 · T3 mudado para a Boa Vista: como fica o detalhe."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
try:
    s.go('CD-01.dc.html'); s.openrow(1,'T3 Sequeiro'); s.fset('faz','Boa Vista'); s.btn('Salvar'); time.sleep(.3)
    print('toast', s.toast()); print('mapa T3', s.js("[...document.querySelectorAll('svg polygon')][3].getAttribute('fill')"))
    s.go('CD-01det.dc.html#talhao=T3'); print('head', s.head()[:140]); print('talhão', s.rows(0)); print('safras', s.rows(1))
finally: s.close()
