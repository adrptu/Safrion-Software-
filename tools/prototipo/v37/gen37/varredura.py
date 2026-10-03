# -*- coding: utf-8 -*-
"""Varredura das páginas de _render no Chrome headless: erro de execução (window.onerror, console.error) e aviso de erro do runtime
na tela. O build não valida JavaScript; isto valida. Uso: python3 varredura.py [filtro]"""
import sys, os, glob, time, json
from cadc_lib import T
HERE=os.path.dirname(os.path.abspath(__file__))
pags=sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE,'_render','*.dc.html')))
if len(sys.argv)>1: pags=[p for p in pags if sys.argv[1] in p]
t=T(); falhas=[]
try:
    for p in pags:
        t.goto(p); time.sleep(.4)
        e=t.errs(); txt=t.J("(document.body&&document.body.innerText||'').slice(0,400)") or ''
        ban=t.J("(()=>{const b=[...document.querySelectorAll('body *')].find(x=>/^[A-Z][A-Za-z0-9-]*: (Unexpected|.*is not defined|Cannot read|.*is not a function|Invalid)/.test((x.innerText||'').trim())&&x.children.length===0); return b?b.innerText.trim().slice(0,200):'';})()") or ''
        vazio=len(txt.strip())<20
        if e or ban or vazio: falhas.append((p,(ban or '')+(' | '+e if e else '')+(' | página vazia' if vazio else ''))); print('FALHA',p,falhas[-1][1][:300],flush=True)
    print(f'RESULTADO: {len(pags)-len(falhas)}/{len(pags)} páginas sem erro')
finally:
    t.c.close() if hasattr(t.c,'close') else None; t.srv.terminate()
sys.exit(1 if falhas else 0)   # página com erro não sai com 0 (portabilidade/CI)
