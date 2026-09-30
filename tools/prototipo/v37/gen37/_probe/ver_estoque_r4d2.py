# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · D2: nova nota (Registrar recebimento) de item sem lote no cenário, persistência ao recarregar, NF com outro formato."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, sub:(a.querySelector('h2').parentElement.parentElement.innerText||'').slice(0,200), btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
v = V()
try:
    v.abrir()
    # confere a 4533 primeiro para a primária virar Registrar recebimento
    v.clk('Conferir NF 4533'); v.setv('fx_g_rec_conf', '20000'); v.setv('fx_g_rec_apto', '20000'); v.setv('fx_g_rec_quar', '0'); v.setv('fx_g_rec_val', '03/2027'); v.clk('Salvar', 'aside[role=dialog]'); print('4533:', v.toast())
    print('prim:', v.prim()); v.clk(v.prim())
    op = [o for o in v.J("[...document.querySelectorAll('#fx_g_rec_ped option')].map(o=>o.value)") if 'PC-091' in o][0]
    v.setv('fx_g_rec_ped', op)
    v.setv('fx_g_rec_nf', 'NF 4600'); v.setv('fx_g_rec_qtd_nf', '8000'); v.setv('fx_g_rec_conf', '8000'); v.setv('fx_g_rec_apto', '8000'); v.setv('fx_g_rec_quar', '0'); v.setv('fx_g_rec_lote', 'S62-0927'); v.setv('fx_g_rec_val', '05/2027')
    print('local padrão:', v.val('fx_g_rec_local'))
    v.clk('Salvar', 'aside[role=dialog]'); print('err:', v.err(), '| toast:', v.toast(), '| aberto:', v.aberto())
    for x in v.rows(): print('   ', x[:260])
    print('k1:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    print('lote:', v.cen("c.lotes['Semente de soja 62 X|S62-0927']"))
    v.row('NF 4600'); print('consulta 4600:', v.J(FORM)); v.clk('Fechar', 'aside[role=dialog]')
    # NF duplicada com outro formato
    v.clk(v.prim()); v.setv('fx_g_rec_ped', op); v.setv('fx_g_rec_nf', '4600'); v.setv('fx_g_rec_qtd_nf', '10'); v.setv('fx_g_rec_conf', '10'); v.setv('fx_g_rec_apto', '10'); v.setv('fx_g_rec_lote', 'S62-0927'); v.setv('fx_g_rec_val', '05/2027')
    v.clk('Salvar', 'aside[role=dialog]'); print('dup 4600:', v.err()); v.clk('Cancelar', 'aside[role=dialog]'); v.clk('Descartar alterações')
    print('aberto após cancelar:', v.aberto())
    v.abrir(); print('após recarregar:'); rs = v.rows(); [print('   ', x[:200]) for x in rs]
    v.ok(any('NF 4600' in x for x in rs) and any('NF 4533' in x and 'Conferido' in x for x in rs), 'notas conferidas continuam depois de recarregar', rs)
    v.etapa(4); print('saldo S62:', v.rowtxt('S62-0927')); print('item S62:', v.rowtxt('Semente de soja 62 X'))
    v.etapa(6); [print('   ', x[:220]) for x in v.rows()]
    print('erros:', v.erros())
finally:
    v.fim()
