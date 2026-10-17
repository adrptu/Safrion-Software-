# -*- coding: utf-8 -*-
"""Tabela v108 × agora a partir dos resumos do robô v5. Uso: python3 -I comparar.py <trabalho>
Lê resumo-<modo>.json, resumo-<modo>-1a-passada.json, saida-<modo>/escopo.v5.json e escopo-28.json; grava comparacao.json."""
import json, os, sys

T = sys.argv[1]
V108 = {'ids': (17, 55), 'cad': (6, 71), 'chega': (44, 88), 'volta': (16, 88), 'reabre': (0, 59), 'escopo': (0, 28),
        'telas': 94, 'detalhes': 180, 'passagens': 209, 'navega': 152, 'noLugar': 43, 'nada': 14, 'naoLeva': 23, 'levaIgnora': 21,
        'passo': (29, 180), 'passoPessoa': 9}


def ler(n):
    p = os.path.join(T, n)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def pct(a, b):
    return f'{a}/{b} ({round(100 * a / b)} %)' if b else f'{a}/{b}'


def escopo_robo(modo):
    e = ler(os.path.join('saida-' + modo, 'escopo.v5.json'))
    if e is None:
        return None
    n = sum(1 for x in e if x['chegou']['fazenda'] == 'Lagoa Grande' and x['chegou']['safra'] == '2026/27' and x['escolheu']['fazenda'] and x['escolheu']['safra'])
    return {'pares': len(e), 'chegouIgual': n, 'brutos': e}


out = {'v108': V108, 'modos': {}}
for modo in ('isolado', 'pacote'):
    r = ler(f'resumo-{modo}.json')
    if not r:
        continue
    r1 = ler(f'resumo-{modo}-1a-passada.json')
    a = r['robo']
    b = r1['robo'] if r1 else None
    out['modos'][modo] = {
        'ids': (a['refsClic'], a['refsTotal']), 'cad': (a['rotClic'], a['rotTotal']),
        'chega': (a['chegou'], a['navRegistro']), 'chega1a': (b['chegou'], b['navRegistro']) if b else None,
        'volta': (a['voltaOrigem'], a['navRegistro']), 'reabre': (a['reabre'], a['voltarDet']),
        'telas': a['telas'], 'detalhes': a['detalhes'], 'passagens': a['passagens'], 'navega': a['navega'], 'noLugar': a['noLugar'], 'nada': a['nada'],
        'naoLeva': a['naoLeva'], 'levaIgnora': a['levaIgnora'], 'passo': (a['detalhes'] - a['semPasso'], a['detalhes']), 'passoPessoa': a['passoPessoa'],
        'escopoResumo': a['escopo'], 'escopoRobo': escopo_robo(modo)}
e28 = ler('escopo-28.json')
if e28:
    out['escopo28'] = {'herda': sum(1 for x in e28 if x['resultado'] == 'herda'), 'telas': len(e28),
                       'porResultado': {k: [x['tela'] for x in e28 if x['resultado'] == k] for k in sorted({x['resultado'] for x in e28})}}
json.dump(out, open(os.path.join(T, 'comparacao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

M = out['modos']
cols = [m for m in ('isolado', 'pacote') if m in M]
cab = '| Medida | v108 | ' + ' | '.join({'isolado': 'agora (isolado)', 'pacote': 'agora (como no pacote)'}[m] for m in cols) + ' |'
print(cab)
print('|---' * (2 + len(cols)) + '|')
def linha(nome, v, f):
    print(f'| {nome} | {v} | ' + ' | '.join(f(M[m]) for m in cols) + ' |')
linha('IDs clicáveis', pct(*V108['ids']), lambda m: pct(*m['ids']))
linha('Cadastros clicáveis', pct(*V108['cad']), lambda m: pct(*m['cad']))
linha('Passagens que chegam no registro (com 2ª passada)', pct(*V108['chega']), lambda m: pct(*m['chega']))
linha('Passagens que chegam no registro (só 1ª passada)', '—', lambda m: pct(*m['chega1a']) if m['chega1a'] else '—')
linha('Volta à origem', pct(*V108['volta']), lambda m: pct(*m['volta']))
linha('Voltar do navegador reabre o detalhe', pct(*V108['reabre']), lambda m: pct(*m['reabre']))
e = out.get('escopo28')
linha('Escopo herdado nas 28 telas principais', pct(*V108['escopo']) + ' (leitura do código)',
      lambda m: (pct(e['herda'], e['telas']) + ' (escopo28)') if e else 'não medido')
linha('Escopo: pares do robô com a escolha na chegada', '—', lambda m: f"{m['escopoRobo']['chegouIgual']}/{m['escopoRobo']['pares']}" if m['escopoRobo'] else '—')
linha('Telas principais com filtro Fazenda / Safra (estático)', '9/28 · 5/28', lambda m: f"{m['escopoResumo']['faz']}/28 · {m['escopoResumo']['saf']}/28")
linha('Telas · detalhes · passagens', f"{V108['telas']} · {V108['detalhes']} · {V108['passagens']}", lambda m: f"{m['telas']} · {m['detalhes']} · {m['passagens']}")
linha('Passagens: outra tela · no lugar · sem efeito', f"{V108['navega']} · {V108['noLugar']} · {V108['nada']}", lambda m: f"{m['navega']} · {m['noLugar']} · {m['nada']}")
linha('Que levam registro: não leva · leva e o destino ignora', f"{V108['naoLeva']} · {V108['levaIgnora']}", lambda m: f"{m['naoLeva']} · {m['levaIgnora']}")
linha('Detalhes com Próximo passo · dizem quem age', f"{pct(*V108['passo'])} · {V108['passoPessoa']}", lambda m: f"{pct(*m['passo'])} · {m['passoPessoa']}")
