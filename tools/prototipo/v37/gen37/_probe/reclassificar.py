# -*- coding: utf-8 -*-
"""Reclassifica uma bateria já executada pelos logs gravados (_probe/bat_*.out + código de saída do log), sem reexecutar.
Uso: python3 _probe/reclassificar.py [log] [saida.md]"""
import re, os, sys
G = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(G); sys.path.insert(0, os.path.join(G, '_probe'))
from classificar import motivos, classe
log = sys.argv[1] if len(sys.argv) > 1 else '_probe/bateria_run.log'
saida = sys.argv[2] if len(sys.argv) > 2 else '_probe/bateria_resultado.md'
L = ['# Bateria de regressão · reclassificada pelo conteúdo real', '', f'Fonte: `{log}` (códigos de saída) e `_probe/bat_*.out`. Classificador: `_probe/classificar.py`.', '',
     '| Teste | Antes | Agora | Motivo / última linha |', '|---|---|---|---|']
cont = {}
for l in open(log, encoding='utf-8').read().splitlines():
    m = re.match(r'\| (.+?) \| (FALHA|ok)[^|]*\(exit (\d+)\) \| (\d+) \| (.*) \|$', l)
    if not m: continue
    t, antes, code, ult = m.group(1), m.group(2), int(m.group(3)), m.group(5)
    f = '_probe/bat_' + '_'.join(t.split()).replace('.py', '') + '.out'
    out = open(f, encoding='utf-8').read() if os.path.exists(f) else ''
    cl = classe(out, code); cont[cl] = cont.get(cl, 0) + 1
    mot = '; '.join(motivos(out, code)[:3]) or ult
    L.append(f'| {t} | {antes} | {cl} | {mot.replace("|", "/")[:150]} |')
tot = sum(cont.values()); exe = tot - cont.get('nao_executado', 0)
L += ['', f"**{cont.get('ok', 0)} ok · {cont.get('falha', 0)} falha · {cont.get('revisar', 0)} a revisar · {cont.get('nao_executado', 0)} não executado** "
      f"(denominador {exe}: os não executados ficam fora)."]
open(saida, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('\n'.join(L[-1:])); print('\n'.join(x for x in L if '| falha |' in x or '| revisar |' in x or '| nao_executado |' in x))
