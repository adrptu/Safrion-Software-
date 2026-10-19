# -*- coding: utf-8 -*-
"""Espelho de verificação das regras de saf2/v2/ESPECIFICACAO.md §4 (R-01 a R-26).
Só lê gen37 (/home/user/sp-tab5/tools/prototipo/v37/gen37, HEAD 884620c). Não grava nada no repositório.
Não é o ocupacao.js/ocupacao.py do PR: prova os números publicados na especificação.
Uso: python3 ocupacao_v2.py [folga]   (folga padrão 1 = dia seguinte, R-06)"""
import sys, copy, datetime as dt
from collections import Counter
G = '/home/user/sp-tab5/tools/prototipo/v37/gen37'
sys.path.insert(0, G)
import dados as D, dados2 as D2, dados_cad as DC, dados_lagoa_safra as DL
from areas.cadastros import CULTIVARES

F = dt.date.fromisoformat
INF = dt.date(9999, 12, 31)
HOJE = dt.date(2026, 9, 23)                                              # dados2.HOJE
def td(n): return dt.timedelta(days=n)
def br(d):
    if d is None: return 'sem data'
    return 'sem fim' if d == INF else d.strftime('%d/%m/%Y')
def ha(x): return ('%.2f' % x).rstrip('0').rstrip('.')
def mais(d, n): return INF if d == INF else d + td(n)

CLASSE = {c[0]: c[2] for c in DC.CULTURAS}                              # dados_cad.py:31-32
CIC = {(c, v): d for _, c, v, tp, d, _ in CULTIVARES if d != ''}        # areas/cadastros.py:406-408
CICMIN, CICMAX = {}, {}
for (c, v), d in CIC.items():
    CICMIN[c] = min(CICMIN.get(c, 9999), d); CICMAX[c] = max(CICMAX.get(c, 0), d)
TAL = {'Santa Rita': {t: float(a) for t, a, *_ in D.TALHOES}, 'Boa Vista': {'B1': 120.0},
       'Lagoa Grande': {k: float(v) for k, v in DL.TALHOES.items()}}
SAFS = {s['id']: dict(s) for s in D2.SAFRAS}
def NV(nome, ini, fim, faz='Santa Rita'): return dict(id='NOVA', nome=nome, ini=ini, fim=fim, fazenda=faz, estado='Rascunho', ro=False)
NOVAS = {'caso5': NV('Nova (caso 5)', '2027-01-10', '2027-08-30'), '2027/28': NV('Nova 2027/28', '2027-09-01', '2028-08-31'),
         'BoaVista': NV('Nova Boa Vista', '2026-09-01', '2027-08-31', 'Boa Vista'),
         'LG2728': NV('Nova Lagoa 2027/28', '2027-09-01', '2028-08-31', 'Lagoa Grande'),
         'LG2627b': NV('Nova Lagoa 2026/27', '2026-09-01', '2027-08-31', 'Lagoa Grande'),
         'ago27': NV('Nova a partir de 01/08/2027', '2027-08-01', '2028-07-31')}
# lavouras em campo (§6.2): plantio observado (antes de HOJE), colheita prevista informada
E45 = [dict(id='e4', fazenda='Santa Rita', local='P1', tipo='Talhão inteiro', cultura='Feijão', variedade='BRS Estilo', area=95, plantio='2026-07-05',
            meta=48, un_meta='sc/ha', plano=None, colheita='2026-10-10', ro=True, origem='lavoura em campo'),
       dict(id='e5', fazenda='Santa Rita', local='P2', tipo='Talhão inteiro', cultura='Milho', variedade='Híbrido AG 8700', area=80, plantio='2026-08-10',
            meta=180, un_meta='sc/ha', plano=None, colheita='2026-11-15', ro=True, origem='lavoura em campo')]

def base(com_e45=True):
    CU = copy.deepcopy(D2.CULTIVOS)
    if com_e45: CU['S2526'] = CU['S2526'] + copy.deepcopy(E45)
    return CU
def safras_com(nova=None):
    s = dict(SAFS)
    if nova: s['NOVA'] = dict(nova)
    return s

# ---------- planos ----------
def planos_da_cultura(cult): return [p['id'] for p in D2.PLANOS if p['cultura'] == cult and p['estado'] == 'Publicado']
def antecedencia(pid):
    """Maior antecedência do plano (dias antes do plantio), pelos DAP negativos."""
    return max([0] + [-a['g']['dias'] for a in D2.PLANO[pid]['atividades'] if a['g']['tipo'] == 'DAP' and a['g']['dias'] < 0])
def atividades(plantio, pid, colheita=None):
    c = dict(plantio=plantio.isoformat(), plano=pid, colheita=colheita)
    return [(a['nome'], a['g']['tipo'], D2.data_atividade(c, a)) for a in D2.PLANO[pid]['atividades']]
def custo_ha(pid): return sum(p['dose'] * p['preco'] for a in D2.PLANO[pid]['atividades'] for p in a['prods'])

def datas_validas(pl, pid, safini, safim, colh=None):
    """R-03/R-04 (OC-R8): DATA só conta dentro da safra do cultivo e a partir de plantio − antecedência; o resto vira aviso."""
    ok, fora = [], []
    for n, tp, d in atividades(pl, pid, colh):
        if tp == 'DATA' and not (safini <= d <= safim and d >= pl - td(antecedencia(pid))): fora.append((n, d))
        else: ok.append((n, tp, d))
    return ok, fora

def fim_estimado(cult, var, pl):
    """R-04 (d) (OC-R2): plantio + o maior entre o ciclo da cultivar (CD-02) e a última atividade relativa dos planos publicados da cultura."""
    cands = []
    if (cult, var) in CIC: cands.append(pl + td(CIC[(cult, var)]))
    for pid in planos_da_cultura(cult):
        ds = [d for n, tp, d in atividades(pl, pid) if tp != 'DATA']
        if ds: cands.append(max(ds))
    return max(cands) if cands else None

# ---------- ocupação ----------
def tal_de(c): return c['local'] if c['tipo'] != 'Parcela' else c['local'].rsplit('-', 1)[0]
def mk(c, sid, s, folga):
    pid = c.get('plano'); pl = F(c['plantio'])
    o = dict(id=c['id'], ciclo=c.get('ciclo') or c['id'], saf=sid, safs=[sid], faz=c['fazenda'], t=tal_de(c), faixa=c['local'], tipo=c['tipo'],
             area=float(c['area']), cult=c['cultura'], var=c['variedade'], plantio=pl, plano=pid, safini=F(s['ini']), safim=F(s['fim']),
             colh_inf=(F(c['colheita']) if c.get('colheita') else None), colh_real=(F(c['colheita_real']) if c.get('colheita_real') else None),
             origem=c.get('origem'), avisos=[], folga=folga)
    o['ini'] = pl
    if pid:
        ok, fora = datas_validas(pl, pid, o['safini'], o['safim'], c.get('colheita'))
        o['ini'] = min([pl] + [d for n, tp, d in ok if tp in ('DAP', 'DATA')])
        if fora: o['avisos'].append(('datas_fixas', pid, fora[0][1]))
        dfim = max([pl] + [d for n, tp, d in ok] + ([o['colh_inf']] if o['colh_inf'] else []))
    if CLASSE[o['cult']] == 'Perene': o['fim'], o['classe'] = INF, 'perene'
    elif o['colh_real']: o['fim'], o['classe'] = o['colh_real'], 'observado'
    elif pid: o['fim'], o['classe'] = dfim, 'plano'
    elif o['colh_inf']: o['fim'], o['classe'] = o['colh_inf'], 'informada'
    else:
        e = fim_estimado(o['cult'], o['var'], pl)
        o['fim'], o['classe'] = (e, 'estimado') if e else (None, 'semdata')
    # núcleo (R-14, OC-R5): parte certa da ocupação
    cm = CICMIN.get(o['cult'])
    if o['classe'] == 'perene': o['nuc'] = INF
    elif o['classe'] == 'observado': o['nuc'] = o['colh_real']
    elif cm: o['nuc'] = min(o['fim'] or INF, pl + td(cm - 1))
    else: o['nuc'] = pl
    return o

ROT = {'perene': 'Perene', 'observado': 'Observado', 'plano': 'Pelo plano', 'informada': 'Colheita informada', 'estimado': 'Estimado (ciclo)', 'semdata': 'Sem ciclo'}

def P(o):
    """OC-R1: fim no pior caso."""
    if o['classe'] == 'perene': return INF
    if o['classe'] in ('plano', 'informada', 'observado'): return o['fim']
    if o['classe'] == 'estimado': return max(o['safim'], o['fim'])
    mc = CICMAX.get(o['cult'])
    return max(o['safim'], o['plantio'] + td(mc)) if mc else INF
def ocupa_ate(o, modo):
    if modo == 'pior': return P(o)
    if o['classe'] == 'semdata': return o['plantio']             # sem estimativa: só o dia de início
    return o['fim']
def liberacao(o, modo):
    """R-06/OC-R9: Livre a partir de = Ocupa até + folga (folga 0 = mesmo dia da colheita)."""
    return mais(ocupa_ate(o, modo), o['folga'])
def ativo(o, x, modo): return o['ini'] <= x < liberacao(o, modo) or (o['ini'] == x)
def nuc_lib(o): return mais(o['nuc'], o['folga'])
def nuc_ativo(o, x): return o['plantio'] <= x < nuc_lib(o) or o['plantio'] == x

def mesma_area(a, b): return a['faixa'] == b['faixa'] or a['tipo'] != 'Parcela' or b['tipo'] != 'Parcela'
def com_plano(o): return bool(o['plano']) or o['classe'] == 'perene'

def ocupacoes(CU, safs, folga=1):
    recs, vistos = [], {}
    for sid, lst in CU.items():
        s = safs.get(sid)
        if not s: continue
        for c in lst:
            o = mk(c, sid, s, folga)
            if o['ciclo'] in vistos: vistos[o['ciclo']]['safs'].append(sid); continue   # R-07
            vistos[o['ciclo']] = o; recs.append(o)
    return recs

def intersec(a0, a1, b0, b1):
    """Dias de [a0,a1) ∩ [b0,b1)."""
    x0, x1 = max(a0, b0), min(a1, b1)
    return (x0, x1) if x0 < x1 else None

def avalia(occs, T, alvo=None):
    """R-14 trava e R-15 pendência entre ocupações de um talhão. Pendência fica na de plantio mais tardio.
    Devolve (travas, pendencias). trava = (tipo, a, b, dia); pendência[id] = [(tipo, causa, dia_ini, dia_fim, ndias)]."""
    trav, pend = [], {}
    oc = sorted(occs, key=lambda o: (o['plantio'], o['id']))
    for i, A in enumerate(oc):
        for B in oc[i + 1:]:
            if A['ciclo'] == B['ciclo']: continue
            if alvo and alvo not in (A['id'], B['id']): continue
            if mesma_area(A, B):
                # observado (REG-02 a): atividade antes da colheita real registrada
                for X, Y in ((A, B), (B, A)):
                    if Y['classe'] == 'observado' and intersec(X['ini'], liberacao(X, 'est'), Y['plantio'], nuc_lib(Y)) and X['plantio'] >= Y['plantio']:
                        trav.append(('observado', Y['id'], X['id'], max(X['ini'], Y['plantio'])))
                # núcleo (OC-R5): parte certa se cruza, com plano em uma das duas (ou perene)
                if (com_plano(A) or com_plano(B)) and intersec(A['plantio'], nuc_lib(A), B['plantio'], nuc_lib(B)):
                    trav.append(('faixa', A['id'], B['id'], B['plantio']))
                    continue
                # previsão (R-15): cruzam pelos fins previstos/estimados
                kind = {'plano': 'prevista', 'informada': 'prevista', 'observado': 'prevista', 'estimado': 'provavel', 'semdata': 'naoconf'}.get(A['classe'])
                if kind:
                    fimA = liberacao(A, 'pior' if kind == 'naoconf' else 'est')
                    r = intersec(A['ini'], fimA, B['ini'], liberacao(B, 'est'))
                    if r: pend.setdefault(B['id'], []).append((kind, A['id'], r[0], r[1] - td(1), (r[1] - r[0]).days))
    # soma diária acima da área (faixas diferentes)
    if occs:
        d0 = min(o['ini'] for o in occs); d1 = max(min(liberacao(o, 'est'), d0 + td(900)) for o in occs)
        x = d0; vis_t, vis_p = set(), {}
        while x <= d1:
            nu = [o for o in occs if nuc_ativo(o, x)]
            if sum(o['area'] for o in nu) > T + 0.005 and any(com_plano(o) for o in nu) and not any(mesma_area(a, b) and a['ciclo'] != b['ciclo'] for k2, a in enumerate(nu) for b in nu[k2 + 1:]):
                last = max(nu, key=lambda o: (o['plantio'], o['id']))
                if not alvo or alvo in [o['id'] for o in nu]:
                    k = ('soma', '+'.join(sorted(o['id'] for o in nu if o is not last)), last['id'])
                    if k not in vis_t: vis_t.add(k); trav.append(('soma', k[1], last['id'], x, round(sum(o['area'] for o in nu), 2)))
            else:
                pv = [o for o in occs if o['ini'] <= x < liberacao(o, 'est')]
                if sum(o['area'] for o in pv) > T + 0.005 and not any(mesma_area(a, b) and a['ciclo'] != b['ciclo'] for k2, a in enumerate(pv) for b in pv[k2 + 1:]):
                    last = max(pv, key=lambda o: (o['plantio'], o['id']))
                    key = (last['id'], '+'.join(sorted(o['id'] for o in pv if o is not last)))
                    vis_p.setdefault(key, []).append(x)
            x += td(1)
        for (lid, causa), dias in vis_p.items():
            if alvo and alvo != lid and alvo not in causa.split('+'): continue
            pend.setdefault(lid, []).append(('soma', causa, dias[0], dias[-1], len(dias)))
    return trav, pend

# ---------- tabela da etapa 2 ----------
def tabela(sid, CU, safra, safs, folga=1, occ=None):
    a, b = F(safra['ini']), F(safra['fim']); faz = safra['fazenda']
    occ = [o for o in (occ or ocupacoes(CU, safs, folga)) if o['faz'] == faz]
    linhas = {}; band = dict(nesta=0.0, livre=0.0, conf=0.0, perene=0.0, ocup=0.0)
    for t, T in TAL[faz].items():
        own = [o for o in occ if o['t'] == t and sid in o['safs']]
        fora = [o for o in occ if o['t'] == t and sid not in o['safs'] and o['ini'] <= b and liberacao(o, 'pior') > a]
        A = sum(o['area'] for o in own)
        dias = [a + td(i) for i in range((b - a).days + 1)]
        def mfirst(modo):
            free = [T - A - sum(o['area'] for o in fora if o['ini'] <= x < liberacao(o, modo)) for x in dias]
            cur, m = 1e18, [0] * len(dias)
            for i in range(len(dias) - 1, -1, -1): cur = min(cur, free[i]); m[i] = cur
            for i, v in enumerate(m):
                if v > 0.005: return round(v, 2), dias[i]
            return 0.0, None
        Lp, dp = mfirst('pior'); Le, de = mfirst('est')
        fix = [o['id'] for o in fora if o['classe'] in ('estimado', 'semdata') and dp is not None and dp == liberacao(o, 'pior')]
        if fix: livre, conf, desde = 0.0, max(Le, Lp), de
        else: livre, conf, desde = Lp, round(max(0.0, Le - Lp), 2), (dp if Lp > 0.005 else de)
        tr, pe = avalia(own + fora, T)
        tr_own = [x for x in tr]
        pend_own = {k: v for k, v in pe.items() if k in [o['id'] for o in own] or any(p[1] in [o['id'] for o in own] for p in v)}
        seq = []
        for x in own + fora:                                        # OC-R11: sucessão a conferir, nos dois sentidos
            if x['classe'] not in ('estimado', 'semdata'): continue
            for y in own + fora:
                if y is x or ((x in own) == (y in own)) or not mesma_area(x, y): continue
                if x['ini'] < y['ini'] < liberacao(x, 'pior'): seq.append((x['id'], y['id']))
        if tr_own: sit = 'Sobreposição'
        elif conf > 0.005 or seq or pend_own: sit = 'A conferir'
        elif livre > 0.005: sit = 'Livre'
        elif own: sit = 'Planejado'
        elif any(o['classe'] == 'perene' for o in fora): sit = 'Perene'
        else: sit = 'Ocupado'
        # R-12 (OC-R4 + REG-05): visíveis
        nomes = {o['faixa'] for o in own}; inteiro = any(o['tipo'] != 'Parcela' for o in own)
        adj = set()
        for x in own:
            ant = [o for o in fora if mesma_area(o, x) and o['ini'] < x['ini']]
            suc = [o for o in fora if mesma_area(o, x) and o['ini'] > x['ini']]
            if ant: adj.add(max(ant, key=lambda o: o['ini'])['id'])
            if suc: adj.add(min(suc, key=lambda o: o['ini'])['id'])
        vis = [o for o in fora if not (o['faixa'] in nomes or inteiro) or o['id'] in adj]
        # §3.2 (DONO-08): folha com 0 ou 1 ocupação de fora; grupo nos outros casos
        if not own: n = 1 if len(vis) <= 1 else 1 + len(vis)
        elif len(own) == 1 and own[0]['tipo'] != 'Parcela' and not vis: n = 1
        else: n = 1 + len(own) + len(vis)
        resid = T - A - livre - conf
        per = min(resid, sum(o['area'] for o in fora if o['classe'] == 'perene')) if resid > 0.005 else 0.0
        editavel = not safra.get('ro')
        vinc = [o['id'] for o in fora if o['classe'] == 'perene' and editavel and
                not any(F(safs[s2]['ini']) <= b and F(safs[s2]['fim']) >= a for s2 in o['safs'] if s2 in safs)]
        linhas[t] = dict(T=T, A=A, sit=sit, livre=livre, conf=conf, area_livre=round(livre + conf, 2), desde=desde, own=own, fora=fora, vis=vis,
                         seq=seq, pend=pe, trav=tr, fix=fix, linhas=n, vinc=vinc, planejar=(livre + conf > 0.005 and editavel))
        band['nesta'] += A; band['livre'] += livre; band['conf'] += conf; band['perene'] += max(per, 0.0); band['ocup'] += max(resid - per, 0.0)
    return linhas, {k: round(v, 2) for k, v in band.items()}

def chips(linhas):
    """OC-R11/DONO-04/REG-06: só a Situação do próprio talhão (qf.nivel0)."""
    c = Counter(v['sit'] for v in linhas.values()); return dict(Todas=len(linhas), **dict(c.most_common()))
def sucessoes(linhas): return sum(1 for v in linhas.values() if v['sit'] == 'A conferir' and v['conf'] <= 0.005)

def faixa_txt(b, linhas, tot):
    p = ['Nesta safra %s' % ha(b['nesta'])] + ['%s %s' % (r, ha(b[k])) for r, k in (('Livre', 'livre'), ('A conferir', 'conf'), ('Perene', 'perene'), ('Ocupado', 'ocup')) if b[k] > 0.005]
    s = sucessoes(linhas)
    return ' · '.join(p) + ' · de %s ha' % ha(tot) + (' · %d sucessão a conferir' % s if s == 1 else (' · %d sucessões a conferir' % s if s else ''))

def mostra(nome, linhas, band, faz='Santa Rita', pr=print, detalhe=True):
    tot = sum(TAL[faz].values())
    pr('== %s | %s | chips %s | linhas %d | soma faixa %s' % (nome, faixa_txt(band, linhas, tot), chips(linhas), sum(v['linhas'] for v in linhas.values()),
                                                           ha(sum(band.values()))))
    if not detalhe: return
    for t, v in linhas.items():
        pr('   %-8s %-12s Área livre %-6s a partir de %-10s | nesta %-5s | own %s | visíveis %s%s%s%s%s' % (
            t, v['sit'], ha(v['area_livre']), br(v['desde']) if v['area_livre'] > 0.005 else '—', ha(v['A']),
            [(o['id'], o['faixa'], br(o['fim']), o['classe']) for o in v['own']],
            [(o['id'], o['faixa'], br(o['fim']), o['classe'], o['saf']) for o in v['vis']],
            (' | escondidas ' + str([o['id'] for o in v['fora'] if o not in v['vis']])) if len(v['vis']) < len(v['fora']) else '',
            (' | seq ' + str(v['seq'])) if v['seq'] else '', (' | Vincular ' + str(v['vinc'])) if v['vinc'] else '',
            (' | pend ' + str({k: [(p[0], p[1], br(p[2]), p[4]) for p in l] for k, l in v['pend'].items()})) if v['pend'] else ''))

def vincular(CU, sid, origem_id):
    """R-24 Vincular ciclo: cultivo desta safra com a identidade do ciclo, sem plano nem colheita."""
    src = [c for l in CU.values() for c in l if c['id'] == origem_id][0]
    nv = dict(copy.deepcopy(src), id='v_' + origem_id, ciclo=src.get('ciclo') or origem_id, plano=None, colheita=None, ro=False)
    CU.setdefault(sid, []).append(nv); return nv

TABELAS = [('S2627', 'S2627', None), ('S27SF', 'S27SF', None), ('caso 5', 'NOVA', NOVAS['caso5']), ('2027/28', 'NOVA', NOVAS['2027/28']),
           ('LG2627', 'LG2627', None), ('Boa Vista nova', 'NOVA', NOVAS['BoaVista']), ('Lagoa nova 2027/28', 'NOVA', NOVAS['LG2728']),
           ('Lagoa nova 2026/27', 'NOVA', NOVAS['LG2627b'])]

if __name__ == '__main__':
    folga = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print('# folga =', folga, '| ciclo mínimo', CICMIN, '| maior ciclo', CICMAX, '| antecedência', {p: antecedencia(p) for p in D2.PLANO})
    for rot, com in (('COM e4/e5', True), ('SEM e4/e5', False)):
        print('\n########', rot)
        CU = base(com)
        print('# períodos (Santa Rita): início · plantio · Ocupa até (fim por) · núcleo até · P')
        for o in sorted(ocupacoes(CU, safras_com(), folga), key=lambda o: (o['plantio'], o['id'])):
            if o['faz'] == 'Santa Rita':
                print('   %-4s %-6s %-5s %-22s %6s ha  início %s  plantio %s  Ocupa até %-10s (%-18s) núcleo %-10s P %s%s' % (
                    o['id'], o['saf'], o['faixa'], o['cult'] + ' ' + o['var'][:10], ha(o['area']), br(o['ini']), br(o['plantio']), br(o['fim']),
                    ROT[o['classe']], br(o['nuc']), br(P(o)), (' avisos ' + str(o['avisos'])) if o['avisos'] else ''))
        for nome, sid, nova in TABELAS:
            CUx = copy.deepcopy(CU); CUx.setdefault('NOVA', [])
            safra = nova or SAFS[sid]
            L, b = tabela(sid, CUx, safra, safras_com(nova), folga)
            mostra(nome, L, b, safra['fazenda'], detalhe=safra['fazenda'] != 'Lagoa Grande')
            if safra['fazenda'] == 'Lagoa Grande':
                print('   pivôs com Vincular ciclo: %d · com Planejar: %d' % (sum(1 for v in L.values() if v['vinc']), sum(1 for v in L.values() if v['planejar'])))
