# -*- coding: utf-8 -*-
"""Teste unitário do núcleo MIP (mip.js + dados_mip.py) no JavaScriptCore do macOS, sem navegador. Uso: python3 mip_unit_test.py"""
import os, sys, subprocess, tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import dados_mip, cenario
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
dados_mip.verificar(); print('OK   dados_mip.verificar (datas, pontos × protocolo, médias citadas)')
src=cenario.js_prefixo()+dados_mip.js_prefixo()+open(os.path.join(HERE,'mip_test.js'),encoding='utf-8').read()
f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8'); f.write(src); f.close()
r=subprocess.run([JSC,f.name],capture_output=True,text=True,timeout=60); os.unlink(f.name)
print(r.stdout.strip()); print(r.stderr.strip()) if r.stderr.strip() else None
sys.exit(0 if 'FALHA' not in r.stdout and 'RESULTADO' in r.stdout else 1)
