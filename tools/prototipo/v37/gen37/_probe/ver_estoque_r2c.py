# -*- coding: utf-8 -*-
"""Verificador (rodada 2) · Estoque C: devoluções (apta/bloqueada, acima da custódia), liberação no lote, reentrega e confirmação no app."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))};})()"
K = "document.querySelector('main').innerText.split('\\n').find(l=>/·|custódia/.test(l))"
v = V()
try:
    v.abrir(); v.etapa(3)
    print('prim:', v.prim()); v.clk(v.prim()); print('form:', v.J(FORM)); print('  aside:', v.aside()[:500])
    v.setv('fx_g_dev_qtd', '600'); v.clk('Salvar', 'aside[role=dialog]'); print('600 ->', v.err())
    v.setv('fx_g_dev_qtd', '500'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('M26-07:', v.cen("c.lotes['MAP 11-52|M26-07']"), '| podeEnc 0417:', repr(v.cen("X.cenPodeEncerrar(c,'OS-0417')")))
    for r in v.rows(): print('   ', r[:240])
    print('k3:', v.J(K), '| prim:', v.prim())
    # REQ-035 bloqueada 5 L
    v.row('REQ-035'); print('form 035:', v.J(FORM))
    v.setv('fx_g_dev_qtd', '5'); v.setv('fx_g_dev_cond', 'Bloqueada para inspeção · vai para quarentena'); v.setv('fx_g_dev_obs', 'Galão com lacre rompido'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('F26-02:', v.cen("c.lotes['Fungicida A|F26-02']"))
    print('linha 035:', v.rowtxt('REQ-035'))
    # etapa 4: F26-02 com bloqueado 5 L e Liberar
    v.etapa(4); print('k4:', v.J(K)); print('F26-02 linha:', v.rowtxt('F26-02'))
    print('liberar:', v.rowbtn('F26-02', 'Liberar após inspeção'), v.rowtxt('F26-02'))
    print('manter:', v.rowbtn('F26-02', 'Manter'), v.rowtxt('F26-02'))
    v.rowbtn('F26-02', 'Liberar após inspeção'); print('confirmar:', v.rowbtn('F26-02', 'Confirmar liberação'), '| toast:', v.toast())
    print('F26-02 após:', v.cen("c.lotes['Fungicida A|F26-02']"), '|', v.rowtxt('F26-02'))
    print('repetir via API:', v.mudar("return cenLiberarQuarentena(c,'Fungicida A|F26-02');"))
    # origem do lote
    v.row('F26-02'); print('origem F26-02:', v.aside()[:700]); v.clk('Fechar', 'aside[role=dialog]')
    # reentrega da REQ-035: devolver o resto (60 L) apto e reentregar
    v.etapa(3); v.row('REQ-035'); print('padrão custódia:', v.val('fx_g_dev_qtd')); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('REQ-035 it:', v.cen("c.reqs['REQ-035'].itens[0]"), '| podeEnc 0421:', repr(v.cen("X.cenPodeEncerrar(c,'OS-0421')")))
    v.etapa(2); print('linha 035:', v.rowtxt('REQ-035'), '| prim:', v.prim())
    v.row('REQ-035'); print('form reentrega:', v.J(FORM)); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('F26-02:', v.cen("c.lotes['Fungicida A|F26-02']"))
    print('app confirma:', v.mudar("return cenConfirmarRecebimento(c,'REQ-035');"))
    v.J("window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
    print('linha 035 pós app:', v.rowtxt('REQ-035'))
    v.etapa(6)
    for r in v.rows(): print('   ', r[:240])
    print('k6:', v.J(K))
    v.row('MV-1001'); print('mov form:', v.aside()[:400]); v.clk('Fechar', 'aside[role=dialog]')
    print('overflow e6:', v.overflow())
    v.shot('ver_est_r2_c_e6.png')
    # recarregar: tudo persiste
    v.abrir(); v.etapa(3)
    for r in v.rows(): print('  e3 recarregado:', r[:240])
    print('erros:', v.erros())
finally:
    v.fim()
