# -*- coding: utf-8 -*-
"""Passo 3a · App (MB-01 → MB-05): aparece "Confirmar recebimento" da OS-0430 e o operador confirma."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-01.dc.html')
m = b.main(); print('   MB-01:', m[:900])
print('   botões:', b.btns()); print('   links:', b.links())
foot = b.J("[...document.querySelectorAll('a,button')].filter(e=>e.offsetParent!==null&&/font-size: 17px/.test(e.getAttribute('style')||'')).map(e=>e.innerText.trim()+' → '+(e.getAttribute('href')||''))")
print('   rodapé:', foot)
b.ok(OS in m, 'MB-01 mostra a OS-0430 na fila do operador', m[:300])
b.ok(any('Confirmar' in f and ('recebimento' in f or 'retirada' in f) for f in (foot or [])), 'MB-01: ação principal é confirmar o recebimento da OS-0430', foot)
b.ok('Confirmar recebimento' in b.body(), 'MB-01 mostra o texto "Confirmar recebimento"', foot)
b.shot('e2e_03a_mb01.png')
er1 = b.erros()
# seguir o rodapé até a MB-05
href = b.J("(()=>{const e=[...document.querySelectorAll('a')].filter(e=>e.offsetParent!==null&&/font-size: 17px/.test(e.getAttribute('style')||''))[0]; return e?e.getAttribute('href'):'';})()"); print('   href rodapé:', href)
b.goto(href if href and href.endswith('.dc.html') else 'MB-05.dc.html')
m = b.main(); print('   MB-05:', m[:900]); print('   botões:', b.btns())
b.ok('G26-14' in m and '16 × galão 20 L' in m, 'MB-05 lista o que foi entregue com lote e embalagem', m[:400])
r = b.clk('Confirmar recebimento'); t = b.toast(); print('   confirmar:', r, '| toast:', t)
st = b.cen(f"c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.confirmado)"); print('   cenário confirmado:', st)
b.ok(r == 'ok' and st == [True, True, True] and 'Recebimento confirmado' in t, 'confirmar recebimento grava os 3 itens confirmados', (r, t, st))
m2 = b.main(); print('   MB-05 depois:', m2[:500])
b.shot('e2e_03a_mb05.png')
er = er1 + b.erros(); b.ok(not er, 'sem erro de JS no app (MB-01, MB-05)', er)
b.fim()
