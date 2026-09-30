# -*- coding: utf-8 -*-
"""App de campo × cenário compartilhado (Chrome real, 15 verificações). Pré-carga na própria página por cenMudar:
aprovar e liberar a OS-0430 (Marcos) e entregar os 3 itens da requisição. Depois, pelas telas do app:
confirmar recebimento (MB-05) → iniciar turno (MB-03) → sem sinal → fechar turno 60 ha (fila 1, realizado não muda) →
sinal volta (realizado 60, sem duplicar) → novo turno (pausar/retomar) de 110 ha recusado junto ao campo → ocorrência registrada (MB-04)
→ Restaurar demonstração (MB-01).
Uso: python3 app_cenario_test.py   (compile antes: areas.mobile.build())"""
import time
from app_lib import App

a = App(['MB-01', 'MB-02det', 'MB-03', 'MB-04', 'MB-05'])
OS = 'OS-0430'
try:
    a.abrir('MB-01')
    r1 = a.mudar(f"c.ordens['{OS}'].aprov=true; return cenLiberar(c,'{OS}');")
    rid = a.cen(f"c.ordens['{OS}'].req")
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)):
        a.mudar(f"return cenEntregar(c,'{rid}','{prod}',{q},'Marcos');")
    print('   pré-carga:', r1[:90], '·', rid)
    a.abrir('MB-01'); b = a.body()
    a.ok(f'{OS} · Dessecação pré-plantio' in b and 'Entregue por Rui · ' + rid in b and a.foot() == f'Confirmar recebimento · {OS}',
         f'MB-01: {OS} na fila com retirada a confirmar e rodapé "Confirmar recebimento" ({a.foot()})')
    a.ok(a.over() <= 0, f'MB-01 com 3 ordens cabe na altura (excesso {a.over()} px)')

    a.abrir('MB-05'); b = a.body()
    a.ok('lote G26-14' in b and '16 × galão 20 L' in b and '8 × galão 20 L' in b and '4 × galão 20 L' in b,
         'MB-05: itens entregues com lote e embalagem')
    a.clk('Confirmar recebimento')
    a.ok(a.cen(f"c.reqs['{rid}'].itens.every(i=>i.confirmado)") and 'Recebimento confirmado' in a.toast(),
         'MB-05: confirmar recebimento grava no cenário: ' + a.toast()[:70])

    a.abrir('MB-03')
    a.clk_sel(f'button[title="Iniciar turno na {OS}"]')
    a.ok(a.cen("c.app.turno && c.app.turno.os") == OS and a.cen(f"c.ordens['{OS}'].etapa") == 'Em execução' and a.foot() == 'Fechar turno',
         f'MB-03: turno iniciado na {OS} (Em execução) e rodapé "Fechar turno"')

    a.clk('Sem sinal')
    a.setv('#ft_ha', '60'); a.setv('#ft_h', '5')
    a.ok(a.cen("c.app.online") is False and a.J("document.querySelector('#ft_c0').value") == '120',
         'sem sinal e consumo pré-calculado (2 L/ha × 60 ha = 120 L)')
    a.clk('Fechar turno')
    a.ok(a.cen("c.app.fila.length") == 1 and a.cen(f"c.ordens['{OS}'].realizado") == 0 and '1 registro aguardando sinal' in a.body()
         and a.cen(f"c.ordens['{OS}'].etapa") == 'Em execução',
         'fechar 60 ha sem sinal: fila 1, realizado não muda, O.S. segue Em execução')

    a.clk('Com sinal'); t = a.toast()
    a.ok(a.cen(f"c.ordens['{OS}'].realizado") == 60 and a.cen("c.app.fila.length") == 0 and 'recibo REC-7742' in t,
         'sinal volta: realizado 60 e recibo exibido · ' + t[:80])
    a.clk('Sem sinal'); a.clk('Com sinal')
    a.ok(a.cen(f"c.ordens['{OS}'].realizado") == 60 and a.cen(f"c.ordens['{OS}'].ap.length") == 1 and a.cen("(c.app.recibos||[]).length") == 1,
         'sem duplicar: novo sinal não soma de novo nem cria outro recibo')

    a.clk_sel(f'button[title="Iniciar turno na {OS}"]')
    a.clk('Pausar turno'); pz = 'Turno pausado' in a.body() and a.cen("c.app.turno.pausas.length") == 1
    a.clk('Retomar turno')
    a.ok(pz and 'Turno aberto' in a.body() and a.cen("!!c.app.turno.pausas[0].fim"), 'novo turno: pausar e retomar mudam o selo e ficam no turno')
    a.setv('#ft_ha', '110'); a.setv('#ft_h', '5'); a.clk('Fechar turno')
    al = a.J("[...document.querySelectorAll('main [role=alert]')].map(x=>x.innerText).join(' | ')")
    a.ok('Máximo 100 ha' in al and a.cen("!!c.app.turno") and a.cen(f"c.ordens['{OS}'].realizado") == 60,
         'fechar 110 ha recusado junto ao campo (saldo 100 ha): ' + al[:90])

    a.abrir('MB-04')
    a.setv('#oc_txt', 'Vento acima de 10 km/h às 10:30; parei a barra 20 min.'); a.clk('Registrar ocorrência')
    a.ok(a.cen(f"c.ocorr.length===1 && c.ocorr[0].os==='{OS}'") and 'OC-501' in a.body() and 'Registrada na O.S.' in a.body(),
         f'MB-04: ocorrência OC-501 registrada na {OS}')

    a.abrir('MB-02det'); b = a.body()
    a.ok(f'{OS} · Dessecação' in b and '60 ha em 5 h' in b and 'OC-501' in b and a.foot() == 'Fechar turno',
         'MB-02det: apontamento enviado, ocorrência e próximo passo da ordem')
    errs = []
    for t in ('MB-03', 'MB-05', 'MB-01'):
        a.abrir(t); errs += a.erros() or []
    a.ok(not errs, f'sem erros JS {errs}')
    a.clk('Restaurar demonstração')
    a.ok(a.cen(f"c.ordens['{OS}'].etapa") == 'A liberar' and a.cen("!c.app.turno && c.app.fila.length===0 && c.ocorr.length===0")
         and f'{OS} · Dessecação' not in a.body() and a.foot() == 'Iniciar turno · OS-0421', 'Restaurar demonstração volta o cenário ao início (cenReset)')
finally:
    a.fim()
