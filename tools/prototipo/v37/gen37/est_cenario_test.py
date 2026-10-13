# -*- coding: utf-8 -*-
"""Estoque × cenário compartilhado (EST.dc.html no Chrome headless), 15 verificações.
Pré-carga: OS-0430 liberada por cenMudar (reserva a requisição nova). Depois, pela tela: entregar os 3 itens,
recusar entrega acima do saldo, receber devolução apta e bloqueada, liberar a quarentena, contar lote com divergência e aprovar
o ajuste; o app confirma e aponta sem sinal. A O.S. e o estoque são conferidos lendo cenGet() na própria página."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

E = Est()
try:
    E.abrir()
    msg = E.mudar("return cenLiberar(c,'OS-0430');"); print('pré-carga:', msg)
    RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')"); print('requisição nova:', RQ)
    E.abrir()
    # 1 · a requisição nova aparece com fase, lote sugerido, embalagem e saldo a entregar
    E.etapa(2); print('k2:', E.k())
    g, d, o = E.rowtxt(RQ, 'Glifosato 480'), E.rowtxt(RQ, '2,4-D 806'), E.rowtxt(RQ, 'Óleo mineral')
    print(' ', g); print(' ', d); print(' ', o)
    E.ok(all('Liberadas' in t and 'galão 20 L' in t and 'A entregar' in t for t in (g, d, o)) and 'lote G26-14' in g and '320 L' in g and '16 galões' in g
         and '160 L' in d and '80 L' in o, f'{RQ}: 3 itens da OS-0430 (Liberadas), lote sugerido, galão 20 L e saldo a entregar 320/160/80 L')
    # 2 · entregar o 1º item com os padrões (saldo a entregar e responsável da O.S.)
    E.row(RQ, 'Glifosato 480'); q, quem = E.val('fx_g_ent_qtd'), E.val('fx_g_ent_quem'); print('padrões:', q, quem, '|', E.aside()[:220])
    E.salvar(); print('toast:', E.toast())
    g = E.rowtxt(RQ, 'Glifosato 480'); st = E.cen(f"(()=>{{const i=c.reqs['{RQ}'].itens[0]; const l=c.lotes['Glifosato 480|G26-14']; return [i.entregue,i.custodia,i.confirmado,l.fisico,l.reservado];}})()")
    print(' ', g, st)
    E.ok(q == '320' and quem == 'Marcos' and 'Entrega completa' in g and 'Aguardando confirmação no app' in g and st == [320, 320, False, 880, 0],
         'entrega com padrões (320 L a Marcos): linha aguarda o app; cenário: custódia 320 L, lote 1.200 → 880 L, reserva baixada')
    # 3 · entrega acima do saldo é recusada no campo e nada muda no cenário
    E.row(RQ, '2,4-D 806'); E.setv('fx_g_ent_qtd', '161'); E.salvar(); e = E.err(); print('erro:', e)
    ok3 = 'Acima do saldo a entregar: 160 L' in e and E.val('fx_g_ent_qtd') == '161' and E.cen(f"c.reqs['{RQ}'].itens[1].custodia") == 0
    E.ok(ok3, 'entrega de 161 L com saldo de 160 L: erro no campo, valor mantido e custódia continua 0', e)
    E.setv('fx_g_ent_qtd', '160'); E.salvar()
    E.row(RQ, 'Óleo mineral'); E.salvar()
    # 4 · a O.S. reflete: tudo entregue e em custódia, encerramento bloqueado pela sobra; 3 itens aguardando o app
    st = E.cen(f"[c.reqs['{RQ}'].itens.map(i=>i.entregue+'/'+i.custodia).join(' '), X.cenPodeEncerrar(c,'OS-0430'), c.ordens['OS-0430'].etapa]"); print('O.S.:', st, '| k2:', E.k())
    E.ok(st[0] == '320/320 160/160 80/80' and 'Sobra em custódia' in st[1] and '3 aguardando confirmação no app' in E.k(),
         'OS-0430 no cenário: 3 itens entregues e em custódia; encerramento bloqueado pela custódia; faixa conta 3 aguardando o app')
    # 5 · o app confirma o recebimento (outra tela): o aviso de mudança do cenário atualiza esta tela sem recarregar
    print('app:', E.mudar(f"return cenConfirmarRecebimento(c,'{RQ}');")); g0 = E.rowtxt(RQ, 'Glifosato 480')
    E.J("window.dispatchEvent(new StorageEvent('storage',{key:'talhao-os-cenario-v1'}))"); time.sleep(.4)
    g = E.rowtxt(RQ, 'Glifosato 480'); print(' ', g)
    E.ok('Aguardando confirmação no app' in g0 and 'Aguardando confirmação no app' not in g and 'Entrega completa' in g,
         'confirmação no app (aviso de outra tela) retira "Aguardando confirmação no app" sem recarregar')
    # 6 · devolução apta volta ao disponível
    E.etapa(3); print('k3:', E.k()); E.row(RQ, 'Glifosato 480'); print('padrão devolução:', E.val('fx_g_dev_qtd'))
    E.setv('fx_g_dev_qtd', '20'); E.salvar(); print('toast:', E.toast())
    st = E.cen(f"(()=>{{const i=c.reqs['{RQ}'].itens[0]; const l=c.lotes['Glifosato 480|G26-14']; return [i.custodia,i.devolvido,l.fisico,l.quarentena];}})()"); print(' ', st, E.rowtxt(RQ, 'Glifosato 480'))
    E.ok(st == [300, 20, 900, 0], 'devolução apta de 20 L: custódia 320 → 300 L, lote G26-14 880 → 900 L sem bloqueio')
    # 7 · devolução bloqueada vai para quarentena (observação obrigatória)
    E.row(RQ, 'Óleo mineral'); E.setv('fx_g_dev_qtd', '10'); E.setv('fx_g_dev_cond', 'Bloqueada para inspeção · vai para quarentena'); E.salvar(); e1 = E.err()
    E.setv('fx_g_dev_obs', 'Galão amassado, lacre rompido'); E.salvar(); print('toast:', E.toast())
    st = E.cen("(()=>{const l=c.lotes['Óleo mineral|O26-05']; return [l.fisico,l.quarentena,X.cenGet&&(l.fisico-l.quarentena-l.reservado)];})()"); print(' ', e1, st)
    E.ok('Descreva a condição' in e1 and st == [330, 10, 320], 'devolução bloqueada de 10 L exige observação e entra em quarentena: O26-05 físico 330 L, bloqueado 10 L, disponível 320 L')
    # 8 · saldos por lote: filtro por local e liberação da quarentena após inspeção
    E.etapa(4); E.clk('Câmara fria'); lot = E.J("[...document.querySelectorAll('[role=row].g2kid')].map(r=>r.innerText.split('\\n')[0].trim())"); E.clk('Todos os locais')
    t = E.rowtxt('O26-05'); print('O26-05:', t, '| Câmara fria:', lot)
    E.rowbtn('O26-05', 'Liberar após inspeção'); E.setv('est-laudo', 'INSP-0042'); E.clk('Liberar com o laudo'); print('toast:', E.toast())   # CTL-3 (R-D2): com o laudo
    st = E.cen("c.lotes['Óleo mineral|O26-05'].quarentena"); t2 = E.rowtxt('O26-05')
    E.ok(lot == ['S58-0801'] and '10 L' in t and st == 0 and 'Liberar após inspeção' not in t2 and '330 L' in t2,
         'filtro Câmara fria mostra só S58-0801; O26-05 liberado após inspeção (bloqueado 10 → 0, disponível 330 L)')
    E.shot('est_cen_saldos.png')
    # 9 · contagem cega com divergência vira ajuste pendente; o saldo não muda
    E.etapa(5); print('primário:', E.prim()); E.clk('Contar INV-2611'); a = E.aside()
    E.setv('fx_g_cnt_contador', 'Paula (almoxarife)'); E.setv('fx_g_cnt_cont', '870'); E.salvar(); print('toast:', E.toast())  # revisão CONF F6: o contador não tem mais valor padrão (era o 1º da lista fixa); a pessoa escolhe quem contou
    st = E.cen("(()=>{const a=(c.ajustes||[]).slice(-1)[0]||{}; return [a.estado,a.dif,a.inv,c.lotes['Glifosato 480|G26-14'].fisico];})()"); print(' ', st, E.rowtxt('INV-2611'))
    E.ok('900' not in a and st == ['Aguardando gestor', -30, 'INV-2611', 900] and 'Ajuste aguardando aprovação' in E.rowtxt('INV-2611'),
         'contagem cega (saldo oculto) de 870 L no G26-14: ajuste −30 L aguardando o gestor; físico continua 900 L')
    # 10 · aprovar o ajuste (com causa) aplica ao lote uma vez
    E.row('INV-2611'); E.setv('fx_g_cnt_causa', 'Bombona com vazamento separada para descarte'); E.salvar()
    E.rowbtn('INV-2611', 'Aprovar ajuste'); print('toast:', E.toast())
    st = E.cen("(()=>{const a=(c.ajustes||[]).slice(-1)[0]||{}; return [a.estado,c.lotes['Glifosato 480|G26-14'].fisico,c.movs.filter(m=>m.tipo==='ajuste').length];})()"); print(' ', st, E.rowtxt('INV-2611'))
    E.ok(st == ['Aprovado', 870, 1] and 'Ajuste aprovado' in E.rowtxt('INV-2611') and 'Aprovar ajuste' not in E.rowtxt('INV-2611'),
         'ajuste aprovado pelo gestor: G26-14 900 → 870 L, um movimento de ajuste, sem botão para aprovar de novo')
    # 11 · movimentos: trilha da reserva ao ajuste, com origem web/app
    E.etapa(6); m = E.main(); print('k6:', E.k())
    tipos = E.J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n').slice(2,3).join(''))")
    print('  tipos:', tipos)
    E.ok(tipos.count('Reserva') == 3 and tipos.count('Entrega') == 3 and tipos.count('Devolução') == 2 and 'Recebimento confirmado no app' in tipos
         and 'Quarentena liberada' in tipos and 'Ajuste de inventário' in tipos and 'App' in m and 'Web' in m,
         'movimentos: 3 reservas, 3 entregas, confirmação no app, 2 devoluções, liberação e ajuste, com origem Web/App')
    # 12 · apontamento do app sem sinal: movimento "Aguardando sinal"; o Estoque só vê consumo e baixa de custódia quando o app envia
    print('app sem sinal:', E.mudar("cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,10,1.5);"))
    E.abrir(); E.etapa(6); t = E.rowtxt('Consumo apontado no app'); print(' ', t, '| k6:', E.k())
    E.etapa(3); g = E.rowtxt(RQ, 'Glifosato 480'); print(' ', g)
    E.ok('Aguardando sinal' in t and 'App' in t and '320 L 0 L 20 L 300 L' in g and 'Aguardando sinal do app' in g,
         'consumo do app sem sinal: movimento "Aguardando sinal"; Glifosato segue consumido 0 L e custódia 300 L até o envio', g)
    # 13 · a O.S. reflete a devolução e o consumo (pode encerrar só sem custódia)
    st = E.cen(f"[c.reqs['{RQ}'].itens.map(i=>i.consumido+'/'+i.devolvido+'/'+i.custodia).join(' '), X.cenPodeEncerrar(c,'OS-0430')]"); print('O.S.:', st)
    E.ok(st[0] == '20/20/280 10/0/150 5/10/65' and st[1] != '', 'OS-0430 no cenário: consumido/devolvido/custódia por item e encerramento ainda bloqueado', st)
    # 14 · filtro Fazenda: Boa Vista sem estoque, volta para Santa Rita
    E.setv('select[aria-label="Filtrar por fazenda"]', 'Boa Vista'); time.sleep(.3); b = E.main(); p = E.prim()
    E.clk('Ver Santa Rita'); b2 = E.main()
    E.ok('Nenhum estoque na Boa Vista · Ver Santa Rita' in b and 'Custódia e devoluções' not in b and p == '' and 'Custódia e devoluções' in b2,
         'Fazenda Boa Vista: "Nenhum estoque na Boa Vista · Ver Santa Rita" (sem botão duplicado); o link volta à Santa Rita', [b[:120], p])
    # 15 · restaurar demonstração volta o cenário ao início; sem erro de script
    E.clk('Restaurar demonstração'); E.clk('Restaurar'); print('toast:', E.toast())
    st = E.cen("[Object.keys(c.reqs).length, c.movs.length, c.ordens['OS-0430'].etapa, c.lotes['Glifosato 480|G26-14'].fisico]"); er = E.erros(); print(' ', st, er)
    E.ok(st == [12, 0, 'A liberar', 1200] and not er, 'Restaurar demonstração: 12 requisições (6 da Santa Rita + 5 da Lagoa Grande + REQ-030 da OB-0110, BEN-1), nenhum movimento, OS-0430 A liberar, G26-14 1.200 L; sem erro de script', er)
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
