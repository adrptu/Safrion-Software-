"""Resume a saída do robô v3: ações por linha/cartão, formulários (digitado × escolhido × preenchido), lotes e primárias.
Uso: python3 -I summ3.py <dir v3out> <saida.json> <saida.txt>"""
import json, os, re, sys

D, OUTJ, OUTT = sys.argv[1], sys.argv[2], sys.argv[3]
MOD = [('AG', 'Agronomia'), ('PL', 'Planejamento'), ('CA', 'Calendário e aprovações'), ('OS', 'Ordens de serviço'), ('SU', 'Suprimentos'), ('MA', 'Manutenção'),
       ('IR', 'Irrigação'), ('CO', 'Colheita e pós-colheita'), ('COLH', 'Colheita e pós-colheita'), ('BEN', 'Beneficiamento'), ('EST', 'Estoque'), ('EXPED', 'Expedição'), ('CARGA', 'Expedição'),
       ('VE', 'Vendas'), ('VEN', 'Vendas'), ('PT', 'Pátio e balança'), ('LO', 'Logística'), ('GE', 'Gestão e finanças'), ('CD', 'Cadastros'), ('CF', 'Configurações'),
       ('IN', 'Início e mapa'), ('MB', 'App de campo'), ('ON', 'Implantação'), ('BO', 'Implantação'), ('MOD', 'Módulos'), ('P', 'Painéis por perfil'), ('SAF', 'Safra'), ('IC', 'Indicadores'), ('IV', 'Inventário'), ('CMP', 'Compras'), ('PROD', 'Produção')]
def modulo(n):
    for p, m in sorted(MOD, key=lambda x: -len(x[0])):
        if n == p or n.startswith(p + '-') or (p == 'P' and re.fullmatch(r'P[A-Z]+', n)):
            return m
    return 'Outros'
TYPED = {'text', 'number', 'textarea', 'search', 'tel', 'email', 'textbox'}
CHOSEN = {'select', 'radio', 'checkbox', 'radiogroup', 'switch', 'combobox', 'listbox', 'date', 'time', 'datetime-local', 'month', 'range'}
FILTER = re.compile(r'^(filtrar|buscar|trocar perfil|ordenar|pesquisar)', re.I)
def classify(f):
    t = f.get('type', 'text'); l = f.get('l', '')
    if FILTER.search(l):
        return 'filtro'
    if f.get('ro') or f.get('dis'):
        return 'calculado'
    if t in ('radio', 'checkbox'):
        return 'escolhido'
    if t in TYPED and (f.get('datalist') or f.get('combo')):
        return 'escolhido'
    if t in CHOSEN:
        return 'escolhido' if not f.get('v') else 'escolhido'
    if t in TYPED:
        return 'pre' if f.get('v') else 'digitado'
    return 'outro'
rows_out, forms, rowacts, batches, prims, cards = [], [], [], [], [], []
for fn in sorted(os.listdir(D)):
    if not fn.endswith('.json') or fn.endswith('.err.json') or fn.endswith('.inv2.json'):
        continue
    d = json.load(open(os.path.join(D, fn)))
    n, inv = d['screen'], d['inv']; m = modulo(n)
    if len(inv.get('primary', [])) > 1:
        prims.append({'tela': n, 'modulo': m, 'nivel': 'tela', 'primarias': inv['primary']})
    for ti, t in enumerate(inv.get('tables', [])):
        for r in t['rows'][:3]:
            acts = [a for a in r['acts'] if a['tag'] in ('button', 'link') and not re.match(r'^(expandir|recolher|▸|▾|selecionar)', a['t'], re.I)]
            if acts:
                rowacts.append({'tela': n, 'modulo': m, 'onde': 'linha da tabela ' + str(ti + 1), 'colunas': ' · '.join(t['heads'][:6]), 'acoes': [a['t'] for a in acts], 'n': len(acts), 'kebab': r['kebab'], 'clicavel': r['clickable'], 'exemplo': r['text'][:80]})
                break
        if t.get('selectAll'):
            batches.append({'tela': n, 'modulo': m, 'tabela': ' · '.join(t['heads'][:5])})
    for c in inv.get('cards', [])[:3]:
        acts = [a for a in c['acts'] if not re.match(r'^(expandir|recolher|▸|▾)', a, re.I)]
        if len(acts) >= 2:
            cards.append({'tela': n, 'modulo': m, 'acoes': acts, 'n': len(acts), 'kebab': c['kebab'], 'exemplo': c['text'][:80]})
    for b in d.get('batch', []):
        batches.append({'tela': n, 'modulo': m, 'lote': [x['t'] for x in b['newBtns']][:10], 'barra': b.get('bar', '')})
    for r in d['results']:
        dl = r.get('dlg')
        flds = (dl or {}).get('fields') or r.get('fields') or []
        if not flds and not dl:
            continue
        cls = [classify(f) for f in flds]
        real = [f for f, c in zip(flds, cls) if c != 'filtro']
        if not real and not dl:
            continue
        cnt = {k: sum(1 for c in cls if c == k) for k in ('digitado', 'escolhido', 'pre', 'calculado', 'outro')}
        nums = [f for f in real if re.search(r'(quant|dose|área|area|peso|valor|preço|preco|litro|horímetro|horimetro|km|umidade|impureza|volume|kg|ha\b|mm)', f.get('l', ''), re.I)]
        dates = [f for f in real if f.get('type') in ('date', 'datetime-local') or re.search(r'\bdata\b', f.get('l', ''), re.I)]
        pb = [b['t'] for b in (dl or {}).get('btns', []) if b.get('primary')]
        if len(pb) > 1:
            prims.append({'tela': n, 'modulo': m, 'nivel': 'modal: ' + ((dl or {}).get('title') or r['cand'])[:60], 'primarias': pb})
        forms.append({'tela': n, 'modulo': m, 'acao': r['cand'][:70], 'tipo': r.get('kind'), 'titulo': ((dl or {}).get('title') or '')[:90], 'campos': len(real),
                      'digitados': cnt['digitado'], 'escolhidos': cnt['escolhido'], 'preenchidos': cnt['pre'], 'calculados': cnt['calculado'],
                      'obrigatorios': sum(1 for f in real if f.get('req')), 'numericos': len(nums), 'numSemTeclado': sum(1 for f in nums if f.get('type') != 'number' and not f.get('inputmode')),
                      'numSemUnidade': sum(1 for f in nums if not f.get('unit')), 'datas': len(dates), 'datasSemAtalho': sum(1 for f in dates if not f.get('chips')),
                      'botoes': [b['t'] for b in (dl or {}).get('btns', [])][:12], 'primarias': pb,
                      'lista': [{k: f.get(k) for k in ('l', 'type', 'v', 'req', 'ro', 'unit', 'inputmode', 'nOpt', 'chips', 'datalist', 'combo') if f.get(k) not in (None, '', False)} for f in real][:30]})
json.dump({'forms': forms, 'rowacts': rowacts, 'cards': cards, 'batches': batches, 'prims': prims}, open(OUTJ, 'w'), ensure_ascii=False)
with open(OUTT, 'w') as o:
    o.write('telas %d · formulários/painéis %d · linhas com botões %d · cartões com 2+ botões %d · lotes %d · contextos com 2+ primárias %d\n' % (len(set(f['tela'] for f in forms) | set(r['tela'] for r in rowacts)), len(forms), len(rowacts), len(cards), len(batches), len(prims)))
    o.write('\n## AÇÕES NA LINHA\n')
    for r in rowacts:
        o.write('%s | %s | %d ações %s | kebab=%s | %s\n' % (r['tela'], r['onde'], r['n'], r['acoes'], r['kebab'], r['exemplo'][:50]))
    o.write('\n## CARTÕES\n')
    for r in cards:
        o.write('%s | %d ações %s | kebab=%s | %s\n' % (r['tela'], r['n'], r['acoes'], r['kebab'], r['exemplo'][:50]))
    o.write('\n## LOTES\n')
    for r in batches:
        o.write('%s\n' % json.dumps(r, ensure_ascii=False))
    o.write('\n## PRIMÁRIAS MÚLTIPLAS\n')
    for r in prims:
        o.write('%s | %s | %s\n' % (r['tela'], r['nivel'], r['primarias']))
    o.write('\n## FORMULÁRIOS (campos: digitados/escolhidos/preenchidos/calculados)\n')
    for f in forms:
        if f['campos']:
            o.write('%s | %s → %s | %d campos: %d dig / %d esc / %d pré / %d calc | req %d | num %d (sem teclado %d, sem unidade %d) | datas %d (sem atalho %d) | prim %s\n   %s\n' % (
                f['tela'], f['acao'][:40], f['titulo'][:50], f['campos'], f['digitados'], f['escolhidos'], f['preenchidos'], f['calculados'], f['obrigatorios'], f['numericos'], f['numSemTeclado'], f['numSemUnidade'], f['datas'], f['datasSemAtalho'], f['primarias'],
                ' ; '.join('%s[%s%s%s]' % (x.get('l', '')[:30], x.get('type'), '=' + str(x.get('v'))[:15] if x.get('v') else '', ' ' + x['unit'] if x.get('unit') else '') for x in f['lista'][:14])))
print(open(OUTT).read()[:400])
