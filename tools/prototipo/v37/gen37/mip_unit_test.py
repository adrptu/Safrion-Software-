# -*- coding: utf-8 -*-
"""Teste unitário do núcleo MIP (mip.js + dados_mip.py) no JavaScriptCore do macOS ou no node (Linux), sem navegador. Uso: python3 mip_unit_test.py"""
import os, sys, subprocess, tempfile
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import dados_mip, cenario
JSC='/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'
dados_mip.verificar(); print('OK   dados_mip.verificar (datas, pontos × protocolo, médias citadas)')
# SINT-T01: jsc no macOS; fora dele (Linux/nuvem) o node, com print → console.log; o mesmo JS nos dois
MOTOR,PRELUDIO=([JSC],'') if os.path.exists(JSC) else (['node'],'globalThis.print=(...a)=>console.log(...a);\n')
import dados_lagoa_fonte as _F
a22=dados_mip.TAL['PV22']['area']; ok22=a22==_F.PIVOS_HA[22]
print(('OK   ' if ok22 else 'FALHA ')+'área do Pivô 22 no MIP = fonte única (dados_lagoa_fonte)')
src=PRELUDIO+cenario.js_prefixo()+dados_mip.js_prefixo()+open(os.path.join(HERE,'mip_test.js'),encoding='utf-8').read()
f=tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8'); f.write(src); f.close()
r=subprocess.run(MOTOR+[f.name],capture_output=True,text=True,timeout=60); os.unlink(f.name)
print(r.stdout.strip()); print(r.stderr.strip()) if r.stderr.strip() else None
sys.exit(0 if ok22 and r.returncode==0 and 'FALHA' not in r.stdout and 'RESULTADO' in r.stdout else 1)
