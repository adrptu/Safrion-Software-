# -*- coding: utf-8 -*-
"""EST-2: recusa de item diferente sem gravar, formulário preservado e recebimentos válidos.
Monta cenário, estoque e permissões reais, com dados sintéticos. Node no PATH.
Uso: python3 est_item_divergente_test.py; GEN aponta uma base anterior para contraprova.
"""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
G = os.environ.get('GEN', HERE)
sys.path.insert(0, G); os.chdir(G)
import cenario
import areas.processo_os as P
from areas import processo_estoque as PE
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
      "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
G2 = open(os.path.join(G, 'g2lib.js'), encoding='utf-8').read()
EST = cenario.js_prefixo() + 'const E2 = ' + json.dumps(PE._dados_js(), ensure_ascii=False) + ';\nvar GRIDS=[];\n' + PE.JS
OS = 'const OSD = ' + json.dumps(dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={}), ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO
src = ('globalThis.print=(...a)=>console.log(...a);\n' + LS + G2 + '\n' + EST + '\n' + OS + '\n'
       + open(os.path.join(HERE, 'est_item_divergente_unit.js'), encoding='utf-8').read())
fd, p = tempfile.mkstemp(prefix='a4_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
finally: os.unlink(p)
print(r.stdout, end='')
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
if r.returncode and not fa: print('FALHA motor JS:', r.stderr[-2000:])
print(f'RESULTADO {n - fa}/{n}' + ('' if r.returncode == 0 or fa else ' · motor JS terminou com erro'))
sys.exit(0 if n and not fa and r.returncode == 0 else 1)
