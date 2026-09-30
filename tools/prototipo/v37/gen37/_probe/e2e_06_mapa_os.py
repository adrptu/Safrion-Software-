# -*- coding: utf-8 -*-
"""Passo 6 · IN-04 (Mapa), camada Ordens de serviço: a OS-0430 aparece no T1 na mesma fase do cenário (lida na O.S.)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 900); OS = 'OS-0430'
b.goto('IN-04.dc.html', wait=1.2)
LS = "(JSON.parse(localStorage.getItem('talhao-os-cenario-v1'))||{ordens:{'OS-0430':{etapa:'A liberar',realizado:0,saldo:160}}})"
fase = b.J(f"{LS}.ordens['{OS}'].etapa"); real = b.J(f"(()=>{{const c={LS}; return [c.ordens['{OS}'].realizado, c.ordens['{OS}'].saldo];}})()"); print('   cenário:', fase, real)
print('   camadas:', b.btns()[:30])
r = b.clk('Ordens de serviço'); print('   camada:', r)
SV = "[...document.querySelectorAll('svg [role=button]')]"
lab = b.J(f"{SV}.map(e=>e.getAttribute('aria-label'))"); print('   polígonos:', lab)
b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('T1:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
p = b.J("(document.querySelector('aside[aria-label^=\"T1\"]')||{innerText:''}).innerText") or ''
i = p.find(OS + ' · Dessecação'); o = p[i:i + 220].replace('\n', ' / '); print('   painel T1:', p[:900].replace('\n', ' / '))
print('   OS-0430 no painel:', o)
b.ok(i >= 0, 'OS-0430 aparece no painel do T1 (camada Ordens de serviço)', p[:300])
b.ok(fase in o, f'fase no mapa igual à do cenário ({fase})', o)
b.ok(f'{real[0]:g}/160 ha' in o.replace(' ', '') or f'{real[0]:g} / 160 ha' in o or f'{real[0]:g}/160' in o.replace(' ', ''), f'realizado no mapa igual ao cenário ({real[0]} ha)', o)
b.shot(f'e2e_06_mapa_{fase.replace(" ", "_")}.png')
er = b.erros(); b.ok(not er, 'sem erro de JS no mapa', er)
b.fim()
