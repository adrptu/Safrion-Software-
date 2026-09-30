# -*- coding: utf-8 -*-
"""v2 · 4y · OS.dc.html com 60 ha no aparelho aguardando sinal: o formulário web de apontamento aceita a área toda (160 ha)?
Depois o app volta o sinal: o realizado passa de 160 ha?"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS); r = b.clk('Registrar apontamento', 'aside[role=dialog]'); print('   abrir form:', r)
a = b.aside(); print('   form:', a[a.find('PRÓXIMO'):][:600])
for f in campos(b): print('   campo:', f)
ok = b.J("(()=>{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith('Área feita')); if(!l) return 'sem rótulo'; const i=l.querySelector('input')||document.getElementById(l.getAttribute('for'))||l.parentElement.querySelector('input[type=text]'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'160'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok';})()"); time.sleep(.3)
print('   área 160:', ok, '| alertas:', b.alerts('aside[role=dialog]'))
r = b.clk('Salvar apontamento', 'aside[role=dialog]'); t = b.toast(); al = b.alerts('aside[role=dialog]')
st = b.cen(f"[c.ordens['{OS}'].realizado, c.ordens['{OS}'].saldo, c.ordens['{OS}'].ap.map(a=>a.origem+':'+a.ha+':'+a.st).join(' | '), c.app.fila.length, c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.consumido+'/'+i.custodia).join(' ')]")
print('   salvar:', r, '| toast:', t, '| alertas:', al); print('   cenário:', st)
b.ok(not (st[0] == 160 and st[3] == 1), 'web não deixa apontar 160 ha com 60 ha do app ainda aguardando sinal (evita passar de 160 ha)', (t, al, st))
b.fim()
