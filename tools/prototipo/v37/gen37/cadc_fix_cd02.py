# -*- coding: utf-8 -*-
"""CD-02 · defeitos do verificador (8 verificações): cultura renomeada continua sendo a da criação; '+ Criar rendimento' salva na operação
mostrada; selo 'Sem pendências' na cor de concluído; operação e conjunto novos aparecem na operação certa.
CADUX P9 (09/10/2026): reescrito com as mesmas regras sobre a seleção que abre detalhe (DEC-0910-01); roda a lógica da página no node
(cadux_node.py). Expectativas que mudaram, com o motivo:
  2  a cultura se renomeia pela ficha ("Ver ficha da cultura" → "Editar cultura", C26) e a criação herda a cultura escolhida no mestre
     (R03); o aviso da criação diz "Criada: X1 em Soja RR" (BOT-03, verbo Criar), não "Salvo";
  6-8 (folga no artboard) são layout: passaram para o teste de navegador cadux_cd01_test.py ("a página não rola", CD-01 a CD-07); fica
     aqui a regra de que a operação nova e os dois conjuntos aparecem nela.
Uso: python3 cadc_fix_cd02.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AMAR, VERDE = 'color:#8A5A00', 'color:#1E7A4C'
o = roda('CD-02', AUX + r'''
let x=v(); OUT.s1=x.c2e_stst;
x=mestre('CU1'); x.dx_ficha(); v(); consGo('g_cult','Editar cultura'); fset('g_cult','nome','Soja RR'); salva('g_cult'); fecha('g_cult');
x=mestre('CU1'); x.c2_criar(); v(); OUT.cu=fval('g_cv','cult'); fset('g_cv','nome','X1'); fset('g_cv','dias','110'); OUT.t2=salva('g_cv'); OUT.o2=!!(painel('g_cv')&&!painel('g_cv').cons); fecha('g_cv');
x=v(); OUT.m2=x.mx_itens.map(i=>i.lab); const x1=RW(C,'g_cv').map(g=>g.kids||[]).flat().find(r=>r.v.nome==='X1'); OUT.r2=x1&&linhaTxt('g_cv',x1.id);
edita('g_cv','cv3'); salva('g_cv'); fecha('g_cv');
x=v(); x.c2t1_go(); x=mestre('OP1'); x.c2_criar(); v(); OUT.op=fval('g_rend','op'); fset('g_rend','cjid','Outro (descrever)');
[['conj','Trator 05 + Pulverizador 2'],['modo','Informado'],['rend','10'],['maq','100'],['pess','1'],['fonte','Medição local'],['vig','2027-06-30']].forEach(([k,val])=>fset('g_rend',k,val));
OUT.t4=salva('g_rend'); OUT.o4=!!(painel('g_rend')&&!painel('g_rend').cons); fecha('g_rend'); x=mestre('OP1'); OUT.dx4=x.dx_sub;
x=mestre(''); edita('g_rend','r6'); fset('g_rend','fonte','Medição local'); salva('g_rend'); fecha('g_rend'); x=v(); OUT.e5=x.c2e; OUT.s5=x.c2e_stst;
x.c2_criar(); v(); fset('g_rend','op','Outra operação…'); fset('g_rend','cjid','Outro (descrever)');
[['nop','Irrigação'],['conj','Pivô central 1'],['modo','Informado'],['rend','3'],['maq','50'],['pess','1'],['fonte','Medição local'],['vig','2027-06-30']].forEach(([k,val])=>fset('g_rend',k,val)); OUT.t6=salva('g_rend'); fecha('g_rend');
const irr=RW(C,'g_op').find(o=>o.v.nome==='Irrigação'); x=mestre(irr.id); x.c2_criar(); v(); OUT.op7=fval('g_rend','op'); fset('g_rend','cjid','Outro (descrever)');
[['conj','Pivô central 2'],['modo','Informado'],['rend','3'],['maq','50'],['pess','1'],['fonte','Medição local'],['vig','2027-06-30']].forEach(([k,val])=>fset('g_rend',k,val)); OUT.t7=salva('g_rend'); fecha('g_rend');
x=mestre(irr.id); OUT.dx7=x.dx_sub; OUT.r7=(x.g_rend_rows||[]).map(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim());
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 selo com pendências nasce amarelo', AMAR in (o.get('s1') or ''), o.get('s1'))
chk('2 cultura renomeada: a criação herda Soja RR e a cultivar X1 é salva nela, com o aviso próprio',
    o.get('cu') == 'Soja RR' and not o.get('o2') and 'Criada: X1 em Soja RR' in (o.get('t2') or '') and any(m.startswith('Soja RR · 4') for m in o.get('m2', []))
    and 'Semente de soja rr X1' in (o.get('r2') or ''), [o.get('cu'), o.get('t2'), o.get('m2'), o.get('r2')])
chk('3 "+ Criar rendimento" com Pulverização escolhida salva em Pulverização', o.get('op') == 'Pulverização' and not o.get('o4') and 'Pulverização rende 10,00 ha/h' in (o.get('t4') or '') and '2 rendimentos' in (o.get('dx4') or ''),
    [o.get('op'), o.get('t4'), o.get('dx4')])
chk('4 sem pendências: selo "Sem pendências" na cor de concluído (verde)', o.get('e5') == 'Sem pendências' and VERDE in (o.get('s5') or ''), [o.get('e5'), o.get('s5')])
chk('5 "Outra operação…" cria Irrigação com o 1º conjunto', 'Operação Irrigação criada' in (o.get('t6') or ''), o.get('t6'))
chk('6 com Irrigação escolhida, o 2º conjunto herda a operação', o.get('op7') == 'Irrigação' and 'Irrigação rende 3,00 ha/h' in (o.get('t7') or ''), [o.get('op7'), o.get('t7')])
chk('7 Irrigação mostra os dois conjuntos novos', o.get('r7') == ['Pivô central 1', 'Pivô central 2'] and '2 rendimentos' in (o.get('dx7') or ''), [o.get('r7'), o.get('dx7')])
chk('8 nenhum erro de JS', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
