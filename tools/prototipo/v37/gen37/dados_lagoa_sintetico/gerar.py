# -*- coding: utf-8 -*-
"""Gerador determinístico da demonstração sintética (CAMADA-SINTETICA-01). Escreve em saida/ os arquivos de specs/esquema_lagoa.md:
lagoa_s2_resumo.json, lagoa_s2.json, lagoa_pivos.geojson, lagoa_cadastro.json, lagoa_rgb.json, lagoa_analise.json, cenas.json e os PNG
(índice e cor natural das cenas 10/09 e 25/09), em Python puro (zlib, sem PIL).

Narrativa dos índices = fase de cada pivô na data da cena, lida das datas de plantio de dados_lagoa_safra._C (fonte única, lida por ast
para não importar o módulo): produção (NDVI alto), formação, plantio recente, preparo (solo exposto) e a renovação do Pivô 12
(lavoura velha na cena de 10/09, solo exposto na de 25/09). Os números são de demonstração: não medem lavoura nem servem de recomendação.

Uso: python3 -m dados_lagoa_sintetico.gerar [--verificar]   (de gen37/; --verificar só confere o carimbo e os hashes, exit 1 se desatualizado)
dados_lagoa_fonte chama garantir() sozinho fora do Mac: a saída falta ou está velha → gera de novo, sempre igual byte a byte."""
import ast, base64, datetime as dt, hashlib, json, math, os, random, struct, sys, zlib

if __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); __package__ = 'dados_lagoa_sintetico'
from . import kml as K
from . import ROTULO

VERSAO = 'camada-sintetica-01/3'
HERE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.dirname(HERE)
SAIDA = os.path.join(HERE, 'saida')
IDX = ['NDVI', 'NDRE', 'EVI', 'SAVI', 'NDMI']
CENAS = [('2026-09-10', '13:16', 3.1), ('2026-09-25', '13:16', 0.4)]     # data, hora UTC, nuvem da cena (%); gerada em ordem cronológica,
# gravada da mais recente para a mais antiga (a primeira é a cena padrão do mapa, como no esquema: 25/09 antes de 10/09)
PX = 10.0                                    # lado do pixel (m), como o Sentinel-2 de 10 m
MARGEM, MARGEM_RGB = 200.0, 1500.0           # metros além da grade de pivôs (índices · cor natural)
NUVEM = dict(cena='2026-09-10', x=4.5 * K.PASSO + 300, y=3.5 * K.PASSO - 200, r=430.0)   # nuvem fictícia parcial na cena de 10/09
LAGOA = dict(x=6 * K.PASSO + 750, y=2 * K.PASSO, rx=520.0, ry=310.0)                    # lagoa fictícia (só na cor natural)
MANCHA = dict(pid='PV06', dx=-140.0, dy=90.0, r=120.0, queda=0.20)                         # reboleira fictícia num pivô em produção
FASES = [('preparo · solo exposto', -1.0, 0.25), ('plantio recente', 0.25, 0.40), ('formação', 0.40, 0.60),
         ('início da produção', 0.60, 0.72), ('produção', 0.72, 1.0)]

# ---------------------------------------------------------------- narrativa (fonte única: dados_lagoa_safra)
def _literais_safra():
    src = open(os.path.join(GEN, 'dados_lagoa_safra.py'), encoding='utf-8').read(); out = {}
    for no in ast.parse(src).body:
        if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name) and no.targets[0].id in ('_C', 'RENOVACAO'):
            out[no.targets[0].id] = ast.literal_eval(no.value)
    return out['_C'], out['RENOVACAO'], hashlib.sha256(repr((out['_C'], out['RENOVACAO'])).encode()).hexdigest()

def ndvi_base(n, plantio, renov, data):
    """NDVI médio do pivô n na data da cena, pela fase (mesmos cortes de idade do mapa: 90, 240 e 300 dias)."""
    if n in renov:   # renovação: lavoura velha até a erradicação (12–13/09), depois solo exposto
        return (0.66, 'produção · lavoura velha') if data < dt.date(2026, 9, 12) else (0.14, 'renovação · solo exposto')
    if plantio is None: return 0.15, 'preparo · solo exposto'
    dias = (data - plantio).days
    if dias < 0: return 0.16, 'preparo · solo exposto'
    if dias < 30: return 0.26, 'plantio recente'
    if dias < 90: return 0.38, 'formação inicial'
    if dias < 240: return 0.57, 'formação · pré-florada'
    if dias < 300: return 0.69, 'início da produção'
    return 0.79, 'produção'

def derivados(v):
    """os outros quatro índices a partir do NDVI do pixel (relações lineares de demonstração, dentro das faixas do mapa)."""
    return [v, 0.52 * v - 0.04, 0.72 * v - 0.04, 0.80 * v - 0.03, 0.62 * v - 0.14]

def quant(v): return max(0, min(254, int(round((v + 1) * 125))))    # o cliente faz q/125 − 1; 255 = sem dado (nuvem)
def deq(q): return q / 125 - 1

# ---------------------------------------------------------------- geometria
def m_de_ll(lon, lat): return (lon - K.LON0) * K.KX, (K.LAT0 - lat) * K.KY
def _pivos():
    out = []
    for pid, nome, ha, lon, lat, r in K.LG_PIVOS:
        x, y = m_de_ll(lon, lat); out.append(dict(id=pid, n=int(pid[2:]), nome=nome, ha=ha, lon=lon, lat=lat, r=r, x=x, y=y))
    return out
def _grade(margem):
    x0, y0 = -margem, -margem; x1, y1 = 6 * K.PASSO + margem, 4 * K.PASSO + margem
    W, H = int(round((x1 - x0) / PX)), int(round((y1 - y0) / PX))
    c = [K.ll_de_m(x0, y0), K.ll_de_m(x0 + W * PX, y0), K.ll_de_m(x0 + W * PX, y0 + H * PX), K.ll_de_m(x0, y0 + H * PX)]
    return x0, y0, W, H, [[round(a, 7), round(b, 7)] for a, b in c]
def circulo(lon, lat, r, n=72):
    k = math.cos(math.radians(lat)); out = []
    for i in range(n):
        a = 2 * math.pi * i / n; out.append([round(lon + r * math.sin(a) / (111320 * k), 7), round(lat + r * math.cos(a) / 110540, 7)])
    return out + [out[0][:]]

# ---------------------------------------------------------------- campo de valores por pixel
class Ruido:
    """ruído suave determinístico (soma de ondas com fase sorteada) + granulação por pixel."""
    def __init__(self, sem):
        r = random.Random(sem)   # ondas de 150–420 m (manchas de solo, lâmina e vigor dentro do pivô) + uma longa (gradiente da fazenda)
        # cada onda em direção sorteada (sem padrão xadrez): (frequência rad/m, cos θ, sen θ, fase)
        self.o = [(f, math.cos(t), math.sin(t), r.uniform(0, 2 * math.pi)) for f, t in
                  [(r.uniform(0.015, 0.042), r.uniform(0, math.pi)) for _ in range(6)] + [(0.0015, r.uniform(0, math.pi))]]
        self.r = random.Random(sem + 7)
    def __call__(self, x, y, amp):
        s = sum(math.sin(f * (x * c + y * n) + a) for f, c, n, a in self.o) / 2.6
        return amp * s + self.r.gauss(0, amp * 0.12)

def _nuvem(data, x, y):
    return data.isoformat() == NUVEM['cena'] and (x - NUVEM['x']) ** 2 + (y - NUVEM['y']) ** 2 <= NUVEM['r'] ** 2

def _cena(c_i, data, pivos, plantio, renov, x0, y0, W, H):
    """pixels dentro dos pivôs: (linha, coluna), dono e NDVI; e o NDVI-base/fase de cada pivô."""
    rz = Ruido(K.SEMENTE + 100 + c_i); pix, dono, vals, base = [], [], [], {}
    for k, p in enumerate(pivos):
        b, fase = ndvi_base(p['n'], plantio.get(p['n']), renov, data); base[p['id']] = (b, fase)
        amp = 0.03 if b < 0.3 else 0.045
        c0, c1 = int((p['x'] - p['r'] - x0) // PX), int((p['x'] + p['r'] - x0) // PX) + 1
        r0, r1 = int((p['y'] - p['r'] - y0) // PX), int((p['y'] + p['r'] - y0) // PX) + 1
        for row in range(max(0, r0), min(H, r1 + 1)):
            for col in range(max(0, c0), min(W, c1 + 1)):
                x, y = x0 + (col + 0.5) * PX, y0 + (row + 0.5) * PX; d = math.hypot(x - p['x'], y - p['y'])
                if d > p['r']: continue
                v = b + rz(x, y, amp) - (0.05 if (b > 0.3 and d > 0.92 * p['r']) else 0.0)
                m = MANCHA
                if p['id'] == m['pid'] and b > 0.6 and math.hypot(x - p['x'] - m['dx'], y - p['y'] - m['dy']) <= m['r']: v -= m['queda']
                pix.append((row, col)); dono.append(k); vals.append(None if _nuvem(data, x, y) else v)
    return pix, dono, vals, base

def _estat(vs):
    vs = sorted(vs); n = len(vs)
    if not n: return None
    q = lambda f: vs[min(n - 1, int(round(f * (n - 1))))]
    return dict(med=round(q(0.5), 3), p10=round(q(0.1), 3), p90=round(q(0.9), 3), n=n)

# ---------------------------------------------------------------- PNG em Python puro
def png(W, H, linhas, cor_tipo):
    """linhas: bytes por linha já no formato (RGB = 3 bytes/pixel, RGBA = 4)."""
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    raw = b''.join(b'\x00' + l for l in linhas)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, cor_tipo, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 9)) + ch(b'IEND', b'')

PAL_NDVI = [(.30, (0xE4, 0x00, 0x2B)), (.45, (0xFF, 0x6A, 0x00)), (.60, (0xFF, 0xD5, 0x00)), (.72, (0xB5, 0xE6, 0x1D)), (.82, (0x3F, 0xBF, 0x2A)), (9, (0x0B, 0x7A, 0x1E))]
def cor_ndvi(v): return next(c for lim, c in PAL_NDVI if v < lim)
def _mix(a, b, t): t = max(0.0, min(1.0, t)); return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))

def png_indice(W, H, pix, vals):
    img = [bytearray(4 * W) for _ in range(H)]
    for (row, col), v in zip(pix, vals):
        c = (236, 239, 236) if v is None else cor_ndvi(v); img[row][4 * col:4 * col + 4] = bytes(c + (235,))
    return png(W, H, [bytes(l) for l in img], 6)

def png_rgb(data, pivos, nd_px, xg, yg):
    x0, y0, W, H, _ = _grade(MARGEM_RGB); rz = Ruido(K.SEMENTE + 300); img = []
    solo, verde, campo = (164, 132, 98), (38, 92, 42), (150, 142, 98)
    for row in range(H):
        l = bytearray(3 * W); y = y0 + (row + 0.5) * PX
        for col in range(W):
            x = x0 + (col + 0.5) * PX
            c = _mix(campo, (120, 128, 84), 0.5 + rz(x, y, 0.35))
            if y % K.PASSO < 10 or x % K.PASSO < 10: c = (196, 178, 146)          # estradas fictícias da grade (1 pixel)
            if ((x - LAGOA['x']) / LAGOA['rx']) ** 2 + ((y - LAGOA['y']) / LAGOA['ry']) ** 2 <= 1: c = (46, 78, 92)
            gc, gr = int((x - xg) // PX), int((y - yg) // PX)
            v = nd_px.get((gr, gc))
            if v is not None: c = _mix(solo, verde, (v - 0.12) / 0.72)
            if _nuvem(data, x, y): c = _mix(c, (246, 246, 248), 0.85)
            l[3 * col:3 * col + 3] = bytes(c)
        img.append(bytes(l))
    return png(W, H, img, 2), W, H

# ---------------------------------------------------------------- arquivos
def _b64(b): return base64.b64encode(b).decode('ascii')
def _dump(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

def gerar(destino=SAIDA):
    C, renov, _ = _literais_safra()
    plantio = {n: dt.date(*map(int, d.split('-'))) for n, _, d, _ in C}
    pivos = _pivos(); x0, y0, W, H, cantos = _grade(MARGEM); xr, yr, Wr, Hr, cantos_rgb = _grade(MARGEM_RGB)
    pv_json = [dict(id=p['id'], rot=f"P{p['n']}", nome=p['nome'], ha=p['ha'], lon=p['lon'], lat=p['lat'], r_m=p['r']) for p in pivos]
    arq = {}; cen_res, cen_s2, cen_meta, analise, rgbj = [], [], {}, {}, {}
    pix_ref = dono_ref = None; anterior = None
    for c_i, (dts, hora, nuv) in enumerate(CENAS):
        data = dt.date(*map(int, dts.split('-'))); d8 = dts.replace('-', ''); cid = f'SINTETICO-S2-{d8}'
        pix, dono, vals, base = _cena(c_i, data, pivos, plantio, renov, x0, y0, W, H)
        assert pix_ref is None or pix == pix_ref, 'a grade de pixels dos pivôs muda entre cenas'
        pix_ref, dono_ref = pix, dono
        q = {n: bytearray() for n in IDX}; por = {p['id']: {n: [] for n in IDX} for p in pivos}; nuvem_p = {p['id']: [0, 0] for p in pivos}
        for (rc, k, v) in zip(pix, dono, vals):
            pid = pivos[k]['id']; nuvem_p[pid][1] += 1
            if v is None:
                nuvem_p[pid][0] += 1
                for n in IDX: q[n].append(255)
                continue
            for n, x in zip(IDX, derivados(v)):
                qq = quant(x); q[n].append(qq); por[pid][n].append(deq(qq))
        est = {}
        for p in pivos:
            e = {n: _estat(por[p['id']][n]) for n in IDX}; e['nuvem'] = round(100 * nuvem_p[p['id']][0] / nuvem_p[p['id']][1], 1); est[p['id']] = e
        pngn = f'lagoa_{d8}.png'; arq[pngn] = png_indice(W, H, pix, vals)
        nd_px = {rc: v for rc, v in zip(pix, vals) if v is not None}
        # cor natural numa grade maior: desloca a posição do pixel da grade de índices
        b, Wr2, Hr2 = png_rgb(data, pivos, nd_px, x0, y0); assert (Wr2, Hr2) == (Wr, Hr)
        arq[f'lagoa_rgb_{d8}.png'] = b; rgbj[f'lagoa_rgb_{d8}.png'] = dict(H=Hr, W=Wr, cantos=cantos_rgb, seg=0.0)
        cen_res.append(dict(id=cid, dt=dts, hora_utc=hora, nuvem=nuv, png=pngn, est=est))
        cen_s2.append(dict(id=cid, dt=dts, nuvem=nuv, png=pngn, q={n: _b64(bytes(q[n])) for n in IDX}, est=est))
        cen_meta[cid] = dict(crs='local fictício (metros a partir do canto da grade · demonstração sintética)', transform=[PX, 0.0, x0, 0.0, -PX, -y0], H=H, W=W,
                             meta={b_: dict(res_m=PX, escala=0.0001, origem=ROTULO) for b_ in ('blue', 'green', 'red', 'nir', 'rededge1', 'swir16', 'scl')},
                             dt=dts, nuvem=nuv, seg=0.0)
        k_ = f'{dts[8:10]}/{dts[5:7]}'
        piv = {p['id']: dict(fase=base[p['id']][1], ndvi=est[p['id']]['NDVI']['med'] if est[p['id']]['NDVI'] else None,
                             dif=(round(est[p['id']]['NDVI']['med'] - anterior[1][p['id']]['NDVI']['med'], 3) if anterior and est[p['id']]['NDVI'] and anterior[1][p['id']]['NDVI'] else None))
               for p in pivos}
        ha_f = {}
        for p in pivos: ha_f[base[p['id']][1]] = round(ha_f.get(base[p['id']][1], 0) + p['ha'], 2)
        analise[k_] = dict(dt=dts, ant=anterior[0] if anterior else None, piv=piv, faz=dict(ha_por_fase=ha_f, rotulo=ROTULO))
        anterior = (k_, est)
    cen_res.reverse(); cen_s2.reverse(); analise = dict(reversed(list(analise.items()))); rgbj = dict(reversed(list(rgbj.items())))
    pix_b = b''.join(struct.pack('<HH', r, c) for r, c in pix_ref)
    arq['lagoa_s2_resumo.json'] = _dump(dict(pivos=pv_json, cantos=cantos, idx=IDX, H=H, W=W, cenas=cen_res))
    arq['lagoa_s2.json'] = _dump(dict(pivos=pv_json, cenas=cen_s2, idx=IDX, H=H, W=W, cantos=cantos, pix=_b64(pix_b), dono=_b64(bytes(dono_ref))))
    arq['lagoa_pivos.geojson'] = _dump(dict(type='FeatureCollection', features=[
        dict(type='Feature', properties=dict(id=p['id'], nome=p['nome'], ha=p['ha'], r_m=p['r'], rotulo=ROTULO),
             geometry=dict(type='Polygon', coordinates=[circulo(p['lon'], p['lat'], p['r'])])) for p in pivos]))
    arq['lagoa_cadastro.json'] = _dump(dict(
        fazenda='Lagoa Grande (demonstração sintética)', municipio='Lagoa Grande (demonstração)', uf='MG', fonte=K.LG_FONTE,
        pivos=[dict(id=p['id'], nome=p['nome'], area_ha=p['ha'], centro=[p['lon'], p['lat']], raio_m=p['r'], geometria='círculo fictício: centro + área')
               for p in pivos],
        perimetros=[dict(nome=n, tema=t, area_ha=None, municipio='Lagoa Grande (demonstração)', estado='MG', modulos_fiscais='38,6', recibo_car=K.LG_PERIMETROS[0]['car'])
                    for n, t in (('Imóvel (demonstração sintética)', 'Área do imóvel'), ('Gleba anexa (demonstração sintética)', 'Área do imóvel'),
                                 ('Sede (demonstração sintética)', 'Área do imóvel'))],
        ambiental=[dict(grupo=g, tema=t, area_ha=a, recibo_car=K.LG_PERIMETROS[0]['car']) for g, t, a, _ in K.LG_AMBIENTAL]
                  + [dict(grupo='Imóvel', tema='Área do imóvel (demonstração)', area_ha=K.LG_PERIMETROS[0]['area'], recibo_car=K.LG_PERIMETROS[0]['car'])],
        agua=[dict(nome=a['nome'], descricao=a['desc'], lon=a['lon'], lat=a['lat']) for a in K.LG_AGUA]))
    arq['lagoa_rgb.json'] = _dump(rgbj)
    arq['lagoa_analise.json'] = _dump(dict(
        desc={'NDVI': dict(o='vigor geral', tec='(NIR − R) / (NIR + R)', uso='falhas e manchas'),
              'NDRE': dict(o='clorofila', tec='(NIR − RE) / (NIR + RE)', uso='nutrição com dossel fechado'),
              'EVI': dict(o='vigor sem saturar', tec='2,5 (NIR − R) / (NIR + 6R − 7,5B + 1)', uso='lavoura fechada'),
              'SAVI': dict(o='vigor com solo exposto', tec='1,5 (NIR − R) / (NIR + R + 0,5)', uso='mudas e formação'),
              'NDMI': dict(o='umidade da folha', tec='(NIR − SWIR) / (NIR + SWIR)', uso='alerta de irrigação')},
        fases=[dict(nome=n, faixa=[a, b]) for n, a, b in FASES], cenas=analise))
    arq['cenas.json'] = _dump(cen_meta)
    os.makedirs(destino, exist_ok=True)
    for n, b in arq.items():
        with open(os.path.join(destino, n), 'wb') as f: f.write(b)
    car = _carimbo({n: hashlib.sha256(b).hexdigest() for n, b in arq.items()})
    with open(os.path.join(destino, '_carimbo.json'), 'w', encoding='utf-8') as f: json.dump(car, f, ensure_ascii=False, indent=1, sort_keys=True)
    return car

def _entrada():
    """hash das entradas: o gerador, as constantes e a narrativa (datas de plantio e renovação)."""
    h = hashlib.sha256()
    for f in ('gerar.py', 'kml.py', '__init__.py'): h.update(open(os.path.join(HERE, f), 'rb').read())
    h.update(_literais_safra()[2].encode()); return h.hexdigest()
def _carimbo(arqs): return dict(versao=VERSAO, rotulo=ROTULO, semente=K.SEMENTE, entrada=_entrada(), arquivos=arqs)

def em_dia(destino=SAIDA):
    try: car = json.load(open(os.path.join(destino, '_carimbo.json'), encoding='utf-8'))
    except (OSError, ValueError): return False
    if car.get('versao') != VERSAO or car.get('entrada') != _entrada(): return False
    for n, h in car.get('arquivos', {}).items():
        p = os.path.join(destino, n)
        if not os.path.exists(p) or hashlib.sha256(open(p, 'rb').read()).hexdigest() != h: return False
    return bool(car.get('arquivos'))

def garantir(destino=SAIDA):
    if not em_dia(destino): gerar(destino)

if __name__ == '__main__':
    if '--verificar' in sys.argv: ok = em_dia(); print('saida em dia' if ok else 'saida ausente ou desatualizada'); sys.exit(0 if ok else 1)
    car = gerar(); print(json.dumps(car, ensure_ascii=False, indent=1, sort_keys=True))
