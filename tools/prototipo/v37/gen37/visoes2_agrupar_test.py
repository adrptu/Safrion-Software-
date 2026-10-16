# -*- coding: utf-8 -*-
"""VISOES-2 §3.3 com AGR-02 (16/10/2026, proprietário: "tire esse todas => santa rita por talhão em todas telas. essa funcao ja esta nos
filtros e no agrupamento"): o Agrupar por agrupa e a seta recolhe; o nome do grupo não desce e não há trilha. Um endereço antigo com trilha
(Safra 2026/27, com "/") não recorta mais nada; a escolha do agrupamento volta pela preferência. Antes (até 15/10) este teste provava a trilha
com "/" (Codex 6168779649, achado 1). Dados sintéticos; render em RENDER_DIR."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir, agrupar_por

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
    c.goto(B, .8); J("localStorage.clear();sessionStorage.clear()"); c.goto(B + '?view=lista', 1.6); i_todas = ids()
    c.goto(B + '?view=lista&ag=quando', 1.6)
    desce = J("[...document.querySelectorAll('[data-g2g=g_os] button')].filter(b=>/^Descer em/.test(b.getAttribute('aria-label')||'')).length")
    grupos = J("[...document.querySelectorAll('[data-g2g=g_os] [data-rid^=\"grp@\"]')].length")
    chk('G1 Agrupar por Quando: grupos com a seta, sem botão de descer no nome e sem trilha', grupos > 0 and desce == 0 and trilha() == [] and ids() == i_todas, [grupos, desce, trilha(), ids(), i_todas])
    c.goto(B + '?view=lista&ag=quando&trilha=Safra%202026%2F27', 1.6)
    chk('G2 endereço antigo com trilha (Safra 2026/27) não recorta: as mesmas O.S. e nenhuma trilha', trilha() == [] and ids() == i_todas, [trilha(), ids(), i_todas])
    c.goto(B + '?view=lista', 1.6); J("Object.keys(localStorage).filter(k=>k.startsWith('g2ag:')).forEach(k=>localStorage.removeItem(k))"); c.goto(B + '?view=lista', 1.6)
    r3 = agrupar_por(J, 'Talhão', 'g_os'); c.goto(B + '?view=lista', 1.6)   # escolher no menu grava a preferência (o endereço só não grava)
    g3 = J("[...document.querySelectorAll('[data-g2g=g_os] [data-rid^=\"grp@\"]')].length")
    chk('G3 escolhido no menu (Talhão), o agrupamento volta pela preferência ao recarregar, com as mesmas O.S. e sem trilha', r3 == 'ok' and g3 > 0 and ids() == i_todas and trilha() == [], [r3, g3, ids(), i_todas])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
