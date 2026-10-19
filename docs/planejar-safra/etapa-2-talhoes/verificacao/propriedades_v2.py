# -*- coding: utf-8 -*-
"""Propriedades do OC-U5 (amostra com semente fixa) sobre sequências de salvamentos. Só leitura.
Uso: python3 propriedades_v2.py [n_sequencias]"""
import sys, copy, random
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from ocupacao_v2 import *
from trava_v2 import N, aplica, checa, plantio_min

random.seed(20261005)
VAR = {'Soja': '58 W', 'Milho': 'Híbrido AG 8700', 'Feijão': 'Pérola'}
PL = {'Soja': ['SOJA-AT', 'SOJA-PD', None], 'Milho': ['MILHO-SF', None], 'Feijão': ['FEIJ-PV', None]}
SAFRAS_T = [('S27SF', None), ('NOVA', NOVAS['caso5']), ('NOVA', NOVAS['2027/28']), ('S2627', None)]
falhas = Counter(); n = 0; salvos = 0; travados = 0
quiet = lambda *a: None
for k in range(int(sys.argv[1]) if len(sys.argv) > 1 else 400):
    folga = random.choice([0, 1, 3])
    sid, nova = random.choice(SAFRAS_T); s = nova or SAFS[sid]; safs = safras_com(nova)
    CU = base(random.random() < 0.8); CU.setdefault('NOVA', [])
    for passo in range(3):
        t = random.choice(['T1', 'T2', 'T3', 'T4', 'P1', 'P2', 'T7']); T = TAL['Santa Rita'][t]
        cult = random.choice(list(VAR)); pid = random.choice(PL[cult])
        d = F(s['ini']) + td(random.randrange(0, max(1, (F(s['fim']) - F(s['ini'])).days - 150)))
        area = round(random.uniform(10, T), 2); inteiro = random.random() < 0.4
        nv = N(id='n%d' % passo, local=(t if inteiro else '%s-Z%d' % (t, passo)), tipo=('Talhão inteiro' if inteiro else 'Parcela'),
               area=(T if inteiro else area), plantio=d.isoformat(), cultura=cult, variedade=VAR[cult], plano=pid)
        tr, pe, o = checa(CU, sid, nv, folga=folga, safs=safs, pr=quiet); n += 1
        # simetria: a trava não depende da ordem
        occ2 = [x for x in ocupacoes(aplica(CU, sid, nv), safs, folga) if x['t'] == t]
        r1 = sorted(str(x[:3]) for x in avalia(occ2, T)[0]); r2 = sorted(str(x[:3]) for x in avalia(list(reversed(occ2)), T)[0])
        if [x.split(',')[0] for x in r1] != [x.split(',')[0] for x in r2]: falhas['trava depende da ordem'] += 1
        if tr: travados += 1; continue
        CU = aplica(CU, sid, nv); salvos += 1
        # invariante: no conjunto aceito nenhuma parte certa (núcleo) se cruza na mesma faixa com plano
        occ = ocupacoes(CU, safs, folga)
        m = [x for x in occ if x['t'] == t]
        for i, A in enumerate(m):
            for B in m[i + 1:]:
                if A['ciclo'] != B['ciclo'] and mesma_area(A, B) and (com_plano(A) or com_plano(B)) and intersec(A['plantio'], nuc_lib(A), B['plantio'], nuc_lib(B)):
                    falhas['núcleos cruzados aceitos'] += 1
        # soma diária das partes certas ≤ área (com plano)
        x = min(o2['plantio'] for o2 in m)
        for j in range(0, 400, 3):
            nu = [o2 for o2 in m if nuc_ativo(o2, x + td(j))]
            if sum(o2['area'] for o2 in nu) > T + 0.005 and any(com_plano(o2) for o2 in nu): falhas['soma certa > área aceita'] += 1; break
        for o2 in occ:
            if o2['classe'] == 'estimado' and P(o2) < o2['fim']: falhas['P < fim estimado'] += 1
            if o2['classe'] == 'perene' and P(o2) != INF: falhas['perene com fim'] += 1
    # faixa e chips
    L, b = tabela(sid, CU, s, safs, folga)
    tot = sum(TAL['Santa Rita'].values())
    if abs(sum(b.values()) - tot) > 0.01: falhas['faixa ≠ total'] += 1
    if sum(v for k2, v in chips(L).items() if k2 != 'Todas') != chips(L)['Todas']: falhas['chips ≠ Todas'] += 1
    if any(v['conf'] < -0.005 or v['livre'] < -0.005 for v in L.values()): falhas['Livre/A conferir < 0'] += 1
    # PlantioMin: aceito sem trava nem pendência; o dia anterior (quando >= base) tem trava ou pendência
    if k % 8 == 0:
        t = random.choice(['T1', 'T3', 'P2']); pid = random.choice(['SOJA-AT', 'MILHO-SF'])
        cult = 'Soja' if pid.startswith('SOJA') else 'Milho'
        nv = N(id='pm', local=t, tipo='Talhão inteiro', area=TAL['Santa Rita'][t], cultura=cult, variedade=VAR[cult], plano=pid)
        v = L[t]
        if v['area_livre'] > TAL['Santa Rita'][t] - 0.005 and v['desde']:
            base_d = v['desde'] + td(antecedencia(pid))
            pm = plantio_min(CU, sid, nv, v['desde'].isoformat(), folga, safs)
            if pm:
                tr, pe, _ = checa(CU, sid, dict(nv, plantio=pm.isoformat()), folga=folga, safs=safs, pr=quiet)
                if tr or pe: falhas['PlantioMin com trava/pendência'] += 1
                if pm > base_d:
                    tr, pe, _ = checa(CU, sid, dict(nv, plantio=(pm - td(1)).isoformat()), folga=folga, safs=safs, pr=quiet)
                    if not tr and not pe: falhas['PlantioMin − 1 também passa'] += 1
# DATA fora da safra nunca muda início nem fim (OC-R8)
for d in ('2027-09-15', '2027-11-01', '2028-02-01'):
    for pid, cult, var in (('CAFE-AR', 'Café', 'Catuaí 144'), ('MAMAO-F', 'Mamão Formosa', 'Formosa')):
        o = mk(N(id='x', local='T3', tipo='Talhão inteiro', area=96, plantio=d, cultura=cult, variedade=var, plano=pid), 'NOVA', NOVAS['2027/28'], 1)
        if o['ini'] != F(d): falhas['DATA fora mudou o início'] += 1
# mesmo ciclo em duas safras não conflita (R-07)
CV = base(True); CV['NOVA'] = []; vincular(CV, 'NOVA', 'c9'); vincular(CV, 'NOVA', 'c8')
if any(avalia([x for x in ocupacoes(CV, safras_com(NOVAS['2027/28'])) if x['t'] == t], TAL['Santa Rita'][t])[0] for t in ('T7', 'C1')): falhas['ciclo vinculado conflita'] += 1
print('salvamentos tentados %d · aceitos %d · recusados %d | falhas %s' % (n, salvos, travados, dict(falhas) or 'nenhuma'))
