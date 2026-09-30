# -*- coding: utf-8 -*-
"""Verificador · Estoque 6: lote vencido recebido em quarentena e liberado; larguras com o cenário carregado; sinal do app após recarregar."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

K = "(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l)||/custódia/.test(l))||'')"
v = V()
try:
    v.abrir()
    # recebimento da NF 4533 com lote vencido: tudo em quarentena
    v.etapa(1); v.clk(v.prim())
    for k, val in [('conf', '20000'), ('apto', '0'), ('quar', '20000'), ('val', '08/2026'), ('obs', 'Lote vencido')]:
        v.setv('fx_g_rec_' + k, val)
    v.clk('Salvar', 'aside[role=dialog]'); print('erro:', v.err(), '| toast:', v.toast())
    v.etapa(4); print('S58-0926:', v.rowtxt('S58-0926'))
    print('libq:', v.rowbtn('S58-0926', 'Liberar após inspeção'), v.rowtxt('S58-0926'))
    print('conf:', v.rowbtn('S58-0926', 'Confirmar liberação'), v.toast())
    print('S58-0926 depois:', v.rowtxt('S58-0926')); print('cen:', v.cen("JSON.stringify(c.lotes['Semente de soja 58 W|S58-0926'])"))
    print('item:', v.rowtxt('Semente de soja 58 W'))
    v.shot('ver_est_vencido.png')
    # cenário carregado para larguras: liberar OS-0430, entrega parcial com app sem sinal, devolução bloqueada, contagem pendente
    print(v.mudar("c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const rid=c.ordens['OS-0430'].req; cenEntregar(c,rid,'Glifosato 480',100,'Marcos'); cenSinal(c,false); cenConfirmarRecebimento(c,rid); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);"))
    v.abrir()
    for i in range(1, 7):
        v.etapa(i); print(f'e{i} overflow:', v.overflow(), '| prim:', v.prim())
    v.etapa(2); v.shot('ver_est_e2_carregado.png')
    for x in v.rows(): print('   |', x[:250])
    # sinal volta; recarrega: consumo continua aguardando sinal?
    print('sinal:', v.mudar("return cenSinal(c,true);"))
    v.abrir(); v.etapa(6); print('k6:', v.J(K)); print('consumo:', v.rowtxt('Consumo apontado no app'))
    print('ap da O.S.:', v.cen("JSON.stringify(c.ordens['OS-0430'].ap.map(a=>[a.dia,a.ha,a.sinc]))"), '| fila:', v.cen("JSON.stringify(c.app.fila)"), '| movs sinc:', v.cen("JSON.stringify(c.movs.filter(m=>m.origem==='app').map(m=>[m.id,m.tipo,m.sinc]))"))
    v.shot('ver_est_e6_sinal.png')
    print('erros:', v.erros())
finally:
    v.fim()
