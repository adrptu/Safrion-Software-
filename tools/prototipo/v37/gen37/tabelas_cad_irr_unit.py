# -*- coding: utf-8 -*-
"""TABELAS-FOCO-20261004 v2 (5983172395) · Cadastros e Irrigação · regras sem navegador (roda depois do build.py, lê project/).
(A) Estrutura das grades G2 publicadas (CD-01..CD-07, CD-01det, IR-01..IR-04, IR-03det, e as colunas por papel do CD-05): rótulo com
    uma variável (sem " · ", " / ", " e "), unidade na célula (data-un) e não no cabeçalho, sem "u"/"pre" antigos, custo como "Custo R$/h".
(B) Auxiliares Python: vazão do documento em m³/h (L/s × 3,6), Outorga × Certidão, parcelas do talhão só com as safras da fazenda dele.
(C) Funções JS das páginas geradas, no node: documento e situação do ponto de água (sem a data na situação), situação de cada papel do
    parceiro, cultura × estádio do setor, o instante ISO que ordena "ontem/hoje/amanhã" e a Pendência sem repetir a Situação.
    (B4: cada grandeza da fonte de clima/sensor com a sua unidade; B5: a unidade do sensor novo vem da grandeza, sem campo no formulário.)
    Revisão TABR (09/10): C7–C9 pendência com o tipo no chip e o detalhe na dica, sem selo de ordem encerrada, com a ordem quando é outra
    (A11, A6, A2); C10–C11 motivo e verbo da pessoa não alocável e a validade que vence primeiro (A3, M-i); C12–C13 calibração a vencer
    no chip e capacidade só com uma grandeza (A10, A4); B6 versão do estado salvo da irrigação (A9); B7 parcelas da lista = do detalhe
    (PV01 da Lagoa Grande, pré-existente); C14 duração da passada = fim − início da mesma linha (IR-03det, pré-existente).
    TABR-CTX-01 (revisão do Codex, 10/10): C15–C18 filtro, ordem e menu da coluna de capacidade que muda de grandeza (CD-03, CD-06); C17b
    (TABR-CTX-02) o mesmo rótulo com outra unidade (Capacidade sc de 60 kg → kg/h) também muda de grandeza.
    Revisão do TABR-CTX-01 (10/10): C19 (TABR-CTX-02) a coluna Fazenda do IR-01 sai com a fazenda do topo e leva filtro, ordem e menu dela;
    C20 a 1ª coluna presa (g2lib) é refeita só quando a coluna entra ou sai (nº de colunas muda), não a cada desenho nem na troca de grandeza.
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
# B1b (revisão TABR, mutante M-a): na grade publicada, a chave que ordena a vazão em L/s é o valor × 3,6 (na tela, os L/s do cenário ficam
# abaixo de 8 m³/h com ou sem conversão, então a ordem sozinha não mostra o erro)
ga = {g['id']: g for g in grids(page('CD-01'))}.get('g_agua') or {}
ls = [(r['v'].get('vazao'), r['v'].get('vazn')) for r in ga.get('rows', []) if str(r['v'].get('vazao', '')).endswith('L/s')]
chk('B1b vazão em L/s da grade publicada ordena pelo valor em m³/h (0,5 L/s → 1,8; 1,0 L/s → 3,6)', ls and all(abs(float(t.split()[0].replace(',', '.')) * 3.6 - float(k)) < 1e-6 for t, k in ls), ls)
r = [tenta(getattr(CF, '_doc_agua', AUS('_doc_agua')), x) for x in ('Outorga', 'Outorga estadual', 'Certidão de uso insignificante', '')]
chk('B2 documento do ponto de água: Outorga × Certidão (de uso insignificante); sem tipo fica vazio', r == ['Outorga', 'Outorga', 'Certidão', ''], r)
pr = tenta(getattr(CF, '_parc_rows', AUS('_parc_rows')), ['T1'], 'Santa Rita')
safras = [g['v']['safra'] for g in pr[0]] if isinstance(pr, tuple) else [pr]
chk('B3 parcelas do T1 (Santa Rita) só com safras da Santa Rita (sem a Safra Mamão da Lagoa Grande)', isinstance(pr, tuple) and safras and not any('Mamão' in x for x in safras), safras)
# B7 (revisão TABR, pré-existente): a lista (CD-01, "Parcelas na safra") e o detalhe do talhão (CD-01det) contam as mesmas parcelas em todo
# talhão; o PV01 da Lagoa Grande tinha 1 parcela na lista e nenhuma no detalhe (o local do cultivo é o nome do pivô, "Pivô 1")
import dados_lagoa_safra as DL
try:
    npc = CF._nparc(); div = []
    for t in CF._tal_rows():
        rr, _ = CF._parc_rows([t['id']], t['v']['faz']); k = sum(len(g['kids']) for g in rr if g['v']['sid'] in (CF.SAF_ATUAL['id'], DL.SAFRA['id']))
        if k != npc.get(t['id'], 0): div.append((t['id'], k, npc.get(t['id'], 0)))
    pv = CF._parc_rows(['PV01'], 'Lagoa Grande')[0]; pv01 = [(k['v']['parc'], k['v']['area']) for g in pv for k in g['kids']]
except Exception as e: div, pv01 = [repr(e)], []
chk('B7 parcelas da lista = parcelas do detalhe em todo talhão (PV01: Pivô 1 com 29,92 ha na Safra Mamão)', not div and pv01 == [('Pivô 1', 29.92)], (div[:4], pv01))

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
const P=(a,ref)=>irrPend(a,ref).map(x=>[x.t,x.c,x.dica]);
console.log(JSON.stringify({p:P([{t:'Impedida · bomba parada',c:'red'},{t:'Falta insumo · Ureia 45%',c:'red'},{t:'Conflito · parada da B3',c:'red',h:'14:00–15:00'},{t:'Janela a definir',c:'yellow'}]),
  f:irrPendFert({t:'Impedida · bomba parada',dono:'Manutenção'}).map(x=>x.t), n:irrPendFert(null),
  mut:P([{t:'Encerrada automaticamente',c:'gray',mut:true}]), ref:P([{t:'Divergência · −3,8 %',c:'yellow'}],'OS-0394')}));"""
up = node(jsp) or {}
# revisão TABR (09/10), A11: uma variável por chip (o tipo no chip, o detalhe na dica); A6: selo informativo de ordem encerrada (mut) não é
# pendência; A2: pendência de outra ordem diz qual é ("Divergência na OS-0394" ao lado da OS-0419)
chk('C7 Pendência: o tipo no chip e o detalhe na dica ("Falta insumo" + "Ureia 45%"; "Conflito" + "parada da B3 · 14:00–15:00"), sem repetir "Impedida"; sem bloqueio = lista vazia',
    up.get('p') == [['Bomba parada', 'red', ''], ['Falta insumo', 'red', 'Ureia 45%'], ['Conflito', 'red', 'parada da B3 · 14:00–15:00'], ['Janela a definir', 'yellow', '']] and up.get('f') == ['Bomba parada'] and up.get('n') == [], up)
chk('C8 (A6) selo informativo de ordem encerrada ("Encerrada automaticamente", mut) não entra na Pendência', up.get('mut') == [], up.get('mut'))
chk('C9 (A2) pendência de outra ordem diz qual é: "Divergência na OS-0394" (dica −3,8 %)', up.get('ref') == [['Divergência na OS-0394', 'yellow', '−3,8 %']], up.get('ref'))
# CD-04 (A3): não alocável diz o motivo (dica) e o próximo passo com verbo; M-i: a validade que vale é a mais próxima entre as exigidas
h4p = page('CD-04'); ia = h4p.find('const AL='); AL = json.JSONDecoder().raw_decode(h4p[ia + 9:])[0] if ia >= 0 else {}
js4 = "const HOJE='2026-09-23'; const AL=" + json.dumps(AL, ensure_ascii=False) + ";\n" + '\n'.join(func(h4p, f) for f in ('ml', 'br', 'ddiff', 'chipc', 'sitOk', 'sitX', 'habExig', 'alocavel', 'c4passo', 'c4sit', 'c4val')) + r"""
const S=(V)=>{ const x=c4sit(Object.assign({sit:'Ativa'},V)); return [x.t, x.p.map(p=>p.t).join(' | '), (x.p[0]||{}).dica||'']; };
console.log(JSON.stringify({ate:S({hab:'Operar trator',v31:'2027-08-31',ate:'2026-09-01'}),venc:S({hab:'Operar trator',v31:'2026-08-15'}),pend:S({hab:'Operar trator'}),
  adm:S({hab:'Conferir',adm:'2026-10-15'}),ok:S({hab:'Operar trator',v31:'2027-08-31'}),
  val:c4val(alocavel({hab:'Operar trator; Irrigar',v31:'2027-08-31',v10:'2026-12-10'}))}));"""
u4 = node(js4) or {}
chk('C10 (A3) CD-04 não alocável: o chip diz a consequência, a dica o motivo e o verbo o que resolver (contrato encerrado → Renovar contrato; NR-31 vencida → Renovar NR-31; pendente → Registrar NR-31; admissão futura → Aguardar admissão)',
    u4.get('ate') == ['Não alocável', 'Não alocável em O.S. | Renovar contrato ›', 'Contrato encerrado em 01/09/2026'] and u4.get('venc') == ['Não alocável', 'Não alocável em O.S. | Renovar NR-31 ›', 'NR-31 vencida em 15/08/2026']
    and u4.get('pend') == ['Não alocável', 'Não alocável em O.S. | Registrar NR-31 ›', 'NR-31 pendente'] and u4.get('adm', [''])[1] == 'Não alocável em O.S. | Aguardar admissão em 15/10/2026 ›' and u4.get('ok') == ['Alocável', 'Alocável', ''], u4)
chk('C11 (M-i) CD-04: com duas habilitações datadas, a validade que vale é a que vence primeiro (NR-10 10/12/2026, não NR-31 31/08/2027)', u4.get('val') == '2026-12-10', u4.get('val'))
# CD-03 (A10, A4): calibração a vencer diz isso no chip (a cor da data não é o único sinal); a capacidade só tem coluna com uma grandeza
h3 = page('CD-03'); ic = h3.find('const C3='); C3 = json.JSONDecoder().raw_decode(h3[ic + 9:])[0] if ic >= 0 else {}
js3 = "const HOJE='2026-09-23'; const C3=" + json.dumps(C3, ensure_ascii=False) + ";\n" + '\n'.join(func(h3, f) for f in ('br', 'ddiff', 'addd', 'chipc', 'sitOk', 'sitX', 'c3cond', 'c3calib', 'c3sit', 'capColDeps', 'c3capCol')) + r"""
const SP={id:'g_atv',cols:[{k:'nome'},{k:'est'},{k:'classe'},{k:'custo_h'},{k:'ncj'},{k:'calv'}]}; const GR=()=>SP; const ST={}; const g2st=()=>ST;
const K=(f)=>{ ST.f={classe:f}; c3capCol({}); const c=SP.cols.find(x=>x.k==='capn'); return c?[SP.cols.indexOf(c),c.l,c.un,c.t]:null; };
const sit=(V)=>{ const x=c3sit({id:'z',v:Object.assign({sit:'Ativo',exige:'Sim',interv:30},V)}); return [x.t,x.p.map(p=>p.t).join(' | '),!!x.res]; };
console.log(JSON.stringify({cap:{todas:K([]),irr:K(['Irrigação']),tr:K(['Trator']),mist:K(['Trator','Pulverizador']),kgh:K(['Tratamento de sementes','Beneficiamento']),col:K(['Colhedora'])},
  vence:sit({calib:'2026-09-01'}),emdia:sit({calib:'2026-09-20'}),vencida:sit({calib:'2026-08-01'})}));"""
u3 = node(js3) or {}; cp = u3.get('cap') or {}
chk('C12 (A10) CD-03: calibração que vence em 15 dias = chip "Calibração a vencer" com "Registrar calibração" (fora do "A resolver"); em dia = Apta; vencida = Calibração vencida',
    u3.get('vence') == ['Calibração a vencer', 'Calibração a vencer | Registrar calibração ›', False] and u3.get('emdia') == ['Apta', 'Apta', False] and (u3.get('vencida') or [''])[0] == 'Calibração vencida', u3)
chk('C13 (A4) CD-03: capacidade só com uma grandeza no filtro de Classe, com rótulo e unidade dela (Irrigação → Vazão m³/h; Trator → Potência cv; Trator + Pulverizador → sem coluna; sementes + beneficiamento → Capacidade kg/h)',
    cp.get('todas') is None and cp.get('irr') == [3, 'Vazão', 'm³/h', 'num'] and cp.get('tr') == [3, 'Potência', 'cv', 'num'] and cp.get('mist') is None
    and cp.get('kgh') == [3, 'Capacidade', 'kg/h', 'num'] and cp.get('col') is None, cp)
# C15–C18 (TABR-CTX-01, revisão do Codex TABR-REV-20261010-01, comentário 6092263670): a coluna de capacidade muda de grandeza com o filtro
# (Classe no CD-03, Tanque/Silo no CD-06); o filtro, a ordenação e o menu de filtro dela saem quando a grandeza+unidade muda ou a coluna sai,
# e ficam com a mesma grandeza (Tratamento de sementes ↔ Beneficiamento, kg/h). Busca, outros filtros, menu de outra coluna e o rascunho do
# cadastro ficam. Funções g2 originais da página; os chips seguem a fórmula de g2vals (rótulo da coluna, ou a chave quando ela não existe).
h6 = page('CD-06')
def cap6(html):
    """c6capCol da página; na base sem a função (8f19e0d), o mesmo trecho que estava dentro do PREVALS."""
    if 'function c6capCol(' in html: return func(html, 'c6capCol')
    i = html.find("const sl=GR('g_loc');"); j = html.find('v.c6l_ncol=sl.cols.length;', i)
    return 'function c6capCol(self){ const v={}; ' + html[i:j + 26] + ' return v.c6l_ncol; }' if i >= 0 and j > i else func(html, 'c6capCol')
G2F = ('g2num', 'g2fmtn', 'g2unf', 'g2fmt', 'g2st', 'g2set', 'g2text', 'g2mem', 'g2fkeys', 'g2key', 'g2match', 'g2sort', 'g2qtok', 'g2qhas', 'g2qrows')
jsx = ("const G2KEEP={}; const C3=" + json.dumps(C3, ensure_ascii=False) + ";\n" + '\n'.join(func(h3, f) for f in G2F + ('capColDeps', 'c3capCol')) + '\n' + cap6(h6) + r"""
const sp3={id:'g_atv',cols:[{k:'nome',l:'Máquina ou instalação'},{k:'est',l:'Situação'},{k:'classe',l:'Classe'},{k:'custo_h',l:'Custo R$/h',t:'num',a:'r',un:'R$/h'}],so:{}};
const sp6={id:'g_loc',cols:[{k:'nome',l:'Local'},{k:'faz',l:'Fazenda'},{k:'tipo',l:'Tipo'},{k:'itens',l:'Itens com este local padrão',t:'num',a:'r'}],qf:{k:'tipo',todas:'Todos'},so:{}};
const GR=(id)=>id==='g_loc'?sp6:sp3;
const R3=(nome,classe,n)=>({id:nome,v:{nome,classe,est:'Apta',capn:n},s:{nome,classe,est:'Apta',capn:g2fmtn(n)}});
const ROWS3=[R3('Trator T1','Trator',155),R3('Trator 04','Trator',78),R3('Bomba do Pivô 1','Irrigação',300),R3('Gotejo T7','Irrigação',45),R3('Máquina TSI','Tratamento de sementes',2400),R3('Packing linha 1','Beneficiamento',2400)];
const R6=(nome,tipo,n)=>({id:nome,v:{nome,faz:'Santa Rita',tipo,capn:n===null?'':n,itens:0},s:{nome,faz:'Santa Rita',tipo,capn:n===null?'':g2fmtn(n)}});
const ROWS6=[R6('Tanque Sede','Tanque',15000),R6('Silo 01','Silo',60000),R6('Galpão 1','Galpão',null)];
const MK=(g2)=>{ const self={state:{g2}}; self.setState=(p)=>{ Object.assign(self.state,p); }; return self; };
// um render: a coluna de capacidade (PREVALS) e o que a grade mostra (cabeçalho, chips de filtro, linhas visíveis) e guarda
function VER(self,sp,capCol,rows){ capCol(self); const st=g2st(self,sp.id); const cap=sp.cols.find(c=>c.k==='capn');
  const chips=Object.keys(st.f||{}).filter(k=>(st.f[k]||[]).length).map(k=>{ const c=sp.cols.find(x=>x.k===k)||{l:k}; return c.l+': '+st.f[k].join(', '); }).sort();
  return {col:cap?cap.l+' '+cap.un:null, chips, vis:g2sort(g2qrows(sp,st,rows).filter(r=>g2match(r,sp,st)),sp,st).map(r=>r.v.nome), f:Object.keys(st.f||{}).sort(),
    so:(st.so&&st.so.k)||null, fmc:st.fmc||null, fmd:st.fmd||null, fmq:st.fmq||'', q:st.q||'', fm:(st.fm&&st.fm.draft&&st.fm.draft.nome)||null}; }
const F=(self,gid,patch)=>g2set(self,gid,{f:Object.assign({},g2st(self,gid).f||{},patch)});
const tira=(self,gid,k)=>{ const f=Object.assign({},g2st(self,gid).f||{}); delete f[k]; g2set(self,gid,{f}); };   // o × do chip
const V3=(s)=>VER(s,sp3,c3capCol,ROWS3), V6=(s)=>VER(s,sp6,c6capCol,ROWS6), out={};
// C15: roteiro do Codex (Trator · Potência = 78 cv → limpar só Classe → Irrigação), com busca, outro filtro e rascunho do cadastro
{ const a=MK({g_atv:{f:{est:['Apta'],classe:['Trator']},q:'o',fm:{draft:{nome:'Rascunho sintético'},orig:{}}}}); V3(a);
  F(a,'g_atv',{capn:['78 cv']}); g2set(a,'g_atv',{so:{k:'capn',d:true}}); out.a1=V3(a); tira(a,'g_atv','classe'); out.a2=V3(a); F(a,'g_atv',{classe:['Irrigação']}); out.a3=V3(a); }
// C16: troca direta Trator → Irrigação com o menu de filtro da Potência aberto (rascunho marcado e pesquisa); o menu de outra coluna fica
{ const b=MK({g_atv:{f:{classe:['Trator']}}}); V3(b); F(b,'g_atv',{capn:['78 cv']}); g2set(b,'g_atv',{so:{k:'capn',d:false}}); V3(b);
  g2set(b,'g_atv',{fmc:'capn',fmd:['78 cv','155 cv'],fmq:'1',fpos:{x:0,xr:0,y:0}}); F(b,'g_atv',{classe:['Irrigação']}); out.b=V3(b);
  const b2=MK({g_atv:{f:{classe:['Trator'],capn:['78 cv']}}}); V3(b2); g2set(b2,'g_atv',{fmc:'est',fmd:['Apta'],fmq:'Ap'}); F(b2,'g_atv',{classe:['Irrigação']}); out.b2=V3(b2); }
// C17: mesma grandeza e unidade (Capacidade kg/h): Tratamento de sementes ↔ Beneficiamento mantém filtro, ordem e menu
{ const k=MK({g_atv:{f:{classe:['Tratamento de sementes']}}}); V3(k); F(k,'g_atv',{capn:['2.400 kg/h']}); g2set(k,'g_atv',{so:{k:'capn',d:true},fmc:'est',fmd:['Apta'],fmq:'Ap'});
  out.k0=V3(k); F(k,'g_atv',{classe:['Beneficiamento']}); out.k1=V3(k); F(k,'g_atv',{classe:['Tratamento de sementes','Beneficiamento']}); out.k2=V3(k); }
// C17b (TABR-CTX-02, lacuna S4 da reverificação): mesmo rótulo com unidade diferente (Armazenagem "Capacidade" em sc de 60 kg → Tratamento de
// sementes "Capacidade" em kg/h) tira o filtro, a ordem e o menu aberto; a comparação é rótulo + unidade, não só o rótulo
{ const V3s=(s)=>VER(s,sp3,c3capCol,ROWS3.concat([R3('Silo 01','Armazenagem',60000)]));
  const u=MK({g_atv:{f:{classe:['Armazenagem']},q:'i'}}); V3s(u); F(u,'g_atv',{capn:['60.000 sc de 60 kg']}); g2set(u,'g_atv',{so:{k:'capn',d:false}});
  out.u0=V3s(u); g2set(u,'g_atv',{fmc:'capn',fmd:['60.000 sc de 60 kg'],fmq:'60',fpos:{x:0,xr:0,y:0}}); F(u,'g_atv',{classe:['Tratamento de sementes']}); out.u1=V3s(u); }
// C18: CD-06 Tanque (L) ↔ Silo (sc de 60 kg) pelo filtro rápido de Tipo, e Todos (a coluna sai)
{ const e=MK({g_loc:{qv:'Tanque',f:{faz:['Santa Rita']},q:'Santa',fm:{draft:{nome:'Rascunho sintético'},orig:{}}}}); V6(e);
  F(e,'g_loc',{capn:['15.000 L']}); g2set(e,'g_loc',{so:{k:'capn',d:true}}); out.e0=V6(e); g2set(e,'g_loc',{qv:'Silo'}); out.e1=V6(e);
  F(e,'g_loc',{capn:['60.000 sc de 60 kg']}); g2set(e,'g_loc',{so:{k:'capn',d:false}}); out.e2=V6(e); g2set(e,'g_loc',{qv:''}); out.e3=V6(e); }
console.log(JSON.stringify(out));""")
ux = node(jsx) or {}
a1, a2, a3, b, b2 = (ux.get(k) or {} for k in ('a1', 'a2', 'a3', 'b', 'b2'))
chk('C15 (TABR-CTX-01) CD-03, roteiro do Codex: Trator · Potência = 78 cv → limpar só Classe tira a coluna, o filtro e a ordem da Potência (sem chip "capn: 78 cv"); '
    'Irrigação → Vazão sem filtro de outra grandeza e as 2 bombas/setores à vista; busca, filtro de Situação e rascunho do cadastro ficam',
    a1.get('vis') == ['Trator 04'] and 'Potência: 78 cv' in a1.get('chips', [])
    and a2.get('col') is None and a2.get('chips') == ['Situação: Apta'] and a2.get('f') == ['est'] and a2.get('so') is None and len(a2.get('vis', [])) == 6
    and a3.get('col') == 'Vazão m³/h' and a3.get('chips') == ['Classe: Irrigação', 'Situação: Apta'] and a3.get('vis') == ['Bomba do Pivô 1', 'Gotejo T7']
    and all(x.get('q') == 'o' and x.get('fm') == 'Rascunho sintético' for x in (a2, a3)), {k: ux.get(k) for k in ('a1', 'a2', 'a3')})
chk('C16 (TABR-CTX-01) CD-03, Trator → Irrigação direto: filtro, ordem e menu aberto da Potência (rascunho e pesquisa) saem; o menu de outra coluna (Situação) fica com o rascunho',
    b.get('col') == 'Vazão m³/h' and b.get('f') == ['classe'] and b.get('so') is None and b.get('fmc') is None and b.get('fmd') is None and b.get('fmq') == ''
    and b.get('vis') == ['Bomba do Pivô 1', 'Gotejo T7'] and b2.get('f') == ['classe'] and b2.get('fmc') == 'est' and b2.get('fmd') == ['Apta'] and b2.get('fmq') == 'Ap', {'b': b, 'b2': b2})
k0, k1, k2 = (ux.get(k) or {} for k in ('k0', 'k1', 'k2'))
chk('C17 (TABR-CTX-01) CD-03, mesma grandeza (Capacidade kg/h): Tratamento de sementes → Beneficiamento → os dois mantêm o filtro 2.400 kg/h, a ordem e o menu aberto',
    k0.get('vis') == ['Máquina TSI'] and k1.get('col') == 'Capacidade kg/h' and 'Capacidade: 2.400 kg/h' in k1.get('chips', []) and k1.get('so') == 'capn' and k1.get('vis') == ['Packing linha 1']
    and (k1.get('fmc'), k1.get('fmd'), k1.get('fmq')) == ('est', ['Apta'], 'Ap') and sorted(k2.get('vis', [])) == ['Máquina TSI', 'Packing linha 1'] and k2.get('so') == 'capn', {k: ux.get(k) for k in ('k0', 'k1', 'k2')})
u0, u1 = (ux.get(k) or {} for k in ('u0', 'u1'))
chk('C17b (TABR-CTX-02) CD-03, mesmo rótulo com unidade diferente: Armazenagem · Capacidade 60.000 sc de 60 kg (↑, menu aberto) → Tratamento de sementes '
    'tira o filtro, a ordem e o menu em sc (a Capacidade passa a kg/h e a Máquina TSI aparece); a busca fica',
    u0.get('col') == 'Capacidade sc de 60 kg' and u0.get('vis') == ['Silo 01'] and 'Capacidade: 60.000 sc de 60 kg' in u0.get('chips', [])
    and u1.get('col') == 'Capacidade kg/h' and u1.get('chips') == ['Classe: Tratamento de sementes'] and u1.get('f') == ['classe'] and u1.get('so') is None
    and (u1.get('fmc'), u1.get('fmd'), u1.get('fmq')) == (None, None, '') and u1.get('vis') == ['Máquina TSI'] and u1.get('q') == 'i', {'u0': u0, 'u1': u1})
e0, e1, e2, e3 = (ux.get(k) or {} for k in ('e0', 'e1', 'e2', 'e3'))
chk('C18 (TABR-CTX-01) CD-06 Locais: Tanque · 15.000 L → Silo tira filtro e ordem em L (o Silo 01 aparece em sc de 60 kg); Silo · 60.000 sc → Todos tira a coluna sem chip órfão; '
    'busca, filtro de Fazenda e rascunho ficam',
    e0.get('vis') == ['Tanque Sede'] and e1.get('col') == 'Capacidade sc de 60 kg' and e1.get('f') == ['faz'] and e1.get('so') is None and e1.get('chips') == ['Fazenda: Santa Rita'] and e1.get('vis') == ['Silo 01']
    and e2.get('vis') == ['Silo 01'] and e3.get('col') is None and e3.get('chips') == ['Fazenda: Santa Rita'] and e3.get('f') == ['faz'] and e3.get('so') is None and len(e3.get('vis', [])) == 3
    and all(x.get('q') == 'Santa' and x.get('fm') == 'Rascunho sintético' for x in (e1, e3)), {k: ux.get(k) for k in ('e0', 'e1', 'e2', 'e3')})
# C19 (TABR-CTX-02, revisão do TABR-CTX-01, 10/10/2026): no IR-01 a coluna Fazenda só existe com "Todas" no topo; com uma fazenda ela sai e leva
# o filtro, a ordem e o menu de filtro dela (antes ficava o chip "faz: Santa Rita", o filtro era ignorado e voltava com "Todas"). Busca e outros
# filtros ficam; a vista restaurada da sessão com filtro de Fazenda e uma fazenda no topo também sai limpa. Funções g2 da página IR-01.
hi = page('IR-01')
cdi = func(hi, 'capColDeps') if 'function capColDeps(' in hi else 'function capColDeps(){}'   # base 36ad018: o IR não tinha a reconciliação
jsf = ("const G2KEEP={};\n" + '\n'.join(func(hi, f) for f in G2F) + '\n' + cdi + '\n' + func(hi, 'irrColsFaz') + r"""
const spi={id:'g_set',cols:[{k:'setor',l:'Setor'},{k:'faz',l:'Fazenda'},{k:'sit',l:'Situação'}],so:{}}; const IRG=()=>spi;
const RI=(setor,faz,sit)=>({id:setor+' '+faz,v:{setor,faz,sit},s:{setor,faz,sit}});
const ROWSI=[RI('Pivô 1','Santa Rita','Impedida'),RI('Pivô 2','Santa Rita','A conferir'),RI('Gotejo T7','Santa Rita','Programada'),RI('Pivô 2','Lagoa Grande','Programada'),RI('Pivô 5','Lagoa Grande','Impedida')];
const MK=(g2)=>{ const self={state:{g2}}; self.setState=(p)=>{ Object.assign(self.state,p); }; return self; };
// um desenho do IR-01 com a fazenda do topo (fz: null = Todas, 'LG'): colunas (PREVALS) e o que a grade mostra
function VI(self,fz){ const v={}; if(irrColsFaz.length===5) irrColsFaz(self,'g_set',fz,v,'set_ncol'); else irrColsFaz('g_set',fz,v,'set_ncol');
  const st=g2st(self,'g_set'), rows=ROWSI.filter(r=>!fz||r.v.faz===(fz==='LG'?'Lagoa Grande':'Santa Rita'));
  const chips=Object.keys(st.f||{}).filter(k=>(st.f[k]||[]).length).map(k=>{ const c=spi.cols.find(x=>x.k===k)||{l:k}; return c.l+': '+st.f[k].join(', '); }).sort();
  return {cols:spi.cols.map(c=>c.k), ncol:v.set_ncol, chips, vis:g2sort(g2qrows(spi,st,rows).filter(r=>g2match(r,spi,st)),spi,st).map(r=>r.id), f:Object.keys(st.f||{}).sort(),
    so:(st.so&&st.so.k)||null, fmc:st.fmc||null, q:st.q||''}; }
const FI=(self,patch)=>g2set(self,'g_set',{f:Object.assign({},g2st(self,'g_set').f||{},patch)}); const out={};
{ const a=MK({g_set:{q:'Pivô'}}); VI(a,null); FI(a,{sit:['Impedida','Programada'],faz:['Santa Rita']}); g2set(a,'g_set',{so:{k:'faz',d:true}}); out.t0=VI(a,null);
  g2set(a,'g_set',{fmc:'faz',fmd:['Santa Rita'],fmq:'S',fpos:{x:0,xr:0,y:0}}); out.lg=VI(a,'LG'); out.todas=VI(a,null); }
{ const b=MK({g_set:{f:{faz:['Santa Rita'],sit:['Impedida']}}}); out.rest=VI(b,'LG'); }
{ const k=MK({g_set:{}}); VI(k,null); FI(k,{faz:['Lagoa Grande']}); out.k=VI(k,null); }
console.log(JSON.stringify(out));""")
uf = node(jsf) or {}
t0, lg, td, rs, kk = (uf.get(k) or {} for k in ('t0', 'lg', 'todas', 'rest', 'k'))
chk('C19 (TABR-CTX-02) IR-01: Todas + Fazenda = Santa Rita (↓) → Lagoa Grande no topo tira a coluna com o filtro, a ordem e o menu dela (sem chip "faz: Santa Rita"); '
    'volta a Todas sem o filtro antigo; Situação e busca ficam; vista restaurada com filtro de Fazenda numa fazenda só sai limpa; com Todas, o filtro fica',
    t0.get('vis') == ['Pivô 1 Santa Rita'] and t0.get('so') == 'faz' and 'Fazenda: Santa Rita' in t0.get('chips', [])
    and lg.get('cols') == ['setor', 'sit'] and lg.get('ncol') == 2 and lg.get('chips') == ['Situação: Impedida, Programada'] and lg.get('f') == ['sit'] and lg.get('so') is None
    and lg.get('fmc') is None and lg.get('q') == 'Pivô' and lg.get('vis') == ['Pivô 2 Lagoa Grande', 'Pivô 5 Lagoa Grande']
    and td.get('ncol') == 3 and td.get('chips') == ['Situação: Impedida, Programada'] and sorted(td.get('vis', [])) == ['Pivô 1 Santa Rita', 'Pivô 2 Lagoa Grande', 'Pivô 5 Lagoa Grande']
    and rs.get('f') == ['sit'] and rs.get('vis') == ['Pivô 5 Lagoa Grande'] and kk.get('chips') == ['Fazenda: Lagoa Grande'], uf)
# C20 (revisão do TABR-CTX-01, 10/10/2026): a 390 px a 1ª coluna presa do g2lib (data-c0, --g2cols) guardava o nº de colunas da abertura e só era
# refeita quando a largura mudava: com a capacidade (ou a Fazenda) entrando, a última coluna caía para a linha de baixo. capColDeps desfaz a coluna
# presa quando a coluna entra ou sai, antes do novo desenho, e o motor a refaz com o nº novo. Só nesses passos: não a cada desenho nem quando só a
# grandeza muda (mesmo nº de colunas), para não refazer sem necessidade (sem vaivém).
jsc = "const G2KEEP={};\n" + '\n'.join(func(h3, f) for f in G2F + ('capColDeps',)) + r"""
let RES=0; const R={removeAttribute:(a)=>{ if(a==='data-c0') RES++; }, style:{removeProperty:()=>{}}};
global.document={querySelectorAll:(q)=>q==='.g2rola[data-c0]'?[R]:[], activeElement:null};
const self={state:{g2:{}}}; self.setState=(p)=>Object.assign(self.state,p);
const passo=(t)=>{ const a=RES; capColDeps(self,'g_atv','capn',t); return RES-a; };
console.log(JSON.stringify(['','','Potência|cv','Potência|cv','Vazão|m³/h','','','Capacidade|kg/h'].map(passo).concat([(()=>{ const s2={state:{g2:{}}}; const a=RES; capColDeps(s2,'g_atv','capn','Potência|cv'); return RES-a; })()])));"""
uc = node(jsc)
chk('C20 (revisão do TABR-CTX-01) a coluna presa é refeita só quando a coluna de capacidade entra ou sai: abertura sem coluna 0, sem coluna 0, entra (Potência) 1, mesmo desenho 0, '
    'Potência → Vazão (mesmo nº de colunas) 0, sai 1, fora 0, entra (kg/h) 1; abertura já com a coluna 0',
    uc == [0, 0, 1, 0, 0, 1, 0, 1, 0], uc)
# C14 (revisão TABR, pré-existente): no IR-03det a Duração é a da janela mostrada na linha (Início e Fim reais → real; previstos → prevista)
hd = page('IR-03det')
jsd = '\n'.join(func(hd, f) for f in ('irrPausaMin', 'irrFimP', 'irrDurP')) + r"""
const o={exec:{pausas:[{n:2,ini:1000,fim:1030}]}};
console.log(JSON.stringify([irrDurP(o,{n:1,ini:1200,dur:870,iniReal:1200,fimReal:1326}), irrDurP(o,{n:1,ini:1200,dur:870}), irrDurP(o,{n:1,ini:null,dur:870}),
  irrDurP(o,{n:2,ini:900,dur:600,iniReal:905})]));"""
ud = node(jsd)
chk('C14 IR-03det: Duração = Fim − Início da mesma linha (feita 20:00–22:06 → 126 min, não os 870 previstos; programada → 870; sem início → 870; em execução com pausa de 30 min → 630)',
    ud == [126, 870, 870, 630], ud)
import dados_irrigacao as DI
# A9: a semente da irrigação mudou (grandezas e unidades por item, a881cbe/ecc8fce): versão nova descarta o estado salvo com a semente antiga
ie = open(os.path.join(HERE, 'irrigacao_estado.js'), encoding='utf-8').read()
chk('B6 (A9) estado salvo da irrigação com outra versão é descartado: semente v=3 e a leitura só aceita a mesma versão', DI.seed()['v'] == 3 and 'p.v === IRR0.v' in ie, DI.seed()['v'])
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
