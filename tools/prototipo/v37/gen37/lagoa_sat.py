# -*- coding: utf-8 -*-
"""Valores do Mapa por pivô e índice a partir do resumo de uma cena da Lagoa Grande (lagoa_s2_resumo.json, real ou sintético).
Fonte única do consumo: areas/inicio.py (Mapa) e tools/geo/s2_l2a_montagem_test.py usam esta função.
Contrato MAPA-REAL (Codex 6270730787): sem leitura válida (máscara, nuvem ou resultado inválido) o índice fica None, nunca zero,
e os demais pivôs e índices seguem. Pivô inteiro sob nuvem vira 'cloud' (a tela já diz "nuvem · sem leitura")."""


def sat_v(cena, ids, idxn):
    out = {}
    for p in ids:
        e = (cena.get('est') or {}).get(p) or {}
        vals = [(e.get(n) or {}).get('med') for n in idxn]
        out[p] = 'cloud' if all(v is None for v in vals) and (e.get('nuvem') or 0) >= 99.95 else vals
    return out
