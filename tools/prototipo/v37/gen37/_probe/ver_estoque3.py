# -*- coding: utf-8 -*-
"""Verificador · Estoque 3: devoluções (padrões, apta, bloqueada), saldos com filtro por local, liberar quarentena, faixas das etapas."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

K = "(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l)||/custódia/.test(l))||'')"
v = V()
try:
    v.abrir(); v.etapa(3)
    print('primária:', v.prim()); v.clk(v.prim()); a = v.aside(); print('form:', a[:400])
    print('campos:', v.J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(i=>i.id+'='+i.value+(i.readOnly?'(ro)':'')+(i.disabled?'(dis)':''))"))
    print('opções cond:', v.J("[...(document.querySelector('#fx_g_dev_cond')||{options:[]}).options].map(o=>o.value)"))
    v.shot('ver_est_dev_form.png')
    # devolução parcial bloqueada sem observação -> erro; com observação -> quarentena
    v.setv('fx_g_dev_qtd', '200'); v.setv('fx_g_dev_cond', 'Bloqueada para inspeção · vai para quarentena'); v.clk('Salvar', 'aside[role=dialog]'); print('erro:', v.err())
    v.setv('fx_g_dev_obs', 'Sacos rasgados'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast(), '| aberto?', v.aberto())
    print('linha:', v.rowtxt('REQ-031')); print('k3:', v.J(K))
    print('cen:', v.cen("JSON.stringify(c.reqs['REQ-031'].itens[0])+' | '+JSON.stringify(c.lotes['MAP 11-52|M26-07'])"))
    # restante apta -> pode encerrar
    v.row('REQ-031'); print('padrão qtd:', v.val('fx_g_dev_qtd'), v.val('fx_g_dev_cond'))
    v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast()); print('linha:', v.rowtxt('REQ-031'))
    print('podeEncerrar:', repr(v.cen("X.cenPodeEncerrar(c,'OS-0417')")))
    print('primária agora:', v.prim())
    v.row('REQ-031'); print('form sem custódia:', v.aside()[:200], '| editáveis:', v.J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled]), aside[role=dialog] textarea:not([readonly])').length")); v.clk('Fechar', 'aside[role=dialog]')
    # saldos: bloqueado do MAP, faixas das etapas 1 e 4
    v.etapa(4); print('k4:', v.J(K)); print('MAP:', v.rowtxt('MAP 11-52')); print('M26-07:', v.rowtxt('M26-07'))
    v.etapa(1); print('k1:', v.J(K)); print('NF 4501:', v.rowtxt('NF 4501'))
    v.etapa(4)
    for loc in ['Galpão 1', 'Galpão 2', 'Câmara fria', 'Almox. defensivos']:
        v.clk(loc); print(loc, '->', v.J("[...document.querySelectorAll('[role=row].g2kid')].map(r=>r.innerText.split('\\n')[0].trim()).join(',')"), '|', v.J("(document.querySelector('main').innerText.match(/\\d+ de \\d+/)||[''])[0]"))
    v.clk('Galpão 2'); v.shot('ver_est_saldo_g2.png')
    # liberar a quarentena do MAP devolvido (Manter primeiro)
    print('libq:', v.rowbtn('M26-07', 'Liberar após inspeção'), v.rowtxt('M26-07'))
    print('manter:', v.rowbtn('M26-07', 'Manter'), v.rowtxt('M26-07'))
    v.rowbtn('M26-07', 'Liberar após inspeção'); v.rowbtn('M26-07', 'Confirmar liberação'); print('toast:', v.toast()); print('M26-07:', v.rowtxt('M26-07'))
    print('cen:', v.cen("JSON.stringify(c.lotes['MAP 11-52|M26-07'])"))
    print('k4:', v.J(K)); v.etapa(1); print('k1:', v.J(K))
    v.etapa(4); print('filtro ainda:', v.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)"))
    # clique na linha do item e do lote: origem
    v.row('M26-07'); print('origem lote:', v.aside()[:600]); v.clk('Fechar', 'aside[role=dialog]')
    v.row('MAP 11-52'); print('origem item:', v.aside()[:400]); v.clk('Fechar', 'aside[role=dialog]')
    print('overflow:', v.overflow())
    print('erros:', v.erros())
finally:
    v.fim()
