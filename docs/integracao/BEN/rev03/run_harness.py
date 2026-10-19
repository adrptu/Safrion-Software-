# -*- coding: utf-8 -*-
"""BEN-REV-20261009-03 · reprodução do Codex: motor das telas (ben_unit_test.motor(), sintético) + harness_codex.js, no node.
Uso (na raiz do repositório): SAFRION_DADOS=sintetico python3 docs/integracao/BEN/rev03/run_harness.py [saida.json]
Antes da correção (4373592): CX26-01 0 e QA-CX-02 1.540; depois (BEN-D31): CX26-01 540 e QA-CX-02 1.000 com reserva 100."""
import os, sys, json, subprocess, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..', '..', '..'))
G = os.path.join(RAIZ, 'tools', 'prototipo', 'v37', 'gen37'); sys.path.insert(0, G); os.environ.setdefault('SAFRION_DADOS', 'sintetico')
import ben_unit_test as T
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'harness_full.js'); open(p, 'w', encoding='utf-8').write(T.motor() + '\n' + open(os.path.join(AQUI, 'harness_codex.js'), encoding='utf-8').read())
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
if len(sys.argv) > 1: open(sys.argv[1], 'w', encoding='utf-8').write(r.stdout)
rep = json.loads(r.stdout)
for c in rep['cases']:
    a = c.get('after') or {}
    print(('PASSOU ' if c['passed'] else 'FALHOU ') + c['name'], c.get('error') or '', json.dumps({k: [a[k]['fisico'], a[k]['reservado']] for k in a}),
          (c['original']['lote'] + ' → ' + c['reversal']['lote']) if c.get('original') else '')
print('RESULTADO:', 'OK' if rep['passed'] else 'FALHOU', sum(c['passed'] for c in rep['cases']), '/', len(rep['cases']))
sys.exit(0 if rep['passed'] else 1)
