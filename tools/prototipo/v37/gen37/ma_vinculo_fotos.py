# -*- coding: utf-8 -*-
"""MA-VINCULO · fotos para conferência visual (1440 e 390 px), com as colunas como a pessoa vê (padrão do "Abre com", não "todas").
Grava em _probe/ma_vinculo/fotos/. Uso: python3 ma_vinculo_fotos.py"""
import os, sys, time
os.environ['G2CV_PADRAO'] = '1'
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cadc_lib, ma_lib
ma_lib.T = lambda: cadc_lib.T(colunas='padrao')
from ma_lib import MA
from ma_vinculo_test import PM11, abre_link, botao
OUT = os.path.join(HERE, '_probe', 'ma_vinculo', 'fotos'); os.makedirs(OUT, exist_ok=True)

def rodada(w, h, suf):
    m = MA(w, h); J = m.J
    if w < 500: m.c.call('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 5})
    shot = lambda n: (time.sleep(.4), m.c.shot(os.path.join(OUT, f'{n}_{suf}.png')))
    try:
        m.ir('', perfil='Otávio', limpa=True, pagina='MOD-MAN.dc.html'); shot('F1_entrada')
        m.ir('vis=ativos'); shot('F2_ativos')
        m.ir('vis=ativos&pend=semplano'); shot('F3_sem_plano')
        abre_link(m, 'a12'); botao(m, 'Contar de agora'); shot('F4_painel_um')
        J("document.querySelector('#vl-painel .ma-rod button:last-child').click()"); time.sleep(1); shot('F4b_depois')
        m.ir('plano=PM-07'); shot('F5_plano')
        J(PM11); m.ir('plano=PM-11'); m.clk('Vincular ativos', 'main'); botao(m, 'Informar a última execução'); shot('F6_lote')
        m.ir('plano=PM-01'); J("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='PM-01|a02'); const b=r&&r.querySelector('button.g2mais'); if(b) b.click();})()"); time.sleep(.4)
        shot('F7a_menu_linha'); m.clk('Desvincular'); shot('F7_desvincular')
        m.ir('ativo=a12'); shot('F8_ativo')
        m.ir('plano=PM-07'); m.clk('Editar plano'); m.setv('#np_tipo', 'modelo'); m.setv('#np_modelo', 'motobomba 125 cv'); shot('F9_aplica_a')
        if w > 500:
            m.ir('', pagina='CD-03.dc.html'); m.t.openrow(0, 'Trator 02'); shot('F10_cd03')
        print(suf, 'erros de JS:', m.errs() or 'nenhum')
    finally:
        try: m.c.close()
        finally: m.t.srv.terminate()

if __name__ == '__main__':
    os.chdir(HERE); rodada(1440, 1000, '1440'); rodada(390, 844, '390')
    print('fotos em', OUT)
