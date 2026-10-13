# -*- coding: utf-8 -*-
"""CD-03 · máquinas, instalações e conjuntos (14 verificações): estado calculado, condição técnica só leitura vinda da Manutenção com as
ordens afetadas, classe primeiro com capacidade condicional, custo por hora com fonte, horímetro, conjunto com substituto, potência
insuficiente barrada no campo e conjunto montado.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: A2, A3, F1) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  1  a primária é "+ Criar ativo" no cabeçalho (BOT-02/03, C24), não "Cadastrar máquina ou instalação" no bloco;
  2  as ordens afetadas pelo T1 em manutenção ficam no Próximo passo do detalhe, um link por ordem (OS#OS-0420, OS#OS-0431, MA-04det#OM-0233;
     BOT-08 e X-REG), e a linha mostra só o estado (BOT-07); a faixa de atenção saiu (C12);
  4  o T1 abre em consulta (SEL-01): a condição vem da OM-0233 no bloco "Condição técnica" e, ao editar, o campo é só leitura e a classe fixa;
  6  na criação a classe vem vazia em "Todos" (X01/R14: sem padrão escondido) e é o 1º campo; ao escolher Trator, só a potência abre;
  11-14 os conjuntos ficam no mestre ("Conjuntos"), em linhas, com o substituto no Próximo passo do painel ("Trocar pelo Trator 02").
Uso: python3 cada_cd03_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
o = roda('CD-03', AUX + r'''
let x=v(); OUT.e1=x.c3e; OUT.crt=[x.cab_criar_on,x.cab_criarT];
OUT.t1=linhaTxt('g_atv','a01'); OUT.prox2=[x.dx_p.proxT,(x.dx_p.lks||[]).map(l=>l.t+'|'+l.h)];
x.c3qf_go=null; const qf=x.g_atv_cqf.find(c=>c.t==='A resolver'); qf.go(); x=v(); OUT.n3=x.c3_conta; OUT.vis3=(x.g_atv_rows||[]).map(r=>r.id);
x.g_atv_cqf.find(c=>c.t==='A resolver').go(); x=v(); OUT.n3b=x.c3_conta;
abre('g_atv','a01'); OUT.p4=cons('g_atv'); consGo('g_atv','Editar ativo'); OUT.cd4=[fdis('g_atv','cond_t'),fval('g_atv','cond_t'),fdis('g_atv','classe')]; OUT.l4=rotulos('g_atv'); cancela('g_atv'); fecha('g_atv');
edita('g_atv','a02'); fset('g_atv','cont_tr','100'); salva('g_atv'); OUT.e5=errosT('g_atv'); cancela('g_atv'); fecha('g_atv');
x=v(); x.c3_criar(); v(); OUT.l6=rotulos('g_atv'); OUT.cl6=fval('g_atv','classe'); fset('g_atv','classe','Trator'); OUT.l6b=rotulos('g_atv');
fset('g_atv','classe','Plantadeira'); fset('g_atv','linhas_pl','20'); fset('g_atv','esp_pl','0,45'); OUT.lv7=[fval('g_atv','larg_pl'),fval('g_atv','exige'),rotulos('g_atv').indexOf('Potência')];
fset('g_atv','classe','Pulverizador'); OUT.l8=rotulos('g_atv');
[['nome','Pulverizador PJ-2500'],['barra_pv','30'],['tanque_pv','2500'],['preq_pv','90'],['cont_pv','0'],['interv','90']].forEach(([k,val])=>fset('g_atv',k,val));
salva('g_atv'); OUT.e9=errosT('g_atv'); fset('g_atv','custo_h','90'); fset('g_atv','custo_f','Tabela de referência'); OUT.t9=salva('g_atv'); OUT.p9=cons('g_atv'); fecha('g_atv');
x=v(); const nid=RW(C,'g_atv').find(r=>r.v.nome==='Pulverizador PJ-2500'); OUT.r9=nid&&linhaTxt('g_atv',nid.id); OUT.e10=x.c3e;
x=mestre('pulverizador'); OUT.r9b=nid&&linhaTxt('g_atv',nid.id);
x=mestre('conjuntos'); OUT.k2=linhaTxt('g_cj','k2'); abre('g_cj','k2'); OUT.p11=cons('g_cj'); fecha('g_cj');
x=v(); x.c3_criar(); v(); OUT.maq0=fval('g_cj','maq'); fset('g_cj','maq','Trator 03'); fset('g_cj','impl','Plantadeira 24 linhas'); fmulti('g_cj','ops',['Plantio']); OUT.pc12=fval('g_cj','pot_c'); salva('g_cj'); OUT.e12=errosT('g_cj');
fset('g_cj','maq','Trator 02'); OUT.t13=salva('g_cj'); OUT.p13=cons('g_cj'); const kn=RW(C,'g_cj').find(r=>r.v.maq==='Trator 02'&&r.v.impl==='Plantadeira 24 linhas'); OUT.r13=kn&&linhaTxt('g_cj',kn.id);
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 cabeçalho: estado calculado "1 máquina em manutenção · 2 calibrações a resolver" e primária "+ Criar ativo" no cabeçalho',
    o.get('e1') == '1 máquina em manutenção · 2 calibrações a resolver' and o.get('crt') == [True, '+ Criar ativo'], [o.get('e1'), o.get('crt')])
px = o.get('prox2') or ['', []]
chk('2 Trator T1: linha "Em manutenção" sem verbo; o Próximo passo do detalhe diz a OM-0233 e o retorno e leva a cada ordem afetada',
    'Em manutenção' in (o.get('t1') or '') and 'OM-0233' in px[0] and 'retorno previsto 24/09' in px[0]
    and 'Abrir OS-0420|OS.dc.html#OS-0420' in px[1] and 'Abrir OS-0431|OS.dc.html#OS-0431' in px[1], [o.get('t1'), px])
chk('3 filtro rápido "A resolver" filtra as exceções (T1, TSI vencida, bomba a aferir) e desligar volta às 15',
    (o.get('n3') or '').startswith('3 de') and set(o.get('vis3') or []) >= {'a01'} and len(o.get('vis3') or []) == 3 and (o.get('n3b') or '').startswith('15 de 15'), [o.get('n3'), o.get('vis3'), o.get('n3b')])
p4 = o.get('p4') or {}; cd4 = o.get('cd4') or [None, '', None]
chk('4 T1 em consulta: condição técnica da OM-0233 (só leitura ao editar), classe fixa e sem "Valor do ativo"',
    'Em manutenção · OM-0233' in p4.get('txt', '') and cd4[0] is True and 'Em manutenção · OM-0233' in (cd4[1] or '') and cd4[2] is True and 'Valor do ativo' not in (o.get('l4') or []), [p4.get('t'), cd4, o.get('l4')])
chk('5 horímetro menor que a última leitura é barrado no campo', 'A última leitura foi 2.988 h' in (o.get('e5') or ''), o.get('e5'))
L6, L6b = o.get('l6') or [], o.get('l6b') or []
chk('6 criação: a classe é o 1º campo, vem vazia em "Todos" (X01) e Trator abre só a potência',
    L6[:1] == ['Classe'] and o.get('cl6') == '' and 'Potência' in L6b and 'Largura da barra' not in L6b and 'Linhas' not in L6b and 'Custo por hora' in L6b, [L6, o.get('cl6'), L6b])
lv = o.get('lv7') or [None, None, 0]
chk('7 Plantadeira: linhas × espaçamento calcula a largura de trabalho (20 × 0,45 = 9 m) e marca "Exige calibração"', lv[0] == '9' and lv[1] == 'Sim' and lv[2] == -1, lv)
L8 = o.get('l8') or []
chk('8 Pulverizador abre largura da barra, tanque útil e potência mínima do trator', 'Largura da barra' in L8 and 'Tanque útil' in L8 and 'Potência mínima do trator' in L8 and 'Linhas' not in L8, L8)
r9 = (o.get('r9') or '') + ' ' + (o.get('r9b') or '')
chk('9 sem custo por hora o cadastro é barrado no campo; com custo e fonte grava, a linha mostra R$/h e barra e tanque na classe, e o painel a fonte',
    'Informe o custo por hora' in (o.get('e9') or '') and 'R$ 90,00/h' in r9 and '30 m' in (o.get('r9b') or '') and '2.500 L' in (o.get('r9b') or '')
    and 'Tabela de referência' in (o.get('p9') or {}).get('txt', ''), [o.get('e9'), o.get('r9'), o.get('r9b'), o.get('t9')])
chk('10 estado do cabeçalho é recalculado (nova máquina sem calibração: 3 a resolver)', o.get('e10') == '1 máquina em manutenção · 3 calibrações a resolver', o.get('e10'))
p11 = o.get('p11') or {}
chk('11 conjunto do T1 fica Indisponível pela manutenção e sugere o substituto Trator 02; Carlos operador',
    'Indisponível' in (o.get('k2') or '') and 'Trator T1 em manutenção' in (p11.get('prox') or '') and p11.get('prim') == 'Trocar pelo Trator 02' and 'Carlos' in p11.get('txt', ''), [o.get('k2'), p11])
chk('12 criar conjunto: máquina começa vazia; Trator 03 (110 cv) com a plantadeira (exige 140 cv) dá erro no campo da máquina',
    o.get('maq0') == '' and 'Trator 03 tem 110 cv; Plantadeira 24 linhas exige 140 cv' in (o.get('e12') or '') and 'abaixo dos 140 cv' in (o.get('pc12') or ''), [o.get('maq0'), o.get('e12'), o.get('pc12')])
r13 = o.get('r13') or ''; p13 = o.get('p13') or {}
chk('13 com o Trator 02 o conjunto é montado: largura 12 m herdada, Disponível, Carlos alocável e sem rendimento',
    # a Situação da linha mostra a pendência ("Sem rendimento"); a disponibilidade fica no aviso e no painel (uma variável por coluna)
    '12 m' in r13 and 'disponível' in (o.get('t13') or '') and 'Carlos' in r13 and 'Conjunto montado' in (o.get('t13') or '') and 'Sem rendimento' in r13, [r13, o.get('t13'), p13.get('prox')])
chk('14 nenhum erro de JS na jornada', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
