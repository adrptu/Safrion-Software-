# -*- coding: utf-8 -*-
"""Passo 6b · IN-04: OS-0430 Em conferência com sobra (T1) × OS-0417 Em conferência com sobra (P1, semente): mesmo selo e mesmo atalho?"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(1440, 900); b.goto('IN-04.dc.html', wait=1.2)
SV = "[...document.querySelectorAll('svg [role=button]')]"
def pan(t):
    b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.4)
    p = b.J(f"(document.querySelector('aside[aria-label^=\"{t}\"]')||{{innerText:''}}).innerText") or ''
    lk = b.J(f"[...document.querySelectorAll('aside[aria-label^=\"{t}\"] a')].map(a=>a.innerText.trim()+' → '+a.getAttribute('href'))")
    b.J(f"{SV}.find(x=>(x.getAttribute('aria-label')||'').startsWith('{t}:')).dispatchEvent(new MouseEvent('click',{{bubbles:true}}))"); time.sleep(.3)
    return p.replace('\n', ' / '), lk
for camada in ('Integrado', 'Ordens de serviço'):
    b.clk(camada); lab = b.J(f"{SV}.map(e=>e.getAttribute('aria-label'))"); print(f'== {camada}: {lab}')
    t1, l1 = pan('T1'); p1, lp1 = pan('P1')
    print('   T1:', t1[:700]); print('   T1 links:', l1); print('   P1:', p1[:700]); print('   P1 links:', lp1)
    o30 = t1[t1.find('OS-0430 · '):]; cust = b.J("(()=>{const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'null'); const o=c&&c.ordens['OS-0430']; const r=o&&o.req&&c.reqs[o.req]; return !!(o&&o.etapa==='Em conferência'&&r&&r.itens.some(i=>i.custodia>0.001));})()")
    if cust: b.ok('Em conferência / Sobras a receber' in o30 and 'Receber sobras → EST.dc.html' in l1, f'{camada}: OS-0430 com sobra mostra "Sobras a receber" e "Receber sobras" (igual à OS-0417)', (o30[:200], l1))
    else: b.ok('Sobras a receber' not in o30 and 'Receber sobras → EST.dc.html' not in l1, f'{camada}: OS-0430 sem custódia não mostra sobras', (o30[:200], l1))
b.shot('e2e_06b_mapa_sobras.png')
er = b.erros(); b.ok(not er, 'sem erro de JS no mapa', er)
b.fim()
