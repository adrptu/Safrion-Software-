# -*- coding: utf-8 -*-
"""Verificador r3j · CD-01det · painel "Definir polígono da T1-B": sem prévia, importar, aviso de não salvo, salvar, versões, primária."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
t0=time.time()
def P(*a): print(f'[{time.time()-t0:4.1f}s]',*a, flush=True)
PG="(document.querySelectorAll('aside[role=dialog]')[0]||{innerText:''}).innerText.replace(/\\n/g,' | ')"
def pbtn(t): r=s.js("((t)=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()===t); if(b){b.click(); return 'ok';} return 'SEM '+t;})("+json.dumps(t)+")"); time.sleep(.35); return r
try:
    s.go('CD-01det.dc.html'); s.clear_ls(); s.go('CD-01det.dc.html')
    P('prim', s.click('Definir polígono da T1-B','header')); P('PG', s.js(PG)[:600])
    s.shot('ver_cad-fazendas_r3j_painel.png')
    P('salvar sem prévia', pbtn('Salvar polígono'), s.js(PG)[-200:])
    P('gerar', pbtn('Gerar prévia')); P('PG prev', s.js(PG)[:900])
    P('fechar ×', s.js("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.getAttribute('aria-label')==='Fechar'); b.click(); return 'ok';})()")); time.sleep(.3); P('PG warn', s.js(PG)[-260:])
    P('continuar', pbtn('Continuar editando'), 'aberto', s.aberto())
    P('esc', s.js("(()=>{const a=document.querySelector('aside[role=dialog]'); a.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true})); return 'ok';})()")); time.sleep(.3); P('após Esc', s.js(PG)[-160:])
    P('continuar', pbtn('Continuar editando'))
    P('salvar', pbtn('Salvar polígono')); time.sleep(.3); P('toast', s.toast()); P('aberto', s.aberto())
    P('HEAD', s.head()[-140:]); P('rows1', s.rows(1)); P('main', s.js("document.querySelector('main').innerText").replace('\n',' | ')[-700:])
    P('main btns', s.js("[...document.querySelectorAll('main button, main a')].filter(e=>e.getClientRects().length).map(e=>e.innerText.replace(/\\s+/g,' ').trim()).filter(t=>!/⇅|▾|▸/.test(t))"))
    # nova versão pelo desenho (T1): −2,6 % pede motivo
    P('nova', s.click('Nova versão do polígono','main')); P('PG', s.js(PG)[:200])
    P('des', pbtn('Desenhar no mapa')); P('gerar', pbtn('Gerar prévia')); P('PG', s.js(PG)[:900])
    P('salvar', pbtn('Salvar polígono')); P('err', s.js(PG)[-300:])
    s.js("(()=>{const x=document.getElementById('pg_mot'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(x,'Carreador ou estrada'); x.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.3)
    P('salvar', pbtn('Salvar polígono')); time.sleep(.3); P('toast', s.toast()); P('rows0', s.rows(0)); P('main', s.js("document.querySelector('main').innerText").replace('\n',' | ')[-600:]); P('HEAD', s.head()[-120:])
    s.shot('ver_cad-fazendas_r3j_fim.png')
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
