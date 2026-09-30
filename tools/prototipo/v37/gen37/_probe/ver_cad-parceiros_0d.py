# -*- coding: utf-8 -*-
"""Exploração: o erro "reading 'g2toast'" aparece em qualquer aviso (motor) ou só no CD-05? (sem verificações)"""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T()
def E(n): e=t.errs(); print(n, '→', (e[:200] if e else 'sem erro')); t.J("window.__verr=[]")
try:
    t.load(); t.abre('Fertisul'); t.setk('whats','65 99911-2234'); t.btn('Salvar'); print('toast',t.st()); E('CD-05 salvar normal')
    t.fil('Clientes'); E('filtro'); time.sleep(.2)
    t.c.goto(t.url.replace('CD-05','CD-06'),wait=1.2); t.J("window.__verr=[]")
    t.J("(()=>{const r=document.querySelectorAll('.g2ed')[0]; (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.4)
    ids=t.J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([disabled])')].map(i=>i.id)"); print(ids[:3])
    t.J(f"({L.SETV})('#{ids[0]}',document.getElementById('{ids[0]}').value+' x')"); time.sleep(.2); t.btn('Salvar'); print('toast',t.st()); E('CD-06 salvar normal')
    print(t.J("typeof DCLogic!=='undefined' ? String(DCLogic.prototype.setState||'').slice(0,600) : 'sem DCLogic'"))
finally: t.close()
