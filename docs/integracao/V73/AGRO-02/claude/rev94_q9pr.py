# -*- coding: utf-8 -*-
"""rev94 · verificação 9 do quantidade_test.py DO PR, isolada (o arquivo inteiro aborta antes, por irrigação, já na base: O1).
Uso: python3 -B rev94_q9pr.py <gen37 do produto> <quantidade_test.py de onde vem a verificação>. Dados sintéticos.
Extrai o laço JS (de "const R={mip" até "// emissão pelo MIP") e a condição do chk 9, e roda com o JS real do produto."""
import os, sys, json, re, subprocess, tempfile
G = os.path.abspath(sys.argv[1]); QT = open(os.path.abspath(sys.argv[2]), encoding='utf-8').read()
os.chdir(G); sys.path.insert(0, G)
ns = {}; exec(QT[QT.index('LS = ('):QT.index('JS_FLUXO = r"""')], ns)
import cenario, dados_mip, dados_irrigacao
from areas.processo_os import JS_NUCLEO
import areas.agronomia as AG
laco = QT[QT.index('const R={mip:[],fert:[],area:[]};'):QT.index('// emissão pelo MIP')]
cond = re.search(r"chk\(f'9 .*?\n    f'.*?',\s*(.*?),\s*\[x for x in ar", QT, re.S).group(1)
PRE = 'globalThis.print=(...a)=>console.log(...a);\n'
DOM = 'globalThis.document={getElementById:()=>null,querySelector:()=>null};globalThis.setTimeout=()=>0;\n'
f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8')
f.write(PRE + ns['LS'] + DOM + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO + dados_mip.js_prefixo() + dados_irrigacao.js_prefixo() + AG.JS_AG01 + laco + '\nprint(JSON.stringify(R.area));\n'); f.close()
p = subprocess.run(['node', f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
if p.returncode: print(p.stderr[-1500:]); sys.exit(2)
ar = json.loads(p.stdout.strip().splitlines()[-1]); na = sum(1 for x in ar if x['antes'])
ok = eval(cond, {'ar': ar, 'na': na, 'len': len, 'all': all, 'any': any})
print('condição do chk 9:', cond)
print(('OK    ' if ok else 'FALHOU ') + f'9 do quantidade_test: {len(ar)} vistorias; abre vazio em {sum(1 for x in ar if x.get("vazio"))}; {na} travariam com 1 casa; travas de área no formulário: {sum(1 for x in ar if x["trava"])}')
sys.exit(0 if ok else 1)
