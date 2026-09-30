# -*- coding: utf-8 -*-
"""Item 2 · OS-0430 Liberada sem entrega (rodar depois do e2e_01) e OS-0424 (REQ-039 reservada): o caminho ao Estoque aparece uma vez só (impedimento "Entregar no Estoque"), sem "Retirar no almoxarifado" duplicado."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
b.goto('OS.dc.html')
for OS in ('OS-0430', 'OS-0424'):
    b.J("(()=>{const x=document.querySelector('aside[role=dialog] button[aria-label=\"Fechar\"]'); if(x) x.click();})()")
    b.row(OS); lk = b.links('aside[role=dialog]'); p = b.aside().upper(); print('  ', OS, lk)
    est = [l for l in lk if l.endswith('EST.dc.html')]
    b.ok(len(est) == 1 and est[0].startswith('Entregar no Estoque') and 'FICHAS DE EXECUÇÃO' in p, f'{OS}: com saldo a entregar, um só link ao Estoque (Entregar no Estoque) e as fichas', lk)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
