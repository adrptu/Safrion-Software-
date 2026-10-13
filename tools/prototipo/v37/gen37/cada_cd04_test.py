# -*- coding: utf-8 -*-
"""CD-04 · pessoas e equipes (15 verificações): estado calculado, habilitação exigida e "Não alocável em O.S." sem bloquear o cadastro,
filtros de Função e "A resolver", formulário na ordem do trabalho, NR-10 exigida por "Irrigar", calendário herdado da equipe, acesso ao
app sem criar login, safrista com "Disponível até" e caldeira nova sem NR-31.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: A1, D4) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  1  a primária é "+ Criar pessoa" no cabeçalho (BOT-02/03, C24), não "Cadastrar pessoa" no bloco;
  2, 3 a linha mostra Situação, Habilidades, Vínculo, Habilitação, Próxima validade e Equipe; o custo-hora saiu da lista (G1, C15) e a
     vigência do contrato fica no painel ("Vínculo");
  6  a pessoa abre em consulta (SEL-01) e "Editar pessoa" mostra o formulário de sempre, na mesma ordem;
  7  o custo salvo fica gravado e só no painel, no bloco recolhido "Custo-hora (restrito)", nunca na linha (G1);
  13 criar em "Todas as pessoas" pede a equipe (vem vazia, R03); com uma equipe escolhida no mestre ela vem herdada.
Uso: python3 cada_cd04_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUX4 = r"""function nomes(){ return (v().g_pes_rows||[]).map(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim()); }
function qf(t){ const c=v().g_pes_cqf.find(c=>c.t===t); c.go(); return v(); }
function fun(k){ v().c4fun_set({target:{value:k}}); return v(); }
"""
o = roda('CD-04', AUX + AUX4 + r'''
let x=v(); OUT.e1=x.c4e; OUT.crt=[x.cab_criar_on,x.cab_criarT]; OUT.cols=GR('g_pes').cols.map(c=>c.l);
OUT.paula=linhaTxt('g_pes','p6'); OUT.fo=x.c4fun_opts.map(o=>o.t); OUT.irr=JSON.stringify(RW(C,'g_pes').map(r=>r.v)).indexOf('Irrigacionista');
OUT.lucas=linhaTxt('g_pes','p4'); abre('g_pes','p4'); OUT.plucas=cons('g_pes'); fecha('g_pes');
x=fun('cal'); OUT.a=nomes(); x=qf('A resolver'); OUT.b=nomes(); x=fun(''); OUT.b2=nomes(); OUT.ch=x.g_pes_cqf.find(c=>c.t==='A resolver').on; x=qf('A resolver'); OUT.c=x.c4_conta;
edita('g_pes','p4'); OUT.l6=rotulos('g_pes'); fset('g_pes','custo','40'); OUT.t7=salva('g_pes'); OUT.p7=cons('g_pes'); OUT.r7=linhaTxt('g_pes','p4'); OUT.cv7=RW(C,'g_pes').find(r=>r.id==='p4').v.custo; fecha('g_pes');
edita('g_pes','p4'); fset('g_pes','v31','2027-08-15'); salva('g_pes'); fecha('g_pes'); x=v(); OUT.r8=linhaTxt('g_pes','p4'); OUT.e8=x.c4e;
edita('g_pes','p7'); OUT.h0=fhelp('g_pes','hab'); fmulti('g_pes','hab',['Almoxarifado','Conferir','Irrigar']); OUT.l9=rotulos('g_pes'); OUT.h1=fhelp('g_pes','hab'); cancela('g_pes'); fecha('g_pes');
edita('g_pes','p9'); OUT.he=fhelp('g_pes','equipe'); OUT.ops=fopts('g_pes','acesso'); OUT.cal=fval('g_pes','cal');
fset('g_pes','acesso','Solicitar acesso ao app'); fset('g_pes','cal','escala 6×2 · 8h'); OUT.t11=salva('g_pes'); OUT.p11=cons('g_pes'); fecha('g_pes'); OUT.r11=linhaTxt('g_pes','p9');
edita('g_pes','p1'); OUT.acd=fdis('g_pes','acesso'); cancela('g_pes'); fecha('g_pes');
x=v(); x.c4_criar(); v(); OUT.eq0=fval('g_pes','equipe'); [['nome','Rita'],['equipe','Campo 2'],['vinc','Safrista'],['adm','2026-09-20'],['custo','32']].forEach(([k,val])=>fset('g_pes',k,val));
fmulti('g_pes','hab',['Preparar calda (caldeiro)']); salva('g_pes'); OUT.e13=errosT('g_pes');
fset('g_pes','ate','2027-03-31'); OUT.t14=salva('g_pes'); OUT.o14=!!(painel('g_pes')&&!painel('g_pes').cons); fecha('g_pes');
const rita=RW(C,'g_pes').find(r=>r.v.nome==='Rita'); OUT.r14=rita&&linhaTxt('g_pes',rita.id); OUT.fo14=v().c4fun_opts.map(o=>o.t);
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 cabeçalho: estado calculado "2 não alocáveis · 1 a renovar em 30 dias" e primária "+ Criar pessoa"', o.get('e1') == '2 não alocáveis · 1 a renovar em 30 dias' and o.get('crt') == [True, '+ Criar pessoa'], [o.get('e1'), o.get('crt')])
p = o.get('paula') or ''
chk('2 Paula é caldeira da equipe Campo 1 com NR-31 válida; "Irrigante" no lugar de "Irrigacionista"',
    'Preparar calda (caldeiro)' in p and 'Campo 1' in p and 'NR-31' in p and '30/04/2027' in p and 'Alocável' in p and o.get('irr') == -1 and 'Irrigantes (1)' in (o.get('fo') or []), [p, o.get('fo')])
l = o.get('lucas') or ''; pl = (o.get('plucas') or {}).get('txt', '') + (o.get('plucas') or {}).get('prox', '')
chk('3 Lucas (safrista) com NR-31 vencida aparece "Não alocável em O.S."; o motivo e a vigência do contrato no painel',
    'Não alocável em O.S.' in l and '15/08/2026' in l and 'Safrista' in l and 'NR-31' in pl and '31/07/2027' in pl, [l, pl[:300]])
chk('4 filtros do bloco: Função Caldeiros → Paula e Nilton; com A resolver → nenhum caldeiro; Todas → 12 (Igor e Marta do beneficiamento, BEN-1)',
    o.get('a') == ['Paula', 'Nilton'] and o.get('b') == [] and (o.get('c') or '').startswith('12 de 12'), [o.get('a'), o.get('b'), o.get('c')])
chk('5 filtro rápido "A resolver" mostra quem precisa de ação (Marcos a renovar, Lucas, Beto) e desligar volta às 12',
    o.get('b2') == ['Marcos', 'Lucas', 'Beto'] and o.get('ch') == 'true' and (o.get('c') or '').startswith('12 de 12'), [o.get('b2'), o.get('ch'), o.get('c')])
chk('6 "Editar pessoa": Nome → Equipe → Habilidades → validade da habilitação exigida → vínculo e vigência → calendário → custo com encargos; sem "Função"',
    o.get('l6') == ['Nome', 'Equipe', 'Habilidades', 'Validade da NR-31', 'Vínculo', 'Admissão', 'Disponível até', 'Calendário de trabalho', 'Custo-hora com encargos', 'Acesso ao app', 'Situação'], o.get('l6'))
p7 = o.get('p7') or {}
chk('7 salvar com NR-31 vencida grava (sem bloquear) e mantém "Não alocável em O.S." com aviso do efeito; o custo fica no painel (restrito)',
    'Não alocável em O.S.' in (o.get('r7') or '') and 'não alocável em O.S. até resolver NR-31 vencida em 15/08/2026' in (o.get('t7') or '') and str(o.get('cv7')) in ('40', '40.0')
    and 'Custo-hora (restrito)' in p7.get('txt', '') and 'R$' not in (o.get('r7') or ''), [o.get('t7'), o.get('r7'), o.get('cv7'), p7.get('txt', '')[-300:]])
chk('8 renovar a NR-31 libera o Lucas e o estado do cabeçalho é recalculado', '15/08/2027' in (o.get('r8') or '') and 'Não alocável' not in (o.get('r8') or '') and o.get('e8') == '1 não alocável · 1 a renovar em 30 dias', [o.get('r8'), o.get('e8')])
chk('9 marcar "Irrigar" faz aparecer a validade da NR-10 exigida (Rui não exigia nenhuma)', 'Nenhuma habilitação exigida' in (o.get('h0') or '') and 'Validade da NR-10' in (o.get('l9') or []) and 'Exige NR-10 com validade' in (o.get('h1') or ''), [o.get('h0'), o.get('l9'), o.get('h1')])
chk('10 calendário herdado da equipe aparece no campo Equipe; acesso ao app oferece "Solicitar acesso ao app"',
    'Calendário da equipe: seg–sáb · 06–15h · 9 h/dia' in (o.get('he') or '') and (o.get('ops') or [])[-2:] == ['Sem login', 'Solicitar acesso ao app'] and o.get('cal') == 'Da equipe', [o.get('he'), o.get('ops'), o.get('cal')])
chk('11 "Solicitar acesso ao app" (simulado) grava o pedido e a exceção de calendário aparece no painel',
    'pedido de acesso ao app enviado ao administrador (simulado)' in (o.get('t11') or '') and 'escala 6×2 · 8h' in (o.get('p11') or {}).get('txt', '') and 'Acesso solicitado' in (o.get('p11') or {}).get('txt', ''), [o.get('t11'), o.get('r11')])
chk('12 quem já tem login vê o acesso só em consulta (pessoa ≠ usuário, D4)', o.get('acd') is True, o.get('acd'))
chk('13 criação em "Todas": equipe vazia (R03); safrista sem "Disponível até" é barrado no campo', o.get('eq0') == '' and 'Informe até quando o safrista fica disponível' in (o.get('e13') or ''), [o.get('eq0'), o.get('e13')])
chk('14 caldeira nova sem NR-31 grava como "Não alocável em O.S." com NR-31 pendente e entra no filtro Caldeiros (3)',
    not o.get('o14') and 'Não alocável em O.S.' in (o.get('r14') or '') and 'pendente' in (o.get('r14') or '') and 'Caldeiros (3)' in (o.get('fo14') or []), [o.get('r14'), o.get('fo14'), o.get('t14')])
chk('15 nenhum erro de JS na jornada', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
