# -*- coding: utf-8 -*-
"""CTL-2 · Frente B · início com entrega parcial no app (Chrome real, 390 px).
PRD 42.2 l.7067 e ESTOS-03: entrega parcial não libera mistura incompleta; a mesma regra da web (cenIniFalta).
Uso: python3 app_entrega_parcial_test.py   (compile antes: build.py)"""
from app_lib import App

a = App(['MB-01', 'MB-02det', 'MB-03', 'MB-05'])
CARD = "(()=>{const b=document.body.innerText; const i=b.indexOf('OS-0430 ·'); return i<0?'':b.slice(i, i+500);})()"
BTN = "!!document.querySelector('main button[title=\"Iniciar turno na OS-0430\"]')"
try:
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    a.mudar("return cenLiberar(c,'OS-0430');"); rid = a.cen("c.ordens['OS-0430'].req")
    a.mudar(f"return cenEntregar(c,'{rid}','Glifosato 480',320,'Marcos','Rui');"); a.abrir('MB-05'); a.clk('Confirmar recebimento')
    # 1 · cartão: retirada pendente, sem Iniciar; rodapé segue na OS-0421
    a.abrir('MB-01'); card = a.J(CARD)
    a.ok(f'Entrega parcial · {rid}' in card and 'Retirar no almoxarifado' in card and 'com você 320 L' in card and 'retirar 160 L' in card and 'retirar 80 L' in card
         and not a.J(BTN) and a.foot() == 'Iniciar turno · OS-0421', 'MB-01: OS-0430 com entrega parcial pede retirada e não oferece Iniciar')
    # 2 · detalhe: o que falta e com quem
    a.J("localStorage.setItem('talhao-os-mb-os','OS-0430')"); a.abrir('MB-02det'); b = a.body()
    a.ok('retirar os insumos com Rui' in b and 'Retirar 160 L com Rui' in b and 'Retirar 80 L com Rui' in b and 'Com você 320 L' in b and a.foot() == 'Retirar no almoxarifado',
         'MB-02det: FALTA "retirar os insumos com Rui", item a item, rodapé Retirar no almoxarifado')
    # 3 · MB-03 não oferece a OS-0430; o comando forçado recusa com dono e não grava
    a.abrir('MB-03'); sem_btn = not a.J(BTN)
    r = a.J("(()=>{const {cenMudar}=window.__cen; const r=cenMudar(null,c=>window.__mb.mbIniciar(c,'OS-0430')); return r.erro||'';})()")
    a.ok(sem_btn and r == f'Iniciar bloqueado: {rid} sem entrega · 2,4-D 806 160 L, Óleo mineral 80 L a entregar. Rui (almoxarife) entrega no Estoque; Marcos confirma o recebimento no app.'
         and a.cen("!c.app.turno") and a.cen("c.ordens['OS-0430'].etapa") == 'Liberadas', 'MB-03: sem botão; mbIniciar recusa com o texto da web e nada muda: ' + r[:80])
    # 4 · Rui entrega o resto: primeiro Confirmar, depois Iniciar
    a.mudar(f"cenEntregar(c,'{rid}','2,4-D 806',160,'Marcos','Rui'); return cenEntregar(c,'{rid}','Óleo mineral',80,'Marcos','Rui');"); a.abrir('MB-01')
    a.ok(a.foot() == 'Confirmar recebimento · OS-0430' and not a.J(BTN), 'resto entregue: rodapé Confirmar recebimento · OS-0430, ainda sem Iniciar')
    a.abrir('MB-05'); a.clk('Confirmar recebimento'); a.abrir('MB-03'); a.clk_sel('main button[title="Iniciar turno na OS-0430"]')
    a.ok(a.cen("c.app.turno && c.app.turno.os") == 'OS-0430' and a.cen("c.ordens['OS-0430'].etapa") == 'Em execução', 'com os três componentes confirmados o turno abre (Em execução)')
    # 5 · fracionada por turno: 20 ha consomem tudo (40/20/10 L) → próximo turno pede retirada
    a.abrir('MB-01'); a.clk('Restaurar demonstração')
    a.mudar("return cenLiberar(c,'OS-0430');"); rid = a.cen("c.ordens['OS-0430'].req")
    a.mudar(f"cenEntregar(c,'{rid}','Glifosato 480',40,'Marcos','Rui'); cenEntregar(c,'{rid}','2,4-D 806',20,'Marcos','Rui'); cenEntregar(c,'{rid}','Óleo mineral',10,'Marcos','Rui'); return cenConfirmarRecebimento(c,'{rid}');")
    a.abrir('MB-03'); a.clk_sel('main button[title="Iniciar turno na OS-0430"]'); a.setv('#ft_ha', '20'); a.setv('#ft_h', '2'); a.clk('Fechar turno')
    a.abrir('MB-01'); card = a.J(CARD)
    a.ok(a.cen(f"c.reqs['{rid}'].itens.map(i=>i.custodia).join(' ')") == '0 0 0' and f'Entrega parcial · {rid}' in card and 'retirar 280 L' in card and not a.J(BTN),
         'fracionada: após 20 ha (custódia 0/0/0) o cartão pede retirada de 280/140/70 L e não oferece Iniciar')
    a.ok(not a.erros(), 'sem erros JS ' + str(a.erros()))
    a.clk('Restaurar demonstração')
finally:
    a.fim()
