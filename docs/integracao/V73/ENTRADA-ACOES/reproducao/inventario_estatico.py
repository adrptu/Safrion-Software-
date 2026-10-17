# -*- coding: utf-8 -*-
"""Inventário estático de entrada e ações da linha, lido do render (somente leitura).

Uso: python3 -B -I inventario_estatico.py <pasta_render> <pasta_gen37> > saida.txt

O que mede (executado sobre o HTML gerado, sem navegador):
- grades do motor (const GRIDS = [...] de cada tela): quantas têm botões de ação nas linhas da semente
  (partes k='act' ou 'cta'), quantas ligam o ⋯ (rmenu), excluir (del) e seleção (sel);
- campos dos formulários das grades: número com e sem unidade declarada, data, lista obrigatória sem valor
  padrão e sem lista dinâmica (o <select> do motor não tem opção vazia: a 1ª opção aparece como se escolhida);
- painéis estáticos (engine.field): listas cuja opção vem do rótulo (aria-label "· lista do cadastro") e
  datas de calendário nativo (aria-label "· calendário").
Limites: linhas montadas em tempo de execução (PREVALS/EXTRAVALS) não entram na contagem de botões; a
contagem é por grade, não por linha visível. Telas ocultas do menu (ui37.oculto) são separadas.
"""
import os, re, sys, json
from collections import Counter, defaultdict

R, G = sys.argv[1], sys.argv[2]
sys.path.insert(0, G)
import ui37  # noqa: E402

def grades(txt):
    for ln in txt.split('\n'):
        if ln.startswith('const GRIDS = '):
            s = ln[len('const GRIDS = '):].rstrip().rstrip(';')
            try:
                return json.loads(s)
            except Exception:
                return []
    return []

def partes(rows):
    for r in rows or []:
        for k, ps in (r.get('p') or {}).items():
            for p in ps or []:
                if isinstance(p, dict):
                    yield k, p
        for x in partes(r.get('kids')):
            yield x

tot = Counter(); por_tela = defaultdict(Counter); sel_sem_def = []; lista_rotulo = Counter(); ex_rotulo = defaultdict(set)
fs = sorted(f for f in os.listdir(R) if f.endswith('.dc.html'))
for f in fs:
    t = open(os.path.join(R, f), encoding='utf-8', errors='replace').read()
    tela = f[:-8]; oc = 'oculta' if ui37.oculto(f) else 'menu'
    for g in grades(t):
        tot['grades_' + oc] += 1
        acts = [p for _, p in partes(g.get('rows')) if p.get('k') in ('act', 'cta')]
        if acts:
            tot['grades_com_botao_na_linha_' + oc] += 1; por_tela[tela]['grades_com_botao'] += 1
        if g.get('rmenu'): tot['grades_rmenu'] += 1; por_tela[tela]['rmenu'] += 1
        if g.get('del'): tot['grades_del'] += 1
        if g.get('sel'): tot['grades_sel_' + oc] += 1; por_tela[tela]['sel'] += 1
        ed = g.get('edit') or {}
        for fl in ed.get('fields') or []:
            ty = fl.get('t', 'txt'); tot['campo_' + oc] += 1
            if fl.get('ro'): tot['campo_ro_' + oc] += 1; continue
            if ty == 'num':
                tot['num_' + oc] += 1
                if not fl.get('u'): tot['num_sem_unidade_' + oc] += 1
            elif ty == 'date':
                tot['data_' + oc] += 1
            elif ty == 'sel':
                tot['sel_' + oc] += 1
                if fl.get('req') and 'def' not in fl and not fl.get('dyn'):
                    tot['sel_obrig_sem_padrao_' + oc] += 1; sel_sem_def.append(f"{tela}:{g['id']}:{fl.get('l')}")
            elif ty in ('txt', 'area'):
                tot['texto_' + oc] += 1
    # painéis estáticos do engine.field
    for m in re.finditer(r'aria-label="([^"]+?) · lista do cadastro"', t):
        tot['painel_lista_por_rotulo_' + oc] += 1; lab = m.group(1).strip().lower(); lista_rotulo[lab] += 1; ex_rotulo[lab].add(tela)
    for m in re.finditer(r'aria-label="([^"]+?) · calendário"', t):
        tot['painel_data_calendario_' + oc] += 1
    tot['input_date_html_' + oc] += len(re.findall(r'type="date"', t))
    tot['inputmode_html_' + oc] += len(re.findall(r'inputmode=', t, re.I))

print('== Totais (render lido; "menu" = tela do menu vigente, "oculta" = ui37.oculto)')
for k in sorted(tot): print(f'{k}: {tot[k]}')
print('\n== Telas com grade de botões na linha (semente) e ⋯ (rmenu)')
for tela in sorted(por_tela):
    c = por_tela[tela]
    if c['grades_com_botao'] or c['rmenu'] or c['sel']:
        print(f"{tela}: botões na linha em {c['grades_com_botao']} grade(s) · rmenu {c['rmenu']} · seleção {c['sel']}")
print('\n== Listas obrigatórias do formulário sem valor e sem opção vazia (o <select> mostra a 1ª opção)')
for x in sel_sem_def: print(x)
print(f'total: {len(sel_sem_def)}')
print('\n== Painéis estáticos: lista escolhida pelo rótulo (engine._opts_for), rótulo · ocorrências · telas')
for lab, n in lista_rotulo.most_common(): print(f'{lab} · {n} · {",".join(sorted(ex_rotulo[lab]))}')
