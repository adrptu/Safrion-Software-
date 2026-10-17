# -*- coding: utf-8 -*-
"""Quantos achados citam só telas fora do menu (ui37.oculto). Executado sobre o anexo dos achados.
Uso: python3 -B -I achados_por_alcance.py <anexo.md> <pasta_gen37>
"Legado" = fora do menu e que não é do app de campo (MB-*) nem do portal do parceiro (PT-*), que têm entrada própria."""
import re, sys
anexo, G = sys.argv[1], sys.argv[2]
sys.path.insert(0, G)
import ui37
t = open(anexo, encoding='utf-8').read()
todas, legado, ids_leg = 0, 0, []
for p in re.split(r'^### ', t, flags=re.M)[1:]:
    m = re.match(r'(\S+) · (\S+) · (.+?) · (.+)$', p.split('\n', 1)[0]); i, tela = m.group(1), m.group(3)
    ts = [x.strip().split(' ')[0] for x in re.split(r'[,/]', tela) if x.strip()]
    oc = [ui37.oculto(x + '.dc.html') for x in ts]
    if all(oc): todas += 1
    if all(o and not x.startswith(('MB-', 'PT-')) for o, x in zip(oc, ts)): legado += 1; ids_leg.append(i)
print('achados que citam só telas fora do menu:', todas)
print('… e que não são do app nem do portal (legado):', legado)
print(' '.join(ids_leg))
