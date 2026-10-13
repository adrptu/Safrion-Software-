# -*- coding: utf-8 -*-
"""COLUNAS-1 · tabela de medidas da evidência (lê <pasta>/antes.json e <pasta>/depois.json do colunas1_evid.py e imprime Markdown).
Uso (de gen37/): python3 colunas1_evid_md.py <pasta das capturas>"""
import sys, os, json
D = sys.argv[1]
A, B = (json.load(open(os.path.join(D, x + '.json'))) for x in ('antes', 'depois'))
def g(d, w): return (d.get(str(w)) or {}).get('grades') or []
def pag(d, w): p = (d.get(str(w)) or {}).get('pagina') or [0, 0]; return max(0, p[0] - p[1])
print('| Tela | Grade | Colunas antes → depois | Rolagem lateral a 1440 (px) antes → depois | Rolagem lateral a 390 (px) antes → depois | 1ª coluna presa a 390 | Página rola a 390 |')
print('|---|---|---|---|---|---|---|')
for k in A:
    ga, gb, ga3, gb3 = g(A[k], 1440), g(B.get(k, {}), 1440), g(A[k], 390), g(B.get(k, {}), 390)
    n = max(len(ga), len(gb))
    for i in range(n):
        a = ga[i] if i < len(ga) else None; b = gb[i] if i < len(gb) else None
        a3 = ga3[i] if i < len(ga3) else None; b3 = gb3[i] if i < len(gb3) else None
        f = lambda x, c: (str(x[c]) if x else '—')
        print(f"| {k} | {i + 1} | {len(a['cols']) if a else '—'} → {len(b['cols']) if b else '— (saiu)'} | {f(a, 'rola')} → {f(b, 'rola')} | {f(a3, 'rola')} → {f(b3, 'rola')} | "
              f"{'sim' if b3 and b3.get('c0preso') else ('—' if not b3 else 'não')} | {pag(A[k], 390)} → {pag(B.get(k, {}), 390)} |")
print()
print('| Tela | Ordenação (coluna · muda a ordem) | Filtro (coluna · linhas antes → depois) | Detalhe abre · fecha · filtro e ordem preservados · rolagem igual | Teclado: Tabs até a linha · seta ↓ · Enter abre · Tab entra · Esc fecha · foco volta à linha |')
print('|---|---|---|---|---|')
for k, v in B.items():
    c = v.get('comportamento') or {}; o = c.get('ordenar') or {}; fl = c.get('filtrar') or {}; dt = c.get('detalhe') or {}; t = c.get('teclado') or {}
    sim = lambda x: 'sim' if x is True else ('não' if x is False else '—')
    seta = t.get('seta_baixo') or {}
    print(f"| {k} | {(o.get('coluna') or '—').replace('Ordenar por ', '')} · {sim(o.get('mudou_ordem'))} | {fl.get('coluna') or '—'} · {fl.get('linhas_antes', '—')} → {fl.get('linhas_depois', '—')} | "
          f"{sim(dt.get('abriu'))} · {sim(dt.get('fechou'))} · {sim(dt.get('filtro_e_ordem_preservados'))} · {sim(dt.get('rolagem_antes') == dt.get('rolagem_depois') if dt else None)} | "
          f"{t.get('tabs_ate_linha', '—')} · {'move' if seta and seta.get('antes') != seta.get('depois') else 'não move'} · {sim(t.get('enter_abre'))} · {sim(t.get('tab_entra_no_detalhe')) if 'tab_entra_no_detalhe' in t else 'já dentro'} · {sim(t.get('esc_fecha'))} · {sim(t.get('foco_volta_linha'))} |"
          + (f" erro: {c['erro']}" if c.get('erro') else ''))
