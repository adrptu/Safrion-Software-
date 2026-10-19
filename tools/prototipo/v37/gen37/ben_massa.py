# -*- coding: utf-8 -*-
"""Beneficiamento · espelho em Decimal das contas de ben.js (ESPECIFICACAO.md §3.4 e §11.3: "espelho Python = JS").
Não é segunda fonte de regra para a tela: serve ao teste (ben_unit_test.py), que confere o JS (BigInt de producao.js) contra esta conta
independente, em 6 casas, meio para cima. Tara, caixas sugeridas, faixa, balanço, alçada e rateio acumulado da genealogia."""
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_CEILING, getcontext
getcontext().prec = 40
Q6 = D('0.000001')


def q6(x): return D(x).quantize(Q6, rounding=ROUND_HALF_UP)


def tara(cx, pallets, tara_cx, tara_pallet): return q6(D(cx) * D(tara_cx) + D(pallets) * D(tara_pallet))


def caixas(kg, frac, massa): return int((D(kg) * D(frac) / D(massa)).to_integral_value(rounding=ROUND_CEILING))


def faixa(proc, tol): return q6(D(proc) * D(tol))


def bal(proc, saidas, tol):
    dif = q6(D(proc) - sum((D(s) for s in saidas), D(0)))
    return dict(dif=dif, pct=q6(dif * 100 / D(proc)), faixa=faixa(proc, tol), dentro=abs(dif) <= faixa(proc, tol))


def alcada(proc, dif, pct, teto):
    lp = q6(D(proc) * D(pct) / 100); lim = min(lp, D(teto)); return dict(lim=lim, passa=abs(D(dif)) > lim, por_pct=lp <= D(teto))


def rateio(S, pesos):
    E = sum((D(p) for p in pesos), D(0)); acc = D(0); prev = D(0); out = []
    for p in pesos:
        acc += D(p); cur = q6(D(S) * acc / E); out.append(cur - prev); prev = cur
    return out
