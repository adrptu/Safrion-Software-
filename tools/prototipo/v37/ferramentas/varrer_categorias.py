"""Varredura por CATEGORIA de dado real (sem conter nenhum valor real): CONTINUIDADE-MAC-20261003 / CORTE-REMOTO-01.
Uso: python3 varrer_categorias.py <pasta> — lista arquivos com marcas que exigem revisão humana antes de ir ao GitHub/nuvem.
A varredura com os valores reais (CAR, centros dos pivôs, áreas, outorgas) fica só no Mac do proprietário.
Fora da conta: dados_lagoa_sintetico/ (gerado, fictício por construção)."""
import os, re, sys
G = sys.argv[1]
CAT = {
    'código de CAR': re.compile(r'\b[A-Z]{2}-\d{7}-[0-9A-F]{32}\b'),
    'id de cena/tile Sentinel-2': re.compile(r'\bS2[ABC]_(MSIL2A_)?T?\d{2}[A-Z]{3}|\bT\d{2}[A-Z]{3}_\d{8}'),
    'par de coordenadas precisas no Brasil': re.compile(r'-(?:[0-2]?\d|3[0-3])\.\d{5,}\s*,\s*-(?:[3-6]\d|7[0-4])\.\d{5,}|-(?:[3-6]\d|7[0-4])\.\d{5,}\s*,\s*-(?:[0-2]?\d|3[0-3])\.\d{5,}'),
    'número de outorga/processo': re.compile(r'\b\d{7}/20\d\d\b'),
    'arquivo KML do proprietário': re.compile('KML ' + 'GER' + 'AL', re.I)   # montado em partes para o arquivo não acusar a si mesmo,
}
achados = {}
for raiz, ds, fs in os.walk(G):
    ds[:] = [d for d in ds if d not in ('.git', 'node_modules', '__pycache__', 'dados_lagoa_sintetico', '_render')]
    for f in fs:
        p = os.path.join(raiz, f)
        if f.endswith(('.png', '.jpg', '.pdf', '.zip', '.tgz', '.bundle')): continue
        try: t = open(p, encoding='utf-8', errors='ignore').read()
        except Exception: continue
        m = [k for k, rx in CAT.items() if rx.search(t)]
        if m: achados[os.path.relpath(p, G)] = m
for k, v in sorted(achados.items()): print(k, '→', ', '.join(v))
print('TOTAL', len(achados))
