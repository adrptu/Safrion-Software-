# -*- coding: utf-8 -*-
"""Inventário estático: cada cor da paleta operacional e os significados que ela recebe nas legendas do IN-04 (D14, D15).
Lê areas/inicio.py (chamadas Lc(l,'cor','texto') e os mapas COLHCOR/CARCOR/SOLOCOR). Executar: python3 -I cor_significado.py <gen37>"""
import re, sys, os, collections
G = sys.argv[1]; src = open(os.path.join(G, 'areas', 'inicio.py'), encoding='utf-8').read().split('\n')
uso = collections.defaultdict(list)
for n, l in enumerate(src, 1):
    for m in re.finditer(r"Lc\((?:l|CAR_L|SOLO_L|COLH_L),'(\w+)','([^']+)'\)", l):
        uso[m.group(1)].append((m.group(2), n))
for nome in ('COLHCOR', 'SOLOCOR'):   # CARCOR repete a legenda de carência (Lc literais)
    for n, l in enumerate(src, 1):
        if l.startswith('const ' + nome + '='):
            for k, v in re.findall(r"'?([\wÀ-ú ]+)'?:'(\w+)'", l.split('=', 1)[1]): uso[v].append((f'{nome} {k.strip()}', n))
print('| cor (token do protótipo) | nº de significados | significados (inicio.py:linha) |'); print('|---|---:|---|')
for cor in sorted(uso, key=lambda c: -len(uso[c])):
    sig = sorted({s for s, _ in uso[cor]}); print(f"| {cor} | {len(sig)} | " + '; '.join(f'{s} ({min(n for s2, n in uso[cor] if s2 == s)})' for s in sig) + ' |')
