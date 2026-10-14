# -*- coding: utf-8 -*-
"""O.S. × cenário compartilhado (OS.dc.html no Chrome headless), 15 verificações · jornada da OS-0430.
Pela tela: liberar pelo agrônomo (pode ajustar antes) → requisição nova reserva por lote. Estoque e App simulados por cenMudar + aviso de
mudança (como outro quadro do Canvas): entregas → confirmação no app → turno sem sinal → sinal → turno 2 com sobra. A tela reflete
entregue/consumido/realizado sem recarregar; encerrar fica bloqueado pela sobra até a devolução no Estoque. Depois: bloqueio por sinal
(OS-0417), liberar bloqueado por falta de lote (OS-0418) e por saldo (OS-0430), Restaurar demonstração e Ajustar antes de liberar
(dose e área → v2 com histórico, liberada no mesmo comando).
Uso: python3 os_cenario_test.py   (compile antes: areas.processo_os.build())"""
import sys, os, time, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os
from conferencia_diaria_nav_helpers import conferir_dias
from comp_lib import troca_visao   # VISOES-1: troca de visão pelo seletor (data-visao), não pelo texto

T = Os(); OS = 'OS-0430'
def setin(lab, val):  # campo do painel pelo rótulo acessível (input + change, como a digitação)
    T.J(f"""(()=>{{const i=[...document.querySelectorAll('aside[role=dialog] input')].find(x=>x.getAttribute('aria-label')==={json.dumps(lab)});
      Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.25)
try:
    T.abrir()
    # 1 · A liberar sem etapa de revisão: próximo passo Liberar para execução (Ana pode ajustar antes); ajuste inválido não libera
    T.ordem(OS); p = T.pan(); st = T.cen(f"[c.ordens['{OS}'].etapa, 'aprov' in c.ordens['{OS}'], c.v]")
    T.btn('Ajustar antes de liberar'); setin('Área da ordem (ha)', '0'); T.btn('Salvar e liberar'); pa = T.pan(); T.btn('Voltar'); print('  ', st)
    T.ok(st == ['A liberar', False, 7] and T.temb('Liberar para execução') and T.temb('Ajustar antes de liberar') and not T.temb('Revisar versão') and not T.temb('Aprovar versão')
         and 'Aguardando agrônomo' not in p and 'Aprovada pelo agrônomo' not in p and 'APV-' not in p and 'Informe a área maior que 0 ha.' in pa and T.cen(f"c.ordens['{OS}'].etapa") == 'A liberar',
         'A liberar sem revisão: Liberar para execução + Ajustar antes de liberar; área 0 recusada junto ao campo, nada liberado; cenário v7 sem aprov (probe Codex; teste original preservado)', (st, p[p.find('PRÓXIMO'):][:300], pa[-300:]))
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
