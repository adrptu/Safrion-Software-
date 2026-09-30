# -*- coding: utf-8 -*-
"""Passo 3c (2ª passada) · MB-03: iniciar turno, Sem sinal, fechar 60 ha (para conferir O.S. e Mapa com o registro no aparelho)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B
b = B(); b.size(390, 1500); OS = 'OS-0430'
b.goto('MB-03.dc.html')
b.clk_sel(f'button[title="Iniciar turno na {OS}"]'); b.clk('Sem sinal'); b.setv('#ft_ha', '60'); b.setv('#ft_h', '5'); b.clk('Fechar turno')
st = b.cen(f"[c.app.fila.length, c.ordens['{OS}'].realizado, c.ordens['{OS}'].etapa, c.app.online]"); print('   cenário:', st, '|', b.toast())
b.ok(st == [1, 0, 'Em execução', False] and '1 registro aguardando sinal' in b.body(), 'turno de 60 ha fechado sem sinal: 1 registro aguardando sinal', st)
b.fim()
