# -*- coding: utf-8 -*-
"""Item 1 · EST etapa 3 com o turno ainda no aparelho: a linha da OS-0430 abre só em consulta e explica o motivo."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
b.goto('EST.dc.html'); RQ = b.cen(f"c.ordens['{OS}'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
prim = b.J("[...document.querySelectorAll('button')].filter(x=>x.offsetParent&&/Receber devolução/.test(x.innerText)).map(x=>x.innerText.trim())"); print('   primário:', prim)
b.ok(not any(RQ in p for p in (prim or [])), 'primário da etapa 3 não chama a devolução da OS-0430 ainda no aparelho', prim)
b.row(RQ, 'Glifosato 480'); a = b.aside(); print('   form:', a[:400])
b.ok('aguardando sinal' in a and 'Salvar' not in b.btns('aside[role=dialog]'), 'linha abre em consulta, com o motivo (apontamento no aparelho)', (a[:300], b.btns('aside[role=dialog]')))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
