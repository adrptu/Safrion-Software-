# -*- coding: utf-8 -*-
"""Verificador (rodada 4) · C: devoluções (apta, bloqueada, acima da custódia), encerramento da O.S., reflexo nas etapas 2 e 4."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V
FORM = "(()=>{const a=document.querySelector('aside[role=dialog]'); if(!a) return null; return {h:(a.querySelector('h2')||{}).innerText, btns:[...a.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()), ins:[...a.querySelectorAll('input,select,textarea')].map(i=>i.id+'='+i.value+(i.readOnly||i.disabled?'(ro)':'')+' w='+i.clientWidth+'/'+i.scrollWidth)};})()"
v = V()
try:
    v.abrir()
    print(v.mudar("c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const r=c.ordens['OS-0430'].req; c.reqs[r].itens.forEach(i=>cenEntregar(c,r,i.prod,i.solicitado,'Marcos')); return cenConfirmarRecebimento(c,r);"))
    v.etapa(3)
    print('k3:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/·|custódia/.test(l))||'')"), '| prim:', v.prim())
    for x in v.rows(): print('   ', x[:260])
    v.row('REQ-47', 'Glifosato'); f = v.J(FORM); print('form:', f); print('  aside:', v.aside()[:500])
    v.ok(v.val('fx_g_dev_qtd') == '320' and 'Apta' in (v.val('fx_g_dev_cond') or ''), 'padrões: custódia inteira e Apta', (v.val('fx_g_dev_qtd'), v.val('fx_g_dev_cond')))
    v.setv('fx_g_dev_qtd', '321'); v.clk('Salvar', 'aside[role=dialog]'); e = v.err(); print('321:', e); v.ok('Acima da custódia' in e, 'recusa acima da custódia', e)
    v.setv('fx_g_dev_qtd', '20'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('G26-14:', v.cen("c.lotes['Glifosato 480|G26-14']"))
    v.row('REQ-47', 'Óleo'); v.setv('fx_g_dev_qtd', '10'); v.setv('fx_g_dev_cond', 'Bloqueada para inspeção · vai para quarentena'); v.clk('Salvar', 'aside[role=dialog]'); e = v.err(); print('bloq sem obs:', e)
    v.ok('Descreva a condição' in e, 'bloqueada exige observação', e)
    v.shot('ver_est_r4_c_form.png')
    v.setv('fx_g_dev_obs', 'Galão com lacre rompido'); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    print('O26-05:', v.cen("c.lotes['Óleo mineral|O26-05']"))
    v.row('REQ-031'); print('REQ-031 padrões:', v.val('fx_g_dev_qtd')); v.clk('Salvar', 'aside[role=dialog]'); print('toast:', v.toast())
    for x in v.rows(): print('   ', x[:260])
    print('k3:', v.J("(document.querySelector('main').innerText.split('\\n').find(l=>/custódia/.test(l))||'')"), '| prim:', v.prim())
    print('podeEncerrar OS-0417:', repr(v.cen("X.cenPodeEncerrar(c,'OS-0417')")))
    v.shot('ver_est_r4_c3.png')
    v.etapa(2); print('e2 REQ-47:', [x[:200] for x in v.rows() if 'REQ-47' in x])
    v.etapa(4); print('O26-05 saldo:', v.rowtxt('O26-05')); print('G26-14 saldo:', v.rowtxt('G26-14'))
    v.row('O26-05'); print('origem O26-05:', v.aside()[:700]); v.clk('Fechar', 'aside[role=dialog]')
    v.etapa(6)
    for x in v.rows()[:4]: print('   ', x[:260])
    v.row('Devolução', 'Óleo'); print('mov form:', v.aside()[:400])
    print('erros:', v.erros())
finally:
    v.fim()
