# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 7: requisição vazia da nova ordem aparece no Estoque (aba real)?
E: OS-0430 em conferência com sobra — lista/Kanban mostram o bloqueio? (comparar com OS-0417)."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '_probe'))
from os_lib import Os
from ver_os_tab import Tab
T = Os(copiar=False); J = T.J
try:
    T.abrir(wait=1.3)
    # nova ordem direto no cenário pela própria função da tela não é exposta: usa a UI (safra 2026/27, cultivo c1, 1ª atividade livre)
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    def setsel(idx, val):
        J(f"""(()=>{{const s=document.querySelectorAll('aside[role=dialog][aria-label="Nova ordem"] select')[{idx}]; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(val)});
          s.dispatchEvent(new Event('input',{{bubbles:true}})); s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.3)
    setsel(0, 'S2627'); setsel(1, 'c1')
    ao = J("[...document.querySelectorAll('aside[role=dialog][aria-label=\"Nova ordem\"] select')[2].options].map(o=>o.value).filter(Boolean)")
    for av in ao:
        setsel(2, av)
        J("(()=>{const i=document.querySelector('#nv_jan'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'2026-10-05'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.2)
        J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Emitir ordem'); b.click();})()"); time.sleep(.4)
        if not J("!!document.querySelector('aside[role=dialog][aria-label=\"Nova ordem\"]')"): break
    T.btn('Revisar versão'); T.btn('Aprovar versão'); T.btn('Liberar para execução'); T.btn('Confirmar liberação'); print('liberar', T.toast()); T.fechar()
    est = Tab(T.c, f'http://127.0.0.1:{T.p}/EST.dc.html')
    t = est.js("document.body.innerText") or ''
    i = t.find('REQ-47'); print('EST mostra REQ-47?', i >= 0, '|', t[max(0, i - 200):i + 200].replace('\n', ' ') if i >= 0 else '')
    est.call('Page.captureScreenshot', {'format': 'png'})
finally:
    T.fim()
