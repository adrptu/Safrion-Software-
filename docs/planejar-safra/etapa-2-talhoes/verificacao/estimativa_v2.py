# -*- coding: utf-8 -*-
"""Fim estimado (R-04 d), pior caso P(o), folga 0/1/3, Colheita informada, Vincular ciclo e árvore depois de ações. Só leitura."""
import sys, copy
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from ocupacao_v2 import *
from trava_v2 import N, checa, aplica

def tab(sid, CU, nova=None, folga=1):
    CUx = copy.deepcopy(CU); CUx.setdefault('NOVA', [])
    return tabela(sid, CUx, nova or SAFS[sid], safras_com(nova), folga)
def resumo(L, b, faz='Santa Rita'):
    return '%s | chips %s | linhas %d' % (faixa_txt(b, L, sum(TAL[faz].values())), chips(L), sum(v['linhas'] for v in L.values()))

if __name__ == '__main__':
    CU = base(True)
    print('# R-04 (d) · candidatos: ciclo da cultivar × última atividade dos planos publicados da cultura')
    for o in ocupacoes(CU, safras_com()):
        if o['classe'] != 'estimado': continue
        c = o['plantio'] + td(CIC[(o['cult'], o['var'])]) if (o['cult'], o['var']) in CIC else None
        pl = {p: br(max(d for n, tp, d in atividades(o['plantio'], p) if tp != 'DATA')) for p in planos_da_cultura(o['cult'])}
        print('   %-3s %-5s %-5s plantio %s | ciclo %s | planos %s → estimado %s | núcleo %s | P %s' % (o['id'], o['faixa'], o['var'], br(o['plantio']), br(c), pl, br(o['fim']), br(o['nuc']), br(P(o))))

    print('\n# Folga 0, 1 e 3 (Livre a partir de; T1-B 20/02 e 21/02)')
    for f in (0, 1, 3):
        for nome, sid, nova in (('S27SF', 'S27SF', None), ('caso 5', 'NOVA', NOVAS['caso5'])):
            L, b = tab(sid, CU, nova, f)
            print('   folga=%d %-7s %s | %s' % (f, nome, faixa_txt(b, L, 1165), ' '.join('%s:%s' % (t, br(v['desde']) if v['area_livre'] > 0.005 else '—') for t, v in L.items() if t in ('T1', 'T2', 'T3', 'T4', 'P1', 'P2'))))
        for d in ('2027-02-20', '2027-02-21'):
            checa(CU, 'S27SF', N(local='T1-B', area=152, plantio=d), folga=f, rot='   folga=%d Milho T1-B %s' % (f, br(F(d))))

    print('\n# OC-R1 (a) · e5 sem colheita informada')
    CA = aplica(CU, 'S2526', muda=('e5', dict(colheita=None)))
    e5 = [o for o in ocupacoes(CA, safras_com()) if o['id'] == 'e5'][0]
    print('   e5 estimado até %s · núcleo %s · P %s' % (br(e5['fim']), br(e5['nuc']), br(P(e5))))
    L, b = tab('S2627', CA); print('   S2627 P2: %s | seq %s | %s' % (L['P2']['sit'], L['P2']['seq'], resumo(L, b)))
    checa(CA, 'S2627', muda=('c7', dict(plano='SOJA-AT')), rot='   c7 SOJA-AT (e5 sem colheita)')
    print('# OC-R1 (b) · milho sem plano no T4 da S27SF, plantio 20/03/2027; safra a partir de 01/08/2027')
    CB = aplica(CU, 'S27SF', N(id='mt', local='T4', tipo='Talhão inteiro', area=204, plantio='2027-03-20', plano=None))
    mt = [o for o in ocupacoes(CB, safras_com(NOVAS['ago27'])) if o['id'] == 'mt'][0]
    print('   mt estimado até %s · P %s' % (br(mt['fim']), br(P(mt))))
    L, b = tab('NOVA', CB, NOVAS['ago27']); v = L['T4']
    print('   ago/27 T4: %s · %s ha a partir de %s · visíveis %s' % (v['sit'], ha(v['area_livre']), br(v['desde']), [o['id'] for o in v['vis']]))
    s = safras_com(NOVAS['ago27']); CBx = copy.deepcopy(CB); CBx['NOVA'] = []
    checa(CBx, 'NOVA', N(id='sj', local='T4', tipo='Talhão inteiro', area=204, plantio='2027-08-05', cultura='Soja', variedade='58 W', plano=None), safs=s, rot='   ago/27 Soja sem plano T4 05/08/2027')
    print('# OC-R1 (c) regressão: com os dados atuais, S2627 e S27SF não mudam (ver saida_ocupacao_f1.txt)')

    print('\n# DONO-07 · Colheita prevista informada no c4 (10/02/2027) e no c6 (05/03/2027)')
    CC = aplica(CU, 'S2627', muda=('c4', dict(colheita='2027-02-10')))
    L, b = tab('S27SF', CC); print('   S27SF T4 %s %s ha a partir de %s | %s' % (L['T4']['sit'], ha(L['T4']['area_livre']), br(L['T4']['desde']), resumo(L, b)))
    print('# OC-12 · SOJA-AT no c6: P1 nas duas safras')
    CT = aplica(CU, 'S2627', muda=('c6', dict(plano='SOJA-AT')))
    for sid in ('S2627', 'S27SF'):
        L, b = tab(sid, CT); print('   %s P1: %s | %s' % (sid, L['P1']['sit'], resumo(L, b)))

    print('\n# OC-06 · Planejar T1 (T1-B 152 ha 21/02/2027) na S27SF')
    L, b = tab('S27SF', aplica(CU, 'S27SF', N(id='t1b', local='T1-B', area=152, plantio='2027-02-21'))); print('   ', resumo(L, b), '| T1', L['T1']['sit'])
    print('# OC-R4 · T4-A 100 ha 28/02/2027 (partest.py:132-137)')
    L, b = tab('S27SF', aplica(CU, 'S27SF', N(id='t4a', local='T4-A', area=100, plantio='2027-02-28')))
    v = L['T4']; print('   T4 %s · %s ha a partir de %s · desta safra %s · visíveis %s | %s' % (v['sit'], ha(v['area_livre']), br(v['desde']), [o['id'] for o in v['own']], [o['id'] for o in v['vis']], resumo(L, b)))
    print('# OC-R2 (a) · Planejar T3 96 ha 18/02/2027')
    L, b = tab('S27SF', aplica(CU, 'S27SF', N(id='t3', local='T3', tipo='Talhão inteiro', area=96, plantio='2027-02-18'))); print('   ', resumo(L, b), '| T3', L['T3']['sit'], [o['id'] for o in L['T3']['vis']])

    print('\n# R-24 Vincular ciclo · 2027/28 (T7 e C1) e Lagoa nova 2027/28')
    CV = copy.deepcopy(CU); CV['NOVA'] = []
    L, b = tab('NOVA', CV, NOVAS['2027/28']); print('   antes   ', resumo(L, b), '| Vincular', {t: v['vinc'] for t, v in L.items() if v['vinc']})
    vincular(CV, 'NOVA', 'c9')
    L, b = tab('NOVA', CV, NOVAS['2027/28']); print('   C1      ', resumo(L, b), '| Vincular', {t: v['vinc'] for t, v in L.items() if v['vinc']})
    vincular(CV, 'NOVA', 'c8')
    L, b = tab('NOVA', CV, NOVAS['2027/28']); print('   C1+T7   ', resumo(L, b))
    L2, b2 = tab('S2627', CV); print('   S2627 depois:', resumo(L2, b2), '| cultivos vinculados sem plano:', [c['id'] for c in CV['NOVA'] if not c['plano']])
    CL = copy.deepcopy(CU); CL['NOVA'] = []
    for c in CU['LG2627']: vincular(CL, 'NOVA', c['id'])
    L, b = tab('NOVA', CL, NOVAS['LG2728']); print('   Lagoa 2027/28 depois de vincular os 23:', resumo(L, b, 'Lagoa Grande'))
    L, b = tab('LG2627', CL); print('   LG2627 depois:', resumo(L, b, 'Lagoa Grande'))
