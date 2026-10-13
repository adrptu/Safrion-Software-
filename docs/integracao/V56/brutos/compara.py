# compara base × candidata: resumo de cada teste e as asserções que falham (texto do teste, sem os valores medidos)
import os, re, sys, glob
S = sys.argv[1]; B = os.path.join(S, 'logs/base'); C = os.path.join(S, 'logs/cand'); C2 = os.path.join(S, 'logs/cand2')
def res(d, n):
    f = os.path.join(d, '_resumo.txt')
    if not os.path.exists(f): return None
    for l in open(f, encoding='utf-8'):
        if l.startswith(n + ' rc=') or l.startswith(n + ' AUSENTE'): return l.split(' :: ', 1)[-1].strip() if ' :: ' in l else l.strip()
    f = os.path.join(d, '_resumo_unit.txt')
    if os.path.exists(f):
        for l in open(f, encoding='utf-8'):
            if l.startswith(n + ' rc=') or l.startswith(n + ' AUSENTE'): return l.split(' :: ', 1)[-1].strip() if ' :: ' in l else l.strip()
    return None
def falhas(d, n):
    f = os.path.join(d, n + '.log')
    if not os.path.exists(f): return None
    out = []
    for l in open(f, encoding='utf-8', errors='replace'):
        m = re.match(r'\s*(FALHA|FALHOU|✗)\s+(.*)', l)
        if m: out.append(re.split(r' · [\[\(\{\'"]', m.group(2))[0].strip()[:200])
    return out
nomes = sorted({os.path.basename(f)[:-4] for f in glob.glob(C + '/*.log')} | {os.path.basename(f)[:-4] for f in glob.glob(C2 + '/*.log')})
for n in nomes:
    c2 = res(C2, n); c = c2 or res(C, n); b = res(B, n)
    fc = falhas(C2 if c2 else C, n) or []; fb = falhas(B, n)
    novo = [x for x in fc if fb is None or x not in fb]
    tag = 'IGUAL' if (fb is not None and sorted(fc) == sorted(fb)) else ('SÓ CAND' if b is None or (b and 'AUSENTE' in b) else 'DIFERE')
    print(f'{n}\n  base: {b}\n  cand{"(pós-correção)" if c2 else ""}: {c}\n  falhas cand: {fc}\n  falhas base: {fb}\n  novas: {novo} [{tag}]')
