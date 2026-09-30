# -*- coding: utf-8 -*-
"""Passo 13b · OS.dc.html (web): OS-0430 Em execução sem nada entregue: Registrar apontamento de 60 ha pela web."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS); rr = b.clk('Registrar apontamento', 'aside[role=dialog]')
if rr != 'ok':  # início bloqueado sem insumo com o operador: não há apontamento pela web
    st = b.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].realizado]"); p = b.aside(); print('   sem apontamento:', st, '|', p[p.find('PRÓXIMO'):][:300])
    b.ok(st[0] == 'Liberadas' and st[1] == 0 and 'Iniciar bloqueado' in p, 'web: sem insumo entregue a ordem não inicia, então não há apontamento de 60 ha sem custódia', (st, p[:300]))
    er = b.erros(); b.ok(not er, 'sem erro de JS', er); b.fim(); sys.exit(0)
b.J("(()=>{const a=document.querySelector('aside[role=dialog]'); const l=[...a.querySelectorAll('label')].find(l=>l.innerText.trim().startsWith('Área feita')); const i=l.querySelector('input')||document.getElementById(l.getAttribute('for'))||l.parentElement.querySelector('input[type=text]'); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,'60'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.2)
r = b.clk('Salvar apontamento', 'aside[role=dialog]'); t = b.toast(); al = b.alerts('aside[role=dialog]')
st = b.cen(f"[c.ordens['{OS}'].realizado, c.ordens['{OS}'].ap.length, c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.entregue+'/'+i.consumido+'/'+i.custodia).join(' ')]")
p = b.aside(); i = p[p.find('INSUMOS'):p.find('RETIRADA')]
print('   salvar:', r, '| toast:', t, '| alertas:', al); print('   cenário realizado/aps/itens(entregue/consumido/custódia):', st); print('   insumos:', i[:600]); print('   linha:', b.rowtxt(OS))
b.ok(not (st[0] == 60 and st[2].startswith('0/')), 'web: apontamento de 60 ha sem insumo entregue deveria ser barrado (consumo sem custódia)', (t, st))
b.shot('e2e_13b_os_web_apontar.png')
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
