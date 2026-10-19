# -*- coding: utf-8 -*-
"""CTL-3 · Frente D (aprova quem decide, R-D0..R-D5) e ATOR: executor do aprova_quem_decide_unit.js, sem navegador.
Monta o JS real no node: g2lib.js inteiro (perfis de demonstração) + cenário + JS do Estoque + núcleo da O.S. (com carência) + manutenção (MA-04).
Uso (de gen37/): python3 aprova_quem_decide_test.py      (sai 1 se algum caso falhar)
Reprodução em outra cópia do gerador: GEN=<gen37 da base> STUBS=<js com G2_PERFIS e funções g2* inertes> python3 aprova_quem_decide_test.py"""
import os, sys, re, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.environ.get('GEN', HERE)
sys.path.insert(0, G); os.chdir(G)
import cenario
import dados_manutencao as DM
import areas.processo_os as P
from areas import processo_estoque as PE
from areas import maquinas as MQ
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
      "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
G2 = open(os.path.join(G, 'g2lib.js'), encoding='utf-8').read()
STUBS = open(os.environ['STUBS'], encoding='utf-8').read() if os.environ.get('STUBS') else ''
# Estoque: cenário + dados da tela + JS da tela (est*, PREVALS, EXTRAVALS)
EST = cenario.js_prefixo() + 'const E2 = ' + json.dumps(PE._dados_js(), ensure_ascii=False) + ';\nvar GRIDS=[];\n' + PE.JS
# O.S.: o núcleo (osc_*) que a tela e o Mapa usam, com os dados das ordens do gerador
OS = 'const OSD = ' + json.dumps(dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={}), ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO
# Manutenção: regras sobre o cenário único (c.man, desde o 1a do PCM simplificado) + JS da tela MA; a ação em massa "Marcar pendentes como feitas" (pan_todas), se existir
MAN = DM.js_regras()
_m = re.search(r"v\.pan_todas=\(\)=>manMudar\(self,c2=>\{(.*?)\}\);\n", MQ.MA_JS, re.S)
MAN += '\nconst MA04_SRC_TODAS = ' + json.dumps(_m.group(1) if _m else '') + ';\n'
src = ('globalThis.print=(...a)=>console.log(...a);\n' + LS + G2 + '\n' + STUBS + '\n' + EST + '\n' + OS + '\n' + MAN + '\n'
       + open(os.path.join(HERE, 'aprova_quem_decide_unit.js'), encoding='utf-8').read())
fd, p = tempfile.mkstemp(prefix='aqd_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
finally: os.unlink(p)
print(r.stdout, end='')
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
if r.returncode and not fa: print('FALHA motor JS:', r.stderr[-2000:])
print(f'RESULTADO {n - fa}/{n}' + ('' if r.returncode == 0 or fa else ' · motor JS terminou com erro'))
sys.exit(0 if n and not fa and r.returncode == 0 else 1)
