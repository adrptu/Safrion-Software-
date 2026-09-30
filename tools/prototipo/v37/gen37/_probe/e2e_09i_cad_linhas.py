# -*- coding: utf-8 -*-
"""Passo 9i · 7 cadastros: abrir a 1ª linha de cada tabela (formulário lateral) e o botão primário (formulário novo); erros de JS.
Mais: caldeiro sem NR-31 grava como não alocável e o cabeçalho do CD-04 conta."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, marcar
b = B(); b.size(1440, 1000)
for t, prim in (('CD-01', 'Cadastrar talhão'), ('CD-01det', None), ('CD-02', 'Cadastrar cultivar'), ('CD-03', 'Cadastrar máquina ou instalação'), ('CD-04', 'Cadastrar pessoa'), ('CD-05', 'Cadastrar parceiro'), ('CD-06', 'Cadastrar item'), ('CD-07', 'Cadastrar código')):
    b.goto(t + '.dc.html')
    r = b.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.offsetParent!==null); if(!r) return 'sem linha'; r.scrollIntoView({block:'center'}); (r.querySelector('[role=cell] span')||r).click(); return r.innerText.split('\\n')[0];})()"); time.sleep(.4)
    a1 = b.J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText")
    b.clk('Cancelar', 'aside[role=dialog]'); b.clk('Descartar alterações', 'aside[role=dialog]'); b.clk('Fechar', 'aside[role=dialog]')
    a2 = ''
    if prim:
        b.clk(prim); a2 = b.J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText")
        b.clk('Cancelar', 'aside[role=dialog]'); b.clk('Descartar alterações', 'aside[role=dialog]')
    er = b.erros(); print(f'   {t}: linha={r!r} → {a1!r} | primário → {a2!r} | erros={er}')
    b.ok(bool(a1) and (not prim or bool(a2)) and not er, f'{t}: linha e primário abrem o formulário lateral, sem erro de JS', (r, a1, a2, er))
b.goto('CD-04.dc.html'); h0 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
b.clk('Cadastrar pessoa'); b.setv('#fx_g_pes_nome', 'Beto Lima'); marcar(b, 'Preparar calda (caldeiro)'); b.setv('#fx_g_pes_adm', '2026-09-01')
b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); h1 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
print('   sem NR-31:', t, '|', h0, '→', h1, '|', b.rowtxt('Beto Lima'))
b.ok('não alocável' in t.lower() or 'Não alocável' in b.rowtxt('Beto Lima') or 'não alocável' in b.rowtxt('Beto Lima'), 'CD-04 · caldeiro sem NR-31 grava como não alocável', (t, b.rowtxt('Beto Lima')))
b.ok(h0 != h1, 'CD-04 · cabeçalho recalcula "não alocáveis"', (h0, h1))
b.fim()
