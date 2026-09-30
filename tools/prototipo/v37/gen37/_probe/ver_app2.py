# -*- coding: utf-8 -*-
"""Verificador App 2: MB-03 validações junto ao campo, consumo pré-calculado, insumo fora da REQ, saldo sem sinal (dois turnos)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-03')
    v.clk('Iniciar turno · OS-0421'); print('   iniciar:', v.toast()[:70], '| foot:', v.foot(), '| hdr:', v.hdr())
    v.clk('Fechar turno'); al = v.alerts(); print('   vazio ->', al, '|', v.toast()[:60])
    v.ok('Informe os hectares' in al and 'Informe as horas' in al and v.cen('!!c.app.turno'), 'campos vazios: erros junto ao campo e nada gravado')
    v.setv('#ft_ha', '140'); v.setv('#ft_h', '25')
    vals = v.J("[...document.querySelectorAll('main input')].map(i=>i.id+'='+i.value).join(' | ')"); print('   valores:', vals)
    print('   dicas:', v.J("[...document.querySelectorAll('main label')].map(l=>l.innerText+' :: '+(l.parentElement.querySelector('span')||{}).innerText).join(' | ')"))
    v.clk('Fechar turno'); al = v.alerts(); print('   140 ha / 25 h ->', al)
    v.ok('Acima do que está com você: 65 L' in al and 'Máximo 24 h' in al and v.cen('!!c.app.turno'), 'consumo acima da custódia e horas > 24: erro junto ao campo')
    # corrigir horas e consumo do fungicida; adjuvante (fora da REQ-035) fica pré-calculado
    v.setv('#ft_h', '8,5'); v.setv('#ft_c0', '65')
    v.clk('Fechar turno'); t = v.toast(); print('   fechar 140 ha ->', t[:120], '| alerts:', v.alerts())
    mv = v.cen("c.movs.filter(m=>m.tipo==='consumo').map(m=>m.det).join(' ; ')"); print('   consumo registrado:', mv)
    print('   REQ-035:', v.cen("JSON.stringify(c.reqs['REQ-035'].itens)"))
    v.ok('Adjuvante espalhante' not in mv, 'insumo fora da REQ-035 (Adjuvante, 0 com você) não deveria ser baixado como consumo: ' + mv)
    b = v.body(); print('   resumo:', b[b.find('Turno fechado'):b.find('Turno fechado') + 250].replace('\n', ' / '))
    # dois turnos sem sinal na mesma ordem: o limite de hectares ignora o que já está no aparelho?
    v.clk('Restaurar demonstração') if False else None
    v.abrir('MB-01'); v.clk('Restaurar demonstração'); v.abrir('MB-03')
    v.clk('Sem sinal'); v.clk('Iniciar turno · OS-0421')
    v.setv('#ft_ha', '120'); v.setv('#ft_h', '8'); v.clk('Fechar turno'); print('   turno 1 sem sinal 120 ha ->', v.toast()[:90])
    v.clk('Iniciar turno · OS-0421'); b = v.body()
    i = b.find('Realizado'); print('   turno 2:', b[i:i + 120].replace('\n', ' / '), '| dica:', v.J("document.querySelector('#ft_ha').parentElement.innerText").replace('\n', ' / '))
    v.setv('#ft_ha', '100'); v.setv('#ft_h', '7'); v.setv('#ft_c0', '5'); v.clk('Fechar turno'); print('   turno 2 sem sinal 100 ha ->', v.toast()[:90], '| alerts:', v.alerts())
    v.clk('Com sinal'); print('   sinal volta ->', v.toast()[:100])
    real = v.cen("c.ordens['OS-0421'].realizado"); area = v.cen("c.ordens['OS-0421'].area")
    print('   OS-0421 realizado', real, 'de', area, '| saldo', v.cen("c.ordens['OS-0421'].saldo"))
    v.ok(real <= area, f'sem sinal, dois turnos não passam da área da ordem (realizado {real} de {area} ha)')
    v.shot('ver_app2_mb03.png')
    v.ok(not v.erros(), 'sem erros JS ' + str(v.erros()))
    v.abrir('MB-01'); v.clk('Restaurar demonstração')
finally:
    v.fim()
