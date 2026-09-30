# -*- coding: utf-8 -*-
"""Pior caso de altura: 2 entregas a confirmar, turno aberto sem sinal com turno anterior no aparelho, recibo existente, erros no MB-03."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_appv_lib import V, precarga
a = V(); OS = 'OS-0430'
try:
    rid = precarga(a)
    a.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');")
    a.abrir('MB-05'); print('   MB-05 2 pend: foot', a.foot(), '| corte', a.corte(), '| btns', a.J("[...document.querySelectorAll('main button')].map(b=>b.innerText).join(' | ')"))
    a.shot('ver_appv6_mb05_2pend.png')
    a.clk(a.foot(), wait=.5); print('   toast', a.toast(), '| foot', a.foot())
    # confirma o 2º pelo botão do cartão (agora é o único)
    print('   2nd:', a.foot(), a.J("[...document.querySelectorAll('main button')].map(b=>b.innerText).join(' | ')"))
    a.clk(a.foot(), wait=.5); print('   toast', a.toast(), '| foot', a.foot())
    a.mudar("return cenSinal(c,true);")
    # recibo existente: 1 envio
    a.abrir('MB-01'); a.clk('Sem sinal'); a.mudar(f"cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,40,4,null,'');"); a.clk('Com sinal', wait=.4)
    a.abrir('MB-01'); a.clk('Sem sinal')
    a.mudar(f"cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,30,3,null,'');")
    a.mudar(f"return cenIniciarTurno(c,'{OS}');")
    a.mudar(f"return cenOcorrencia(c,'{OS}','Clima','texto de teste um');")
    for t in ('MB-01', 'MB-02', 'MB-02det', 'MB-03', 'MB-03x-recibo', 'MB-04', 'MB-05'):
        a.abrir(t); print('  ', t, '| corte', a.corte(), '| larg', a.larg(), '| foot', a.foot(), '| hdr', a.hdr()[:80], '| err', a.erros())
        if t in ('MB-01', 'MB-03'): a.shot(f'ver_appv6_{t}.png')
    a.abrir('MB-03'); a.setv('#ft_ha', '200'); a.setv('#ft_h', '30'); a.clk('Fechar turno', wait=.4)
    print('   MB-03 erros:', a.alerts(), '| corte', a.corte())
    a.shot('ver_appv6_MB-03_erros.png')
    print('   hint:', a.J("[...document.querySelectorAll('main span')].map(s=>s.innerText).filter(t=>/Máximo|com você/.test(t)).join(' | ')"))
finally:
    a.fim()
