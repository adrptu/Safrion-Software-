# compara uma bateria nova com a referência da V56 (cand-2e466eb, com os refeitos de cand-1f83eee por cima), teste a teste:
# código de saída, o resumo (sem tempos) e as asserções que falham (rótulo da asserção, sem os valores medidos; horários mascarados)
# uso: compara2.py <dir nova (nav)> [<dir nova (unit)>]
import os, re, sys
B = '/home/user/sp-acel/docs/integracao/V56/brutos'
REF = [os.path.join(B, x) for x in os.environ.get('REF', 'cand-2e466eb,cand-1f83eee').split(',')]   # o último que tem o teste vale
NOVA = sys.argv[1:]


def linhas(d):
    out = {}
    for f in ('_resumo.txt', '_resumo_unit.txt'):
        p = os.path.join(d, f)
        if os.path.exists(p):
            for l in open(p, encoding='utf-8'):
                m = re.match(r'(\S+) rc=(\d*) ', l)
                if m: out[m.group(1)] = (m.group(2), re.sub(r' · \d+ s\b', '', l.split(' :: ', 1)[-1].strip() if ' :: ' in l else ''))
    return out


def falhas(d, n):
    p = os.path.join(d, n + '.log')
    if not os.path.exists(p): return None
    out = []
    for l in open(p, encoding='utf-8', errors='replace'):
        m = re.match(r'\s*(FALHA|FALHOU|✗)\s+(.*)', l)
        if m:
            r = re.split(r' · [\[\(\{\'"]| [\[\{]', m.group(2))[0].strip()[:160]
            out.append(re.sub(r'/home/user/sp-[\w-]+/', '<worktree>/', re.sub(r'\b\d\d:\d\d\b', 'HH:MM', r)))   # caminho da worktree não é resultado
    return sorted(out)


ref = {}
for r in REF:
    for n, v in linhas(r).items(): ref[n] = (v, r)
nomes, nova = [], {}
for d in NOVA:
    for n, v in linhas(d).items(): nova[n] = (v, d); nomes.append(n)
iguais = dif = 0
for n in nomes:
    (rc, res), d = nova[n]
    if n not in ref:
        print(f'SEM_REF {n}: rc={rc} {res}'); continue
    (rrc, rres), rd = ref[n]
    fa, fb = falhas(rd, n), falhas(d, n)
    ok = rc == rrc and res == rres and fa == fb
    iguais += ok; dif += not ok
    print(('IGUAL ' if ok else 'DIFERE') + f' {n}: rc={rc} {res[:150]}' + ('' if ok else f'\n   ref ({os.path.basename(rd)}): rc={rrc} {rres[:200]}\n   falhas ref: {fa}\n   falhas nova: {fb}'))
falta = sorted(set(ref) - set(nova))
print(f'TOTAL {iguais} iguais · {dif} diferentes · {len(nomes)} rodados' + (f' · sem rodar: {falta}' if falta else ''))
