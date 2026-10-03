# -*- coding: utf-8 -*-
"""Verificador · tabelas mais largas que o contêiner (rolagem horizontal escondida) em cada etapa da Compra e do Estoque, a 1440 px,
na versão atual e na cópia de segurança anterior às mudanças (bk_cmpest), para separar o que é novo do que já existia."""
import time, json, os, shutil, sys
from verif_cmpest_lib import V
import verif_cmpest_lib as L
OV="""[...document.querySelectorAll('main *')].filter(e=>e.offsetParent&&['auto','scroll','hidden','clip'].includes(getComputedStyle(e).overflowX)&&e.scrollWidth>e.clientWidth+1&&e.querySelector('[role=row]')).map(e=>e.scrollWidth+'>'+e.clientWidth)"""
def run(page,steps,pre=None,tag=''):
    v=V(page); J=v.J
    try:
        v.open()
        if pre: pre(v)
        for s in steps:
            v.clk(s); time.sleep(.3); v.clk('Expandir tudo'); print(f'{tag} {page} {s}:', J(OV))
    finally: v.close()
def cmp_pre(v):
    v.clk('Abrir compra'); v.clk('3 Solicite cotações'); v.clk('Enviar convites (simulado)'); time.sleep(7)
    v.clk('Comparar propostas'); v.clk('Revisar aprovação'); v.clk('Enviar à Direção'); v.clk('Registrar aprovação da Direção')
which=sys.argv[1] if len(sys.argv)>1 else 'atual'
if which=='antigo':
    L.R='/private/tmp/claude-501/-Users-adrianussanders-Library-Application-Support-Claude-scratch-workspaces-3f2449ee-7729-4f0a-96cc-d0f539bf7a66-57b91317-014d-44f0-ad90-4438cd376723-scratch-2026-09-22-5d85a9/ed477ec7-a5fd-431d-bc5d-c0e06c6234e4/scratchpad/v38/verif_render_antigo'
run('CMP.dc.html',['2 Confira a demanda','3 Solicite cotações','4 Compare propostas','5 Aprove a compra','6 Acompanhe a entrega'],cmp_pre,which)
run('EST.dc.html',['1 Confira recebimentos','2 Entregue por O.S.','3 Receba devoluções','4 Confira saldos','5 Faça contagens'],None,which)
