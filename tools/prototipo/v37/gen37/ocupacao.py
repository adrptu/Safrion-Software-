# -*- coding: utf-8 -*-
"""Ocupação dos talhões no tempo (Planejar safra, etapa 2 · ESPECIFICACAO.md R-01 a R-25): espelho em Python de ocupacao.js.
Fonte única das regras (ENG-011): início, Ocupa até e "Fim por", núcleo (parte certa), pior caso P(o), liberação com folga, Área livre,
Livre × A conferir, Situação do talhão, filhas visíveis, trava (só o certo), pendência e aviso (previsões), PlantioMin e mensagens.
Datas são dias inteiros desde 01/01/1970 (o mesmo número no JS); INF = sem fim. Sem dependência de dados: quem chama passa
culturas, cultivares, planos, safras, talhões e cultivos. ocupacao_unit.py confere JS = Python e os números da especificação."""
import datetime as _dt

INF = 10 ** 8
_EPOCH = _dt.date(1970, 1, 1)
ROT = {'perene': 'Perene', 'observado': 'Observado', 'plano': 'Pelo plano', 'informada': 'Colheita informada', 'estimado': 'Estimado (ciclo)', 'semdata': 'Sem ciclo'}


# ---------- datas e números ----------
def dia(iso):
    if not iso: return None
    return (_dt.date.fromisoformat(str(iso)[:10]) - _EPOCH).days
def iso(d):
    if d is None: return ''
    if d >= INF: return ''
    return (_EPOCH + _dt.timedelta(days=d)).isoformat()
def br(d):
    if d is None: return 'sem data'
    if d >= INF: return 'sem fim'
    x = _EPOCH + _dt.timedelta(days=d); return '%02d/%02d/%04d' % (x.day, x.month, x.year)
def ddmm(d):
    return br(d)[:5]
def r2(x):
    import math
    return math.floor(x * 100 + 0.5) / 100
def ha(x):
    """Área como na grade: até 2 casas, vírgula, milhar com ponto ("1.285,23")."""
    v = r2(x); neg = v < 0; v = abs(v)
    ip = int(v); fr = int(round((v - ip) * 100))
    if fr == 100: ip += 1; fr = 0
    s = '{:,}'.format(ip).replace(',', '.')
    if fr: s += ',' + ('%02d' % fr).rstrip('0')
    return ('-' if neg else '') + s
def mais(d, n): return INF if d >= INF else d + n


# ---------- contexto (cadastros) ----------
def ctx_de(culturas, cultivares, planos, folga=1):
    """culturas: {nome: classe ('Anual'|'Perene')}; cultivares: [(cultura, variedade, dias)]; planos: [plano publicado ou não]."""
    cic, mn, mx = {}, {}, {}
    for c, v, d in cultivares:
        if d in ('', None): continue
        d = int(d); cic[c + '|' + v] = d
        mn[c] = min(mn.get(c, 10 ** 6), d); mx[c] = max(mx.get(c, 0), d)
    return dict(classe=dict(culturas), cic=cic, cicmin=mn, cicmax=mx, planos={p['id']: p for p in planos},
                pub=[p for p in planos if p.get('estado', 'Publicado') == 'Publicado'], folga=int(folga))


def antecedencia(ctx, pid):
    """Maior antecedência do plano (dias antes do plantio), pelos DAP negativos."""
    pl = ctx['planos'].get(pid)
    if not pl: return 0
    return max([0] + [-a['g']['dias'] for a in pl['atividades'] if a['g']['tipo'] == 'DAP' and (a['g']['dias'] or 0) < 0])


def _colheita_plano(pl, plantio):
    ca = next((a for a in pl['atividades'] if str(a['op']).startswith('Colheita')), None)
    if ca and ca['g']['tipo'] == 'DAP': return plantio + ca['g']['dias']
    if ca and ca['g']['tipo'] == 'DATA': return dia(ca['g']['data'])
    return plantio


def atividades(ctx, plantio, pid, colheita=None):
    """[(nome, tipo, dia)] das atividades do plano para um plantio (mesma regra de dataAtv/colheitaDe do safra.js)."""
    pl = ctx['planos'].get(pid)
    if not pl: return []
    out = []
    for a in pl['atividades']:
        g = a['g']; t = g['tipo']
        if t == 'DAP': d = plantio + g['dias']
        elif t == 'DATA': d = dia(g['data'])
        else:
            col = colheita if colheita is not None else _colheita_plano(pl, plantio)
            d = col + (g['dias'] if t == 'DAPC' else -g['dias'])
        out.append((a['nome'], t, d))
    return out


def datas_validas(ctx, plantio, pid, safini, safim, colheita=None):
    """R-03/R-04: DATA só conta dentro da safra do cultivo e a partir de plantio − antecedência; o resto vira aviso."""
    ok, fora = [], []
    ant = antecedencia(ctx, pid)
    for n, tp, d in atividades(ctx, plantio, pid, colheita):
        if tp == 'DATA' and not (safini <= d <= safim and d >= plantio - ant): fora.append((n, d))
        else: ok.append((n, tp, d))
    return ok, fora


def fim_estimado(ctx, cult, var, plantio):
    """R-04 (e): plantio + o maior entre o ciclo da cultivar e a última atividade relativa (DAP/DANC/DAPC) dos planos publicados da cultura."""
    cands = []
    k = cult + '|' + var
    if k in ctx['cic']: cands.append(plantio + ctx['cic'][k])
    for p in ctx['pub']:
        if p['cultura'] != cult: continue
        ds = [d for n, tp, d in atividades(ctx, plantio, p['id']) if tp != 'DATA']
        if ds: cands.append(max(ds))
    return max(cands) if cands else None


# ---------- ocupação ----------
def talhao_de(local, tipo):
    return local if tipo != 'Parcela' else str(local).rsplit('-', 1)[0]


def mk(ctx, c, s):
    """Ocupação de um cultivo c (dict: id, ciclo, saf, faz, talhao, faixa, tipo, area, cult, var, plantio, plano, colheita,
    colheita_real, origem) na safra s (dict: id, nome, ini, fim, ro)."""
    folga = ctx['folga']
    pid = c.get('plano') or None
    if pid and (pid not in ctx['planos'] or ctx['planos'][pid]['cultura'] != c['cult']): pid = None   # plano de outra cultura não vale (R-04)
    pl = dia(c['plantio'])
    colh = dia(c.get('colheita')) if c.get('colheita') else None
    real = dia(c.get('colheita_real')) if c.get('colheita_real') else None
    o = dict(id=c['id'], ciclo=c.get('ciclo') or c['id'], saf=c['saf'], safs=[c['saf']], safnome=s.get('nome', c['saf']), faz=c['faz'],
             t=c.get('talhao') or talhao_de(c['faixa'], c['tipo']), faixa=c['faixa'], tipo=c['tipo'], area=float(c['area'] or 0),
             cult=c['cult'], var=c.get('var') or '', plantio=pl, plano=pid, safini=dia(s['ini']), safim=dia(s['fim']), ro=bool(s.get('ro')),
             colh_inf=colh, colh_real=real, origem=c.get('origem') or '', avisos=[], folga=folga, ini=pl)
    dfim = None
    if pid:
        ok, fora = datas_validas(ctx, pl, pid, o['safini'], o['safim'], colh)
        ini_c = [pl] + [d for n, tp, d in ok if tp in ('DAP', 'DATA')]
        o['ini'] = min(ini_c)
        if fora: o['avisos'].append(('datas_fixas', pid, fora[0][1]))
        dfim = max([pl] + [d for n, tp, d in ok] + ([colh] if colh is not None else []))
    classe = ctx['classe'].get(o['cult'], 'Anual')
    if classe == 'Perene': o['fim'], o['classe'] = INF, 'perene'
    elif real is not None: o['fim'], o['classe'] = real, 'observado'
    elif pid: o['fim'], o['classe'] = dfim, 'plano'
    elif colh is not None: o['fim'], o['classe'] = colh, 'informada'
    else:
        e = fim_estimado(ctx, o['cult'], o['var'], pl)
        o['fim'], o['classe'] = (e, 'estimado') if e is not None else (None, 'semdata')
    cm = ctx['cicmin'].get(o['cult'])
    if o['classe'] == 'perene': o['nuc'] = INF
    elif o['classe'] == 'observado': o['nuc'] = real
    elif cm: o['nuc'] = min(o['fim'] if o['fim'] is not None else INF, pl + cm - 1)
    else: o['nuc'] = pl
    return o


def P(ctx, o):
    """Fim no pior caso (R-08)."""
    if o['classe'] == 'perene': return INF
    if o['classe'] in ('plano', 'informada', 'observado'): return o['fim']
    if o['classe'] == 'estimado': return max(o['safim'], o['fim'])
    mc = ctx['cicmax'].get(o['cult'])
    return max(o['safim'], o['plantio'] + mc) if mc else INF


def ocupa_ate(ctx, o, modo):
    if modo == 'pior': return P(ctx, o)
    if o['classe'] == 'semdata': return o['plantio']
    return o['fim']


def liberacao(ctx, o, modo): return mais(ocupa_ate(ctx, o, modo), o['folga'])
def ativo(ctx, o, x, modo): return o['ini'] <= x < liberacao(ctx, o, modo) or o['ini'] == x
def nuc_lib(o): return mais(o['nuc'], o['folga'])
def nuc_ativo(o, x): return o['plantio'] <= x < nuc_lib(o) or o['plantio'] == x
def mesma_area(a, b): return a['faixa'] == b['faixa'] or a['tipo'] != 'Parcela' or b['tipo'] != 'Parcela'
def com_plano(o): return bool(o['plano']) or o['classe'] == 'perene'


def ocupacoes(ctx, safras, cults):
    """Uma ocupação por ciclo (R-07): o mesmo ciclo em duas safras conta uma vez e lembra as safras."""
    recs, vistos = [], {}
    for c in cults:
        s = safras.get(c['saf'])
        if not s: continue
        o = mk(ctx, c, s)
        if o['ciclo'] in vistos: vistos[o['ciclo']]['safs'].append(c['saf']); continue
        vistos[o['ciclo']] = o; recs.append(o)
    return recs


def intersec(a0, a1, b0, b1):
    x0, x1 = max(a0, b0), min(a1, b1)
    return (x0, x1) if x0 < x1 else None


def avalia(ctx, occs, T, alvo=None):
    """R-14 trava (só o certo) e R-15 pendência (previsões) entre as ocupações de um talhão de área T.
    trava: (tipo, id_a, id_b, dia[, soma]); pendência[id]: [(tipo, causa, dia_ini, dia_fim, ndias)]. A pendência fica na de plantio mais tardio.
    Soma no tempo por eventos (SAF-C01): os núcleos ativos só mudam em plantio, plantio + 1 e fim do núcleo (com folga), e os períodos
    previstos em início e liberação (est). Entre dois pontos seguidos nada muda: cada trecho é avaliado uma vez, sem horizonte (o teto
    antigo, d0 + 900 dias, deixava uma perene ou ocupação antiga esconder a soma de anos depois). Depois do último ponto só ficam perenes,
    com núcleo igual ao previsto: dá trava ou nada, nunca pendência; por isso o último trecho conta 1 dia."""
    trav, pend = [], {}
    oc = sorted(occs, key=lambda o: (o['plantio'], o['id']))
    for i, A in enumerate(oc):
        for B in oc[i + 1:]:
            if A['ciclo'] == B['ciclo']: continue
            if alvo and alvo not in (A['id'], B['id']): continue
            if not mesma_area(A, B): continue
            for X, Y in ((A, B), (B, A)):
                if Y['classe'] == 'observado' and intersec(X['ini'], liberacao(ctx, X, 'est'), Y['plantio'], nuc_lib(Y)) and X['plantio'] >= Y['plantio']:
                    trav.append(('observado', Y['id'], X['id'], max(X['ini'], Y['plantio'])))
            if (com_plano(A) or com_plano(B)) and intersec(A['plantio'], nuc_lib(A), B['plantio'], nuc_lib(B)):
                trav.append(('faixa', A['id'], B['id'], B['plantio'])); continue
            kind = {'plano': 'prevista', 'informada': 'prevista', 'observado': 'prevista', 'estimado': 'provavel', 'semdata': 'naoconf'}.get(A['classe'])
            if kind:
                fimA = liberacao(ctx, A, 'pior' if kind == 'naoconf' else 'est')
                r = intersec(A['ini'], fimA, B['ini'], liberacao(ctx, B, 'est'))
                if r: pend.setdefault(B['id'], []).append((kind, A['id'], r[0], r[1] - 1, r[1] - r[0]))
    if occs:
        pts = sorted({x for o in occs for x in (o['plantio'], o['plantio'] + 1, nuc_lib(o), o['ini'], liberacao(ctx, o, 'est')) if x < INF})
        vis_t, vis_p, ordp = set(), {}, []
        cruz = lambda lst: any(mesma_area(a, b) and a['ciclo'] != b['ciclo'] for k2, a in enumerate(lst) for b in lst[k2 + 1:])
        for i, x in enumerate(pts):
            n = (pts[i + 1] if i + 1 < len(pts) else x + 1) - x
            nu = [o for o in occs if nuc_ativo(o, x)]
            if sum(o['area'] for o in nu) > T + 0.005 and any(com_plano(o) for o in nu) and not cruz(nu):
                last = max(nu, key=lambda o: (o['plantio'], o['id']))
                if not alvo or alvo in [o['id'] for o in nu]:
                    k = ('soma', '+'.join(sorted(o['id'] for o in nu if o is not last)), last['id'])
                    if k not in vis_t: vis_t.add(k); trav.append(('soma', k[1], last['id'], x, r2(sum(o['area'] for o in nu))))
            else:
                pv = [o for o in occs if o['ini'] <= x < liberacao(ctx, o, 'est')]
                if sum(o['area'] for o in pv) > T + 0.005 and not cruz(pv):
                    last = max(pv, key=lambda o: (o['plantio'], o['id']))
                    key = (last['id'], '+'.join(sorted(o['id'] for o in pv if o is not last)))
                    if key not in vis_p: vis_p[key] = [x, x, 0]; ordp.append(key)
                    v = vis_p[key]; v[1] = x + n - 1; v[2] += n
        for key in ordp:
            lid, causa = key; d_ini, d_fim, nd = vis_p[key]
            if alvo and alvo != lid and alvo not in causa.split('+'): continue
            pend.setdefault(lid, []).append(('soma', causa, d_ini, d_fim, nd))
    return trav, pend


# ---------- tabela da etapa 2 ----------
def tabela(ctx, safra, occ, talhoes, safras):
    """Linhas por talhão (R-09 a R-12, R-24) e faixa de resumo. safra: dict(id, ini, fim, faz, ro); talhoes: [(nome, área)] na ordem do CD-01;
    occ: ocupacoes() de todas as safras; safras: {id: safra} (para a condição do Vincular ciclo)."""
    sid = safra['id']; a, b = dia(safra['ini']), dia(safra['fim']); faz = safra['faz']
    occ = [o for o in occ if o['faz'] == faz]
    linhas, ordem = {}, []
    band = dict(nesta=0.0, livre=0.0, conf=0.0, perene=0.0, ocup=0.0)
    for t, T in talhoes:
        T = float(T)
        own = [o for o in occ if o['t'] == t and sid in o['safs']]
        fora = [o for o in occ if o['t'] == t and sid not in o['safs'] and o['ini'] <= b and liberacao(ctx, o, 'pior') > a]
        A = sum(o['area'] for o in own)
        n = b - a + 1
        def mfirst(modo):
            free = [T - A - sum(o['area'] for o in fora if o['ini'] <= a + i < liberacao(ctx, o, modo)) for i in range(n)]
            cur, m = 1e18, [0.0] * n
            for i in range(n - 1, -1, -1): cur = min(cur, free[i]); m[i] = cur
            for i in range(n):
                if m[i] > 0.005: return r2(m[i]), a + i
            return 0.0, None
        Lp, dp = mfirst('pior'); Le, de = mfirst('est')
        fix = [o['id'] for o in fora if o['classe'] in ('estimado', 'semdata') and dp is not None and dp == liberacao(ctx, o, 'pior')]
        if fix: livre, conf, desde = 0.0, max(Le, Lp), de
        else: livre, conf, desde = Lp, r2(max(0.0, Le - Lp)), (dp if Lp > 0.005 else de)
        est = conf > 0.005 or bool(fix)
        tr, pe = avalia(ctx, own + fora, T)
        ids_own = [o['id'] for o in own]
        pend_own = {k: v for k, v in pe.items() if k in ids_own or any(p[1] in ids_own for p in v)}
        seq = []
        for x in own + fora:
            if x['classe'] not in ('estimado', 'semdata'): continue
            for y in own + fora:
                if y is x or ((x in own) == (y in own)) or not mesma_area(x, y): continue
                if x['ini'] < y['ini'] < liberacao(ctx, x, 'pior'): seq.append((x['id'], y['id']))
        if tr: sit = 'Sobreposição'
        elif conf > 0.005 or seq or pend_own: sit = 'A conferir'
        elif livre > 0.005: sit = 'Livre'
        elif own: sit = 'Planejado'
        elif any(o['classe'] == 'perene' for o in fora): sit = 'Perene'
        else: sit = 'Ocupado'
        nomes = {o['faixa'] for o in own}; inteiro = any(o['tipo'] != 'Parcela' for o in own)
        adj = []
        for x in own:
            ant = [o for o in fora if mesma_area(o, x) and o['ini'] < x['ini']]
            suc = [o for o in fora if mesma_area(o, x) and o['ini'] > x['ini']]
            if ant: adj.append(max(ant, key=lambda o: (o['ini'], o['id']))['id'])
            if suc: adj.append(min(suc, key=lambda o: (o['ini'], o['id']))['id'])
        vis = [o for o in fora if not (o['faixa'] in nomes or inteiro) or o['id'] in adj]
        vis.sort(key=lambda o: (o['ini'], o['id']))
        if not own: nl = 1 if len(vis) <= 1 else 1 + len(vis)
        elif len(own) == 1 and own[0]['tipo'] != 'Parcela' and not vis: nl = 1
        else: nl = 1 + len(own) + len(vis)
        resid = T - A - livre - conf
        per = min(resid, sum(o['area'] for o in fora if o['classe'] == 'perene')) if resid > 0.005 else 0.0
        # excesso (SAF-C01): a maior soma certa acima da área nas travas de soma; fora da partição da faixa (soma T, R-09), no texto da faixa
        exc = r2(max(0.0, max([T] + [x[4] for x in tr if x[0] == 'soma']) - T))
        editavel = not safra.get('ro')
        vinc = [o['id'] for o in fora if o['classe'] == 'perene' and editavel and
                not any(dia(safras[s2]['ini']) <= b and dia(safras[s2]['fim']) >= a for s2 in o['safs'] if s2 in safras)]
        linhas[t] = dict(t=t, T=T, A=r2(A), sit=sit, livre=r2(livre), conf=r2(conf), area_livre=r2(livre + conf), desde=desde, est=est,
                         own=own, fora=fora, vis=vis, seq=seq, pend=pe, pend_own=pend_own, trav=tr, exc=exc, fix=fix, linhas=nl, vinc=vinc,
                         planejar=(livre + conf > 0.005 and editavel))
        ordem.append(t)
        band['nesta'] += A; band['livre'] += livre; band['conf'] += conf; band['perene'] += max(per, 0.0); band['ocup'] += max(resid - per, 0.0)
    return [linhas[t] for t in ordem], {k: r2(v) for k, v in band.items()}


def chips(linhas):
    """Filtro rápido só pela Situação do nível 0 (qf.nivel0): a soma dos chips é Todas."""
    c = {}
    for v in linhas: c[v['sit']] = c.get(v['sit'], 0) + 1
    return c


def sucessoes(linhas): return sum(1 for v in linhas if v['sit'] == 'A conferir' and v['conf'] <= 0.005)


def faixa_txt(band, linhas, tot):
    p = ['Nesta safra %s' % ha(band['nesta'])] + ['%s %s' % (r, ha(band[k])) for r, k in (('Livre', 'livre'), ('A conferir', 'conf'), ('Perene', 'perene'), ('Ocupado', 'ocup')) if band[k] > 0.005]
    s = sucessoes(linhas); ex = r2(sum(v.get('exc', 0) for v in linhas))
    return (' · '.join(p) + ' · de %s ha' % ha(tot) + (' · %s ha em sobreposição' % ha(ex) if ex > 0.005 else '') +
            (' · %d sucessão a conferir' % s if s == 1 else (' · %d sucessões a conferir' % s if s else '')))




# ---------- salvar: trava, pendência nova e aviso (R-14, R-15) ----------
def checa(ctx, safras, antes, depois, sid, alvo, T):
    """antes/depois: listas de cultivos sem e com a mudança (novo cultivo ou edição); alvo: id do cultivo; T: área do talhão do alvo.
    Devolve dict(trav, pend (só as pendências que a mudança criou), aviso (ocupações estimadas que o alvo começa antes de liberar), o, mesmo)."""
    occ = ocupacoes(ctx, safras, depois)
    o = next((x for x in occ if x['id'] == alvo), None)
    if o is None: return dict(trav=[], pend={}, aviso=[], o=None, mesmo=[])
    T = float(T)
    mesmo = [x for x in occ if x['faz'] == o['faz'] and x['t'] == o['t']]
    trav, pe = avalia(ctx, mesmo, T, alvo)
    soma = sum(x['area'] for x in mesmo if sid in x['safs'])
    if soma > T + 0.005: trav = [('safra', sid, alvo, o['plantio'], r2(soma))] + trav
    occ0 = ocupacoes(ctx, safras, antes)
    _, pe0 = avalia(ctx, [x for x in occ0 if x['faz'] == o['faz'] and x['t'] == o['t']], T)
    aviso = [y for y in mesmo if y is not o and mesma_area(o, y) and y['classe'] in ('estimado', 'semdata') and y['ini'] < o['ini'] < liberacao(ctx, y, 'pior')]
    return dict(trav=trav, pend=pend_novas(pe0, pe), aviso=aviso, o=o, mesmo=mesmo)


def pend_novas(antes, depois):
    out = {}
    for k, v in depois.items():
        n = [p for p in v if p not in antes.get(k, [])]
        if n: out[k] = n
    return out


def troca(cults, novo):
    """Lista com o cultivo novo ou editado (mesmo id substitui)."""
    out = [c for c in cults if c['id'] != novo['id']]
    return out + [novo]


def plantio_min(ctx, safras, cults, sid, novo, desde, T, ate=None):
    """R-17: menor plantio ≥ desde + antecedência do plano sem trava nem pendência nova contra as ocupações do talhão. None = sem janela."""
    t = novo.get('talhao') or talhao_de(novo['faixa'], novo['tipo'])
    base = [c for c in cults if c['faz'] == novo['faz'] and (c.get('talhao') or talhao_de(c['faixa'], c['tipo'])) == t and c['id'] != novo['id']]
    antes = base + ([c for c in cults if c['id'] == novo['id']])
    d = desde + (antecedencia(ctx, novo['plano']) if novo.get('plano') else 0)
    fim = ate if ate is not None else dia(safras[sid]['fim'])
    while d <= fim:
        nv = dict(novo, plantio=iso(d))
        r = checa(ctx, safras, antes, base + [nv], sid, novo['id'], T)
        if not r['trav'] and not r['pend']: return d
        d += 1
    return None


# ---------- textos (OC-U4): fato, dano e saída ----------
FEM_CULT = {'Soja'}
FEM_ATV = {'dessecação', 'adubação', 'colheita', 'calagem', 'gessagem', 'fertirrigação', 'poda', 'sexagem', 'pulverização', 'aplicação'}
def nome_cv(o): return (o['cult'] + ' ' + str(o['var']).replace('Híbrido ', '')).strip()
def _minus(s): return s[:1].lower() + s[1:] if s else s
def _f(cult): return cult in FEM_CULT
def art(cult): return 'a' if _f(cult) else 'o'
def de(cult): return 'da' if _f(cult) else 'do'
def gen(cult, masc): return masc[:-1] + 'a' if _f(cult) else masc   # previsto → prevista, colhido → colhida, plantado → plantada
def _plano_nome(ctx, o): return ctx['planos'][o['plano']]['nome'] if o.get('plano') in ctx['planos'] else ''
def _atv_em(ctx, o, d):
    """Nome curto da atividade do plano do alvo que cai no dia d (ex.: "dessecação")."""
    if not o.get('plano'): return 'plantio'
    for n, tp, x in atividades(ctx, o['plantio'], o['plano'], o['colh_inf']):
        if x == d: return _minus(n.split(' ')[0])
    return 'plantio'
def _atv_do(ctx, o):
    """"A dessecação da Soja alta tecnologia" · "O plantio do Milho safrinha" · sem plano: "O plantio do milho"."""
    a = _atv_em(ctx, o, o['ini']); pn = _plano_nome(ctx, o)
    alvo = ('%s %s' % (de(o['cult']), pn)) if pn else ('%s %s' % (de(o['cult']), _minus(o['cult'])))
    return '%s %s %s' % ('A' if a in FEM_ATV else 'O', a, alvo)
def _pomar(cult): return {'Café': 'o cafezal', 'Mamão Formosa': 'o pomar'}.get(cult, 'a lavoura perene')
def _faz_safra(o, sid): return 'desta safra' if sid in o['safs'] else 'da ' + o['safnome']
def _dias(n): return '%d %s' % (n, 'dia' if n == 1 else 'dias')


def msg_trava(ctx, chk, sid, T, safnomes, pmin=None):
    """Mensagem única da trava pela precedência: área da própria safra (M1) > colheita real (M4) > perene (M3) > núcleo (M2) > soma (M1)."""
    o = chk['o']; tr = chk['trav']
    by = {x['id']: x for x in chk['mesmo']}
    folga = ctx['folga']
    tipos = [x[0] for x in tr]
    if 'safra' in tipos or 'soma' in tipos:
        outros = [x for x in chk['mesmo'] if x is not o and intersec(o['ini'], liberacao(ctx, o, 'est'), x['ini'], liberacao(ctx, x, 'est'))]
        if outros:
            ini = max([o['ini']] + [x['ini'] for x in outros]); fim = min([o['fim'] if o['fim'] is not None else o['plantio']] + [x['fim'] for x in outros if x['fim'] is not None])
            # maior soma dos outros nos dias ini..ate: só muda no início e na liberação de cada um (SAF-C01; o laço dia a dia ia até 10^8 com perenes)
            ate = ini + max(1, fim - ini + 1) - 1
            pts = [d for d in [ini] + [x['ini'] for x in outros] + [liberacao(ctx, x, 'est') for x in outros] if ini <= d <= ate]
            pior = max(sum(x['area'] for x in outros if x['ini'] <= d < liberacao(ctx, x, 'est')) for d in pts)
            quem = ' e '.join('%s (%s, %s)' % (x['cult'], x['faixa'], x['safnome']) for x in outros)
            quando = ('A partir de %s' % br(ini)) if fim >= INF else ('De %s a %s' % (br(ini), br(fim)))
            return '%s, %s ha de %s estão com %s. Máximo %s ha nesse período.' % (quando, ha(pior), o['t'], quem, ha(max(0.0, T - pior)))
        soma = next((x[4] for x in tr if x[0] == 'safra'), 0)
        return 'As áreas de %s nesta safra somariam %s ha; o talhão tem %s ha (livre: %s ha).' % (o['t'], ha(soma), ha(T), ha(max(0.0, T - (soma - o['area']))))
    ob = next((x for x in tr if x[0] == 'observado'), None)
    if ob:
        Y = by.get(ob[1]); X = by.get(ob[2])
        if Y is o: Y, X = X, Y
        a = _atv_do(ctx, X)
        return ('%s %s de %s foi %s em %s; %s cai em %s, com %s %s em campo.%s' % (
            art(Y['cult']).upper(), nome_cv(Y), Y['faixa'], gen(Y['cult'], 'colhido'), br(Y['colh_real']), _minus(a[:1]) + a[1:], br(X['ini']), art(Y['cult']), _minus(Y['cult']),
            (' Plantio a partir de %s resolve.' % br(pmin)) if pmin is not None else ''))
    fx = next((x for x in tr if x[0] == 'faixa'), None)
    if fx:
        a, b = by.get(fx[1]), by.get(fx[2]); outro = b if a is o else a
        if outro['classe'] == 'perene':
            return ('%s tem %s perene, sem fim registrado. O plano geraria insumo e O.S. sobre %s. O encerramento do ciclo ainda não existe no sistema.'
                    % (outro['faixa'], outro['cult'], _pomar(outro['cult'])))
        if o['classe'] == 'perene':
            return ('%s tem %s %s desde %s. O plano geraria insumo e O.S. sobre lavoura em campo.' % (outro['faixa'], outro['cult'], _faz_safra(outro, sid), br(outro['plantio'])))
        pri = outro if outro['plantio'] <= o['plantio'] else o; seg = o if pri is outro else outro
        cm = ctx['cicmin'].get(pri['cult'])
        if pri['classe'] == 'observado': base = '%s em %s' % (gen(pri['cult'], 'colhido'), br(pri['colh_real']))
        elif cm and pri['nuc'] == pri['plantio'] + cm - 1: base = 'ciclo mínimo %s %s, %d dias, CD-02' % (de(pri['cult']), _minus(pri['cult']), cm)
        else: base = 'colheita prevista em %s' % br(pri['fim'])
        if pri is outro:
            return ('%s está com %s %s, %s em %s: ocupa a área até pelo menos %s (%s). O plano geraria insumo e O.S. sobre lavoura em campo. '
                    'Informe a colheita %s %s ou plante a partir de %s.' % (pri['faixa'], nome_cv(pri), _faz_safra(pri, sid), gen(pri['cult'], 'plantado'), br(pri['plantio']),
                                                                           br(pri['nuc']), base, de(pri['cult']), _minus(pri['cult']), br(mais(pri['nuc'], folga))))
        return ('%s: %s %s %s, %s em %s, ocupa a área até pelo menos %s (%s), e %s %s %s começa em %s. O plano geraria insumo e O.S. sobre lavoura em campo.'
                % (pri['faixa'], art(pri['cult']), nome_cv(pri), _faz_safra(pri, sid), gen(pri['cult'], 'plantado'), br(pri['plantio']), br(pri['nuc']), base,
                   art(seg['cult']), seg['cult'], _faz_safra(seg, sid), br(seg['plantio'])))
    return 'Sobreposição com outra ocupação do talhão.'


def msg_sem_janela(ctx, o, seg, base_lib, sid):
    """P3: sem janela antes do fim da safra para o alvo o, porque a sucessora seg começa cedo demais."""
    ant = antecedencia(ctx, o['plano']) if o.get('plano') else 0
    pl = base_lib + ant
    if o.get('plano'):
        ok, _f2 = datas_validas(ctx, pl, o['plano'], o['safini'], o['safim'], None)
        fim = max([pl] + [d for n, tp, d in ok])
    else:
        fim = fim_estimado(ctx, o['cult'], o['var'], pl) or pl
    return ('%s tem %s %s a partir de %s. Para %s %s com %s começar depois do cultivo anterior (%s), replaneje esse %s para %s ou depois.'
            % (o['faixa'], seg['cult'], _faz_safra(seg, sid), br(seg['plantio']), art(o['cult']), _minus(o['cult']), _plano_nome(ctx, o) or 'o plano', br(base_lib),
               _minus(seg['cult']), br(mais(fim, ctx['folga']))))


def msg_pend(ctx, chk, sid, pmin=None):
    """P1 (pendência no próprio cultivo) ou P2 (o cultivo editado empurra a sucessora). '' sem pendência."""
    o = chk['o']; by = {x['id']: x for x in chk['mesmo']}
    if not chk['pend']: return ''
    if o['id'] in chk['pend']:
        p = chk['pend'][o['id']][0]
        if p[0] == 'soma':
            return '%s: a soma prevista das áreas passa da área do talhão de %s a %s (%s).' % (o['t'], br(p[2]), br(p[3]), _dias(p[4]))
        A = by.get(p[1])
        return ('%s: sobreposição prevista de %s. %s cai em %s e %s %s (%s) está %s até %s. %sou confirme a colheita %s %s.'
                % (o['faixa'], _dias(p[4]), _atv_do(ctx, o), br(o['ini']), art(A['cult']), nome_cv(A), A['safnome'], gen(A['cult'], 'previsto'),
                   br(A['fim']) if A['fim'] is not None else 'sem data', ('Mude o plantio para %s ou depois, ' % br(pmin)) if pmin is not None else 'Mude o plantio ',
                   de(A['cult']), _minus(A['cult'])))
    k = next(iter(chk['pend'])); p = chk['pend'][k][0]; B = by.get(k)
    if p[0] == 'soma':
        return '%s: a soma prevista das áreas passa da área do talhão de %s a %s (%s).' % (o['t'], br(p[2]), br(p[3]), _dias(p[4]))
    return ('%s: a colheita prevista %s %s passa para %s, depois do plantio %s %s da %s (%s). Sobreposição prevista de %s.'
            % (o['faixa'], de(o['cult']), o['cult'], br(o['fim']), de(B['cult']), B['cult'], B['safnome'], br(B['plantio']), _dias(p[4])))


def msg_aviso(ctx, chk):
    """Aviso ao salvar (R-15) quando a anterior tem fim Estimado ou Sem ciclo e a nova começa antes do P(o) dela."""
    o = chk['o']; out = []
    for y in chk['aviso']:
        pe = [p for p in chk['pend'].get(o['id'], []) if p[1] == y['id']]
        if y['classe'] == 'semdata': out.append('saída %s %s não conferida' % (de(y['cult']), _minus(y['cult'])))
        elif pe: out.append('provável sobreposição (%s) com %s %s da %s' % (_dias(pe[0][4]), art(y['cult']), _minus(y['cult']), y['safnome']))
        else: out.append('saída %s %s estimada em %s; confirme a colheita' % (de(y['cult']), _minus(y['cult']), br(y['fim'])))
    return '; '.join(out)


def pend_curta(ctx, o, p, by):
    """Texto da célula Situação/nota: "Sobreposição prevista: 11 dias (dessecação 05/11 × milho até 15/11)"."""
    if p[0] == 'soma': return 'Soma prevista acima da área: %s (%s a %s)' % (_dias(p[4]), ddmm(p[2]), ddmm(p[3]))
    A = by.get(p[1])
    return 'Sobreposição prevista: %s (%s %s × %s até %s)' % (_dias(p[4]), _atv_em(ctx, o, o['ini']), ddmm(o['ini']), _minus(A['cult']),
                                                              ddmm(A['fim']) if A['fim'] is not None else 'sem data')
