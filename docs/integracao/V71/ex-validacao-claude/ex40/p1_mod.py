# -*- coding: utf-8 -*-
"""EX-40.1 · páginas de módulo (MOD-*): o que o cartão mostra (nome, ícone, contagem?) e quantos cliques do menu à tela de trabalho (executado)."""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, G, clique, BTN, BTNC, LAB
sys.path.insert(0, G)
import ui37
s = S(); s.reset('Ana')
hubs = list(ui37.HUB37.items()) + [(ui37.OUTROS37[0], ui37.OUTROS37[2])]
s.p('# EX-40.1 · telas de entrada dos módulos (render b87f79b, Ana, 1440 × 1000)')
res = {}
for nome, f in hubs:
    s.go(f)
    d = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); const cs=[...document.querySelectorAll('a.mod-cartao')].filter(a=>a.getClientRects().length);
      return {h1:n((document.querySelector('h1')||{}).innerText), blocos:[...document.querySelectorAll('.mod-bloco-tit')].map(e=>n(e.innerText)),
        cartoes:cs.map(a=>({t:n(a.innerText), h:a.getAttribute('href'), num:/\\d/.test(a.innerText)}))};})()""")
    res[nome] = d
    s.p(f"\n## {nome} ({f}) · h1 '{d['h1']}' · {len(d['cartoes'])} cartões · blocos {d['blocos']}")
    for k in d['cartoes']: s.p(f"  - {k['t']!r} → {k['h']} · tem número no cartão: {k['num']}")
s.shot('p1_MOD-AGR.png') if False else None
s.go('MOD-AGR.dc.html'); s.shot('p1_MOD-AGR.png')
# cliques do Mapa (início) até a lista de O.S., como a pessoa: ícone Agrícola no menu lateral → cartão "Ordens de serviço"
s.go('IN-04.dc.html', espera=1.5); s.cliques = 0
r1 = clique(s, "document.querySelector('a[aria-label=\"Agrícola\"]')", 1.2); u1 = s.J("location.pathname.split('/').pop()")
r2 = clique(s, "[...document.querySelectorAll('a.mod-cartao')].find(a=>a.innerText.includes('Ordens de serviço'))", 1.5); u2 = s.J("location.pathname.split('/').pop()")
qf = s.J("[...document.querySelectorAll('button[aria-pressed]')].filter(b=>b.getClientRects().length).map(b=>(b.innerText||'').replace(/\\s+/g,' ').trim()).filter(t=>/\\d/.test(t)).slice(0,12)")
s.p(f"\n## Caminho Mapa → Agrícola → Ordens de serviço: {r1}/{r2} · telas {u1} → {u2} · cliques {s.cliques}")
s.p(f"   filtros rápidos com contagem na O.S.: {qf}")
volta = s.J("[...document.querySelectorAll('a')].filter(a=>a.getClientRects().length&&/^‹/.test((a.innerText||'').trim())).map(a=>a.innerText.trim()+' → '+a.getAttribute('href')).slice(0,3)")
s.p(f"   volta ao módulo: {volta}")
# o mesmo para a Manutenção e o Suprimentos (ícone → cartão Painel), contando
for mod, card in (('Manutenção', 'Painel'), ('Suprimentos', 'Estoque'), ('Comercial', 'Contratos e pedidos')):
    s.go('IN-04.dc.html', espera=1.2); s.cliques = 0
    clique(s, f"document.querySelector('a[aria-label=\"{mod}\"]')", 1.2); a = s.J("location.pathname.split('/').pop()")
    clique(s, f"[...document.querySelectorAll('a.mod-cartao')].find(a=>a.innerText.trim()==={json.dumps(card)})", 1.5); b = s.J("location.pathname.split('/').pop()+location.hash")
    s.p(f"   {mod}: ícone → {a} → cartão '{card}' → {b} · cliques {s.cliques}")
s.save('p1_mod.json', res)
s.p(f"\nerros JS: {s.errs()}")
s.fim('p1_mod.log')
