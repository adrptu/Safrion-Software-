# -*- coding: utf-8 -*-
"""Estoque × cenário compartilhado (EST.dc.html no Chrome headless), 15 verificações, na forma do SUP (4 seções; o painel resolve).
Pré-carga: OS-0430 liberada por cenMudar (reserva a requisição nova). Depois, pela tela: entregar parte e a requisição inteira, recusar
entrega acima do saldo, receber devolução apta e bloqueada, laudo da parcela, contar lote com divergência e aprovar o ajuste; o app confirma
e aponta sem sinal. A O.S. e o estoque são conferidos lendo cenGet() na própria página. Fica o propósito da versão anterior; mudou a forma."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

E = Est()
try:
    E.abrir()
    msg = E.mudar("return cenLiberar(c,'OS-0430');"); print('pré-carga:', msg)
    RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')"); print('requisição nova:', RQ)
    E.perfil('Rui')
    # 1 · a requisição nova aparece na fila com a situação; o painel mostra a conta e "Separe:" com lote, validade, local e embalagem
    E.ir(f'#req={RQ}'); a = E.aside(); p = E.prim_painel()
    E.ok(E.cel(RQ, 'Situação') == 'A entregar' and '16 galões de 20 L' in a and 'G26-14' in a and 'Almox. defensivos' in a and p.endswith('a Marcos') and '320 L Glifosato 480' in p,
         f'{RQ}: A entregar; "Separe:" com lote e 16 galões de 20 L; primária entrega a requisição inteira a Marcos', [p, a[:200]])
    # 2 · entregar parte: recebedor herdado da O.S.; a quantidade é digitada (SUP §4.1: em branco, até a reserva própria; antes vinha o saldo)
    E.clk('Entregar parte de Glifosato 480 ›', 'aside[role=dialog]'); q, quem = E.val('fx_g_req_qtd'), E.val('fx_g_req_quem'); E.setv('fx_g_req_qtd', '320'); E.clk_prim()
    st = E.cen(f"(()=>{{const i=c.reqs['{RQ}'].itens[0]; const l=c.lotes['Glifosato 480|G26-14']; return [i.entregue,i.custodia,i.confirmado,l.fisico,l.reservado];}})()")
    E.ok(q == '' and quem == 'Marcos' and st == [320, 320, False, 880, 0], 'entrega parcial de 320 L a Marcos (recebedor herdado, quantidade digitada): custódia 320 L, lote 1.200 → 880 L, reserva baixada', [q, quem, st])
    # 3 · entrega acima do saldo é recusada no campo e nada muda no cenário
    E.ir(f'#req={RQ}'); E.clk('Entregar parte de 2,4-D 806 ›', 'aside[role=dialog]'); E.setv('fx_g_req_qtd', '161'); E.clk_prim(); e = E.err()
    E.ok('Acima do saldo a entregar: 160 L' in e and E.val('fx_g_req_qtd') == '161' and E.cen(f"c.reqs['{RQ}'].itens[1].custodia") == 0, 'entrega de 161 L com saldo de 160 L: erro no campo, valor mantido e custódia 0', e)
    # entrega o restante pela requisição inteira (2,4-D e Óleo mineral): tudo ou nada
    E.ir(f'#req={RQ}'); p = E.prim_painel(); E.clk_prim()
    st = E.cen(f"[c.reqs['{RQ}'].itens.map(i=>i.entregue+'/'+i.custodia).join(' '), cenPodeEncerrar(c,'OS-0430'), c.ordens['OS-0430'].etapa]")
    E.ok(p.startswith(f'Entregar {RQ} · 160 L 2,4-D 806') and st[0] == '320/320 160/160 80/80' and 'Sobra em custódia' in st[1],
         'entregar a requisição inteira leva o que falta; OS-0430 com 3 itens em custódia e encerramento bloqueado pela custódia', [p, st])
    # 4 · a fila diz que aguarda o app
    E.ir_secao('Atenda requisições'); E.ok(E.cel(RQ, 'Situação') == 'Aguarda confirmação no app', 'situação "Aguarda confirmação no app"', E.cel(RQ, 'Situação'))
    # 5 · o app confirma (outra tela): o aviso de mudança do cenário atualiza esta tela sem recarregar
    print('app:', E.mudar(f"return cenConfirmarRecebimento(c,'{RQ}');"))
    E.J("window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
    E.ok(E.cel(RQ, 'Situação') == 'Em uso', 'confirmação no app (aviso de outra tela) troca a situação para "Em uso" sem recarregar', E.cel(RQ, 'Situação'))
    # 6 · devolução apta volta ao lote (OS-0430 ativa: volta também à reserva dela)
    E.ir(f'#req={RQ}'); E.clk('Registrar devolução de Glifosato 480 ›', 'aside[role=dialog]'); E.setv('fx_g_req_dqtd', '20'); E.clk_prim()
    st = E.cen(f"(()=>{{const i=c.reqs['{RQ}'].itens[0]; const l=c.lotes['Glifosato 480|G26-14']; return [i.custodia,i.devolvido,l.fisico,l.quarentena,l.reservado];}})()")
    E.ok(st == [300, 20, 900, 0, 20], 'devolução apta de 20 L: custódia 320 → 300 L, lote 880 → 900 L, 20 L voltam à reserva da O.S. ativa', st)
    # 7 · devolução bloqueada vai para quarentena como parcela da requisição (observação obrigatória)
    E.ir(f'#req={RQ}'); E.clk('Registrar devolução de Óleo mineral ›', 'aside[role=dialog]'); E.setv('fx_g_req_dqtd', '10'); E.setv('fx_g_req_cond', 'Bloqueada para inspeção · vai para quarentena'); E.clk_prim(); e1 = E.err()
    E.setv('fx_g_req_obs', 'Galão amassado, lacre rompido'); E.clk_prim()
    st = E.cen(f"(()=>{{const l=c.lotes['Óleo mineral|O26-05']; return [l.fisico,l.quarentena,cenDisp(l),(cenQuar(l)[0]||{{}}).doc];}})()")
    E.ok('Descreva a condição' in e1 and st == [330, 10, 320, RQ], f'devolução bloqueada de 10 L exige observação e entra em quarentena como parcela da {RQ}: O26-05 330 L, 10 L bloqueados, 320 L disponíveis', [e1, st])
    # 8 · saldos por lote: filtro por local e laudo da parcela
    E.ir('#sec=saldos'); E.clk('Câmara fria'); lot = E.J("[...document.querySelectorAll('main [role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>r.querySelector('[role=cell]+[role=cell]').innerText.trim())"); E.clk('Todos os locais')
    E.perfil('Ana'); E.ir(f'#nf={RQ}'); E.setv('fx_g_rec_laudo', 'INSP-0042'); E.setv('fx_g_rec_res', 'Aprovado'); E.clk_prim()
    st = E.cen("[c.lotes['Óleo mineral|O26-05'].quarentena, cenDisp(c.lotes['Óleo mineral|O26-05'])]")
    E.ok(lot == ['S58-0801'] and st == [0, 330], 'filtro Câmara fria mostra só S58-0801; laudo INSP-0042 libera a parcela (bloqueado 10 → 0, disponível 330 L)', [lot, st])
    E.shot('est_cen_saldos.png')
    # 9 · contagem cega com divergência vira ajuste pendente; o saldo não muda
    E.perfil('Paula'); E.ir('#sec=contagens'); E.row('INV-2611'); a = E.aside(); E.setv('fx_g_cnt_cont', '870'); E.clk_prim()
    E.setv('fx_g_cnt_causa', 'Bombona com vazamento separada para descarte'); E.clk_prim()
    st = E.cen("(()=>{const a=(c.ajustes||[]).slice(-1)[0]||{}; return [a.estado,a.dif,a.inv,c.lotes['Glifosato 480|G26-14'].fisico];})()")
    E.ok('900' not in a and st == ['Aguardando gestor', -30, 'INV-2611', 900], 'contagem cega de 870 L no G26-14: ajuste −30 L aguardando a gestora; físico continua 900 L', [a[:120], st])
    # 10 · aprovar o ajuste aplica ao lote uma vez
    E.perfil('Ana'); E.ir('#sec=contagens'); E.row('INV-2611'); E.clk_prim()
    st = E.cen("(()=>{const a=(c.ajustes||[]).slice(-1)[0]||{}; return [a.estado,c.lotes['Glifosato 480|G26-14'].fisico,c.movs.filter(m=>m.tipo==='ajuste').length];})()")
    E.row('INV-2611'); p2 = E.prim_painel()
    E.ok(st == ['Aprovado', 870, 1] and p2 == '', 'ajuste aprovado pela gestora: G26-14 900 → 870 L, um movimento de ajuste, sem primária para aprovar de novo', [st, p2])
    # 11 · movimentos: trilha da reserva ao ajuste, com quem agiu
    E.ir('#sec=movimentos'); tipos = E.J("[...document.querySelectorAll('main [role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>r.querySelectorAll('[role=cell]')[1].innerText.trim())")
    print('  tipos:', tipos)
    E.ok(tipos.count('Reserva') == 3 and tipos.count('Entrega') == 3 and tipos.count('Devolução') == 2 and 'Recebimento confirmado no app' in tipos and 'Quarentena liberada' in tipos and 'Ajuste de inventário' in tipos,
         'movimentos: 3 reservas, 3 entregas, confirmação no app, 2 devoluções, laudo e ajuste', tipos)
    # 12 · apontamento do app sem sinal: movimento "Aguardando sinal"; o Estoque só vê consumo e baixa de custódia quando o app envia
    print('app sem sinal:', E.mudar("cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,10,1.5);"))
    E.ir('#sec=movimentos'); t = E.rowtxt('Consumo apontado no app')
    E.ir(f'#req={RQ}'); cu = E.cel('Glifosato 480', 'Em custódia'); pn = E.aside()
    E.ok('Aguardando sinal' in t and cu == '300 L' and 'consumido 0 L' in pn, 'consumo do app sem sinal: movimento "Aguardando sinal"; o Estoque mostra Glifosato consumido 0 L e custódia 300 L até o envio', [t, cu, pn[:200]])
    # 13 · a O.S. reflete a devolução e o consumo (pode encerrar só sem custódia)
    E.mudar("return cenSinal(c,true);")
    st = E.cen(f"[c.reqs['{RQ}'].itens.map(i=>i.consumido+'/'+i.devolvido+'/'+i.custodia).join(' '), cenPodeEncerrar(c,'OS-0430')]"); print('O.S.:', st)
    E.ok(st[0] == '20/20/280 10/0/150 5/10/65' and st[1] != '', 'OS-0430 no cenário: consumido/devolvido/custódia por item e encerramento ainda bloqueado', st)
    # 14 · filtro Fazenda: Boa Vista sem estoque, volta para Santa Rita
    E.fazenda('Boa Vista'); b = E.main(); E.clk('Ver Santa Rita'); b2 = E.main()
    E.ok('Nenhum estoque na Boa Vista' in b and 'Requisições das O.S.' not in b and 'Nenhum estoque na Boa Vista' not in b2,
         'Fazenda Boa Vista: "Nenhum estoque na Boa Vista · Ver Santa Rita"; o link volta à Santa Rita', b[:120])
    # 15 · restaurar demonstração volta o cenário ao início; sem erro de script
    E.clk('Restaurar demonstração'); E.clk('Restaurar')
    st = E.cen("[Object.keys(c.reqs).length, c.movs.length, c.ordens['OS-0430'].etapa, c.lotes['Glifosato 480|G26-14'].fisico]"); er = E.erros()
    E.ok(st == [12, 0, 'A liberar', 1200] and not er, 'Restaurar demonstração: 12 requisições (6 da Santa Rita + 5 da Lagoa Grande + REQ-030 da OB-0110, BEN-1), nenhum movimento, OS-0430 A liberar, G26-14 1.200 L; sem erro de script', [st, er])
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
