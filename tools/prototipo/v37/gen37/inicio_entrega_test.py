# -*- coding: utf-8 -*-
"""CTL-2 · Frente B · início com entrega parcial: uma regra (cenIniFalta, cenario.js) na web (osIniErro/osc_iniciar) e no app (cenIniciarTurno,
mbPasso). Sem navegador: monta o JS real da O.S. e do app e roda no node (inicio_entrega_unit.js). Uso (de gen37/): python3 inicio_entrega_test.py"""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cenario
from areas.processo_os import JS_NUCLEO
from areas import mobile
PR = os.path.join(HERE, '_probe'); os.makedirs(PR, exist_ok=True)
PRE = 'globalThis.document={getElementById:()=>null,querySelector:()=>null};globalThis.window={addEventListener:()=>{}};\n'
open(os.path.join(PR, 'ini_web.js'), 'w', encoding='utf-8').write(PRE + cenario.perfis_js() + cenario.js_prefixo() + 'const OSD={nova:{emb:{}}};const RC_OS=[];\n' + JS_NUCLEO)   # CTL-3: perfis (cenExige)
open(os.path.join(PR, 'ini_app.js'), 'w', encoding='utf-8').write(PRE + cenario.perfis_js() + cenario.js_prefixo() + mobile.JS_BASE + mobile.MBAPP_JS)   # o app também carrega o g2lib (cenConcQuem)
r = subprocess.run(['node', os.path.join(HERE, 'inicio_entrega_unit.js'), PR], capture_output=True, text=True, timeout=60)
out = r.stdout.strip().splitlines(); res = json.loads(out[-1]) if r.returncode == 0 and out else []
for x in res: print(('OK    ' if x['ok'] else 'FALHA ') + x['n'] + ('' if x['ok'] else ' · ' + x['info']))
if r.returncode: print('FALHA motor JS:', r.stderr[:600])
n = sum(x['ok'] for x in res); print(f'{n}/{len(res)}'); sys.exit(0 if res and n == len(res) else 1)
