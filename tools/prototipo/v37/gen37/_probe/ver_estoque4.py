# -*- coding: utf-8 -*-
"""Verificador · Estoque 4: recebimento NF 4533 e novo recebimento; origem do item; contagem nova, INV-2609, movimentos."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

K = "(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l)||/custódia/.test(l))||'')"
v = V()
try:
    v.abrir(); v.etapa(4)
    # clique no nome do item (não na seta)
    r = v.J("(()=>{const row=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('MAP 11-52')>=0&&!r.classList.contains('g2kid')); const cells=row.querySelectorAll('[role=cell]'); const b=[...cells[0].querySelectorAll('span,b,div')].find(e=>e.innerText.trim()==='MAP 11-52'); (b||cells[1]).click(); return row.className;})()"); time.sleep(.4)
    print('item row class:', r, '| aberto:', v.aberto(), v.aside()[:400]); v.clk('Fechar', 'aside[role=dialog]')
    # recebimento NF 4533 pela primária
    v.etapa(1); print('primária:', v.prim()); v.clk(v.prim())
    print('campos:', v.J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(i=>i.id+'='+i.value+(i.readOnly?'(ro)':'')+(i.disabled?'(dis)':''))"))
    v.setv('fx_g_rec_conf', '20000'); v.setv('fx_g_rec_apto', '20000'); v.setv('fx_g_rec_quar', '0'); v.setv('fx_g_rec_val', '05/2027')
    v.clk('Salvar', 'aside[role=dialog]'); print('erro:', v.err(), '| toast:', v.toast())
    print('linha:', v.rowtxt('NF 4533')); print('primária agora:', v.prim()); print('k1:', v.J(K))
    print('lote cen:', v.cen("JSON.stringify(c.lotes['Semente de soja 58 W|S58-0926'])"))
    # novo recebimento PC-091 (semente 62 X) com parte em quarentena
    v.clk(v.prim()); print('novo form:', v.aside()[:200])
    v.setv('fx_g_rec_ped', v.J("[...document.querySelector('#fx_g_rec_ped').options].map(o=>o.value).find(x=>x.startsWith('PC-091'))"))
    for k, val in [('nf', 'NF 4600'), ('qtd_nf', '8000'), ('conf', '8000'), ('apto', '7500'), ('quar', '500'), ('lote', 'S62-1001'), ('val', '09/2027'), ('local', 'Câmara fria'), ('obs', 'Laudo de germinação pendente')]:
        v.setv('fx_g_rec_' + k, val)
    v.clk('Salvar', 'aside[role=dialog]'); print('erro:', v.err(), '| toast:', v.toast())
    print('linhas e1:'); [print('   |', x[:200]) for x in v.rows()]
    print('k1:', v.J(K))
    v.abrir(); v.etapa(1); print('após recarregar:'); [print('   |', x[:200]) for x in v.rows()]
    v.etapa(4); print('S62:', v.rowtxt('S62-1001')); print('item 62X:', v.rowtxt('Semente de soja 62 X'))
    # contagens: INV-2609 aprovar (causa de base)
    v.etapa(5); print('k5:', v.J(K)); print('aprovar 2609:', v.rowbtn('INV-2609', 'Aprovar ajuste'), v.toast()); print('linha:', v.rowtxt('INV-2609'))
    print('M26-07 cen:', v.cen("c.lotes['MAP 11-52|M26-07'].fisico"))
    # nova contagem de O26-05 sem diferença e de D26-01 com diferença
    print('prim antes:', v.prim(), '| +nova:', v.clk('+ Nova contagem'))
    if not v.aberto(): v.clk(v.prim())
    print('aberto nova:', v.aberto(), v.aside()[:300])
    print('opções lote:', v.J("[...(document.querySelector('#fx_g_cnt_lote')||{options:[]}).options].map(o=>o.value).slice(0,20)"))
    v.setv('fx_g_cnt_lote', v.J("[...document.querySelector('#fx_g_cnt_lote').options].map(o=>o.value).find(x=>x.startsWith('D26-01'))")); v.setv('fx_g_cnt_cont', '290')
    v.clk('Salvar', 'aside[role=dialog]'); print('erro:', v.err(), '| toast:', v.toast())
    for x in v.rows(): print('   |', x[:220])
    print('prim:', v.prim(), '| k5:', v.J(K))
    print('overflow:', v.overflow()); v.shot('ver_est_cnt.png')
    v.etapa(6); print('k6:', v.J(K))
    for x in v.rows(): print('   mov|', x[:220])
    print('overflow:', v.overflow())
    print('erros:', v.erros())
finally:
    v.fim()
