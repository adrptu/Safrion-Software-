# Diferenças entre dois retratos (antes × depois), por página × tamanho e por grupo. Uso: python3 compara.py <antes.json> <depois.json>
import json, sys
A = json.load(open(sys.argv[1])); D = json.load(open(sys.argv[2])); n = 0
for k in sorted(set(A) | set(D)):
    a, d = A.get(k), D.get(k)
    if a == d: continue
    n += 1
    if not a or not d: print(k, 'ausente', a is None, d is None); continue
    dif = [g for g in ('main', 'filhos', 'cartoes', 'rolas') if a.get(g) != d.get(g)]
    extra = []
    if 'rolas' in dif: extra.append(('rolas', a['rolas'], d['rolas']))
    if 'cartoes' in dif: extra.append(('cartoes', [(x, y) for x, y in zip(a['cartoes'], d['cartoes']) if x != y][:4]))
    print(k, dif, *extra)
print('páginas×tamanhos com diferença:', n, 'de', len(A))
