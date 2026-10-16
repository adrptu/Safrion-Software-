# -*- coding: utf-8 -*-
"""EX-40.2 (PL-05 "Notificar responsáveis") e EX-40.5 (bloco "Manutenções e impacto na produção" em PL-03 e PL-04) · executado."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, clique, BTN, BTNC
s = S(); s.reset('Ana')
s.p('# EX-40.2 · PL-05 Notificar responsáveis (render b87f79b)')
for perfil in ('Ana', 'Caio'):
    s.perfil(perfil); s.go('PL-05.dc.html', espera=1.2)
    h1 = s.J("(document.querySelector('h1')||{}).innerText")
    antes = s.J("JSON.stringify(Object.keys(localStorage).sort())")
    r = clique(s, BTN('Notificar responsáveis')); t = s.toast()
    depois = s.J("JSON.stringify(Object.keys(localStorage).sort())")
    s.p(f"[{perfil}] h1 {h1!r} · clique {r} · aviso: {t!r}")
    s.p(f"   chaves do localStorage antes {antes} · depois {depois}")
    if perfil == 'Ana': s.shot('p2_PL-05_notificar.png')
s.go('PL-05.dc.html', espera=1.2)
fila = s.J("(()=>{const g=[...document.querySelectorAll('table')].find(t=>t.innerText.includes('Causa'));return g?g.innerText.replace(/\\s+/g,' ').slice(0,900):'';})()")
s.p(f"   fila (texto): {fila}")
s.p('\n# EX-40.5 · Manutenções e impacto na produção em PL-03 e PL-04')
txt = {}
for f in ('PL-03.dc.html', 'PL-04.dc.html'):
    s.go(f, espera=1.2)
    d = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim();
      const h=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&n(e.textContent)==='Manutenções e impacto na produção')[0];
      if(!h) return null; let sec=h;
      while(sec.parentElement&&!/Corretiva OM-0233/.test(sec.innerText)) sec=sec.parentElement;
      return {h1:n((document.querySelector('h1')||{}).innerText), y:Math.round(h.getBoundingClientRect().top+scrollY), txt:n(sec.innerText).slice(0,1500), acoes:[...sec.querySelectorAll('button,a,[role=menuitem]')].map(b=>n(b.innerText||b.getAttribute('aria-label'))).filter(Boolean)};})()""")
    txt[f] = d
    s.p(f"{f}: {json.dumps(d, ensure_ascii=False)[:1800]}")
if txt.get('PL-03.dc.html') and txt.get('PL-04.dc.html'):
    a, b = txt['PL-03.dc.html']['txt'], txt['PL-04.dc.html']['txt']
    s.p(f"\nmesmo texto do bloco nas duas telas: {a == b} · tamanho {len(a)} × {len(b)}")
s.p(f"erros JS: {s.errs()}")
s.fim('p2_planej.log')
