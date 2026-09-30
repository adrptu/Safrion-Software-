# -*- coding: utf-8 -*-
"""O.S. × cenário compartilhado (OS.dc.html no Chrome headless), 14 verificações · jornada da OS-0430.
Pela tela: revisar/aprovar (recibo) → liberar (requisição nova reserva por lote). Estoque e App simulados por cenMudar + aviso de
mudança (como outro quadro do Canvas): entregas → confirmação no app → turno sem sinal → sinal → turno 2 com sobra. A tela reflete
entregue/consumido/realizado sem recarregar; encerrar fica bloqueado pela sobra até a devolução no Estoque. Depois: bloqueio por sinal
(OS-0417), liberar bloqueado por falta de lote (OS-0418) e por saldo (OS-0430) e Restaurar demonstração.
Uso: python3 os_cenario_test.py   (compile antes: areas.processo_os.build())"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from os_lib import Os

T = Os(); OS = 'OS-0430'
try:
    T.abrir()
    # 1 · revisar e aprovar: grava aprov=true com recibo no cenário; a ordem continua em A liberar
    T.ordem(OS); T.btn('Revisar versão'); T.btn('Aprovar versão'); tt = T.toast(); st = T.cen(f"[c.ordens['{OS}'].aprov, c.ordens['{OS}'].etapa, (c.ordens['{OS}'].osc||{{}}).recibo]")
    print('  ', tt, st)
    T.ok(st[0] is True and st[1] == 'A liberar' and st[2]['id'] == 'APV-0430-v1' and 'recibo APV-0430-v1' in tt and 'ainda não foi liberada' in tt
         and 'A liberar' in T.linha(OS) and 'Aprovada pelo agrônomo' in T.linha(OS) and 'v1 aprovada · recibo APV-0430-v1' in T.pan(), 'aprovar grava aprov=true com recibo APV-0430-v1; fase continua A liberar', (tt, st))
    # 2 · liberar: a requisição nova reserva por lote (Glifosato 320 L, 2,4-D 160 L, Óleo 80 L)
    T.btn('Liberar para execução'); ct = T.pan(); T.btn('Confirmar liberação'); tt = T.toast()
    RQ = T.cen(f"c.ordens['{OS}'].req"); st = T.cen(f"[c.ordens['{OS}'].etapa, c.reqs['{RQ}'].itens.map(i=>i.prod+' '+i.solicitado+' '+i.lote).join(' | '), c.lotes['Glifosato 480|G26-14'].reservado]")
    print('  ', RQ, st, '|', tt)
    T.ok('reserva no Estoque, por lote: Glifosato 480 320 L, 2,4-D 806 160 L, Óleo mineral 80 L' in ct and st[0] == 'Liberadas' and st[1].startswith('Glifosato 480 320 G26-14 | 2,4-D 806 160')
         and 'Óleo mineral 80' in st[1] and st[2] == 320 and f'{OS} liberada. {RQ} reservou' in tt and 'Reservado 320 L · lote G26-14' in T.ins() and 'Liberadas' in T.linha(OS),
         f'liberar: {RQ} reserva Glifosato 480 320 L (G26-14), 2,4-D 806 160 L e Óleo mineral 80 L; painel mostra a reserva por lote', (ct[-300:], st, tt))
    # 3 · Estoque entrega os 3 itens a Marcos (outra tela): o painel mostra entregue, embalagem e a quem, sem recarregar
    for prod, q in (('Glifosato 480', 320), ('2,4-D 806', 160), ('Óleo mineral', 80)): T.mudar(f"return cenEntregar(c,'{RQ}','{prod}',{q},'Marcos');", avisar=False)
    T.mudar("return {msg:''};"); i = T.ins(); print('  ', i[:400])
    T.ok('Entregue 320 L (16 × galão 20 L) a Marcos' in i and i.count('Aguardando confirmação no app') >= 3 and 'Entregue · aguardando confirmação no app' in i,
         'entregas do Estoque aparecem sem recarregar: 320 L (16 × galão 20 L) a Marcos, aguardando confirmação no app', i[:400])
    # 4 · App: confirma, inicia turno, fica sem sinal e fecha 60 ha → "Aguardando sinal"; realizado e consumo só mudam no envio (custódia 320 L)
    T.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenIniciarTurno(c,'{OS}'); cenSinal(c,false); return cenFecharTurno(c,60,5);")
    p = T.pan(); a = T.aps(); i = T.ins(); print('  ', a, '|', T.linha(OS))
    T.ok('Em execução' in T.linha(OS) and '0 / 160 ha' in T.linha(OS) and len(a) == 1 and 'Dia 1 · app' in a[0] and 'Aguardando sinal' in a[0] and 'não somado' in a[0]
         and 'Acumulado 0 / 160 ha · saldo 160 ha · 60 ha no aparelho aguardando sinal' in p and 'Confirmado no app' in i and 'Consumido 120 L' not in i and 'Em custódia 320 L' in i and 'consumo no aparelho, aguardando sinal' in i,
         'turno do app sem sinal: Em execução, "Dia 1 · app · Aguardando sinal" fora do acumulado; consumo ainda no aparelho (custódia 320 L)', (a, T.linha(OS), i[:300]))
    # 5 · sinal volta: o realizado passa a 60 ha (uma vez só)
    T.mudar("cenSinal(c,true); return cenSinal(c,true);"); a = T.aps(); i = T.ins(); print('  ', a, '|', T.linha(OS))
    T.ok('60 / 160 ha' in T.linha(OS) and 'saldo 100 ha' in T.linha(OS) and len(a) == 1 and 'Provisório' in a[0] and '60 / 160 ha' in a[0] and 'Consumido 120 L' in i and 'Em custódia 200 L' in i,
         'sinal de volta: realizado 60 / 160 ha e consumo 120 L (custódia 200 L) juntos, sem duplicar', (a, T.linha(OS), i[:300]))
    # 6 · turno 2 de 100 ha com 180 L de Glifosato (sobra 20 L): saldo zero → próximo passo Enviar para conferência
    T.mudar(f"cenIniciarTurno(c,'{OS}'); return cenFecharTurno(c,100,8,{{'Glifosato 480':180}});"); i = T.ins()
    T.ok('160 / 160 ha' in T.linha(OS) and T.temb('Enviar para conferência') and 'Consumido 300 L' in i and 'Em custódia 20 L' in i,
         'turno 2 (100 ha, 180 L de Glifosato): 160 / 160 ha, sobra 20 L em custódia, botão Enviar para conferência', (T.linha(OS), i[:300]))
    # 7 · em conferência, encerrar fica bloqueado pela sobra, com o atalho para receber a devolução no Estoque
    T.btn('Enviar para conferência'); T.btn('Confirmar envio'); p = T.pan(); print('  ', p[p.find('PRÓXIMO'):][:300])
    T.ok('Em conferência' in T.linha(OS) and 'Encerrar bloqueado: sobra em custódia · Glifosato 480 20 L (1 × galão 20 L) com Marcos.' in p
         and T.link('Receber devolução no Estoque') == 'EST.dc.html' and not T.temb('Conferir e encerrar'),
         'Em conferência: encerrar bloqueado pela sobra de 20 L com Marcos e link "Receber devolução no Estoque" → EST.dc.html', p[:500])
    # 8 · Estoque recebe a devolução (apta): o bloqueio sai sem recarregar e o botão de encerrar aparece
    T.mudar(f"return cenDevolver(c,'{RQ}','Glifosato 480',20,true);"); p = T.pan(); i = T.ins()
    T.ok('Encerrar bloqueado' not in p and T.temb('Conferir e encerrar') and 'Devolvido 20 L' in i and 'Consumido · sobra devolvida' in i and 'nada em custódia' in p,
         'devolução recebida no Estoque: bloqueio some, trilha mostra Devolvido 20 L e surge Conferir e encerrar', p[:500])
    # 9 · conferir e encerrar grava no cenário (regra atual: Em conferência → Encerradas)
    T.btn('Conferir e encerrar'); T.btn('Confirmar encerramento'); st = T.cen(f"[c.ordens['{OS}'].etapa, c.ordens['{OS}'].ap.map(a=>a.st).join(',')]"); print('  ', st, T.toast())
    T.ok(st == ['Encerradas', 'Conferido,Conferido'] and 'Encerradas' in T.linha(OS) and 'somente consulta' in T.pan() and f'{OS} encerrada' in T.toast(),
         'encerrar: cenário Encerradas, apontamentos conferidos, painel somente consulta', st)
    T.shot('os_cenario_encerrada.png'); T.fechar()
    # 10 · bloqueio por sinal: OS-0417 com apontamento no aparelho aguardando sinal
    T.mudar("c.ordens['OS-0417'].ap.push({d:'26/09',dia:4,ha:0,st:'Provisório',origem:'app',sinc:false}); return {msg:''};")
    T.ordem('OS-0417'); p = T.pan()
    T.ok('Encerrar bloqueado: há apontamentos no aparelho aguardando sinal.' in p and 'Quem resolve: Paula reconecta o app' in p and not T.temb('Conferir e encerrar'),
         'OS-0417: apontamento aguardando sinal bloqueia o encerramento e diz quem resolve', p[:400])
    T.fechar()
    # 11 · liberar bloqueado pelo Estoque: OS-0418 aprovada, sem lote de Ureia 45% → motivo no próximo passo, sem botão de liberar
    T.ordem('OS-0418'); T.btn('Revisar versão'); T.btn('Aprovar versão'); p = T.pan()
    T.ok('Liberar bloqueado: sem lote de Ureia 45% no Estoque.' in p and T.link('Ver saldos no Estoque') == 'EST.dc.html' and not T.temb('Liberar para execução')
         and T.cen("c.ordens['OS-0418'].etapa") == 'A liberar',
         'OS-0418 aprovada: liberar bloqueado com o motivo do Estoque (sem lote de Ureia 45%) e atalho aos saldos', p[p.find('PRÓXIMO'):][:300])
    T.fechar()
    # 12 · outra tela restaura a demonstração: a O.S. volta ao início sem recarregar; com o lote G26-14 baixo, liberar mostra o saldo
    T.J("window.__cen.cenReset(); window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4); l0 = T.linha(OS)
    T.mudar("c.lotes['Glifosato 480|G26-14'].fisico=100; return {msg:''};"); T.ordem(OS); T.btn('Revisar versão'); T.btn('Aprovar versão'); p = T.pan(); print('  ', l0, '|', p[p.find('PRÓXIMO'):][:260])
    T.ok('A liberar' in l0 and 'Aguardando agrônomo' in l0 and 'Liberar bloqueado: saldo insuficiente de Glifosato 480: 100 L disponíveis para 320 L.' in p and not T.temb('Liberar para execução'),
         'cenReset em outra tela volta a OS-0430 a A liberar; com 100 L no G26-14, liberar fica bloqueado pelo saldo', (l0, p[:300]))
    T.fechar()
    # 13 · Restaurar demonstração (rodapé, com confirmação): aprovação, lote e requisições voltam ao início
    T.btn('Restaurar demonstração', 'body'); T.btn('Restaurar', 'body'); tt = T.toast()
    st = T.cen(f"[Object.keys(c.reqs).length, c.ordens['{OS}'].etapa, c.ordens['{OS}'].aprov, c.lotes['Glifosato 480|G26-14'].fisico, c.ordens['OS-0418'].aprov]"); print('  ', st, tt)
    T.ok(st == [6, 'A liberar', False, 1200, False] and 'Demonstração restaurada' in tt and 'Aguardando agrônomo' in T.linha(OS),
         'Restaurar demonstração: 6 requisições, OS-0430 e OS-0418 sem aprovação, G26-14 com 1.200 L', (st, tt))
    # 14 · sem erro de script
    er = T.erros(); T.ok(not er, 'sem erro de script', er)
finally:
    ok = T.fim()
sys.exit(0 if ok else 1)
