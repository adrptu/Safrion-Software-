# -*- coding: utf-8 -*-
"""Item 1 · turno de 60 ha no aparelho sem sinal: O.S., Estoque e Mapa não mostram consumo nem baixa de custódia antes do envio."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 1000); OS = 'OS-0430'
st = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado]") if False else None
b.goto('OS.dc.html'); st = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado]"); print('   cenário (fila, realizado):', st)
b.ok(st == [1, 0], 'pré-condição: 1 registro no aparelho e 0 ha realizados', st)
lin = b.rowtxt(OS); b.row(OS); p = b.aside(); ins = p[p.upper().find('INSUMOS E DOSES'):][:900]
b.ok('0 / 160 ha' in lin and 'Aguardando sinal do app' in lin, 'OS: lista 0 / 160 ha com "Aguardando sinal do app"', lin)
b.ok('Consumido 120 L' not in ins and 'Em custódia 320 L' in ins and 'Em custódia 160 L' in ins and 'Em custódia 80 L' in ins, 'OS: insumos sem consumo e custódia 320/160/80 L até o envio', ins[:400])
b.ok(ins.count('consumo no aparelho, aguardando sinal') == 3, 'OS: situação de cada insumo diz que o consumo está no aparelho', ins[:400])
b.goto('EST.dc.html'); RQ = b.cen(f"c.ordens['{OS}'].req")
b.J("document.querySelectorAll('nav[aria-label=\"Etapas do processo\"] button')[2].click()"); time.sleep(.4)
g = b.rowtxt(RQ, 'Glifosato 480'); print('   EST:', g)
b.ok('320 L 0 L 0 L 320 L' in g and 'Aguardando sinal do app' in g, 'EST: consumido 0 L e custódia 320 L, com "Aguardando sinal do app"', g)
b.goto('IN-04.dc.html', wait=1.2); b.clk('Ordens de serviço')
SV = "[...document.querySelectorAll('svg [role=button]')]"
b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
p = (b.J("(document.querySelector('aside[aria-label^=\"T1\"]')||{innerText:''}).innerText") or '').replace('\n', ' / ')
i = p.find(OS + ' · Dessecação'); o = p[i:i + 240]; print('   Mapa:', o)
b.ok('0/160 ha' in o and '320 L + 160 L + 80 L em custódia' in o and 'aguardando sinal' in o, 'Mapa: 0/160 ha e 320 + 160 + 80 L em custódia até o envio', o)
er = b.erros(); b.ok(not er, 'sem erro de JS', er)
b.fim()
