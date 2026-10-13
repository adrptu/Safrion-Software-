# -*- coding: utf-8 -*-
"""Menu Manutenção com subitens enxutos (pedido do proprietário, 13/10/2026): um subitem por visão da tela única MA.dc.html.
Confere: os 4 subitens e a ordem; o destaque (aria-current="page" e fundo verde) segue a visão aberta; tocar um subitem na própria
tela troca a visão sem recarregar. Uso: python3 ma_menu_test.py (lê _render)."""
import sys, json
from ma_lib import MA

m = MA(1440, 900); J = m.J
ITENS = ['Pendências sem ordem', 'Ordens de manutenção', 'Ativos e disponibilidade', 'Planos preventivos']
VIS = ['semordem', 'ordens', 'ativos', 'planos']
LER = ("JSON.stringify([...document.querySelectorAll('nav[aria-label=Menu] a')].filter(a=>/MA\\.dc\\.html#vis=/.test(a.getAttribute('href')))"
       ".map(a=>[a.innerText.trim(),a.getAttribute('href'),a.getAttribute('aria-current'),getComputedStyle(a).backgroundColor]))")
try:
    for i, v in enumerate(VIS):
        m.ir('vis=' + v, perfil='Otávio'); L = json.loads(J(LER) or '[]')
        m.ok([x[0] for x in L] == ITENS and [x[1] for x in L] == ['MA.dc.html#vis=' + k for k in VIS]
             and [x[2] for x in L] == ['page' if k == i else 'false' for k in range(4)]
             and L[i][3] == 'rgb(30, 122, 76)' and all(L[k][3] == 'rgba(0, 0, 0, 0)' for k in range(4) if k != i),
             f'visão {v}: 4 subitens na ordem e só "{ITENS[i]}" destacado', L)
    m.ir('vis=ordens', perfil='Otávio'); m.clk('Planos preventivos', 'nav[aria-label=Menu]', w=1.5)
    cur = J("([...document.querySelectorAll('nav[aria-label=Menu] a[aria-current=page]')].map(a=>a.innerText.trim()))")
    m.ok(m.hash() == '#vis=planos' and cur == ['Planos preventivos'] and 'PLANOS' in (m.body() or '').upper(),
         'tocar "Planos preventivos" estando em Ordens troca a visão na mesma tela e move o destaque', [m.hash(), cur])
finally:
    m.fim() if hasattr(m, 'fim') else None
