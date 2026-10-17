# -*- coding: utf-8 -*-
"""Alcance das telas a partir do menu vigente (executado sobre o render da varredura, somente leitura).
Uso: python3 -B -I alcance_menu.py <pasta_render> <pasta_gen37>
Lê cada <tela>.dc.html, colhe as referências a outras telas (XX.dc.html) e faz uma busca em largura a partir das telas do menu
(ui37.oculto == False). Imprime: telas ocultas alcançáveis (com o caminho mais curto) e telas ocultas sem caminho a partir do menu.
Aproximação: conta toda referência no HTML (links, dados de JS com h:'…'), inclusive as que só aparecem em certo estado."""
import os, re, sys, json
from collections import deque
R, G = sys.argv[1], sys.argv[2]
sys.path.insert(0, G)
import ui37
fs = sorted(f for f in os.listdir(R) if f.endswith('.dc.html'))
nomes = set(fs)
arestas = {}
for f in fs:
    t = open(os.path.join(R, f), encoding='utf-8', errors='replace').read()
    arestas[f] = sorted({m for m in re.findall(r'([A-Za-z0-9-]+\.dc\.html)', t) if m in nomes and m != f})
menu = [f for f in fs if not ui37.oculto(f)]
pai = {f: None for f in menu}
q = deque(menu)
while q:
    a = q.popleft()
    for b in arestas[a]:
        if b not in pai:
            pai[b] = a; q.append(b)
def caminho(f):
    c = []
    while f: c.append(f[:-8]); f = pai[f]
    return ' <- '.join(c)
ocultas = [f for f in fs if ui37.oculto(f)]
alc = [f for f in ocultas if f in pai]
sem = [f for f in ocultas if f not in pai]
print('menu', len(menu), '| ocultas', len(ocultas), '| ocultas alcançáveis', len(alc), '| sem caminho', len(sem))
for f in alc: print('ALCANCAVEL', caminho(f))
for f in sem: print('SEM_CAMINHO', f[:-8], '| entra por:', ','.join(x[:-8] for x in fs if f in arestas[x]) or '—')
