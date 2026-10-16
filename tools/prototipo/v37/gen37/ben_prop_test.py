# -*- coding: utf-8 -*-
"""Beneficiamento · rodada 3 (BEN-D33..D36): propriedade aleatória dos invariantes de caixas (ben_prop.js) no motor das telas, sem navegador.
Uso: SAFRION_DADOS=sintetico python3 ben_prop_test.py   → uma linha por caso fixo (U53a..g) e por invariante violado (com a trilha mínima) e
'RESULTADO: OK|FALHOU' no fim. RUNS e STEPS pelo ambiente (padrão 120 × 35 em 3 sementes, ~30 s); o noturno roda maior.
No código anterior à rodada 3 o teste tem de reprovar mostrando os seis invariantes do aceite (COBERTURA)."""
import os, sys, json
os.environ.setdefault('SAFRION_DADOS', 'sintetico'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ben_unit_test as T
SEIS = ['I-a1', 'I-d2', 'I-e4', 'I-b1', 'I-a4', 'I-a3']   # aceite 1 da seção 6 do desenho: o gerador alcança cada um
import subprocess
os.makedirs(os.path.join(T.HERE, '_probe'), exist_ok=True); arq = os.path.join(T.HERE, '_probe', 'ben_prop_all.js')
open(arq, 'w', encoding='utf-8').write(T.motor() + open(os.path.join(T.HERE, 'ben_prop.js'), encoding='utf-8').read())
r = subprocess.run(['node', arq], capture_output=True, text=True, timeout=int(os.environ.get('PROP_TIMEOUT', '900')))   # o noturno (RUNS e STEPS maiores) passa dos 180 s do node() da unidade
try: out = json.loads(r.stdout.strip().splitlines()[-1])
except Exception: out = {'ok': False, 'fixas': [], 'invariantes': [], 'falhas': [{'inv': 'motor', 'info': r.stderr[-800:]}]}
for f in out.get('fixas', []): print(('OK    ' if f['ok'] else 'FALHA ') + f['n'] + ' ' + f['t'] + ('' if f['ok'] else ' · ' + json.dumps(f['V'], ensure_ascii=False)[:500]))
for f in out.get('falhas', []): print('FALHA', f['inv'], 'semente', f.get('seed'), 'passo', f.get('passo'), json.dumps(f.get('info'), ensure_ascii=False)[:400], '\n  trilha mínima:', json.dumps(f.get('trilha'), ensure_ascii=False))
vis = out.get('invariantes', [])
if not out.get('ok'): print('COBERTURA dos seis do aceite:', 'todos vistos' if all(x in vis for x in SEIS) else 'faltou ' + ', '.join(x for x in SEIS if x not in vis), '·', vis)
print('RESULTADO:', 'OK' if out.get('ok') else 'FALHOU', out.get('runs'), 'sequências ×', out.get('steps'), 'passos;', len(out.get('fixas', [])), 'casos fixos', '· invariantes violados:', ', '.join(vis) or 'nenhum')
sys.exit(0 if out.get('ok') else 1)
