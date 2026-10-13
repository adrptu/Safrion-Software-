# -*- coding: utf-8 -*-
"""SUP · Suprimentos simplificado: executor do sup_unit.js, sem navegador (docs/suprimentos-simplificado §9.2).
Monta o JS real no node: g2lib.js inteiro (perfis de demonstração, CTL-3) + cenário (cenario.js_prefixo) + dados da tela do Estoque
(processo_estoque._dados_js, o E2) + regras da tela (est.js) + sup_unit.js.
Uso (de gen37/): python3 sup_unit_test.py      (sai 1 se algum caso falhar)
Reprodução em outra cópia do gerador: GEN=<gen37 da base> python3 sup_unit_test.py"""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.environ.get('GEN', HERE)
sys.path.insert(0, G); os.chdir(G)
import cenario
from areas import processo_estoque as PE
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
      "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
G2 = open(os.path.join(G, 'g2lib.js'), encoding='utf-8').read()
EST = cenario.js_prefixo() + 'const E2 = ' + json.dumps(PE._dados_js(), ensure_ascii=False) + ';\n' + open(os.path.join(G, 'est.js'), encoding='utf-8').read()
src = 'globalThis.print=(...a)=>console.log(...a);\n' + LS + G2 + '\n' + EST + '\n' + open(os.path.join(HERE, 'sup_unit.js'), encoding='utf-8').read()
fd, p = tempfile.mkstemp(prefix='sup_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
finally: os.unlink(p)
print(r.stdout, end='')
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
if r.returncode and not fa: print('FALHA motor JS:', r.stderr[-2000:])
print(f'RESULTADO {n - fa}/{n}' + ('' if r.returncode == 0 or fa else ' · motor JS terminou com erro'))
sys.exit(0 if n and not fa and r.returncode == 0 else 1)
