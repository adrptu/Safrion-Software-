# -*- coding: utf-8 -*-
"""Verificador r3i · CD-01det: #talhao=T2/ZZ em carga nova, seletor (troca e hash), parcela em consulta com origem, linha do talhão abre formulário."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
def fresh(u): s.c.goto('about:blank',wait=0.2) if False else s.c.call('Page.navigate',{'url':'about:blank'}); time.sleep(.3); s.go(u)
try:
    s.go('CD-01det.dc.html'); s.clear_ls()
    fresh('CD-01det.dc.html#talhao=T2'); P('T2 HEAD', s.head()[:60], '...', s.head()[-120:]); P('T2 sel', s.js("document.querySelector('header select').value")); P('T2 rows1', s.rows(1)); P('geo', s.js("document.querySelector('main').innerText").replace('\n',' | ')[-500:])
    fresh('CD-01det.dc.html#talhao=ZZ'); P('ZZ HEAD', s.head()); P('ZZ sel', s.js("(()=>{const x=document.querySelector('header select'); return [x.value,x.selectedIndex,x.options[x.selectedIndex]&&x.options[x.selectedIndex].text];})()"))
    P('ZZ main', s.js("document.querySelector('main').innerText").replace('\n',' | ')[:300]); P('ZZ ERRS', s.errs())
    s.shot('ver_cad-fazendas_r3i_ZZ.png')
    # seletor → P1
    s.js("(()=>{const x=document.querySelector('header select'); const P=HTMLSelectElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(x,'P1'); x.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.4)
    P('P1 HEAD', s.head()[:60], '...', s.head()[-110:]); P('hash', s.js("location.hash")); P('P1 rows0', s.rows(0)); P('P1 rows1', s.rows(1))
    # linha do talhão abre formulário
    P('open', s.js("(()=>{const r=[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')][1]; (r.querySelector('[role=cell] span')||r).click(); return 'ok';})()")); time.sleep(.4)
    P('ASIDE', s.aside()[:300]); P('LABELS', s.labels(), 'faz opts', s.fopts('faz'))
    s.btn('Cancelar'); time.sleep(.2)
    # parcela em consulta
    P('open parc', s.openrow(1,'P1 talhão inteiro')); P('ASIDE parc', s.aside()[:500]); P('inputs editáveis', s.js("[...document.querySelectorAll('aside[role=dialog] input, aside[role=dialog] select, aside[role=dialog] textarea')].filter(i=>!i.disabled&&!i.readOnly).length"))
    P('links', s.js("[...document.querySelectorAll('aside[role=dialog] a')].map(a=>a.innerText+' ->'+a.getAttribute('href'))"), 'btns', s.js("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim())"))
    s.shot('ver_cad-fazendas_r3i_parc.png')
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
