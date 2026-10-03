# -*- coding: utf-8 -*-
"""O.S. · liberar ordem nova (verificador v39, itens 1 e 5): ordem sem insumos libera sem requisição; ordem do plano leva os insumos
da atividade (dose × área) e a requisição nova segue o formato REQ-041, REQ-042 (três dígitos, sem pular)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
T = Os(); J = T.J
NV = 'aside[role=dialog][aria-label="Nova ordem"]'
def setv(sel, val):
    J(f"""(()=>{{const i=document.querySelector({json.dumps(sel)}); const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.3)
def nova(cult, atv, jan='2026-10-05'):
    T.btn('Nova ordem', root='main'); setv('#nv_saf', 'S2627'); setv('#nv_cult', cult); setv('#nv_atv', atv); setv('#nv_jan', jan)
    T.btn('Emitir ordem', root=NV)
    return (J("(()=>{const a=document.querySelector('aside[role=dialog]'); return a?a.getAttribute('aria-label'):'';})()") or '').split(' · ')[0]
def pedir_liberar():  # O.S. sem revisão (01/10): o agrônomo libera direto
    T.btn('Liberar para execução')
try:
    T.abrir(wait=1.3)
    n0 = T.cen("Object.keys(c.reqs).length")
    # ---- 1) ordem sem insumos (colheita): libera sem requisição ----
    oid = nova('c1', 'a8'); p = T.pan()
    T.ok(oid == 'OS-0440' and 'Sem insumos' in p, 'nova ordem de colheita nasce sem insumos', (oid, p[:200]))
    pedir_liberar(); p = T.pan()
    T.ok('sem insumos a reservar' in p and 'nenhum insumo' not in p and 'por lote:' not in p, 'confirmação diz que não há insumo a reservar', p[p.find('PRÓXIMO'):][:300])
    T.btn('Confirmar liberação'); t = T.toast(); p = T.pan()
    T.ok('OS-0440 liberada' in t and 'REQ' not in t and 'reservou' not in t, 'toast sem requisição vazia', t)
    T.ok(T.cen("c.ordens['OS-0440'].req") is None and T.cen("Object.keys(c.reqs).length") == n0 and not T.cen("Object.values(c.reqs).some(r=>!r.itens.length)"),
         'cenário: nenhuma requisição vazia', T.cen("JSON.stringify(Object.values(c.reqs).map(r=>[r.id,r.itens.length]))"))
    T.ok('Liberadas' in T.linha('OS-0440') and 'reservou' not in p, 'situação atual sem reserva que não houve', p[p.find('SITUAÇÃO ATUAL'):][:200])
    T.fechar()
    # ---- 2) ordem do plano com insumos: dose × área e REQ-041 ----
    oid = nova('c1', 'a2'); p = T.pan()
    T.ok(oid == 'OS-0441' and J("document.querySelector('aside[role=dialog]').getAttribute('aria-label')") == 'OS-0441 · Tratamento de sementes',
         'título sem repetir operação e atividade', J("document.querySelector('aside[role=dialog]').getAttribute('aria-label')"))
    T.ok('Fungicida TS' in p and '0,1 L/ha' in p and '16 L' in p and 'Inoculante líquido' in p and '32 L' in p, 'insumos do plano com dose e total da ordem', T.ins()[:300])
    T.ok('Gatilho' .upper() in p and 'Tratamento de sementes' in p and 'OPERAÇÃO —' not in p, 'atividade preenchida pelo plano', p[p.find('ATIVIDADE'):][:260])
    pedir_liberar(); p = T.pan()
    T.ok('por lote: Fungicida TS 16 L, Inoculante líquido 32 L' in p, 'confirmação lista a reserva por lote', p[p.find('PRÓXIMO'):][:300])
    T.btn('Confirmar liberação'); t = T.toast()
    T.ok('REQ-041 reservou no Estoque: Fungicida TS 16 L, Inoculante líquido 32 L' in t, 'requisição nova com três dígitos: REQ-041', t)
    T.ok(T.cen("c.lotes['Fungicida TS|FT26-09'].reservado") == 16 and 'REQ-041' in T.ins(), 'reserva no lote e situação do insumo com REQ-041', (T.cen("c.lotes['Fungicida TS|FT26-09'].reservado"), T.ins()[:260]))
    T.fechar()
    # ---- 3) a próxima liberação segue a sequência (OS-0430 → REQ-042) ----
    T.ordem('OS-0430'); pedir_liberar(); T.btn('Confirmar liberação'); t = T.toast()
    T.ok('REQ-042 reservou' in t and T.cen("c.ordens['OS-0430'].req") == 'REQ-042', 'sequência contínua: OS-0430 recebe REQ-042', t)
    T.fechar()
    T.ok(not T.erros(), 'sem erro JS', T.erros())
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
