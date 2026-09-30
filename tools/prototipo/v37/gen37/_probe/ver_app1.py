# -*- coding: utf-8 -*-
"""Verificador App 1: MB-01 fila, sinal, iniciar pelo cartão/rodapé, passo com outro turno aberto, MB-02det por ordem escolhida."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_app_lib import V
v = V()
try:
    v.abrir('MB-01')
    v.clk('Sem sinal')
    v.ok(v.cen('c.app.online') is False and 'Nada aguardando sinal' in v.body(), 'MB-01 sem sinal: online=false, contador zero')
    print('   aria:', v.J("[...document.querySelectorAll('[role=group] button')].map(b=>b.innerText+'='+b.getAttribute('aria-pressed')).join(', ')"), '| toast:', v.toast()[:80])
    v.clk('Com sinal'); print('   com sinal toast:', v.toast()[:90])
    # iniciar pelo botão do cartão
    r = v.clk_sel('main button[title="Iniciar turno na OS-0421"]')
    b = v.body(); print('   click cartão:', r, '| toast:', v.toast()[:80])
    v.ok(v.cen("c.app.turno && c.app.turno.os") == 'OS-0421' and 'Turno aberto · desde' in b and v.foot() == 'Fechar turno · OS-0421',
         'cartão Iniciar turno abre o turno e o rodapé vira Fechar turno · OS-0421 (' + v.foot() + ')')
    print('   hdr:', v.hdr())
    # entregar REQ-039 (OS-0424) com turno aberto
    print('   entrega:', v.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');")[:80])
    v.abrir('MB-01'); b = v.body()
    v.ok('Entregue por Rui · REQ-039' in b and 'entregue 65 L · a confirmar' in b and v.foot() == 'Fechar turno · OS-0421', 'OS-0424 entregue: passo Confirmar recebimento; rodapé segue no turno aberto')
    # abrir detalhe da OS-0424 pelo cartão
    v.clk_sel('main a[title^="Abrir a OS-0424"]'); time.sleep(1.2)
    v.J("window.__errs=[]")
    print('   MB-02det OS-0424 hdr:', v.hdr(), '| foot:', v.foot())
    v.ok('OS-0424' in v.hdr() and v.foot() == 'Confirmar recebimento', 'MB-02det abre a ordem escolhida (OS-0424) com rodapé Confirmar recebimento')
    print('   det body:', v.J("document.querySelector('main').innerText").replace('\n', ' / ')[:900])
    # confirmar e ver o passo com outro turno aberto
    print('   confirmar:', v.mudar("return cenConfirmarRecebimento(c,'REQ-039');")[:80])
    v.abrir('MB-02det'); f = v.foot(); print('   MB-02det OS-0424 com turno da OS-0421 aberto -> rodapé:', f, '| selo:', v.J("document.querySelector('main').innerText").split('\n')[:14])
    v.clk(f); t = v.toast(); print('   clicar rodapé ->', t[:120])
    v.ok(v.cen("c.app.turno.os") == 'OS-0421', 'o turno aberto continua na OS-0421')
    v.abrir('MB-01'); b = v.body(); print('   MB-01 cartão OS-0424:', b[b.find('OS-0424 ·'):b.find('OS-0424 ·') + 260].replace('\n', ' / '))
    r = v.clk_sel('main button[title="Iniciar turno na OS-0424"]'); print('   cartão Iniciar turno OS-0424:', r, '->', v.toast()[:120])
    v.ok(not v.erros(), 'sem erros JS ' + str(v.erros()))
    v.shot('ver_app1_mb01.png')
    # rodapé Iniciar turno (botão) após restaurar
    v.clk('Restaurar demonstração'); print('   restaurar:', v.toast()[:80], '| foot:', v.foot())
    v.clk('Iniciar turno · OS-0421'); print('   rodapé iniciar ->', v.toast()[:80], '| foot:', v.foot())
    v.ok(v.cen("c.app.turno && c.app.turno.os") == 'OS-0421' and v.foot() == 'Fechar turno · OS-0421', 'rodapé Iniciar turno executa na própria tela')
    v.clk('Restaurar demonstração')
finally:
    v.fim()
