# -*- coding: utf-8 -*-
"""Roda a jornada e2e em ordem (e2e_*.py, fora e2e_lib e a sonda com argumento), a partir do cenário restaurado, no Chrome 9777
e no servidor 8777 já em execução. Cada sonda com limite de tempo; classificação por _probe/classificar.py.
Uso: python3 _probe/e2e_rodar.py [saida.md]"""
import subprocess, sys, os, time, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(os.path.dirname(HERE))
from classificar import classe, motivos
from e2e_lib import B
saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'e2e_resultado.md')
b = B(); b.goto('MB-01.dc.html'); b.J("localStorage.removeItem('talhao-os-cenario-v1'); localStorage.removeItem('talhao-os-mb-os'); 'ok'")
del b
fs = [f for f in sorted(glob.glob(os.path.join(HERE, 'e2e_*.py'))) if os.path.basename(f) not in ('e2e_lib.py', 'e2e_00_probe.py')]
L = ['# Jornada e2e com o harness corrigido', '', '| Sonda | Classe | Motivo / última linha |', '|---|---|---|']; cont = {}
for f in fs:
    n = os.path.basename(f)
    try:
        p = subprocess.run(['python3', '-u', f], capture_output=True, text=True, timeout=180); out = p.stdout + p.stderr; code = p.returncode
    except subprocess.TimeoutExpired: out, code = 'TIMEOUT (180 s)', 124
    open(os.path.join(HERE, 'e2eh_' + n.replace('.py', '.out')), 'w', encoding='utf-8').write(out)
    cl = classe(out, code); cont[cl] = cont.get(cl, 0) + 1
    ult = ([l for l in out.strip().splitlines() if l.strip()] or [''])[-1]
    L.append(f"| {n} | {cl} | {('; '.join(motivos(out, code)[:2]) or ult).replace('|', '/')[:150]} |"); print(L[-1], flush=True)
L += ['', ' · '.join(f'{k}: {v}' for k, v in sorted(cont.items()))]
open(saida, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print(L[-1])
