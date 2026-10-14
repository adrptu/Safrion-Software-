# textos soltos: blocos de texto à vista em main/header fora de tabela, botão, link, formulário, diálogo e cabeçalho h1-h3, com ≥ 45 caracteres
import os, sys, json, glob
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(G, '_render')
JS = r"""JSON.stringify((()=>{ const out=[]; const raiz=document.querySelector('[data-root]')||document.body;
  const fora=e=>e.closest('[role=table],[role=grid],table,button,a,select,input,textarea,label,[role=dialog],aside,nav,h1,h2,h3,[role=tab],[role=status],[role=alert],svg,.menu-lat,[data-acoes]');
  const w=document.createTreeWalker(raiz,NodeFilter.SHOW_TEXT); const vist=new Set();
  while(w.nextNode()){ const n=w.currentNode; const t=n.textContent.replace(/\s+/g,' ').trim(); if(t.length<12) continue; const el=n.parentElement; if(!el||fora(el)) continue;
    const b=el.closest('div,p,span,section')||el; if(vist.has(b)) continue; if(!b.getClientRects().length) continue;
    const tx=(b.innerText||'').replace(/\s+/g,' ').trim(); if(tx.length<45) continue; if(b.querySelector('[role=table],button,input,select')) continue; vist.add(b); out.push(tx.slice(0,140)); }
  return out; })())"""
p, srv = servir(R); c = Chrome(); J = c.js; res = {}
try:
    c.aparelho(1440, 900, 1, False)
    for f in sorted(glob.glob(os.path.join(R, '*.dc.html'))):
        n = os.path.basename(f); c.goto(f'http://127.0.0.1:{p}/{n}', 2.5 if n.startswith('AG-07') else 1.1)
        t = json.loads(J(JS) or '[]')
        if t: res[n] = t
finally:
    c.close(); srv.terminate()
json.dump(res, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
tot = sorted(((sum(len(x) for x in v), k, len(v)) for k, v in res.items()), reverse=True)
print('telas com texto solto:', len(res), '· caracteres:', sum(x[0] for x in tot))
for s_, k, n in tot[:25]: print(f'{s_:6d} {n:3d} {k}')
