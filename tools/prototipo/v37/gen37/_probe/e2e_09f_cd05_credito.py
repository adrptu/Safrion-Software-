# -*- coding: utf-8 -*-
"""Passo 9f · CD-05: parceiro de crédito inválido e válido."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2e_lib import B, campos, marcar, alerta_campo
b = B(); b.size(1440, 1000); b.goto('CD-05.dc.html')
b.clk('Cadastrar parceiro'); marcar(b, 'Parceiro de crédito')
for f in campos(b)[12:]: print('   campo:', f['id'], '|', f['lab'], '|', f['val'], f.get('opts') or '')
print('   seção:', b.aside()[b.aside().find('CRÉDITO'):][:600])
b.setv('#fx_g_forn_cnpj', '45.987.321/0001-60'); b.setv('#fx_g_forn_nome', 'Banco Cerrado')
b.clk('Salvar', 'aside[role=dialog]'); al = b.alerts('aside[role=dialog]'); print('   inválido:', al)
b.ok(b.J("!!document.querySelector('aside[role=dialog]')") and 'Escolha ao menos uma opção' in al and 'gerente' in al, 'CD-05 · crédito sem linha e sem gerente barrado junto aos campos', al)
seed = b.J("(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.indexOf('Banco Terra')>=0); return r?r.innerText.replace(/\\s+/g,' '):'';})()"); print('   Banco Terra:', seed)
import re
cn = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', seed); cn = cn.group(0) if cn else ''
b.setv('#fx_g_forn_cnpj', cn); time.sleep(.3); a = alerta_campo(b, '#fx_g_forn_cnpj'); print('   CNPJ repetido', cn, '→', a)
av = b.aside(); av = av[av.find('Já cadastrado'):][:120]; print('   aviso ao digitar:', av)
b.ok('Já cadastrado: Banco Terra' in av, 'CD-05 · CNPJ do Banco Terra repetido avisado junto ao campo, ao digitar', (a, av))
b.setv('#fx_g_forn_cnpj', '07.654.321/0001-98')
marcar(b, 'Custeio'); b.J("(()=>{const ls=[...document.querySelectorAll('aside[role=dialog] label')].filter(l=>l.innerText.trim()==='Penhor de safra'); ls[0].querySelector('input').click();})()")
b.setv('#fx_g_forn_ger', 'Rafael Nunes'); b.setv('#fx_g_forn_ger_email', 'rafael@bancocerrado'); b.setv('#fx_g_forn_ger_tel', '64 3611-2200')
b.clk('Salvar', 'aside[role=dialog]'); a = alerta_campo(b, '#fx_g_forn_ger_email'); print('   e-mail do gerente inválido →', a)
b.ok(bool(a), 'CD-05 · e-mail do gerente inválido barrado no campo', a)
b.setv('#fx_g_forn_ger_email', 'rafael@bancocerrado.com.br')
b.clk('Salvar', 'aside[role=dialog]'); a = alerta_campo(b, '#fx_g_forn_cnpj'); print('   CNPJ com dígito errado (-98) →', a)
b.ok('inválido' in a and b.J("!!document.querySelector('aside[role=dialog]')"), 'CD-05 · CNPJ com dígito verificador errado barrado no campo', a)
b.setv('#fx_g_forn_cnpj', '07.654.321/0001-59')
s = b.clk('Salvar', 'aside[role=dialog]'); t = b.toast(); al = b.alerts('aside[role=dialog]'); aberto = b.J("!!document.querySelector('aside[role=dialog]')")
print('   válido:', t, '| alertas:', al, '| aberto:', aberto); lin = b.rowtxt('Banco Cerrado'); print('   linha:', lin)
b.ok(not aberto and 'Banco Cerrado' in lin and 'crédito' in lin.lower(), 'CD-05 · parceiro de crédito válido salvo e na lista', (t, al, lin))
er = b.erros(); b.ok(not er, 'CD-05 sem erro de JS', er)
b.shot('e2e_09f_cd05_credito_invalido.png')   # antes do fim(): com falha, fim() lança e a captura se perderia
b.fim()
