# -*- coding: utf-8 -*-
"""Passo 9b · CD-01: cadastrar fazenda inválida (erro no campo) e válida (linha nova)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos, fid, alerta_campo
b = B(); b.size(1440, 1000); b.goto('CD-01.dc.html')
n0 = b.J("[...document.querySelectorAll('[role=row].g2ed')].length")
print('  ', b.clk('+ Cadastrar fazenda'))
for f in campos(b): print('   campo:', f)
print('   aside:', b.aside()[:300])
s = b.clk('Salvar', 'aside[role=dialog]'); al = b.alerts('aside[role=dialog]'); print('   salvar vazio:', s, '| alertas:', al)
b.ok(bool(al) and b.J("!!document.querySelector('aside[role=dialog]')"), 'CD-01 · fazenda vazia: erros junto aos campos e formulário aberto', al)
b.shot('e2e_09b_cd01_invalido.png')
# inválido por conteúdo: nome repetido e área não numérica
b.setv('#fx_g_faz_nome', 'Santa Rita'); b.setv('#fx_g_faz_mun', 'Jataí'); b.setv('#fx_g_faz_area', 'abc')
b.clk('Salvar', 'aside[role=dialog]'); a1 = alerta_campo(b, '#fx_g_faz_nome'); a2 = alerta_campo(b, '#fx_g_faz_area'); print('   repetido/área:', a1, '|', a2, '| valores:', b.val('#fx_g_faz_nome'), b.val('#fx_g_faz_area'))
b.ok(bool(a1) and bool(a2) and b.val('#fx_g_faz_area') == 'abc', 'CD-01 · nome repetido e área "abc": erro em cada campo, digitado preservado', (a1, a2))
b.setv('#fx_g_faz_area', '-5'); b.setv('#fx_g_faz_nome', 'Esperança'); b.clk('Salvar', 'aside[role=dialog]'); a3 = alerta_campo(b, '#fx_g_faz_area'); print('   área −5:', a3)
b.ok(bool(a3), 'CD-01 · área negativa barrada no campo', a3)
# válido
b.setv('#fx_g_faz_area', '850'); b.setv('#fx_g_faz_car', 'GO-5211909-ABCD'); b.setv('#fx_g_faz_matr', 'Matrícula 7.001 · CRI de Jataí')
s = b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); aberto = b.J("!!document.querySelector('aside[role=dialog]')"); print('   salvar válido:', s, '| toast:', t, '| aberto:', aberto, '| alertas:', b.alerts('aside[role=dialog]'))
lin = b.rowtxt('Esperança'); print('   linha:', lin)
b.ok(not aberto and 'Esperança' in lin and '850 ha' in lin and 'Jataí' in lin, 'CD-01 · fazenda válida salva e aparece na lista (850 ha, Jataí/GO)', (t, lin))
# a fazenda nova aparece no agrupamento de talhões e reabre pela linha
print('   talhões:', b.J("[...document.querySelectorAll('[role=row]')].map(r=>r.innerText.replace(/\\s+/g,' ')).filter(t=>t.indexOf('Esperança')>=0)"))
b.row('Esperança'); print('   reabrir:', b.aside()[:200]); b.clk('Cancelar', 'aside[role=dialog]')
er = b.erros(); b.ok(not er, 'CD-01 sem erro de JS', er)
b.fim()
