# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · D: recebimento (NF 4533 vencida toda em quarentena, nova nota), persistência ao recarregar, filtro por local e liberação da quarentena."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
v = V()
try:
    v.abrir()
    v.clk('Conferir NF 4533'); f = v.J(FORM); print('prim abre:', f)
    v.setv('fx_g_rec_conf', '20000'); v.setv('fx_g_rec_apto', '0'); v.setv('fx_g_rec_quar', '20000'); v.setv('fx_g_rec_val', '08/2026'); v.setv('fx_g_rec_obs', 'Lote vencido na chegada')
    v.clk('Salvar', 'aside[role=dialog]'); print('err:', v.err(), '| toast:', v.toast())
    print('linha:', v.rowtxt('NF 4533')); print('k1:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"), '| prim:', v.prim())
    v.etapa(4); print('lote vencido:', v.rowtxt('S58-0926')); print('item:', v.rowtxt('Semente de soja 58 W', 'lotes'))
    print('k4:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    v.ok('Liberar após inspeção' not in v.rowtxt('S58-0926') and 'Vencido' in v.rowtxt('S58-0926'), 'lote vencido: chip Vencido e sem liberar', v.rowtxt('S58-0926'))
    # nova nota: Registrar recebimento
    v.etapa(1); print('prim e1:', v.prim()); v.clk(v.prim()); f = v.J(FORM); print('novo form:', f)
    v.setv('fx_g_rec_ped', [o for o in v.J("[...document.querySelectorAll('#fx_g_rec_ped option')].map(o=>o.value)") if 'PC-091' in o][0]); time.sleep(.3)
    print('ped opções:', v.J("[...document.querySelectorAll('#fx_g_rec_ped option')].map(o=>o.value)"))
    print('val ro?', v.J("(()=>{const i=document.querySelector('#fx_g_rec_val'); return i?[i.value,i.readOnly,i.disabled]:null})()"))
    v.setv('fx_g_rec_nf', 'NF 4600'); v.setv('fx_g_rec_qtd_nf', '8000'); v.setv('fx_g_rec_conf', '8000'); v.setv('fx_g_rec_apto', '8000'); v.setv('fx_g_rec_quar', '0'); v.setv('fx_g_rec_lote', 'U26-20')
    v.clk('Salvar', 'aside[role=dialog]'); print('err:', v.err(), '| toast:', v.toast())
    for x in v.rows(): print('   ', x[:260])
    print('k1:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    # recarrega: tudo continua
    v.abrir(); print('após recarregar:'); [print('   ', x[:200]) for x in v.rows()]
    v.ok(any('NF 4533' in x and 'Vencido' in x for x in v.rows()) and any('NF 4600' in x for x in v.rows()), 'notas continuam conferidas depois de recarregar')
    # filtro por local + liberar quarentena KCl
    v.etapa(4)
    for lc in ('Galpão 1', 'Galpão 2', 'Câmara fria', 'Almox. defensivos', 'Todos os locais'):
        v.clk(lc); print(lc, '→', v.J("(document.querySelector('main').innerText.match(/\\d+ de \\d+/)||[''])[0]"), [x[:40] for x in v.rows() if not x.startswith('▾')][:8])
    v.rowbtn('K26-11', 'Liberar após inspeção'); print('K26 pede:', v.rowtxt('K26-11')); v.rowbtn('K26-11', 'Manter'); print('manter:', v.rowtxt('K26-11'))
    v.rowbtn('K26-11', 'Liberar após inspeção'); v.rowbtn('K26-11', 'Confirmar liberação'); print('toast:', v.toast()); print('K26:', v.rowtxt('K26-11'))
    print('lote cen:', v.cen("c.lotes['KCl 60%|K26-11']"))
    v.etapa(1); print('NF 4501:', v.rowtxt('NF 4501'))
    v.shot('ver_est_r4_d1.png')
    v.etapa(4); v.shot('ver_est_r4_d4.png'); print('overflow:', v.overflow())
    print('erros:', v.erros())
finally:
    v.fim()
