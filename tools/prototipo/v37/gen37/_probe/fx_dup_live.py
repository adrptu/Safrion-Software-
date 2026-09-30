# -*- coding: utf-8 -*-
"""Sonda: aviso de CNPJ já cadastrado ao digitar, depois de um salvar com erros (CD-05)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, marcar, alerta_campo
b = B(); b.size(1440, 1000); b.goto('CD-05.dc.html')
b.clk('Cadastrar parceiro'); marcar(b, 'Parceiro de crédito')
b.setv('#fx_g_forn_cnpj', '45.987.321/0001-60'); b.setv('#fx_g_forn_nome', 'Banco Cerrado'); b.clk('Salvar', 'aside[role=dialog]')
b.setv('#fx_g_forn_cnpj', '11.000.222/0001-20'); time.sleep(.3)
a = b.aside(); i = a.find('CPF ou CNPJ'); print('ASIDE:', a[:200], '|||', a[i:i+250])
print('ALERTAS:', b.alerts('aside[role=dialog]')); print('CAMPO:', alerta_campo(b, '#fx_g_forn_cnpj'))
