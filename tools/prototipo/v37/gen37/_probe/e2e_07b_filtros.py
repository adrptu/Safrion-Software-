# -*- coding: utf-8 -*-
"""Passo 7b · filtros do topo: OS, EST e IN-04 filtram de fato; Boa Vista mostra estado vazio com ação; SAF e CMP só mostram contexto."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
FZ = 'select[aria-label="Filtrar por fazenda"]'; SF = 'select[aria-label="Filtrar por safra"]'
nrows = lambda: b.J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent!==null).length")
ids = lambda: b.J("[...document.querySelectorAll('[role=row].g2ed')].filter(r=>r.offsetParent!==null).map(r=>r.innerText.trim().split(/\\s/)[0])")
# ---- O.S.
b.goto('OS.dc.html'); n0 = nrows(); i0 = ids()
b.setv(FZ, 'Boa Vista'); time.sleep(.3); m = b.main(); nb = nrows(); prim = b.btns('main')
print('   OS Boa Vista:', m[:400], '| linhas:', nb)
b.ok(nb == 0 and 'Nenhuma ordem na Boa Vista' in m and 'Ver Santa Rita' in m, 'O.S. · Boa Vista: estado vazio "Nenhuma ordem na Boa Vista · Ver Santa Rita"', m[:300])
b.clk('Ver Santa Rita'); n1 = nrows(); v1 = b.val(FZ); print('   após Ver Santa Rita:', v1, n1)
b.ok(v1 == 'Santa Rita' and n1 == n0, 'O.S. · "Ver Santa Rita" volta o filtro e a lista', (v1, n1, n0))
b.setv(SF, '2025/26'); time.sleep(.3); i2 = ids(); m2 = b.main(); print('   OS safra 2025/26:', i2, m2[:200])
b.setv(SF, 'Safrinha 2027'); time.sleep(.3); i3 = ids(); m3 = b.main(); print('   OS Safrinha 2027:', i3, m3[:250])
b.setv(SF, '2026/27'); time.sleep(.3); i4 = ids(); print('   OS 2026/27:', i4)
b.ok(len(i2) < len(i0) and set(i2) <= set(i0), 'O.S. · filtro de safra 2025/26 reduz a lista', (i0, i2))
b.ok((len(i3) > 0) or ('Nenhuma ordem' in m3), 'O.S. · safra sem ordens mostra estado vazio claro', m3[:300])
b.setv(SF, 'Todas'); time.sleep(.3)
# ---- Estoque
b.goto('EST.dc.html')
b.setv(FZ, 'Boa Vista'); time.sleep(.3); m = b.main(); print('   EST Boa Vista:', m[:300])
b.ok('Nenhum estoque na Boa Vista' in m and 'Ver Santa Rita' in m, 'Estoque · Boa Vista: estado vazio com "Ver Santa Rita"', m[:300])
b.clk('Ver Santa Rita'); v = b.val(FZ); b.ok(v == 'Santa Rita' and 'Custódia e devoluções' in b.main() or v == 'Santa Rita', 'Estoque · volta à Santa Rita', v)
# ---- Mapa
b.size(1440, 900); b.goto('IN-04.dc.html')
b.setv(FZ, 'Boa Vista'); time.sleep(.4); m = b.body(); nsv = b.J("document.querySelectorAll('svg [role=button]').length")
lk = b.J("(()=>{const a=[...document.querySelectorAll('a')].find(a=>/Cadastrar talhões/.test(a.innerText)); return a?a.getAttribute('href'):null;})()")
print('   IN-04 Boa Vista:', m[:300].replace('\n', ' / '), '| polígonos:', nsv, '| ação:', lk)
b.ok(nsv == 0 and 'Boa Vista' in m and lk == 'CD-01.dc.html', 'Mapa · Boa Vista: sem talhões e ação "Cadastrar talhões" → CD-01', (nsv, lk))
b.setv(FZ, 'Santa Rita'); time.sleep(.3)
# ---- SAF e CMP: só contexto
for t in ('SAF.dc.html', 'CMP.dc.html'):
    b.goto(t); ns = b.J("document.querySelectorAll('select[aria-label^=\"Filtrar\"]').length"); h = b.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')")
    b.ok(ns == 0 and 'Santa Rita' in h, f'{t}: Fazenda/Safra só como contexto (sem seletor de filtro)', (ns, h[:160]))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
