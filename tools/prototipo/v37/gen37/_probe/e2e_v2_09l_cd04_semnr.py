# -*- coding: utf-8 -*-
"""v2 · 9l · CD-04: caldeiro sem validade da NR-31 grava como não alocável e o cabeçalho recalcula."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, marcar
b = B(); b.size(1440, 1000); b.goto('CD-04.dc.html')
H = lambda: b.J("[...document.querySelectorAll('header button, header a')].map(x=>x.innerText.trim()).find(t=>/não aloc/.test(t))")
h0 = H(); b.clk('Cadastrar pessoa'); b.setv('#fx_g_pes_nome', 'Beto Lima'); marcar(b, 'Preparar calda (caldeiro)'); b.setv('#fx_g_pes_adm', '2026-09-01'); b.setv('#fx_g_pes_custo', '32')
b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); al = b.alerts('aside[role=dialog]'); h1 = H(); lin = b.rowtxt('Beto Lima')
print('   salvar:', t, '| alertas:', al, '|', h0, '→', h1, '| linha:', lin)
b.ok('não alocável' in (t + lin).lower(), 'CD-04 · caldeiro sem NR-31 grava como não alocável', (t, lin))
b.ok(h0 != h1, 'CD-04 · cabeçalho recalcula "não alocáveis"', (h0, h1))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
