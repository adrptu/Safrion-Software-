# -*- coding: utf-8 -*-
"""App × ordem sem saldo e turno em outra ordem (Chrome real, ≤ 15 verificações) — MB-01, MB-02det e MB-03.
Saldo 0 ha não oferece 'Iniciar turno': o próximo passo é devolver a sobra (ou aguardar o encerramento); com outro turno aberto
o passo nomeado é 'Fechar turno · <ordem aberta>' e leva ao MB-03; turno aberto numa ordem sem saldo (estado antigo) pode ser descartado.
Uso: python3 app_saldo_zero_test.py   (compile antes: areas.mobile.build())"""
from app_lib import App

a = App(['MB-01', 'MB-02det', 'MB-03', 'MB-05'])
CARD = "(()=>{const b=document.body.innerText; const i=b.indexOf('OS-0424 ·'); return b.slice(i, i+420);})()"
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    # outro turno aberto (OS-0421) e OS-0424 recebida: o cartão da OS-0424 nomeia 'Fechar turno · OS-0421' (link ao MB-03)
    a.clk_sel('button[title="Iniciar turno na OS-0421"]')
    a.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos','Rui');"); a.mudar("return cenConfirmarRecebimento(c,'REQ-039');")
    a.abrir('MB-01'); card = a.J(CARD)
    lk = a.J("[...document.querySelectorAll('main a')].filter(x=>x.innerText.trim()==='Fechar turno · OS-0421').map(x=>x.getAttribute('href')).join('|')")
    a.ok('Outro turno aberto · OS-0421' in card and 'Iniciar turno' not in card and lk == 'MB-03.dc.html',
         f'MB-01: com turno na OS-0421 a OS-0424 nomeia "Fechar turno · OS-0421" → MB-03 ({lk})')
    a.J("localStorage.setItem('talhao-os-mb-os','OS-0424')"); a.abrir('MB-02det'); b = a.body()
    a.ok(a.foot() == 'Fechar turno · OS-0421' and 'fechar o turno da OS-0421' in b and 'Iniciar turno' not in b,
         'MB-02det OS-0424: próxima ação e rodapé "Fechar turno · OS-0421" (' + a.foot() + ')')
    # fecha o turno da OS-0421 e faz a OS-0424 inteira (128 ha no T1-B desde o G1 do CTL-1; antes 80 ha no P2) pelo MB-03
    a.abrir('MB-03'); a.setv('#ft_ha', '20'); a.setv('#ft_h', '3'); a.clk('Fechar turno')
    a.clk_sel('main button[title="Iniciar turno na OS-0424"]'); a.setv('#ft_ha', '128'); a.setv('#ft_h', '6'); a.clk('Fechar turno')
    a.ok(a.cen("c.ordens['OS-0424'].saldo") == 0 and a.cen("!c.app.turno"), 'OS-0424 feita: saldo 0 ha e nenhum turno aberto')
    a.abrir('MB-01'); card = a.J(CARD)
    a.ok('Área feita · sobra com você' in card and 'Devolver sobra' in card and 'Iniciar turno' not in card,
         'MB-01: OS-0424 com saldo 0 não oferece Iniciar turno; passo "Devolver sobra"')
    a.ok(a.J("document.querySelector('main button[title=\"Iniciar turno na OS-0424\"]')") is None and a.foot() == 'Iniciar turno · OS-0421',
         'MB-01: nenhum botão Iniciar na OS-0424; rodapé segue na OS-0421 (' + a.foot() + ')')
    a.abrir('MB-02det'); b = a.body()
    a.ok(a.foot() == 'Devolver sobra' and 'devolver a sobra ao Rui: Fungicida A 1 L' in b,
         'MB-02det OS-0424: FALTA "devolver a sobra ao Rui: Fungicida A 1 L" e rodapé "Devolver sobra" (' + a.foot() + ')')
    a.abrir('MB-05')
    a.ok('área feita: devolva a sobra ao Rui' in a.body(), 'MB-05: a sobra da OS-0424 aparece em "Com você" com o passo de devolução')
    a.abrir('MB-03'); b = a.body()
    a.ok(a.J("document.querySelector('main button[title=\"Iniciar turno na OS-0424\"]')") is None and a.foot() == 'Iniciar turno · OS-0421',
         'MB-03 sem turno: a OS-0424 não é oferecida para iniciar')
    r = a.J("(()=>{const {cenMudar}=window.__cen; const r=cenMudar(null,c=>window.__mb.mbIniciar(c,'OS-0424')); return r.erro||'';})()")
    a.ok('saldo 0 ha' in r and a.cen("!c.app.turno"), 'guarda do app: iniciar sem saldo é recusado: ' + r[:70])
    # estado antigo: turno aberto numa ordem sem saldo → MB-03 oferece descartar (o operador não fica preso)
    a.mudar("c.app.turno={os:'OS-0424',ini:'10:00',pausas:[],fim:null}; return {msg:'turno antigo'};")
    a.abrir('MB-03'); b = a.body()
    a.ok(a.foot() == 'Descartar turno' and 'Saldo 0 ha: nada a apontar' in b and a.J("document.querySelector('#ft_ha')") is None,
         'MB-03 com turno numa ordem sem saldo: sem formulário e rodapé "Descartar turno" (' + a.foot() + ')')
    a.clk('Descartar turno')
    a.ok(a.cen("!c.app.turno") and 'descartado sem apontamento' in a.toast() and a.foot() == 'Iniciar turno · OS-0421',
         'Descartar turno libera o app: ' + a.toast()[:60])
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
finally:
    a.fim()
import sys; sys.exit(1 if a.FAIL else 0)   # SUP: falha sai com código ≠ 0
