# -*- coding: utf-8 -*-
"""Passo 10 · IN-02 (Aprovações) e IN-04 (cabeçalho) depois de aprovar a OS-0430 na tela O.S.: a decisão sai da fila."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
LS = "JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null')"
st = b.J(f"(()=>{{const c={LS}; return c?[c.ordens['OS-0430'].etapa, c.ordens['OS-0430'].aprov]:null;}})()"); print('   cenário:', st)
b.goto('IN-02.dc.html'); rows = b.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,140))") or []
hdr = b.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')"); print('   IN-02 cabeçalho:', hdr[-160:]); [print('   ', r) for r in rows]
r430 = [r for r in rows if 'OS-0430' in r]
b.ok(not r430 or all(('Pendente' not in r) for r in r430), 'IN-02 · OS-0430 aprovada na tela O.S. não aparece como pendente', r430)
b.goto('IN-01.dc.html'); m = b.main(); i = m.find('OS-0430'); print('   IN-01 OS-0430:', m[max(0, i - 120):i + 200] if i >= 0 else '(ausente)')
b.ok(i < 0 or 'Aguardando agrônomo' not in m[max(0, i - 120):i + 200], 'IN-01 (Início) não mostra a OS-0430 aguardando o agrônomo', m[max(0, i - 120):i + 200])
b.goto('IN-03.dc.html'); m = b.main(); i = m.find('OS-0430'); print('   IN-03 OS-0430:', m[max(0, i - 150):i + 200] if i >= 0 else '(ausente)')
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
