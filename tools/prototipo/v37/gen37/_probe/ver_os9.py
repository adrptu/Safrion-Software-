# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 9: Nova ordem na Safrinha 2027 com o filtro Safrinha 2027 (estado vazio → 1 ordem);
situação da nova ordem liberada sem insumos."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
def filtro(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
def setsel(idx, val):
    J(f"""(()=>{{const s=document.querySelectorAll('aside[role=dialog][aria-label="Nova ordem"] select')[{idx}]; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(val)});
      s.dispatchEvent(new Event('input',{{bubbles:true}})); s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.3)
def ids(): return J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0].trim())") or []
def chips(): return J("[...document.querySelectorAll('[aria-label=\"Filtrar por fase\"] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())") or []
def vazio(): return J("(()=>{const d=document.querySelector('[aria-label=\"Sem ordens no filtro\"]'); return d?d.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
try:
    T.abrir(wait=1.3)
    filtro('Filtrar por safra', 'Safrinha 2027'); print('vazio', vazio())
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    setsel(0, 'S27SF'); co = J("[...document.querySelectorAll('aside[role=dialog][aria-label=\"Nova ordem\"] select')[1].options].map(o=>o.value+'='+o.text)"); print('cultivos safrinha', co)
    ok = False
    for cv in [x.split('=')[0] for x in co if x.split('=')[0]]:
        setsel(1, cv); ao = J("[...document.querySelectorAll('aside[role=dialog][aria-label=\"Nova ordem\"] select')[2].options].map(o=>o.value).filter(Boolean)")
        for av in ao:
            setsel(2, av)
            J("(()=>{const i=document.querySelector('#nv_jan'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'2027-02-05'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.2)
            J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Emitir ordem'); b.click();})()"); time.sleep(.4)
            if not J("!!document.querySelector('aside[role=dialog][aria-label=\"Nova ordem\"]')"): ok = True; break
        if ok: break
    print('emitida', ok, T.toast())
    T.fechar(); print('ids', ids(), '| chips', chips(), '| vazio', vazio())
    T.ordem(ids()[0] if ids() else 'OS-0440'); T.btn('Revisar versão'); T.btn('Aprovar versão'); T.btn('Liberar para execução'); T.btn('Confirmar liberação')
    p = T.pan(); print('toast', T.toast()); print('situação', p[p.find('SITUAÇÃO ATUAL'):][:200])
    print('erros', T.erros())
finally:
    T.fim()
