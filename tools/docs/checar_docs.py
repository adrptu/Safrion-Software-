# -*- coding: utf-8 -*-
"""Integridade da documentação (roda localmente e na CI, só com Python padrão).
Confere: arquivos obrigatórios do PRD 23.4; CLAUDE.md importa AGENTS.md (fonte única); PRD com versão identificada;
IDs definidos em tabela não repetidos (RN, CMD, CAL, FO, AC, DEC-2609, ENG, NFR, ACE); decisões do índice existem no PRD;
links relativos entre arquivos .md existem; nenhum marcador de conflito de merge."""
import os, re, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
falhas, oks = [], []
def ok(cond, msg): (oks if cond else falhas).append(msg)
def ler(p): return open(os.path.join(RAIZ, p), encoding='utf-8').read()

OBRIG = ['AGENTS.md', 'CLAUDE.md', 'README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'docs/PRD.md', 'docs/STATUS.md',
         'docs/DECISIONS.md', 'docs/OPERACAO.md', 'docs/architecture/versions.md', '.github/pull_request_template.md']
for p in OBRIG: ok(os.path.exists(os.path.join(RAIZ, p)), f'arquivo obrigatório presente: {p}')
if os.path.exists(os.path.join(RAIZ, 'CLAUDE.md')):
    ok(ler('CLAUDE.md').strip().startswith('@AGENTS.md'), 'CLAUDE.md importa AGENTS.md (fonte única de instruções)')

prd = ler('docs/PRD.md')
m = re.search(r'^\*\*Versão (\d+\.\d+) · ([^·*]+)', prd, re.M)
ok(bool(m), 'PRD com versão e data identificadas no cabeçalho')
for pref in ['RN', 'CMD', 'CAL', 'FO', 'DEC-2609', 'ENG', 'NFR', 'ACE']:
    # definição = primeira coluna de tabela ou título de seção (os cálculos CAL-xx são títulos ###)
    ids = re.findall(rf'^(?:\| |#+ )({pref}-\d{{2,3}})\b', prd, re.M)
    rep = sorted({i for i in ids if ids.count(i) > 1})
    ok(not rep, f'{pref}: {len(set(ids))} IDs definidos em tabela, sem repetição' + (f' — repetidos: {rep[:10]}' if rep else ''))

dec = ler('docs/DECISIONS.md')
for i in re.findall(r'^\| (DEC-2609-\d\d|DEC-0\d) \|', dec, re.M):
    ok(re.search(rf'^\| {i} \|', prd, re.M) is not None, f'decisão {i} do índice existe no PRD')

quebrados = []
for base, _, arqs in os.walk(RAIZ):
    if '/.git' in base or '/node_modules' in base: continue
    for a in arqs:
        if not a.endswith('.md'): continue
        p = os.path.join(base, a); txt = open(p, encoding='utf-8').read()
        if re.search(r'^(<<<<<<<|>>>>>>>) ', txt, re.M): falhas.append(f'marcador de conflito em {os.path.relpath(p, RAIZ)}')
        for alvo in re.findall(r'\]\(([^)#:]+?)(?:#[^)]*)?\)', txt):
            if alvo.startswith(('http', 'mailto')): continue
            if not os.path.exists(os.path.normpath(os.path.join(base, alvo))): quebrados.append(f'{os.path.relpath(p, RAIZ)} → {alvo}')
ok(not quebrados, 'links relativos entre documentos existem' + (f' — quebrados: {quebrados[:10]}' if quebrados else ''))

for m_ in oks: print('OK    ', m_)
for m_ in falhas: print('FALHA ', m_)
print(f'\n{len(oks)} OK · {len(falhas)} falha(s)')
sys.exit(1 if falhas else 0)
