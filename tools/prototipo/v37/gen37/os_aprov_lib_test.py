# -*- coding: utf-8 -*-
"""Frente F (CTL-1) · executor do os_aprov_lib_unit.js: liberar a O.S. agrícola grava a aprovação (CMD-42) e a liberação (CMD-06).
Monta o JS real (cenario.js + JS_NUCLEO da O.S. com carência + OSD do gerador) e roda no jsc (macOS) ou no node (Linux/nuvem),
como o carencia_test.py. Sem navegador. Uso: python3 os_aprov_lib_test.py   (sai 1 se alguma verificação falhar)."""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')

import cenario
import areas.processo_os as P
osd = dict(ords=P._ordens(), nova=P._nova_ordem_dados())
src = (PRELUDIO + cenario.js_prefixo() + 'const OSD = ' + json.dumps(osd, ensure_ascii=False) + ';\n' + P.JS_NUCLEO + '\n'
       + open(os.path.join(HERE, 'os_aprov_lib_unit.js'), encoding='utf-8').read())
fd, p = tempfile.mkstemp(prefix='os_aprov_lib_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try:
    r = subprocess.run(MOTOR + [p], capture_output=True, text=True, timeout=120)
finally:
    os.unlink(p)
print(r.stdout, end='')
linhas = r.stdout.strip().splitlines()
fal = [l for l in linhas if l.startswith('FALHA')]
tot = [l for l in linhas if l.startswith('TOTAL ')]
if r.returncode or not tot:
    print('FALHA motor JS não terminou:', r.stderr[-1500:]); sys.exit(1)
print('RESULTADO', 'falhou' if fal else 'passou', '·', tot[-1])
sys.exit(1 if fal else 0)
