# -*- coding: utf-8 -*-
"""EDL-01 · executor do saf_lote_unit.js no node, sem navegador: o bloco SL-PURO de safra_lote.js (colar do Excel, datas com atalho, número
pt-BR, o que cada célula aceita, aplicar aos marcados e o contador de alterações) com o g2num do g2lib.js (fonte única do número).
Uso (de gen37/): python3 -B saf_lote_unit_test.py   (sai 1 se algum caso falhar)
Contraprova: GEN=<gen37 da base> falha na montagem (a base não tem safra_lote.js)."""
import os, sys, re, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); G = os.environ.get('GEN', HERE)
src_l = open(os.path.join(G, 'safra_lote.js'), encoding='utf-8').read()
i, j = src_l.index('// >>> SL-PURO'), src_l.index('// <<< SL-PURO')
g2 = open(os.path.join(G, 'g2lib.js'), encoding='utf-8').read()
num = re.search(r'^function g2num\(s\)\{.*$', g2, re.M).group(0)
src = num + '\n' + src_l[i:j] + '\n' + open(os.path.join(HERE, 'saf_lote_unit.js'), encoding='utf-8').read()
fd, p = tempfile.mkstemp(prefix='saflote_', suffix='.js')
with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(src)
try: r = subprocess.run(['node', p], capture_output=True, text=True, timeout=120)
finally: os.unlink(p)
print(r.stdout, end='')
lin = r.stdout.splitlines(); n = sum(1 for l in lin if l.startswith(('OK ', 'FALHA '))); fa = sum(1 for l in lin if l.startswith('FALHA '))
if r.returncode: print('ERRO node:', r.stderr[-1500:])
print(f'RESULTADO {n - fa}/{n}')
sys.exit(0 if n and not fa and r.returncode == 0 else 1)
