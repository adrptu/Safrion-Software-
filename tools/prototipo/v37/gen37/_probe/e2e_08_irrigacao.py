# -*- coding: utf-8 -*-
"""Passo 8 · irrigação só com água sem agrônomo, coerente em OS, IN-02, IN-04 (camada Irrigação), PL-04, IR-02 e MB-08 (texto renderizado)."""
import sys, os, time, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B()
PROIB = re.compile(r'Fora da política|PA-07|exceç\w*|política de água|revisão individual', re.I)
def proib(txt):
    out = []
    for m in PROIB.finditer(txt):
        ctx = txt[max(0, m.start() - 90):m.end() + 60].replace('\n', ' ')
        if re.search(r'fertirriga', ctx, re.I): continue
        out.append(ctx)
    return out
def todo_texto():
    # inclui o texto dos formulários e painéis que já estão no DOM
    return b.J("document.body.innerText") or ''
res = {}
for t, w, h in (('OS.dc.html', 1440, 1000), ('IN-02.dc.html', 1440, 1000), ('PL-04.dc.html', 1440, 1000), ('IR-02.dc.html', 1440, 1000), ('MB-08.dc.html', 390, 1500)):
    b.size(w, h); b.goto(t); txt = todo_texto(); p = proib(txt); res[t] = txt
    print(f'   {t}: proibidos={p[:3]} erros={b.erros()}')
    b.ok(not p and not b.erros(), f'{t}: sem "Fora da política", PA-07 ou exceção de água; sem erro de JS', p[:3])
# O.S.: abrir OS-0422 e OS-0423 e ler o painel
b.size(1440, 1000); b.goto('OS.dc.html')
b.row('OS-0422'); p22 = b.aside(); b.clk('Fechar', 'aside[role=dialog]')
b.row('OS-0423'); p23 = b.aside(); b.clk('Fechar', 'aside[role=dialog]')
b.row('OS-0418'); p18 = b.aside()
print('   OS-0422:', p22[:420]); print('   OS-0423:', p23[:420]); print('   OS-0418:', p18[:300])
b.ok('13,5 mm' in p22 and '2 passadas' in p22 and '6,75 mm' in p22 and 'a definir' in p22.lower() and not proib(p22) and 'agrônom' not in p22.lower(),
     'O.S. · OS-0422: 13,5 mm em 2 passadas de 6,75 mm, janela a definir, sem agrônomo', p22[:400])
b.ok('B3' in p23 and 'ET' in p23 and not proib(p23) and 'agrônom' not in p23.lower(), 'O.S. · OS-0423: conflito com a parada da B3, estimativa por ET, sem agrônomo', p23[:400])
b.ok('agrônom' in p18.lower() and 'Fertirriga' in p18, 'O.S. · OS-0418 (fertirrigação) aguarda o agrônomo', p18[:300])
# IN-02: fila de aprovações
b.goto('IN-02.dc.html'); rows = b.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0])") or []
print('   IN-02 linhas:', rows)
b.ok(not any(('0419' in r or '0422' in r or '0423' in r) for r in rows) and any('0418' in r for r in rows), 'IN-02 · Aprovações sem OS-0419/0422/0423 (só água) e com OS-0418 (fertirrigação)', rows)
# IN-04: camada Irrigação
b.size(1440, 900); b.goto('IN-04.dc.html'); b.clk('Irrigação'); txt = b.body(); p = proib(txt)
lab = b.J("[...document.querySelectorAll('svg [role=button]')].map(e=>e.getAttribute('aria-label'))"); print('   IN-04 irrigação:', lab, p[:2])
b.ok(not p and any('B3' in (l or '') for l in lab), 'IN-04 · camada Irrigação sem exceção de água; T7 com conflito da B3', (lab, p[:2]))
b.shot('e2e_08_in04_irrig.png')
b.fim()
