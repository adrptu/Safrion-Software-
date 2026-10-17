# -*- coding: utf-8 -*-
"""RESOLVE-1-CLIQUE · reprodução sem navegador (Claude, 16/10/2026).

Monta no Node o motor real do protótipo, como ma_regras_test.py (os_unit) e est_onda0_test.py:
perfis do g2lib + cenário (CEN0 e cenario.js) + núcleo da O.S. (JS_NUCLEO, OSD) + regras da manutenção
e de Compras de materiais (dados_manutencao.js_regras, dados_compras_mat) + dados2.os_base/est_base
+ repro_casos.js. Dados sintéticos. Nada é gravado na pasta do gerador: o pacote vai para uma pasta
temporária, Python roda com -B e o estado do navegador é um objeto em memória.

Uso:  python3 -B repro.py --gen <pasta gen37> [--rotulo texto]
Sai 0 quando o motor executou; cada caso imprime o observado (não é teste de aceite)."""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('--gen', required=True)
ap.add_argument('--rotulo', default='')
a = ap.parse_args()
G = Path(a.gen).resolve()
HERE = Path(__file__).resolve().parent
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
sys.dont_write_bytecode = True
sys.path.insert(0, str(G)); os.chdir(G)

import cenario, dados2 as D2, dados_manutencao as DM   # noqa: E402
import areas.processo_os as P                            # noqa: E402

# armazenamento do navegador simulado em memória (o motor só fala com ele por getItem/setItem/removeItem)
pre = ("globalThis.print=(...a)=>console.log(...a);var __ls={};"
       "var localStorage={getItem:k=>(k in __ls?__ls[k]:null),setItem:(k,v)=>{__ls[k]=String(v);},removeItem:k=>{delete __ls[k];}};"
       "var window={addEventListener(){}};var location={hash:'',pathname:'',search:''};var history={replaceState(){}};\n")
osd = dict(ords=P._ordens(), nova=P._nova_ordem_dados(), aloc={}, agf={})
src = (pre + cenario.perfis_js() + cenario.js_prefixo()
       + 'const OSD = ' + json.dumps(osd, ensure_ascii=False) + ';\n' + P.JS_NUCLEO + '\n' + DM.js_regras()
       + '\nconst R1C_OSB = ' + json.dumps(D2.os_base(), ensure_ascii=False)
       + ';\nconst R1C_ESTB = ' + json.dumps(D2.est_base(), ensure_ascii=False)
       + ';\nconst R1C_LOCFAZ = ' + json.dumps(D2.LOC_FAZ, ensure_ascii=False)
       + ';\nconst R1C_ROTULO = ' + json.dumps(a.rotulo) + ';\n'
       + (HERE / 'repro_casos.js').read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='resolve1_') as td:
    p = Path(td) / 'run.js'; p.write_text(src, encoding='utf-8')
    r = subprocess.run(['node', str(p)], capture_output=True, text=True, timeout=180)
print(r.stdout, end='')
if r.stderr: print(r.stderr, end='', file=sys.stderr)
raise SystemExit(r.returncode)
