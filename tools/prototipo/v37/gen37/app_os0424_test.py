# -*- coding: utf-8 -*-
"""OS-0424-app × REQ-039 do cenário (Chrome real, ≤ 15 verificações): reservado → entregue por Rui (cenEntregar na página) →
confirmar recebimento sem sinal (fila do aparelho) → fichas do caldeiro seguem → sinal volta. A ficha impressa não muda.
Uso: python3 app_os0424_test.py   (compile antes: areas.os_campo.build())"""
from app_lib import App

a = App(['OS-0424-app', 'OS-0424-ficha', 'MB-01'])
try:
    a.abrir('OS-0424-app'); b = a.body()
    a.ok('Reservado · retire com Rui no almoxarifado' in b and a.J("document.querySelector('main').nextElementSibling.innerText.trim()") == 'Retirar no almoxarifado',
         'antes da entrega: retirada reservada e botão "Retirar no almoxarifado"')
    a.clk('Retirar no almoxarifado')
    a.ok('Nada entregue ainda' in a.toast() and a.cen("c.reqs['REQ-039'].itens[0].confirmado") is False, 'sem entrega o app não confirma nada: ' + a.toast()[:60])
    print('   pré-carga:', a.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');")[:80], '·', a.mudar("return cenSinal(c,false);")[:40])
    a.abrir('OS-0424-app'); b = a.body()
    a.ok('Entregue por Rui · confirme o recebimento' in b and 'F26-02' in b and '13 × galão 5 L' in b, 'entregue: mostra lote e embalagem da REQ-039')
    a.clk('Confirmar recebimento'); b = a.body()
    a.ok(a.cen("c.reqs['REQ-039'].itens[0].confirmado") is True and a.cen("c.app.fila.length") == 1 and 'aguardando sinal' in b,
         'confirmar sem sinal grava no cenário e vai para a fila do aparelho')
    a.ok('Carga 1 de 3' in b and 'Carga 1 preparada' in a.J("document.querySelector('main').nextElementSibling.innerText"),
         'fichas do caldeiro seguem: carga a carga depois do recebimento')
    a.abrir('MB-01'); a.clk('Com sinal')
    a.ok(a.cen("c.app.fila.length") == 0 and 'recibo REC-7742' in a.toast(), 'sinal volta no app: recebimento enviado uma vez')
    a.abrir('OS-0424-app')
    a.ok('conferido com Rui' in a.body() and 'aguardando sinal' not in a.body(), 'OS-0424-app mostra recebido e enviado')
    a.abrir('OS-0424-ficha'); b = a.body()
    a.ok('REQ-039' in b and 'F26-02' in b and 'Recebido por (caldeiro)' in b, 'ficha impressa mantém retirada, lote e assinaturas')
    a.ok(not a.erros(), 'sem erros JS')
finally:
    a.fim()
