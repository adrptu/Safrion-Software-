# -*- coding: utf-8 -*-
"""Painéis estáticos (engine.drawer_button): o botão de confirmar mostra um texto fixo ("done") e não lê os campos.
Uso: python3 -B -I paineis_estaticos.py <pasta_render> <pasta_gen37>
Lê o SPEC de cada tela (const SPEC = [...]) e lista os itens type='drawer' (rótulo e texto fixo do resultado),
separando telas do menu e ocultas (ui37.oculto). Executado sobre o HTML gerado, sem navegador."""
import os, sys, json
R, G = sys.argv[1], sys.argv[2]
sys.path.insert(0, G)
import ui37
tot = {'menu': 0, 'oculta': 0}; linhas = []
for f in sorted(x for x in os.listdir(R) if x.endswith('.dc.html')):
    t = open(os.path.join(R, f), encoding='utf-8', errors='replace').read()
    for ln in t.split('\n'):
        if ln.startswith('const SPEC = '):
            try: spec = json.loads(ln[len('const SPEC = '):].rstrip().rstrip(';'))
            except Exception: spec = []
            for s in spec:
                if s.get('type') == 'drawer':
                    oc = 'oculta' if ui37.oculto(f) else 'menu'; tot[oc] += 1
                    linhas.append(f"{oc}\t{f[:-8]}\t{s.get('label','')}\t{(s.get('done') or '')[:90]}")
            break
print('painéis estáticos (confirmar com texto fixo):', tot)
for l in linhas: print(l)
