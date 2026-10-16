# -*- coding: utf-8 -*-
"""EX-40.10 · MB-06 "Concluir com 9 de 14 pontos": o que o toque faz, o dano (o que fica concluído sem os 5 pontos) e se volta atrás · executado.
App a 390 × 844 com toque; depois AG-01 e PAGR a 1440 (perfil Ana)."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, BTN, BTNC, _centro
def toca(s, sel, w=.7):
    xy = _centro(s, sel)
    if not xy: return 'NÃO ACHEI'
    s.cliques = getattr(s, 'cliques', 0) + 1; s.c.toque(*xy); time.sleep(w); return 'ok'
s = S(390, 844, toque=True); s.reset('Ana')
s.go('MB-06.dc.html#VIS-014', espera=2.0); time.sleep(.6)
s.p('# EX-40.10 · MB-06 · VIS-014 (P1 feijão · ácaro · Marcos), 390 × 844 com toque')
d = s.J("""(()=>{const n=x=>(x||'').replace(/\\s+/g,' ').trim(); const bs=[...document.querySelectorAll('button,a')].filter(b=>b.getClientRects().length);
  const C=bs.find(b=>/^Concluir com/.test(n(b.innerText))); const P=bs.filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)');
  const box=e=>{const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)];};
  return {cab:n((document.querySelector('h1')||{}).innerText)+' · '+n(document.body.innerText).slice(0,260), concluir:C?{t:n(C.innerText),box:box(C),dica:C.title}:null,
    prim:P.map(b=>({t:n(b.innerText),box:box(b)}))};})()""")
s.p(json.dumps(d, ensure_ascii=False)); s.shot('p7_MB-06_antes.png')
s.cliques = 0
r = toca(s, BTNC('Concluir com')); t = s.toast()
cab = s.J("(document.body.innerText||'').replace(/\\s+/g,' ').slice(0,420)")
dlg = bool(s.J("!!document.querySelector('[role=alertdialog]')"))
s.p(f"\ntoque em 'Concluir com …' ({r}) · cliques {s.cliques} · confirmação pedida? {dlg}")
s.p(f"  aviso: {t!r}"); s.p(f"  tela depois: {cab!r}"); s.shot('p7_MB-06_depois.png')
s.go('MB-06.dc.html#VIS-014', espera=2.0); time.sleep(.6)
reab = s.J("(document.body.innerText||'').replace(/\\s+/g,' ').slice(0,300)")
s.p(f"  reabrindo MB-06#VIS-014: {reab!r}")
s.fim()
s = S(1440, 1000); s.go('Main.dc.html')   # mesmo origin: o estado do MIP (localStorage) não é compartilhado entre perfis de navegador; refaz no 1440
s.J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Ana'); 1")
s.go('MB-06.dc.html#VIS-014', espera=2.0); time.sleep(.5); clique_r = s.J(f"(()=>{{const b={BTNC('Concluir com')}; if(!b) return 'sem botão'; b.click(); return 'ok';}})()"); time.sleep(.8)
s.p(f"\n# 1440 (Ana) · concluída a VIS-014 com 9 de 14 ({clique_r}); AG-01 e PAGR")
s.go('AG-01.dc.html#VIS-014', espera=2.0); time.sleep(1.0)
pan = s.J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog],aside')].find(e=>e.getClientRects().length&&/VIS-014/.test(e.innerText)); return d?d.innerText.replace(/\\s+/g,' ').slice(0,1400):'(sem painel) '+(document.body.innerText.match(/VIS-014[^\\n]{0,200}/)||[''])[0];})()")
s.p(f"AG-01 · VIS-014: {pan!r}")
bts = s.J("(()=>{const d=[...document.querySelectorAll('aside[role=dialog],[role=dialog],aside')].find(e=>e.getClientRects().length&&/VIS-014/.test(e.innerText)); return d?[...d.querySelectorAll('button,a')].filter(b=>b.getClientRects().length).map(b=>(b.innerText||b.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim()).filter(Boolean):[];})()")
s.p(f"  ações no painel: {bts}"); s.shot('p7_AG-01_VIS-014.png')
s.go('PAGR.dc.html', espera=2.0); time.sleep(.8)
pg = s.J("(document.body.innerText.match(/VIS-014[^\\n]{0,160}/g)||[]).slice(0,3)")
s.p(f"PAGR · linhas com VIS-014: {pg}")
s.p(f"erros JS: {s.errs()}")
s.fim('p7_mb06.log')
