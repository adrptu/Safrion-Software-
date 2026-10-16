# -*- coding: utf-8 -*-
"""EX-40.9 · ações destrutivas fora do ⋯: "Encerrar saldo" (VEN), "Cancelar reserva" (VEN/PROD), "Cancelar sem execução" (O.S.) · executado.
Para cada uma: onde está (à vista, ⋯), o que pede antes de gravar (motivo, confirmação), quantos cliques, se há desfazer, e o estado depois."""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e40lib import S, clique, BTN, BTNC
PAINEL = "([...document.querySelectorAll('aside[role=dialog],[role=dialog],aside')].find(e=>e.getClientRects().length&&e.innerText.length>40))"
def anat(s, alvo):
    """botões visíveis do painel: texto, verde?, vermelho?, dentro de ⋯?, distância ao alvo"""
    return s.J(f"""(()=>{{const P={PAINEL}; if(!P) return null; const n=x=>(x||'').replace(/\\s+/g,' ').trim();
      const bs=[...P.querySelectorAll('button,a,summary')].filter(b=>b.getClientRects().length);
      const A=bs.find(b=>n(b.innerText).startsWith({json.dumps(alvo)})); const ra=A?A.getBoundingClientRect():null;
      return {{mais:[...P.querySelectorAll('[aria-haspopup=menu],summary')].filter(b=>b.getClientRects().length).map(b=>b.getAttribute('aria-label')||n(b.innerText)),
        alvo:A?{{t:n(A.innerText),cor:getComputedStyle(A).color,fundo:getComputedStyle(A).backgroundColor,dentroMenu:!!A.closest('[role=menu]')}}:null,
        prim:bs.filter(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>{{const r=b.getBoundingClientRect(); return {{t:n(b.innerText),dist:ra?Math.round(Math.hypot(r.left-ra.left,r.top-ra.top)):null}};}}),
        sec:bs.filter(b=>getComputedStyle(b).backgroundColor!=='rgb(30, 122, 76)'&&b.tagName==='BUTTON').map(b=>n(b.innerText||b.getAttribute('aria-label'))).filter(Boolean).slice(0,14)}};}})()""")
def digita(s, sel, txt):
    clique(s, sel, .3); s.c.call('Input.insertText', {'text': txt}); time.sleep(.3)
s = S(); s.reset('Ana')
s.p('# EX-40.9 · ações destrutivas (render b87f79b, Ana · gestora; dados sintéticos)')
# ---- 1. Encerrar saldo (VEN · PV-030)
s.go('VEN.dc.html#PV-030', espera=2.0); time.sleep(.8)
s.p('\n## 1. VEN · PV-030 · "Encerrar saldo"'); s.p(json.dumps(anat(s, 'Encerrar saldo'), ensure_ascii=False))
s.shot('p6_VEN_PV-030.png'); s.cliques = 0
r1 = clique(s, BTNC('Encerrar saldo', PAINEL)); form = s.J(f"{PAINEL}.innerText.replace(/\\s+/g,' ').slice(0,500)")
s.p(f"  clique 1 ({r1}) → {form[:400]!r}")
r2 = clique(s, BTN('Encerrar saldo', PAINEL)); t = s.toast()
s.p(f"  clique 2 sem motivo ({r2}) → {t!r}")
digita(s, f"{PAINEL}.querySelector('input,textarea')", 'teste sintético EX-40')
r3 = clique(s, BTN('Encerrar saldo', PAINEL), 1.0); t = s.toast(); st = s.J(f"{PAINEL}?{PAINEL}.innerText.replace(/\\s+/g,' ').slice(0,300):''")
s.p(f"  clique 3 com motivo ({r3}) → {t!r}")
s.p(f"  painel depois: {st!r} · cliques {s.cliques} · digitação 1 campo")
desf = s.J(f"(()=>{{const P={PAINEL}; if(!P) return []; return [...P.querySelectorAll('button')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim()).filter(t=>/Desfazer|Reabrir|Retomar/.test(t));}})()")
s.p(f"  desfazer/reabrir à vista: {desf}")
# ---- 2. Cancelar reserva (VEN · PV-030 · RS-0001)
s.reset('Ana'); s.go('VEN.dc.html#PV-030', espera=2.0); time.sleep(.8)
s.p('\n## 2. VEN · PV-030 · reserva RS-0001 · "Cancelar reserva"')
lin = s.J(f"(()=>{{const P={PAINEL}; if(!P) return null; const b=[...P.querySelectorAll('button,a')].find(x=>x.getClientRects().length&&x.innerText.trim()==='Cancelar reserva'); if(!b) return null; let r=b.parentElement; while(r&&r.innerText.length<30) r=r.parentElement; return {{linha:r.innerText.replace(/\\s+/g,' ').slice(0,200),cor:getComputedStyle(b).color,menu:!!b.closest('[role=menu]')}};}})()")
s.p(f"  linha: {lin}"); s.cliques = 0
r1 = clique(s, BTN('Cancelar reserva', PAINEL)); form = s.J(f"{PAINEL}.innerText.replace(/\\s+/g,' ').slice(0,400)")
s.p(f"  clique 1 ({r1}) → {form[:300]!r}")
digita(s, f"{PAINEL}.querySelector('input,textarea')", 'teste sintético EX-40')
r2 = clique(s, BTNC('Cancelar RS-0001', PAINEL), 1.0); t = s.toast()
st = s.J(f"(()=>{{const P={PAINEL}; return P?(P.innerText.match(/RS-0001[^\\n]{{0,120}}/)||[''])[0]:'';}})()")
s.p(f"  clique 2 com motivo ({r2}) → {t!r} · linha depois {st!r} · cliques {s.cliques}")
s.go('PROD.dc.html#L10-031', espera=2.0); time.sleep(.8)
disp = s.J(f"{PAINEL}?{PAINEL}.innerText.replace(/\\s+/g,' ').slice(0,400):document.body.innerText.slice(0,200)")
s.p(f"  PROD · L10-031 depois: {disp[:300]!r}")
# ---- 3. Cancelar sem execução (O.S. · OS-0431 A liberar)
s.reset('Ana'); s.go('OS.dc.html#OS-0431', espera=2.2); time.sleep(.8)
s.p('\n## 3. O.S. · OS-0431 · "Cancelar sem execução"'); s.p(json.dumps(anat(s, 'Cancelar sem execução'), ensure_ascii=False))
s.shot('p6_OS-0431_painel.png'); s.cliques = 0
r1 = clique(s, BTN('Cancelar sem execução', PAINEL)); form = s.J(f"{PAINEL}.innerText.replace(/\\s+/g,' ').slice(0,1200)")
s.p(f"  clique 1 ({r1}) → {form[-500:]!r}")
r2 = clique(s, BTNC('Confirmar cancelamento', PAINEL)); t = s.toast()
s.p(f"  clique 2 sem motivo ({r2}) → {t!r}")
digita(s, f"{PAINEL}.querySelector('textarea[aria-label=\"Motivo do cancelamento\"]')", 'teste sintético EX-40')
r3 = clique(s, BTNC('Confirmar cancelamento', PAINEL), 1.2); t = s.toast()
st = s.J(f"{PAINEL}?{PAINEL}.innerText.replace(/\\s+/g,' ').slice(0,300):''")
s.p(f"  clique 3 com motivo ({r3}) → {t!r}")
s.p(f"  painel depois: {st!r} · cliques {s.cliques}")
s.p(f"erros JS: {s.errs()}")
s.fim('p6_destrutivas.log')
