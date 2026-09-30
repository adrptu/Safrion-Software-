# -*- coding: utf-8 -*-
"""Itens 3 e 4 · IN-04, camada Irrigação: a programação de hoje mostra a mesma janela e duração do IR-02 e do PL-04 (OS-0419 e OS-0418)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
b.goto('IN-04.dc.html', wait=1.2)
print('   camada:', b.clk('Irrigação'))
body = b.body(); print('   tem Kanban:', 'Kanban' in body)
SV = "[...document.querySelectorAll('svg [role=button]')]"
res = {}
for t in ('P2', 'P1'):
    b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
    p = b.J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{innerText:''}}).innerText") or ''
    res[t] = p.replace('\n', ' / '); print('  ', t, ':', res[t][:700])
b.ok('hoje 20:00–amanhã 10:31' in res['P2'] and '14,5 h' in res['P2'], 'IN-04 P2: OS-0419 hoje 20:00–amanhã 10:31 (14,5 h), igual ao IR-02', res['P2'][:300])
b.ok('24/09 21:00–25/09 11:15' in res['P1'] and '14,3 h' in res['P1'] and '05:00' not in res['P1'], 'IN-04 P1: OS-0418 24/09 21:00–25/09 11:15 (14,3 h), igual ao IR-02 e PL-04', res['P1'][:300])
b.goto('PL-04.dc.html'); r18, r19 = b.rowtxt('OS-0418'), b.rowtxt('OS-0419'); print('   PL-04:', r18, '|', r19)
b.ok('24/09 21:00–25/09 11:15' in r18 and '14,3 h' in r18, 'PL-04 OS-0418 com a mesma janela e 14,3 h', r18)
b.ok('hoje 20:00–amanhã 10:31' in r19 and '14,5 h' in r19, 'PL-04 OS-0419 com a mesma janela e 14,5 h', r19)
b.goto('IR-02.dc.html'); a18, a19 = b.rowtxt('OS-0418'), b.rowtxt('OS-0419'); print('   IR-02:', a18, '|', a19)
b.ok('24/09 21:00–25/09 11:15' in a18 and '14,3 h' in a18 and 'hoje 20:00–amanhã 10:31' in a19 and '14,5 h' in a19, 'IR-02 com as mesmas janelas e durações', (a18, a19))
b.goto('OS.dc.html'); o18, o19 = b.rowtxt('OS-0418'), b.rowtxt('OS-0419'); print('   OS:', o18, '|', o19)
b.ok('24/09 21:00–25/09 11:15' in o18 and 'hoje 20:00–amanhã 10:31' in o19, 'OS.dc.html com as mesmas janelas', (o18, o19))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
