# -*- coding: utf-8 -*-
"""Exploração: o erro do aviso (componentDidUpdate sem estado anterior) acontece também em telas de outras frentes? (sem verificações)"""
import importlib.util, os, time
s=importlib.util.spec_from_file_location('vl',os.path.join(os.path.dirname(os.path.abspath(__file__)),'ver_cad-parceiros_lib.py')); L=importlib.util.module_from_spec(s); s.loader.exec_module(L)
t=L.T('CD-01.dc.html')
try:
    t.load(); print('load', t.errs())
    t.J("(()=>{const r=document.querySelectorAll('.g2ed')[0]; (r.querySelector('[role=cell] span')||r).click();})()"); time.sleep(.4)
    ids=t.J("[...document.querySelectorAll('aside[role=dialog] input:not([readonly]):not([disabled])')].map(i=>i.id)"); print(ids[:3])
    if ids: t.J(f"({L.SETV})('#{ids[0]}',document.getElementById('{ids[0]}').value+' x')"); time.sleep(.2); t.btn('Salvar')
    print('toast',t.st()); print('errs', t.errs()[:300])
    time.sleep(5); print('toast após 5 s:', t.st()[:120])
finally: t.close()
