# -*- coding: utf-8 -*-
"""Confere as contas da semente do SOLO-01 (ESPECIFICACAO §6) em decimal e lê cultivos, metas, áreas e datas de dados2.
Uso: cd tools/prototipo/v37/gen37 && python3 ../../../../docs/analise-solo/verificacao/conta_semente.py
Rodado sobre ecc8b00 em 06/10/2026 (saída em ESPECIFICACAO §6). Não é o serviço de domínio: só oráculo da especificação."""
import sys, os, datetime as dt
sys.path.insert(0, os.getcwd())
from decimal import Decimal as D, ROUND_HALF_UP
import dados2 as D2
q = lambda x, n='0.01': x.quantize(D(n), rounding=ROUND_HALF_UP)
def ind(ca, mg, k, hal, al):   # PRD 38.3: SB, T, t, V, m; None = não calculável
    sb = ca + mg + k; T = sb + hal if hal is not None else None; t = sb + al
    return sb, T, t, (100 * sb / T if T else None), (100 * al / t if t else None)
def nc(v1, v2, T, prnt): n = max(D(0), (v2 - v1) * T / 100); return n, n * 100 / prnt   # CAL-10: PRNT uma vez
print('AC-27', nc(D(40), D(60), D(5), D(80)))
K = lambda mg: D(mg) / D(391)   # K mg/dm³ → cmolc/dm³
for nome, a, v2, prnt in [('LAU-2043 T4 Z2', (D('3.90'), D('1.40'), K('31.28'), D('3.82'), D('0.10')), None, None),
                          ('LAU-2044 T4 20-40', (D('1.10'), D('0.50'), K('23.46'), D('3.00'), D('0.10')), None, None),
                          ('LAU-2050 C1 sem H+Al', (D('3.40'), D('1.10'), K('97.75'), None, D('0')), None, None),
                          ('LAU-2061 T1', (D('3.10'), D('1.25'), K('58.65'), D('3.00'), D('0')), 60, 85),
                          ('LAU-2063 T2', (D('1.25'), D('0.44'), K('136.85'), D('3.06'), D('0.30')), 60, 85),
                          ('LAU-2071 PV12', (D('2.90'), D('0.95'), K('78.20'), D('4.05'), D('0.20')), 70, 90),
                          ('LAU-2072 PV12 20-40', (D('0.30'), D('0.20'), K('31.28'), D('4.00'), D('0.60')), None, None),
                          ('LAU-2073 T7', (D('3.90'), D('1.30'), K('160.31'), D('2.89'), D('0')), 70, 85)]:
    sb, T, t, V, m = ind(*a)
    print(nome, 'K', q(a[2], '0.001'), 'SB', q(sb), 'T', q(T) if T else 'n/c', 't', q(t), 'V', q(V) if V else 'n/c',
          'm', q(m) if m is not None else 'n/c', ('NC100/dose t/ha', [q(x, '0.0001') for x in nc(V, D(v2), T, D(prnt))]) if v2 else '')
for s in ('S2627', 'LG2627'):
    for c in D2.CULTIVOS[s]:
        if c['local'] in ('T1-A', 'T1-B', 'T2', 'Pivô 12', 'C1', 'T7') and c['plano']:
            out = [(a['id'], a['nome'], str(D2.data_atividade(c, a)), [(p['prod'], p['dose'], p['un'], p['preco']) for p in a['prods']])
                   for a in D2.PLANO[c['plano']]['atividades'] if any(p['prod'] in ('KCl 60%', 'Calcário dolomítico filler', 'Gesso agrícola') for p in a['prods'])]
            print(s, c['id'], c['local'], c['area'], c['meta'], c['un_meta'], c['plano'], c['plantio'], out)
print('T2 DAP-60', dt.date(2026, 10, 18) - dt.timedelta(days=60), '· hoje+7', dt.date(2026, 9, 23) + dt.timedelta(days=7))
a = D('48.47'); print('PV12 calagem', a * 200, a * 200 * D('0.18'), '· gesso', a * 500, a * 500 * D('0.22'))
print('T2 calcário', D(298) * D('1.2'), D(298) * D('1.2') * 180, '· KCl T2', 298 * 120, 298 * 120 * D('2.4'),
      '· T1-A', 160 * 30, 160 * 30 * D('2.4'), '· T1-B', 152 * 30, 152 * 30 * D('2.4'), '· T7', D(42) * D('0.4'), D(42) * D('0.4') * 180)
print('KCl líquido S2627', 4800 + 4560 - 35760, (4800 + 4560 - 35760) * D('2.4'))
# revisão por contraexemplo (06/10/2026): estoque da OS-0502 no cenário, faixa de meta da R07 e R17 com um laudo sintético do T1 (V 50 %)
import cenario, quantidade as Q
lot = [(k, l['fisico'], l['reservado']) for k, l in cenario.seed()['lotes'].items() if k.startswith('Calcário dolomítico filler')]
print('OS-0502 lote', lot, '· precisa 2.000', Q.qtd(2000, 48.47), '· 1.800', Q.qtd(1800, 48.47))
print('metas R07 kg/ha', {c['local']: c['meta'] * 60 for c in D2.CULTIVOS['S2627'] if c['cultura'] == 'Soja' and c['plano']}, '· faixa 2.400–4.800')
print('R17 T1 V 50 %', [q(x, '0.0001') for x in nc(D(50), D(60), D('7.50'), D(85))], '→ T1-A e T1-B na S2627; nada na S27SF')
