# Sonda do Claude sobre o delta 0e124664 (A3: Wilson 95 % e falso forte por semente/safra). Uso: python3 -I sonda_rx0_0e124664.py <dir do raiox_gabarito.py>
import sys; sys.path.insert(0, sys.argv[1]); import raiox_gabarito as g
W = g.intervalo_wilson
for k, n, lo, hi in ((0, 80, 0.0, 0.0458), (1, 80, 0.0022, 0.0675), (0, 20, 0.0, 0.1611), (16, 20, 0.5840, 0.9193), (17, 20, 0.6396, 0.9476)):
    r = W(k, n); ok = abs(r['inferior'] - lo) < 5e-5 and abs(r['superior'] - hi) < 5e-5
    print(f"W {k}/{n}: {r['inferior']:.4f}–{r['superior']:.4f} · oráculo {lo:.4f}–{hi:.4f} · {'ok' if ok else 'DIVERGE'}")
for rot, a in (('bool', (True, 3)), ('float', (1.0, 3)), ('eventos > total', (4, 3)), ('negativo', (-1, 3))):
    try: W(*a); print('W', rot, ': aceito (esperado: recusa)')
    except ValueError: print('W', rot, ': recusa')
print('W 0/0:', W(0, 0))
def des(sementes, cels=(('A', 'n', 'placebo'), ('B', 'k', 'fraco'))):
    return [dict(safra='s1', semente=s, alvo=a, fator=f, classe=c) for s in sementes for a, f, c in cels]
D80 = des(range(80))
res = [dict(r, motor='fraco') for r in D80]
s = g.resumir_falsos_fortes(res, D80)[0]; print('R1 80 sementes, 0 forte:', s['eventos_nas_completas'], s['estado'], round(s['wilson95']['superior'], 4))
res2 = [dict(r, motor='forte') if r['semente'] == 3 else dict(r, motor='fraco') for r in D80]
s = g.resumir_falsos_fortes(res2, D80)[0]; print('R2 uma semente com 2 células forte conta 1 evento:', s['eventos_nas_completas'], round(s['wilson95']['superior'], 4))
s = g.resumir_falsos_fortes(res[:-1], D80)[0]; print('R3 célula faltante:', s['estado'], s['wilson95'], len(s['faltantes']))
resi = [dict(r, motor='insuf') for r in D80]
s = g.resumir_falsos_fortes(resi, D80)[0]; print('R4 motor só insuf:', s['eventos_nas_completas'], s['insuf_celulas'], s['estado'], '(direção reprova à parte: insuf não é acerto)')
for rot, fn in (('desenho diferente entre sementes', lambda: g.resumir_falsos_fortes([], des([0]) + des([1], (('A', 'n', 'placebo'),)))),
                ('resultado fora do desenho', lambda: g.resumir_falsos_fortes([dict(safra='s1', semente=99, alvo='A', fator='n', classe='placebo', motor='fraco')], D80)),
                ('classe do motor inválida', lambda: g.resumir_falsos_fortes([dict(D80[0], motor='Forte')], D80)),
                ('classe esperada forte no desenho', lambda: g.resumir_falsos_fortes([], [dict(safra='s1', semente=0, alvo='A', fator='n', classe='forte')]))):
    try: fn(); print('R5', rot, ': aceito (esperado: recusa)')
    except ValueError as e: print('R5', rot, ': recusa ·', e)
s2 = g.resumir_falsos_fortes([dict(r, motor='fraco') for r in des(range(3)) + [dict(x, safra='s2') for x in des(range(3))]], des(range(3)) + [dict(x, safra='s2') for x in des(range(3))])
print('R6 safras separadas:', [(x['safra'], x['sementes_planejadas']) for x in s2])
