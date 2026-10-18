# -*- coding: utf-8 -*-
"""INTEL-03 F1 · contas do bloco "Mercado e momento" (inteligencia.js: int3Real, int3Percentil, int3Sazonal, int3Leitura) no node, sem navegador.
Oráculo independente em Decimal, aqui, dos mesmos dados (dados_inteligencia.precos(): séries sintéticas de 60 meses e IPCA sintético).
  A2/A3 índice do mês, faixa, melhor mês, acerto, evidência e percentil iguais ao oráculo, em 2 vendas e 2 compras × 12, 24, 36 e 48 meses
  A4 contraprova da inflação: série que só sobe com o IPCA sai "Sem padrão" sem inflação; no nominal daria um falso melhor mês (o último de cada janela)
  A5 12 meses nunca dá selo (um ano é exemplo, não padrão)
  ausente ≠ zero: período maior que a série = falta; mês sem IPCA = sem leitura
Uso (de gen37/): SAFRION_DADOS=sintetico python3 -B intel03_unit_test.py → 'RESULTADO: OK n/n'."""
import os, sys, json, subprocess
from decimal import Decimal as D, getcontext
getcontext().prec = 40
sys.dont_write_bytecode = True
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comercial_unit_test as CU
import dados_inteligencia as DI

P = DI.precos(); IPCA = {m: D(v) for m, v in P['ipca'].items()}
MES = lambda m: int(m[5:7]) - 1
media = lambda xs: sum(xs, D(0)) / len(xs)


def leitura(serie, n, lado, ipca=IPCA):
    ult = ipca[serie[-1]['m']]
    real = [dict(m=x['m'], p=D(x['p']) * ult / ipca[x['m']]) for x in serie]
    if len(real) < n: return dict(falta=True)
    js = real[-n:]; N = len(js) // 12; anos = []
    mt = D(len(js) - 1) / 2; mp = media([x['p'] for x in js])
    b_ = sum(((D(t) - mt) * (x['p'] - mp) for t, x in enumerate(js)), D(0)) / sum(((D(t) - mt) ** 2 for t in range(len(js))), D(0))
    sem = [dict(m=x['m'], p=x['p'] / (mp + b_ * (D(t) - mt))) for t, x in enumerate(js)]   # sem a tendência linear do período
    for w in range(N):
        jan = sem[len(sem) - 12 * (w + 1): len(sem) - 12 * w]; med = media([x['p'] for x in jan]); r = [None] * 12
        for x in jan: r[MES(x['m'])] = x['p'] / med
        anos.append(r)
    idx = [media([a[k] for a in anos]) for k in range(12)]
    venda = lado == 'venda'; melhor = 0
    for k in range(1, 12):
        if (idx[k] > idx[melhor]) if venda else (idx[k] < idx[melhor]): melhor = k
    acerto = sum(1 for a in anos if (a[melhor] > 1 if venda else a[melhor] < 1))
    amp = max(idx) - min(idx)
    ev = 'Sem padrão' if (N == 1 or amp < D('0.03')) else ('Forte' if (N >= 3 and acerto >= N - 1) else 'Fraca')
    xs = [x['p'] for x in js]; hoje = xs[-1]
    pct = int((D(sum(1 for x in xs if x < hoje)) / (len(xs) - 1) * 100).quantize(D('1'), rounding='ROUND_HALF_UP'))
    return dict(N=N, idx=[float(x) for x in idx], mn=[float(min(a[k] for a in anos)) for k in range(12)], mx=[float(max(a[k] for a in anos)) for k in range(12)],
                melhor=melhor, acerto=acerto, ev=ev, pct=pct, amp=float(amp))


def oraculo():
    casos = []
    for lado, lista, chave in (('venda', P['vendas'], 'prod'), ('compra', P['compras'], 'nome')):
        com = [x for x in lista if x.get('serie')][:2]
        for x in com:
            for n in (12, 24, 36, 48):
                casos.append(dict(lado=lado, nome=x[chave], n=n, o=leitura(x['serie'], n, lado)))
    # A4: série que só acompanha o IPCA (sem época): o preço real é constante
    so = [dict(m=m, p=str((D('100') * IPCA[m] / IPCA[P['meses'][0]]).quantize(D('0.01')))) for m in P['meses']]
    um = {m: D('100') for m in P['meses']}
    a4 = dict(real=[leitura(so, n, 'venda')['ev'] for n in (24, 36, 48)], nominal=[leitura(so, n, 'venda', um)['ev'] for n in (24, 36, 48)])
    return dict(casos=casos, so=so, um={m: '100' for m in P['meses']}, a4=a4)


JS = r'''
const R = []; function ok(n, c, info) { R.push({ n, ok: !!c, info: c ? '' : JSON.stringify(info === undefined ? '' : info).slice(0, 700) }); }
const perto = (a, b) => Math.abs(Number(a) - Number(b)) <= 1e-5;   /* o motor guarda 6 casas (ENG-013); o oráculo, 40 dígitos */
const serieDe = (lado, nome) => lado === 'venda' ? INTP.vendas.find(x => x.prod === nome).serie : INTP.compras.find(x => x.nome === nome).serie;
ORA.casos.forEach(c => { const L = int3Leitura(serieDe(c.lado, c.nome), INTP.ipca, c.n, c.lado), o = c.o;
  const igual = L && !L.falta && L.N === o.N && L.z.idx.every((x, i) => perto(x, o.idx[i])) && L.z.min.every((x, i) => perto(x, o.mn[i])) && L.z.max.every((x, i) => perto(x, o.mx[i]))
    && L.melhor === o.melhor && L.acerto === o.acerto && L.ev === o.ev && L.pct === o.pct;
  ok('A3 ' + c.lado + ' · ' + c.nome + ' · ' + c.n + ' meses: índice, faixa, melhor mês, acerto (' + o.acerto + ' de ' + o.N + '), evidência (' + o.ev + ') e percentil (' + o.pct + ') = oráculo',
    igual, L && { N: L.N, melhor: L.melhor, acerto: L.acerto, ev: L.ev, pct: L.pct, o: { N: o.N, melhor: o.melhor, acerto: o.acerto, ev: o.ev, pct: o.pct } });
  if (c.n === 12) ok('A5 ' + c.lado + ' · ' + c.nome + ': 12 meses é "Sem padrão" e não dá selo', L.ev === 'Sem padrão' && L.selo === null, [L.ev, L.selo]); });
const real = [24, 36, 48].map(n => int3Leitura(ORA.so, INTP.ipca, n, 'venda').ev), nom = [24, 36, 48].map(n => int3Leitura(ORA.so, ORA.um, n, 'venda').ev);
/* leitura ingênua (a do INTEL-02: preço nominal, com tendência, janelas de 12 meses): acha um "melhor mês" falso na série que só sobe com o IPCA */
const ing = intSazonal(ORA.so.slice(-48)), ingMelhor = intExtremo(ing, true), ingAmp = prSub(ing.idx.reduce((a, b) => prCmp(b, a) > 0 ? b : a), ing.idx.reduce((a, b) => prCmp(b, a) < 0 ? b : a));
ok('A4 série que só sobe com o IPCA: sem inflação é "Sem padrão" em 24, 36 e 48 meses (igual ao oráculo)', real.every(x => x === 'Sem padrão') && JSON.stringify(real) === JSON.stringify(ORA.a4.real), real);
ok('A4 sem o IPCA, a tendência linear do período também tira a inflação: "Sem padrão" (igual ao oráculo)', nom.every(x => x === 'Sem padrão') && JSON.stringify(nom) === JSON.stringify(ORA.a4.nominal), nom);
ok('A4 contraprova: a leitura ingênua (nominal e com tendência, a do INTEL-02) acha um falso melhor mês (setembro, o último de cada janela) com amplitude de 3% ou mais', ingMelhor === 8 && prCmp(ingAmp, '0.03') >= 0, [ingMelhor, ingAmp]);
const s0 = INTP.vendas.find(x => x.serie && x.serie.length).serie;
ok('ausente ≠ zero: período maior que a série é falta (não índice 0)', int3Leitura(s0.slice(-30), INTP.ipca, 36, 'venda').falta === true, int3Leitura(s0.slice(-30), INTP.ipca, 36, 'venda'));
const ip = Object.assign({}, INTP.ipca); delete ip[s0[10].m];
ok('ausente ≠ zero: mês sem IPCA = sem leitura (null), não preço real inventado', int3Leitura(s0, ip, 48, 'venda') === null, int3Leitura(s0, ip, 48, 'venda'));
ok('percentil: o menor preço do período é 0, o maior é 100, um só mês não tem posição', int3Percentil(['1', '2', '3'], '1') === 0 && int3Percentil(['1', '2', '3'], '3') === 100 && int3Percentil(['5'], '5') === null,
  [int3Percentil(['1', '2', '3'], '1'), int3Percentil(['1', '2', '3'], '3')]);
const L = int3Leitura(s0, INTP.ipca, 48, 'venda'), Lc = int3Leitura(s0, INTP.ipca, 48, 'compra');
ok('selo segue o lado: com evidência, venda e compra leem o mesmo percentil ao contrário', L.ev === 'Sem padrão' || (L.pct >= 70 ? L.selo === 'Bom momento para vender' : L.pct <= 30 ? L.selo === 'Abaixo do normal' : L.selo === 'Neutro'), [L.ev, L.pct, L.selo, Lc.selo]);
'''


def main():
    src = CU.fonte(True).split('const NUCLEO =')[0]
    src += DI.js_precos() + open(os.path.join(HERE, 'inteligencia.js'), encoding='utf-8').read()
    src += 'const ORA = ' + json.dumps(oraculo(), ensure_ascii=False) + ';\n' + JS + '\nprint(JSON.stringify(R));\n'
    os.makedirs(os.path.join(HERE, '_probe'), exist_ok=True)
    p = os.path.join(HERE, '_probe', 'intel03_unit.js'); open(p, 'w', encoding='utf-8').write(src)
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
