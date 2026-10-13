# -*- coding: utf-8 -*-
"""CD-05 (Parceiros e fornecedores): abrir fornecedor, marcar grupo, e-mail inválido mostra erro no campo (preservando o digitado),
corrigir, salvar; a linha e a cobertura por grupo refletem o salvo; não homologado não recebe cotação; CPF (11) ou CNPJ (14), contato e
canais autorizados: homologar exige contato e e-mail autorizado; canal sem autorização aparece na linha. Papéis (v3.9): grupos,
homologação e cobertura só em Fornecedores; parceiro de crédito não mostra campos de fornecedor; prestador exige as operações. 33 verificações.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: D1, D3) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  4  o fornecedor abre em consulta (SEL-01) e "Editar parceiro" abre o formulário lateral;
  14 o e-mail salvo aparece na linha (coluna E-mail) e no painel;
  15, 17, 29 a cobertura é o grupo "Grupos de insumo" do mestre (C17), em vez da aba "Cobertura";
  21, 24 o CPF/CNPJ fica no bloco Identidade do painel (§2.2: a lista tem até 7 colunas do papel, começando por Parceiro e Situação);
  30 "+ Criar parceiro" no cabeçalho (BOT-03).
Uso: python3 cd05test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUXC = r"""function cob(g){ const sel=st().mx_sel; let x=mestre('grupos'); const t=linhaTxt('g_cob','c_'+g); mestre(sel||''); return t; }
function marcados(k){ const F=painel('g_forn'); const f=F&&F.fields.find(f=>f.fid==='fx_g_forn_'+k); return f?(f.mopts||[]).filter(o=>o.on).map(o=>o.t):[]; }
function aberto(){ const F=painel('g_forn'); return !!(F&&!F.cons); }
function linN(n){ const r=(v().g_forn_rows||[]).find(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim().indexOf(n)===0); return r?r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '):''; }
function idN(n){ const r=RW(C,'g_forn').find(r=>r.v.nome===n); return r&&r.id; }
"""
o = roda('CD-05', AUX + AUXC + r'''
let x=mestre('fornecedor'); OUT.nh=JSON.stringify((x.g_forn_rows||[]).map(r=>r.cells.map(c=>(c.parts||[]).map(p=>p.t).join(' ')))).indexOf('não recebe cotação')>=0;
OUT.c0=cob('Combustível');
abre('g_forn','F03'); OUT.p1=cons('g_forn'); consGo('g_forn','Editar parceiro'); OUT.ab1=aberto(); OUT.g1=marcados('grupos');
fmulti('g_forn','grupos',marcados('grupos').concat(['Combustível'])); OUT.g2=marcados('grupos');
fset('g_forn','email','vendas@agronorte'); salva('g_forn'); OUT.e3=errosT('g_forn'); OUT.ab3=aberto(); OUT.v3=fval('g_forn','email'); OUT.g3=marcados('grupos');
fset('g_forn','whats','9999'); salva('g_forn'); OUT.e4=errosT('g_forn');
fset('g_forn','email','vendas@agronorte.com.br'); fset('g_forn','whats','65 99888-1122'); OUT.t5=salva('g_forn'); OUT.ab5=aberto(); fecha('g_forn');
x=v(); OUT.l5=linN('Agro Norte'); abre('g_forn','F03'); OUT.p5=JSON.stringify(cons('g_forn')); fecha('g_forn'); OUT.c5=cob('Combustível');
edita('g_forn','F03'); fset('g_forn','homol','Não'); OUT.t6=salva('g_forn'); fecha('g_forn'); OUT.c6=cob('Combustível');
x=mestre(''); edita('g_forn',idN('Banco Terra')); OUT.l7=rotulos('g_forn'); fmulti('g_forn','papeis',marcados('papeis').concat(['Fornecedor'])); fset('g_forn','email',''); fset('g_forn','homol','Sim'); salva('g_forn'); OUT.e7=errosT('g_forn');
cancela('g_forn'); fecha('g_forn'); OUT.ab8=aberto();
abre('g_forn',idN('Sementes Vale')); OUT.psv=JSON.stringify(cons('g_forn')); fecha('g_forn'); OUT.lsv=linN('Sementes Vale'); OUT.lfe=linN('Fertisul');
abre('g_forn',idN('Adão Ferreira')); OUT.pad=JSON.stringify(cons('g_forn')); fecha('g_forn');
x=mestre('fornecedor'); edita('g_forn','F01'); OUT.l9=rotulos('g_forn'); OUT.ct9=fval('g_forn','contato'); OUT.cn9=marcados('canais');
fmulti('g_forn','canais',['WhatsApp']); fset('g_forn','contato',''); salva('g_forn'); OUT.e10=errosT('g_forn'); OUT.c10=cob('Fertilizantes'); cancela('g_forn'); fecha('g_forn');
x=mestre(''); x.cd5_criar(); v(); fset('g_forn','nome','Joana Prado'); fset('g_forn','cnpj','987.654.321-001'); fmulti('g_forn','papeis',['Prestador']); salva('g_forn'); OUT.e11=errosT('g_forn');
fset('g_forn','cnpj','123.456.789-09'); salva('g_forn'); OUT.e12=errosT('g_forn');
fmulti('g_forn','canais',['WhatsApp']); fset('g_forn','cnpj','987.654.321-00'); salva('g_forn'); OUT.e13=errosT('g_forn');
fmulti('g_forn','canais',[]); fmulti('g_forn','ops',['Poda']); OUT.t14=salva('g_forn'); OUT.ab14=aberto(); OUT.e14=errosT('g_forn'); fecha('g_forn'); abre('g_forn',idN('Joana Prado')); OUT.pj=JSON.stringify(cons('g_forn'));
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 sem erro JS', not o.get('__errs'), o.get('__errs'))
chk('2 não homologado: não recebe cotação', o.get('nh'))
chk('3 Combustível começa sem fornecedor', 'Sem fornecedor' in (o.get('c0') or ''), o.get('c0'))
chk('4 Agro Norte abre em consulta e "Editar parceiro" abre o formulário lateral', (o.get('p1') or {}).get('t') == 'Parceiro · Agro Norte' and o.get('ab1'), o.get('p1'))
chk('5 grupos já marcados', len(o.get('g1') or []) >= 1, o.get('g1'))
chk('6 grupo Combustível marcado', 'Combustível' in (o.get('g2') or []), o.get('g2'))
chk('7 erro junto ao campo e-mail', 'email: E-mail inválido' in (o.get('e3') or ''), o.get('e3'))
chk('8 formulário continua aberto', o.get('ab3'))
chk('9 digitado preservado', o.get('v3') == 'vendas@agronorte', o.get('v3'))
chk('10 grupo marcado preservado', 'Combustível' in (o.get('g3') or []), o.get('g3'))
chk('11 WhatsApp inválido barrado', 'Informe DDD e número' in (o.get('e4') or ''), o.get('e4'))
chk('12 salvou e voltou à consulta', not o.get('ab5'), o.get('ab5'))
chk('13 aviso de salvo', bool(o.get('t5')), o.get('t5'))
chk('14 linha atualizada (grupos e e-mail salvos na linha e no painel)', 'Combustível' in (o.get('l5') or '') and 'vendas@agronorte.com.br' in (o.get('l5') or '') and 'vendas@agronorte.com.br' in (o.get('p5') or ''), [o.get('l5')])
chk('15 cobertura de Combustível recalculada (1 fornecedor, sem concorrência)', 'Sem concorrência' in (o.get('c5') or '') and ' 1 ' in ' ' + (o.get('c5') or '') + ' ', o.get('c5'))
chk('16 aviso: não recebe cotação', 'não recebe cotação' in (o.get('t6') or ''), o.get('t6'))
chk('17 Combustível volta a sem fornecedor', 'Sem fornecedor' in (o.get('c6') or ''), o.get('c6'))
L7 = o.get('l7') or []
chk('18 crédito sem campos de fornecedor', 'Linhas de crédito' in L7 and 'Homologado' not in L7 and 'Grupos homologados' not in L7, L7)
chk('19 homologar exige grupo e e-mail', 'grupo' in (o.get('e7') or '') and 'e-mail' in (o.get('e7') or ''), o.get('e7'))
chk('20 cancelar preserva e fecha', not o.get('ab8'))
chk('21 CPF/CNPJ do parceiro no painel (Identidade)', 'CPF ou CNPJ' in (o.get('psv') or ''), (o.get('psv') or '')[:200])
chk('22 WhatsApp sem autorização mostra o aviso', '65 99555-6677 não autorizado' in (o.get('lsv') or ''), o.get('lsv'))
chk('23 canal autorizado sem aviso', 'não autorizado' not in (o.get('lfe') or ''), o.get('lfe'))
chk('24 pessoa física com CPF', '123.456.789-09' in (o.get('pad') or ''), (o.get('pad') or '')[:200])
L9 = o.get('l9') or []
chk('25 formulário tem CPF ou CNPJ, contato e canais', all(x in L9 for x in ['CPF ou CNPJ', 'Nome do contato', 'Canais autorizados']), L9)
chk('26 contato preenchido', bool(o.get('ct9')), o.get('ct9'))
chk('27 canais do cadastro marcados', o.get('cn9') == ['E-mail', 'WhatsApp'], o.get('cn9'))
chk('28 homologar exige e-mail autorizado e contato', 'Marque E-mail' in (o.get('e10') or '') and 'nome do contato' in (o.get('e10') or ''), o.get('e10'))
chk('29 cobertura não muda antes de salvar', 'Fertilizantes' in (o.get('c10') or '') and '| 3 |' in (o.get('c10') or ''), o.get('c10'))
chk('30 12 dígitos barrado', 'Informe CPF (11 dígitos) ou CNPJ (14 dígitos).' in (o.get('e11') or ''), o.get('e11'))
chk('31 CPF repetido barrado', 'CPF já cadastrado em Adão Ferreira' in (o.get('e12') or ''), o.get('e12'))
chk('32 canal WhatsApp sem número barrado', 'Informe o WhatsApp ou desmarque o canal.' in (o.get('e13') or ''), o.get('e13'))
chk('33 pessoa física com CPF de 11 dígitos salva', not o.get('ab14') and '987.654.321-00' in (o.get('pj') or ''), [o.get('e14'), (o.get('pj') or '')[:200]])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
