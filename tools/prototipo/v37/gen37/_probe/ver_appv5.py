# -*- coding: utf-8 -*-
"""OS-0424-app × REQ-039: reservado → entregue → confirmar sem sinal → cargas → sinal volta; MB-01/MB-05 coerentes; ficha sem erro."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_appv_lib import V
a = V()
FOOT = "(()=>{const m=document.querySelector('main'); return m.nextElementSibling.innerText.trim();})()"
try:
    a.abrir('OS-0424-app'); print('   ret:', a.main()[:200].replace('\n', ' / '), '| foot', a.J(FOOT))
    a.clk('Retirar no almoxarifado'); print('   toast', a.toast())
    a.ok(a.cen("c.reqs['REQ-039'].itens[0].confirmado") is False, 'retirar sem entrega não muda')
    print('   entrega:', a.mudar("return cenEntregar(c,'REQ-039','Fungicida A',65,'Marcos');"))
    a.abrir('MB-01'); m = a.main(); print('   MB-01:', [l for l in m.split('\n') if 'REQ-039' in l or 'confirmar' in l.lower() or 'Confirmar' in l], '| foot', a.foot(), '| hdr', a.hdr())
    a.ok(a.foot() == 'Confirmar recebimento · OS-0424', 'MB-01 rodapé confirmar OS-0424')
    a.abrir('MB-05'); print('   MB-05:', a.main()[:700].replace('\n', ' / '), '| foot', a.foot())
    a.abrir('OS-0424-app'); print('   entregue:', a.main()[:250].replace('\n', ' / '), '| foot', a.J(FOOT))
    a.ok('Entregue por Rui · confirme o recebimento' in a.main() and a.J(FOOT) == 'Confirmar recebimento', 'OS-0424-app entregue')
    print('   off:', a.mudar("return cenSinal(c,false);"))
    a.abrir('OS-0424-app'); a.clk('Confirmar recebimento', wait=.5); print('   toast', a.toast()); print('   rec:', a.main()[:250].replace('\n', ' / '), '| foot', a.J(FOOT))
    a.ok(a.cen("c.reqs['REQ-039'].itens[0].confirmado") is True and a.cen('c.app.fila.length') == 1 and 'aguardando sinal' in a.main(), 'confirmar sem sinal vai para a fila')
    for i in range(3): a.clk(a.J(FOOT), wait=.3)
    print('   após cargas:', a.J(FOOT), '|', a.toast()); a.clk('Registrar apontamento', wait=.3); print('   apont toast:', a.toast())
    a.shot('ver_appv5_os0424_rec.png')
    a.abrir('MB-01'); print('   MB-01 off hdr', a.hdr(), '| foot', a.foot()); a.clk('Com sinal', wait=.5); print('   toast', a.toast())
    m = a.main(); print('   MB-01 cards:', [l for l in m.split('\n') if 'Fungicida' in l or 'Pronta' in l or 'Iniciar' in l], '| foot', a.foot())
    a.abrir('OS-0424-app'); print('   rec on:', a.main()[:250].replace('\n', ' / '))
    a.ok('conferido com Rui' in a.main() and 'aguardando sinal' not in a.main(), 'OS-0424-app recebido e enviado')
    a.abrir('MB-03x-recibo'); print('   3x:', [l for l in a.main().split('\n') if 'REC' in l or 'Recebimento' in l])
    a.abrir('OS-0424-ficha'); print('   ficha err', a.erros(), '| len', len(a.body()))
    a.ok(not a.erros(), 'sem erros JS')
finally:
    a.fim()
