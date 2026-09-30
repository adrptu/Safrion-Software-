# -*- coding: utf-8 -*-
"""Passo 5a · App MB-03: turno de 100 ha na OS-0430 (Glifosato ajustado para 180 L → sobra 20 L em custódia)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-03.dc.html')
r = b.clk_sel(f'button[title="Iniciar turno na {OS}"]'); print('   iniciar:', r, b.toast())
b.setv('#ft_ha', '100'); b.setv('#ft_h', '8')
pre = b.J("[...document.querySelectorAll('[id^=ft_c]')].map(i=>i.id+'='+i.value)"); print('   consumo pré-calculado:', pre)
b.ok(pre == ['ft_c0=200', 'ft_c1=100', 'ft_c2=50'], 'consumo pré-calculado pela dose × 100 ha (200/100/50 L)', pre)
b.setv('#ft_c0', '180')
r = b.clk('Fechar turno'); t = b.toast(); print('   fechar:', r, '|', t, '| alertas:', b.alerts('main'))
st = b.cen(f"[c.ordens['{OS}'].realizado, c.ordens['{OS}'].saldo, c.ordens['{OS}'].ap.length, c.app.fila.length, c.reqs[c.ordens['{OS}'].req].itens.map(i=>i.consumido+'/'+i.custodia).join(' ')]"); print('   cenário:', st)
b.ok(st == [160, 0, 2, 0, '300/20 160/0 80/0'], 'turno 2 com sinal: realizado 160 ha, saldo 0, sobra 20 L de Glifosato em custódia', st)
print('   MB-03:', b.main()[:600])
b.goto('MB-05.dc.html'); m = b.main(); print('   MB-05:', m[:700])
b.ok('20 L' in m, 'MB-05 mostra a sobra de 20 L de Glifosato com o operador', m[:500])
b.shot('e2e_05a_mb05_sobra.png')
er = b.erros(); b.ok(not er, 'sem erro de JS no app', er)
b.fim()
