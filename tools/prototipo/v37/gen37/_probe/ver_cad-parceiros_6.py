# -*- coding: utf-8 -*-
"""Verificador CD-05 · filtro de coluna em Todos e troca para Fornecedores (colunas diferentes)."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T(); SH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_')
TOP="document.querySelectorAll('[role=table]')[0].parentElement.parentElement.innerText.split('PARCEIRO')[0].replace(/\\s+/g,' ').trim()"
try:
    t.load()
    t.J("document.querySelector('[aria-label=\"Filtrar Papéis\"]').click()"); time.sleep(.3)
    t.J("[...document.querySelectorAll('[data-root] label')].find(l=>l.innerText.trim().startsWith('Cliente')).querySelector('input').click()"); time.sleep(.3)
    t.J("[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Fechar').click()"); time.sleep(.2)
    a=t.J(TOP); na=len(t.rows())
    t.fil('Fornecedores'); b=t.J(TOP); nb=len(t.rows()); t.c.shot(SH+'chip_forn.png')
    print('Todos com filtro Papéis=Cliente:', a, na); print('Fornecedores:', b, nb)
    t.chk('1 ao trocar para Fornecedores, o chip de filtro não mostra chave técnica nem filtro inativo', 'papeis:' not in b and not ('Cliente' in b and nb==7), (b,nb))
finally: t.close()
