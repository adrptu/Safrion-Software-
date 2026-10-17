# -*- coding: utf-8 -*-
"""Comparação caso a caso dos brutos: base v5 (259c13bc, modo isolado) × linha de base v5.1, na mesma candidata.

Chave da passagem: (tela, tipo do elemento, texto, href). O robô deduplica as passagens de uma tela por (texto, href),
então a chave é única por tela. Para cada passagem nas duas medidas, recalcula a chegada com o critério de cada método
(o do resumo v5 e o do resumo v5.1, copiados sem mudança de regra) e dá a razão de cada diferença.
Também compara as referências (IDs) de cada detalhe, por (tela, linha).

Uso: python3 -I comparar_casos.py <brutos v5> <navegacao v5> <brutos v5.1> <navegacao v5.1> <ocultas.json> <saida.json>"""
import collections, json, os, re, sys

B5, NAV5, B51, NAV51, OC, OUT = sys.argv[1:7]
oc = json.load(open(OC, encoding='utf-8'))
SAI = {o['tela'] for o in oc if o.get('decisao') == 'Excluir'}
ENTR5 = re.compile(r'\b(OS|PV|VIS|OM|PC|REQ|OC|CT|CG|OB|CRE|REC|INSP|RC|OF|RT|VG|LAU|TK|TR|NEC|DIA|LC|VD|MV|INV|EF|CMD|AC|COT|AGS|FAT|AM|AU|PD|DV|NC|SM|NEG|EX|DEC|CR|ES|LM|CON|RM)-\d{2,5}[A-Z]?\b')
ENTR51 = re.compile(r'\b(OS|PV|VIS|OM|PC|REQ|OC|CT|CG|OB|CRE|REC|RA|INSP|RC|OF|RT|VG|LAU|TK|TR|NEC|DIA|LC|VD|MV|INV|EF|AC|COT|AGS|FAT|AM|AU|PD|DV|NC|SM|NEG|CR|ES|LM|CON|RM)-\d{2,5}[A-Z]?\b')


def ler(D):
    pas, det, err = {}, {}, []
    for f in sorted(os.listdir(D)):
        if f.endswith('.v5err.json'):
            err.append(f)
        if not f.endswith('.v5.json') or f.startswith('escopo'):
            continue
        d = json.load(open(os.path.join(D, f), encoding='utf-8')); t = d['screen']
        if t in SAI or t.startswith('MOD-') or t == 'CD':
            continue
        for x in d.get('detalhes', []):
            det[(t, x.get('linha'))] = x
        for i, p in enumerate(d.get('passagens', [])):
            k = (t, p['el'].get('k'), p['el']['t'], p['el'].get('h') or '')
            pas[k] = dict(p, tela=t, i=i)
    chk = {}
    ck = os.path.join(D, 'leva-check.json')
    if os.path.exists(ck):
        for x in json.load(open(ck, encoding='utf-8')):
            chk[(x['tela'], x['i'])] = x
    return pas, det, chk, err


P5, D5, C5, E5 = ler(B5)
P51, D51, C51, E51 = ler(B51)
TIT5 = {r['tela']: r['titulo'] for r in json.load(open(NAV5, encoding='utf-8'))['rows']}


def chegou5(p):   # critério do anexo-robo-v5-resumo.py (v5), sem mudança
    CHK = {k: bool(x['dlg']) or x['alvoNoH1'] or ('#' in x['url'] and (x['alvoNoCorpo'] or bool(x['tokNoCorpo']))) for k, x in C5.items()}
    leva = ('#' in (p['el'].get('h') or '')) or bool(ENTR5.search(p['el']['t'])) or ('#' in (p.get('para') or ''))
    if (p['tela'], p.get('i')) in CHK: return CHK[(p['tela'], p['i'])], '2ª passada v5'
    if CHK and not leva: return False, 'não leva'
    alvo, org = p.get('alvo') or '', p.get('origemId') or ''
    para = p.get('para') or ''; dest = para.split('#')[0]; h = para.split('#', 1)[1] if '#' in para else ''
    if p.get('abriu'): return True, 'título (includes)'
    if p.get('destacou'): return True, 'seleção/foco (includes)'
    if p.get('dlgOrigem'): return True, 'diálogo com o ID da ORIGEM'
    foco = p.get('foco') or ''
    if (alvo and alvo in foco) or (org and org in foco): return True, 'foco'
    if alvo and any(alvo in a for a in p.get('avisos') or []): return True, 'aviso'
    if alvo and alvo in TIT5.get(dest, ''): return True, 'título da página'
    if h and re.search(r'(det|x-[a-z0-9-]+|-app|-ficha)$', dest): return True, 'página de registro pelo endereço'
    return bool(not alvo and p.get('titulo')), ('sem alvo e diálogo aberto' if (not alvo and p.get('titulo')) else 'nenhum')


def chegou51(p):   # critério do resumo.py (v5.1), sem mudança
    if not p.get('alvo'): return False, 'sem alvo'
    if p.get('abriu'): return True, 'título (ID exato)'
    if p.get('destacou'): return True, 'seleção (ID exato)'
    x = C51.get((p['tela'], p.get('i')))
    if x and x.get('chegouEstrito') is True: return True, '2ª passada estrita'
    return False, 'não chegou'


def isrec5(p):
    return p.get('r') == 'navega' and (p.get('origem') == 'detalhe' or bool(p.get('alvo')) or '#' in (p.get('para') or ''))


def isrec51(p):
    return p.get('r') == 'navega' and bool(p.get('alvo'))


casos = []
for k in sorted(set(P5) | set(P51)):
    a, b = P5.get(k), P51.get(k)
    c = {'tela': k[0], 'k': k[1], 'clique': k[2], 'href': k[3]}
    if not a or not b:
        c['razao'] = ['só na base v5' if a else 'só na v5.1'] + ['amostra: a passagem não foi listada na outra execução (ordem/visibilidade da tela)']
        c['v5'] = a and {x: a.get(x) for x in ('r', 'para', 'alvo')}
        c['v51'] = b and {x: b.get(x) for x in ('r', 'para', 'alvo', 'esperado')}
        casos.append(c); continue
    r5, r51 = a.get('r'), b.get('r')
    ch5, m5 = chegou5(a) if isrec5(a) else (None, 'fora do denominador v5')
    ch51, m51 = chegou51(b) if isrec51(b) else (None, 'inconclusiva' if (r51 == 'navega' and not b.get('alvo')) else 'fora do denominador v5.1')
    c.update({'v5': {'r': r5, 'para': a.get('para'), 'alvo': a.get('alvo'), 'chegou': ch5, 'como': m5, 'volta': a.get('voltaOrigem'), 'reabre': (a.get('voltar') or {}).get('detalheReaberto') if a.get('origem') == 'detalhe' else None},
              'v51': {'r': r51, 'para': b.get('para'), 'alvo': b.get('alvo'), 'fonte': (b.get('esperado') or {}).get('source'), 'chegou': ch51, 'como': m51, 'volta': b.get('voltaOrigem'),
                      'reabre': (b.get('voltar') or {}).get('detalheReaberto') if b.get('origem') == 'detalhe' else None, 'empilhado': b.get('empilhado')}})
    raz = []
    if r5 != r51:
        raz.append(f'comportamento: v5 "{r5}" × v5.1 "{r51}" (mesma candidata: variação entre execuções ou espera)')
    if r5 == r51 == 'navega' and (a.get('para') or '') != (b.get('para') or ''):
        raz.append(f'destino diferente: {a.get("para")} × {b.get("para")}')
    al5, al51 = a.get('alvo') or '', b.get('alvo') or ''
    if al5 != al51:
        if not al51:
            raz.append(f'alvo: v5 inferia "{al5}" (hash do destino ou texto); v5.1 sem alvo único na origem ({(b.get("esperado") or {}).get("source")}) → inconclusiva')
        elif not al5:
            raz.append(f'alvo: v5.1 captura "{al51}" na origem; v5 não tinha alvo')
        else:
            raz.append(f'alvo: v5 "{al5}" (do destino) × v5.1 "{al51}" (da origem, {(b.get("esperado") or {}).get("source")})')
    if ch5 != ch51:
        if ch5 and ch51 is False:
            raz.append(f'chegada: v5 aceitava por "{m5}"; v5.1 recusa ({m51})')
        elif ch5 and ch51 is None:
            raz.append(f'denominador: v5 contava (chegou por "{m5}"); v5.1 {m51}')
        elif ch5 is False and ch51 is None:
            raz.append(f'denominador: v5 contava como não chegou; v5.1 {m51}')
        elif ch5 is None and ch51 is not None:
            raz.append(f'denominador: entra na v5.1 ({m51}, chegou={ch51}); fora na v5 ({m5})')
        elif ch5 is False and ch51:
            raz.append(f'chegada: v5.1 aceita por "{m51}"; v5 não ({m5})')
    rb5, rb51 = c['v5']['reabre'], c['v51']['reabre']
    if rb5 != rb51:
        raz.append(f'Voltar: v5 {rb5} × v5.1 {rb51}' + (' (v5.1 exige a mesma tela de origem)' if rb5 and not rb51 and not (b.get('voltar') or {}).get('mesmaTela') else ' (variação entre execuções)'))
    if bool(a.get('voltaOrigem')) != bool(b.get('voltaOrigem')):
        raz.append(f'volta à origem: v5 {a.get("voltaOrigem")} × v5.1 {b.get("voltaOrigem")} (mesmo critério nos dois: variação entre execuções)')
    c['razao'] = raz or ['igual']
    casos.append(c)

# referências (IDs) por detalhe
refs = []
for k in sorted(set(D5) | set(D51), key=str):
    a, b = D5.get(k) or {}, D51.get(k) or {}
    if a.get('titulo') is None and b.get('titulo') is None:
        continue
    ra, rb = a.get('refs') or {}, b.get('refs') or {}
    for i in sorted(set(ra) | set(rb)):
        x, y = ra.get(i), rb.get(i)
        if x == y:
            continue
        pre = i.split('-')[0]
        if x and not y:
            raz = f'prefixo {pre} saiu do denominador (CMD/EX/DEC)' if pre in ('CMD', 'EX', 'DEC') else 'só na base v5 (variação)'
        elif y and not x:
            raz = 'prefixo RA entrou no denominador' if pre == 'RA' else 'só na v5.1 (variação)'
        else:
            raz = 'contagem diferente (variação)'
        refs.append({'tela': k[0], 'linha': k[1], 'titulo5': a.get('titulo'), 'titulo51': b.get('titulo'), 'id': i, 'v5': x, 'v51': y, 'razao': raz})

cont = collections.Counter()
for c in casos:
    for r in c['razao']:
        cont[re.sub(r'"[^"]*"|\([^)]*\)|\S+-\d+\S*|[A-Z][A-Za-z0-9-]*#\S+', '…', r)[:90]] += 1
res = {'chave': 'tela|k|texto|href', 'passagens_v5': len(P5), 'passagens_v51': len(P51), 'erros_v5': E5, 'erros_v51': E51,
       'iguais': sum(1 for c in casos if c['razao'] == ['igual']), 'diferentes': sum(1 for c in casos if c['razao'] != ['igual']),
       'razoes': cont.most_common(), 'refsDiferentes': collections.Counter(r['razao'] for r in refs).most_common(), 'casos': casos, 'refs': refs}
json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ('casos', 'refs')}, ensure_ascii=False, indent=1))
