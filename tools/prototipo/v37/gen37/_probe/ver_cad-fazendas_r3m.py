# -*- coding: utf-8 -*-
"""Verificador r3m · CD-01: filtro "Sem polígono" na árvore; B1 (Boa Vista) aceita o setor "Gotejo T7" da Santa Rita? CD-01det: "Reativar B1"."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
def fresh(u): s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    s.js("(()=>{const t=document.querySelectorAll('[role=table]')[1]; const h=[...t.querySelectorAll('[role=columnheader]')].find(x=>x.innerText.indexOf('POLÍGONO')>=0); [...h.querySelectorAll('button')].find(b=>b.innerText.trim()==='▾').click();})()"); time.sleep(.4)
    P('chk', s.js("(()=>{const l=[...document.querySelectorAll('label')].find(l=>l.innerText.indexOf('Sem polígono')>=0); if(!l) return 'sem'; l.click(); return 'ok';})()")); time.sleep(.4)
    P('rows filtradas', s.rows(1))
    s.click('Limpar'); s.click('Fechar'); time.sleep(.2)
    s.openrow(1,'B1 Sequeiro'); s.fset('sis','Gotejo'); P('setor opts', s.fopts('setor')); s.fset('setor','Gotejo T7'); s.btn('Salvar'); time.sleep(.3)
    P('B1 gotejo T7', 'aberto' if s.aberto() else 'salvo', s.alerts() or s.toast()); P('B1', s.rowtxt(1,'B1 ')); P('T7', s.rowtxt(1,'T7 '))
    # detalhe: B1 inativo → Reativar B1
    s.openrow(1,'B1 '); s.fset('sit','Inativo'); s.btn('Salvar'); time.sleep(.3)
    fresh('CD-01det.dc.html#talhao=B1'); P('HEAD', s.head()[-110:])
    P('reativar', s.click('Reativar B1','header')); time.sleep(.3); P('ASIDE', s.aside()[:80], 'sit', s.fv('sit'), 'focus', s.js("document.activeElement&&document.activeElement.id"))
    s.btn('Salvar'); time.sleep(.3); P('toast', s.toast(), s.alerts()); P('HEAD', s.head()[-110:]); P('rows0', s.rows(0))
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
