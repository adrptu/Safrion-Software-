# -*- coding: utf-8 -*-
"""Comparação caso a caso: rodada 1 (v5.1 @96a99f68, base) × rodada 2 (v5.1 @7c2045d6), mesmo _render.
Chave da passagem: (tela, tipo, texto, href), como em revisor/comparar_casos.py. A chegada de cada rodada é recalculada com o
critério do próprio resumo (título/seleção da 1ª passada ou chegouEstrito da 2ª passada daquela rodada).
Também compara refs por (tela, linha) e os casos dirigidos dos percursos críticos por (percurso, sub, tela+visão, linha, texto, href).
Filtra as telas como o resumo.py: sem as marcadas Excluir em ocultas.json, sem MOD-* e sem CD (247 passagens na base).
Uso: python3 -I comparar_r2.py --r1 <brutos rodada 1> --r2 <saida-isolado rodada 2> --r1crit <saidas rodada 1> --ocultas <ocultas.json> --saida <json>"""
import argparse, collections, json, os
ap = argparse.ArgumentParser(); ap.add_argument('--r1', required=True); ap.add_argument('--r2', required=True); ap.add_argument('--r1crit', required=True); ap.add_argument('--saida', required=True); ap.add_argument('--ocultas', required=True)
a = ap.parse_args()
SAI = {o['tela'] for o in json.load(open(a.ocultas, encoding='utf-8')) if o.get('decisao') == 'Excluir'}
def carrega(D):
    pas, det, err = {}, {}, []
    chk = {}
    ck = os.path.join(D, 'leva-check.json')
    if os.path.exists(ck):
        for x in json.load(open(ck, encoding='utf-8')): chk[(x['tela'], x['i'])] = x.get('chegouEstrito') is True
    for f in sorted(os.listdir(D)):
        if f.endswith('.v5err.json'): err.append(f); continue
        if not f.endswith('.v5.json') or f.startswith('escopo'): continue
        d = json.load(open(os.path.join(D, f), encoding='utf-8')); t = d['screen']
        if t in SAI or t.startswith('MOD-') or t == 'CD': continue
        for x in d.get('detalhes', []): det[(t, x.get('linha'))] = x
        for i, p in enumerate(d.get('passagens', [])):
            k = (t, p['el']['k'], p['el']['t'], p['el'].get('h') or '')
            if p.get('r') in ('não achou', 'não reabriu', 'erro'): err.append(f'{t}[{i}] {p.get("r")}'); continue
            pas[k] = dict(p, tela=t, i=i, chk=chk.get((t, i)))
    return pas, det, err
def chegou(p):
    if p.get('r') != 'navega' or not p.get('alvo'): return None
    return bool(p.get('abriu') or p.get('destacou') or p.get('chk'))
P1, D1, E1 = carrega(a.r1); P2, D2, E2 = carrega(a.r2)
casos, raz = [], collections.Counter()
for k in sorted(set(P1) | set(P2)):
    p, q = P1.get(k), P2.get(k)
    c = {'tela': k[0], 'k': k[1], 'clique': k[2], 'href': k[3]}
    if not p or not q:
        c['razao'] = ['só na rodada 1' if p else 'só na rodada 2']; casos.append(c); raz[c['razao'][0]] += 1; continue
    r = []
    if (p.get('r'), p.get('para')) != (q.get('r'), q.get('para')): r.append(f"comportamento: {p.get('r')} {p.get('para')} × {q.get('r')} {q.get('para')}")
    if (p.get('alvo') or '') != (q.get('alvo') or ''): r.append(f"alvo: {p.get('alvo')!r} ({(p.get('esperado') or {}).get('source')}) × {q.get('alvo')!r} ({(q.get('esperado') or {}).get('source')})")
    c1, c2 = chegou(p), chegou(q)
    if c1 != c2:
        como = 'título do diálogo' if q.get('titulo') else 'h1 da página (sem diálogo; o h1 não fica no bruto)'
        r.append(f"chegada: {c1} × {c2}" + (f" · prova da rodada 2: {como}; titulo={q.get('titulo')!r}" if c2 else f" · titulo r1={p.get('titulo')!r} r2={q.get('titulo')!r}"))
    if bool(p.get('voltaOrigem')) != bool(q.get('voltaOrigem')): r.append(f"volta à origem: {bool(p.get('voltaOrigem'))} × {bool(q.get('voltaOrigem'))} · links {q.get('volta')}")
    v1 = (p.get('voltar') or {}).get('detalheReaberto'); v2 = (q.get('voltar') or {}).get('detalheReaberto')
    if p.get('origem') == 'detalhe' and v1 != v2: r.append(f"Voltar reabre: {v1} × {v2} · chegou {(q.get('voltar') or {}).get('chegou')}")
    c['razao'] = r or ['igual']
    c.update({'r1': {'r': p.get('r'), 'para': p.get('para'), 'alvo': p.get('alvo'), 'chegou': c1, 'titulo': p.get('titulo')},
              'r2': {'r': q.get('r'), 'para': q.get('para'), 'alvo': q.get('alvo'), 'chegou': c2, 'titulo': q.get('titulo')}})
    casos.append(c)
    for x in c['razao']: raz[x.split(':')[0]] += 1
refs = []
for k in sorted(set(D1) | set(D2), key=str):
    x, y = (D1.get(k) or {}).get('refs') or {}, (D2.get(k) or {}).get('refs') or {}
    if x != y: refs.append({'tela': k[0], 'linha': k[1], 'r1': x, 'r2': y})
def crit(D):
    out = {}
    for f in ('casos-criticos.json', 'casos-criticos-endereco.json'):
        p = os.path.join(D, f)
        if not os.path.exists(p): continue
        for c in json.load(open(p, encoding='utf-8'))['casos']:
            out[(f, c['percurso'], c['sub'], c['tela'] + (c.get('visao') or ''), c['linha'], c['el']['t'], c['el'].get('h') or '')] = c['res']
    return out
C1, C2 = crit(a.r1crit), crit(a.r2)
cc = []
for k in sorted(set(C1) | set(C2), key=str):
    x, y = C1.get(k), C2.get(k)
    f = lambda r: None if r is None else {kk: r.get(kk) for kk in ('r', 'para', 'alvo', 'abriu', 'destacou', 'inconclusivo')}
    cc.append({'chave': list(k), 'r1': f(x), 'r2': f(y), 'igual': f(x) == f(y)})
res = {'passagens_r1': len(P1), 'passagens_r2': len(P2), 'erros_r1': E1, 'erros_r2': E2, 'mesmasChaves': set(P1) == set(P2),
       'razoes': dict(raz), 'diferentes': [c for c in casos if c['razao'] != ['igual']], 'refsDiferentes': refs,
       'criticos': {'r1': len(C1), 'r2': len(C2), 'iguais': sum(x['igual'] for x in cc), 'casos': cc}}
json.dump(res, open(a.saida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ('diferentes', 'criticos')}, ensure_ascii=False)[:2000])
print('críticos', {k: v for k, v in res['criticos'].items() if k != 'casos'})
for c in res['diferentes']: print('-', c['tela'], '|', c['clique'][:50], '|', c['href'], '|', ' ; '.join(c['razao']))
