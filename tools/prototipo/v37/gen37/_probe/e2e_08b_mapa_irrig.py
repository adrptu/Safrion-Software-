# -*- coding: utf-8 -*-
"""Passo 8b · IN-04 camada Irrigação › Programação de hoje: T7 conflito B3, P2 OS-0419/0422 sem exceção de água."""
import sys, os, time, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 900); b.goto('IN-04.dc.html')
print('  ', b.clk('Irrigação'), b.clk('Programação de hoje'))
SV = "[...document.querySelectorAll('svg [role=button]')]"
lab = b.J(f"{SV}.map(e=>e.getAttribute('aria-label'))"); print('   polígonos:', lab)
def pan(t):
    b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
    p = b.J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{innerText:''}}).innerText") or ''
    b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.3)
    return p.replace('\n', ' / ')
t7 = pan('T7'); p2 = pan('P2'); p1 = pan('P1'); print('   T7:', t7[:400]); print('   P2:', p2[:500]); print('   P1:', p1[:400])
body = b.body(); bad = [m for m in re.findall(r'.{60}(?:Fora da política|PA-07|exceç\w*|política).{40}', body.replace('\n', ' '), re.I)]
b.ok(any('B3' in (l or '') for l in lab) and 'B3' in t7, 'T7: conflito com a parada da B3 no mapa', (lab, t7[:200]))
b.ok('6,75' in p2 or '13,5' in p2 or 'Janela a definir' in p2, 'P2: OS-0422 com janela a definir / passadas', p2[:300])
b.ok(not bad, 'camada Irrigação sem política/exceção de água', bad[:3])
b.ok('agrônom' in p1.lower() or 'OS-0418' in p1, 'P1: OS-0418 fertirrigação aguardando decisão', p1[:300])
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
