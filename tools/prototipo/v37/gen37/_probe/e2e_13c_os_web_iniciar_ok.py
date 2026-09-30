# -*- coding: utf-8 -*-
"""Passo 13c · OS.dc.html (web): OS-0430 Liberada. Uso: python3 e2e_13c_os_web_iniciar_ok.py entregue|confirmado [iniciar]
entregue   = depois do e2e_02 (Estoque entregou, app ainda não confirmou): início bloqueado, nomeia a confirmação no app.
confirmado = depois do e2e_03a (app confirmou): "Iniciar execução" liberado; a confirmação diz a verdade; com 'iniciar', confirma o início."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
fase = sys.argv[1] if len(sys.argv) > 1 else 'entregue'; ini = 'iniciar' in sys.argv[2:]
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('OS.dc.html'); b.row(OS); p = b.aside(); bt = b.btns('aside[role=dialog]')
print('   próximo:', p[p.find('PRÓXIMO'):][:420]); print('   botões:', bt)
if fase == 'entregue':
    b.ok('Iniciar execução' not in bt and 'Iniciar bloqueado' in p and 'entregues a Marcos, aguardando confirmação no app' in p and 'Marcos confirma o recebimento no app' in p,
         'entregue sem confirmação: início bloqueado e o próximo passo é a confirmação no app', p[p.find('PRÓXIMO'):][:400])
    b.ok(any(l.startswith('Ver no app') and l.endswith('→ MB-05.dc.html') for l in b.links('aside[role=dialog]')), 'atalho "Ver no app" → MB-05', b.links('aside[role=dialog]'))
else:
    b.ok('Iniciar execução' in bt and 'Iniciar bloqueado' not in p, 'confirmado no app: "Iniciar execução" liberado', bt)
    b.clk('Iniciar execução', 'aside[role=dialog]'); p = b.aside()
    b.ok('insumos com Marcos, confirmados no app' in p and 'máquina, equipe e insumos confirmados' not in p, 'confirmação do início descreve os insumos confirmados no app', p[p.find('PRÓXIMO'):][:400])
    if ini:
        b.clk('Confirmar início', 'aside[role=dialog]'); st = b.cen(f"c.ordens['{OS}'].etapa"); print('   toast:', b.toast(), '|', st)
        b.ok(st == 'Em execução', 'Confirmar início grava Em execução', st)
    else:
        b.clk('Voltar', 'aside[role=dialog]')
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
