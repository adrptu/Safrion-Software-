# -*- coding: utf-8 -*-
"""Verificador App 8: ordem com saldo 0 ha continua oferecendo 'Iniciar turno' pelas telas do app; o turno aberto não fecha e trava a fila."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
    # pelas telas: Rui entrega (Estoque), Marcos confirma no MB-05, faz a OS-0424 inteira num turno pelo MB-03
    v.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');")
    v.abrir('MB-05'); v.clk('Confirmar recebimento'); print('   MB-05:', v.toast()[:70])
    v.abrir('MB-03'); v.clk_sel('main button[title="Iniciar turno na OS-0424"]'); print('   iniciar:', v.toast()[:60])
    v.setv('#ft_ha', '80'); v.setv('#ft_h', '6'); v.clk('Fechar turno'); print('   fechar 80 ha:', v.toast()[:90])
    v.abrir('MB-01'); b = v.body(); i = b.find('OS-0424 ·'); print('   MB-01 cartão:', b[i:i + 280].replace('\n', ' / '))
    v.ok('Iniciar turno' not in b[i:i + 400], 'ordem com saldo 0 ha não oferece Iniciar turno (MB-01)')
    v.clk_sel('main button[title="Iniciar turno na OS-0424"]'); print('   clicou Iniciar turno na OS-0424:', v.toast()[:70], '| foot:', v.foot())
    v.abrir('MB-03'); print('   MB-03 dica:', v.J("(document.querySelector('#ft_ha')||{parentElement:{innerText:'-'}}).parentElement.innerText").replace('\n', ' / '))
    for ha in ('0', '1', '0,5'):
        v.setv('#ft_ha', ha); v.setv('#ft_h', '1'); v.clk('Fechar turno'); print(f'   fechar {ha} ha ->', v.alerts()[:90])
    v.abrir('MB-01'); v.clk_sel('main button[title="Iniciar turno na OS-0421"]'); t = v.toast(); print('   iniciar OS-0421 ->', t[:80], '| foot:', v.foot())
    v.ok(v.cen("!c.app.turno || c.app.turno.os!=='OS-0424'"), 'não fica preso num turno que não pode ser fechado (turno em ' + str(v.cen("c.app.turno && c.app.turno.os")) + ')')
    v.c.size(1440, 1200); time.sleep(.3); v.abrir('MB-03'); v.shot('ver_app8_mb03_preso.png'); v.c.size(1440, 1000)
    v.ok(not v.erros(), 'sem erros JS ' + str(v.erros()))
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
