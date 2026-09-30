# -*- coding: utf-8 -*-
"""Passo 9h · CD-04: pessoa caldeiro inválida (erro no campo) e válida (linha nova)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos, marcar, alerta_campo
BASE = ('fx_g_pes_nome', 'fx_g_pes_equipe', 'fx_g_pes_vinc', 'fx_g_pes_adm', 'fx_g_pes_ate', 'fx_g_pes_cal', 'fx_g_pes_custo', 'fx_g_pes_acesso', 'fx_g_pes_sit')
b = B(); b.size(1440, 1000); b.goto('CD-04.dc.html')
b.clk('Cadastrar pessoa')
print('   marcar caldeiro:', marcar(b, 'Preparar calda (caldeiro)'))
extra = [f for f in campos(b) if f['id'] and f['id'] not in BASE]
for f in extra: print('   campo novo:', f['id'], '|', f['lab'], '|', f['val'], f.get('opts') or '')
a = b.aside(); print('   habilitação:', a[a.find('Manutenção de máquinas'):][:420])
# inválido: sem nome, safrista sem data final, custo não numérico
b.setv('#fx_g_pes_vinc', 'Safrista'); b.setv('#fx_g_pes_custo', 'vinte')
b.clk('Salvar', 'aside[role=dialog]'); al = b.alerts('aside[role=dialog]'); print('   inválido:', al)
b.ok(b.J("!!document.querySelector('aside[role=dialog]')") and 'Informe nome' in al and b.val('#fx_g_pes_custo') == 'vinte', 'CD-04 · caldeiro inválido: erros no campo e digitado preservado', al)
b.shot('e2e_09h_cd04_invalido.png')
types = {f['id']: f['type'] for f in campos(b) if f['id']}; print('   tipos:', types.get('fx_g_pes_adm'), types.get('fx_g_pes_ate'), types.get('fx_g_pes_v31'))
b.setv('#fx_g_pes_nome', 'Joana Ribeiro'); b.setv('#fx_g_pes_adm', '2026-09-01'); b.setv('#fx_g_pes_ate', '2026-08-01'); b.setv('#fx_g_pes_custo', '38,50')
b.clk('Salvar', 'aside[role=dialog]'); a = b.alerts('aside[role=dialog]'); print('   até antes da admissão:', a)
b.ok(b.J("!!document.querySelector('aside[role=dialog]')") and ('admiss' in a.lower() or 'depois' in a.lower() or 'anterior' in a.lower()), 'CD-04 · "Disponível até" antes da admissão barrado', a)
b.setv('#fx_g_pes_ate', '2027-03-31'); b.setv('#fx_g_pes_v31', '2027-05-31')
b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); a = b.alerts('aside[role=dialog]'); aberto = b.J("!!document.querySelector('aside[role=dialog]')")
print('   válido:', t, '| alertas:', a, '| aberto:', aberto); lin = b.rowtxt('Joana Ribeiro'); print('   linha:', lin)
b.ok(not aberto and 'Joana Ribeiro' in lin and 'aldeir' in lin, 'CD-04 · caldeiro válido salvo e na lista', (t, a, lin))
hdr = b.J("[...document.querySelectorAll('header button, header a')].filter(x=>x.offsetParent!==null).map(x=>x.innerText.trim()).filter(Boolean).slice(-3)"); print('   cabeçalho:', hdr)
er = b.erros(); b.ok(not er, 'CD-04 sem erro de JS', er)
b.fim()
