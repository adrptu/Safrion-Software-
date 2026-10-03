# -*- coding: utf-8 -*-
"""Constantes da demonstração sintética, com os mesmos nomes e formatos do dados_lagoa_kml.py do Mac (specs/esquema_lagoa.md).

Fictício por construção (CAMADA-SINTETICA-01):
- local inventado no mar, fora do território (≈ 34,6° S · 47,2° O), para nenhum círculo coincidir com imóvel real;
- áreas sorteadas pela semente fixa; pivôs em grade com folga (círculos não se sobrepõem);
- CAR "SINTETICO-…", outorga "SINT-nnn/0000", rios "Rio A/Ribeirão B (demonstração)".
Nenhum valor daqui é recomendação agronômica nem descreve a fazenda real."""
import math, random

SEMENTE = 20261003
LAT0, LON0 = -34.6, -47.2            # canto noroeste da grade de pivôs (fictício, no mar)
KX = 111320 * math.cos(math.radians(LAT0)); KY = 110540   # metros por grau (mesma aproximação do talgeo.js)
PASSO = 1300.0                        # metros entre centros da grade (raio máximo 553 m + folga)
IDS = [n for n in range(1, 25) if n != 16]          # PV01–PV24 sem PV16 (como o KML do Mac)

LG_FONTE = 'Demonstração sintética · dados fictícios gerados por dados_lagoa_sintetico (semente 20261003), sem dado real da fazenda'
LG_GEO = 'Demonstração sintética · círculo fictício pelo centro e pela área'

def raio_de_ha(ha): return math.sqrt(ha * 1e4 / math.pi)
def ll_de_m(x, y): return LON0 + x / KX, LAT0 - y / KY       # x para leste, y para sul, em metros

def _pivos():
    r = random.Random(SEMENTE); out = []
    for i, n in enumerate(IDS):
        ha = round(r.uniform(28.0, 96.0), 2)
        x = (i % 6 + 0.5) * PASSO + r.uniform(-80, 80); y = (i // 6 + 0.5) * PASSO + r.uniform(-80, 80)
        lon, lat = ll_de_m(x, y)
        out.append((f'PV{n:02d}', f'Pivô {n}', ha, round(lon, 6), round(lat, 6), round(raio_de_ha(ha), 2)))
    return out
LG_PIVOS = _pivos()
_HA = sum(p[2] for p in LG_PIVOS)
_CAR = 'SINTETICO-MG-0000001-DEMONSTRACAO'

LG_PERIMETROS = [
    dict(nome='Imóvel (demonstração sintética)', area=round(_HA * 1.85, 2), car=_CAR, mf=38.6, mun='Lagoa Grande/MG (demonstração)',
         temas=['Área do imóvel', 'Reserva legal', 'APP', 'Vegetação nativa']),
    dict(nome='Gleba anexa (demonstração sintética)', area=None, car=_CAR, mf=0, mun='Lagoa Grande/MG (demonstração)', temas=['Área do imóvel']),
]

def _ambiental():
    r = random.Random(SEMENTE + 1); rl = [round(r.uniform(60, 140), 2) for _ in range(3)]
    app = [('APP de curso d’água até 10 m', 41.3), ('APP de curso d’água de 10 a 50 m', 18.7), ('APP de nascente', 6.2),
           ('APP de lagoa natural', 22.4), ('APP de vereda', 15.9), ('APP de reservatório artificial', 4.8),
           ('APP de topo de morro', 9.1), ('APP de declividade', 3.6)]
    out = [('Reserva legal', 'Reserva legal total (demonstração)', round(sum(rl), 2), True)]
    out += [('Reserva legal', f'Reserva legal averbada · gleba {g} (demonstração)', a, False) for g, a in zip('ABC', rl)]
    out.append(('APP', 'APP total (demonstração; categorias se sobrepõem)', round(0.8 * sum(a for _, a in app), 2), True))
    out += [('APP', t, a, False) for t, a in app]
    out += [('Vegetação nativa', 'Remanescente de vegetação nativa (demonstração)', 212.5, True),
            ('Área consolidada', 'Área rural consolidada (demonstração)', round(_HA * 0.9, 2), True),
            ('Servidão administrativa', 'Servidão de linha de transmissão (demonstração)', 7.4, True),
            ('Uso restrito', 'Área de uso restrito (demonstração)', 12.0, True),
            ('Pousio', 'Área em pousio declarada (demonstração)', 30.0, True)]
    return out
LG_AMBIENTAL = _ambiental()

def _agua():
    # situação coberta de propósito (hoje da demonstração = 23/09/2026): vigente, vence em 90 dias, vencida, em renovação e sem descrição
    base = [('Outorga', 'Captação superficial', 'Rio A (demonstração)', '180 m³/h', '20 h/dia · 12 meses', 'Irrigação', '2031-04-30', ''),
            ('Outorga', 'Captação superficial', 'Rio A (demonstração)', '150 m³/h', '20 h/dia · 12 meses', 'Irrigação', '2026-11-20', ''),
            ('Outorga', 'Captação superficial', 'Ribeirão B (demonstração)', '120 m³/h', '18 h/dia · 10 meses', 'Irrigação', '2026-05-10', ''),
            ('Outorga', 'Barramento', 'Ribeirão B (demonstração)', '—', 'regularização de vazão', 'Irrigação', '2025-12-01', 'SINT-REN-004'),
            ('Outorga', 'Poço tubular', '', '12 m³/h', '16 h/dia · 12 meses', 'Consumo humano', '2029-08-15', ''),
            ('Certidão de uso insignificante', 'Captação superficial', 'Córrego C (demonstração)', '1,0 L/s', 'contínuo', 'Dessedentação animal', '2028-02-28', ''),
            ('Outorga', 'Captação superficial', 'Rio A (demonstração)', '200 m³/h', '20 h/dia · 12 meses', 'Irrigação', '2032-06-30', ''),
            ('Outorga', 'Lançamento', 'Córrego C (demonstração)', '8 m³/h', 'contínuo', 'Lavagem de máquinas', '2027-03-31', ''),
            ('Certidão de uso insignificante', 'Poço manual', '', '0,5 L/s', 'contínuo', 'Consumo humano', '2026-12-10', ''),
            ('Outorga', 'Captação superficial', 'Ribeirão B (demonstração)', '160 m³/h', '20 h/dia · 12 meses', 'Irrigação', '2030-10-31', ''),
            ('Outorga', 'Barramento', 'Córrego C (demonstração)', '—', 'regularização de vazão', 'Irrigação', '2033-01-31', ''),
            ('Outorga', 'Poço tubular', '', '20 m³/h', '20 h/dia · 12 meses', 'Fertirrigação', '2026-08-31', ''),
            ('Certidão de uso insignificante', 'Captação superficial', 'Rio A (demonstração)', '1,0 L/s', 'contínuo', 'Dessedentação animal', '2029-05-31', ''),
            ('Outorga', 'Captação superficial', 'Rio A (demonstração)', '140 m³/h', '18 h/dia · 12 meses', 'Irrigação', '2027-09-30', ''),
            ('Outorga', 'Poço tubular', '', '15 m³/h', '16 h/dia · 12 meses', 'Consumo humano', '2026-01-15', 'SINT-REN-015'),
            ('Certidão de uso insignificante', 'Captação superficial', 'Córrego C (demonstração)', '0,8 L/s', 'contínuo', 'Dessedentação animal', '', '')]
    r = random.Random(SEMENTE + 2); out = []
    for i, (tipo, modo, curso, vaz, reg, fin, venc, renov) in enumerate(base, 1):
        lon, lat = ll_de_m(r.uniform(-400, 6 * PASSO + 400), r.uniform(-400, 4 * PASSO + 400))
        desc = '' if i == 16 else f'{modo} · {fin.lower()} · ponto fictício {i} (demonstração sintética)'
        out.append(dict(curso=curso, desc=desc, fin=fin, id=f'AG{i:02d}', lat=round(lat, 6), lon=round(lon, 6), modo=modo,
                        nome=f'Ponto de água {i} (demonstração)', num=f'SINT-{i:03d}/0000', proc=f'SINT-PROC-{i:03d}', regime=reg,
                        renov=renov, tipo=tipo, vazao=vaz, venc=venc))
    return out
LG_AGUA = _agua()
