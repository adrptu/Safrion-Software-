# -*- coding: utf-8 -*-
"""O.S. · liberar ordem nova (verificador v39, itens 1 e 5): ordem sem insumos libera sem requisição; ordem do plano leva os insumos
da atividade (dose × área) e a requisição nova segue o formato REQ-041, REQ-042 (três dígitos, sem pular).
CTL-1 (Frente F): a confirmação é "aprovar e liberar" (PRD 41.3) e grava na Origem CMD-42 (aprovada) e CMD-06 (liberada); recusa não grava."""
import sys, os, time, json, re
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
    # SINT-T01: colheita sem pendência de carência (café C1 · k4). A soja do T1 tem a OS-0421 (fungicida) em execução: a colheita lá
    # fica bloqueada pela carência em qualquer janela, o que é proteção do produto; a prova negativa está no item 4
    oid = nova('c9', 'k4'); p = T.pan()
    T.ok(oid == 'OS-0440' and 'Sem insumos' in p, 'nova ordem de colheita nasce sem insumos', (oid, p[:200]))
    pedir_liberar(); p = T.pan()
    T.ok('sem insumos a reservar' in p and 'nenhum insumo' not in p and 'por lote:' not in p, 'confirmação diz que não há insumo a reservar', p[p.find('PRÓXIMO'):][:300])
    T.ok('Ana (agrônoma) aprova esta versão e libera' in p, 'CTL-1: confirmação diz que confirmar é aprovar esta versão e liberar', p[p.find('PRÓXIMO'):][:300])
    T.btn('Confirmar liberação'); t = T.toast(); p = T.pan()
    ev = T.cen("((c.ordens['OS-0440'].osc||{}).ev||[]).map(e=>e.cmd+'|'+e.t)") or []
    T.ok(len(ev) == 2 and re.match(r'^CMD-42\|v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · [\d.,]+ ha · sem insumos \(CMD-42\)$', ev[0]) and re.match(r'^CMD-06\|v1 liberada por Ana \(agrônoma\) às \d\d:\d\d \(CMD-06\)$', ev[1])
         and 'sem insumos (CMD-42)' in p and 'reservada' not in p, 'CTL-1: sem insumos grava CMD-42 "sem insumos" e CMD-06 sem reserva, e a Origem mostra os dois', (ev, p[p.find('ORIGEM'):][:400]))
    T.ok(t.rstrip().endswith('v1 aprovada e liberada por Ana (agrônoma).'), 'CTL-1: aviso termina na aprovação (sem segundo próximo passo)', t)
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
    T.btn('Confirmar liberação'); t = T.toast(); p = T.pan()
    T.ok('REQ-041 reservou no Estoque: Fungicida TS 16 L, Inoculante líquido 32 L' in t, 'requisição nova com três dígitos: REQ-041', t)
    T.ok(t.rstrip().endswith('v1 aprovada e liberada por Ana (agrônoma).'), 'CTL-1: aviso termina em "v1 aprovada e liberada por Ana (agrônoma)."', t)
    T.ok(re.search(r'v1 aprovada por Ana \(agrônoma\) às \d\d:\d\d · 160 ha · Fungicida TS 0,1 L/ha, Inoculante líquido 0,2 L/ha \(CMD-42\)', p)
         and re.search(r'v1 liberada por Ana \(agrônoma\) às \d\d:\d\d · REQ-041 reservada no Estoque \(CMD-06\)', p), 'CTL-1: Origem com CMD-42 (área e doses) e CMD-06 (REQ-041 reservada)', p[p.find('ORIGEM'):][:500])
    T.ok(T.cen("c.lotes['Fungicida TS|FT26-09'].reservado") == 16 and 'REQ-041' in T.ins(), 'reserva no lote e situação do insumo com REQ-041', (T.cen("c.lotes['Fungicida TS|FT26-09'].reservado"), T.ins()[:260]))
    T.fechar()
    # ---- 3) a próxima liberação segue a sequência (OS-0430 → REQ-042) ----
    T.ordem('OS-0430'); pedir_liberar(); T.btn('Confirmar liberação'); t = T.toast()
    T.ok('REQ-042 reservou' in t and T.cen("c.ordens['OS-0430'].req") == 'REQ-042', 'sequência contínua: OS-0430 recebe REQ-042', t)
    T.fechar()
    # ---- 4) prova negativa: colheita da soja no T1 (OS-0421 de fungicida em execução) continua impedida de liberar ----
    oid = nova('c1', 'a8'); pedir_liberar(); p = T.pan(); T.btn('Confirmar liberação')
    T.ok(oid == 'OS-0442' and 'Liberar bloqueado: carência' in p and 'T1' in p and T.cen("c.ordens['OS-0442'].etapa") == 'A liberar', 'colheita da soja no T1 com aplicação de fungicida pendente: liberar segue bloqueado pela carência', (oid, p[p.find('PRÓXIMO'):][:300]))
    T.ok(not T.cen("((c.ordens['OS-0442'].osc||{}).ev||[]).length"), 'CTL-1: recusa pela carência não grava CMD-42 nem CMD-06', T.cen("JSON.stringify((c.ordens['OS-0442'].osc||{}).ev||[])"))
    T.fechar()
    T.ok(not T.erros(), 'sem erro JS', T.erros())
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
