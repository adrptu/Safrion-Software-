# -*- coding: utf-8 -*-
"""TABELAS-FOCO-20261004 v2 (5983172395) · Cadastros e Irrigação · regras sem navegador (roda depois do build.py, lê project/).
(A) Estrutura das grades G2 publicadas (CD-01..CD-07, CD-01det, IR-01..IR-04, IR-03det, e as colunas por papel do CD-05): rótulo com
    uma variável (sem " · ", " / ", " e "), unidade na célula (data-un) e não no cabeçalho, sem "u"/"pre" antigos, custo como "Custo R$/h".
(B) Auxiliares Python: vazão do documento em m³/h (L/s × 3,6), Outorga × Certidão, parcelas do talhão só com as safras da fazenda dele.
(C) Funções JS das páginas geradas, no node: documento e situação do ponto de água (sem a data na situação), situação de cada papel do
    parceiro, cultura × estádio do setor, o instante ISO que ordena "ontem/hoje/amanhã" e a Pendência sem repetir a Situação.
    (B4: cada grandeza da fonte de clima/sensor com a sua unidade; B5: a unidade do sensor novo vem da grandeza, sem campo no formulário.)
Uso: python3 tabelas_cad_irr_unit.py   (sai com 1 se alguma regra falhar)"""
import os, re, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from tabelas_inventario import grids
P = os.path.join(HERE, 'project')
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('OK    ' if cond else 'FALHA ') + n + ('' if cond else ' · ' + str(info)[:400]), flush=True)

ESCOPO = {'CD-01': ['g_tal', 'g_amb', 'g_agua'], 'CD-01det': ['g_idt', 'g_parc'], 'CD-02': ['g_cv', 'g_rend'], 'CD-03': ['g_atv'], 'CD-04': ['g_pes'],
          'CD-05': ['g_forn', 'g_cob'], 'CD-06': ['g_itm', 'g_loc'], 'CD-07': ['g_dim'], 'IR-01': ['g_set'], 'IR-02': ['g_ag'], 'IR-03': ['g_os'],
          'IR-03det': ['g_pas', 'g_trl'], 'IR-04': ['g_src', 'g_cap', 'g_des']}
R_ROT = re.compile(r'\s·\s|\s/\s|\se\s', re.I)
UNID = {'ha', '%', 'R$', 'ha/h', 'R$/h', 'R$/ha', 'R$/kg', 'm', 'km/h', 'h', 'L', 'kg', 't', 'sc', 'mm', 'dias', 'L/s', 'm³', 'm³/h', 'kWh', 'h/dia', 'cv'}
def page(n): return open(os.path.join(P, n + '.dc.html'), encoding='utf-8').read()

# ---------------- (A) estrutura ----------------
cols_todas = []
for pg, gids in ESCOPO.items():
    html = page(pg); gs = {g['id']: g for g in grids(html)}
    falta = [g for g in gids if g not in gs]
    chk(f'A1 {pg}: grades {", ".join(gids)} publicadas', not falta, falta)
    for gid in gids:
        for c in (gs.get(gid) or {}).get('cols', []): cols_todas.append((pg, gid, c))
# colunas por papel do CD-05 (trocam no navegador; vêm do JS da página)
h5 = page('CD-05'); i5 = h5.find('COLS_P=')
colsp = json.JSONDecoder().raw_decode(h5[i5 + 7:])[0] if i5 >= 0 else {}
chk('A1 CD-05: colunas por papel (Fornecedor, Cliente, Parceiro de crédito, Transportador, Prestador) publicadas', set(colsp) == {'Fornecedor', 'Cliente', 'Parceiro de crédito', 'Transportador', 'Prestador'}, list(colsp))
for papel, cs in colsp.items():
    for c in cs: cols_todas.append(('CD-05 ' + papel, 'g_forn', c))
# coluna "Motivo da suspensão": entra só quando há parceiro suspenso no filtro (nunca fica sempre vazia)
im = h5.find('COL_MOT='); colm = json.JSONDecoder().raw_decode(h5[im + 8:])[0] if im >= 0 else {}
chk('A1 CD-05: coluna dinâmica "Motivo da suspensão" publicada', colm.get('l') == 'Motivo da suspensão', colm)
if colm: cols_todas.append(('CD-05 suspenso', 'g_forn', colm))
comp = [(pg, gid, c['l']) for pg, gid, c in cols_todas if R_ROT.search(re.sub(r'\([^)]*\)', '', c.get('l') or ''))]
chk(f'A2 {len(cols_todas)} colunas: nenhum rótulo composto (" · ", " / ", " e ")', not comp, comp)
velho = [(pg, gid, c['l']) for pg, gid, c in cols_todas if c.get('t') == 'num' and (c.get('u') or c.get('pre'))]
chk('A3 nenhuma coluna numérica com a unidade só no formato antigo (u/pre): a unidade vai na célula com data-un', not velho, velho)
parent = [(pg, gid, c['l']) for pg, gid, c in cols_todas if re.search(r'\(([^()]+)\)\s*$', c.get('l') or '') and re.search(r'\(([^()]+)\)\s*$', c['l']).group(1) in UNID]
chk('A3 nenhum cabeçalho com unidade entre parênteses ("Área (ha)")', not parent, parent)
custo = [(pg, gid, c['l'], c.get('un')) for pg, gid, c in cols_todas if str(c.get('un', '')).startswith('R$/') and c['l'] != 'Custo ' + c['un'] and c['l'] != 'Preço ' + c['un']]
chk('A4 custo por unidade rotulado "Custo R$/h", "Custo R$/ha"', not custo, custo)
semun = [(pg, gid, c['l']) for pg, gid, c in cols_todas if c.get('t') == 'num' and not c.get('un') and c['k'] in ('area', 'decl', 'calc', 'difp', 'rend', 'custo_h', 'custo_ha', 'larg', 'vel', 'efic', 'def', 'nec', 'lam', 'ls', 'vol', 'kwh', 'ef', 'dur', 'cob', 'dias', 'largn', 'custo', 'lim', 'ha', 'resta', 'pct', 'h', 'var')]
chk('A5 colunas de medida (área, lâmina, vazão, custo…) com a unidade na célula (data-un)', not semun, semun)
dt = {(pg, c['k']) for pg, gid, c in cols_todas if c.get('t') == 'date'}
chk('A6 datas e instantes tipados como data (ordenam por data): vencimento, plantio, início e fim, quando, atualização, validade',
    {('CD-01', 'venc'), ('CD-01det', 'plantio'), ('CD-03', 'calv'), ('CD-04', 'habv'), ('CD-06', 'pdata'), ('CD-07', 'ini'), ('CD-07', 'fim'), ('IR-01', 'pps'), ('IR-02', 'ini'), ('IR-03', 'fim'),
     ('IR-03det', 'hora'), ('IR-04', 'at'), ('IR-04', 'venc')} <= dt, sorted(dt))

# ---------------- (B) auxiliares Python ----------------
from areas import cad_fazendas as CF
def tenta(f, *a):
    """chama o auxiliar; ausente ou com erro (ex.: na base 24da80b) vira a mensagem, e a verificação falha em vez de interromper o teste"""
    try: return f(*a)
    except Exception as e: return 'ERRO ' + type(e).__name__ + ': ' + str(e)[:120]
AUS = lambda nome: (lambda *a: (_ for _ in ()).throw(AttributeError(nome + ' ausente')))
casos = [('180 m³/h', 180.0), ('1,0 L/s', 3.6), ('0,5 L/s', 1.8), ('—', ''), ('', '')]
r = [(t, tenta(getattr(CF, '_vazao_m3h', AUS('_vazao_m3h')), t)) for t, _ in casos]
chk('B1 vazão do documento em m³/h para ordenar: 180 m³/h → 180; 1,0 L/s → 3,6; "—" → vazio', all(abs(a - b) < 1e-9 if isinstance(b, float) and isinstance(a, float) else a == b for (_, a), (_, b) in zip(r, casos)), r)
r = [tenta(getattr(CF, '_doc_agua', AUS('_doc_agua')), x) for x in ('Outorga', 'Outorga estadual', 'Certidão de uso insignificante', '')]
chk('B2 documento do ponto de água: Outorga × Certidão (de uso insignificante); sem tipo fica vazio', r == ['Outorga', 'Outorga', 'Certidão', ''], r)
pr = tenta(getattr(CF, '_parc_rows', AUS('_parc_rows')), ['T1'], 'Santa Rita')
safras = [g['v']['safra'] for g in pr[0]] if isinstance(pr, tuple) else [pr]
chk('B3 parcelas do T1 (Santa Rita) só com safras da Santa Rita (sem a Safra Mamão da Lagoa Grande)', isinstance(pr, tuple) and safras and not any('Mamão' in x for x in safras), safras)

# ---------------- (C) funções JS das páginas, no node ----------------
def func(html, nome):
    if 'function ' + nome + '(' not in html: return 'function ' + nome + '(){ throw new Error(' + json.dumps(nome + ' ausente na página') + '); }'
    i = html.index('function ' + nome + '('); j = html.index('{', i); n = 0
    for k in range(j, len(html)):
        n += {'{': 1, '}': -1}.get(html[k], 0)
        if n == 0: return html[i:k + 1]
    raise ValueError(nome)
def node(src):
    r = subprocess.run(['node', '-e', src], capture_output=True, text=True, timeout=60)
    if r.returncode: print((r.stderr.strip().splitlines() or [''])[-1][:300])
    try: return json.loads(r.stdout or 'null')
    except ValueError: return None
h1 = page('CD-01')
js1 = "const HOJE='2026-09-23';\n" + '\n'.join(func(h1, f) for f in ('chipc', 'br', 'ddiff', 'sitOk', 'sitInfo', 'sitX', 'aguaDoc', 'aguaSit')) + r"""
const T=(V)=>{ const s=aguaSit(V); return [s.t,s.p.map(p=>p.t).join(' ')]; };
console.log(JSON.stringify({doc:[aguaDoc({tipo:'Outorga',num:'SINT-003/0000'}),aguaDoc({tipo:'Certidão de uso insignificante',num:'SINT-006/0000'}),aguaDoc({tipo:'',num:'X'})],
  vig:T({tipo:'Outorga',venc:'2031-04-30'}),venc:T({tipo:'Outorga',venc:'2026-05-10'}),av:T({tipo:'Outorga',venc:'2026-11-20'}),ren:T({tipo:'Outorga',venc:'2025-12-01',renov:'SINT-REN-004'})}));"""
u1 = node(js1) or {}
chk('C1 documento da água: outorga é "Outorga …" (antes saía "Certidão …"); certidão é "Certidão …"', u1.get('doc') == ['Outorga SINT-003/0000', 'Certidão SINT-006/0000', ''], u1.get('doc'))
chk('C2 situação da água só com o estado e o próximo passo (a data fica em Vencimento; o processo no painel)',
    [u1.get(k) for k in ('vig', 'venc', 'av', 'ren')] == [['Vigente', 'Vigente'], ['Vencida', 'Vencida Renovar ›'], ['Vence em 90 dias', 'Vence em 90 dias Renovar ›'], ['Em renovação', 'Em renovação']], [u1.get(k) for k in ('vig', 'venc', 'av', 'ren')])
h5 = page('CD-05')
js5 = "const HOJE='2026-09-23';\n" + func(h5, 'ml') + '\n' + func(h5, 'sitPapeis') + r"""
const S=(V,so)=>sitPapeis(V,String(V.papeis).split('; '),so).map(x=>x.t);
console.log(JSON.stringify([S({papeis:'Fornecedor; Cliente',homol:'Sim',lim:1500000,limv:'2027-06-30'}),S({papeis:'Cliente',lim:40000,limv:'2026-08-31'}),S({papeis:'Cliente',lim:''}),
  S({papeis:'Fornecedor',homol:'Não'}),S({papeis:'Transportador',rntrc:''}),S({papeis:'Fornecedor; Cliente',homol:'Sim',sit:'Suspenso'}),S({papeis:'Fornecedor; Cliente',homol:'Sim',lim:1,limv:'2027-01-01'},'Cliente')]));"""
u5 = node(js5) or []
chk('C3 situação por papel (só o estado; o valor fica na coluna do papel): dois papéis = dois estados; vencido, sem limite, não homologado, sem RNTRC, suspenso; filtro de um papel mostra só o dele',
    u5 == [['Homologado', 'Limite vigente'], ['Limite vencido'], ['Sem limite de crédito'], ['Não homologado'], ['Sem RNTRC'], ['Suspenso'], ['Limite vigente']], u5)
hi = page('IR-01')
m0 = re.search(r'IRR_D0\s*=\s*Date\.UTC\(2026, 8, 23\);', hi)
jsi = 'const IRR_D0=Date.UTC(2026, 8, 23);\n' + '\n'.join(func(hi, f) for f in ('irrN', 'irrHm', 'irrDiaN', 'irrDdmm', 'irrIso', 'irrDiaT', 'irrQuando', 'irrIsoM', 'irrCultEst')) + r"""
const m=(d,hh)=>d*1440+Number(hh.split(':')[0])*60+Number(hh.split(':')[1]);
const xs=[[-4,'14:00'],[-1,'20:00'],[0,'14:00'],[0,'20:00'],[1,'10:31'],[2,'11:15']].map(([d,h])=>m(d,h));
console.log(JSON.stringify({ce:[irrCultEst({cult:'Milho V10'}),irrCultEst({cult:'Feijão R5'}),irrCultEst({cult:'Mamão'}),irrCultEst({cult:'Mamão · produção',fase:'produção'}),irrCultEst({cult:'Mamão · plantio previsto',fase:'preparo de área'})],
  iso:xs.map(irrIsoM), txt:xs.map(irrQuando), vazio:irrIsoM(null)}));"""
ui = node(jsi) or {}
chk('C4 cultura × estádio do setor: Milho | V10, Feijão | R5, Mamão | (vazio), Mamão | fase do mamão (Lagoa Grande)',
    ui.get('ce') == [{'c': 'Milho', 'e': 'V10'}, {'c': 'Feijão', 'e': 'R5'}, {'c': 'Mamão', 'e': ''}, {'c': 'Mamão', 'e': 'produção'}, {'c': 'Mamão', 'e': 'preparo de área'}], ui.get('ce'))
iso, txt = ui.get('iso') or [], ui.get('txt') or []
chk('C5 instante ISO ordena no tempo (19/09 < ontem < hoje < amanhã < 25/09) e a célula mostra o texto relativo',
    m0 is not None and len(iso) == 6 and iso == sorted(iso) and iso[0] == '2026-09-19 14:00' and iso[3] == '2026-09-23 20:00' and txt[1:5] == ['ontem 20:00', 'hoje 14:00', 'hoje 20:00', 'amanhã 10:31'] and ui.get('vazio') == '', (iso, txt))
chk('C6 pelo texto a ordem sairia errada ("amanhã" < "hoje" < "ontem"): por isso o valor que ordena é o ISO', len(txt) == 6 and sorted(txt[1:5]) != txt[1:5], sorted(txt[1:5]))
jsp = func(hi, 'irrPend') + '\n' + func(hi, 'irrPendFert') + r"""
console.log(JSON.stringify({p:irrPend([{t:'Impedida · bomba parada',c:'red'},{t:'Falta insumo · Ureia 45%',c:'red'},{t:'Conflito · parada da B3',c:'red'},{t:'Janela a definir',c:'yellow'}]).map(x=>[x.t,x.c]),
  f:irrPendFert({t:'Impedida · bomba parada',dono:'Manutenção'}).map(x=>x.t), n:irrPendFert(null)}));"""
up = node(jsp) or {}
chk('C7 Pendência sem repetir a Situação: "Impedida · bomba parada" → "Bomba parada" (cor mantida); falta insumo, conflito e janela ficam como estão; sem bloqueio = lista vazia',
    up.get('p') == [['Bomba parada', 'red'], ['Falta insumo · Ureia 45%', 'red'], ['Conflito · parada da B3', 'red'], ['Janela a definir', 'yellow']] and up.get('f') == ['Bomba parada'] and up.get('n') == [], up)
import dados_irrigacao as DI
desc = [(k, f['gr'], f['un']) for k, f in DI.FONTES.items() if len(f['gr'].split(' / ')) != len(f['un'].split(' · '))]
chk('B4 cada grandeza da fonte tem a sua unidade, na mesma ordem (a estação: ET₀, chuva e vento → mm/dia, mm e km/h)', not desc, desc)
# B5: "Cadastrar sensor" não pede a unidade; ela vem da grandeza (UN_GR) e é a mesma da semente para a mesma grandeza (antes: Volume | % vol.)
h4 = page('IR-04'); ed = ({g['id']: g for g in grids(h4)}.get('g_src') or {}).get('edit') or {}
fk = [f['k'] for f in ed.get('fields', [])]; ops = next((f.get('opts') for f in ed.get('fields', []) if f['k'] == 'gr'), []) or []
iu = h4.find('UN_GR='); ung = dict(re.findall(r"'([^']+)':'([^']*)'", h4[iu:h4.index(';', iu)])) if iu >= 0 else {}
dif = [(k, f['gr'], f['un'], ung.get(f['gr'])) for k, f in DI.FONTES.items() if f['gr'] in ung and ung[f['gr']] != f['un']]
chk('B5 cadastrar sensor: o formulário não pede Unidade; cada grandeza do seletor tem a sua unidade (UN_GR) e ela é a mesma da semente',
    'un' not in fk and 'gr' in fk and ops and all(o in ung for o in ops) and not dif, (fk, ops, ung, dif))
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
