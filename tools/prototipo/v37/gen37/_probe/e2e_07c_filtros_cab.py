# -*- coding: utf-8 -*-
"""Passo 7c · o cabeçalho (resumo de estado e ação primária) acompanha o filtro Fazenda/Safra em OS e EST?"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
FZ = 'select[aria-label="Filtrar por fazenda"]'; SF = 'select[aria-label="Filtrar por safra"]'
H = lambda: b.J("(()=>{const h=document.querySelector('header'); const t=h.innerText; const i=t.lastIndexOf('›'); return t.slice(i).replace(/\\s+/g,' ');})()")
HB = lambda: b.J("[...document.querySelectorAll('header button')].filter(x=>x.offsetParent!==null).map(x=>x.innerText.trim())")
b.goto('OS.dc.html'); print('   OS Santa Rita:', H(), HB())
b.setv(FZ, 'Boa Vista'); time.sleep(.3); h = H(); hb = HB(); print('   OS Boa Vista:', h, hb)
b.ok('em execução' not in h and 'impedidas' not in h, 'O.S. · Boa Vista: resumo do cabeçalho não conta ordens da Santa Rita', h)
b.setv(FZ, 'Santa Rita'); b.setv(SF, '2025/26'); time.sleep(.3); h = H(); print('   OS 2025/26:', h, HB())
b.ok('em execução' not in h and 'impedidas' not in h, 'O.S. · safra 2025/26 (só encerradas): resumo não conta ordens de 2026/27', h)
b.setv(SF, 'Todas'); time.sleep(.3)
b.goto('EST.dc.html'); print('   EST Santa Rita:', H(), HB())
b.setv(FZ, 'Boa Vista'); time.sleep(.3); h = H(); hb = HB(); print('   EST Boa Vista:', h, hb)
b.ok(not any('NF' in x for x in hb), 'Estoque · Boa Vista: sem ação "Conferir NF" da Santa Rita no cabeçalho', hb)
b.setv(FZ, 'Todas'); time.sleep(.3); m = b.main(); print('   EST Todas:', H(), m[:250])
b.setv(FZ, 'Santa Rita'); time.sleep(.3)
b.goto('OS.dc.html'); b.setv(FZ, 'Todas'); time.sleep(.3); n = b.J("[...document.querySelectorAll('[role=row].g2ed')].length"); print('   OS Todas:', n, H())
b.setv(FZ, 'Santa Rita'); time.sleep(.3)
b.fim()
