# tabela antes × depois dos 15 (ACELERA): par alternado da 14-medida (mesma trava, um logo após o outro) como medida principal;
# amostras extras: antes = 00-antes e 06-medida/antes (código 302b26f, que não mudou); depois = 13-bateria/nav (código final).
# Resultado: o resumo (sem tempos) de todas as amostras tem de ser um só.
import os, re, sys, statistics, json
S = sys.argv[1]


def le(d):
    r = {}
    p = os.path.join(S, d, '_resumo.txt')
    if os.path.exists(p):
        for l in open(p, encoding='utf-8'):
            m = re.match(r'(\S+) rc=(\d+) t=([\d.]+)s :: (.*)', l)
            if m: r[m.group(1)] = (float(m.group(3)), m.group(2) + ' ' + re.sub(r' · \d+ s\b', '', m.group(4)).strip())
    return r


PA, PD = le('14-medida/antes'), le('14-medida/depois')
EA = [le('00-antes'), le('06-medida/antes')]; ED = [le('13-bateria/nav')]
nomes = [l.split('|')[0] for l in open(os.path.join(S, 'bin/lista15.txt')) if l.strip()]
ta = td = 0; out = []; dados = {}
for n in nomes:
    if n not in PA or n not in PD: out.append(f'| `{n}` | — | — | — | falta amostra |'); continue
    a, d = PA[n][0], PD[n][0]; ta += a; td += d
    xa = [x[n][0] for x in EA if n in x]; xd = [x[n][0] for x in ED if n in x]
    res = {x[n][1] for x in [PA, PD] + EA + ED if n in x}
    dados[n] = {'antes': a, 'depois': d, 'antes_extra': xa, 'depois_extra': xd, 'resultados': sorted(res)}
    out.append(f'| `{n}` | {a:.0f} | {d:.0f} | {100 * (d - a) / a:+.0f}% | ' + ' · '.join(f'{x:.0f}' for x in xa) + ' | '
               + ' · '.join(f'{x:.0f}' for x in xd) + f' | {"sim" if len(res) == 1 else "NÃO: " + str(res)} |')
print('| Teste | Antes (s) | Depois (s) | Diferença | Antes, outras amostras (s) | Depois, na bateria (s) | Mesmo resultado em todas |')
print('|---|---|---|---|---|---|---|')
print('\n'.join(out))
if ta: print(f'| **Soma** | **{ta:.0f}** | **{td:.0f}** | **{100 * (td - ta) / ta:+.0f}%** | | | |')
json.dump(dados, open(os.path.join(S, '14-medida', 'medida.json'), 'w'), ensure_ascii=False, indent=1)
