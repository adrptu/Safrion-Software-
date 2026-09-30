# -*- coding: utf-8 -*-
"""Verificador CD-05 · motivo antigo depois de reativar (passos exatos) e seções Cliente/Crédito (visual)."""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T(); SH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_')
MV="(document.getElementById('fx_g_forn_motivo')||{value:null}).value"
try:
    t.load()
    # motivo depois de reativar
    t.abre('Casa do Adubo'); t.btn('Suspender parceiro'); t.setk('motivo','Entrega fora do prazo'); t.btn('Salvar'); time.sleep(.2)
    t.abre('Casa do Adubo'); t.btn('Reativar parceiro'); t.btn('Salvar'); time.sleep(.2); ln=t.lin('Casa do Adubo')
    t.abre('Casa do Adubo'); t.btn('Suspender parceiro'); mv=t.J(MV); t.btn('Salvar'); time.sleep(.2); st=t.st(); ab=t.aberto(); ln2=t.lin('Casa do Adubo')
    t.chk('1 depois de reativar, nova suspensão começa sem motivo e exige motivo', mv=='' and ab, (ln,mv,ab,st[:120],ln2))
    # visual das seções Cliente e Parceiro de crédito
    t.novo(); t.setk('cnpj','12.121.212/0001-12'); t.can('Cliente'); t.can('Parceiro de crédito')
    t.J("(()=>{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label[for]')].find(l=>l.innerText.trim()==='Produtos de interesse'); a.scrollTop=l.getBoundingClientRect().top+a.scrollTop-80;})()"); time.sleep(.3)
    t.c.shot(SH+'secoes.png')
    u=t.J("(()=>{const i=document.getElementById('fx_g_forn_lim'); return i.parentElement.innerText.replace(/\\s+/g,' ');})()")
    print('unidade do limite:', repr(u))
    t.btn('Cancelar'); t.btn('Descartar alterações')
finally: t.close()
