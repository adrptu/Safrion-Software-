# -*- coding: utf-8 -*-
"""Passo 14 · Restaurar demonstração pela O.S. e conferir o Mapa com a OS-0430 em A liberar / Aguardando agrônomo."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); b.goto('OS.dc.html'); b.clk('Restaurar demonstração'); b.clk('Restaurar'); print('   ', b.toast(), '| linha:', b.rowtxt('OS-0430'))
b.size(1440, 900); b.goto('IN-04.dc.html', wait=1.2); b.clk('Ordens de serviço')
SV = "[...document.querySelectorAll('svg [role=button]')]"
b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
p = (b.J("(document.querySelector('aside[aria-label^=\"T1\"]')||{innerText:''}).innerText") or '').replace('\n', ' / '); i = p.find('OS-0430 · Dessecação'); o = p[i:i + 200]; print('   mapa:', o)
h = b.J("document.querySelector('header').innerText.replace(/\\s+/g,' ')"); print('   cabeçalho:', h[-80:])
b.ok('A liberar' in o and 'Aguardando agrônomo' in o and '3 decisões pendentes' in h, 'Mapa após restaurar: OS-0430 A liberar · Aguardando agrônomo; 3 decisões pendentes', (o, h[-80:]))
b.fim()
