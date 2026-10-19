# -*- coding: utf-8 -*-
"""Geometria dos talhões, fonte única do Mapa (IN-04) e do Planejar safra em mapa (SAF-MAPA, proprietário, 18/10/2026: "Em planejar safra
coloque o modo de visão mapa para ver geograficamente como está o plano da safra e permita clicar nos talhões e fazer todo o trabalho").

- Santa Rita: polígonos e círculos no plano do desenho de 1000 × 620 (o mesmo do IN-04, que importa GEO daqui).
- Lagoa Grande: os contornos dos pivôs do arquivo da fazenda (lagoa_pivos.geojson; sintético fora do Mac), em lon/lat, levados ao plano por
  projeção equirretangular local (x = Δlon·cos φ0, y = −Δlat), com a mesma escala nos dois eixos.
- Talhão sem contorno (B1 da Boa Vista, talhão novo do cadastro) não entra aqui: a tela o mostra na faixa "Sem contorno no mapa"."""
import json, math, os

# Santa Rita (IN-04): id, tipo, geometria no plano 1000 × 620
GEO_SR = [('T1', 'poly', '30,30 300,22 312,282 40,292'), ('T2', 'poly', '326,22 580,28 574,280 332,286'),
          ('P1', 'circ', '700,158,104'), ('P2', 'circ', '902,158,92'),
          ('T4', 'poly', '40,344 306,336 312,598 46,606'), ('T3', 'poly', '328,338 572,334 578,596 334,600'),
          ('T7', 'poly', '598,344 782,338 788,598 604,602'), ('C1', 'poly', '804,338 976,334 982,596 810,600')]
LARG = 1000   # largura do plano; a altura segue a forma da fazenda


def _poly(txt):
    return [tuple(map(float, p.split(','))) for p in txt.split()]


def _centro(pts):
    """centróide do polígono (área com sinal); para o rótulo no meio do talhão"""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        k = x0 * y1 - x1 * y0; a += k; cx += (x0 + x1) * k; cy += (y0 + y1) * k
    if abs(a) < 1e-9:
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return cx / (3 * a), cy / (3 * a)


def _d(pts):
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'


def _sr():
    out = {}
    for t, tp, g in GEO_SR:
        if tp == 'circ':
            cx, cy, r = map(float, g.split(','))
            d = f'M{cx - r:.1f},{cy:.1f} a{r:.1f},{r:.1f} 0 1,0 {2 * r:.1f},0 a{r:.1f},{r:.1f} 0 1,0 {-2 * r:.1f},0 Z'
            out[t] = dict(d=d, lx=round(cx, 1), ly=round(cy, 1), w=round(2 * r, 1))
        else:
            pts = _poly(g); cx, cy = _centro(pts)
            out[t] = dict(d=_d(pts), lx=round(cx, 1), ly=round(cy, 1), w=round(max(p[0] for p in pts) - min(p[0] for p in pts), 1))
    return dict(vb=[0, 0, LARG, 620], t=out)


def _lg():
    import dados_lagoa_fonte as F
    nome = {p[0]: p[1] for p in F.LG_PIVOS}
    try:
        geo = json.load(open(os.path.join(F.DIR, 'lagoa_pivos.geojson'), encoding='utf-8'))
    except OSError:
        return None
    anel = {}
    for f in geo.get('features', []):
        pid = (f.get('properties') or {}).get('id'); g = f.get('geometry') or {}
        if pid in nome and g.get('type') == 'Polygon' and g.get('coordinates'):
            anel[nome[pid]] = g['coordinates'][0]
    if not anel:
        return None
    lons = [p[0] for r in anel.values() for p in r]; lats = [p[1] for r in anel.values() for p in r]
    lat0 = (min(lats) + max(lats)) / 2; kx = math.cos(math.radians(lat0))
    w = (max(lons) - min(lons)) * kx; h = max(lats) - min(lats); m = 0.04
    esc = LARG / (w * (1 + 2 * m))
    proj = dict(lon0=min(lons), lat1=max(lats), kx=kx, esc=esc, mx=w * m * esc, my=h * m * esc)
    def xy(lon, lat):
        return (proj['mx'] + (lon - proj['lon0']) * kx * esc, proj['my'] + (proj['lat1'] - lat) * esc)
    out = {}
    for t, r in anel.items():
        pts = [xy(*p[:2]) for p in r[:-1] if len(p) >= 2]
        cx, cy = _centro(pts)
        out[t] = dict(d=_d(pts), lx=round(cx, 1), ly=round(cy, 1), w=round(max(p[0] for p in pts) - min(p[0] for p in pts), 1))
    alt = round(h * esc + 2 * proj['my'], 1)
    return dict(vb=[0, 0, LARG, alt], t=out, proj={k: round(v, 9) for k, v in proj.items()})


def mapa():
    """{fazenda: {vb, t: {talhão: {d, lx, ly, w}}, proj?}} das fazendas com contorno"""
    out = {'Santa Rita': _sr()}
    lg = _lg()
    if lg:
        out['Lagoa Grande'] = lg
    return out
