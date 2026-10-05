# -*- coding: utf-8 -*-
"""Frente E1 (CTL-1) · trava legal única na liberação e no ajuste da O.S. (cenUsoLegal = a regra do AG-01, RN-016 · RF-EXT-002 · ENG-011).
Monta cenario.js + mip.js (dados_mip) + núcleo da O.S. e roda legal_unit.js no JavaScriptCore do macOS ou no node (Linux), sem navegador.
Uso: python3 legal_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
import cenario, dados_mip
from areas.processo_os import JS_NUCLEO
g2 = [l for l in open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8') if l.startswith('function g2num')][0]
SHIM = ("if(typeof console==='undefined'){ globalThis.console={log:(...a)=>print(...a)}; }\n"
        "const __LS={};globalThis.localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v)},removeItem:k=>{delete __LS[k]}};\n"
        "var window={addEventListener(){}}; var location={hash:''};\n")
src = (PRELUDIO + SHIM + g2 + cenario.js_prefixo() + dados_mip.js_prefixo() + "const OSD={ords:[],nova:{emb:{}}};\n" + JS_NUCLEO
       + "\nconst MODO='legal';\n" + open(os.path.join(HERE, 'legal_unit.js'), encoding='utf-8').read())
f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(src); f.close()
try:
    r = subprocess.run(MOTOR + [f.name], capture_output=True, text=True, timeout=180)
finally:
    os.unlink(f.name)
print(r.stdout.strip()); print(r.stderr.strip()[-2000:]) if r.stderr.strip() else None
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA ')) ); fa = sum(1 for l in lin if l.startswith('FALHA '))
print(f'RESULTADO {n - fa}/{n}' + ('' if r.returncode == 0 else ' · motor JS terminou com erro'))
sys.exit(0 if r.returncode == 0 and n and not fa else 1)
