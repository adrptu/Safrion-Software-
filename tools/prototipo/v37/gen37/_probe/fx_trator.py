# -*- coding: utf-8 -*-
"""Item 5 · OS.dc.html: o trator do Conjunto (Atividade) é o mesmo de Recursos alocados, na OS-0430, OS-0421 e OS-0424."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000)
b.goto('OS.dc.html')
for OS in ('OS-0430', 'OS-0421', 'OS-0424'):
    b.J("(()=>{const x=document.querySelector('aside[role=dialog] button[aria-label=\"Fechar\"]'); if(x) x.click();})()")
    b.row(OS); p = b.aside(); u = p.upper()
    i = u.find('CONJUNTO'); cj = p[i:i + 90]; j = u.find('RECURSOS ALOCADOS'); rc = p[j:j + 90]
    t1 = re.findall(r'Trator \w+', cj); t2 = re.findall(r'Trator \w+', rc); print('  ', OS, '|', cj, '|', rc)
    b.ok(t1 and t1 == t2[:1], f'{OS}: mesmo trator no Conjunto e em Recursos alocados ({t1} × {t2[:1]})', (cj, rc))
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
