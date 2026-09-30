# -*- coding: utf-8 -*-
"""Verificador App 14: OS-0424-app × REQ-039 (entrega parcial em duas vezes, sem sinal, cargas, Registrar apontamento) e MB-01/MB-05 coerentes."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
M = lambda: v.J("document.querySelector('main').innerText").replace('\n', ' / ')
RS = lambda: v.J("[...document.querySelectorAll('main span')].map(s=>s.innerText).find(t=>/Reservado|Entregue|Recebido/.test(t))")
PB = lambda: v.J("[...document.querySelectorAll('button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim()).pop()")
try:
    v.abrir('OS-0424-app')
    print('  ins OS-0424:', v.cen("JSON.stringify(c.ordens['OS-0424'].ins)"), '| req:', v.cen("JSON.stringify(c.reqs['REQ-039'])"))
    print('  inicial:', RS(), '|', PB())
    v.clk(PB()); print('  prim sem entrega:', v.toast()[:200])
    # entrega parcial 40 L
    print('  ent40:', v.mudar("return cenEntregar(c,'REQ-039','Fungicida A',40,'Marcos');")[:90])
    v.abrir('OS-0424-app'); print('  após 40:', RS(), '|', PB())
    v.clk('Confirmar recebimento'); print('  conf40:', v.toast()[:150], '|', RS(), '|', PB())
    print('  ent25:', v.mudar("return cenEntregar(c,'REQ-039','Fungicida A',25,'Marcos');")[:90])
    v.abrir('OS-0424-app'); print('  após +25:', RS(), '|', PB())
    v.abrir('MB-01'); b = v.body(); i = b.find('OS-0424 ·'); print('  MB-01 cartão:', b[i:i + 330].replace('\n', ' / '), '| foot', v.foot())
    v.abrir('MB-05'); print('  MB-05:', M()[:600], '| foot', v.foot(), '| hdr', v.hdr())
    v.ok(v.cen("c.reqs['REQ-039'].itens[0].custodia") == 65 and 'Confirmar recebimento' in (v.foot() or ''), 'segunda entrega (25 L) pede confirmação no app')
    finally_state = v.cen("JSON.stringify(c.reqs['REQ-039'].itens[0])"); print('  item:', finally_state)
    # cargas e Registrar apontamento
    v.abrir('OS-0424-app')
    for k in range(3):
        v.clk(PB()); print('  carga:', v.toast()[:90])
    print('  prim final:', PB()); v.clk(PB()); print('  registrar apontamento ->', v.toast()[:160], '| url', v.J('location.pathname'))
    print('  turno?', v.cen('JSON.stringify(c.app.turno)'))
    v.shot('ver_app14_os0424.png')
    print('  erros', v.erros())
finally:
    v.fim()
