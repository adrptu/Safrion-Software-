# -*- coding: utf-8 -*-
"""CD-05 (defeitos do verificador, rodada 2): motivo da suspensão limpo ao reativar; menu do filtro de coluna só com valores das linhas
do papel escolhido; troca de papel sem filtro de coluna inativo; clientes de Vendas e Gestão cadastrados no CD-05. 15 verificações.
CADUX P9 (09/10/2026): reescrito com as mesmas regras sobre a seleção que abre detalhe (DEC-0910-01); roda a lógica das páginas no node
(cadux_node.py). Expectativas que mudaram, com o motivo:
  4-7  o parceiro abre em consulta e "Editar parceiro" mostra o formulário com "Suspender parceiro"/"Reativar parceiro" (SEL-01);
  8-13 o papel se escolhe no mestre (C17), não em chips de filtro; as regras de limpeza dos filtros de coluna são as mesmas;
  14   (conteúdo cabe na prancheta) é layout: passou para o teste de navegador cadux_cd01_test.py ("a página não rola" em CD-01 a CD-07).
Uso: python3 cadp_fix_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:500] if extra and not cond else ''), flush=True)
TXT = r"""function cel(r,i){ const c=r.cells.filter(c=>c.isData)[i]; return c?c.parts.map(p=>p.t).filter(Boolean):[]; }"""
ve4 = roda('VE-04', TXT + r'''let x=v(); OUT.c=(x.g_cart_rows||[]).map(r=>cel(r,1).join(' ').trim()).concat((x.g_rsv_rows||[]).map(r=>{ const t=cel(r,0).join(' '); const i=t.indexOf('·'); return i>=0?t.slice(i+1).trim():''; })).filter(Boolean);''')
ve5 = roda('VE-05', TXT + r'''let x=v(); OUT.o=(x.g_ob_rows||[]).map(r=>cel(r,0));''')
ge5 = roda('GE-05', TXT + r'''let x=v(); OUT.g=(x.g_rec_rows||[]).filter(r=>!/g2kid/.test(r.cls)).map(r=>cel(r,0)[0]).filter(Boolean);''')
s_ve4 = set(ve4.get('c') or [])
s_cli5 = {x[1] for x in (ve5.get('o') or []) if len(x) > 1 and x[0].strip().endswith('venda')}
s_bar5 = {x[1] for x in (ve5.get('o') or []) if len(x) > 1 and x[0].strip().endswith('barter')}
s_ge5 = set(ge5.get('g') or [])
AUXF = r"""function nomes(){ return (v().g_forn_rows||[]).map(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim()); }
function menu(k){ g2set(C,'g_forn',{fmc:k}); const x=v(); const o=(x.g_forn_fm.vals||[]).map(a=>a.t+' '+a.n); g2set(C,'g_forn',{fmc:null}); v(); return o; }
function so(k,val){ g2set(C,'g_forn',{f:Object.assign({},g2st(C,'g_forn').f||{},{[k]:[val]})}); v(); }
function chips(){ return (v().g_forn_fchips||[]).map(c=>c.t); }
function aberto(){ const F=painel('g_forn'); return !!(F&&!F.cons); }
"""
o = roda('CD-05', AUX + AUXF + r'''
let x=mestre('cliente'); OUT.cli=nomes(); x=mestre('fornecedor'); OUT.forn=nomes(); x=mestre(''); OUT.coop=JSON.stringify(x,(k,val)=>typeof val==='function'?undefined:val).indexOf('Coopergrão')>=0;
edita('g_forn','F02'); x=v(); x.cd5_suspender(); v(); fset('g_forn','motivo','Entrega fora do prazo'); salva('g_forn'); OUT.o4=aberto(); fecha('g_forn'); OUT.r4=linhaTxt('g_forn','F02');
edita('g_forn','F02'); x=v(); OUT.re5=x.cd5_reatT; x.cd5_reativar(); v(); OUT.sit5=g2st(C,'g_forn').fm.draft.sit; salva('g_forn'); OUT.o5=aberto(); fecha('g_forn'); OUT.r5=linhaTxt('g_forn','F02');
edita('g_forn','F02'); x=v(); x.cd5_suspender(); v(); OUT.mv6=fval('g_forn','motivo'); OUT.hp6=fhelp('g_forn','motivo'); salva('g_forn'); OUT.e7=errosT('g_forn'); OUT.o7=aberto(); cancela('g_forn'); fecha('g_forn'); OUT.r7=linhaTxt('g_forn','F02');
x=mestre('cliente'); OUT.m8=menu('papel'); OUT.m9=menu('papeis');
x=mestre(''); so('papeis','Cliente'); OUT.a10=[chips(),nomes().length]; x=mestre('fornecedor'); OUT.b10=[chips(),nomes().length];
x=mestre(''); OUT.d11=[chips(),nomes().length];
so('nome','Fertisul'); x=mestre('fornecedor'); OUT.e12=[chips(),nomes()];
g2set(C,'g_forn',{f:{}}); x=mestre('cliente'); so('papel','Limite vencido'); OUT.g13=[chips(),nomes().length]; x=mestre(''); OUT.h13=[chips(),nomes().length];
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 sem erro JS', not o.get('__errs') and not ve4.get('__errs') and not ve5.get('__errs') and not ge5.get('__errs'), [o.get('__errs'), ve4.get('__errs'), ve5.get('__errs'), ge5.get('__errs')])
cli, forn = set(o.get('cli') or []), set(o.get('forn') or [])
falta = sorted((s_ve4 | s_ge5 | s_cli5) - cli)
chk('2 clientes com pedido (VE-04), contrato de venda (VE-05) e título (GE-05) existem no CD-05 como Cliente',
    not falta and {'Coop Grão Sul', 'Atacado Bom Preço', 'CD Horti'} <= cli and len(s_ve4) >= 3 and len(s_ge5) >= 4, [falta, sorted(s_ve4), sorted(s_ge5), sorted(s_cli5)])
chk('3 contraparte de barter (VE-05) cadastrada como Fornecedor; Coopergrão, sem uso em outra tela, saiu', s_bar5 and s_bar5 <= forn and not o.get('coop'), [sorted(s_bar5), sorted(forn)])
chk('4 suspenso com motivo na linha', not o.get('o4') and 'Suspenso' in (o.get('r4') or '') and 'Entrega fora do prazo' in (o.get('r4') or ''), o.get('r4'))
chk('5 reativado: linha volta a Homologado, sem o motivo', o.get('re5') == 'Reativar parceiro' and o.get('sit5') == 'Ativo' and not o.get('o5') and 'Homologado' in (o.get('r5') or '') and 'Entrega fora do prazo' not in (o.get('r5') or ''), [o.get('re5'), o.get('r5')])
chk('6 nova suspensão começa com motivo vazio e a ajuda não promete histórico', o.get('mv6') == '' and 'Aparece na listagem enquanto durar a suspensão.' in (o.get('hp6') or '') and 'histórico' not in (o.get('hp6') or ''), [o.get('mv6'), o.get('hp6')])
chk('7 salvar sem motivo novo é barrado junto ao campo', o.get('o7') and 'motivo: Informe motivo da suspensão.' in (o.get('e7') or '') and 'Suspenso' not in (o.get('r7') or ''), [o.get('e7'), o.get('r7')])
m8 = o.get('m8') or []
chk('8 Clientes · Situação do papel: sem "—" dos não clientes, contagens somam 7', m8 and not any(x.startswith('—') for x in m8) and sum(int(x.rsplit(' ', 1)[1]) for x in m8) == 7, m8)
chk('9 Clientes · Papéis: só valores das 7 linhas de cliente (Coop. Vale também é Fornecedor), sem valor zerado', o.get('m9') == ['Cliente 7', 'Fornecedor 1'], o.get('m9'))
a10, b10 = o.get('a10') or [[], 0], o.get('b10') or [[], 0]
chk('10 Papéis: Cliente em Todos; em Fornecedores o filtro da coluna que sai é limpo', 'Papéis: Cliente' in a10[0] and a10[1] == 7 and not any(c.startswith('Papéis') for c in b10[0]) and b10[1] == 8, [a10, b10])
d11 = o.get('d11') or [[], 0]
chk('11 de volta a Todos o filtro limpo não reaparece', not any(c.startswith('Papéis') for c in d11[0]) and d11[1] == 20, d11)
e12 = o.get('e12') or [[], []]
chk('12 filtro de coluna comum às duas grades continua valendo em Fornecedores', 'Parceiro: Fertisul' in e12[0] and e12[1] == ['Fertisul'], e12)
g13, h13 = o.get('g13') or [[], 0], o.get('h13') or [[], 0]
chk('13 filtro de Situação do papel (texto muda com o papel) é limpo ao trocar de papel', any(c.startswith('Situação do papel') for c in g13[0]) and g13[1] == 1 and not any(c.startswith('Situação do papel') for c in h13[0]) and h13[1] == 20, [g13, h13])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
