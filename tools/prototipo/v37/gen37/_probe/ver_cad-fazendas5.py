# -*- coding: utf-8 -*-
"""Verificador 5 · o console.error 'reading g2toast' é da frente ou do motor? Compara CD-01 com outra tela G2 (só leitura) e mede se o aviso some."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
def g2save_first(tela):
    s.go(tela); e0=len(s.errs())
    s.js("(()=>{const r=document.querySelectorAll('.g2ed')[0]; const x=r.querySelector('[role=cell] span')||r.querySelector('[role=cell]'); x.click();})()"); time.sleep(.4)
    s.btn('Salvar'); time.sleep(.4)
    t1=s.toast(); e1=s.errs()[e0:]
    for _ in range(12): time.sleep(.5)
    t2=s.toast(); s.click('Expandir tudo'); e2=s.errs()[e0:]
    print(tela, '| aviso logo após salvar:', t1[:80], '| após 6 s:', t2[:80], '| erros:', len(e1), len(e2), (e2[:1] if e2 else ''), flush=True)
try:
    for t in sys.argv[1:] or ['CD-01.dc.html','CD-04.dc.html','CD-06.dc.html']:
        g2save_first(t)
finally: s.close()
