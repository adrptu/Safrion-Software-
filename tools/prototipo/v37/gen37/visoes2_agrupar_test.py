# -*- coding: utf-8 -*-
"""VISOES-2 §3.3 · "Agrupar por" no navegador: a trilha com "/" (Safra 2026/27) sobrevive ao endereço e à recarga com os mesmos IDs
(Codex 6168779649, achado 1). O filtro de Talhão nos grupos está na unidade (visoes2_ag_unit.js A4–A7). Dados sintéticos; render em RENDER_DIR."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:400], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
B = f'http://127.0.0.1:{p}/OS.dc.html'
def trilha(): return J("(()=>{const n=document.querySelector('[data-g2agtr=g_os]'); return n?n.innerText.split(/[›\\n]+/).map(x=>x.trim()).filter(Boolean):[]})()") or []
def ids(): return sorted(set(x.split('@')[0] for x in (J("[...document.querySelectorAll('[data-g2g=g_os] [data-rid]')].filter(e=>e.offsetParent).map(e=>e.getAttribute('data-rid'))") or []) if not x.startswith('grp@')))
try:
    c.aparelho(1440, 900, 1, False)
    c.goto(B, .8); J("localStorage.clear();sessionStorage.clear()"); c.goto(B + '?view=lista&ag=quando', 1.6)
    J("[...document.querySelectorAll('[data-g2g=g_os] button')].find(b=>b.getAttribute('aria-label')==='Descer em Safra 2026/27 (safra)').click()"); time.sleep(.6)
    t0, i0, q0 = trilha(), ids(), J("location.search")
    chk('G1 descer em "Safra 2026/27": a trilha mostra a safra inteira e o endereço leva %2F', any(x == 'Safra 2026/27' for x in t0) and 'trilha=Safra%202026%2F27' in q0 and len(i0) > 0, [t0, q0, i0])
    c.goto(B + '?view=lista', 1.6)
    chk('G2 sem ag no endereço, a escolha volta pela preferência salva: mesma trilha e mesmos IDs', trilha() == t0 and ids() == i0, [trilha(), t0, ids(), i0])
    J("Object.keys(localStorage).filter(k=>k.startsWith('g2ag:')).forEach(k=>localStorage.removeItem(k))")
    c.goto(B + q0, 1.6)
    chk('G3 recarregar só pelo endereço (preferência apagada) volta à mesma trilha e aos mesmos IDs', trilha() == t0 and ids() == i0, [trilha(), t0, ids(), i0])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
