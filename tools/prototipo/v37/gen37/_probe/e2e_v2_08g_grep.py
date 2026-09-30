# -*- coding: utf-8 -*-
"""v2 · 8g · grep nos .dc.html de _render: "Fora da política", "PA-07", "exceção" (fora de contexto de fertirrigação)."""
import re, os, sys, html
R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_render')
PAT = re.compile(r'Fora da política|PA-07|exceç(?:ão|ões)', re.I)
telas = sys.argv[1:] or ['OS', 'IN-02', 'IN-04', 'PL-04', 'IR-02', 'MB-08']
for t in telas:
    s = html.unescape(open(os.path.join(R, t + '.dc.html'), encoding='utf-8').read())
    hits = []
    for m in PAT.finditer(s):
        ctx = s[max(0, m.start() - 160):m.end() + 120].replace('\n', ' ')
        if re.search(r'fertirriga|OS-0418', ctx, re.I): continue
        hits.append(ctx)
    print(f'== {t}: {len(hits)} ocorrência(s) fora de fertirrigação')
    for h in hits[:12]: print('   …' + h + '…')
