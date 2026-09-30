# -*- coding: utf-8 -*-
"""Passo 9j · CD-02 e CD-06 (linha de dados, não o grupo) e CD-04 caldeiro sem NR-31 (com os alertas)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, marcar
b = B(); b.size(1440, 1000)
for t in ('CD-02', 'CD-06'):
    b.goto(t + '.dc.html')
    r = b.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.offsetParent!==null && !r.classList.contains('g2grp') && r.innerText.trim()[0]!=='▾'); if(!r) return 'sem linha'; r.scrollIntoView({block:'center'}); (r.querySelector('[role=cell] span')||r).click(); return r.innerText.split('\\n')[0];})()"); time.sleep(.4)
    a1 = b.J("(document.querySelector('aside[role=dialog] h2')||{innerText:''}).innerText"); er = b.erros()
    print(f'   {t}: linha={r!r} → {a1!r} erros={er}')
    b.ok(bool(a1) and not er, f'{t}: linha de dados abre o formulário lateral', (r, a1))
b.goto('CD-04.dc.html'); h0 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
b.clk('Cadastrar pessoa'); b.setv('#fx_g_pes_nome', 'Beto Lima'); marcar(b, 'Preparar calda (caldeiro)'); b.setv('#fx_g_pes_adm', '2026-09-01')
b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); al = b.alerts('aside[role=dialog]'); aberto = b.J("!!document.querySelector('aside[role=dialog]')")
h1 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
print('   sem NR-31:', t, '| alertas:', al, '| aberto:', aberto, '|', h0, '→', h1, '|', b.rowtxt('Beto Lima'))
b.setv('#fx_g_pes_custo', '30'); b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); aberto = b.J("!!document.querySelector('aside[role=dialog]')")
h1 = b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))"); lin = b.rowtxt('Beto Lima')
print('   com custo:', t, '| aberto:', aberto, '|', h0, '→', h1, '|', lin)
b.ok(not aberto and 'Beto Lima' in lin and ('não alocável' in (t + lin).lower()), 'CD-04 · caldeiro sem NR-31 grava como não alocável', (t, lin))
b.ok(h0 != h1 and h1 and h1.startswith('3 não alocáveis'), 'CD-04 · cabeçalho passa a 3 não alocáveis', (h0, h1))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
