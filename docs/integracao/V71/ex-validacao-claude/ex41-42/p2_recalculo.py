# -*- coding: utf-8 -*-
"""EX-42 · recálculo independente (Python, Decimal) da matemática do protótipo pragas-no-tempo.html, a partir dos dados internos
que o próprio JS gerou (out/proto_dados.json, do p1_proto.py) e comparação com o texto lido na tela (out/p1_proto.json).
Não chama nenhuma função do protótipo: as regras são as do texto do EX-42, escritas aqui de novo.
Uso: python3 -I p2_recalculo.py  → out/p2_recalculo.txt e out/p2_recalculo.json"""
import json, os, datetime as dt
from decimal import Decimal as D, ROUND_HALF_UP, getcontext
getcontext().prec = 28
B = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(B, 'out')
P = json.load(open(os.path.join(OUT, 'proto_dados.json'), encoding='utf-8'))
TELA = json.load(open(os.path.join(OUT, 'p1_proto.json'), encoding='utf-8'))
T = open(os.path.join(OUT, 'p2_recalculo.txt'), 'w', encoding='utf-8'); RES = {}; CHK = []
def out(*a):
    s = ' '.join(str(x) for x in a); print(s); T.write(s + '\n')
def chk(nome, ok, info=''):
    CHK.append((nome, bool(ok))); out(('OK    ' if ok else 'DIFERE ') + nome + (' · ' + str(info) if info else ''))
Dd = lambda x: D(repr(x)) if x is not None else None
START = dt.date(2026, 7, 1); fd = lambda d: (START + dt.timedelta(days=d)).strftime('%d/%m')
def mediana(v):
    s = sorted(v); n = len(s)
    if not n: return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
r0 = lambda x: int((x).quantize(D('1'), ROUND_HALF_UP))
pct_txt = lambda r: (f'{r0(r * 100)} %' if r >= 0 else f'subiu {r0(-r * 100)} %')
PIV = {p['id']: p for p in P['pivos']}
CL = P['clima']

# ---------------- A. Pragas: janela antes → depois (texto do EX-42: vistoria até 10 dias antes → 5 a 14 dias depois) ----------------
out('== A. Janela de efeito em pragas (todas as aplicações dos 4 alvos)')
tot = mesmo_dia = dif_js = interf = 0; casos_mesmo_dia = []; red_estrita_vs = []
for aid, a in P['alvos'].items():
    for pid, s in a['piv'].items():
        obs = [(o[0], Dd(o[1])) for o in s['obs']]
        for k, ap in enumerate(s['apps']):
            tot += 1; d0 = ap['day']
            antes = [o for o in obs if o[0] <= d0 and d0 - o[0] <= 10]
            b = antes[-1] if antes else None
            aft = next((o for o in obs if d0 + 5 <= o[0] <= d0 + 14), None)
            red = (b[1] - aft[1]) / b[1] if b and aft and b[1] > 0 else None
            js = Dd(ap['red'])
            if (red is None) != (js is None) or (red is not None and abs(red - js) > D('1e-12')): dif_js += 1
            # leitura do próprio dia da aplicação usada como "antes" (a ordem no dia é desconhecida)
            if b and b[0] == d0:
                mesmo_dia += 1
                antes_e = [o for o in obs if o[0] < d0 and d0 - o[0] <= 10]; be = antes_e[-1] if antes_e else None
                re = (be[1] - aft[1]) / be[1] if be and aft and be[1] > 0 else None
                casos_mesmo_dia.append(dict(alvo=aid, pivo=pid, dia=fd(d0), antes_mesmo_dia=str(b[1].quantize(D('0.01'))), depois=str(aft[1].quantize(D('0.01'))) if aft else None,
                                            red_prototipo=(pct_txt(red) if red is not None else None), antes_estrito=(fd(be[0]) + ' ' + str(be[1].quantize(D('0.01')))) if be else 'nenhuma',
                                            red_estrita=(pct_txt(re) if re is not None else 'sem par')))
            # outra aplicação (qualquer alvo) no mesmo pivô entre a aplicação e a leitura depois
            if aft:
                outras = [(a2, x['day']) for a2, al2 in P['alvos'].items() for x in al2['piv'].get(pid, {'apps': []})['apps'] if d0 < x['day'] <= aft[0] and not (a2 == aid and x['day'] == d0)]
                if outras: interf += 1
chk('A1 redução do JS = recálculo pela regra escrita (antes ≤ dia da aplicação)', dif_js == 0, f'{tot} aplicações, {dif_js} diferenças')
out(f'A2 "antes" lido no próprio dia da aplicação: {mesmo_dia} de {tot} aplicações ({(D(mesmo_dia) / D(tot) * 100).quantize(D("0.1"))} %)')
for x in casos_mesmo_dia[:6]: out('   ', x)
out(f'A3 pares com outra aplicação no mesmo pivô entre a aplicação e a leitura depois (sem marca de interferência na tela): {interf}')
RES['A'] = dict(total=tot, mesmo_dia=mesmo_dia, interferencia=interf, exemplos_mesmo_dia=casos_mesmo_dia[:10])

# ---------------- B. "O que reduziu" · Ácaro-rajado até 25/09 (dia 86), agrupado por produto ----------------
out('\n== B. O que reduziu ácaro-rajado até 25/09 · por produto (mediana, n, volta ao NC)')
a = P['alvos']['acaro']; NC = D(a['nc']); DIA = 86
g = {}
for pid, s in a['piv'].items():
    obs = [(o[0], Dd(o[1])) for o in s['obs']]
    for ap in s['apps']:
        d0 = ap['day']; antes = [o for o in obs if o[0] <= d0 and d0 - o[0] <= 10]; b = antes[-1] if antes else None
        aft = next((o for o in obs if d0 + 5 <= o[0] <= d0 + 14), None)
        if not (b and aft and b[1] > 0 and aft[0] <= DIA): continue
        red = (b[1] - aft[1]) / b[1]
        back = next((o for o in obs if o[0] > d0 and o[1] >= NC), None)
        nunca_abaixo = aft[1] >= NC          # a leitura depois já estava ≥ NC: não houve "volta"
        G = g.setdefault(ap['prod'], dict(red=[], ctl=[], aberto=0, nunca_abaixo=0, ctl_corrigido=[]))
        G['red'].append(red)
        if back and back[0] <= DIA: G['ctl'].append(D(back[0] - d0))
        else: G['aberto'] += 1
        if nunca_abaixo: G['nunca_abaixo'] += 1
        else:
            # volta ao NC corrigida: primeira leitura ≥ NC depois de uma leitura < NC posterior à aplicação
            abaixo = next(o for o in obs if o[0] >= aft[0] and o[1] < NC)
            bk = next((o for o in obs if o[0] > abaixo[0] and o[1] >= NC and o[0] <= DIA), None)
            if bk: G['ctl_corrigido'].append(D(bk[0] - d0))
tela = {l[0].split(' IRAC')[0].split(' ação')[0]: l for l in TELA['oque']['86|Produto']['linhas']}
for prod, G in sorted(g.items(), key=lambda kv: -mediana(kv[1]['red'])):
    m = mediana(G['red']); mc = mediana(G['ctl']) if G['ctl'] else None
    calc = [str(len(G['red'])), pct_txt(m), (f'em {r0(mc)} d' if mc is not None else '—') + (f" {G['aberto']} segue{'m' if G['aberto'] > 1 else ''} abaixo" if G['aberto'] else '')]
    t = tela.get(prod)
    chk(f'B {prod}: n · mediana · volta ao NC', t and [t[1], t[2], t[3]] == calc, f'recalculado {calc} · tela {t[1:] if t else None}')
    out(f'   {prod}: "voltou ao NC" sem nunca ter ficado abaixo do NC: {G["nunca_abaixo"]} de {len(G["red"])}; mediana corrigida da volta: '
        f'{(str(r0(mediana(G["ctl_corrigido"]))) + " d (n=" + str(len(G["ctl_corrigido"])) + ")") if G["ctl_corrigido"] else "sem casos"}; média em vez de mediana: {pct_txt(sum(G["red"]) / len(G["red"]))}')
RES['B'] = {k: dict(n=len(v['red']), mediana=str(mediana(v['red'])), nunca_abaixo=v['nunca_abaixo'], aberto=v['aberto']) for k, v in g.items()}

# ---------------- C. Textos do painel com n < 3 sem aviso ----------------
out('\n== C. Frases do painel com menos de 3 casos e sem "pouca evidência"')
fen_barra = []; fen_atom = []
for pid, s in a['piv'].items():
    obs = [(o[0], Dd(o[1])) for o in s['obs']]
    for ap in s['apps']:
        if ap['prod'] != 'Fenpiroximato': continue
        d0 = ap['day']; antes = [o for o in obs if o[0] <= d0 and d0 - o[0] <= 10]; b = antes[-1] if antes else None
        aft = next((o for o in obs if d0 + 5 <= o[0] <= d0 + 14), None)
        if b and aft and b[1] > 0 and aft[0] <= DIA: (fen_barra if ap['eq'] == 'b100' else fen_atom).append((b[1] - aft[1]) / b[1])
frase = [x for x in TELA['oque']['86|Produto']['insights'] if 'barra a 100' in x]
chk('C1 frase "barra × atomizador" do Fenpiroximato tem n ≥ 3 nos dois lados', len(fen_barra) >= 3 and len(fen_atom) >= 3,
    f'barra n={len(fen_barra)} ({pct_txt(mediana(fen_barra))}), atomizador n={len(fen_atom)} ({pct_txt(mediana(fen_atom))}); tela: {frase}')
RES['C'] = dict(fen_barra=len(fen_barra), fen_atom=len(fen_atom), frase=frase)

# ---------------- D. Validade da vistoria no mapa: protótipo 14 dias × PEND-13 7 dias ----------------
out('\n== D. Validade da vistoria no mapa (ácaro, todos os dias e pivôs)')
cont = {'atual_ate7': 0, 'vencida_8a14': 0, 'sem': 0}
for pid, s in a['piv'].items():
    obs = s['obs']
    for d in range(P['DAYS'] + 1):
        ult = [o for o in obs if o[0] <= d]
        if not ult: cont['sem'] += 1; continue
        age = d - ult[-1][0]
        if age <= 7: cont['atual_ate7'] += 1
        elif age <= 14: cont['vencida_8a14'] += 1
        else: cont['sem'] += 1
mostradas = cont['atual_ate7'] + cont['vencida_8a14']
chk('D1 rótulos com leitura no mapa (tela, 87 dias) = recálculo com validade de 14 dias', TELA['leituras_no_mapa'] == mostradas, f"tela {TELA['leituras_no_mapa']} · recálculo {mostradas}")
out(f"D2 dessas, com idade de 8 a 14 dias (vencidas pela PEND-13, 7 dias, e coloridas como atuais no protótipo): {cont['vencida_8a14']} ({(D(cont['vencida_8a14']) / D(mostradas) * 100).quantize(D('0.1'))} %)")
# média da fazenda em 25/09: protótipo (14 dias) × PEND-13 (7 dias)
def media(d, val):
    sw = sv = D(0); acima = n = 0
    for pid, s in a['piv'].items():
        n += 1; ult = [o for o in s['obs'] if o[0] <= d]
        if not ult or d - ult[-1][0] > val: continue
        ha = Dd(PIV[pid]['ha']); v = Dd(ult[-1][1]); sw += ha; sv += ha * v; acima += v >= NC
    return (sv / sw if sw else None), acima, n, sw
m14, ac14, n14, sw14 = media(86, 14); m7, ac7, n7, sw7 = media(86, 7)
chk('D3 média da fazenda 25/09 (tela "15 % · 6 de 20") = recálculo com 14 dias', TELA['inicio']['now'].find(f'{r0(m14)} %') > 0 and f'{ac14} de {n14}' in TELA['inicio']['now'],
    f'14 dias: {m14.quantize(D("0.0001"))} %, {ac14} de {n14}, área {sw14} ha · PEND-13 7 dias: {m7.quantize(D("0.0001"))} %, {ac7} de {n7}, área {sw7} ha')
RES['D'] = dict(cont=cont, media14=str(m14), media7=str(m7), acima14=ac14, acima7=ac7)

# ---------------- E. Vigor: cena até 10 dias antes → 10 a 25 dias depois, menos a variação mediana dos pivôs do mesmo estádio ----------------
out('\n== E. Resposta do vigor (NDVI) por adubação')
SAT = P['sat']
def cena(pid, d): return next((s for s in SAT[pid] if s['day'] == d), None)
dif = 0; contam = []; casos = []
for e in P['adub']:
    sc = SAT[e['pid']]; d0 = e['day']
    bef = [s for s in sc if s['ok'] and s['day'] <= d0 and d0 - s['day'] <= 10]; bef = bef[-1] if bef else None
    aft = next((s for s in sc if s['ok'] and d0 + 10 <= s['day'] <= d0 + 25), None)
    js = e['js']['NDVI']
    if not bef or not aft:
        if js: dif += 1
        continue
    dlt = Dd(aft['NDVI']) - Dd(bef['NDVI']); st = PIV[e['pid']]['stage']
    peers = []; peers_adub = 0
    for q in P['pivos']:
        if q['stage'] != st or q['id'] == e['pid']: continue
        cb, ca = cena(q['id'], bef['day']), cena(q['id'], aft['day'])
        if cb and ca and cb['ok'] and ca['ok']:
            peers.append(Dd(ca['NDVI']) - Dd(cb['NDVI']))
            peers_adub += any(x['pid'] == q['id'] and bef['day'] < x['day'] <= aft['day'] for x in P['adub'])
    dc = mediana(peers); rel = dlt - dc if dc is not None else None
    if rel is None: ruim = js is not None and js.get('rel') is not None
    else: ruim = js is None or js.get('rel') is None or abs(Dd(js['rel']) - rel) > D('1e-9')
    dif += ruim
    if peers: contam.append(D(peers_adub) / D(len(peers)))
    if e['pid'] == 'P9': casos.append((fd(d0), fd(bef['day']), fd(aft['day']), str(Dd(bef['NDVI']).quantize(D('0.01'))), str(Dd(aft['NDVI']).quantize(D('0.01'))), str(rel.quantize(D('0.0001'))), len(peers)))
chk('E1 resposta do JS = recálculo (117 adubações)', dif == 0, f'{dif} diferenças')
out('E2 P9 (dia · cena antes · cena depois · NDVI antes → depois · resposta · nº de pivôs de comparação):')
for x in casos: out('   ', x)
tela_p9 = TELA['sat_P9']
for x in casos:
    rr = D(x[5]); s = ('' if abs(rr) < D('0.005') else ('+' if rr > 0 else '−')) + str(abs(rr).quantize(D('0.01'), ROUND_HALF_UP)).replace('.', ',')
    chk(f'E3 P9 {x[0]}: "{s} em relação aos pivôs" na tela', f'{s} em relação aos pivôs' in tela_p9)
pc = mediana(contam)
out(f'E4 fração mediana dos pivôs de comparação que também foram adubados na mesma janela: {(pc * 100).quantize(D("0.1"))} % (n={len(contam)} adubações)')
RES['E'] = dict(p9=casos, contaminacao_mediana=str(pc))

# ---------------- F. Satélite: validade 15 dias (protótipo) × 10 dias (PEND-13) e nuvem ----------------
out('\n== F. Satélite: cena mostrada no mapa')
cont = {'ok_ate10': 0, 'ok_11a15': 0, 'nuvem': 0, 'sem': 0, 'cenas_com_nuvem': 0}
for pid, sc in SAT.items():
    st = PIV[pid]['stage']
    cont['cenas_com_nuvem'] += sum(1 for s in sc if not s['ok'])
    for d in range(P['DAYS'] + 1):
        if st == 'solo' or (st == 'velha' and d > 75): continue
        ss = [s for s in sc if s['day'] <= d]
        if not ss: cont['sem'] += 1; continue
        val = [s for s in ss if s['ok']]; v = val[-1] if val else None; last = ss[-1]
        if not last['ok'] and (not v or d - v['day'] > 15): cont['nuvem'] += 1
        elif not v or d - v['day'] > 15: cont['sem'] += 1
        elif d - v['day'] <= 10: cont['ok_ate10'] += 1
        else: cont['ok_11a15'] += 1
out(f"F1 pivô-dias: {cont}")
chk('F2 tela: nenhum pivô hachurado por nuvem em 87 dias (varredura) = recálculo', TELA['sat_varredura']['contagem']['cloud'] == cont['nuvem'], f"tela {TELA['sat_varredura']['contagem']} · recálculo nuvem {cont['nuvem']}")
out(f"F3 pivô-dias com cena de 11 a 15 dias mostrada em cor de índice (seria 'sem leitura atual' pela PEND-13, 10 dias): {cont['ok_11a15']}")
RES['F'] = cont

# ---------------- G. Alerta de clima no dia da aplicação: regra do texto × código ----------------
out('\n== G. "Dia quente e seco" no dia da aplicação (texto: ≥ 32 °C e UR < 50 %)')
n = alerta = regra = so_alerta = 0; ex = []
for aid, al in P['alvos'].items():
    for pid, s in al['piv'].items():
        for ap in s['apps']:
            c = CL[ap['day']]; n += 1
            al_cod = c['ur'] < 50 or c['tmax'] > 32; al_reg = c['tmax'] >= 32 and c['ur'] < 50
            alerta += al_cod; regra += al_reg
            if al_cod and not al_reg:
                so_alerta += 1
                if len(ex) < 4: ex.append((aid, pid, fd(ap['day']), round(c['tmax'], 1), round(c['ur'], 1)))
chk('G1 aplicações com o alerta = aplicações que cumprem a regra escrita', alerta == regra, f'{n} aplicações: alerta {alerta}, regra {regra}, alerta sem cumprir a regra {so_alerta}; ex. {ex}')
fav = sum(1 for c in CL if c['quenteSeco']); fav_ok = sum(1 for c in CL if (c['tmax'] >= 32 and c['ur'] < 50) == c['quenteSeco'])
chk('G2 faixa "favorável a ácaro" (quenteSeco) = ≥ 32 °C e UR < 50 %', fav_ok == len(CL), f'{fav} dias favoráveis')
mol_ur = sum(1 for c in CL if c['molhado'] and c['ur'] < 90)
out(f'G3 dias "molhamento ≥ 8 h" com UR < 90 % (o texto diz "UR ≥ 90 %", o código não usa UR): {mol_ur} de {sum(1 for c in CL if c["molhado"])}')
RES['G'] = dict(n=n, alerta=alerta, regra=regra, so_alerta=so_alerta, mol_ur_menor90=mol_ur)

# ---------------- H. Crescimento semanal sem controle: semanas favoráveis × demais (ácaro, até 25/09) ----------------
out('\n== H. Crescimento semanal sem controle (ácaro)')
fav, nfav = [], []
for pid, s in a['piv'].items():
    obs = s['obs']
    for i in range(1, len(obs)):
        (d1, v1), (d2, v2) = obs[i - 1], obs[i]
        if d2 > DIA or v1 < 0.8: continue
        if any(d1 - 10 < ap['day'] <= d2 for ap in s['apps']): continue
        gr = (Dd(v2) / Dd(v1)) ** (D(7) / D(d2 - d1)) - 1
        qs = sum(1 for d in range(d1 + 1, d2 + 1) if CL[d]['quenteSeco'])
        (fav if qs >= 3 else nfav).append(gr)
gf, gn = mediana(fav), mediana(nfav)
txt = next((x for x in TELA['oque']['86|Produto']['insights'] if x.startswith('Clima')), '')
chk('H1 "+91 % … +52 % (33 e 117 intervalos)"', f'+{r0(gf * 100)} %' in txt and f'+{r0(gn * 100)} %' in txt and f'({len(fav)} e {len(nfav)} intervalos' in txt, f'recalculado +{r0(gf*100)} % (n={len(fav)}) e +{r0(gn*100)} % (n={len(nfav)}); tela: {txt}')
RES['H'] = dict(fav=len(fav), nfav=len(nfav), gf=str(gf), gn=str(gn))

out(f'\nRESULTADO: {sum(1 for _, o in CHK if o)} de {len(CHK)} conferências iguais; diferenças: {[n for n, o in CHK if not o]}')
json.dump(RES, open(os.path.join(OUT, 'p2_recalculo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
