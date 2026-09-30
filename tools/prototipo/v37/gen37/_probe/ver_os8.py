# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 8: OS-0430 em conferência com sobra na lista e no Kanban (x OS-0417); Kanban Encerradas após encerrar."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J; OS = 'OS-0430'
def card(id_): return J(f"(()=>{{const k=[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] [role=button]')].find(k=>k.innerText.trim().startsWith('{id_}')); return k?k.innerText.replace(/\\s+/g,' '):'';}})()")
def tab(t): J(f"(()=>{{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='{t}'); b&&b.click();}})()"); time.sleep(.4)
try:
    T.abrir(wait=1.3)
    T.ordem(OS); T.btn('Revisar versão'); T.btn('Aprovar versão'); T.btn('Liberar para execução'); T.btn('Confirmar liberação'); T.fechar()
    RQ = T.cen(f"c.ordens['{OS}'].req")
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)): T.mudar(f"return cenEntregar(c,'{RQ}','{prod}',{q},'Marcos');", avisar=False)
    T.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,160,12,{{'Glifosato 480':300}});")
    T.ordem(OS); T.btn('Enviar para conferência'); T.btn('Confirmar envio'); p = T.pan(); T.fechar()
    print('painel bloqueio:', p[p.find('PRÓXIMO'):][:200])
    print('LISTA 0430:', T.linha(OS)); print('LISTA 0417:', T.linha('OS-0417'))
    T.shot('ver_os8_lista_conf.png')
    tab('Kanban'); print('KB 0430:', card(OS)); print('KB 0417:', card('OS-0417')); T.shot('ver_os8_kanban_conf.png'); tab('Lista')
    T.mudar(f"return cenDevolver(c,'{RQ}','Glifosato 480',20,true);")
    T.ordem(OS); T.btn('Conferir e encerrar'); T.btn('Confirmar encerramento'); print('encerrar', T.toast()); T.fechar()
    tab('Kanban'); print('KB Encerradas:', J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,3).join(' | ')).pop()"))
    print('KB 0430 encerrada:', card(OS)); T.shot('ver_os8_kanban_enc.png')
    print('erros', T.erros())
finally:
    T.fim()
