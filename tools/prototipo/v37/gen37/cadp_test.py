# -*- coding: utf-8 -*-
"""CD-05 com papéis (v3.9): papéis com contagem; cadastrar cliente; cadastrar parceiro de crédito; CNPJ já cadastrado → aviso ao digitar
e "Abrir e ativar papel" sem duplicar; suspender com motivo obrigatório (sai da cotação). 15 verificações.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: D1, D3, E2) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  2, 3 os papéis são o mestre (Fornecedores, Clientes, Crédito, Transportadores, Prestadores e Grupos de insumo), com a contagem, em vez de
     chips de filtro e de uma aba "Cobertura" (C17); escolher o papel mostra as colunas dele;
  4, 7 "+ Criar parceiro" no cabeçalho com o papel do mestre já marcado (R03, BOT-03), em vez de "Cadastrar parceiro" no bloco;
  15 a cobertura de cotação é o grupo "Grupos de insumo" do mestre; o parceiro abre em consulta (SEL-01) e "Reativar parceiro" fica
     no formulário de edição.
Uso: python3 cadp_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUX5 = r"""function mlab(){ return v().mx_itens.filter(i=>i.item).map(i=>i.t+' '+i.n); }
function linN(n){ const r=(v().g_forn_rows||[]).find(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').indexOf(n)>=0); return r?r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '):''; }
function idN(n){ const r=RW(C,'g_forn').find(r=>r.v.nome===n); return r&&r.id; }
function campo(k){ const F=painel('g_forn'); return F&&F.fields.find(f=>f.fid==='fx_g_forn_'+k); }
function marcado(k,t){ const f=campo(k); const o=f&&(f.mopts||[]).find(o=>o.t===t); return !!(o&&o.on); }
"""
o = roda('CD-05', AUX + AUX5 + r'''
let x=v(); OUT.e1=x.cd5e; OUT.m2=mlab();
x=mestre('cliente'); OUT.c3=x.cd5_conta; OUT.cols3=GR('g_forn').cols.map(c=>c.l); OUT.r3=(x.g_forn_rows||[]).map(r=>r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '));
x.cd5_criar(); v(); fset('g_forn','cnpj','41.552.310/0001-04'); fset('g_forn','nome','Hortifruti Serra Azul'); OUT.l4=rotulos('g_forn');
fset('g_forn','lim','50.000'); salva('g_forn'); OUT.a5=errosT('g_forn'); OUT.o5=!!painel('g_forn');
fmulti('g_forn','prod',['Mamão Formosa classe A']); fset('g_forn','limv','2027-03-31'); fset('g_forn','entrega','CD Salvador/BA · seg–sex 05–10h'); OUT.t6=salva('g_forn'); OUT.o6=!!(painel('g_forn')&&!painel('g_forn').cons); fecha('g_forn');
x=v(); OUT.r6=linN('Hortifruti Serra Azul'); OUT.m6=mlab();
x=mestre('credito'); x.cd5_criar(); v(); fset('g_forn','cnpj','52.119.804/0001-08'); fset('g_forn','nome','Cooperativa Cerrado Crédito'); OUT.l7=rotulos('g_forn');
salva('g_forn'); OUT.a8=errosT('g_forn'); OUT.o8=!!painel('g_forn');
fmulti('g_forn','linhas',['Custeio']); fmulti('g_forn','gar',['Penhor de safra']); fset('g_forn','ger','Luís Prado'); fset('g_forn','ger_email','luis.prado@cerradocredito.coop.br'); fset('g_forn','ger_tel','64 99111-2233');
OUT.t9=salva('g_forn'); OUT.a9=errosT('g_forn'); OUT.o9=!!(painel('g_forn')&&!painel('g_forn').cons); fecha('g_forn'); x=v(); OUT.r9=linN('Cooperativa Cerrado Crédito'); OUT.m9=mlab();
x=mestre(''); x.cd5_criar(); v(); fmulti('g_forn','papeis',['Fornecedor']); fset('g_forn','cnpj','98.765.432/0001-98'); const fc=campo('cnpj'); OUT.d10=[fc.hasDup,fc.dupT]; salva('g_forn'); OUT.a10=errosT('g_forn');
campo('cnpj').dupGo(); v(); const P=painel('g_forn'); OUT.t11=P&&P.title; OUT.on11=[marcado('papeis','Fornecedor'),marcado('papeis','Cliente')]; OUT.l11=rotulos('g_forn');
OUT.t12=salva('g_forn'); fecha('g_forn'); x=v(); OUT.n12=RW(C,'g_forn').filter(r=>r.v.nome==='Coop Grão Sul').length; OUT.r12=linN('Coop Grão Sul'); OUT.m12=mlab(); OUT.c12=x.cd5_conta;
edita('g_forn','F05'); x=v(); x.cd5_suspender(); v(); OUT.l13=rotulos('g_forn'); salva('g_forn'); OUT.a13=errosT('g_forn'); OUT.o13=!!painel('g_forn');
fset('g_forn','motivo','Documentação fiscal vencida'); OUT.t14=salva('g_forn'); fecha('g_forn'); x=v(); OUT.r14=linhaTxt('g_forn','F05');
x=mestre('grupos'); OUT.cob=linhaTxt('g_cob','c_Sementes')||((x.g_cob_rows||[]).map(r=>r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | ')).find(t=>t.indexOf('Sementes')===0));
x=mestre(''); abre('g_forn','F05'); OUT.p15=cons('g_forn'); consGo('g_forn','Editar parceiro'); x=v(); OUT.re15=[x.cd5_reat,x.cd5_reatT];
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 sem erro JS e estado do cabeçalho calculado', not o.get('__errs') and o.get('e1') == '2 grupos sem fornecedor · 1 limite vencido', o.get('e1'))
chk('2 papéis no mestre com contagem', o.get('m2') == ['Todos os parceiros ', 'Fornecedores 8', 'Clientes 7', 'Crédito 3', 'Transportadores 2', 'Prestadores 1', 'Grupos de insumo 9'], o.get('m2'))
r3 = o.get('r3') or []
chk('3 Clientes: só clientes, com limite e validade em colunas próprias', len(r3) == 7 and all('Cliente' in x for x in r3) and 'Limite de crédito' in (o.get('cols3') or []) and (o.get('c3') or '').startswith('7 de 7'), [o.get('cols3'), r3[:2]])
L4 = o.get('l4') or []
chk('4 cliente: começa pelo CPF/CNPJ (papel Cliente herdado do mestre) e mostra só a seção Cliente', L4[:1] == ['CPF ou CNPJ'] and all(x in L4 for x in ['Produtos de interesse', 'Local e horário de entrega', 'Condição de pagamento', 'Limite de crédito comercial', 'Validade da análise de crédito'])
    and 'Grupos homologados' not in L4 and 'Linhas de crédito' not in L4, L4)
chk('5 cliente: produtos e validade do limite obrigatórios', o.get('o5') and 'Escolha ao menos uma opção.' in (o.get('a5') or '') and 'Informe a validade da análise de crédito.' in (o.get('a5') or ''), o.get('a5'))
chk('6 cliente salvo com limite e contagem', not o.get('o6') and 'R$ 50.000' in (o.get('r6') or '') and '31/03/2027' in (o.get('r6') or '') and 'Limite vigente' in (o.get('r6') or '') and 'Clientes 8' in (o.get('m6') or []), [o.get('r6'), o.get('m6'), o.get('t6')])
L7 = o.get('l7') or []
chk('7 crédito: seção com linhas, garantias e gerente com e-mail e telefone', all(x in L7 for x in ['Linhas de crédito', 'Garantias aceitas', 'Gerente do crédito', 'E-mail do gerente', 'Telefone do gerente']) and 'Produtos de interesse' not in L7 and 'Homologado' not in L7, L7)
chk('8 crédito: linhas e gerente obrigatórios', o.get('o8') and 'Escolha ao menos uma opção.' in (o.get('a8') or '') and 'Informe gerente do crédito.' in (o.get('a8') or ''), o.get('a8'))
chk('9 crédito salvo: linhas e garantias na linha; Crédito conta 4', not o.get('o9') and 'Custeio' in (o.get('r9') or '') and 'Penhor de safra' in (o.get('r9') or '') and 'Crédito 4' in (o.get('m9') or []), [o.get('r9'), o.get('m9'), o.get('a9')])
d10 = o.get('d10') or [False, '']
chk('10 CNPJ duplicado: aviso ao digitar com "Abrir e ativar papel" e salvar barrado', d10[0] and 'Já cadastrado: Coop Grão Sul (Cliente)' in (d10[1] or '') and 'CNPJ já cadastrado em Coop Grão Sul' in (o.get('a10') or ''), [d10, o.get('a10')])
chk('11 abre Coop Grão Sul com Fornecedor marcado e a seção Fornecedor', o.get('t11') == 'Parceiro · Coop Grão Sul' and o.get('on11') == [True, True] and 'Grupos homologados' in (o.get('l11') or []) and 'Produtos de interesse' in (o.get('l11') or []), [o.get('t11'), o.get('on11'), o.get('l11')])
m12 = o.get('m12') or []
chk('12 salvo sem duplicar: Coop Grão Sul com 2 papéis, total 22, Fornecedores 9', o.get('n12') == 1 and 'Fornecedor' in (o.get('r12') or '') and 'Cliente' in (o.get('r12') or '') and (o.get('c12') or '').startswith('22 de 22') and 'Fornecedores 9' in m12, [o.get('r12'), o.get('c12'), m12])
chk('13 suspender sem motivo é barrado junto ao campo', o.get('o13') and 'Motivo da suspensão' in (o.get('l13') or []) and 'motivo: Informe motivo da suspensão.' in (o.get('a13') or ''), [o.get('l13'), o.get('a13')])
chk('14 suspenso com motivo: aviso e situação na linha', 'Suspenso: Sementes Vale sai de cotação' in (o.get('t14') or '') and 'Suspenso' in (o.get('r14') or '') and 'Documentação fiscal vencida' in (o.get('r14') or ''), [o.get('t14'), o.get('r14')])
p15 = json.dumps(o.get('p15') or {}, ensure_ascii=False); cob = o.get('cob') or ''
chk('15 suspenso sai da cobertura (Sementes: 1 fornecedor, sem concorrência) e o parceiro abre com "Reativar parceiro"',
    cob.startswith('Sementes') and '1' in cob and 'Sem concorrência' in cob and 'Suspenso' in p15 and 'fora de cotação' in p15.lower() and (o.get('re15') or [False, ''])[1] == 'Reativar parceiro', [cob, p15[:300], o.get('re15')])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
