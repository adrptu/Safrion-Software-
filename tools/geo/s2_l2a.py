# -*- coding: utf-8 -*-
"""Lagoa Grande real: KML do proprietário + Sentinel-2 L2A (ESA/Copernicus, catálogo Earth Search) → dados_lagoa/ e
dados_lagoa_kml.py no formato de specs/esquema_lagoa.md (o mesmo da demonstração sintética, lido por dados_lagoa_fonte).

Dado real (exceção do proprietário de 19/10/2026, só para o artefato privado): a saída fica fora de qualquer repositório git.
O script recusa gravar dentro de um worktree. Nada daqui vai para o GitHub, log versionado, fixture ou teste.

Uso: python s2_l2a.py --kml <arquivo.kml> --gen37 <cópia de gen37 fora do git> [--datas 2026-09-25,2026-09-10]
Precisa de rasterio e numpy só para processar (importados na hora); a rede só lê o catálogo público e os COG (sem conta, sem custo).
Teste sem rede e sem dado real: tools/geo/s2_l2a_test.py."""
import argparse, base64, datetime as dt, hashlib, json, math, os, re, struct, sys, urllib.request, zlib
import xml.etree.ElementTree as ET



def _geo():
    """numpy e rasterio só quando processa (o teste de regras não precisa deles)"""
    import numpy, rasterio
    from rasterio.warp import transform
    from rasterio.windows import from_bounds
    from rasterio.enums import Resampling
    return numpy, rasterio, transform, from_bounds, Resampling

STAC = 'https://earth-search.aws.element84.com/v1/search'
IDX = ['NDVI', 'NDRE', 'EVI', 'SAVI', 'NDMI']
PX = 10.0
MARGEM, MARGEM_RGB = 200.0, 1500.0
NUVEM_SCL = {3, 8, 9, 10}          # sombra de nuvem, nuvem média, nuvem alta, cirro
FASES = [('preparo · solo exposto', -1.0, 0.25), ('plantio recente', 0.25, 0.40), ('formação', 0.40, 0.60),
         ('início da produção', 0.60, 0.72), ('produção', 0.72, 1.0)]
PAL_NDVI = [(.30, (0xE4, 0x00, 0x2B)), (.45, (0xFF, 0x6A, 0x00)), (.60, (0xFF, 0xD5, 0x00)), (.72, (0xB5, 0xE6, 0x1D)), (.82, (0x3F, 0xBF, 0x2A)), (9, (0x0B, 0x7A, 0x1E))]
LG_FONTE = 'KML do proprietário (pivôs, CAR e recursos hídricos) e imagem Sentinel-2 L2A da ESA (Copernicus), catálogo Earth Search'
LG_GEO = 'Círculo pelo ponto central do KML e pela área declarada (HECTARE)'


# ---------------------------------------------------------------- segurança da saída
def fora_do_git(caminho):
    p = os.path.abspath(caminho)
    while True:
        if os.path.exists(os.path.join(p, '.git')): return False
        q = os.path.dirname(p)
        if q == p: return True
        p = q


# ---------------------------------------------------------------- KML
def _ns(t): return t.split('}')[-1]
def _txt(e, tag):
    for c in e:
        if _ns(c.tag) == tag: return (c.text or '').strip()
    return ''
def _coords(pm):
    out = []
    for x in pm.iter():
        if _ns(x.tag) == 'coordinates':
            out.append([tuple(map(float, s.split(',')[:2])) for s in (x.text or '').split()])
    return out
def _dados(pm): return {x.get('name'): (_txt(x, 'value') or (x.text or '').strip()) for x in pm.iter() if _ns(x.tag) in ('Data', 'SimpleData')}
def _desc(pm): return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', _txt(pm, 'description'))).strip()
def _f(s): return float(s.replace('.', '').replace(',', '.')) if re.search(r',\d', s) else float(s)

def area_ha(anel):
    """área geodésica aproximada (esfera de 6.378.137 m) de um anel lon/lat, em ha"""
    R = 6378137.0; s = 0.0
    for (x1, y1), (x2, y2) in zip(anel, anel[1:] + anel[:1]):
        s += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(s * R * R / 2) / 1e4

def _agua(n, nome, desc, lon, lat):
    a = dict(curso='', desc=desc, fin='', id=f'AG{n:02d}', lat=round(lat, 6), lon=round(lon, 6), modo='', nome=nome,
             num='', proc='', regime='', renov='', tipo='', vazao='', venc='')
    m = re.search(r'N°\s*(\d+)', nome)
    if m: a['num'] = m.group(1)
    if not desc: return a
    m = re.match(r'(OUTORGA ESTADUAL|CERTIDÃO DE USO INSIGNIFICANTE)\s+([\d/]+)', desc, re.I)
    if m:
        a['tipo'] = 'Outorga' if m.group(1).upper().startswith('OUTORGA') else 'Certidão de uso insignificante'; a['num'] = m.group(2)
    m = re.search(r'PROCESSO:\s*([\d/]+)', desc); a['proc'] = m.group(1) if m else ''
    m = re.search(r'Modo de Uso:\s*(.+?)\s+(?:Curso d.água:|Vazão:)', desc)
    modo = m.group(1).strip() if m else ''
    if re.match(r'Captação Direta', modo, re.I): modo = 'Captação superficial (captação direta)'
    elif re.match(r'Captação Em Barramento', modo, re.I): modo = 'Captação superficial em barramento, com regularização de vazão'
    elif modo: modo = modo[0].upper() + modo[1:].lower()
    a['modo'] = modo
    m = re.search(r'Curso d.água:\s*(.+?)\s+Vazão:', desc); a['curso'] = m.group(1).strip() if m else ''
    m = re.search(r'Vazão:\s*([\d.,]+)\s*\(?\s*(m³/h|l/s)', desc, re.I)
    if m: a['vazao'] = f"{m.group(1)} {'m³/h' if m.group(2).lower() == 'm³/h' else 'L/s'}"
    m = re.search(r'durante\s*(\d{1,2}):(\d{2})\s*horas/dia', desc)
    if m: a['regime'] = f"{int(m.group(1))} h/dia" if m.group(2) == '00' else f"{int(m.group(1))},{int(m.group(2)) * 100 // 60:02d} h/dia"
    elif re.search(r'\((Março|Janeiro)', desc): a['regime'] = 'sazonal (ver a descrição)'
    m = re.search(r'Finalid+ade:\s*(.+?)(?:\.\s*)?VENCIMENTO', desc, re.I)
    fin = (m.group(1).strip().rstrip('.') if m else '')
    a['fin'] = 'Irrigação' if fin.lower().startswith('irrigação') else fin
    m = re.search(r'VENCIMENTO:\s*(\d{2})/(\d{2})/(\d{4})', desc, re.I)
    if m: a['venc'] = f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    m = re.search(r'EM RENOVAÇÃO.*?PROCESSO TÉCNICO:\s*([\d/]+)', desc, re.I)
    if m: a['renov'] = m.group(1)
    return a

def ler_kml(caminho):
    r = ET.parse(caminho).getroot()
    pai = {c: p for p in r.iter() for c in p}
    def pasta(pm):
        p = pai.get(pm); cam = []
        while p is not None:
            if _ns(p.tag) in ('Folder', 'Document'): cam.append(_txt(p, 'name'))
            p = pai.get(p)
        return list(reversed(cam))
    pivos, circulos, perim, amb, agua = [], [], [], [], []
    vistos = set()
    for pm in r.iter():
        if _ns(pm.tag) != 'Placemark': continue
        cam, nome, desc, dd, cs = pasta(pm), _txt(pm, 'name'), _desc(pm), _dados(pm), _coords(pm)
        topo = cam[-1] if cam else ''
        if topo == 'PIVÔS':
            n = int(re.search(r'(\d+)', nome).group(1)); ha = _f(re.search(r'HECTARES?:\s*([\d.,]+)', desc).group(1))
            lon, lat = cs[0][0]; pivos.append((f'PV{n:02d}', f'Pivô {n}', round(ha, 2), round(lon, 6), round(lat, 6), round(math.sqrt(ha * 1e4 / math.pi), 2)))
        elif topo == 'POLIGONO':
            circulos.append(cs[0])
        elif 'PERÍMETRO' in cam:
            perim.append(dict(nome=nome, tema=dd.get('tema', ''), area=float(dd['area']) if dd.get('area') else round(area_ha(cs[0]), 2),
                              car=dd.get('recibo', ''), mf=float(dd['modfiscais']) if dd.get('modfiscais') else 0.0, mun=dd.get('municipio', '')))
        elif topo in ('RESERVA LEGAL', 'APP') and dd.get('tema'):
            k = (topo, dd['tema'], dd['area'])
            if k in vistos: continue
            vistos.add(k); grupo = 'Reserva legal' if topo == 'RESERVA LEGAL' else 'APP'
            amb.append((grupo, dd['tema'], round(float(dd['area']), 2), 'Total' in dd['tema']))
        elif topo.startswith('RECURSOS HIDRICOS') or (len(cam) == 1 and re.match(r'(Captação|Barragem)', nome)):
            lon, lat = cs[0][0]; agua.append((nome, desc, lon, lat))
    pivos.sort(key=lambda p: int(p[0][2:]))
    agua = [_agua(i, n, d, lo, la) for i, (n, d, lo, la) in enumerate(agua, 1)]
    car = next((p for p in perim if p['car'] and 'Líquida' not in p['tema']), None)
    temas = sorted({p['tema'] for p in perim if p['tema']} | {g for g, _, _, _ in amb})
    LG_PERIMETROS = [dict(nome='Imóvel (CAR)', area=round(car['area'], 2), car=car['car'], mf=round(car['mf'], 1), mun='Lagoa Grande/MG', temas=temas)]
    for p in perim:
        if not p['car']: LG_PERIMETROS.append(dict(nome=p['nome'].capitalize(), area=round(p['area'], 2), car='', mf=0.0, mun='Lagoa Grande/MG', temas=['Perímetro']))
    return dict(pivos=pivos, circulos=circulos, perimetros=LG_PERIMETROS, perim_kml=perim, ambiental=amb, agua=agua)


def conferir_circulos(pivos, circulos):
    """para cada pivô, o círculo desenhado mais próximo: raio médio e área (só conferência; o círculo usado vem do centro + área declarada)"""
    out = []
    for pid, _, ha, lon, lat, r in pivos:
        k = 111320 * math.cos(math.radians(lat))
        melhor = None
        for c in circulos:
            cx = sum(x for x, _ in c) / len(c); cy = sum(y for _, y in c) / len(c)
            d = math.hypot((cx - lon) * k, (cy - lat) * 110540)
            if melhor is None or d < melhor[0]:
                rm = sum(math.hypot((x - cx) * k, (y - cy) * 110540) for x, y in c) / len(c); melhor = (d, rm)
        out.append((pid, ha, round(melhor[1] ** 2 * math.pi / 1e4, 2) if melhor and melhor[0] < 150 else None))
    return out


# ---------------------------------------------------------------- catálogo e leitura
def buscar(bbox, data):
    q = json.dumps(dict(collections=['sentinel-2-l2a'], bbox=bbox, datetime=f'{data}T00:00:00Z/{data}T23:59:59Z', limit=10)).encode()
    req = urllib.request.Request(STAC, data=q, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as f: fs = json.load(f)['features']
    if not fs: raise SystemExit(f'sem cena Sentinel-2 L2A em {data}')
    return min(fs, key=lambda f: f['properties'].get('eo:cloud_cover', 100))

def ler(href, b, H, W):
    _, rasterio, _, from_bounds, Resampling = _geo()
    with rasterio.open('/vsicurl/' + href) as s:
        a = s.read(1, window=from_bounds(*b, transform=s.transform), out_shape=(H, W), resampling=Resampling.nearest, boundless=True, fill_value=0)
    return a

def refl(dn, banda, ja_aplicado):
    """reflectância de superfície. Com 'earthsearch:boa_offset_applied' verdadeiro o catálogo já descontou o deslocamento de −0,1
    (linha de base ≥ 04.00): descontar de novo deixa o vermelho negativo na vegetação densa e satura o NDVI em 1 (conferido em 19/10:
    B04 bruto p5 = 296 sobre os pivôs, isto é, 0,03 de reflectância)."""
    rb = banda.get('raster:bands', [{}])[0]; e, o = rb.get('scale', 1e-4), (0.0 if ja_aplicado else rb.get('offset', 0.0))
    r = dn.astype('float64') * e + o; r[dn == 0] = float('nan'); return r


# ---------------------------------------------------------------- formato (o mesmo de dados_lagoa_sintetico.gerar)
def quant(v): return max(0, min(254, int(round((v + 1) * 125))))
def deq(q): return q / 125 - 1
def _estat(vs):
    vs = sorted(vs); n = len(vs)
    if not n: return None
    q = lambda f: vs[min(n - 1, int(round(f * (n - 1))))]
    return dict(med=round(q(0.5), 3), p10=round(q(0.1), 3), p90=round(q(0.9), 3), n=n)
def png(W, H, linhas, cor_tipo):
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    raw = b''.join(b'\x00' + l for l in linhas)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, cor_tipo, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 9)) + ch(b'IEND', b'')
def cor_ndvi(v): return next(c for lim, c in PAL_NDVI if v < lim)
def circulo(lon, lat, r, n=72):
    k = math.cos(math.radians(lat)); out = []
    for i in range(n):
        a = 2 * math.pi * i / n; out.append([round(lon + r * math.sin(a) / (111320 * k), 7), round(lat + r * math.cos(a) / 110540, 7)])
    return out + [out[0][:]]
def _b64(b): return base64.b64encode(b).decode('ascii')
def _dump(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
def fase_de(v):
    if v is None: return 'sem leitura (nuvem)'
    return next(n for n, a, b in FASES if a <= v < b or (b == 1.0 and v >= 1.0))


def grade(cx, cy, rs, margem):
    x0 = math.floor((min(x - r for x, r in zip(cx, rs)) - margem) / PX) * PX; x1 = math.ceil((max(x + r for x, r in zip(cx, rs)) + margem) / PX) * PX
    y1 = math.ceil((max(y + r for y, r in zip(cy, rs)) + margem) / PX) * PX; y0 = math.floor((min(y - r for y, r in zip(cy, rs)) - margem) / PX) * PX
    return x0, y0, x1, y1, int(round((x1 - x0) / PX)), int(round((y1 - y0) / PX))

def cantos(crs, x0, y0, x1, y1):
    rtransform = _geo()[2]
    xs, ys = rtransform(crs, 'EPSG:4326', [x0, x1, x1, x0], [y1, y1, y0, y0])
    return [[round(a, 7), round(b, 7)] for a, b in zip(xs, ys)]


def processar(kml, gen37, datas):
    dest = os.path.join(gen37, 'dados_lagoa')
    if not fora_do_git(gen37): raise SystemExit('recusado: a saída é dado real e não pode ficar dentro de um repositório git')
    np, rasterio, rtransform, from_bounds, Resampling = _geo()
    K = ler_kml(kml); pivos = K['pivos']
    conf = conferir_circulos(pivos, K['circulos'])
    lon = [p[3] for p in pivos]; lat = [p[4] for p in pivos]
    bbox = [min(lon) - 0.03, min(lat) - 0.03, max(lon) + 0.03, max(lat) + 0.03]
    itens = [buscar(bbox, d) for d in datas]                      # a primeira é a cena padrão do mapa (mais recente)
    crs = 'EPSG:%d' % itens[0]['properties']['proj:epsg']
    cx, cy = rtransform('EPSG:4326', crs, lon, lat)
    rs = [p[5] for p in pivos]
    x0, y0, x1, y1, W, H = grade(cx, cy, rs, MARGEM); xr0, yr0, xr1, yr1, Wr, Hr = grade(cx, cy, rs, MARGEM_RGB)
    cant, cant_rgb = cantos(crs, x0, y0, x1, y1), cantos(crs, xr0, yr0, xr1, yr1)
    # pixels de cada pivô (centro do pixel dentro do círculo), em ordem de pivô, linha e coluna
    pix, dono = [], []
    for k, (px, py, r) in enumerate(zip(cx, cy, rs)):
        c0, c1 = int((px - r - x0) // PX), int((px + r - x0) // PX) + 1
        r0, r1 = int((y1 - (py + r)) // PX), int((y1 - (py - r)) // PX) + 1
        for row in range(max(0, r0), min(H, r1 + 1)):
            for col in range(max(0, c0), min(W, c1 + 1)):
                x, y = x0 + (col + 0.5) * PX, y1 - (row + 0.5) * PX
                if math.hypot(x - px, y - py) <= r: pix.append((row, col)); dono.append(k)
    pv_json = [dict(id=p[0], rot=f"P{int(p[0][2:])}", nome=p[1], ha=p[2], lon=p[3], lat=p[4], r_m=p[5]) for p in pivos]
    arq, cen_res, cen_s2, cen_meta, analise, rgbj, anterior = {}, [], [], {}, {}, {}, None
    for it in reversed(itens):                                   # cronológica; gravada da mais recente para a mais antiga
        pr, A = it['properties'], it['assets']; dts = pr['datetime'][:10]; d8 = dts.replace('-', ''); hora = pr['datetime'][11:16]
        b = (x0, y0, x1, y1)
        oa = bool(pr.get('earthsearch:boa_offset_applied'))
        B = {n: refl(ler(A[n]['href'], b, H, W), A[n], oa) for n in ('blue', 'green', 'red', 'nir', 'rededge1', 'swir16')}
        scl = ler(A['scl']['href'], b, H, W)
        bl, rd, ni, re_, sw = B['blue'], B['red'], B['nir'], B['rededge1'], B['swir16']
        with np.errstate(divide='ignore', invalid='ignore'):
            ind = dict(NDVI=(ni - rd) / (ni + rd), NDRE=(ni - re_) / (ni + re_), EVI=2.5 * (ni - rd) / (ni + 6 * rd - 7.5 * bl + 1),
                       SAVI=1.5 * (ni - rd) / (ni + rd + 0.5), NDMI=(ni - sw) / (ni + sw))
        nuv = np.isin(scl, list(NUVEM_SCL)) | (scl == 0) | np.isnan(ni)
        q = {n: bytearray() for n in IDX}; por = {p[0]: {n: [] for n in IDX} for p in pivos}; nuvem_p = {p[0]: [0, 0] for p in pivos}
        vnd = {}
        for (row, col), k in zip(pix, dono):
            pid = pivos[k][0]; nuvem_p[pid][1] += 1
            if nuv[row, col] or not all(np.isfinite(ind[n][row, col]) for n in IDX):
                nuvem_p[pid][0] += 1
                for n in IDX: q[n].append(255)
                continue
            for n in IDX:
                v = float(max(-1.0, min(1.0, ind[n][row, col]))); qq = quant(v); q[n].append(qq); por[pid][n].append(deq(qq))
            vnd[(row, col)] = float(max(-1.0, min(1.0, ind['NDVI'][row, col])))
        est = {}
        for p in pivos:
            e = {n: _estat(por[p[0]][n]) for n in IDX}; e['nuvem'] = round(100 * nuvem_p[p[0]][0] / max(1, nuvem_p[p[0]][1]), 1); est[p[0]] = e
        nuvem_faz = round(100 * sum(v[0] for v in nuvem_p.values()) / max(1, sum(v[1] for v in nuvem_p.values())), 1)
        img = [bytearray(4 * W) for _ in range(H)]
        for (row, col), k in zip(pix, dono):
            v = vnd.get((row, col)); c = (236, 239, 236) if v is None else cor_ndvi(v); img[row][4 * col:4 * col + 4] = bytes(c + (235,))
        pngn = f'lagoa_{d8}.png'; arq[pngn] = png(W, H, [bytes(l) for l in img], 6)
        tci = []
        with rasterio.open('/vsicurl/' + A['visual']['href']) as s:
            t = s.read(window=from_bounds(xr0, yr0, xr1, yr1, transform=s.transform), out_shape=(3, Hr, Wr), resampling=Resampling.bilinear, boundless=True, fill_value=0)
        rgb = np.ascontiguousarray(np.transpose(t, (1, 2, 0)).astype('uint8'))
        arq[f'lagoa_rgb_{d8}.png'] = png(Wr, Hr, [rgb[i].tobytes() for i in range(Hr)], 2)
        rgbj[f'lagoa_rgb_{d8}.png'] = dict(H=Hr, W=Wr, cantos=cant_rgb, seg=0.0)
        cen_res.append(dict(id=it['id'], dt=dts, hora_utc=hora, nuvem=nuvem_faz, png=pngn, est=est))
        cen_s2.append(dict(id=it['id'], dt=dts, nuvem=nuvem_faz, png=pngn, q={n: _b64(bytes(q[n])) for n in IDX}, est=est))
        cen_meta[it['id']] = dict(crs=crs, transform=[PX, 0.0, x0, 0.0, -PX, y1], H=H, W=W,
                                  meta={n: dict(res_m=float(A[n].get('gsd') or A[n].get('raster:bands', [{}])[0].get('spatial_resolution', 10)),
                                                escala=A[n].get('raster:bands', [{}])[0].get('scale', 1), origem='Earth Search · ' + it['id'])
                                        for n in ('blue', 'green', 'red', 'nir', 'rededge1', 'swir16', 'scl')},
                                  dt=dts, nuvem=nuvem_faz, seg=0.0)
        k_ = f'{dts[8:10]}/{dts[5:7]}'
        piv = {p[0]: dict(fase=fase_de(est[p[0]]['NDVI']['med'] if est[p[0]]['NDVI'] else None), ndvi=est[p[0]]['NDVI']['med'] if est[p[0]]['NDVI'] else None,
                          dif=(round(est[p[0]]['NDVI']['med'] - anterior[1][p[0]]['NDVI']['med'], 3) if anterior and est[p[0]]['NDVI'] and anterior[1][p[0]]['NDVI'] else None))
               for p in pivos}
        ha_f = {}
        for p in pivos: f_ = piv[p[0]]['fase']; ha_f[f_] = round(ha_f.get(f_, 0) + p[2], 2)
        analise[k_] = dict(dt=dts, ant=anterior[0] if anterior else None, piv=piv, faz=dict(ha_por_fase=ha_f, rotulo=''))
        anterior = (k_, est)
    cen_res.reverse(); cen_s2.reverse(); analise = dict(reversed(list(analise.items()))); rgbj = dict(reversed(list(rgbj.items())))
    pix_b = b''.join(struct.pack('<HH', r_, c_) for r_, c_ in pix)
    arq['lagoa_s2_resumo.json'] = _dump(dict(pivos=pv_json, cantos=cant, idx=IDX, H=H, W=W, cenas=cen_res))
    arq['lagoa_s2.json'] = _dump(dict(pivos=pv_json, cenas=cen_s2, idx=IDX, H=H, W=W, cantos=cant, pix=_b64(pix_b), dono=_b64(bytes(dono))))
    arq['lagoa_pivos.geojson'] = _dump(dict(type='FeatureCollection', features=[
        dict(type='Feature', properties=dict(id=p[0], nome=p[1], ha=p[2], r_m=p[5], rotulo=''), geometry=dict(type='Polygon', coordinates=[circulo(p[3], p[4], p[5])])) for p in pivos]))
    P0 = K['perimetros'][0]
    arq['lagoa_cadastro.json'] = _dump(dict(
        fazenda='Lagoa Grande', municipio='Lagoa Grande', uf='MG', fonte=LG_FONTE,
        pivos=[dict(id=p[0], nome=p[1], area_ha=p[2], centro=[p[3], p[4]], raio_m=p[5], geometria='círculo: centro do KML + área declarada') for p in pivos],
        perimetros=[dict(nome=p['nome'] or 'Perímetro', tema=p['tema'] or 'Perímetro', area_ha=round(p['area'], 2), municipio='Lagoa Grande', estado='MG',
                         modulos_fiscais=(f"{p['mf']:.1f}".replace('.', ',') if p['mf'] else ''), recibo_car=p['car']) for p in K['perim_kml']],
        ambiental=[dict(grupo=g, tema=t, area_ha=a, recibo_car=P0['car']) for g, t, a, _ in K['ambiental']]
                  + [dict(grupo='Imóvel', tema='Área do imóvel (CAR)', area_ha=P0['area'], recibo_car=P0['car'])],
        agua=[dict(nome=a['nome'], descricao=a['desc'], lon=a['lon'], lat=a['lat']) for a in K['agua']]))
    arq['lagoa_rgb.json'] = _dump(rgbj)
    arq['lagoa_analise.json'] = _dump(dict(
        desc={'NDVI': dict(o='vigor geral', tec='(NIR − R) / (NIR + R)', uso='falhas e manchas'),
              'NDRE': dict(o='clorofila', tec='(NIR − RE) / (NIR + RE)', uso='nutrição com dossel fechado'),
              'EVI': dict(o='vigor sem saturar', tec='2,5 (NIR − R) / (NIR + 6R − 7,5B + 1)', uso='lavoura fechada'),
              'SAVI': dict(o='vigor com solo exposto', tec='1,5 (NIR − R) / (NIR + R + 0,5)', uso='mudas e formação'),
              'NDMI': dict(o='umidade da folha', tec='(NIR − SWIR) / (NIR + SWIR)', uso='alerta de irrigação')},
        fases=[dict(nome=n, faixa=[a, b]) for n, a, b in FASES], cenas=analise))
    arq['cenas.json'] = _dump(cen_meta)
    os.makedirs(dest, exist_ok=True)
    for n, b_ in arq.items():
        with open(os.path.join(dest, n), 'wb') as f: f.write(b_)
    with open(os.path.join(gen37, 'dados_lagoa_kml.py'), 'w', encoding='utf-8') as f:
        f.write('# -*- coding: utf-8 -*-\n"""Lagoa Grande real (gerado por lagoa_real.py a partir do KML do proprietário). Dado real: fora do git."""\n')
        for n, v in (('LG_FONTE', LG_FONTE), ('LG_GEO', LG_GEO), ('LG_PIVOS', pivos), ('LG_PERIMETROS', K['perimetros']),
                     ('LG_AMBIENTAL', K['ambiental']), ('LG_AGUA', K['agua'])):
            f.write(f'{n} = {v!r}\n')
    return dict(pivos=len(pivos), ha=round(sum(p[2] for p in pivos), 2), agua=len(K['agua']), ambiental=len(K['ambiental']), perimetros=len(K['perimetros']),
                H=H, W=W, Hr=Hr, Wr=Wr, pixels=len(pix), cenas=[(c['id'], c['dt'], c['nuvem']) for c in cen_res],
                conferencia_circulos=conf, arquivos={n: hashlib.sha256(b_).hexdigest()[:16] for n, b_ in sorted(arq.items())})


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--kml', required=True); ap.add_argument('--gen37', required=True)
    ap.add_argument('--datas', default='2026-09-25,2026-09-10'); a = ap.parse_args()
    print(json.dumps(processar(a.kml, a.gen37, a.datas.split(',')), ensure_ascii=False, indent=1))
