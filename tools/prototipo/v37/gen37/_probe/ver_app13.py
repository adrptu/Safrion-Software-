# -*- coding: utf-8 -*-
"""Verificador App 13: MB-04 (erro, voz, foto, ordem, sem sinal), MB-03x-recibo (reenviar sem sinal, recibos), MB-02det da OS-0430, pausar/retomar, fechar pausado."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
OS = 'OS-0430'
M = lambda: v.J("document.querySelector('main').innerText").replace('\n', ' / ')
try:
    v.abrir('MB-01')
    v.mudar(f"c.ordens['{OS}'].aprov=true; return cenLiberar(c,'{OS}');"); rid = v.cen(f"c.ordens['{OS}'].req")
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)):
        v.mudar(f"return cenEntregar(c,'{rid}','{prod}',{q},'Marcos');")
    v.mudar(f"return cenConfirmarRecebimento(c,'{rid}');")
    # MB-01: Abrir ordem do cartão da OS-0430
    v.abrir('MB-01'); r = v.clk_sel(f'main a[title^="Abrir a {OS}"]'); time.sleep(1.2)
    v.J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(e.message));")
    print('  det:', r, v.J('location.pathname'), '| hdr:', v.hdr(), '| foot:', v.foot(), '| title', v.J('document.title'))
    print('  det main:', M()[:1100])
    v.ok(OS in v.hdr() and v.foot() == f'Iniciar turno · {OS}', 'MB-02det abre OS-0430 com Iniciar turno')
    v.clk(f'Iniciar turno · {OS}'); print('  det iniciar:', v.toast()[:100], '| foot:', v.foot(), '| hdr', v.hdr())
    v.ok(v.cen('c.app.turno && c.app.turno.os') == OS and v.foot() == 'Fechar turno', 'det: iniciar na própria tela e rodapé Fechar turno')
    # MB-03: pausar, fechar pausado
    v.abrir('MB-03'); print('  MB-03 hdr:', v.hdr(), '| foot:', v.foot())
    v.clk('Pausar turno'); print('  pausar:', v.toast()[:80], '| hdr', v.hdr(), '| chips', M()[:400])
    v.setv('#ft_ha', '30'); v.setv('#ft_h', '3'); v.clk('Fechar turno'); print('  fechar pausado:', v.toast()[:160], v.cen('c.app.turno'))
    # MB-04 sem sinal
    v.abrir('MB-04'); print('  MB-04 hdr:', v.hdr(), '| ordens:', v.J("[...document.querySelectorAll('[aria-label=\"Ordem da ocorrência\"] button')].map(b=>b.innerText+'='+b.getAttribute('aria-pressed')).join(', ')"))
    v.clk('Sem sinal'); v.clk('Registrar ocorrência'); print('  vazio:', v.alerts(), '|', v.toast()[:80])
    v.ok('Descreva' in v.alerts() and v.cen('c.ocorr.length') == 0, 'MB-04 descrição vazia: erro junto ao campo')
    v.clk('Ditar (simulado)'); print('  voz:', v.J("document.querySelector('#oc_txt').value"), '|', v.toast()[:80])
    v.clk('Anexar foto (simulado)'); print('  foto:', v.toast()[:80], '|', M()[-160:])
    v.clk('Clima'); v.clk('OS-0421 · T1+T2')
    v.clk('Registrar ocorrência'); print('  reg:', v.toast()[:120], '| hdr', v.hdr(), '| foot', v.foot())
    print('  MB-04 depois:', M()[:700])
    v.ok(v.cen('c.ocorr.length') == 1 and v.cen('c.ocorr[0].os') == 'OS-0421' and v.cen('c.ocorr[0].tipo') == 'Clima' and v.cen('c.ocorr[0].sinc') is False, 'ocorrência sem sinal: OS-0421 Clima no aparelho')
    v.clk('Nova ocorrência'); print('  nova:', v.hdr(), '| sel:', v.J("[...document.querySelectorAll('[aria-pressed=true]')].map(b=>b.innerText).join(', ')"), '| txt', v.J("document.querySelector('#oc_txt').value"))
    v.setv('#oc_txt', 'Segunda ocorrência'); v.clk('Registrar ocorrência')
    v.clk('Nova ocorrência'); v.setv('#oc_txt', 'Terceira ocorrência'); v.clk('Registrar ocorrência')
    print('  3 ocorr:', M()[:900], '| corte', v.corte())
    # MB-03x-recibo com fila
    v.abrir('MB-03x-recibo'); print('  rec hdr:', v.hdr(), '| foot:', v.foot()); print('  rec main:', M()[:900])
    v.clk('Reenviar pendentes'); print('  reenviar sem sinal:', v.toast()[:160], v.cen('c.app.fila.length'))
    v.clk('Com sinal'); print('  com sinal:', v.toast()[:160]); print('  rec depois:', M()[:900], '| foot', v.foot(), '| corte', v.corte())
    v.ok(v.cen('c.app.fila.length') == 0 and v.cen('c.ocorr.every(o=>o.sinc)'), 'sinal volta: ocorrências enviadas')
    v.shot('ver_app13_rec.png')
    v.abrir('MB-02det'); print('  det OS sel:', v.hdr(), '| main', M()[:1200], '| corte', v.corte())
    v.ok(not v.erros(), 'sem erros JS ' + str(v.erros()))
finally:
    v.fim()
