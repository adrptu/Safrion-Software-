# -*- coding: utf-8 -*-
"""SUP-1 · O.S. × Estoque: executor do sup_os_unit.js (bloqueio do encerramento por consumo em conferência e atalhos #req= da O.S.), sem navegador.
Monta no node o g2lib.js inteiro (perfis) + cenário + núcleo da O.S. com as ordens do gerador. Uso (de gen37/): python3 sup_os_test.py"""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import cenario
import areas.processo_os as P
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
      "var window={addEventListener(){}}; var document={getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[],addEventListener(){}}; var requestAnimationFrame=()=>0; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
G2 = open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read()
OS = 'const OSD = ' + json.dumps(dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={}), ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO
src = LS + G2 + '\n' + cenario.js_prefixo() + '\n' + OS + '\n' + open(os.path.join(HERE, 'sup_os_unit.js'), encoding='utf-8').read()
fd, p = tempfile.mkstemp(prefix='supos_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
finally: os.unlink(p)
print(r.stdout, end='')
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
if r.returncode and not fa: print('FALHA motor JS:', r.stderr[-2000:])
print(f'RESULTADO {n - fa}/{n}'); sys.exit(0 if n and not fa and r.returncode == 0 else 1)
