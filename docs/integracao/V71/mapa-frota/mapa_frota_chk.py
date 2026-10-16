# -*- coding: utf-8 -*-
"""MAPA-FROTA · conferência em Decimal (especificação executável, sem navegador).

Confere, contra as fontes do protótipo (tools/prototipo/v37/gen37), os números e as regras que a especificação MAPA-FROTA.md usa:
  R  rendimento de referência = largura × velocidade × eficiência (DEC-2609-03) e larguras dos implementos do cadastro;
  C  O.S. Em execução e conjuntos pela alocação (fonte única alocacao.py), conflito latente e ausência de alocação na Lagoa Grande;
  E  projeção de preparo do EX-38 (tanque ÷ vazão) e "quanto falta" no rendimento de referência, rotulados como projeção;
  G  plausibilidade do percurso sintético (passadas dentro da geometria demonstrativa, tempo × área ÷ (largura × velocidade));
  L  oráculo do contrato de leitura: ordem pelo instante observado, duplicata, atrasada, futura, inválida, salto impossível, idade;
  P  prioridade de fontes (telemetria > app de campo > última posição) e pausa informada;
  V  vínculo do equipamento do fornecedor ao ativo por fabricante + nº de série normalizado (nunca por nome);
  K  conflito de ativo em duas O.S. Em execução (agrupador compatível não é conflito).
Nada aqui exercita o navegador, o banco ou um fornecedor real. A posição simulada nunca produz área, consumo nem fase.
Uso: python3 -B docs/integracao/V71/mapa-frota/mapa_frota_chk.py   (sai 0 com todos OK; 1 com falha)
"""
import ast, math, os, re, sys
from decimal import Decimal as D, ROUND_HALF_UP, getcontext

getcontext().prec = 28
HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'tools', 'prototipo', 'v37', 'gen37'))
sys.path.insert(0, G)

import dados as DD            # noqa: E402  registro canônico das O.S. (Santa Rita) e talhões
import dados2 as D2           # noqa: E402  rendimento dos conjuntos (CONJ)
import dados_cad as DC        # noqa: E402  CD-03: ativos e conjuntos
import alocacao as AL         # noqa: E402  alocação vigente (fonte única de quem e o que está em cada O.S.)
import dados_lagoa_safra as DL  # noqa: E402  O.S. da Lagoa Grande
import dados_lagoa_fonte as LF  # noqa: E402  pivôs (sintéticos fora do Mac do proprietário)
from dados_config import DIA_OP  # noqa: E402  data operacional do cenário (CEN_DIA_OP)

RES = []


def chk(cid, desc, ok, val=''):
    RES.append((cid, bool(ok)))
    print(('OK    ' if ok else 'FALHA ') + cid + ' · ' + desc + (' · ' + str(val) if val != '' else ''))


def q1(x):
    return x.quantize(D('0.1'), rounding=ROUND_HALF_UP)


def br(x, n=2):
    s = f'{x:.{n}f}'
    return s.replace('.', ',')


# ------------------------------------------------------------------ R · rendimento de referência (DEC-2609-03)
print('# R · rendimento = largura (m) × velocidade (km/h) × eficiência (%) ÷ 1000 → ha/h')
for c in D2.CONJ:
    if c.get('larg') is None:
        continue
    calc = D(str(c['larg'])) * D(str(c['vel'])) * D(str(c['efic'])) / D(1000)
    chk('R-' + c['id'], c['op'] + ' · ' + c['conj'], q1(calc) == q1(D(str(c['rend']))), f'{br(calc, 3)} ha/h calculado × {br(D(str(c["rend"])), 1)} ha/h no catálogo')
A = {a['id']: a for a in DC.ATIVOS}
CJ = {c['id']: c for c in D2.CONJ}
chk('R5', 'Plantadeira 24 linhas × 0,5 m = largura do rendimento r2', D(str(A['a06']['linhas'])) * D(str(A['a06']['esp'])) == D(str(CJ['r2']['larg'])),
    f"{A['a06']['linhas']} × {A['a06']['esp']} m = {CJ['r2']['larg']} m")
chk('R6', 'Pulverizador PJ-3030: barra = largura do r1', A['a05']['barra'] == CJ['r1']['larg'], f"{A['a05']['barra']} m")
chk('R7', 'Distribuidor 3 t: largura = r3', A['a07']['larg'] == CJ['r3']['larg'], f"{A['a07']['larg']} m")
chk('R8', 'Colhedora: plataforma = r5', A['a08']['plat'] == CJ['r5']['larg'], f"{A['a08']['plat']} m")

# ------------------------------------------------------------------ C · O.S. Em execução e conjuntos pela alocação
print('# C · O.S. Em execução (registro) e conjunto pela alocação no dia operacional ' + DIA_OP)
emx = sorted(o['id'] for o in DD.ORDENS + DL.ORDENS if o['etapa'] == 'Em execução')
chk('C1', 'O.S. Em execução no registro inicial (Santa Rita + Lagoa Grande)', emx == ['OS-0420', 'OS-0421', 'OS-0505', 'OS-0506', 'OS-0507'], ', '.join(emx))


def conj_dia(os_id, dia):
    rs = sorted({a['r'] for a in AL.ALOC if a['os'] == os_id and a['dia'] == dia and AL.TIPO.get(a['r']) in ('Máquina', 'Implemento')})
    cond = any(a['sit'] == 'condicional' for a in AL.ALOC if a['os'] == os_id and a['dia'] == dia)
    return rs, cond


r21, c21 = conj_dia('OS-0421', DIA_OP)
chk('C2', 'OS-0421 em ' + DIA_OP + ': Trator 03 + Pulverizador PJ-3030 (firme)', r21 == ['PJ', 'T03'] and not c21, ' + '.join(AL.NOME[r] for r in r21))
r20, c20 = conj_dia('OS-0420', DIA_OP)
chk('C3', 'OS-0420 em ' + DIA_OP + ': Trator 02 + Plantadeira (alocação condicional; a O.S. segue "Impedida · ativo bloqueado")', r20 == ['PL', 'T02'] and c20,
    ' + '.join(AL.NOME[r] for r in r20) + ' · condicional')
sel = next(o for o in DD.ORDENS if o['id'] == 'OS-0420')['selo']
chk('C3b', 'selo da OS-0420 no registro', sel == 'Impedida · ativo bloqueado', sel)
# conflito latente: mesmo recurso, mesmo dia, horários sobrepostos em O.S. diferentes
blk = [a for a in AL.ALOC if a['sit'] != 'manutenção']
conf = sorted({(a['r'], a['os'], b['os'], a['dia']) for a in blk for b in blk
               if a['r'] == b['r'] and a['dia'] == b['dia'] and a['os'] < b['os'] and a['ini'] < b['fim'] and b['ini'] < a['fim']})
c24 = [x for x in conf if x[1:] == ('OS-0421', 'OS-0424', '2026-09-24')]
chk('C4', 'conflito latente em 24/09 06:00–11:00: PJ, MAR e PAU na OS-0421 e na OS-0424', sorted(x[0] for x in c24) == ['MAR', 'PAU', 'PJ'],
    ', '.join(f'{x[0]} {x[1]}×{x[2]}' for x in c24))
lg_os = {o['id'] for o in DL.ORDENS}
chk('C5', 'nenhuma O.S. da Lagoa Grande tem recurso na alocação (a F1 precisa da fixture de conjunto)', not any(a['os'] in lg_os for a in AL.ALOC), '0 blocos')
chk('C6', 'CD-03: conjunto padrão de pulverização é Trator 02 + PJ-3030, a OS-0421 está alocada com o Trator 03 (fonte do mapa = alocação)',
    DC.CONJUNTOS[0][1:4] == ('Trator 02', 'Pulverizador PJ-3030', 'Pulverização') and 'T03' in r21, str(DC.CONJUNTOS[0][:4]))

# ------------------------------------------------------------------ E · EX-38 (projeção) e "quanto falta"
print('# E · projeção de preparo (EX-38) e tempo restante no rendimento de referência (rotulados como projeção, não fato)')
o21 = next(o for o in DD.ORDENS if o['id'] == 'OS-0421')
tanque, saldo = D(str(A['a05']['tanque'])), D(str(o21['saldo']))
src = open(os.path.join(G, 'cenario.py'), encoding='utf-8').read()
vazao = D(re.search(r"instrucao'\] = dict\(vazao=(\d+)", src).group(1))
ha_carga = tanque / vazao
n = int((saldo / ha_carga).to_integral_value(rounding='ROUND_CEILING'))
ult = saldo - ha_carga * (n - 1)
chk('E1', 'OS-0421: tanque 3.000 L ÷ vazão 100 L/ha = 30 ha por carga', ha_carga == D(30), f'{br(ha_carga, 0)} ha')
chk('E2', 'saldo 160 ha → 6 cargas, a última com 10 ha (projeção, não carga real)', n == 6 and ult == D(10), f'{n} cargas · última {br(ult, 0)} ha')
h = saldo / D(str(CJ['r1']['rend']))
chk('E3', 'saldo 160 ha ÷ 21,6 ha/h ≈ 7,4 h (estimativa no rendimento de referência)', q1(h) == D('7.4'), f'{br(h, 3)} h')

# ------------------------------------------------------------------ G · percurso sintético (plausibilidade, nunca área)
print('# G · percurso sintético dentro da geometria demonstrativa (passadas de 36 m, recuo de 18 m nas cabeceiras)')
txt = open(os.path.join(G, 'areas', 'inicio.py'), encoding='utf-8').read()
GEO = ast.literal_eval(re.search(r'^GEO=(\[.*?\])\n', txt, re.S | re.M).group(1))
pts = [tuple(D(v) for v in p.split(',')) for p in dict((g[0], g[2]) for g in GEO)['T2'].split()]
TALHA = {t[0]: D(str(t[1])) for t in DD.TALHOES}


def area_u(p):
    s = sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))
    return abs(s) / 2


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


sg = [cross(pts[i], pts[(i + 1) % 4], pts[(i + 2) % 4]) for i in range(4)]
chk('G1', 'T2 é convexo (o trecho entre passadas fica dentro)', all(x > 0 for x in sg) or all(x < 0 for x in sg))
s = (TALHA['T2'] * D(10000) / area_u(pts)).sqrt()
chk('G2', 'escala do desenho da Santa Rita: 298 ha ÷ área do polígono', D('6') < s < D('7.5'), f'{br(s, 3)} m por unidade do SVG')
d_u, rc_u = D(36) / s, D(18) / s
xs = [p[0] for p in pts]
x, passes = min(xs) + d_u / 2, []
while x < max(xs) - d_u / 2:
    ys = []
    for i in range(4):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % 4]
        if x1 != x2 and min(x1, x2) <= x <= max(x1, x2):
            ys.append(y1 + (x - x1) * (y2 - y1) / (x2 - x1))
    lo, hi = min(ys) + rc_u, max(ys) - rc_u
    if hi > lo:
        passes.append((x, lo, hi))
    x += d_u
rota = []
for k, (x, lo, hi) in enumerate(passes):
    rota += [(x, lo), (x, hi)] if k % 2 == 0 else [(x, hi), (x, lo)]
sgn = 1 if sg[0] > 0 else -1
dentro = all(all(sgn * cross(pts[i], pts[(i + 1) % 4], p) > 0 for i in range(4)) for p in rota)
L_u = sum(((rota[i + 1][0] - rota[i][0]) ** 2 + (rota[i + 1][1] - rota[i][1]) ** 2).sqrt() for i in range(len(rota) - 1))
L_m = L_u * s
chk('G3', 'T2: todos os vértices do percurso dentro do polígono', dentro and len(passes) > 40, f'{len(passes)} passadas · {br(L_m / 1000, 1)} km')
t_rota = L_m / D(8000)
t_ref = TALHA['T2'] * D(10000) / (D(36) * D(8000))
chk('G4', 'tempo do percurso a 8 km/h × área ÷ (36 m × 8 km/h): plausível (0,85–1,05), não é medida de área',
    D('0.85') <= t_rota / t_ref <= D('1.05'), f'{br(t_rota, 2)} h × {br(t_ref, 2)} h · razão {br(t_rota / t_ref, 3)}')
v_px = D(8000) / D(3600) / s
chk('G4b', '8 km/h no desenho da Santa Rita (1 unidade ≈ 1 px a 1440 px): movimento lento, legível só com rumo e rastro', v_px < D(1), f'{br(v_px, 2)} unidade/s')
pv = {p[0]: p for p in LF.LG_PIVOS}['PV19']
r_ha = (D(str(pv[2])) * D(10000) / D(str(math.pi))).sqrt()
chk('G5', 'Pivô 19: raio pela área (tgRaioDeHa) = raio da geometria', abs(r_ha - D(str(pv[5]))) <= D('0.01'), f'{br(r_ha, 2)} m × {pv[5]} m ({LF.ROTULO})')
r, d, rc = D(str(pv[5])), D(36), D(18)
x, ok_c, Lc, np_ = -r + d / 2, True, D(0), 0
while x < r - d / 2:
    hc = (r * r - x * x).sqrt() - rc
    if hc > 0:
        np_ += 1
        Lc += 2 * hc
        ok_c = ok_c and (x * x + hc * hc) < r * r
    x += d
chk('G6', 'Pivô 19: passadas de 36 m com recuo de 18 m ficam dentro do círculo (percurso em metros relativos ao centro, sem coordenada real gravada)',
    ok_c and np_ > 20, f'{np_} passadas · {br(Lc / 1000, 1)} km')

# ------------------------------------------------------------------ L · oráculo do contrato de leitura
print('# L · leituras de uma fonte: ordem pelo instante observado; limite de idade declarado pela fonte (fixture: 60 s)')
TOL_FUT, VMAX = 120, D(60)   # tolerância de relógio para "futura" (s) e velocidade máxima plausível da classe (km/h), declaradas na fixture


def dist_m(a, b):
    k = D(str(math.cos(math.radians(float(a['lat'])))))
    dx = (b['lon'] - a['lon']) * D(111320) * k
    dy = (b['lat'] - a['lat']) * D(110540)
    return (dx * dx + dy * dy).sqrt()


def valida(r):
    try:
        la, lo = D(str(r['lat'])), D(str(r['lon']))
    except Exception:
        return False
    return la.is_finite() and lo.is_finite() and abs(la) <= 90 and abs(lo) <= 180 and not (la == 0 and lo == 0)


def processar(recebidas):
    """recebidas: leituras na ordem de chegada. Devolve atual, rastro (ordenado por observado), recusadas e suspeitas."""
    atual, rastro, vistos, recus, susp = None, [], set(), [], None
    for r in recebidas:
        if r['id'] in vistos:
            recus.append((r['id'], 'duplicada'))
            continue
        vistos.add(r['id'])
        if not valida(r):
            recus.append((r['id'], 'inválida'))
            continue
        if r['obs'] > r['rec'] + TOL_FUT:
            recus.append((r['id'], 'futura'))
            continue
        if atual is not None and r['obs'] == atual['obs']:
            recus.append((r['id'], 'mesmo instante'))
            continue
        if atual is not None and r['obs'] < atual['obs']:
            rastro.append(dict(r, atrasada=True))
            continue
        if susp is not None:   # a leitura anterior saltou: esta decide
            v_s = dist_m(susp, r) / D(r['obs'] - susp['obs']) * D('3.6')
            if v_s <= VMAX:
                rastro.append(susp)
                atual = susp
            else:
                recus.append((susp['id'], 'salto descartado'))
            susp = None
        if atual is not None:
            v = dist_m(atual, r) / D(r['obs'] - atual['obs']) * D('3.6')
            if v > VMAX:
                susp = r
                continue
        rastro.append(r)
        atual = r
    return dict(atual=atual, rastro=sorted(rastro, key=lambda x: x['obs']), recus=recus, susp=susp)


def idade_txt(seg):
    m = seg // 60
    return f'há {m} min' if m < 60 else f'há {m // 60} h {m % 60:02d} min'


def situacao(res, agora, limite):
    a = res['atual']
    if a is None:
        return ('Posição indisponível', None)
    idade = agora - a['obs']
    return ('Atual', idade) if idade <= limite else ('Sem sinal ' + idade_txt(idade), idade)


def R_(i, obs, rec, dlat=0, dlon=0, lat=None, lon=None):
    base_lat, base_lon = D('-34.629941'), D('-47.122425')   # centro sintético do Pivô 19 (no mar, lat < −34)
    return dict(id=i, obs=obs, rec=rec, lat=base_lat + D(str(dlat)) if lat is None else lat, lon=base_lon + D(str(dlon)) if lon is None else lon)


m10 = D('0.0001')   # ≈ 11 m em latitude
seq = [R_('a', 0, 1), R_('b', 10, 11, dlat=m10), R_('c', 20, 21, dlat=2 * m10)]
res = processar(seq)
chk('L1', 'sequência normal: atual = última observada; idade 5 s ≤ 60 s', res['atual']['id'] == 'c' and situacao(res, 25, 60) == ('Atual', 5))
res = processar(seq + [R_('b', 10, 30, dlat=m10)])
chk('L2', 'duplicata (mesmo id) ignorada, sem mexer no rastro', [x['id'] for x in res['rastro']] == ['a', 'b', 'c'] and ('b', 'duplicada') in res['recus'])
res = processar(seq + [R_('d', 15, 40, dlat=D('1.5') * m10)])
chk('L3', 'atrasada (observada antes da atual): entra no rastro marcada, o marcador não volta',
    res['atual']['id'] == 'c' and [x['id'] for x in res['rastro']] == ['a', 'b', 'd', 'c'] and res['rastro'][2].get('atrasada'))
res = processar(seq + [R_('f', 400, 30, dlat=3 * m10)])
chk('L4', 'futura (observada > recebida + 120 s): recusada, não vira atual', res['atual']['id'] == 'c' and ('f', 'futura') in res['recus'])
res = processar(seq + [R_('g', 30, 31, lat=D(95)), R_('z', 31, 32, lat=D(0), lon=D(0))])
chk('L5', 'inválida (latitude 95° ou 0,0): recusada', res['atual']['id'] == 'c' and ('g', 'inválida') in res['recus'] and ('z', 'inválida') in res['recus'])
res = processar(seq)
chk('L6', 'fronteira do limite: idade 60 s = Atual; 61 s = Sem sinal há 1 min',
    situacao(res, 80, 60) == ('Atual', 60) and situacao(res, 81, 60)[0] == 'Sem sinal há 1 min')
chk('L6b', 'texto da idade: 1.145 s → há 19 min; 3.900 s → há 1 h 05 min', idade_txt(1145) == 'há 19 min' and idade_txt(3900) == 'há 1 h 05 min')
chk('L7', 'nenhuma leitura: Posição indisponível (nunca o centro do talhão)', situacao(processar([]), 100, 60) == ('Posição indisponível', None))
salto = D('0.02')   # ≈ 2,2 km em 10 s ≈ 800 km/h
res = processar(seq + [R_('s', 30, 31, dlat=salto), R_('t', 40, 41, dlat=salto + m10)])
chk('L8', 'salto impossível confirmado pela leitura seguinte coerente: suspeita vira posição, a seguinte é a atual',
    res['atual']['id'] == 't' and [x['id'] for x in res['rastro']][-2:] == ['s', 't'])
res = processar(seq + [R_('s', 30, 31, dlat=salto), R_('u', 40, 41, dlat=3 * m10)])
chk('L9', 'salto isolado (a seguinte volta para perto): a suspeita é descartada', res['atual']['id'] == 'u' and ('s', 'salto descartado') in res['recus'])
res = processar(seq + [R_('c2', 20, 22, dlat=5 * m10)])
chk('L10', 'mesmo instante observado com outro id na mesma fonte: o segundo não troca a posição', res['atual']['id'] == 'c' and ('c2', 'mesmo instante') in res['recus'])

# ------------------------------------------------------------------ P · prioridade de fontes por máquina
print('# P · telemetria > app de campo > última posição; pausa informada não é "sem sinal"')
PRIO = ['telemetria', 'app']


def escolher(fontes, agora):
    """fontes: {tipo: dict(obs=, limite=, conectada=True, pausa=None)}; devolve (fonte, rótulo)."""
    atuais = [t for t in PRIO if t in fontes and fontes[t].get('conectada', True) and fontes[t]['obs'] is not None
              and agora - fontes[t]['obs'] <= fontes[t]['limite']]
    for t in PRIO:
        f = fontes.get(t)
        if f and f.get('pausa') is not None and f.get('online', True) and t == 'app' and not atuais:
            return ('app', 'Parada · pausa desde ' + f['pausa'] + ' · posição da pausa')
    if atuais:
        return (atuais[0], 'Atual')
    ult = [(f['obs'], t) for t, f in fontes.items() if f['obs'] is not None]
    if not ult:
        return (None, 'Posição indisponível')
    obs, t = max(ult)
    if not fontes[t].get('conectada', True):
        return (t, 'Sem fonte: ' + t + ' desconectada · última ' + idade_txt(agora - obs))
    return (t, 'Sem sinal ' + idade_txt(agora - obs))


chk('P1', 'telemetria e app atuais: vale a telemetria', escolher({'telemetria': dict(obs=100, limite=60), 'app': dict(obs=100, limite=120)}, 110) == ('telemetria', 'Atual'))
chk('P2', 'telemetria velha (300 s) e app atual: vale o app (troca marcada no rastro)', escolher({'telemetria': dict(obs=0, limite=60), 'app': dict(obs=250, limite=120)}, 300) == ('app', 'Atual'))
chk('P3', 'as duas velhas: a mais recente, como Sem sinal', escolher({'telemetria': dict(obs=0, limite=60), 'app': dict(obs=100, limite=120)}, 300) == ('app', 'Sem sinal há 3 min'))
chk('P4', 'telemetria desconectada e sem app: "Sem fonte" com a última posição (visual de sem sinal)',
    escolher({'telemetria': dict(obs=0, limite=60, conectada=False)}, 600) == ('telemetria', 'Sem fonte: telemetria desconectada · última há 10 min'))
chk('P5', 'app em pausa informada (aparelho com sinal): "Parada · pausa", não "Sem sinal"',
    escolher({'app': dict(obs=0, limite=120, pausa='11:02', online=True)}, 2400) == ('app', 'Parada · pausa desde 11:02 · posição da pausa'))
chk('P6', 'app em pausa mas sem sinal do aparelho: volta a ser Sem sinal',
    escolher({'app': dict(obs=0, limite=120, pausa='11:02', online=False)}, 2400) == ('app', 'Sem sinal há 40 min'))
chk('P7', 'nenhuma fonte com leitura: Posição indisponível', escolher({'telemetria': dict(obs=None, limite=60)}, 10) == (None, 'Posição indisponível'))

# ------------------------------------------------------------------ V · vínculo por fabricante + nº de série
print('# V · equipamento do fornecedor × ativo do cadastro (série normalizada; nome nunca vincula)')


def norm(s):
    return re.sub(r'[\s\-./]', '', str(s or '')).upper()


CAD = [dict(id='a01', nome='Trator T1', fab='John Deere', modelo='6M 155', serie='SINT-JD-6M155-0001'),
       dict(id='a04', nome='Trator 04', fab='John Deere', modelo='5078E', serie='SINT-JD-5078E-0004'),
       dict(id='a02', nome='Trator 02', fab='Massey Ferguson', modelo='7719', serie='SINT-MF-7719-0002'),
       dict(id='x1', nome='Trator A', fab='John Deere', modelo='6110J', serie='SINT-JD-REP-0009'),
       dict(id='x2', nome='Trator B', fab='John Deere', modelo='6110J', serie='SINT-JD-REP-0009')]


def vincular(e):
    if not norm(e.get('serie')):
        return ('confirmar', 'sem nº de série no fornecedor')
    cs = [a for a in CAD if norm(a['serie']) == norm(e['serie'])]
    if not cs:
        return ('sem_ativo', '')
    if len(cs) > 1:
        return ('confirmar', 'série repetida no cadastro: ' + ', '.join(a['id'] for a in cs))
    a = cs[0]
    if norm(a['fab']) != norm(e['fab']):
        return ('confirmar', 'fabricante diferente')
    if norm(a['modelo']) != norm(e['modelo']):
        return ('confirmar', 'modelo diferente: ' + a['modelo'] + ' × ' + e['modelo'])
    return ('vinculado', a['id'])


chk('V1', 'série igual (caixa diferente), mesmo fabricante e modelo: vinculado sozinho', vincular(dict(fab='John Deere', modelo='6M 155', serie='sint-jd-6m155-0001')) == ('vinculado', 'a01'))
chk('V2', 'série com espaços no lugar dos hífens: mesma série normalizada', vincular(dict(fab='JOHN DEERE', modelo='5078 E', serie='SINT JD 5078E 0004')) == ('vinculado', 'a04'))
chk('V3', 'série igual e modelo diferente: confirmar vínculo', vincular(dict(fab='John Deere', modelo='5075E', serie='SINT-JD-5078E-0004'))[0] == 'confirmar')
chk('V4', 'série desconhecida: sem ativo no cadastro (criar ou ignorar)', vincular(dict(fab='John Deere', modelo='8R 340', serie='SINT-JD-8R-0099')) == ('sem_ativo', ''))
chk('V5', 'mesmo nome "Trator T1", série diferente: nunca vincula por nome', vincular(dict(fab='John Deere', modelo='6M 155', serie='SINT-JD-OUTRO-0777', nome='Trator T1'))[0] == 'sem_ativo')
chk('V6', 'série repetida no cadastro: confirmar, nunca escolher sozinho', vincular(dict(fab='John Deere', modelo='6110J', serie='SINT-JD-REP-0009'))[0] == 'confirmar')
chk('V7', 'fornecedor sem nº de série: confirmar', vincular(dict(fab='John Deere', modelo='6M 155', serie=''))[0] == 'confirmar')
chk('V8', 'série igual de outro fabricante: confirmar', vincular(dict(fab='Case IH', modelo='7719', serie='SINT-MF-7719-0002')) == ('confirmar', 'fabricante diferente'))

# ------------------------------------------------------------------ K · conflito de ativo entre O.S. Em execução
print('# K · um ativo em duas O.S. Em execução incompatíveis = conflito (sem escolher uma); mesmo agrupador não é conflito')


def conflitos(conjs, etapa, grupo):
    por = {}
    for os_id, rs in conjs.items():
        if etapa.get(os_id) != 'Em execução':
            continue
        for r in rs:
            por.setdefault(r, []).append(os_id)
    out = {}
    for r, oss in por.items():
        gs = {grupo.get(o) or o for o in oss}
        if len(oss) > 1 and len(gs) > 1:
            out[r] = sorted(oss)
    return out


cj = {'OS-0421': ['T03', 'PJ'], 'OS-0424': ['T04', 'PJ'], 'OS-0430': ['T03', 'PJ']}
chk('K1', 'PJ na OS-0421 e na OS-0424, as duas Em execução: conflito com as duas origens',
    conflitos(cj, {'OS-0421': 'Em execução', 'OS-0424': 'Em execução', 'OS-0430': 'A liberar'}, {}) == {'PJ': ['OS-0421', 'OS-0424']})
chk('K2', 'as mesmas O.S. no mesmo agrupador (OS-LOTE): sem conflito',
    conflitos(cj, {'OS-0421': 'Em execução', 'OS-0424': 'Em execução'}, {'OS-0421': 'G1', 'OS-0424': 'G1'}) == {})
chk('K3', 'O.S. A liberar não ocupa o ativo no mapa', conflitos(cj, {'OS-0421': 'Em execução', 'OS-0430': 'A liberar'}, {}) == {})

ok = sum(1 for _, x in RES if x)
print(f'\n{ok} OK · {len(RES) - ok} falhas')
sys.exit(0 if ok == len(RES) else 1)
