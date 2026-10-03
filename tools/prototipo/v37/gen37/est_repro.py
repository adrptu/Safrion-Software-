# -*- coding: utf-8 -*-
"""Reprodução dos defeitos apontados pelo verificador da frente Estoque (EST.dc.html no Chrome headless, 1440×1000).
Uso: python3 est_repro.py a|b|c|d  (cada parte < 40 s; só imprime o que vê, não corrige nada)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from est_lib import Est

OVF = "[...document.querySelectorAll('[role=table]')].filter(x=>x.offsetParent).map(x=>[x.parentElement.scrollWidth,x.parentElement.clientWidth])"


def liberar_0430(E):
    E.mudar("return cenLiberar(c,'OS-0430');")
    return E.cen("Object.keys(c.reqs).find(k=>c.reqs[k].os==='OS-0430')")


def a(E):
    # D1 lote vencido liberável · D4 recebimentos rolando depois de conferir
    print('prim:', E.prim()); print(E.clk('Conferir NF 4533'))
    E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_apto', '0'); E.setv('fx_g_rec_quar', '20000'); E.setv('fx_g_rec_val', '08/2026'); E.setv('fx_g_rec_obs', 'Lote vencido'); E.salvar()
    print('toast:', E.toast()); print('NF 4533:', E.rowtxt('NF 4533')); print('ovf etapa1 (vencido):', E.J(OVF))
    E.etapa(4); print('S58-0926:', E.rowtxt('S58-0926')); print('ovf etapa4:', E.J(OVF))
    print(E.rowbtn('S58-0926', 'Liberar após inspeção')); print(E.rowbtn('S58-0926', 'Confirmar liberação')); print('toast:', E.toast())
    print('S58-0926 depois:', E.rowtxt('S58-0926'))


def b(E):
    # D4 recebimentos com validade 05/2027 · D2 contagens · D8 restaurar/filtro · D9 faixa etapa 2 · D11 contador
    E.clk('Conferir NF 4533'); E.setv('fx_g_rec_conf', '20000'); E.setv('fx_g_rec_apto', '20000'); E.setv('fx_g_rec_quar', '0'); E.setv('fx_g_rec_val', '05/2027'); E.salvar()
    print('toast:', E.toast()); print('ovf etapa1:', E.J(OVF)); E.shot('est_rep_e1.png')
    E.etapa(4); print('ovf etapa4 (2 lotes):', E.J(OVF))
    E.etapa(5); print('ovf etapa5:', E.J(OVF)); print('INV-2609:', E.rowtxt('INV-2609'))
    E.clk('+ Nova contagem'); E.setv('fx_g_cnt_lote', E.J("[...document.querySelector('#fx_g_cnt_lote').options].map(o=>o.value).find(v=>v.startsWith('D26-01'))")); E.setv('fx_g_cnt_cont', '290'); E.salvar()
    print('toast:', E.toast()); print('ovf etapa5 após nova:', E.J(OVF)); E.shot('est_rep_e5.png')
    E.etapa(2); print('k2:', E.k()); print('REQ-036:', E.rowtxt('REQ-036'))
    E.etapa(4); E.clk('Câmara fria'); E.clk('Restaurar demonstração'); E.clk('Restaurar'); print('toast:', E.toast())
    print('chip ativo:', E.J("[...document.querySelectorAll('button[aria-pressed=true]')].map(b=>b.innerText)"), '| linhas:', E.J("[...document.querySelectorAll('[role=row].g2kid')].map(r=>r.innerText.split('\\n')[0])"))


def c(E):
    # D3 chip Aguardando sinal cortado · D5 continua aguardando depois do sinal · D7 consumo sem unidade
    RQ = liberar_0430(E); print('RQ', RQ)
    print(E.mudar(f"cenEntregar(c,'{RQ}','Glifosato 480',320,'Marcos'); cenEntregar(c,'{RQ}','2,4-D 806',160,'Marcos'); return cenEntregar(c,'{RQ}','Óleo mineral',80,'Marcos');"))
    print(E.mudar("cenSinal(c,false); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);"))
    E.abrir(); E.etapa(6); print('k6:', E.k()); print('consumo:', E.rowtxt('Consumo apontado no app')); print('ovf etapa6:', E.J(OVF)); E.shot('est_rep_e6.png')
    print('sinal:', E.mudar("return cenSinal(c,true);"))
    E.abrir(); E.etapa(6); print('k6 depois do sinal:', E.k()); print('consumo:', E.rowtxt('Consumo apontado no app'))
    print('quem entrega:', E.rowtxt('Entrega', 'Glifosato 480'))


def d(E):
    # D6 confirmação lista itens não entregues · D10 ajuste sem documento
    RQ = liberar_0430(E); E.abrir()
    E.etapa(2); E.row(RQ, 'Glifosato 480'); E.salvar(); print('toast:', E.toast())
    print('app:', E.mudar(f"return cenConfirmarRecebimento(c,'{RQ}');"))
    E.etapa(5); print(E.rowbtn('INV-2609', 'Aprovar ajuste')); print('toast:', E.toast())
    E.abrir(); E.etapa(6); print('confirmado:', E.rowtxt('Recebimento confirmado no app')); print('ajuste:', E.rowtxt('Ajuste de inventário'))


P = {'a': a, 'b': b, 'c': c, 'd': d}
if __name__ == '__main__':
    for k in [x for x in sys.argv[1:] if x in P] or list(P):
        print(f'===== {k} ====='); E = Est()
        try:
            E.abrir(); P[k](E); print('erros:', E.erros())
        finally:
            E.fim()
