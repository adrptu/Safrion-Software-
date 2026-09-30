# -*- coding: utf-8 -*-
"""Exploração: menu de filtro de coluna da grade (sem verificações)."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T()
try:
    t.load()
    t.J("document.querySelector('[aria-label=\"Filtrar Situação do papel\"]').click()"); time.sleep(.4)
    print(t.J("(()=>{const d=[...document.querySelectorAll('[role=dialog],[role=menu],[role=listbox]')]; return d.map(x=>x.outerHTML.slice(0,300)+' ||| '+x.innerText.slice(0,1500));})()"))
    print(t.J("document.activeElement && document.activeElement.outerHTML.slice(0,300)"))
finally: t.close()
