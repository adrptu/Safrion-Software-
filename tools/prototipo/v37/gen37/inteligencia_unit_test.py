# -*- coding: utf-8 -*-
"""INTEL-01 · testes de unidade da Inteligência de vendas e de compras (inteligencia.js) no node, sem navegador.
Oráculo independente: as contas esperadas saem daqui, em Decimal, dos mesmos dados (INTC e a semente), e não do JS testado.
Monta o JS real: perfis + cenário + producao.js + PR_UI_JS/PR_PED_JS + comercial.js + INTC + inteligencia.js (a mesma montagem
do comercial_unit_test.py). Uso (de gen37/): SAFRION_DADOS=sintetico python3 inteligencia_unit_test.py → 'RESULTADO: OK n/n'."""
import os, sys, json, subprocess
from decimal import Decimal as D
sys.dont_write_bytecode = True
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comercial_unit_test as CU
import dados_inteligencia as DI


def oraculo():
    d = DI.dados(); hoje = '2026-09-26'
    iso = lambda s: s[6:10] + '-' + s[3:5] + '-' + s[0:2]
    it = {}
    for i in d['itens']:
        cs = sorted(d['cot'].get(i['nome'], []), key=lambda x: D(x['preco']))
        val = [x for x in cs if iso(x['validade']) >= hoje]
        m = val[0] if val else None
        it[i['nome']] = dict(melhor=m['preco'] if m else None, f=m['f'] if m else None,
                             vref=str((D(m['preco']) - D(i['ref'])) / D(i['ref'])) if m else None,
                             eco=str(D(i['qtd']) * (D(i['ref']) - D(m['preco']))) if m else None)
    eco = sum((D(v['eco']) for v in it.values() if v['eco'] is not None and D(v['eco']) > 0), D(0))
    tot = sum((D(i['qtd']) * D(i['ref']) for i in d['itens']), D(0))
    pont = {}
    for f in d['forn']:
        es = [h for h in d['hist'] if h['f'] == f['id'] and h['entregue']]
        pont[f['id']] = str(D(sum(1 for h in es if not h['atraso'] > 0)) / D(len(es))) if es else None
    return dict(itens=it, eco=str(eco), rsha=str(tot / D(d['area'])), pont=pont, n_itens=len(d['itens']), precos=oraculo_precos())


def oraculo_precos():
    """INTEL-02 em Decimal, dos mesmos dados (DI.precos), sem o JS: índice sazonal, tendência sem a época, normal do mês, melhor mês,
    recomendação e economia."""
    P = DI.precos(); MES = lambda m: int(m[5:7]) - 1
    media = lambda xs: sum(xs, D(0)) / len(xs)
    IP = {m: D(v) for m, v in P['ipca'].items()}
    def saz(s):
        # INTEL-03 (18/10): sem inflação (IPCA) e sem a tendência linear do histórico, como o bloco "Mercado e momento" (intZ)
        ult = IP[s[-1]['m']]; real = [D(x['p']) * ult / IP[x['m']] for x in s]
        mt = D(len(real) - 1) / 2; mp = media(real)
        b_ = sum(((D(t) - mt) * (p - mp) for t, p in enumerate(real)), D(0)) / sum(((D(t) - mt) ** 2 for t in range(len(real))), D(0))
        sem = [dict(m=x['m'], p=real[t] / (mp + b_ * (D(t) - mt))) for t, x in enumerate(s)]
        acc = [[] for _ in range(12)]
        for w in range(len(sem) // 12):
            jan = sem[len(sem) - 12 * (w + 1): len(sem) - 12 * w]; med = media([x['p'] for x in jan])
            for x in jan: acc[MES(x['m'])].append(x['p'] / med)
        return [media(a) for a in acc]
    def comum(s):
        idx = saz(s); m0 = MES(s[-1]['m']); ds = lambda x: D(x['p']) / idx[MES(x['m'])]
        a, b = media([ds(x) for x in s[-3:]]), media([ds(x) for x in s[-6:-3]]); tv = (a - b) / b
        esp = media([D(x['p']) for x in s[-12:]]) * idx[m0]; vs = (D(s[-1]['p']) - esp) / esp
        return dict(idx=[str(x) for x in idx], m0=m0, tv=str(tv), tend='Alta' if tv > D('0.03') else 'Queda' if tv < D('-0.03') else 'Estável', esp=str(esp), vs=str(vs)), idx, m0, vs
    vendas, compras = {}, {}
    for v in P['vendas']:
        if not v['serie']: vendas[v['prod']] = None; continue
        o, idx, m0, vs = comum(v['serie']); bdB = 0
        for d in range(1, 12):
            if idx[(m0 + d) % 12] > idx[(m0 + bdB) % 12]: bdB = d
        # revisão Codex INTEL-02-LIQUIDO-01: o alvo é o maior ganho LÍQUIDO (empate: o mais cedo); o oráculo antigo repetia a seleção bruta
        bd, liq, ganho = 0, D(0), D(0)
        if bdB > 0:
            cand = [(idx[(m0 + d) % 12] / idx[m0] - 1 - D('0.012') * d, -d) for d in range(1, 12)]
            l, nd = max(cand); bd = -nd; liq = l; ganho = idx[(m0 + bd) % 12] / idx[m0] - 1
        rec = 'Vender na colheita' if v.get('perecivel') else 'Vender agora' if (bdB == 0 or vs >= D('0.05')) else 'Esperar' if liq >= D('0.03') else 'Sem ganho em esperar'
        o.update(melhor=max(range(12), key=lambda k: (idx[k], -k)), bd=bd, ganho=str(ganho), liq=str(liq), rec=rec); vendas[v['prod']] = o
    eco_t = D(0)
    for c in P['compras']:
        s = c['serie']; o, idx, m0, vs = comum(s); ref = s[-1]['m']; lim = c['lim']
        DD = max(0, min(11, (int(lim[:4]) - int(ref[:4])) * 12 + int(lim[5:7]) - int(ref[5:7]))) if lim else 11; bd = 0
        for d in range(1, DD + 1):
            if idx[(m0 + d) % 12] < idx[(m0 + bd) % 12]: bd = d
        econ = 1 - idx[(m0 + bd) % 12] / idx[m0]
        rec = 'Comprar agora' if (DD == 0 or bd == 0 or vs <= D('-0.05')) else 'Esperar' if econ >= D('0.03') else 'Comprar até a necessidade'
        eco = D(c['qtd']) * D(s[-1]['p']) * econ if rec == 'Esperar' else None
        if eco is not None: eco_t += eco
        o.update(melhor=min(range(12), key=lambda k: (idx[k], k)), D=DD, bd=bd, econ=str(econ), rec=rec, eco=None if eco is None else str(eco)); compras[c['nome']] = o
    return dict(vendas=vendas, compras=compras, economia=str(eco_t))


def main():
    src = CU.fonte(True).split('const NUCLEO =')[0]
    src += DI.js() + DI.js_precos() + open(os.path.join(HERE, 'inteligencia.js'), encoding='utf-8').read()
    src += 'const ORA = ' + json.dumps(oraculo(), ensure_ascii=False) + ';\n'
    src += open(os.path.join(HERE, 'inteligencia_unit.js'), encoding='utf-8').read() + '\nprint(JSON.stringify(R));\n'
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'inteligencia_unit.js'); open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=180)
    out = r.stdout.strip().splitlines(); res = json.loads(out[-1]) if out and r.returncode == 0 else []
    ok = [r.returncode == 0 and bool(res)]
    print(('OK    ' if ok[0] else 'FALHA ') + 'motor JS (node) executou sem erro' + ('' if ok[0] else ' · ' + r.stderr[-900:]))
    for x in res:
        ok.append(x['ok']); print(('OK    ' if x['ok'] else 'FALHA ') + x['n'] + ('' if x['ok'] else ' · ' + x['info']))
    print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
    return all(ok)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
