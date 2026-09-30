# -*- coding: utf-8 -*-
"""Verificador r3k · CD-01det B1 (polígono v1) → CD-01 reflete; talhão novo na lista → detalhe; inativar no detalhe → lista."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
PG="(document.querySelectorAll('aside[role=dialog]')[0]||{innerText:''}).innerText.replace(/\\n/g,' | ')"
def pbtn(t): r=s.js("((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return 'ok';} return 'SEM '+t;})("+json.dumps(t)+")"); time.sleep(.35); return r
def fresh(u): s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01det.dc.html'); s.clear_ls(); fresh('CD-01det.dc.html#talhao=B1')
    P('HEAD', s.head()[:50], '...', s.head()[-110:]); P('main', s.js("document.querySelector('main').innerText").replace('\n',' | ')[:900])
    P('prim', s.click('Definir polígono do B1','header')); pbtn('Gerar prévia'); P('PG', s.js(PG)[:500]); pbtn('Salvar polígono'); time.sleep(.3)
    P('toast', s.toast()); P('HEAD', s.head()[-110:]); P('rows0', s.rows(0))
    fresh('CD-01.dc.html'); P('CD01 HEAD', s.head()[:160]); P('B1', s.rowtxt(1,'B1 ')); P('BV g', s.rowtxt(1,'Boa Vista'))
    s.click('Cadastrar talhão','header'); s.fset('t','N1'); s.fset('faz','Boa Vista'); s.fset('decl','100'); s.btn('Salvar'); time.sleep(.3); P('toast', s.toast()); P('N1', s.rowtxt(1,'N1 '))
    href=s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[1].querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('N1')===0||r.innerText.indexOf('N1\\n')>=0); return r?r.querySelector('a').getAttribute('href'):null;})()"); P('href', href)
    fresh(href); P('N1 HEAD', s.head()[:60], '...', s.head()[-120:]); P('N1 main', s.js("document.querySelector('main').innerText").replace('\n',' | ')[:900])
    P('open', s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')][1]; (r.querySelector('[role=cell] span')||r).click(); return 'ok';})()")); time.sleep(.4)
    s.fset('sit','Inativo'); s.btn('Salvar'); time.sleep(.3); P('toast', s.toast(), s.alerts()); P('N1 HEAD', s.head()[-120:]); P('main btns', s.js("[...document.querySelectorAll('main button, main a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/\\s+/g,' ').trim()).filter(t=>!/⇅|▾|▸/.test(t))"))
    s.shot('ver_cad-fazendas_r3k_N1inativo.png')
    fresh('CD-01.dc.html'); P('N1 lista', s.rowtxt(1,'N1 ')); P('BV g', s.rowtxt(1,'Boa Vista')); P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
