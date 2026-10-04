# -*- coding: utf-8 -*-
"""Regra única de quantidade de insumo (SINT-C03, SINT-REV-20261003-2300).

quantidade(dose, área) = dose × área em DECIMAL exato (cada número pela sua forma decimal mais curta), com 2 casas,
meio para cima (ROUND_HALF_UP). Ex.: 0,5 L/ha × 62,25 ha = 31,125 → 31,13 L; × 62,79 ha = 31,395 → 31,40 L.
O consumo de um apontamento é quantidade(área acumulada depois) − quantidade(área acumulada antes): a soma dos
apontamentos fecha exatamente no total da ordem e a custódia zera, sem tolerância.
Mesma regra no JS: cenQtd / cenQtdTrecho (cenario.js); quantidade_test.py confere a igualdade dos dois lados."""
from decimal import Decimal, ROUND_HALF_UP


def _dec(x):
    return Decimal(repr(float(x)))


def qtd(dose, area):
    return float((_dec(dose) * _dec(area)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def qtd_trecho(dose, antes, ha):
    """consumo do trecho [antes, antes + ha] (áreas acumuladas, normalizadas a 6 casas)."""
    a0 = round(antes, 6); a1 = round(antes + ha, 6)
    return float(Decimal(repr(qtd(dose, a1))) - Decimal(repr(qtd(dose, a0))))
