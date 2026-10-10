# -*- coding: utf-8 -*-
"""Teste focal da camada sintética (CAMADA-SINTETICA-01), sem navegador. Uso (de gen37/): python3 dados_lagoa_sintetico/camada_test.py
Confere: determinismo byte a byte, estrutura do specs/esquema_lagoa.md, IDs e ordem iguais em todos os arquivos, áreas (raio, círculo,
pixels), pixels dentro do dono, narrativa da safra nos índices, rótulo, categorias de dado real (varrer_categorias.py), modo sem dado
real, falta da camada e regeneração da saída adulterada."""
import base64, hashlib, json, math, os, shutil, struct, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.dirname(HERE); sys.path.insert(0, GEN)
os.environ['SAFRION_DADOS'] = 'sintetico'
import dados_lagoa_fonte as F
from dados_lagoa_sintetico import gerar as G, kml as K
OK = []
def chk(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHOU ') + nome + ('' if cond else ' · ' + str(info)[:400]), flush=True)
def lj(n): return json.load(open(os.path.join(F.DIR, n), encoding='utf-8'))
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
ARQS = ['lagoa_s2_resumo.json', 'lagoa_s2.json', 'lagoa_pivos.geojson', 'lagoa_cadastro.json', 'lagoa_rgb.json', 'lagoa_analise.json', 'cenas.json',
        'lagoa_20260910.png', 'lagoa_20260925.png', 'lagoa_rgb_20260910.png', 'lagoa_rgb_20260925.png']

# 1 · modo sem dado real e rótulo
chk('1 fonte sintética: REAL falso, DIR = dados_lagoa_sintetico/saida, rótulo "Demonstração sintética", nada do real importado',
    F.REAL is False and F.DIR == G.SAIDA and F.ROTULO == 'Demonstração sintética' and 'dados_lagoa_kml' not in sys.modules
    and K.LG_FONTE.startswith('Demonstração sintética') and K.LG_GEO.startswith('Demonstração sintética'), [F.REAL, F.DIR, F.ROTULO])

# 2 · determinismo: duas gerações em pastas novas = mesmos bytes = carimbo da saída
d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
try:
    c1, c2 = G.gerar(d1), G.gerar(d2); car = json.load(open(os.path.join(F.DIR, '_carimbo.json'), encoding='utf-8'))
    chk('2 determinístico: 2 gerações idênticas byte a byte e iguais à saída em uso (11 arquivos)',
        c1['arquivos'] == c2['arquivos'] == car['arquivos'] and sorted(c1['arquivos']) == sorted(ARQS)
        and all(sha(os.path.join(F.DIR, n)) == h for n, h in car['arquivos'].items()), [len(c1['arquivos'])])
finally:
    shutil.rmtree(d1, ignore_errors=True); shutil.rmtree(d2, ignore_errors=True)

# 3 · estrutura (specs/esquema_lagoa.md)
R, S2, GJ, CAD, RGB, AN, CEN = (lj(n) for n in ARQS[:7])
ids = [f'PV{n:02d}' for n in range(1, 25) if n != 16]
est_ok = all(set(c['est'][p]) == set(G.IDX) | {'nuvem'} and all(set(c['est'][p][n]) == {'med', 'p10', 'p90', 'n'} for n in G.IDX) for c in R['cenas'] for p in ids)
chk('3 estrutura: chaves e quantidades do esquema (23 pivôs, 2 cenas, 5 índices, cadastro 3/19/16, 4 cantos, KML 2/18/16)',
    set(R) == {'pivos', 'cantos', 'idx', 'H', 'W', 'cenas'} and set(S2) == {'pivos', 'cenas', 'idx', 'H', 'W', 'cantos', 'pix', 'dono'}
    and all(set(p) == {'id', 'rot', 'nome', 'ha', 'lon', 'lat', 'r_m'} for p in R['pivos']) and len(R['cantos']) == 4 and R['idx'] == G.IDX
    and all(set(c) == {'id', 'dt', 'hora_utc', 'nuvem', 'png', 'est'} for c in R['cenas']) and all(set(c) == {'id', 'dt', 'nuvem', 'png', 'q', 'est'} for c in S2['cenas'])
    and set(CAD) == {'fazenda', 'municipio', 'uf', 'fonte', 'pivos', 'perimetros', 'ambiental', 'agua'}
    and (len(CAD['pivos']), len(CAD['perimetros']), len(CAD['ambiental']), len(CAD['agua'])) == (23, 3, 19, 16)
    and set(RGB) == {'lagoa_rgb_20260925.png', 'lagoa_rgb_20260910.png'} and set(AN) == {'desc', 'fases', 'cenas'} and len(AN['fases']) == 5
    and set(AN['cenas']) == {'25/09', '10/09'} and AN['cenas']['10/09']['ant'] is None and len(CEN) == 2 and est_ok
    and len(K.LG_PIVOS) == 23 and all(len(t) == 6 for t in K.LG_PIVOS) and len(K.LG_PERIMETROS) == 2
    and all(set(p) == {'area', 'car', 'mf', 'mun', 'nome', 'temas'} for p in K.LG_PERIMETROS) and len(K.LG_AMBIENTAL) == 18
    and all(len(t) == 4 and isinstance(t[3], bool) for t in K.LG_AMBIENTAL) and len(K.LG_AGUA) == 16
    and all(set(a) == {'curso', 'desc', 'fin', 'id', 'lat', 'lon', 'modo', 'nome', 'num', 'proc', 'regime', 'renov', 'tipo', 'vazao', 'venc'} for a in K.LG_AGUA),
    [list(R), list(S2), len(CAD['ambiental'])])

# 4 · IDs e ordem iguais em todos os arquivos; rótulo 'P{n}' que o mapa converte em 'Pivô n'
lp = [(p[0], p[2], p[3], p[4], p[5]) for p in K.LG_PIVOS]
chk('4 IDs PV01–PV24 sem PV16, mesma ordem e mesmos valores no KML, resumo, pixels, GeoJSON e cadastro',
    [p[0] for p in K.LG_PIVOS] == ids and R['pivos'] == S2['pivos'] and [(p['id'], p['ha'], p['lon'], p['lat'], p['r_m']) for p in R['pivos']] == lp
    and [f['properties']['id'] for f in GJ['features']] == ids and [(p['id'], p['area_ha'], p['centro'][0], p['centro'][1], p['raio_m']) for p in CAD['pivos']] == lp
    and all(p['rot'] == 'P' + str(int(p['id'][2:])) and p['nome'] == 'Pivô ' + str(int(p['id'][2:])) for p in R['pivos'])
    and F.PIVOS_HA == {int(p[0][2:]): round(p[2], 2) for p in K.LG_PIVOS}, [p[0] for p in K.LG_PIVOS][:5])   # SINT-C01: sem arredondar a inteiro

# 5 · áreas: raio pela área, círculo do GeoJSON pela área (excesso esférico, como talgeo.js), sem sobreposição, perímetro do imóvel
def area_anel(r):
    r = r[:-1]; n = len(r); s = 0.0
    for i in range(n):
        p1, p2, p3 = r[i], r[(i + 1) % n], r[(i + 2) % n]; s += (math.radians(p3[0]) - math.radians(p1[0])) * math.sin(math.radians(p2[1]))
    return abs(s * 6378137 ** 2 / 2) / 1e4
err_r = max(abs(p[5] - math.sqrt(p[2] * 1e4 / math.pi)) for p in K.LG_PIVOS)
err_a = max(abs(area_anel(f['geometry']['coordinates'][0]) - f['properties']['ha']) / f['properties']['ha'] for f in GJ['features'])
xy = [(*G.m_de_ll(p[3], p[4]), p[5]) for p in K.LG_PIVOS]
folga = min(math.hypot(a[0] - b[0], a[1] - b[1]) - a[2] - b[2] for i, a in enumerate(xy) for b in xy[i + 1:])
# o círculo de 72 lados com as constantes do talgeo.js (110 540 m/grau de latitude × esfera de 6 378 137 m) sai ≈ +0,58 % da área declarada,
# como no próprio app; o limite é o mesmo 1 % a partir do qual o tmValida pede motivo
chk('5 áreas: raio = √(ha·10⁴/π) (±0,01 m), círculo do GeoJSON ≈ ha (< 1 %), pivôs sem sobreposição, imóvel > soma dos pivôs',
    err_r <= 0.006 and err_a < 0.01 and folga > 50 and K.LG_PERIMETROS[0]['area'] > sum(p[2] for p in K.LG_PIVOS), [err_r, err_a, folga])

# 6 · pixels: tamanhos coerentes, dono válido, cada pixel dentro do círculo do dono, contagem ≈ área, 255 só na nuvem de 10/09
pix = base64.b64decode(S2['pix']); dono = base64.b64decode(S2['dono']); npx = len(dono)
rc = [struct.unpack_from('<HH', pix, 4 * i) for i in range(npx)]
x0, y0 = -G.MARGEM, -G.MARGEM
fora = sum(1 for (r, c), k in zip(rc, dono) if math.hypot(x0 + (c + 0.5) * G.PX - xy[k][0], y0 + (r + 0.5) * G.PX - xy[k][1]) > xy[k][2] + 1e-6)
cont = [0] * 23
for k in dono: cont[k] += 1
err_px = max(abs(cont[k] * G.PX ** 2 / 1e4 - K.LG_PIVOS[k][2]) / K.LG_PIVOS[k][2] for k in range(23))
qs = {c['dt']: {n: base64.b64decode(c['q'][n]) for n in G.IDX} for c in S2['cenas']}
nuv = {dtc: sum(1 for b in q['NDVI'] if b == 255) for dtc, q in qs.items()}
chk('6 pixels: pix = 4·n bytes, q de cada índice com n bytes, dono < 23, todos dentro do círculo do dono, n·100 m² ≈ ha (±3 %), nuvem só em 10/09',
    len(pix) == 4 * npx and all(len(b) == npx for q in qs.values() for b in q.values()) and max(dono) == 22 and fora == 0 and err_px < 0.03
    and nuv['2026-09-25'] == 0 and nuv['2026-09-10'] > 0 and all(r < S2['H'] and c < S2['W'] for r, c in rc), [fora, err_px, nuv])

# 7 · estatística publicada = recalculada dos pixels quantizados (o que o mapa desenha)
def med(vs): vs = sorted(vs); return round(vs[int(round(0.5 * (len(vs) - 1)))], 3)
dif = []
for c in S2['cenas']:
    for k, p in enumerate(ids):
        for n in G.IDX:
            vs = [G.deq(b) for b, d in zip(qs[c['dt']][n], dono) if d == k and b != 255]
            if abs(med(vs) - c['est'][p][n]['med']) > 1e-9: dif.append((c['dt'], p, n))
chk('7 mediana de cada pivô e índice = recalculada dos pixels quantizados (q/125 − 1); nuvem % do pivô coerente; cena mais recente primeiro (padrão do mapa)',
    not dif and [c['dt'] for c in R['cenas']] == ['2026-09-25', '2026-09-10'] and R['cenas'][1]['est']['PV24']['nuvem'] > 0 and all(R['cenas'][0]['est'][p]['nuvem'] == 0 for p in ids), dif[:5])

# 8 · narrativa: fase pela data de plantio (dados_lagoa_safra) e renovação do Pivô 12
C, renov, _ = G._literais_safra()
fase = {c['dt']: {p: AN['cenas'][f"{c['dt'][8:10]}/{c['dt'][5:7]}"]['piv'][p]['fase'] for p in ids} for c in R['cenas']}
nd = {c['dt']: {p: c['est'][p]['NDVI']['med'] for p in ids} for c in R['cenas']}
ordem = ['preparo · solo exposto', 'plantio recente', 'formação inicial', 'formação · pré-florada', 'início da produção', 'produção']
media = lambda d, f: [nd[d][p] for p in ids if fase[d][p] == f]
seq = [sum(m) / len(m) for f in ordem for m in [media('2026-09-25', f)] if m]
chk('8 narrativa: NDVI médio cresce com a fase (preparo < plantio < formação < produção); Pivô 12 lavoura velha em 10/09 e solo exposto em 25/09',
    seq == sorted(seq) and len(seq) >= 4 and 12 in renov and nd['2026-09-10']['PV12'] > 0.55 and nd['2026-09-25']['PV12'] < 0.25
    and fase['2026-09-25']['PV12'].startswith('renovação'), [seq, nd['2026-09-10']['PV12'], nd['2026-09-25']['PV12']])

# 9 · identificadores fictícios e sem categoria de dado real (varrer_categorias.py, fonte única das regras)
tmp = tempfile.mkdtemp()
try:
    for n in os.listdir(F.DIR): shutil.copy(os.path.join(F.DIR, n), tmp)
    for n in ('kml.py', 'gerar.py', '__init__.py'): shutil.copy(os.path.join(HERE, n), tmp)
    v = subprocess.run([sys.executable, os.path.join(GEN, '..', 'ferramentas', 'varrer_categorias.py'), tmp], capture_output=True, text=True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
chk('9 CAR "SINTETICO-…", outorga "SINT-nnn/0000", cenas "SINTETICO-S2-…", local no mar (lat < −34) e varrer_categorias TOTAL 0 na saída e nas fontes',
    all(p['car'].startswith('SINTETICO-') for p in K.LG_PERIMETROS) and all(a['num'].startswith('SINT-') for a in K.LG_AGUA)
    and all(c['id'].startswith('SINTETICO-S2-') for c in R['cenas']) and all(p[4] < -34 for p in K.LG_PIVOS) and v.stdout.strip().endswith('TOTAL 0'),
    v.stdout[-300:] + v.stderr[-300:])

# 10 · falta da camada: mensagem clara; 11 · saída adulterada é refeita igual
tmp = tempfile.mkdtemp()
try:
    shutil.copy(os.path.join(GEN, 'dados_lagoa_fonte.py'), tmp)
    sem = subprocess.run([sys.executable, '-c', 'import dados_lagoa_fonte'], cwd=tmp, capture_output=True, text=True, env=dict(os.environ, PYTHONPATH=tmp))
    G.gerar(tmp); car0 = json.load(open(os.path.join(tmp, '_carimbo.json'), encoding='utf-8'))
    with open(os.path.join(tmp, 'lagoa_s2.json'), 'r+b') as f: f.seek(100); f.write(b'#')
    antes = G.em_dia(tmp); G.garantir(tmp); depois = G.em_dia(tmp) and sha(os.path.join(tmp, 'lagoa_s2.json')) == car0['arquivos']['lagoa_s2.json']
finally:
    shutil.rmtree(tmp, ignore_errors=True)
chk('10 sem a camada: o import falha com "Sem dados da Lagoa Grande … gere dados_lagoa_sintetico/"',
    sem.returncode != 0 and 'Sem dados da Lagoa Grande' in sem.stderr and 'dados_lagoa_sintetico' in sem.stderr, sem.stderr[-300:])
chk('11 saída adulterada: em_dia() acusa e garantir() refaz com os mesmos bytes', antes is False and depois, [antes, depois])

# 12 · SINT-G01: carimbo parcial, com arquivo a mais ou fora do formato não vale; garantir() refaz o conjunto inteiro
tmp = tempfile.mkdtemp()
try:
    car0 = G.gerar(tmp); cp = os.path.join(tmp, '_carimbo.json')
    def carimbo(c): json.dump(c, open(cp, 'w', encoding='utf-8'))
    um = next(iter(sorted(car0['arquivos'])))
    for n in car0['arquivos']:
        if n != um: os.remove(os.path.join(tmp, n))
    carimbo(dict(car0, arquivos={um: car0['arquivos'][um]})); parcial = G.em_dia(tmp)
    G.garantir(tmp); refeito = G.em_dia(tmp) and sorted(os.listdir(tmp)) == sorted(list(car0['arquivos']) + ['_carimbo.json'])
    open(os.path.join(tmp, 'extra.json'), 'w').write('{}')
    carimbo(dict(car0, arquivos=dict(car0['arquivos'], **{'extra.json': sha(os.path.join(tmp, 'extra.json'))}))); a_mais = G.em_dia(tmp)
    carimbo(dict(car0, arquivos=list(car0['arquivos']))); formato = G.em_dia(tmp)
    carimbo(car0); valido = G.em_dia(tmp)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
chk('12 SINT-G01: carimbo com 1 arquivo, com arquivo a mais ou com "arquivos" fora do formato → em_dia False; garantir() refaz as 11 saídas; carimbo íntegro → True',
    parcial is False and refeito and a_mais is False and formato is False and valido is True, [parcial, refeito, a_mais, formato, valido])

# 13 · SINT-C01: a mesma área (2 casas) no mapa, no cadastro, na safra, nos cultivos e nas O.S.
import dados_lagoa_safra as DLS
mapa = {int(p['id'][2:]): p['ha'] for p in R['pivos']}
cad = {int(p['id'][2:]): p['area_ha'] for p in CAD['pivos']}
cult = {int(c['local'].split()[-1]): c['area'] for c in DLS.CULTIVOS}
tal = {int(t.split()[-1]): ha for t, ha in DLS.TALHOES.items()}
ords = {o['id']: (o['area'], mapa[int(o['talhao'].split()[-1])]) for o in DLS.ORDENS}
chk('13 SINT-C01: PIVOS_HA = área do mapa = cadastro = TALHOES = CULTIVOS = área de cada O.S. (igualdade exata, sem tolerância); 22+ áreas com decimais',
    F.PIVOS_HA == mapa == cad == tal == cult and all(a == m for a, m in ords.values()) and sum(1 for v in mapa.values() if v != int(v)) >= 20,
    [k for k in mapa if not (F.PIVOS_HA.get(k) == mapa[k] == cad.get(k) == tal.get(k))][:5])

# 14 · SINT-C02: sementes de ordens/apontamentos/saldos/frações/textos/insumos coerentes com a área, também com áreas trocadas
def invariantes(L):
    e = []; br = L._br
    for o in L.ORDENS:
        ap = [a for a in L.AP.get(o['id'], []) if a[3] != 'Previsto']
        if not (0 <= o['realizado'] <= o['area'] + 1e-9): e.append((o['id'], 'realizado > área'))
        if abs(o['saldo'] - round(max(0, o['area'] - o['realizado']), 2)) > 1e-9: e.append((o['id'], 'saldo'))
        if o['id'] in L.AP and abs(sum(a[2] for a in ap) - o['realizado']) > 1e-6: e.append((o['id'], 'apontamentos ≠ realizado'))
        if o['id'] in L.AP and abs(sum(a[2] for a in L.AP[o['id']]) - o['area']) > 1e-6 and o['etapa'] != 'Em execução' or (o['etapa'] == 'Em execução' and o['id'] != 'OS-0507' and abs(sum(a[2] for a in L.AP[o['id']]) - o['area']) > 1e-6):
            e.append((o['id'], 'apontamentos previstos ≠ área'))
        if o['etapa'] in ('Encerradas', 'Em conferência') and (o['realizado'] != o['area'] or o['saldo'] != 0): e.append((o['id'], 'fechada com saldo'))
    for oid in ('OS-0506', 'OS-0507'):   # fração consumida da requisição = realizado/área da O.S.
        ox = next(o for o in L.ORDENS if o['id'] == oid)
        if abs(L.REQS[oid][2] - ox['realizado'] / ox['area']) > 0.005: e.append((oid, 'fração consumida ≠ realizado/área'))
    o7 = next(o for o in L.ORDENS if o['id'] == 'OS-0507')
    if br(o7['realizado']) + ' de ' + br(o7['area']) + ' ha' not in L.COND['OS-0507']: e.append(('OS-0507', 'texto'))
    a = L.PIVOS; d = L._dose
    import quantidade as _Q
    if L._MUDA != int(round(_Q.qtd(d('MAMAO-IMP', 'i4', 'Muda de mamão Formosa'), a[11]))) or L.ESTOQUE['Muda de mamão Formosa'] < L._MUDA or L.ESTOQUE['Superfosfato simples'] < L._SFS:
        e.append(('OS-0503', 'reserva maior que o estoque apto'))
    if br(L._MUDA) + ' mudas' not in L.COND['OS-0503'] or br(a[13]) + ' ha' not in L.ORIG['OS-0501'][1] or br(a[12]) + ' ha' not in L.ORIG['OS-0509'][1]: e.append(('textos', 'área'))
    if not (L.ESTOQUE['Calcário dolomítico filler'] < L._CALC <= L.ESTOQUE['Calcário dolomítico filler'] + L.RECEB['Calcário dolomítico filler']): e.append(('OS-0502', 'cenário falta+pedido'))
    return e
def com_areas(fator):
    import importlib.util, types
    salvo = sys.modules['dados_lagoa_fonte']
    sys.modules['dados_lagoa_fonte'] = types.SimpleNamespace(PIVOS_HA={n: round(v * fator, 2) for n, v in F.PIVOS_HA.items()})
    try:
        sp = importlib.util.spec_from_file_location(f'dls_{fator}', os.path.join(GEN, 'dados_lagoa_safra.py')); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
    finally: sys.modules['dados_lagoa_fonte'] = salvo
e0, e1 = invariantes(DLS), invariantes(com_areas(1.13))
chk('14 SINT-C02: realizado ≤ área, saldo = área − realizado, apontamentos = realizado, fechadas 100 %, fração/texto/reserva/estoque/calcário coerentes — com a área sintética e com áreas ×1,13',
    not e0 and not e1, [e0[:4], e1[:4]])

# PRE-REV-20261004 · P5/P6: o que outras sementes dizem de uma O.S. da Lagoa vem da própria O.S.
import dados_irrigacao as DI, dados_mip as DM
_O = {o['id']: o for o in DLS.ORDENS}
fb = {k: (DI.FERT[k]['base'], _O[k]['realizado']) for k in DI.FERT if k in _O}
dm = [(v['id'], v['dec']['os'], v['dec']['area'], _O[v['dec']['os']]['area'], DM.TAL[v['tal']]['area']) for v in DM.VIS
      if v.get('dec') and v['dec'].get('os') in _O and v['dec'].get('area') is not None]
chk('15 PRE-REV P5/P6: base das fertirrigações = realizado semeado da O.S.; área das decisões do MIP ligadas = área da O.S. e ≤ área do talhão',
    len(fb) >= 2 and all(a == b for a, b in fb.values()) and len(dm) >= 2 and all(a == b and a <= t + 1e-9 for _, _, a, b, t in dm),
    [fb, [(x[0], x[1]) for x in dm if not (x[2] == x[3] and x[2] <= x[4] + 1e-9)]])
# PRE-REV P4: semente mudou → versão nova; o estado salvo com a versão anterior é descartado (cenário da O.S., irrigação e MIP)
import json as _json, subprocess as _sp, tempfile as _tf, cenario as _CEN
_JS = r"""
const __LS={};globalThis.localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v)},removeItem:k=>{delete __LS[k]}};
""" + _CEN.js_prefixo() + DM.js_prefixo() + DI.js_prefixo() + r"""
(()=>{ const velho=(o,k)=>{ const x=JSON.parse(JSON.stringify(o)); x.v=o.v-1; x.MARCA=1; localStorage.setItem(k,JSON.stringify(x)); };
velho(CEN0,CEN_KEY); velho(MIP0,MIP_KEY); velho(IRR0,IRR_KEY); CEN_MEM=null; MIP_MEM=null; irrReset&&0;
console.log(JSON.stringify({cen:[CEN0.v,!cenGet().MARCA],mip:[MIP0.v,!mipGet().MARCA],irr:[IRR0.v,!irrGet().MARCA]})); })();
"""
_f = _tf.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); _f.write(_JS); _f.close()
_p = _sp.run(['node', _f.name], capture_output=True, text=True, timeout=120); os.unlink(_f.name)
try: _r = _json.loads(_p.stdout.strip().splitlines()[-1])
except Exception: _r = {'erro': _p.stderr[-600:]}
chk('16 PRE-REV P4: versões cenário 3, MIP 2, irrigação 2; o estado salvo com a versão anterior é descartado nas três bases',
    _r.get('cen') == [3, True] and _r.get('mip') == [2, True] and _r.get('irr') == [2, True], _r)
# verificação SAF-C02: o montar_render dizia "dados reais locais: 5/5" com a camada sintética; o rótulo sai de F.REAL (ENG-017)
import glob as _glob
if _glob.glob(os.path.join(GEN, 'project', '*.dc.html')):
    _m = _sp.run([sys.executable, os.path.join(GEN, 'montar_render.py')], capture_output=True, text=True, timeout=300, env=dict(os.environ, SAFRION_DADOS='sintetico'))
    chk('17 montar_render com a camada sintética: "dados da Lagoa Grande: sintéticos", nunca "reais"',
        _m.returncode == 0 and 'dados da Lagoa Grande: sintéticos ' in _m.stdout and 'reais' not in _m.stdout, [_m.returncode, _m.stdout[-300:], _m.stderr[-300:]])
else:
    print('PULADO 17 montar_render: sem project/*.dc.html (rode python3 build.py antes)', flush=True)
print(f'RESULTADO: {sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
