"""Resume o robô v5 (passagens entre telas). Uso: python3 -I v5summ.py <v5out> <ocultas.json> <v3 (telas)> <saida.json>
Conta só as telas que ficam no sistema (exclui as marcadas Excluir em ocultas.json e as que só redirecionam)."""
import json, os, re, sys, collections
D, OC, V3, OUT = sys.argv[1:5]
oc = json.load(open(OC, encoding='utf-8'))
sai = {o['tela'] for o in oc if o.get('decisao') == 'Excluir'}
QUEM = re.compile(r'\b(Ana|Caio|Rui|Paula|Zé|Otávio|João|Igor|Dora|Marta|Lúcia|Marcos|agrônom\w*|almoxarif\w*|PCP|confer\w*|mecânic\w*|comercial|qualidade|compras|comprador\w*|suprimentos|manutenção|gestor\w*|operador\w*|responsável|motorista|expedição|produção)\b', re.I)
det = []; pas = []; telas = []
for f in sorted(os.listdir(D)):
    if not f.endswith('.v5.json') or f.startswith('escopo'): continue
    d = json.load(open(os.path.join(D, f), encoding='utf-8')); t = d['screen']
    if t in sai or t.startswith('MOD-') or t == 'CD': continue   # hubs só levam às telas, sem registro
    telas.append(t)
    for x in d.get('detalhes', []):
        if x.get('titulo') is not None: det.append(dict(x, tela=t))
    for i, p in enumerate(d.get('passagens', [])):
        if p.get('r') in ('não achou', 'não reabriu', 'erro'): continue
        pas.append(dict(p, tela=t, i=i))
refsT = refsC = rotT = rotC = 0; semPasso = passoT = passoP = 0
for x in det:
    for k, v in (x.get('refs') or {}).items(): refsT += 1; refsC += 1 if v.get('clic') else 0
    for r in x.get('rotulos') or []: rotT += 1; rotC += 1 if r.get('clic') else 0
    ps = x.get('passo') or {}
    if ps.get('tem'): passoT += 1; passoP += 1 if QUEM.search(ps.get('texto') or '') else 0
    else: semPasso += 1
nav = [p for p in pas if p['r'] == 'navega']
NAVJ = os.path.join(os.path.dirname(OC), 'navegacao.json')
TIT = {r['tela']: r['titulo'] for r in json.load(open(NAVJ, encoding='utf-8'))['rows']}
ENTR = re.compile(r'\b(OS|PV|VIS|OM|PC|REQ|OC|CT|CG|OB|CRE|REC|INSP|RC|OF|RT|VG|LAU|TK|TR|NEC|DIA|LC|VD|MV|INV|EF|CMD|AC|COT|AGS|FAT|AM|AU|PD|DV|NC|SM|NEG|EX|DEC|CR|ES|LM|CON|RM)-\d{2,5}[A-Z]?\b')
CHK = {}
_ck = os.path.join(D, 'leva-check.json')   # 2ª passada: abre o endereço do link e espera 2,6 s
if os.path.exists(_ck):
    for x in json.load(open(_ck, encoding='utf-8')):
        CHK[(x['tela'], x['i'])] = bool(x['dlg']) or x['alvoNoH1'] or ('#' in x['url'] and (x['alvoNoCorpo'] or bool(x['tokNoCorpo'])))
def leva(p): return ('#' in (p['el'].get('h') or '')) or bool(ENTR.search(p['el']['t'])) or ('#' in (p.get('para') or ''))
def chegou(p):
    if (p['tela'], p.get('i')) in CHK: return CHK[(p['tela'], p['i'])]
    if CHK and not leva(p): return False
    alvo, org = p.get('alvo') or '', p.get('origemId') or ''
    para = p.get('para') or ''; dest = para.split('#')[0]; h = para.split('#', 1)[1] if '#' in para else ''
    if p.get('abriu') or p.get('destacou') or p.get('dlgOrigem'): return True
    foco = p.get('foco') or ''
    if (alvo and alvo in foco) or (org and org in foco): return True
    if alvo and any(alvo in a for a in p.get('avisos') or []): return True
    if alvo and alvo in TIT.get(dest, ''): return True          # página do próprio registro (AG-04det = REC-014)
    if h and re.search(r'(det|x-[a-z0-9-]+|-app|-ficha)$', dest): return True   # página de registro aberta pelo endereço
    return bool(not alvo and p.get('titulo'))
voltarDet = [p for p in nav if p.get('origem') == 'detalhe']
rec = [p for p in nav if p.get('origem') == 'detalhe' or p.get('alvo') or '#' in (p.get('para') or '')]   # passagens que levam um registro
rows = []
for p in pas:
    if p['r'] == 'navega':
        isrec = p.get('origem') == 'detalhe' or bool(p.get('alvo')) or '#' in (p.get('para') or '')
        c = chegou(p) if isrec else None; v = bool(p.get('voltaOrigem')); rb = (p.get('voltar') or {}).get('detalheReaberto') if p.get('origem') == 'detalhe' else None
        rows.append({'de': p['tela'], 'ctx': '' if p.get('origem') == 'tela' else 'no detalhe', 'clique': p['el']['t'], 'para': p.get('para', ''), 'chegou': c, 'volta': v, 'reabre': rb, 'prob': (c is False) or (not v) or (rb is False)})
    elif p['r'] in ('abre no lugar', 'mesma tela'):
        rows.append({'de': p['tela'], 'ctx': '' if p.get('origem') == 'tela' else 'no detalhe', 'clique': p['el']['t'], 'para': 'no lugar' + (': ' + p['titulo'] if p.get('titulo') else ''), 'chegou': None, 'volta': None, 'reabre': None, 'prob': False})
    elif p['r'] == 'nada':
        rows.append({'de': p['tela'], 'ctx': '' if p.get('origem') == 'tela' else 'no detalhe', 'clique': p['el']['t'], 'para': 'sem efeito em 6 s (conferir)', 'chegou': None, 'volta': None, 'reabre': None, 'prob': False})
# escopo (estático): telas principais com Fazenda/Safra e se a escolha segue para outra tela
PRINC = ['IN-04', 'OS', 'EST', 'MA', 'CMP', 'VEN', 'COLH', 'PA', 'SAF', 'AG-01', 'AG-02', 'AG-07', 'IR-01', 'CARGA', 'BEN', 'PROD', 'GE-02', 'GE-03', 'PAGR', 'PMAN', 'PSUP', 'IC', 'PCOM', 'EXPED', 'IV', 'GE-08', 'MB-05', 'CD-01']
faz = saf = 0
for t in PRINC:
    s = open(os.path.join(V3, t + '.dc.html'), encoding='utf-8').read()
    faz += 'aria-label="Filtrar por fazenda"' in s; saf += 'aria-label="Filtrar por safra"' in s
PROC = {'OS', 'MA', 'EST', 'CMP', 'BEN', 'CARGA', 'COLH', 'PROD', 'VEN', 'EXPED', 'AG-01', 'AG-02', 'IR-01', 'SAF', 'PA', 'MB-05', 'GE-08', 'IN-01', 'IN-02'}
dp = [x for x in det if x['tela'] in PROC]
proc = {'det': len(dp), 'passo': sum(1 for x in dp if (x.get('passo') or {}).get('tem')), 'quem': sum(1 for x in dp if (x.get('passo') or {}).get('tem') and QUEM.search((x['passo'].get('texto') or '')))}
res = {'processo': proc, 'telas': len(telas), 'detalhes': len(det), 'refsTotal': refsT, 'refsClic': refsC, 'rotTotal': rotT, 'rotClic': rotC, 'passagens': len(pas), 'navega': len(nav),
       'noLugar': sum(1 for p in pas if p['r'] in ('abre no lugar', 'mesma tela')), 'nada': sum(1 for p in pas if p['r'] == 'nada'),
       'navRegistro': len(rec), 'naoLeva': sum(1 for p in rec if not leva(p)), 'levaIgnora': sum(1 for p in rec if leva(p) and not chegou(p)), 'chegou': sum(1 for p in rec if chegou(p)), 'voltaOrigem': sum(1 for p in rec if p.get('voltaOrigem')), 'voltarDet': len(voltarDet), 'reabre': sum(1 for p in voltarDet if (p.get('voltar') or {}).get('detalheReaberto')),
       'passoTotal': passoT, 'passoPessoa': passoP, 'semPasso': semPasso, 'escopo': {'telas': len(PRINC), 'faz': faz, 'saf': saf, 'herda': 0}}
top = collections.Counter((r['de'], r['para'].split('#')[0]) for r in rows if r['prob'])
json.dump({'robo': res, 'passagens': rows, 'piores': top.most_common(25)}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(json.dumps(res, ensure_ascii=False))
print('linhas', len(rows), 'com problema', sum(r['prob'] for r in rows))
