# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 6: nova ordem → aprovar → liberar (requisição sem itens?), cancelar OS-0430 liberada,
apontamento web acima da custódia (OS-0421), filtros com Nova ordem, Restaurar com filtro."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
def setsel(idx, val):
    J(f"""(()=>{{const s=document.querySelectorAll('aside[role=dialog][aria-label="Nova ordem"] select')[{idx}]; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,{json.dumps(val)});
      s.dispatchEvent(new Event('input',{{bubbles:true}})); s.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.3)
def opts(idx): return J(f"[...document.querySelectorAll('aside[role=dialog][aria-label=\"Nova ordem\"] select')[{idx}].options].map(o=>o.value+'='+o.text)")
try:
    T.abrir(wait=1.3)
    # ---- nova ordem ----
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Nova ordem'); b.click();})()"); time.sleep(.4)
    print('safras', opts(0)); so = [o for o in opts(0) if o.split('=')[0]]; setsel(0, so[0].split('=')[0])
    co = [o for o in opts(1) if o.split('=')[0]]; print('cultivos', co[:6])
    done = False
    for cv in co:
        setsel(1, cv.split('=')[0]); ao = [o for o in opts(2) if o.split('=')[0]]
        for av in ao:
            setsel(2, av.split('=')[0])
            J("(()=>{const i=document.querySelector('#nv_jan'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'2026-10-05'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.2)
            J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Emitir ordem'); b.click();})()"); time.sleep(.4)
            if not J("!!document.querySelector('aside[role=dialog][aria-label=\"Nova ordem\"]')"): done = True; break
        if done: break
    print('emitida', done, T.toast())
    nid = J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.getAttribute('aria-label'):'';})()"); print('painel', nid)
    oid = (nid or '').split(' · ')[0]
    T.btn('Revisar versão'); T.btn('Aprovar versão'); print('aprovar', T.toast())
    p = T.pan(); print('passo', p[p.find('PRÓXIMO'):][:260])
    T.btn('Liberar para execução'); p = T.pan(); print('confirmação', p[p.find('PRÓXIMO'):][:300])
    T.btn('Confirmar liberação'); print('liberar', T.toast())
    print('cen', T.cen(f"[c.ordens['{oid}'].etapa, c.ordens['{oid}'].req, JSON.stringify(c.reqs[c.ordens['{oid}'].req]||null)]"))
    print('ins painel', T.ins()[:200])
    T.fechar()
    # ---- cancelar OS-0424 (liberada, reserva de 65 L) ----
    T.ordem('OS-0424'); lr0 = T.cen("c.lotes['Fungicida A|F26-02'].reservado")
    T.btn('Cancelar sem execução'); J("(()=>{const t=document.querySelector('aside[role=dialog] textarea'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(t,'chuva'); t.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.2)
    T.btn('Confirmar cancelamento'); print('cancelar 0424', T.toast(), '| reservado lote', lr0, '->', T.cen("c.lotes['Fungicida A|F26-02'].reservado"), T.cen("c.reqs['REQ-039'].estado"))
    print('   ins', T.ins()[:260]); T.fechar()
    # ---- apontamento web acima da custódia (OS-0421: 65 L em custódia; 160 ha × 0,5 = 80 L) ----
    T.ordem('OS-0421'); T.btn('Registrar apontamento')
    J("(()=>{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==='Área feita em hectares'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'160'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"); time.sleep(.2)
    T.btn('Salvar apontamento'); p = T.pan(); print('ap 160 ha', p[p.find('PRÓXIMO'):][:420], '| toast', T.toast())
    T.fechar()
    print('erros', T.erros())
finally:
    T.fim()
