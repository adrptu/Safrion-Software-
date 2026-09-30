# -*- coding: utf-8 -*-
"""Jornada 2: turno com pausa, erros junto ao campo (saldo, consumo, horas), chip do resumo após o sinal, MB-01 com turno aberto."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_appv_lib import V, precarga
a = V(); OS = 'OS-0430'
try:
    rid = precarga(a)
    a.abrir('MB-05'); a.clk('Confirmar recebimento', wait=.5)
    a.abrir('MB-03'); a.clk_sel(f'button[title="Iniciar turno na {OS}"]', wait=.5)
    a.clk('Pausar turno'); print('   pausado: hdr', a.hdr(), '| main', a.main()[:500].replace('\n', ' / '))
    a.ok('turno pausado' in a.hdr() and 'Retomar turno' in a.main(), 'pausa muda selo e botão')
    a.abrir('MB-01'); print('   MB-01 pausado:', [l for l in a.main().split('\n') if 'Turno' in l or 'turno' in l], '| foot', a.foot())
    a.abrir('MB-03'); a.clk('Retomar turno'); print('   retomado: hdr', a.hdr(), a.toast())
    # erros vazios
    a.clk('Fechar turno', wait=.4); print('   vazio alerts:', a.alerts(), '| toast', a.toast())
    a.ok('Informe os hectares' in a.alerts() and 'Informe as horas' in a.alerts(), 'vazio: erros junto aos campos')
    a.setv('#ft_ha', '170'); a.setv('#ft_h', '5'); a.clk('Fechar turno', wait=.4); print('   170 alerts:', a.alerts())
    a.ok('Máximo 160 ha' in a.alerts(), '170 ha recusado (saldo 160)')
    a.setv('#ft_ha', '50'); a.setv('#ft_c0', '400'); a.clk('Fechar turno', wait=.4); al = a.alerts(); print('   consumo 400 alerts:', al)
    a.ok('Acima do que está com você: 320 L' in al, 'consumo acima da custódia recusado junto ao campo')
    a.shot('ver_appv3_mb03_erros.png')
    a.setv('#ft_c0', '100'); a.setv('#ft_obs', 'teste obs'); a.clk('Sem sinal'); a.clk('Fechar turno', wait=.5); print('   toast', a.toast())
    print('   resumo:', a.main()[:600].replace('\n', ' / '))
    ap = a.cen(f"c.ordens['{OS}'].ap"); print('   ap:', ap)
    a.ok(ap and ap[-1]['cons'].get('Glifosato 480') == 100 and ap[-1]['obs'] == 'teste obs', 'consumo editado e obs gravados')
    a.clk('Com sinal', wait=.5); print('   após sinal:', a.main()[:600].replace('\n', ' / '))
    ch = a.J("[...document.querySelectorAll('main span')].map(s=>s.innerText).filter(t=>/Enviado|aguardando sinal/.test(t)).join(' | ')")
    a.ok('Enviado' in ch, 'resumo do turno muda para Enviado após o sinal: ' + ch)
    # 2º turno: 110 ha com saldo 110 => ok? saldo = 160-50 = 110
    a.clk_sel(f'button[title="Iniciar turno na {OS}"]', wait=.5)
    a.abrir('MB-01'); print('   MB-01 turno aberto:', a.hdr(), '|', [l for l in a.main().split('\n') if 'urno' in l], '| foot', a.foot(), '| corte', a.corte())
    a.shot('ver_appv3_mb01_turno.png')
    a.abrir('MB-02det'); print('   MB-02det:', a.hdr(), '| foot', a.foot(), '| corte', a.corte())
    a.abrir('MB-03'); a.setv('#ft_ha', '120'); a.setv('#ft_h', '5'); a.clk('Fechar turno', wait=.4); print('   120 alerts:', a.alerts())
    a.ok('Máximo 110 ha' in a.alerts(), '120 ha recusado (saldo 110)')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
finally:
    a.fim()
