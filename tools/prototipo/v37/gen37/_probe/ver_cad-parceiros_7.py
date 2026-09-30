# -*- coding: utf-8 -*-
"""Verificador CD-05 · cada parceiro dos dados: abrir e cancelar sem mudar fecha direto; abrir e salvar sem mudar passa nas regras do próprio formulário."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T()
try:
    t.load(); nomes=t.J(f"{t.ROWS}.map(r=>r.querySelector('[role=cell] b, [role=cell] strong, [role=cell] span').innerText.trim())")
    print(nomes)
    ruins=[]; falha=[]
    for n in nomes:
        t.abre(n); t.btn('Cancelar')
        if t.aberto(): ruins.append(n); t.btn('Descartar alterações')
    t.chk('1 abrir e cancelar sem mudar fecha sem confirmação (todos)', not ruins, ruins)
    for n in nomes:
        t.abre(n); t.btn('Salvar'); time.sleep(.1)
        if t.aberto(): falha.append((n,t.al())); t.btn('Cancelar'); t.btn('Descartar alterações')
    t.chk('2 salvar sem mudar passa nas regras (dados de exemplo coerentes com o formulário)', not falha, falha)
finally: t.close()
