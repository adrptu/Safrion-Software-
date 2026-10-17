# -*- coding: utf-8 -*-
"""ENTRADA-RAPIDA (EDL-01, INP) · inventário das listas que se editam por formulário, sem navegador: lê a especificação das grades
(GRIDS) em project/*.dc.html depois do build e grava, por grade: tela, linhas da semente, campos editáveis do formulário, quantos são
número e quais números não declaram unidade. Bruto para docs/integracao/V73/ENTRADA-RAPIDA.md.
Uso (de gen37/, depois do build): python3 -B entrada_inventario.py [saida.json]"""
import json, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, 'project')
out = []
for f in sorted(glob.glob(os.path.join(P, '*.dc.html'))):
    s = open(f, encoding='utf-8').read(); i = s.find('GRIDS = [')
    if i < 0: continue
    try: G, _ = json.JSONDecoder().raw_decode(s[i + len('GRIDS = '):])
    except Exception: continue
    for g in G:
        ed = g.get('edit') or {}; fs = [x for x in (ed.get('fields') or []) if not x.get('ro') and x.get('l')]
        if ed.get('m') != 'form' or not fs: continue
        def cnt(rs): return sum((0 if r.get('grp') else 1) + cnt(r.get('kids')) for r in (rs or []))
        out.append(dict(pag=os.path.basename(f).replace('.dc.html', ''), gid=g['id'], tit=ed.get('title', ''), linhas=cnt(g.get('rows')), campos=len(fs),
                        num=sum(1 for x in fs if x.get('t') == 'num'), num_sem_unidade=[x['l'] for x in fs if x.get('t') == 'num' and not x.get('u')],
                        datas=sum(1 for x in fs if x.get('t') == 'date'), listas=sum(1 for x in fs if x.get('t') == 'sel')))
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', '..', '..', 'docs', 'integracao', 'V73', 'entrada-inventario.json')
json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'{len(out)} listas editáveis por formulário → {os.path.normpath(dst)}')
