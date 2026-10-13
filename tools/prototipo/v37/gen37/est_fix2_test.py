# -*- coding: utf-8 -*-
"""Correções do verificador · Estoque, parte 2 (EST.dc.html no Chrome headless, 1440×1000, cenário limpo), na forma do SUP:
nota conferida sem rolagem, trilha de movimentos com documento da contagem e do ajuste, confirmação do app só com o que foi entregue,
consumo do app com unidade e quantidade, "Aguardando sinal" que some quando o sinal volta, entregas gravadas por quem entregou.
Fica o propósito da versão anterior (docs/suprimentos-simplificado §9.3); a faixa da etapa 6 virou a visão Movimentos de Confira saldos."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

MOV = "(t=>[...document.querySelectorAll('main [role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')&&r.innerText.indexOf(t)>=0).map(r=>r.innerText.replace(/\\s+/g,' ')))"


def cabe(E): return bool(E.J("document.documentElement.scrollWidth<=innerWidth+1"))
def movs(E, t): return E.J(f"({MOV})({t!r})".replace("'", '"'))


E = Est()
try:
    E.abrir(); E.perfil('Rui')
    # 1 · NF 4533 conferida com validade: a página continua sem rolagem lateral; os dois lotes da Semente de soja 58 W em Saldos
    E.ir('#sec=recebimentos'); E.row('NF 4533'); E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_val', '05/2027'); E.clk_prim()
    E.ok(cabe(E) and E.cel('NF 4533', 'Situação') == 'Conferida', 'NF 4533 conferida: "Conferida" e página sem rolagem', E.cel('NF 4533', 'Situação'))
    E.ir('#sec=saldos'); lot = [r for r in ('S58-0801', 'S58-0926') if E.rowtxt(r) != 'sem linha']
    E.ok(cabe(E) and lot == ['S58-0801', 'S58-0926'], 'Saldos: Semente de soja 58 W com os lotes S58-0801 e S58-0926, uma linha por lote, sem rolagem', lot)
    # 2 · contagem sem diferença e ajuste aprovado: documento e contador na trilha
    E.perfil('Paula'); E.ir('#sec=contagens'); E.row('INV-2611'); E.setv('fx_g_cnt_cont', '1200'); E.clk_prim()
    E.perfil('Ana'); E.ir('#sec=contagens'); E.row('INV-2609'); E.clk_prim()
    E.ir('#sec=movimentos'); c0, a0 = movs(E, 'Contagem sem diferença'), movs(E, 'Ajuste de inventário'); print(' ', c0, a0)
    E.ok(len(c0) == 1 and 'INV-2611' in c0[0] and 'Paula (almoxarife)' in c0[0], 'contagem sem diferença na trilha com INV-2611 e o contador', c0)
    E.ok(len(a0) == 1 and 'INV-2609' in a0[0] and '−600 kg' in a0[0] and 'Ana (gestora)' in a0[0], 'ajuste de inventário na trilha com INV-2609, −600 kg e quem aprovou', a0)
    # 3 · OS-0430 liberada; só Glifosato entregue pela tela; o app confirma: a trilha mostra só o Glifosato
    E.mudar("return cenLiberar(c,'OS-0430');"); RQ = E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')")
    E.perfil('Rui'); E.ir(f'#req={RQ}'); E.clk('Entregar parte de Glifosato 480 ›', 'aside[role=dialog]'); E.setv('fx_g_req_qtd', '320'); E.clk_prim()   # SUP §4.1: quantidade digitada
    print('app:', E.mudar(f"return cenConfirmarRecebimento(c,'{RQ}');"))
    E.ir('#sec=movimentos'); r = movs(E, 'Recebimento confirmado no app'); print(' ', r)
    E.ok(len(r) == 1 and 'Glifosato 480' in r[0] and '320 L' in r[0] and '2,4-D' not in r[0] and 'Óleo mineral' not in r[0], 'confirmação do app lista só o Glifosato 480 (320 L) entregue', r)
    # 4 · entrega dos outros 2 itens e turno de 5 ha fechado sem sinal: consumo com unidade e "Aguardando sinal"
    E.mudar(f"cenEntregar(c,'{RQ}','2,4-D 806',160,'Marcos','Rui'); return cenEntregar(c,'{RQ}','Óleo mineral',80,'Marcos','Rui');")
    print('app:', E.mudar(f"cenConfirmarRecebimento(c,'{RQ}'); cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);"))
    E.ir('#sec=movimentos'); r = movs(E, 'Consumo apontado no app'); print(' ', r)
    E.ok(len(r) == 1 and all(x in r[0] for x in ('Glifosato 480', '10 L', '2,4-D 806', '5 L', 'Óleo mineral', '2,5 L')) and 'Glifosato 480 10,' not in r[0],
         'consumo do app: cada item com quantidade e unidade (10 L, 5 L, 2,5 L)', r)
    E.ok('Aguardando sinal' in r[0] and cabe(E), 'sem sinal: "Aguardando sinal" na linha, página sem rolagem', r)
    E.shot('est_fix_e6.png')
    # 5 · o sinal volta: o apontamento é enviado e o consumo deixa de aguardar
    print('sinal:', E.mudar("return cenSinal(c,true);")); E.ir('#sec=movimentos'); r = movs(E, 'Consumo apontado no app')
    E.ok(r and 'Aguardando sinal' not in r[0], 'sinal de volta: consumo sem "Aguardando sinal"', r)
    # 6 · novo turno sem sinal: só o consumo novo aguarda; o já enviado continua enviado
    print('app:', E.mudar("cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,2,0.5);"))
    E.ir('#sec=movimentos'); r = movs(E, 'Consumo apontado no app')
    E.ok(len(r) == 2 and 'Aguardando sinal' in r[0] and 'Aguardando sinal' not in r[1] and '4 L' in r[0], 'segundo turno sem sinal: só o consumo novo (4 L de Glifosato) aguarda; o anterior segue enviado', r)
    q = movs(E, 'Entrega'); E.ok(q and all('Rui (almoxarife)' in x for x in q), 'entregas na trilha por "Rui (almoxarife)", quem entregou', q[:1])
    er = E.erros(); E.ok(not er, 'sem erro de script', er)
finally:
    ok = E.fim()
sys.exit(0 if ok else 1)
