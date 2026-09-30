# -*- coding: utf-8 -*-
"""Verificador (rodada 2) · Estoque B: entregas por O.S. (padrões, consulta com motivo, recusa, aguardando app, reserva de outra O.S.)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
v = V()
try:
    v.abrir(); v.etapa(2)
    # consulta: REQ-031, REQ-036, REQ-038
    for rq in ('REQ-031', 'REQ-036', 'REQ-038'):
        print(rq, v.row(rq), v.J(FORM)); print('   aside:', v.aside()[:400]); v.clk('Fechar', 'aside[role=dialog]')
    # primária abre REQ-035
    print('prim:', v.prim()); v.clk(v.prim()); print('form prim:', v.J(FORM)); print('   aside:', v.aside()[:500])
    v.clk('Fechar', 'aside[role=dialog]'); v.clk('Cancelar', 'aside[role=dialog]')
    # REQ-035 entregar 15 L para Paula; reserva da REQ-039 (65 L) deve ficar
    v.row('REQ-035'); print('padrões REQ-035:', v.val('fx_g_ent_qtd'), v.val('fx_g_ent_quem'))
    v.setv('fx_g_ent_qtd', '0'); v.clk('Salvar', 'aside[role=dialog]'); print('qtd 0 ->', v.err())
    v.setv('fx_g_ent_qtd', 'abc'); v.clk('Salvar', 'aside[role=dialog]'); print('qtd abc ->', v.err())
    v.setv('fx_g_ent_qtd', '15'); v.setv('fx_g_ent_quem', 'Paula'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| aberto:', v.J("!!document.querySelector('aside[role=dialog]')"))
    print('F26-02:', v.cen("c.lotes['Fungicida A|F26-02']"))
    print('REQ-035 it:', v.cen("c.reqs['REQ-035'].itens[0]"))
    print('linha 035:', v.rowtxt('REQ-035')); print('linha 039:', v.rowtxt('REQ-039'))
    print('k2:', v.J("document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))"))
    print('prim agora:', v.prim())
    # custódia com quem? etapa 3
    v.etapa(3); print('e3 035:', v.rowtxt('REQ-035')); v.etapa(2)
    # REQ-039: padrões e entrega
    v.row('REQ-039'); print('padrões REQ-039:', v.J(FORM)); print('  aside:', v.aside()[:500])
    v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('F26-02 depois 039:', v.cen("c.lotes['Fungicida A|F26-02']"))
    # REQ-040 NPK 8.000 kg
    v.row('REQ-040'); print('padrões REQ-040:', v.J(FORM)); print('  aside:', v.aside()[:500])
    v.setv('fx_g_ent_qtd', '8001'); v.clk('Salvar', 'aside[role=dialog]'); print('8001 ->', v.err())
    v.setv('fx_g_ent_qtd', '8000'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    for r in v.rows(): print('   ', r[:260])
    print('k2:', v.J("document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))"), '| prim:', v.prim())
    # linha entregue abre em consulta
    v.row('REQ-040'); print('REQ-040 entregue:', v.J(FORM)); print('  aside:', v.aside()[:300]); v.clk('Fechar', 'aside[role=dialog]')
    print('overflow:', v.overflow())
    v.shot('ver_est_r2_b_e2.png')
    print('erros:', v.erros())
finally:
    v.fim()
