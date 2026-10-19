# -*- coding: utf-8 -*-
"""Conferência em Decimal dos oráculos da MAPA-MIP-PROD (partes 1 e 2). Dados sintéticos de demonstração.
Uso: python3 -I mapa_mip_prod_chk.py  (não lê o repositório: as entradas estão escritas aqui, com a fonte citada no comentário)."""
from decimal import Decimal as D, getcontext
import datetime as dt, hashlib
getcontext().prec = 40
OK = []
def chk(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHA ') + nome + (' · ' + str(info) if info else ''))
def q(x, n=6): return x.quantize(D(1).scaleb(-n))
def d(s): return dt.date.fromisoformat(s)

print('== PARTE 1 · linha do tempo do MIP (Lagoa Grande, Ácaro-rajado, protocolo mamao-acaro, NC 15 % folhas com ácaro, 20 pontos)')
NC = D(15); VALIDADE = 7   # PROJ-13/PEND-13: vistoria MIP/MID 7 dias (valor aceito pela DEC-1610-04); idade = validade ainda é atual
AREA = {'PV02': D('37.75'), 'PV04': D('73.18'), 'PV06': D('62.79'), 'PV09': D('74.98'), 'PV17': D('33.36')}   # dados_lagoa_safra.PIVOS
# leituras: (id, pivô, data, soma dos 20 pontos) · existentes: VIS-051, VIS-057, VIS-060 (dados_mip.py) · novas: VIS-061..072 (semente proposta)
PTS = {  # composição dos 20 pontos de cada leitura nova (valores em % de folhas com ácaro)
 'VIS-061': [20]*16+[30]*4, 'VIS-062': [10]*18+[0]*2, 'VIS-063': [20]*20, 'VIS-064': [10]*12+[0]*8, 'VIS-065': [20]*16+[0]*4,
 'VIS-066': [10]*16+[0]*4, 'VIS-067': [20]*18+[0]*2, 'VIS-068': [10]*15+[0]*5, 'VIS-069': [20]*12+[0]*8, 'VIS-070': [10]*20,
 'VIS-071': [10]*10+[0]*10, 'VIS-072': [10]*12+[0]*8,
 'VIS-051': [20, 10, 30, 20, 10, 20, 30, 10, 20, 20, 10, 20, 10, 30, 20, 10, 20, 20, 10, 20],
 'VIS-057': [0, 10, 0, 10, 0, 0, 10, 0, 10, 0, 0, 10, 0, 10, 0, 0, 10, 0, 10, 0],
 'VIS-060': [0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 0, 0, 0]}
LEIT = [('VIS-061','PV06','2026-08-25'),('VIS-062','PV06','2026-09-04'),('VIS-051','PV06','2026-09-19'),
        ('VIS-063','PV04','2026-08-27'),('VIS-064','PV04','2026-09-10'),('VIS-057','PV04','2026-09-22'),
        ('VIS-065','PV17','2026-08-26'),('VIS-066','PV17','2026-09-03'),('VIS-060','PV17','2026-09-10'),
        ('VIS-067','PV09','2026-08-28'),('VIS-068','PV09','2026-09-08'),('VIS-071','PV09','2026-09-20'),
        ('VIS-069','PV02','2026-09-01'),('VIS-070','PV02','2026-09-09'),('VIS-072','PV02','2026-09-18')]
for k, v in PTS.items(): assert len(v) == 20, k
MED = {i: D(sum(PTS[i])) / D(20) for i, _, _ in LEIT}   # CAL-12: soma das observações válidas ÷ amostras válidas
def classe(m):   # mipRes: ≥ NC acima; ≥ 0,8 NC perto; foco só com ≥ 2 pontos ≥ 2 × NC e média < NC
    return 'acima' if m >= NC else ('perto' if m >= D('0.8') * NC else 'abaixo')
def reb(i): return sum(1 for x in PTS[i] if D(x) >= 2 * NC)
for i, t, s in LEIT:
    print(f'   {i} {t} {s} média {MED[i]} → {classe(MED[i])}' + (f' · {reb(i)} pontos ≥ 2×NC' if reb(i) else ''))
chk('nenhuma leitura nova abaixo do NC tem reboleira (≥ 2 pontos ≥ 30): a classe é a da média', all(not (MED[i] < NC and reb(i) >= 2) for i, _, _ in LEIT))
def estado(t, D0):
    xs = [(s, i) for i, tt, s in LEIT if tt == t and d(s) <= d(D0)]
    if not xs: return ('sem leitura', None, None)
    s, i = max(xs); idade = (d(D0) - d(s)).days
    return ('atual' if idade <= VALIDADE else 'sem leitura recente', i, idade)
def media_global(D0, mut=None):
    num = den = D(0); n = 0; vals = []
    for t, a in AREA.items():
        e, i, idade = estado(t, D0)
        if e == 'atual': num += MED[i] * a; den += a; n += 1; vals.append(MED[i])
        elif mut == 'velha' and i: num += MED[i] * a; den += a
        elif mut == 'zero' and i: den += a
    if mut == 'simples': return sum(vals) / len(vals)
    return (num / den if den else None), den, n
for D0 in ('2026-09-04', '2026-09-23'):
    print('   estado em', D0, {t: estado(t, D0) for t in AREA})
m, den, n = media_global('2026-09-04')
print('   04/09: média ponderada', m, '· área com leitura atual', den, 'ha ·', n, 'pivôs')
chk('T1 média global 04/09 = Σ(média×área)/Σ área dos pivôs com leitura atual = 2.634,63/208,88 = 12,6131…', q(m, 4) == D('12.6131') and den == D('208.88'), q(m, 6))
chk('T1 PV04 em 04/09: última 27/08 com 8 dias > 7 → "sem leitura recente" (fora da média, nunca zero)', estado('PV04', '2026-09-04')[0] == 'sem leitura recente')
chk('T1 PV09 em 04/09: leitura de 28/08 com 7 dias = validade → atual', estado('PV09', '2026-09-04') == ('atual', 'VIS-067', 7))
mv, _, _ = media_global('2026-09-04', 'velha'); mz, _, _ = media_global('2026-09-04', 'zero'); ms = media_global('2026-09-04', 'simples')
print('   mutantes 04/09: leitura velha na média', q(mv, 4), '· velha como zero', q(mz, 4), '· média simples', ms)
chk('T1 mutantes distintos do oráculo (velha 14,5296 · zero 9,3407 · simples 11,75)', q(mv, 4) == D('14.5296') and q(mz, 4) == D('9.3407') and ms == D('11.75'), (q(mv, 4), q(mz, 4), ms))
m2, den2, n2 = media_global('2026-09-23')
print('   23/09: média ponderada', m2, '· área', den2, '·', n2, 'pivôs')
chk('T2 média global 23/09 (PV06 18, PV04 4, PV09 5, PV02 6; PV17 de 10/09 fora) = 2.024,34/248,70 = 8,1397…', q(m2, 4) == D('8.1397') and den2 == D('248.70') and sum(MED[i] * AREA[t] for i, t in (('VIS-051','PV06'),('VIS-057','PV04'),('VIS-071','PV09'),('VIS-072','PV02'))) == D('2024.34'), q(m2, 6))
chk('T2 classes em 04/09: PV06 9 abaixo · PV17 8 abaixo · PV09 18 acima · PV02 12 perto (12 = 0,8 × 15)',
    [classe(MED[i]) for i in ('VIS-062', 'VIS-066', 'VIS-067', 'VIS-069')] == ['abaixo', 'abaixo', 'acima', 'perto'])
# cobertura: pivôs com o protocolo na data (mamão plantado até a data; dados_lagoa_safra: plantio por pivô)
PLANT = {'PV01':('29.92','2026-05-19'),'PV02':('37.75','2025-09-02'),'PV03':('70.18','2026-05-05'),'PV04':('73.18','2025-06-10'),'PV05':('71.11','2026-08-25'),
         'PV06':('62.79','2025-03-12'),'PV07':('61.39','2026-07-28'),'PV08':('50.63','2026-08-11'),'PV09':('74.98','2025-08-05'),'PV10':('30.15','2026-03-24'),
         'PV11':('50.0','2026-10-06'),'PV12':('48.47','2026-11-24'),'PV13':('49.31','2026-10-20'),'PV14':('63.16','2026-04-07'),'PV15':('36.17','2026-07-14'),
         'PV17':('33.36','2025-10-07'),'PV18':('48.93','2025-04-02'),'PV19':('75.11','2025-04-02'),'PV20':('77.39','2025-08-05'),'PV21':('80.82','2026-03-10'),
         'PV22':('62.07','2025-09-02'),'PV23':('63.99','2025-07-08'),'PV24':('34.37','2025-03-12')}
def cob(D0): return sum(D(a) for a, p in PLANT.values() if d(p) <= d(D0)), sum(1 for a, p in PLANT.values() if d(p) <= d(D0))
c1, k1 = cob('2026-09-04'); c2, k2 = cob('2026-09-23')
print('   área com o protocolo: 04/09', c1, 'ha em', k1, 'pivôs · 23/09', c2, 'ha em', k2)
chk('T3 cobertura 04/09 = 208,88 de 1.137,45 ha (18,36 %; 20 pivôs com mamão) · 23/09 = 248,70 de 1.137,45 ha (21,86 %)',
    c1 == D('1137.45') and c2 == D('1137.45') and k1 == 20 and q(den / c1 * 100, 2) == D('18.36') and q(den2 / c2 * 100, 2) == D('21.86'), (c1, q(den / c1 * 100, 2), q(den2 / c2 * 100, 2)))

print('== PARTE 1 · pares antes × depois (antes: até 7 dias antes do 1º apontamento; depois: 3 a 14 dias após o último; dia da aplicação não entra)')
APL = [  # (talhão, produtos, 1º e último apontamento, área apontada, origem) · OS-0521..0524 propostas; APL PV06 28/08 já existe (dados_mip.APL, sem O.S.)
 ('PV06', 'Abamectina 18 EC', '2026-08-28', '2026-08-28', None, 'histórico sem O.S.'),
 ('PV04', 'Acaricida D', '2026-08-29', '2026-08-30', D('73.18'), 'OS-0521'),
 ('PV17', 'Acaricida D', '2026-08-28', '2026-08-28', D('33.36'), 'OS-0522'),
 ('PV09', 'Acaricida D', '2026-08-30', '2026-08-31', D('74.98'), 'OS-0523'),
 ('PV02', 'Fenpiroximato 50 SC + Óleo mineral', '2026-09-02', '2026-09-02', D('20'), 'OS-0524')]
def par(t, ini, fim):
    antes = [(s, i) for i, tt, s in LEIT if tt == t and d(s) < d(ini) and (d(ini) - d(s)).days <= 7]
    dep = [(s, i) for i, tt, s in LEIT if tt == t and 3 <= (d(s) - d(fim)).days <= 14]
    return (max(antes)[1] if antes else None), (min(dep)[1] if dep else None)
RED = {}
for t, prod, ini, fim, ha, orig in APL:
    a, b = par(t, ini, fim); r = (MED[a] - MED[b]) / MED[a] if (a and b and MED[a] > 0) else None
    parcial = []
    if ha is None: parcial.append('sem O.S.: dose e área não registradas')
    elif ha < AREA[t] * D('0.95'): parcial.append(f'área {ha} de {AREA[t]} ha')
    RED[orig] = (prod, r, parcial)
    print(f'   {orig} {t} {prod}: antes {a} ({MED[a]}) · depois {b} ({MED[b]}) · redução {q(r * 100, 4)} %' + (' · PARCIAL: ' + '; '.join(parcial) if parcial else ''))
chk('T4 OS-0521 PV04: (20 − 6) ÷ 20 = 70 %', RED['OS-0521'][1] == D('0.7'))
chk('T4 OS-0522 PV17: (16 − 8) ÷ 16 = 50 %', RED['OS-0522'][1] == D('0.5'))
chk('T4 OS-0523 PV09: (18 − 7,5) ÷ 18 = 58,333… %', q(RED['OS-0523'][1], 6) == D('0.583333'))
chk('T4 PV06 histórico: 59,0909… % e parcial (sem O.S.)', q(RED['histórico sem O.S.'][1], 6) == D('0.590909') and RED['histórico sem O.S.'][2])
chk('T4 OS-0524 PV02: 16,666… % e parcial (área 20 de 37,75 ha = 52,98 %)', q(RED['OS-0524'][1], 6) == D('0.166667') and RED['OS-0524'][2] and q(D(20) / D('37.75') * 100, 2) == D('52.98'))
comp = sorted(r for p, r, pa in RED.values() if p == 'Acaricida D' and not pa)
med = comp[len(comp) // 2]; media = sum(comp) / len(comp)
print('   Acaricida D: pares completos', [str(q(x * 100, 4)) for x in comp], '· mediana', q(med * 100, 4), '% · mín–máx', comp[0] * 100, '–', comp[-1] * 100, '% · média (mutante)', q(media * 100, 4))
chk('T5 ranking Acaricida D: 3 pares completos (= n mínimo 3) · mediana 58,3333 % · 50,0 a 70,0 %', len(comp) == 3 and q(med, 6) == D('0.583333') and comp[0] == D('0.5') and comp[-1] == D('0.7'))
chk('T5 mutante "média em vez de mediana" dá 59,4444 % (≠ 58,3333 %)', q(media * 100, 4) == D('59.4444'))
chk('T5 Abamectina e Fenpiroximato + óleo: 0 pares completos → "poucos casos", sem número de comparação',
    all(pa for p, r, pa in RED.values() if p != 'Acaricida D'))
# dose, produto e calda da marca no gráfico
chk('T6 OS-0521: Acaricida D 0,6 L/ha × 73,18 ha = 43,908 L; calda 1.000 L/ha × 73,18 ha = 73.180 L', D('0.6') * D('73.18') == D('43.908') and D(1000) * D('73.18') == D('73180'))
chk('T6 OS-0524: Fenpiroximato 100 mL/100 L com calda 1.000 L/ha = 1,0 L/ha; 20 ha → 20 L', D('0.1') * D(1000) / D(100) == D(1) and D(1) * D(20) == D(20))
chk('T6 carência OS-0521: 7 dias do último apontamento (30/08) → colheita liberada em 06/09', d('2026-08-30') + dt.timedelta(days=7) == d('2026-09-06'))
# pressão = soma diária do excesso acima do NC que o mapa mostraria no dia (mesma regra de validade); PV04 de 27/08 a 23/09
def pressao(t, ini, fim):
    p = D(0); sem = 0; dia = d(ini)
    while dia <= d(fim):
        e, i, idade = estado(t, dia.isoformat())
        if e == 'atual': p += max(D(0), MED[i] - NC)
        else: sem += 1
        dia += dt.timedelta(days=1)
    return p, sem
p4, s4 = pressao('PV04', '2026-08-27', '2026-09-23')
print('   pressão PV04 27/08–23/09:', p4, '(% folhas)·dia ·', s4, 'dias sem leitura atual')
chk('T7 pressão PV04 de 27/08 a 23/09 = 5 × 8 dias (27/08 a 03/09) = 40 (% folhas)·dia, com 10 dias sem leitura atual (04 a 09/09 e 18 a 21/09)', p4 == D(40) and s4 == 10, (p4, s4))
# mutante trapézio: excesso linear de 5 a 0 entre 27/08 (20) e a data em que a reta cruza 15 (20→6 em 14 dias: 5 dias) = 5×5/2 = 12,5
chk('T7 mutante trapézio (reta entre leituras) dá 12,5 ≠ 40', D(5) * D(5) / D(2) == D('12.5'))

print('== PARTE 2 · mapa de colheita: conversões, limpeza e médias (Soja, sc de 60 kg, umidade de referência 14 %: dados_cad.CULTURA_UN)')
larg, dist, massa_u, U, UP = D('9.0'), D('8.0'), D('28.8'), D(17), D(14)
area_ha = larg * dist / D(10000); kg_ha_u = massa_u / area_ha; kg_ha_14 = kg_ha_u * (100 - U) / (100 - UP); sc = kg_ha_14 / 60
print('   ponto: área', area_ha, 'ha · úmida', kg_ha_u, 'kg/ha · a 14 %', q(kg_ha_14, 6), 'kg/ha ·', q(sc, 6), 'sc/ha')
chk('P1 ponto 9 m × 8 m, 28,8 kg a 17 %: 4.000 kg/ha úmida → 3.860,465116 kg/ha a 14 % (CAL-16) → 64,341085 sc/ha',
    kg_ha_u == D(4000) and q(kg_ha_14, 6) == D('3860.465116') and q(sc, 6) == D('64.341085'))
m1, m2c, m3 = q(kg_ha_u / 60, 6), q(kg_ha_14 * 83 / 86 / 60, 6), q(kg_ha_14 / 50, 6)
print('   mutantes P1: sem correção', m1, '· corrigir duas vezes', m2c, '· saca de 50 kg', m3)
chk('P1 mutantes: sem correção 66,666667 · corrigir duas vezes 62,096629 · saca de 50 kg 77,209302', m1 == D('66.666667') and m2c == D('62.096629') and m3 == D('77.209302'), (m1, m2c, m3))
pts = [(D(72), D(4000)), (D(36), D(2000)), (D(72), D(3500))]   # (área do ponto em m², kg/ha)
pond = sum(a * y for a, y in pts) / sum(a for a, _ in pts); simp = sum(y for _, y in pts) / len(pts)
chk('P2 média ponderada pela área dos pontos = 612.000/180 = 3.400 kg/ha (a média simples 3.166,67 é o mutante; PRD 62.3)', pond == D(3400) and q(simp, 2) == D('3166.67'))
amostra = [D(x) for x in ('62', '58', '60', '61', '59', '63', '57', '60', '0', '180', '64')]
s = sorted(amostra); medn = s[len(s) // 2]; mad = sorted(abs(x - medn) for x in amostra)[len(s) // 2]; lim = D(3) * D('1.4826') * mad
fora = [x for x in amostra if abs(x - medn) > lim]
print('   outlier: mediana', medn, '· MAD', mad, '· limite ±', lim, '· excluídos', fora)
chk('P3 outlier pela mediana ± 3 × 1,4826 × MAD (mediana 60, MAD 2, ±8,8956): exclui 0 e 180, mantém 57 a 64', medn == 60 and mad == 2 and lim == D('8.8956') and fora == [D(0), D(180)])
ds, vs = [D(3), D(4), D(5)], [D(60), D(50), D(70)]
idw = sum(v / x ** 2 for v, x in zip(vs, ds)) / sum(1 / x ** 2 for x in ds)
chk('P4 IDW potência 2 com pontos a 3, 4 e 5 m (60, 50, 70) = 12,591667 ÷ 0,213611 = 58,946684', q(idw, 6) == D('58.946684'), q(idw, 6))
mapa, apur = D('62.40'), D('60.50')
chk('P5 diferença mapa × apurada = (62,40 − 60,50) ÷ 60,50 = +3,1405 %', q((mapa - apur) / apur * 100, 4) == D('3.1405'))
csv = 'lon;lat;hora;passada;vel_kmh;largura_m;dist_m;umid_pct;massa_kg\n-54,2843;-15,5588;2025-03-10T09:00:00-03:00;1;6,0;9,0;8,0;17,0;28,8\n'
h1 = hashlib.sha256(csv.encode('utf-8')).hexdigest(); h2 = hashlib.sha256(csv.encode('utf-8')).hexdigest(); h3 = hashlib.sha256(csv.replace('28,8', '28,9').encode('utf-8')).hexdigest()
chk('P6 idempotência: mesmos bytes → mesmo SHA-256 (mesma importação); 1 byte diferente → outro SHA-256 (nova versão)', h1 == h2 and h1 != h3, h1[:16])
print('\nRESUMO:', sum(OK), 'de', len(OK), 'conferências passaram')
