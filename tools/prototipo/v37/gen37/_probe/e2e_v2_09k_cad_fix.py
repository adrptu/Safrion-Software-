# -*- coding: utf-8 -*-
"""v2 · 9k · CD-02 e CD-06: abrir uma linha de dados (não o grupo); CD-04: caldeiro sem NR-31 (alertas ao salvar)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, marcar, campos
b = B(); b.size(1440, 1000)
for t in ('CD-02', 'CD-06'):
    b.goto(t + '.dc.html')
    r = b.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent!==null).find(r=>!/^\\s*▾/.test(r.innerText)&&r.querySelectorAll('[role=cell]').length>2); if(!r) return 'sem linha'; r.scrollIntoView({block:'center'}); (r.querySelector('[role=cell] span')||r).click(); return r.innerText.replace(/\\s+/g,' ').slice(0,80);})()"); time.sleep(.4)
    a1 = b.J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText"); er = b.erros()
    print(f'   {t}: linha={r!r} → {a1!r} | erros={er}')
    b.ok(bool(a1) and not er, f'{t}: linha de dados abre o formulário lateral', (r, a1, er))
    b.clk('Cancelar', 'aside[role=dialog]'); b.clk('Descartar alterações', 'aside[role=dialog]')
b.goto('CD-04.dc.html'); h0 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
b.clk('Cadastrar pessoa'); b.setv('#fx_g_pes_nome', 'Beto Lima'); print('   marcar:', marcar(b, 'Preparar calda (caldeiro)')); b.setv('#fx_g_pes_adm', '2026-09-01')
for f in campos(b): print('   campo:', f['id'], '|', f['lab'][:40], '|', f['val'])
b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); al = b.alerts('aside[role=dialog]'); aberto = b.J("!!document.querySelector('aside[role=dialog]')")
h1 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
print('   salvar:', t, '| alertas:', al, '| aberto:', aberto, '|', h0, '→', h1, '|', b.rowtxt('Beto Lima'))
b.fim()
