# -*- coding: utf-8 -*-
"""Varredura das páginas de _render no Chrome headless: erro de execução (window.onerror, console.error) e aviso de erro do runtime
na tela. O build não valida JavaScript; isto valida. Uso: python3 varredura.py [filtro]"""
import sys, os, glob, time, json
from cadc_lib import T
HERE=os.path.dirname(os.path.abspath(__file__))
pags=sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE,'_render','*.dc.html')))
if len(sys.argv)>1: pags=[p for p in pags if sys.argv[1] in p]
t=T(); falhas=[]
# VISOES-1 §2.4 (estática): nas telas com seletor de visões (data-visoes), nenhuma escrita de URL com location.pathname sem location.search
# (apagaria o ?view); a regra é a de visoes.escritas_sem_query (replaceState, pushState, location.replace/assign, location.href=)
import visoes as _V
for p in pags:
    s=open(os.path.join(HERE,'_render',p),encoding='utf-8').read()
    r=_V.escritas_sem_query(s) if 'data-visoes=' in s else []
    if r: falhas.append((p,'escrita de URL sem location.search numa tela com seletor de visões: '+r[0])); print('FALHA',p,falhas[-1][1],flush=True)
try:
    for p in pags:
        t.goto(p); time.sleep(.4)
        # Sob carga a página pode demorar a montar: espera haver texto (até 8 s) antes de julgar "página vazia".
        txt=''; t0=time.time()
        while True:
            txt=t.J("(document.body&&document.body.innerText||'').slice(0,400)") or ''
            if len(txt.strip())>=20 or time.time()-t0>8: break
            time.sleep(.25)
        e=t.errs()
        ban=t.J("(()=>{const b=[...document.querySelectorAll('body *')].find(x=>/^[A-Z][A-Za-z0-9-]*: (Unexpected|.*is not defined|Cannot read|.*is not a function|Invalid)/.test((x.innerText||'').trim())&&x.children.length===0); return b?b.innerText.trim().slice(0,200):'';})()") or ''
        vazio=len(txt.strip())<20
        if e or ban or vazio: falhas.append((p,(ban or '')+(' | '+e if e else '')+(' | página vazia' if vazio else ''))); print('FALHA',p,falhas[-1][1][:300],flush=True)
    print(f'RESULTADO: {len(pags)-len(falhas)}/{len(pags)} páginas sem erro')
finally:
    t.c.close() if hasattr(t.c,'close') else None; t.srv.terminate()
sys.exit(1 if falhas else 0)   # página com erro não sai com 0 (portabilidade/CI)
