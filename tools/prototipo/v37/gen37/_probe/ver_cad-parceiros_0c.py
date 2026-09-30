# -*- coding: utf-8 -*-
"""Exploração: em que passo aparece o erro "reading 'g2toast'" (sem verificações)."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T()
def E(n): e=t.errs(); print(n, '→', (e[:300] if e else 'sem erro')); t.J("window.__verr=[]")
try:
    t.load(); E('load')
    t.novo(); E('novo')
    t.can('Transportador'); E('marca Transportador')
    t.setk('cnpj','66.890.123/0001-60'); E('digita CNPJ dup')
    t.btn('Abrir e ativar papel'); E('abrir e ativar')
    print('toast', t.st())
    t.btn('Cancelar'); E('cancelar')
    t.btn('Descartar alterações'); E('descartar')
    t.novo(); E('novo2'); t.setk('cnpj','66.890.123/0001-60'); t.btn('Abrir e ativar papel'); E('abrir sem papel'); print('toast', t.st())
    t.btn('Cancelar'); E('cancelar2')
    print('stack', t.J("(()=>{try{ return String(window.__lastStack||'') }catch(e){return ''}})()"))
finally: t.close()
