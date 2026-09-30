# -*- coding: utf-8 -*-
"""Verificador · Estoque 2: entregas por O.S. pela tela (primária, padrões, parcial, outra pessoa, confirmação no app, recarregar)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

v = V()
try:
    v.abrir()
    print('pré:', v.mudar("c.ordens['OS-0430'].aprov=true; return cenLiberar(c,'OS-0430');"))
    RQ = v.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')"); print('RQ', RQ)
    v.abrir(); v.etapa(2)
    print('faixa:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    print('primária:', v.prim())
    for r in v.rows(): print('   |', r[:230])
    # primária abre o formulário do primeiro item entregável
    v.clk(v.prim()); a = v.aside(); print('form:', a[:500])
    print('campos:', v.J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select,aside[role=dialog] textarea')].map(i=>i.id+'='+i.value+(i.readOnly?'(ro)':'')+(i.disabled?'(dis)':''))"))
    print('opções quem:', v.J("[...(document.querySelector('#fx_g_ent_quem')||{options:[]}).options].map(o=>o.value)"))
    print('botões form:', v.J("[...document.querySelectorAll('aside[role=dialog] button')].map(b=>b.innerText.trim()).filter(Boolean)"))
    v.shot('ver_est_ent_form.png')
    v.clk('Cancelar', 'aside[role=dialog]'); v.clk('Fechar', 'aside[role=dialog]')
    # entrega parcial de Glifosato a Paula
    v.row(RQ, 'Glifosato 480'); v.setv('fx_g_ent_qtd', '100'); v.setv('fx_g_ent_quem', 'Paula'); v.clk('Salvar', 'aside[role=dialog]')
    print('toast:', v.toast()); print('linha:', v.rowtxt(RQ, 'Glifosato 480'))
    print('cen:', v.cen(f"JSON.stringify(c.reqs['{RQ}'].itens[0])+' lote '+JSON.stringify(c.lotes['Glifosato 480|G26-14'])"))
    print('primária agora:', v.prim())
    # entrega do restante (220) a Marcos: custódia agora de 2 pessoas mas 'quem' é um só
    v.row(RQ, 'Glifosato 480'); print('padrão qtd:', v.val('fx_g_ent_qtd'), 'quem:', v.val('fx_g_ent_quem')); print('ajuda:', v.aside()[:400])
    v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast()); print('linha:', v.rowtxt(RQ, 'Glifosato 480'))
    print('cen:', v.cen(f"JSON.stringify(c.reqs['{RQ}'].itens[0])"))
    # linha entregue completa: abre como?
    v.row(RQ, 'Glifosato 480'); print('form completa:', v.aside()[:300], '| ro?', v.J("document.querySelectorAll('aside[role=dialog] input:not([readonly]), aside[role=dialog] select:not([disabled])').length"))
    v.clk('Fechar', 'aside[role=dialog]')
    # app confirma; recarrega; estado persiste
    print('app:', v.mudar(f"return cenConfirmarRecebimento(c,'{RQ}');"))
    v.abrir(); v.etapa(2); print('após recarregar:', v.rowtxt(RQ, 'Glifosato 480'))
    print('faixa:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l))||'')"))
    v.etapa(3); print('devol:', v.rowtxt(RQ, 'Glifosato 480'))
    print('k3:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l)||/custódia/.test(l))||'')"))
    v.etapa(6)
    for r in v.rows(): print('   mov|', r[:200])
    print('overflow e6:', v.overflow())
    v.shot('ver_est_mov.png')
    print('erros:', v.erros())
finally:
    v.fim()
