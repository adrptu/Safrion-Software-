# -*- coding: utf-8 -*-
"""Verificador App 12 (rodada nova): jornada OS-0430 pela interface — confirmar sem sinal, turno sem sinal, 2º turno acima do resta, consumo acima da custódia, sinal volta."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
OS = 'OS-0430'
try:
    v.abrir('MB-01')
    print('  pre:', v.mudar(f"c.ordens['{OS}'].aprov=true; return cenLiberar(c,'{OS}');")[:100])
    rid = v.cen(f"c.ordens['{OS}'].req"); print('  rid', rid)
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)):
        print('  ent:', v.mudar(f"return cenEntregar(c,'{rid}','{prod}',{q},'Marcos');")[:80])
    v.abrir('MB-01'); b = v.body()
    i = b.find(OS + ' ·'); print('  card:', b[i:i + 420].replace('\n', ' / '))
    print('  hdr:', v.hdr(), '| foot:', v.foot(), '| corte', v.corte())
    v.ok(v.foot() == f'Confirmar recebimento · {OS}', 'MB-01 rodapé Confirmar recebimento')
    # rodapé leva a MB-05
    v.clk(f'Confirmar recebimento · {OS}'); time.sleep(1.2)
    v.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")
    print('  url:', v.J('location.pathname'), '| hdr:', v.hdr(), '| foot:', v.foot())
    print('  MB-05 main:', v.J("document.querySelector('main').innerText").replace('\n', ' / ')[:900])
    v.clk('Sem sinal'); print('  sem sinal toast:', v.toast()[:100])
    v.clk('Confirmar recebimento'); print('  confirmar toast:', v.toast()[:160])
    b = v.body(); print('  sig:', v.J("document.querySelector('[aria-live=polite]').innerText"), '| hdr', v.hdr(), '| foot', v.foot())
    print('  MB-05 after:', v.J("document.querySelector('main').innerText").replace('\n', ' / ')[:700])
    v.ok(v.cen('c.app.fila.length') == 1 and '1 registro aguardando sinal' in b, 'confirmar sem sinal: fila 1 e contador')
    v.shot('ver_app12_mb05_off.png')
    # MB-03: iniciar turno no cartão da OS-0430
    v.abrir('MB-03'); print('  MB-03 foot:', v.foot(), '| lista:', v.J("[...document.querySelectorAll('main button')].map(b=>b.title).filter(Boolean).join(' ; ')")[:300])
    r = v.clk_sel(f'button[title="Iniciar turno na {OS}"]'); print('  iniciar:', r, v.toast()[:100])
    v.ok(v.cen("c.app.turno && c.app.turno.os") == OS and v.cen(f"c.ordens['{OS}'].etapa") == 'Em execução', 'turno aberto e O.S. Em execução')
    v.setv('#ft_ha', '60')
    print('  consumo pré:', v.J("[...document.querySelectorAll('input[id^=ft_c]')].map(i=>i.id+'='+i.value).join(', ')"), '| hint ha:', v.J("document.querySelector('#ft_ha').parentElement.innerText").replace('\n', ' / '))
    v.setv('#ft_h', '5'); v.clk('Fechar turno'); print('  fechar1:', v.toast()[:160])
    b = v.body(); print('  resumo:', v.J("document.querySelector('main').innerText").replace('\n', ' / ')[:500])
    v.ok(v.cen('c.app.fila.length') == 2 and v.cen(f"c.ordens['{OS}'].realizado") == 0, 'turno 1 sem sinal: fila 2, realizado 0')
    # 2º turno sem sinal: máximo = 160 - 60 = 100
    r = v.clk_sel(f'button[title="Iniciar turno na {OS}"]'); print('  iniciar2:', r, v.toast()[:100])
    print('  hint:', v.J("document.querySelector('#ft_ha') && document.querySelector('#ft_ha').parentElement.innerText").replace('\n', ' / '))
    v.setv('#ft_ha', '120'); v.setv('#ft_h', '5'); v.clk('Fechar turno')
    print('  alerts 120ha:', v.alerts(), '| toast', v.toast()[:80])
    v.ok('Máximo 100' in v.alerts() and v.cen("!!c.app.turno"), '2º turno 120 ha recusado (resta 100)')
    # consumo acima da custódia (Glifosato com você 200 L)
    v.setv('#ft_ha', '50'); time.sleep(.2)
    print('  consumo 50ha:', v.J("[...document.querySelectorAll('input[id^=ft_c]')].map(i=>i.id+'='+i.value).join(', ')"))
    v.setv('#ft_c0', '250'); v.clk('Fechar turno'); print('  alerts cons:', v.alerts())
    v.ok('Acima do que está com você' in v.alerts() and v.cen("!!c.app.turno"), 'consumo acima da custódia recusado junto ao campo')
    v.setv('#ft_c0', '100'); v.setv('#ft_h', '0'); v.clk('Fechar turno'); print('  alerts h0:', v.alerts())
    v.setv('#ft_h', '4,5'); v.clk('Fechar turno'); print('  fechar2:', v.toast()[:160])
    print('  fila:', v.cen('c.app.fila'), '| sig:', v.J("document.querySelector('[aria-live=polite]').innerText"))
    v.shot('ver_app12_mb03_off2.png')
    # sinal volta
    v.clk('Com sinal'); t = v.toast(); print('  com sinal:', t[:200])
    print('  realizado/saldo:', v.cen(f"[c.ordens['{OS}'].realizado,c.ordens['{OS}'].saldo, c.app.fila.length, (c.app.recibos||[]).map(r=>r.id+':'+r.n).join(',')]"))
    v.ok(v.cen(f"c.ordens['{OS}'].realizado") == 110 and v.cen('c.app.fila.length') == 0, 'sinal volta: realizado 110, fila 0')
    v.clk('Sem sinal'); v.clk('Com sinal'); print('  2x:', v.toast()[:100], v.cen(f"[c.ordens['{OS}'].realizado,(c.app.recibos||[]).length]"))
    print('  movs app:', v.cen("c.movs.filter(m=>m.origem==='app').map(m=>m.id+' '+m.tipo+' '+m.sinc+' '+(m.det||'')).join(' | ')"))
    print('  custódia:', v.cen(f"c.reqs['{rid}'].itens.map(i=>i.prod+' '+i.custodia+' cons '+i.consumido).join(' | ')"))
    v.abrir('MB-01'); b = v.body(); i = b.find(OS + ' ·'); print('  MB-01 card:', b[i:i + 420].replace('\n', ' / '), '| hdr', v.hdr(), '| foot', v.foot())
    v.ok(not v.erros(), 'sem erros JS')
finally:
    v.fim()
