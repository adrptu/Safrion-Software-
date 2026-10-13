# -*- coding: utf-8 -*-
"""CD-05 (defeitos do verificador): canal E-mail autorizado sem e-mail é barrado como o WhatsApp; o CNPJ da Fertisul é o mesmo no CD-05
e no PT-07 (Portal do parceiro), e esse CNPJ é recusado como parceiro novo. O parceiro novo do teste é Fornecedor (o campo Homologado só
existe na seção Fornecedor). 12 verificações.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: D1, D3) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica das páginas no node (cadux_node.py). Muda só o caminho: "+ Criar parceiro" no cabeçalho (BOT-03) e o parceiro existente abre em
consulta com "Editar parceiro" (SEL-01); o CPF/CNPJ fica no bloco Identidade do painel (ESPECIFICACAO §2.2: a lista tem até 7 colunas
do papel). As mensagens e as travas são as mesmas.
Uso: python3 cadp_vtest.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
pt = roda('PT-07', r'''let x=v(); OUT.t=JSON.stringify(x,(k,val)=>typeof val==='function'?undefined:val);''')
cnpjs = sorted(set(re.findall(r'12\.345\.678/\d{4}-\d{2}', pt.get('t') or '')))
chk('1 PT-07 mostra um CNPJ da Fertisul', len(cnpjs) == 1, cnpjs)
doc = cnpjs[0] if cnpjs else '12.345.678/0001-95'
AUXV = r"""function linN(n){ const r=(v().g_forn_rows||[]).find(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim().indexOf(n)===0); return r?r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '):''; }
function novo(nome,doc,canais){ v().cd5_criar(); v(); fset('g_forn','nome',nome); fset('g_forn','cnpj',doc); fmulti('g_forn','papeis',['Fornecedor']); if(canais) fmulti('g_forn','canais',canais);
  if(painel('g_forn').fields.some(f=>f.fid==='fx_g_forn_homol')) fset('g_forn','homol','Não'); return salva('g_forn'); }
function aberto(){ const F=painel('g_forn'); return !!(F&&!F.cons); }
"""
o = roda('CD-05', AUX + AUXV + r'''
let x=v(); abre('g_forn','F01'); OUT.f=JSON.stringify(cons('g_forn')); fecha('g_forn');
novo('Dup',__DOC__); OUT.a4=errosT('g_forn'); OUT.o4=aberto(); fecha('g_forn'); OUT.dup=linN('Dup');
novo('Teste Email Vazio','11.222.333/0001-81',['E-mail']); OUT.a6=errosT('g_forn'); OUT.o6=aberto(); fecha('g_forn'); OUT.ev=linN('Teste Email Vazio');
novo('Teste Whats Vazio','11.222.333/0001-81',['WhatsApp']); OUT.a9=errosT('g_forn'); OUT.o9=aberto();
fset('g_forn','whats','65 99123-4567'); salva('g_forn'); OUT.o10=aberto(); fecha('g_forn'); OUT.wv=linN('Teste Whats Vazio');
novo('Teste Email Cheio','11.444.777/0001-61',['E-mail']); fset('g_forn','email','contato@teste.com.br'); salva('g_forn'); OUT.o11=aberto(); fecha('g_forn'); OUT.ec=linN('Teste Email Cheio');
edita('g_forn','F07'); fmulti('g_forn','canais',['E-mail']); fset('g_forn','homol','Sim'); salva('g_forn'); OUT.a12=errosT('g_forn');
'''.replace('__DOC__', json.dumps(doc)))
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('2 sem erro JS', not o.get('__errs') and not pt.get('__errs'), [o.get('__errs'), pt.get('__errs')])
cd = sorted(set(re.findall(r'12\.345\.678/\d{4}-\d{2}', o.get('f') or '')))
chk('3 CD-05 mostra o mesmo CNPJ da Fertisul que o PT-07 (no bloco Identidade do painel)', cnpjs and cd == cnpjs, [cd, cnpjs])
chk('4 CNPJ da Fertisul recusado como parceiro novo', o.get('o4') and 'CNPJ já cadastrado em Fertisul' in (o.get('a4') or ''), o.get('a4'))
chk('5 nenhum parceiro Dup criado', o.get('dup') == '', o.get('dup'))
chk('6 canal E-mail sem e-mail barrado', o.get('o6') and 'Informe o e-mail ou desmarque o canal.' in (o.get('a6') or ''), o.get('a6'))
chk('7 erro junto ao campo e-mail', 'email: Informe o e-mail ou desmarque o canal.' in (o.get('a6') or ''), o.get('a6'))
chk('8 nenhum parceiro salvo com e-mail autorizado vazio', o.get('ev') == '', o.get('ev'))
chk('9 canal WhatsApp sem número barrado', o.get('o9') and 'Informe o WhatsApp ou desmarque o canal.' in (o.get('a9') or ''), o.get('a9'))
chk('10 com o número preenchido salva', not o.get('o10') and '65 99123-4567' in (o.get('wv') or ''), o.get('wv'))
chk('11 com o e-mail preenchido salva', not o.get('o11') and 'contato@teste.com.br' in (o.get('ec') or ''), o.get('ec'))
chk('12 homologar sem e-mail pede o e-mail da cotação', 'Informe o e-mail: a cotação é enviada por ele.' in (o.get('a12') or ''), o.get('a12'))
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
