# -*- coding: utf-8 -*-
"""Passo 9c · CD-01: área total 0 ha e −5 ha na fazenda nova (limite do campo)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, alerta_campo
b = B(); b.size(1440, 1000); b.goto('CD-01.dc.html')
b.clk('+ Cadastrar fazenda'); b.setv('#fx_g_faz_nome', 'Fazenda Zero'); b.setv('#fx_g_faz_mun', 'Jataí')
b.setv('#fx_g_faz_area', '-5'); b.clk('Salvar', 'aside[role=dialog]'); print('   −5:', alerta_campo(b, '#fx_g_faz_area'))
b.setv('#fx_g_faz_area', '0'); b.clk('Salvar', 'aside[role=dialog]'); a = alerta_campo(b, '#fx_g_faz_area'); aberto = b.J("!!document.querySelector('aside[role=dialog]')"); t = b.toast()
print('   0:', a, '| aberto:', aberto, '| toast:', t, '| linha:', b.rowtxt('Fazenda Zero'))
b.ok(aberto and bool(a), 'CD-01 · área total 0 ha deve ser barrada no campo', (a, t, b.rowtxt('Fazenda Zero')))
b.shot('e2e_09c_cd01_area0.png')
b.fim()
