# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · E: contagens (INV-2609 da base, INV-2611 cega, nova contagem sem diferença) e trilha."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
v = V()
try:
    v.abrir()
    # devolução de 500 kg da REQ-031 antes da aprovação (movimento posterior à contagem de corte)
    v.etapa(3); v.row('REQ-031'); v.clk('Salvar', 'aside[role=dialog]'); print('dev:', v.toast())
    v.etapa(5); print('k5:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"), '| prim:', v.prim())
    print('tools:', v.J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&/Nova contagem/.test(b.innerText)).map(b=>b.innerText)"))
    v.row('INV-2609'); f = v.J(FORM); print('INV-2609 form:', f); print('  aside:', v.aside()[:500]); v.clk('Fechar', 'aside[role=dialog]'); v.clk('Cancelar', 'aside[role=dialog]')
    v.rowbtn('INV-2609', 'Aprovar ajuste'); print('aprovar 2609:', v.toast())
    print('MAP:', v.cen("c.lotes['MAP 11-52|M26-07'].fisico"), '| linha:', v.rowtxt('INV-2609'))
    # INV-2611 cega
    v.clk(v.prim()); f = v.J(FORM); print('INV-2611 form:', f); print('  aside:', v.aside()[:500])
    v.ok('1.200' not in v.aside() and '1200' not in v.aside(), 'formulário não mostra o saldo do sistema', v.aside())
    v.setv('fx_g_cnt_cont', '1180'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast()); print('linha:', v.rowtxt('INV-2611'))
    v.rowbtn('INV-2611', 'Aprovar ajuste'); print('sem causa:', v.toast(), '| aberto:', v.aberto(), v.J(FORM))
    v.setv('fx_g_cnt_causa', 'Galão furado descartado'); v.clk('Salvar', 'aside[role=dialog]'); print('causa:', v.toast())
    v.rowbtn('INV-2611', 'Aprovar ajuste'); print('aprovar:', v.toast()); print('G26:', v.cen("c.lotes['Glifosato 480|G26-14'].fisico"), '|', v.rowtxt('INV-2611'))
    print('k5:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"), '| prim:', v.prim())
    print('tools:', v.J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&/Nova contagem/.test(b.innerText)).map(b=>b.innerText)"))
    # nova contagem sem diferença
    v.clk(v.prim()); f = v.J(FORM); print('nova form:', f and f['h'], f and f['ins'][:1])
    lbl = [o for o in v.J("[...document.querySelectorAll('#fx_g_cnt_lote option')].map(o=>o.value)") if o.startswith('D26-01')][0]
    v.setv('fx_g_cnt_lote', lbl); v.setv('fx_g_cnt_cont', '300'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), v.err())
    for x in v.rows(): print('   ', x[:240])
    v.shot('ver_est_r4_e5.png'); print('overflow:', v.overflow())
    v.etapa(6)
    for x in v.rows(): print('   ', x[:240])
    v.etapa(4); v.row('M26-07'); print('origem M26-07:', v.aside()[:600])
    print('erros:', v.erros())
finally:
    v.fim()
