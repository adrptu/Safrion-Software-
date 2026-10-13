# -*- coding: utf-8 -*-
"""Monta _render/ (o que a varredura e os testes servem) a partir do que o build gera, sem depender do Mac.
Uso: python3 build.py && python3 montar_render.py && python3 varredura.py
Copia project/*.dc.html, support.js e os JSONs do AGROFIT (dados_agrofit/site, dados abertos CC-BY). Os arquivos da
Fazenda Lagoa Grande (dados_lagoa/: lagoa_s2.json e imagens) entram só se existirem localmente: são dado real e ficam
fora do repositório (CONTINUIDADE-MAC-20261003). Sem eles, a camada Satélite da Lagoa Grande aparece sem imagem."""
import os, sys, glob, shutil
G = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(G, '_render'); P = os.path.join(G, 'project')
os.makedirs(R, exist_ok=True)
pags = sorted(glob.glob(os.path.join(P, '*.dc.html')))
if not pags: sys.exit('sem páginas em project/: rode python3 build.py antes')
for f in pags: shutil.copy2(f, R)
extras = [os.path.join(G, 'support.js')] + sorted(glob.glob(os.path.join(G, 'dados_agrofit', 'site', '*.json')))
reais = [os.path.join(__import__('dados_lagoa_fonte').DIR, n) for n in ('lagoa_s2.json',)] + sorted(glob.glob(os.path.join(__import__('dados_lagoa_fonte').DIR, 'lagoa_*.png')))
falta = [e for e in extras if not os.path.exists(e)]
if falta: sys.exit('faltam arquivos do site: ' + ', '.join(os.path.relpath(e, G) for e in falta))
for e in extras + [r for r in reais if os.path.exists(r)]: shutil.copy2(e, R)
print(f'_render montado: {len(pags)} páginas + {len(extras)} arquivos do site · dados reais locais: {sum(os.path.exists(r) for r in reais)}/{len(reais)}')
