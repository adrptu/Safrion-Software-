# -*- coding: utf-8 -*-
"""P0 · inventário das 156 páginas do render (executado): links (a[href]) de cada página, alcance a partir do menu vigente (BFS em saltos),
e onde aparecem os textos citados no EX-40 (visível = innerText; presente = textContent, inclui menus ⋯ fechados)."""
import os, sys, json, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, R, OUT, G
sys.path.insert(0, G)
import ui37
TXT = ['Restaurar demonstração', 'Encerrar saldo', 'Cancelar reserva', 'Cancelar sem execução', 'Notificar responsáveis', 'Água no solo',
       'Manutenções e impacto na produção', 'Concluir com', 'Propor melhoria', 'Propor revisão', 'Formalizar contrato', 'Aprovar e emitir',
       'Emitir pedido', 'Aprovar compra', 'Validar', 'Publicar']
pags = sorted(f for f in os.listdir(R) if f.endswith('.dc.html'))
s = S(); s.reset('Ana')
inv = {}
for f in pags:
    s.go(f, espera=.5)
    d = s.J("""(()=>{const n=s=>(s||'').replace(/\\s+/g,' ').trim();
      const hs=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).filter(h=>h&&/\\.dc\\.html/.test(h)).map(h=>h.split('#')[0].split('?')[0].split('/').pop());
      const h1=document.querySelector('h1'); return {h1:h1?n(h1.innerText).slice(0,80):'', links:[...new Set(hs)], vis:document.body.innerText, all:(()=>{const tw=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,{acceptNode:x=>(x.parentElement&&x.parentElement.closest('script,style,template'))?2:1}); let o=''; while(tw.nextNode()) o+=tw.currentNode.nodeValue+' '; return o;})(), errs:(window.__errs||[]).slice(0,3)};})()""")
    oc = {}
    for t in TXT:
        v = d['vis'].count(t); a = d['all'].count(t)
        if v or a: oc[t] = [v, a]
    inv[f] = dict(h1=d['h1'], links=d['links'], oc=oc, errs=d['errs'], oculto=ui37.oculto(f))
    print(f, d['h1'][:40], len(d['links']), oc, d['errs'][:1], flush=True)
s.fim()
# alcance: raiz = telas do menu vigente (não ocultas) + Main; BFS pelos links
raiz = [f for f in pags if not inv[f]['oculto']]
dist = {f: 0 for f in raiz}; fila = list(raiz)
while fila:
    f = fila.pop(0)
    for h in inv.get(f, {}).get('links', []):
        if h in inv and h not in dist: dist[h] = dist[f] + 1; fila.append(h)
for f in pags: inv[f]['saltos'] = dist.get(f)
json.dump(inv, open(os.path.join(OUT, 'p0_inventario.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
lin = ['# P0 · inventário (executado, render b87f79b, perfil Ana)', f'páginas: {len(pags)} · no menu (não ocultas): {len(raiz)} · ocultas: {len(pags)-len(raiz)}',
       'sem caminho por link a partir do menu: ' + ', '.join(f for f in pags if dist.get(f) is None)]
for t in TXT:
    lin.append(f'\n## "{t}" (visível, presente no DOM) · página (saltos do menu; oculta?)')
    for f in pags:
        if t in inv[f]['oc']: lin.append(f"  {f}: {inv[f]['oc'][t]} · saltos={inv[f]['saltos']} · oculta={inv[f]['oculto']}")
lin.append('\n## erros de JavaScript')
for f in pags:
    if inv[f]['errs']: lin.append(f'  {f}: {inv[f]["errs"]}')
open(os.path.join(OUT, 'p0_inventario.txt'), 'w', encoding='utf-8').write('\n'.join(lin) + '\n')
print('\n'.join(lin))
