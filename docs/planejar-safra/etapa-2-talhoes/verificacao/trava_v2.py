# -*- coding: utf-8 -*-
"""Trava (R-14), pendência e aviso (R-15), plantio mínimo (R-17) e mensagens M1-M4 da especificação v2. Só leitura.
Uso: python3 trava_v2.py [folga]"""
import sys, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from ocupacao_v2 import *

def N(**k):
    return dict(dict(id='nv', fazenda='Santa Rita', tipo='Parcela', cultura='Milho', variedade='Híbrido AG 8700', meta=170, un_meta='sc/ha',
                     plano='MILHO-SF', colheita=None, ro=False), **k)

def aplica(CU, sid, novo=None, muda=None):
    CU = copy.deepcopy(CU); CU.setdefault(sid, [])
    if muda:
        for c in CU[sid]:
            if c['id'] == muda[0]: c.update(muda[1])
    if novo: CU[sid] = CU[sid] + [novo]
    return CU

def checa(CU, sid, novo=None, muda=None, folga=1, safs=None, rot='', pr=print):
    """Salvar: travas que envolvem o alvo, pendências novas e aviso de saída estimada."""
    safs = safs or safras_com()
    alvo = (novo or {}).get('id') or muda[0]
    CU2 = aplica(CU, sid, novo, muda)
    occ = ocupacoes(CU2, safs, folga)
    o = [x for x in occ if x['id'] == alvo][0]; T = TAL[o['faz']][o['t']]
    mesmo = [x for x in occ if x['faz'] == o['faz'] and x['t'] == o['t']]
    trav, pe = avalia(mesmo, T, alvo)
    soma = sum(x['area'] for x in mesmo if sid in x['safs'])        # regra de hoje (safra.js:527-537): área desta safra ≤ área do talhão
    if soma > T + 0.005: trav = [('safra', sid, alvo, o['plantio'], round(soma, 2))] + trav
    _, pe0 = avalia([x for x in ocupacoes(CU, safs, folga) if x['faz'] == o['faz'] and x['t'] == o['t']], T)
    novas = {k: [p for p in v if p not in pe0.get(k, [])] for k, v in pe.items()}
    novas = {k: v for k, v in novas.items() if v}
    aviso = [(y['id'], br(y['fim'])) for y in mesmo if y is not o and mesma_area(o, y) and y['classe'] in ('estimado', 'semdata')
             and y['ini'] < o['ini'] < liberacao(y, 'pior')]
    txt = ('TRAVA ' + str([tuple(br(x) if hasattr(x, 'year') else x for x in t) for t in trav])) if trav else 'salva'
    pend = {k: [(p[0], p[1], br(p[2]) + '..' + br(p[3]), '%d dia(s)' % p[4]) for p in v] for k, v in novas.items()}
    pr('%-52s início %s → Ocupa até %s (%s) | %s%s%s%s' % (rot, br(o['ini']), br(o['fim']), ROT[o['classe']], txt,
       (' | pendência ' + str(pend)) if pend else '', (' | aviso saída estimada ' + str(aviso)) if aviso and not trav else '',
       (' | aviso ' + str(o['avisos'])) if o['avisos'] else ''))
    return trav, novas, o

def plantio_min(CU, sid, novo, desde, folga=1, safs=None, ate=None):
    """R-17 PlantioMin: menor plantio >= desde + antecedência do plano sem trava nem pendência contra qualquer ocupação do talhão."""
    safs = safs or safras_com(); s = safs[sid]
    d = F(desde) + td(antecedencia(novo['plano']) if novo.get('plano') else 0)
    fim = ate or F(s['fim'])
    while d <= fim:
        tr, pe, _ = checa(CU, sid, None, None, folga, safs, pr=lambda *a: None) if False else (None, None, None)
        nv = dict(novo, plantio=d.isoformat())
        if novo['id'] in [c['id'] for c in CU.get(sid, [])]: t2, p2, _ = checa(CU, sid, muda=(novo['id'], dict(plantio=d.isoformat(), plano=novo.get('plano'))), folga=folga, safs=safs, pr=lambda *a: None)
        else: t2, p2, _ = checa(CU, sid, nv, folga=folga, safs=safs, pr=lambda *a: None)
        if not t2 and not p2: return d
        d += td(1)
    return None

def msg_M1(CU, novo, sid, folga=1):
    """OC-R10: período = interseção; máximo = área − ocupação de fora no pior dia."""
    occ = ocupacoes(aplica(CU, sid, novo), safras_com(), folga)
    o = [x for x in occ if x['id'] == novo['id']][0]; T = TAL[o['faz']][o['t']]
    outros = [x for x in occ if x['t'] == o['t'] and x is not o and intersec(o['ini'], liberacao(o, 'est'), x['ini'], liberacao(x, 'est'))]
    ini = max([o['ini']] + [x['ini'] for x in outros]); fim = min([o['fim']] + [x['fim'] for x in outros])
    pior = max(sum(x['area'] for x in outros if x['ini'] <= ini + td(k) < liberacao(x, 'est')) for k in range((fim - ini).days + 1))
    return 'De %s a %s, %s ha de %s estão com %s. Máximo %s ha nesse período.' % (br(ini), br(fim), ha(pior), o['t'], '+'.join(x['id'] for x in outros), ha(T - pior))

if __name__ == '__main__':
    folga = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print('# folga', folga)
    for rot, com in (('COM e4/e5', True), ('SEM e4/e5', False)):
        CU = base(com); print('\n########', rot)
        print('# Dados atuais: travas e pendências (Santa Rita e Lagoa)')
        occ = ocupacoes(CU, safras_com(), folga); achou = False
        for faz in ('Santa Rita', 'Lagoa Grande'):
            for t, T in TAL[faz].items():
                tr, pe = avalia([x for x in occ if x['faz'] == faz and x['t'] == t], T)
                if tr or pe: achou = True; print('   ', faz, t, tr, pe)
        print('   nenhuma' if not achou else '')
        print('# R-17 sucessão (S27SF)')
        for d in ('2027-02-21', '2027-02-20', '2027-02-15'):
            checa(CU, 'S27SF', N(local='T1-B', area=152, plantio=d), folga=folga, rot='Milho T1-B 152 ha %s' % br(F(d)))
        checa(CU, 'S27SF', N(local='T1-C', area=152, plantio='2027-02-15'), folga=folga, rot='Milho T1-C 152 ha 15/02/2027')
        print('# M1 (OC-07) e OC-R10')
        nv = N(local='T1', tipo='Talhão inteiro', area=312, plantio='2027-02-21')
        checa(CU, 'S27SF', nv, folga=folga, rot='Milho T1 312 ha 21/02/2027')
        print('   M1:', msg_M1(CU, nv, 'S27SF', folga))
        checa(CU, 'S27SF', N(local='T1', tipo='Talhão inteiro', area=312, plantio='2027-07-11'), folga=folga, rot='Milho T1 312 ha 11/07/2027')
        print('# OC-R5 (núcleo pelo ciclo mínimo) · T3 sobre o c5 (soja 22/10/2026, sem plano, núcleo até 10/02/2027)')
        for d in ('2026-10-23', '2027-01-10', '2027-02-10', '2027-02-11', '2027-02-17', '2027-02-18'):
            checa(CU, 'S27SF', N(id='m3', local='T3', tipo='Talhão inteiro', area=96, plantio=d), folga=folga, rot='Milho MILHO-SF T3 %s' % br(F(d)))
        checa(CU, 'S27SF', N(id='m3', local='T3', tipo='Talhão inteiro', area=96, plantio='2026-10-23', plano=None), folga=folga, rot='Milho SEM plano T3 23/10/2026')
        CI = aplica(CU, 'S2627', muda=('c5', dict(colheita='2027-01-20')))
        checa(CI, 'S27SF', N(id='m3', local='T3', tipo='Talhão inteiro', area=96, plantio='2027-01-21'), folga=folga, rot='c5 colheita 20/01/2027 → milho 21/01/2027')
        checa(CI, 'S27SF', N(id='m3', local='T3', tipo='Talhão inteiro', area=96, plantio='2027-01-20'), folga=folga, rot='c5 colheita 20/01/2027 → milho 20/01/2027')
        print('# M3/OC-09 · lote SOJA-AT e SOJA-PD em c4, c5, c6, c7 (S2627)')
        for p in ('SOJA-AT', 'SOJA-PD'):
            for cid in ('c4', 'c5', 'c6', 'c7'): checa(CU, 'S2627', muda=(cid, dict(plano=p)), folga=folga, rot='%s %s' % (cid, p))
        c7 = [c for c in CU['S2627'] if c['id'] == 'c7'][0]
        if com:
            for p in ('SOJA-AT', 'SOJA-PD'):
                print('     PlantioMin do c7 com %s (desde a liberação do e5 16/11/2026): %s' % (p, br(plantio_min(CU, 'S2627', dict(c7, plano=p), '2026-11-16', folga, ate=F('2027-01-31')))))
        print('   demanda do P2 (80 ha): SOJA-AT R$ %.2f · SOJA-PD R$ %.2f' % (80 * custo_ha('SOJA-AT'), 80 * custo_ha('SOJA-PD')))
        print('# REG-02 negativo: colheita REAL do e5 em 20/11/2026')
        if com:
            CR = aplica(CU, 'S2526', muda=('e5', dict(colheita_real='2026-11-20')))
            checa(CR, 'S2627', muda=('c7', dict(plano='SOJA-AT')), folga=folga, rot='c7 SOJA-AT (e5 colhido de fato em 20/11)')
            print('     PlantioMin do c7 SOJA-AT depois da colheita real: %s' % br(plantio_min(CR, 'S2627', dict(c7, plano='SOJA-AT'), (F('2026-11-20') + td(folga)).isoformat(), folga, ate=F('2027-01-31'))))
        print('# M4 · plantio do c1 em 30/10/2026')
        checa(CU, 'S2627', muda=('c1', dict(plantio='2026-10-30')), folga=folga, rot='c1 plantio 30/10/2026')
        print('# OC-11 · T3 na S27SF com milho em 11/02/2027, depois SOJA-AT/PD no c5')
        m = N(id='m3', local='T3', tipo='Talhão inteiro', area=96, plantio='2027-02-11')
        CT = aplica(CU, 'S27SF', m)
        for p in ('SOJA-AT', 'SOJA-PD'): checa(CT, 'S2627', muda=('c5', dict(plano=p)), folga=folga, rot='depois: c5 %s' % p)
        print('# OC-R2 (a) · Planejar T3 com o padrão do painel e depois o lote SOJA-AT/PD')
        pm = plantio_min(CU, 'S27SF', N(id='m3', local='T3', tipo='Talhão inteiro', area=96), '2027-02-18', folga)
        print('   PlantioMin MILHO-SF no T3 (Livre a partir de 18/02/2027):', br(pm))
        CT = aplica(CU, 'S27SF', N(id='m3', local='T3', tipo='Talhão inteiro', area=96, plantio=pm.isoformat()))
        for p in ('SOJA-AT', 'SOJA-PD'): checa(CT, 'S2627', muda=('c5', dict(plano=p)), folga=folga, rot='T3 %s · c5 %s' % (br(pm), p))
        print('# OC-R2 (b) · Planejar P2 com o padrão e depois SOJA-AT no c7; janela do M3')
        pm2 = plantio_min(CU, 'S27SF', N(id='m2', local='P2', tipo='Talhão inteiro', area=80), '2027-03-24', folga)
        print('   PlantioMin MILHO-SF no P2 (Livre a partir de 24/03/2027):', br(pm2))
        CP = aplica(CU, 'S27SF', N(id='m2', local='P2', tipo='Talhão inteiro', area=80, plantio=pm2.isoformat()))
        checa(CP, 'S2627', muda=('c7', dict(plano='SOJA-AT')), folga=folga, rot='P2 %s · c7 SOJA-AT 25/11/2026' % br(pm2))
        for p, dd in (('SOJA-AT', '2026-12-06'), ('SOJA-PD', '2026-12-01')):
            checa(CP, 'S2627', muda=('c7', dict(plano=p, plantio=dd)), folga=folga, rot='P2 %s · c7 %s %s' % (br(pm2), p, br(F(dd))))
        if com:
            print('   janela do c7 SOJA-AT com P2 em %s: %s' % (br(pm2), br(plantio_min(CP, 'S2627', dict(c7, plano='SOJA-AT'), '2026-11-16', folga, ate=F('2027-01-31')))))
            fim_c7 = colheita = F('2026-12-06') + td(118)
            print('   saída dupla: c7 SOJA-AT em 06/12/2026 termina em %s → milho do P2 a partir de %s' % (br(fim_c7), br(fim_c7 + td(folga))))
        print('# DONO-05 · PlantioMin por plano (S27SF T1-B, Livre a partir de 21/02/2027)')
        for cult, var, pid in (('Soja', '62 X', 'SOJA-AT'), ('Soja', '62 X', 'SOJA-PD'), ('Milho', 'Híbrido AG 8700', 'MILHO-SF'), ('Feijão', 'Pérola', 'FEIJ-PV')):
            nv = N(local='T1-B', area=152, cultura=cult, variedade=var, plano=pid)
            print('   %-9s PlantioMin %s' % (pid, br(plantio_min(CU, 'S27SF', nv, '2027-02-21', folga))))
        checa(CU, 'S27SF', N(local='T1-B', area=152, cultura='Soja', variedade='62 X', plano='SOJA-AT', plantio='2027-03-12'), folga=folga, rot='SOJA-AT T1-B 12/03/2027')
        checa(CU, 'S27SF', N(local='T1-B', area=152, cultura='Soja', variedade='62 X', plano='SOJA-AT', plantio='2027-03-13'), folga=folga, rot='SOJA-AT T1-B 13/03/2027')
        print('# OC-R8 · DATA fora da safra (2027/28)')
        s28 = safras_com(NOVAS['2027/28']); CN = copy.deepcopy(CU); CN['NOVA'] = []
        checa(CN, 'NOVA', N(id='cf', local='T3', tipo='Talhão inteiro', area=96, plantio='2027-11-01', cultura='Café', variedade='Catuaí 144', plano='CAFE-AR'), folga=folga, safs=s28, rot='Café CAFE-AR T3 01/11/2027')
        checa(CN, 'NOVA', N(id='mf', local='P2', tipo='Talhão inteiro', area=80, plantio='2027-11-01', cultura='Mamão Formosa', variedade='Formosa', plano='MAMAO-F'), folga=folga, safs=s28, rot='Mamão MAMAO-F P2 01/11/2027')
        print('# Perene bloqueia: milho no T7 na 2027/28; R-07 vincular C1 não conflita')
        checa(CN, 'NOVA', N(id='mt7', local='T7', tipo='Talhão inteiro', area=42, plantio='2027-10-01'), folga=folga, safs=s28, rot='Milho T7 01/10/2027')
        CV = copy.deepcopy(CN); v = vincular(CV, 'NOVA', 'c9')
        tr, pe = avalia([x for x in ocupacoes(CV, s28, folga) if x['t'] == 'C1'], 38.0)
        print('   vincular c9 na 2027/28: ocupações do ciclo %d · travas %s · pendências %s' % (sum(1 for x in ocupacoes(CV, s28, folga) if x['ciclo'] == 'c9'), tr, pe))
        print('   CAFE-AR no ciclo vinculado: atividades de data fixa fora da 2027/28 =', datas_validas(F('2019-01-15'), 'CAFE-AR', F('2027-09-01'), F('2028-08-31'))[1])
