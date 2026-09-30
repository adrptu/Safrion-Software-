# -*- coding: utf-8 -*-
"""Verificador r3l · CD-01: "Cadastrar fazenda…" salvando (volta ao talhão), filtro da árvore, renomear e o que muda no mapa e no detalhe."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
def fresh(u): s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.click('Cadastrar talhão','header'); s.fset('t','X9'); s.fset('sis','Gotejo'); s.fset('decl','50'); s.fset('faz','Cadastrar fazenda…')
    s.fset('nome','Serra Azul'); s.fset('mun','Jataí'); s.fset('area','100'); s.btn('Salvar'); time.sleep(.3)
    P('volta', s.aside()[:60], '| t', s.fv('t'), 'sis', s.fv('sis'), 'decl', s.fv('decl'), 'faz', s.fv('faz'), 'LABELS', s.labels()); P('toast', s.toast())
    s.fset('setor','Gotejo T7'); s.btn('Salvar'); time.sleep(.3); P('X9', s.aberto(), s.toast(), s.alerts()); P('SA g', s.rowtxt(1,'Serra Azul')); P('X9 row', s.rowtxt(1,'X9 '))
    # filtro da árvore: coluna Polígono
    P('filtro', s.js("(()=>{const t=document.querySelectorAll('[role=table]')[1]; const hs=[...t.querySelectorAll('[role=columnheader]')]; const h=hs.find(x=>x.innerText.indexOf('POLÍGONO')>=0); const b=[...h.querySelectorAll('button')].find(b=>b.innerText.trim()==='▾'); b.click(); return 'ok';})()")); time.sleep(.4)
    P('menu', s.js("(()=>{const m=[...document.querySelectorAll('[role=menu],[role=dialog],[role=listbox]')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/\\s+/g,' ').slice(0,300)); return m;})()"))
    s.shot('ver_cad-fazendas_r3l_filtro.png')
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
