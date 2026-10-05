# -*- coding: utf-8 -*-
"""TF05 (TABELAS-FOCO-20261004 v2, 5983172395) — inventário estrutural de TODAS as grades G2 publicadas e das tabelas manuais.
Lê project/*.dc.html (gerado por build.py), extrai GRIDS (as grades G2 com colunas e linhas da página) e procura, por coluna, sinais de
variável composta: rótulo com "·", "/" ou "e"; valores com duas medidas ("190 / 350 ha", "95 ha · 100 %"), número seguido de texto com
"·", ou data + texto. É triagem estrutural (heurística): cada suspeita vira decisão (separar, ou exceção semântica justificada) no
incremento da tela; nada aqui declara a tela conforme. Tabelas manuais (role=table fora do G2) são contadas por página.
Uso: python3 tabelas_inventario.py [saida.md] [saida.json]"""
import os, re, sys, json, glob
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, 'project')
OUT_MD = sys.argv[1] if len(sys.argv) > 1 else None; OUT_JS = sys.argv[2] if len(sys.argv) > 2 else None
NUM = r'\d[\d.]*(?:,\d+)?'
UN = r'(?:ha|%|kg|L|t|sc|h|mm|m|km/h|R\$|R\$/ha|R\$/kg|un|dias?)'
R_DUAS = re.compile(rf'{NUM}\s+/\s+{NUM}|{NUM}\s*/\s*{NUM}\s*{UN}\b')        # 190 / 350 ha, 190/350 ha (não confunde com data 24/09)
R_FAIXA = re.compile(r'\d{2}/\d{2}(?:/\d{2,4})?(?:\s+\d{2}:\d{2})?\s*[–-]\s*\d{2}(?:/\d{2}|:\d{2})')   # 19–21/09, 01/07/26 – 30/06/27
R_MED2 = re.compile(rf'{NUM}\s*{UN}\b.*[·;|].*{NUM}\s*{UN}\b')            # 95 ha · 100 %
R_NUMTXT = re.compile(rf'^{NUM}\s*{UN}?\s*·\s*\D')                        # 38 ha · café
R_DATATXT = re.compile(r'\d{2}/\d{2}(?:/\d{2,4})?\s*[·–-]\s*\D{3,}')       # 24/09 · Rui
R_ROT = re.compile(r'\s·\s|\s/\s|\se\s', re.I)   # unidade entre parênteses (ha/h) e mês (set/26) não são rótulo composto

def textos(r, k):
    v = (r.get('v') or {}).get(k); s = (r.get('s') or {}).get(k); ps = (r.get('p') or {}).get(k)
    out = []
    for x in (v, s):
        if isinstance(x, str) and x.strip(): out.append(x.strip())
    if ps:
        t = ' '.join(str(q.get('t', '')) for q in ps if isinstance(q, dict) and q.get('k') != 'br').strip()
        if t: out.append(t)
    return out

def linhas(rows):
    for r in rows or []:
        yield r
        yield from linhas(r.get('kids'))

def grids(html):
    m = re.search(r'const GRIDS = (\[.*?\]);\nconst NAV', html, re.S)
    return json.loads(m.group(1).replace('<\\/', '</')) if m else []

def main():
    inv = []; manuais = []
    try: MENU = {f for f, b in json.load(open(os.path.join(P, 'canvas.json'), encoding='utf-8'))['boards'].items() if b.get('page') == 'menu'}
    except Exception: MENU = set()
    for f in sorted(glob.glob(os.path.join(P, '*.dc.html'))):
        pag = os.path.basename(f); html = open(f, encoding='utf-8').read()
        gs = grids(html)
        n_tab = len(re.findall(r'role="table"', html)); n_g2 = len(gs)
        if n_tab > n_g2: manuais.append(dict(pagina=pag, tabelas=n_tab - n_g2))
        for g in gs:
            rs = list(linhas(g.get('rows')))
            cols = []
            for c in g.get('cols') or []:
                k, l = c.get('k'), c.get('l') or c.get('k')
                motivos, ex = [], ''
                if R_ROT.search(re.sub(r'\([^)]*\)', '', l or '')): motivos.append('rótulo composto')
                cnt = {'duas medidas': 0, 'início–fim': 0, 'número + texto': 0, 'data + texto': 0}
                for r in rs:
                    for t in textos(r, k):
                        hit = None
                        if R_DUAS.search(t) or R_MED2.search(t): hit = 'duas medidas'
                        elif R_FAIXA.search(t): hit = 'início–fim'
                        elif R_NUMTXT.search(t): hit = 'número + texto'
                        elif R_DATATXT.search(t): hit = 'data + texto'
                        if hit:
                            cnt[hit] += 1; ex = ex or t[:70]; break
                motivos += [f'{m} ({n})' for m, n in cnt.items() if n]
                cols.append(dict(k=k, l=l, t=c.get('t', 'txt'), multi=bool(c.get('multi')), suspeita=motivos, exemplo=ex))
            inv.append(dict(menu=pag in MENU, pagina=pag, grade=g.get('id') or '(sem id)', linhas=len(rs), colunas=cols))
    sus = sorted([(g, c) for g in inv for c in g['colunas'] if c['suspeita']], key=lambda x: (not x[0]['menu'], x[0]['pagina']))
    susm = [x for x in sus if x[0]['menu']]
    md = ['# TF05 · Inventário estrutural das grades (gerado por `tabelas_inventario.py`)', '',
          f'Páginas com grade G2: {len({g["pagina"] for g in inv})} · grades: {len(inv)} · colunas: {sum(len(g["colunas"]) for g in inv)} · '
          f'colunas com suspeita de variável composta: {len(sus)} em {len({(g["pagina"], g["grade"]) for g, _ in sus})} grades · '
          f'páginas com tabela manual fora do G2: {len(manuais)} ({sum(m["tabelas"] for m in manuais)} tabelas).', '',
          f'Menu vigente ({len(MENU)} telas): {sum(1 for g in inv if g["menu"])} grades · {len(susm)} colunas com suspeita em {len({(g["pagina"], g["grade"]) for g, _ in susm})} grades (vêm primeiro na lista).', '',
          'Motivos: rótulo composto (o cabeçalho junta duas variáveis); duas medidas ("190 / 350 ha", "95 ha · 100 %"); início–fim (intervalo numa célula); número + texto; data + texto. '
          'Triagem heurística: a suspeita não prova defeito, e a ausência de suspeita não prova conformidade. Cada linha vira decisão no incremento da tela.', '',
          '## Colunas com suspeita', '', '| Menu | Página | Grade | Coluna | Motivo | Exemplo |', '|---|---|---|---|---|---|']
    for g, c in sus:
        md.append(f"| {'sim' if g['menu'] else 'oculto'} | {g['pagina']} | {g['grade']} | {c['l']} | {'; '.join(c['suspeita'])} | {c['exemplo'].replace('|', '/')} |")
    md += ['', '## Todas as grades', '', '| Página | Grade | Linhas | Colunas (tipo) |', '|---|---|---|---|']
    for g in inv:
        md.append(f"| {g['pagina']} | {g['grade']} | {g['linhas']} | " + ', '.join(c['l'] + (' [multi]' if c['multi'] else '') + ('' if c['t'] == 'txt' else f" [{c['t']}]") for c in g['colunas']) + ' |')
    md += ['', '## Tabelas manuais (role=table fora do G2)', '', '| Página | Tabelas |', '|---|---|'] + [f"| {m['pagina']} | {m['tabelas']} |" for m in manuais]
    txt = '\n'.join(md) + '\n'
    if OUT_MD: open(OUT_MD, 'w', encoding='utf-8').write(txt)
    if OUT_JS: json.dump(dict(grades=inv, manuais=manuais), open(OUT_JS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n'.join(md[:5]))
    os_ = [c for g in inv if g['pagina'] == 'OS.dc.html' and g['grade'] == 'g_os' for c in g['colunas'] if c['suspeita']]
    print('g_os (O.S., incremento 1) com suspeita:', [(c['l'], c['suspeita'], c['exemplo']) for c in os_])

if __name__ == '__main__':
    main()
