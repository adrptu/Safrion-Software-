# -*- coding: utf-8 -*-
"""Passo 9d · CD-05: formulário de parceiro novo com papel Cliente e com papel Parceiro de crédito (campos que aparecem)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos, marcar
b = B(); b.size(1440, 1000); b.goto('CD-05.dc.html')
print('  ', b.clk('Cadastrar parceiro'))
for f in campos(b): print('   campo0:', f['id'], '|', f['lab'], '|', f['val'], f.get('opts') or '')
print('   marcar Cliente:', marcar(b, 'Cliente'))
for f in campos(b): print('   campoC:', f['id'], '|', f['lab'], '|', f['val'], f.get('opts') or '')
print('   aside:', b.aside()[:1500])
