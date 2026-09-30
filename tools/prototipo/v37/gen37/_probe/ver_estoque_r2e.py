# -*- coding: utf-8 -*-
"""Verificador (rodada 2) · Estoque E: recebimento NF 4533 com quarentena 0, nova nota PC-091, persistência e saldo por local."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
K = "document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))"
v = V()
try:
    v.abrir()
    print('toolbar e1:', v.J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()).filter(Boolean).slice(0,12)"))
    v.clk('Conferir NF 4533')
    v.setv('fx_g_rec_conf', '20000'); v.setv('fx_g_rec_apto', '20000'); v.setv('fx_g_rec_quar', '0'); v.setv('fx_g_rec_val', '03/2027'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| err:', v.err())
    print('lote:', v.cen("c.lotes['Semente de soja 58 W|S58-0926']"))
    for r in v.rows(): print('   ', r[:240])
    print('k1:', v.J(K), '| prim:', v.prim())
    v.row('NF 4533'); print('4533 consulta:', v.J(FORM)); print('  ', v.aside()[:200]); v.clk('Fechar', 'aside[role=dialog]')
    v.clk('Registrar recebimento'); print('novo:', v.J(FORM))
    v.setv('fx_g_rec_ped', [o for o in v.J("[...document.querySelector('#fx_g_rec_ped').options].map(o=>o.value)") if 'PC-091' in o][0])
    v.setv('fx_g_rec_nf', 'NF 4600'); v.setv('fx_g_rec_qtd_nf', '8000'); v.setv('fx_g_rec_conf', '8000'); v.setv('fx_g_rec_apto', '8000'); v.setv('fx_g_rec_lote', 'S62-0001'); v.setv('fx_g_rec_val', '05/2027'); v.setv('fx_g_rec_local', 'Câmara fria')
    v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| err:', v.err())
    for r in v.rows(): print('   ', r[:240])
    print('k1:', v.J(K), '| prim:', v.prim())
    print('lote novo:', v.cen("c.lotes['Semente de soja 62 X|S62-0001']"))
    v.etapa(4); v.clk('Câmara fria'); print('câmara fria:', v.rows()); print('overflow:', v.overflow()); v.shot('ver_est_r2_e_cf.png'); v.clk('Todos os locais')
    v.etapa(6)
    for r in v.rows(): print('  mov:', r[:240])
    v.abrir(); print('recarregado:', v.rows()); print('prim:', v.prim())
    # contagem do lote novo aparece nas opções
    v.etapa(5); v.clk('Nova contagem'); print('nova contagem:', v.J(FORM))
    print('erros:', v.erros())
finally:
    v.fim()
