"""Resume o robô v4: o que cada clique faz em tabela e cartões. Uso: python3 -I v4summ.py <v4out> <grids.json> <saida.json>"""
import json, os, sys, collections
D, GJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
def cls(t):
    if not t: return None
    r = t.get('r')
    if r == 'diálogo':
        tipo = t.get('tipo', '')
        if t.get('campos', 0) > 0 and not t.get('consulta') and any(p.lower().startswith('salvar') for p in t.get('primarias', [])): what = 'formulário de edição'
        elif t.get('consulta') or not t.get('campos'): what = 'detalhe (consulta)'
        else: what = 'formulário'
        return what + ' · ' + tipo
    if r in ('navega', 'muda o endereço'): return 'navega para outra tela'
    if r == 'menu': return 'abre menu'
    if r in ('expande', 'recolhe'): return 'expande ou recolhe'
    if r == 'edita na linha': return 'edita na própria linha'
    if r and r.startswith('muda a tela'): return 'muda a tela sem abrir nada'
    return 'nada'
agg = {k: collections.Counter() for k in ('linha', 'pai', 'seta', 'filho', 'botao')}
by_mode = {m: collections.Counter() for m in ('tabela', 'cartoes')}
icons = collections.Counter(); menus = 0; menu_items = []; mismatch = []; cards_nofocus = 0; cards_total = 0; rows_total = 0; rows_nofocus = 0
screens = []; own_tables = collections.Counter(); own_menus = []
for f in sorted(os.listdir(D)):
    if not f.endswith('.v4.json'): continue
    d = json.load(open(os.path.join(D, f))); sc = {'tela': d['screen'], 'h1': d.get('h1', ''), 'grades': []}
    per = collections.defaultdict(dict)
    for g in d['grades']:
        if g.get('erro') or not g.get('linhas'): continue
        t = g.get('testes', {}); am = g.get('amostra') or {}
        if g['modo'] == 'cartoes': cards_total += 1; cards_nofocus += 1 if am.get('tab') in (None, '-1') else 0
        else: rows_total += 1; rows_nofocus += 1 if am.get('tab') in (None, '-1') else 0
        row = {'gid': g['gid'], 'modo': g['modo'], 'linhas': g['linhas'], 'foco': am.get('tab') not in (None, '-1'), 'botoes': g.get('botoesNaLinha', []), 'links': g.get('linksNaLinha', []), 'temMais': g.get('temMais')}
        for k in ('linha', 'pai', 'seta', 'filho', 'botao'):
            c = cls(t.get(k)); row[k] = c
            if c: agg[k][c] += 1
            if k == 'linha' and c: by_mode[g['modo']][c] += 1
            if k in ('linha', 'pai') and t.get(k): row[k + '_titulo'] = t[k].get('titulo', '')
        m = t.get('mais')
        if m and m.get('r') == 'menu':
            menus += 1; its = m.get('itens', []); row['mais'] = [(x['t'], x['icone']) for x in its]
            for x in its: icons[x['icone']] += 1
            menu_items += [x['t'] for x in its]
        per[g['gid']][g['modo']] = row; sc['grades'].append(row)
    for gid, md in per.items():
        if 'tabela' in md and 'cartoes' in md and md['tabela'].get('linha') != md['cartoes'].get('linha'):
            mismatch.append({'tela': d['screen'], 'grade': gid, 'tabela': md['tabela'].get('linha'), 'cartoes': md['cartoes'].get('linha')})
    for o in d.get('outros', []):
        if o.get('onde') == 'tabela própria': own_tables[cls(o)] += 1
        elif o.get('r') == 'menu': own_menus.append({'tela': d['screen'], 'alvo': o.get('alvo'), 'itens': [(x['t'], x['icone']) for x in o.get('itens', [])]})
    screens.append(sc)
grids = [g for g in json.load(open(GJ)) if 'grid' in g]
static = {'grades': len(grids), 'telas': len(set(g['tela'] for g in grids)), 'abre': dict(collections.Counter(g['abre'] for g in grids)), 'rmenu': sum(g['rmenu'] for g in grids),
          'comBotoes': sum(1 for g in grids if g['acoes'].get('act') or g['acoes'].get('cta')), 'comLinks': sum(1 for g in grids if g['acoes'].get('nav')), 'comPais': sum(1 for g in grids if g['pais']), 'modo': dict(collections.Counter(str(g['modo']) for g in grids))}
for g in json.load(open(GJ)):
    for o in own_menus: pass
for o in own_menus:
    for x in o['itens']: icons[x[1]] += 1
res = {'agg': {k: dict(v) for k, v in agg.items()}, 'porModo': {k: dict(v) for k, v in by_mode.items()}, 'icones': dict(icons), 'menus': menus, 'menusProprios': own_menus, 'itensMenu': collections.Counter(menu_items).most_common(60),
       'divergeModo': mismatch, 'cartoesSemFoco': [cards_nofocus, cards_total], 'linhasSemFoco': [rows_nofocus, rows_total], 'tabelasProprias': dict(own_tables), 'estatico': static, 'telas': screens}
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=0)
for k, v in res['agg'].items(): print(k, v)
print('por modo', res['porModo']); print('ícones', res['icones'], 'menus', menus, 'menus próprios', len(own_menus))
print('diverge entre modos', len(mismatch)); print('cartões sem foco', res['cartoesSemFoco'], 'linhas sem foco', res['linhasSemFoco']); print('tabelas próprias', res['tabelasProprias'])
print('estático', static)
