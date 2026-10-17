# -*- coding: utf-8 -*-
"""Gera a tabela única da validação do Claude e as contagens, a partir de tabela_claude.tsv e do anexo dos achados.

Uso (na raiz da worktree):
  git show 529adf7:docs/integracao/V73/pedidos-1610/entrada-acoes-revisao-anexo-achados.md > /tmp/anexo.md
  python3 -I docs/integracao/V73/ENTRADA-ACOES/reproducao/gera_tabela.py /tmp/anexo.md docs/integracao/V73/ENTRADA-ACOES/reproducao/tabela_claude.tsv
Saída: a tabela em Markdown (ordem do anexo) e as contagens. Falha se faltar ou sobrar ID, ou se a validação não for uma das 4.
"""
import re, sys, csv
from collections import Counter

anexo, tsv = sys.argv[1], sys.argv[2]
t = open(anexo, encoding='utf-8').read()
ach = []
for p in re.split(r'^### ', t, flags=re.M)[1:]:
    m = re.match(r'(\S+) · (\S+) · (.+?) · (.+)$', p.split('\n', 1)[0])
    ach.append(dict(id=m.group(1), pri=m.group(2), tela=m.group(3), tipo=m.group(4)))
lin = {r['id']: r for r in csv.DictReader(open(tsv, encoding='utf-8'), delimiter='\t')}
ids = [a['id'] for a in ach]
falta = [i for i in ids if i not in lin]; sobra = [i for i in lin if i not in ids]
assert not falta and not sobra, (falta, sobra)
VAL = {'Confirmado', 'Refutado', 'Já resolvido', 'Em andamento'}
assert all(r['validacao'] in VAL for r in lin.values()), [r['id'] for r in lin.values() if r['validacao'] not in VAL]
esc = lambda s: s.replace('|', '‖').strip()
print('| ID | Prioridade | Tela · tipo | Validação | Evidência na fonte | Decisão Claude | Onda | Esforço | Risco |')
print('|---|---|---|---|---|---|---|---|---|')
for a in ach:
    r = lin[a['id']]
    print(f"| {a['id']} | {a['pri']} | {esc(a['tela'])} · {esc(a['tipo'])} | {r['validacao']} | {esc(r['evidencia'])} | {esc(r['decisao'])} | {r['onda']} | {r['esforco']} | {esc(r['risco'])} |")
tot = Counter(lin[i]['validacao'] for i in ids)
alta = Counter(lin[a['id']]['validacao'] for a in ach if a['pri'] == 'Alta')
ond = Counter(lin[i]['onda'] for i in ids)
dec = Counter(lin[i]['decisao'].split(':')[0].split(' ')[0] for i in ids)
print()
print('Contagem por validação (187):', dict(tot))
print('Contagem por validação (57 altos):', dict(alta), '· total altos', sum(alta.values()))
print('Por onda sugerida:', dict(ond))
print('Por decisão (1ª palavra):', dict(dec))
