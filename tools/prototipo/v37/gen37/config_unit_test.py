# -*- coding: utf-8 -*-
"""CONF-01 · executor do config_unit.js (regras de Configurações sem navegador): papéis e acesso (R1-R6), alçadas lidas pelos comandos
(R7-R11), idempotência (R12), aprovar e liberar por quem age (R13), trilha (R14-R15) e fila do ERP (R17).
Monta o JS real na ordem das telas: g2lib.js inteiro + assinatura (ASSIN0 + assinatura.js) + Configurações (CONF0 + configuracoes.js)
+ cenário + JS do Estoque + núcleo da O.S. (com carência). Uso (de gen37/): python3 config_unit_test.py   (sai 1 se algum caso falhar)"""
import os, sys, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); os.chdir(HERE)
import cenario
import dados_assinatura as DA
import dados_config as DCF
import areas.processo_os as P
from areas import processo_estoque as PE
LS = ("var __ls={}; var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};\n"
      "var window={addEventListener(){}}; var location={hash:'',pathname:'',search:''}; var history={replaceState(){}};\n")
G2 = open(os.path.join(HERE, 'g2lib.js'), encoding='utf-8').read()
EST = cenario.js_prefixo() + 'const E2 = ' + json.dumps(PE._dados_js(), ensure_ascii=False) + ';\nvar GRIDS=[];\n' + PE.JS
OS = 'const OSD = ' + json.dumps(dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={}), ensure_ascii=False) + ';\nconst RC_OS=[];\n' + P.JS_NUCLEO
# fontes para a varredura de literais (A4): o JS de cada arquivo do §0, como entra nas telas
FONTES = dict(cenario=open(os.path.join(HERE, 'cenario.js'), encoding='utf-8').read(), os=P.JS_NUCLEO, est=PE.JS, ostela=P.JS, irr=open(os.path.join(HERE, 'irrigacao_estado.js'), encoding='utf-8').read())
src = ('globalThis.print=(...a)=>console.log(...a);\n' + LS + G2 + '\n' + DA.js_prefixo() + DCF.js_prefixo() + EST + '\n' + OS + '\n'
       + 'const FONTES = ' + json.dumps(FONTES, ensure_ascii=False) + ';\n'
       + open(os.path.join(HERE, 'config_unit.js'), encoding='utf-8').read())
fd, p = tempfile.mkstemp(prefix='conf_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
finally: os.unlink(p)
print(r.stdout, end='')
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
if r.returncode and not fa: print('FALHA motor JS:', r.stderr[-2000:])
print(f'RESULTADO {n - fa}/{n}' + ('' if r.returncode == 0 or fa else ' · motor JS terminou com erro'))
sys.exit(0 if n and not fa and r.returncode == 0 else 1)
