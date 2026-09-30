# -*- coding: utf-8 -*-
"""Passo 9g · CD-05: parceiro de crédito com CNPJ já cadastrado (Banco Terra 11.000.222/0001-20)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, marcar
b = B(); b.size(1440, 1000); b.goto('CD-05.dc.html')
b.clk('Cadastrar parceiro'); marcar(b, 'Parceiro de crédito'); marcar(b, 'Custeio')
b.setv('#fx_g_forn_cnpj', '11.000.222/0001-20'); b.setv('#fx_g_forn_nome', 'Banco Terra Filial'); b.setv('#fx_g_forn_ger', 'Rafael Nunes')
time.sleep(.3); print('   ao digitar:', b.alerts('aside[role=dialog]'), '|', b.aside()[:260])
b.clk('Salvar', 'aside[role=dialog]'); al = b.alerts('aside[role=dialog]'); aberto = b.J("!!document.querySelector('aside[role=dialog]')"); print('   salvar:', al, '| aberto:', aberto, '| toast:', b.toast())
b.ok(aberto and 'já cadastrado' in al, 'CD-05 · CNPJ repetido barrado', al)
b.fim()
