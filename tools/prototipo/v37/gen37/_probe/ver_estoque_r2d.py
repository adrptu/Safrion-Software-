# -*- coding: utf-8 -*-
"""Verificador (rodada 2) · Estoque D: recebimento (NF 4533, nova nota, persistência), liberação do KCl refletida na nota, Boa Vista/Todas."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
K = "document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))"
v = V()
try:
    v.abrir()
    v.clk('Conferir NF 4533'); print('form 4533:', v.J(FORM))
    v.setv('fx_g_rec_conf', '20000'); v.setv('fx_g_rec_apto', '20000'); v.setv('fx_g_rec_val', '03/2027'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| err:', v.err())
    print('lote:', v.cen("c.lotes['Semente de soja 58 W|S58-0926']"))
    for r in v.rows(): print('   ', r[:240])
    print('k1:', v.J(K), '| prim:', v.prim())
    v.row('NF 4533'); print('4533 consulta:', v.J(FORM)); print('  ', v.aside()[:300]); v.clk('Fechar', 'aside[role=dialog]')
    # nova nota
    v.clk('Registrar recebimento'); print('novo:', v.J(FORM))
    v.setv('fx_g_rec_ped', [o for o in v.J("[...document.querySelector('#fx_g_rec_ped').options].map(o=>o.value)") if 'PC-091' in o][0])
    v.setv('fx_g_rec_nf', 'NF 4600'); v.setv('fx_g_rec_qtd_nf', '8000'); v.setv('fx_g_rec_conf', '8000'); v.setv('fx_g_rec_apto', '8000'); v.setv('fx_g_rec_lote', 'G26-14'); v.setv('fx_g_rec_val', '05/2027'); v.setv('fx_g_rec_local', 'Câmara fria')
    v.clk('Salvar', 'aside[role=dialog]'); print('lote de outro item ->', v.err())
    v.setv('fx_g_rec_lote', 'S62-0001'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| err:', v.err())
    for r in v.rows(): print('   ', r[:240])
    print('k1:', v.J(K), '| prim:', v.prim())
    print('lote novo:', v.cen("c.lotes['Semente de soja 62 X|S62-0001']"))
    # etapa 4: câmara fria
    v.etapa(4); v.clk('Câmara fria'); print('câmara fria:', v.rows()); v.clk('Todos os locais')
    # liberar KCl
    v.rowbtn('K26-11', 'Liberar após inspeção'); v.rowbtn('K26-11', 'Confirmar liberação'); print('toast:', v.toast())
    v.etapa(1); print('NF 4501:', v.rowtxt('NF 4501')); print('k1:', v.J(K))
    # recarregar
    v.abrir(); print('recarregado:', v.rows()); print('prim:', v.prim())
    # Boa Vista em todas as etapas
    v.setv('select[aria-label="Filtrar por fazenda"]', 'Boa Vista'); time.sleep(.3)
    for i in range(1, 7):
        v.etapa(i); m = v.J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")
        print(f'BV e{i}:', m[:160], '| prim:', repr(v.prim()), '| prim visível:', v.J("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>b.innerText)"))
    v.shot('ver_est_r2_d_bv.png')
    print('opções fazenda:', v.J("[...document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').options].map(o=>o.value+'/'+o.text)"))
    v.setv('select[aria-label="Filtrar por fazenda"]', [o for o in v.J("[...document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').options].map(o=>o.value)") if 'Toda' in o][0]); time.sleep(.3)
    v.etapa(2); print('Todas e2:', v.J("document.querySelector('main').innerText.replace(/\\s+/g,' ')")[:200], '| prim:', v.prim())
    print('erros:', v.erros())
finally:
    v.fim()
