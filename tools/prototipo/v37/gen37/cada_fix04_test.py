# -*- coding: utf-8 -*-
"""CD-04 · regressão dos defeitos do verificador (12 verificações): aviso sem ponto duplo, ajuda das habilidades com a soma das
habilitações, líder inativo pede outro líder (no aviso e no campo), renomear a pessoa atualiza o líder da equipe, equipe nova com líder.
CADUX P9 (09/10/2026): reescrito com as mesmas regras sobre a seleção que abre detalhe (DEC-0910-01); roda a lógica da página no node
(cadux_node.py). Expectativas que mudaram, com o motivo:
  2  o rótulo é "Aprovar O.S. (agrônomo)" (C16, DEC-2609-05: aprovar não libera; o antigo continua como sinônimo nos dados);
  4, 5, 7, 9 a equipe é o grupo do mestre: o líder e o calendário aparecem no cabeçalho do detalhe e na ficha ("Ver ficha da equipe" →
     "Editar equipe"), não num cartão da aba Equipes (as abas saíram, C17);
  10 "+ Criar equipe" é secundário no rodapé do mestre (a primária da tela é "+ Criar pessoa", BOT-01).
Uso: python3 cada_fix04_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUX4 = r"""function ficha(id){ let x=mestre(id); x.dx_ficha(); v(); return cons('g_eq'); }
function selT(gid,k){ const F=painel(gid); const f=F&&F.fields.find(f=>f.fid==='fx_'+gid+'_'+k); if(!f) return null; const o=(f.opts||[]).find(o=>((o&&o.v!==undefined)?o.v:o)===f.v); return o?((o.t!==undefined)?o.t:o):null; }
"""
o = roda('CD-04', AUX + AUX4 + r'''
edita('g_pes','p1'); OUT.t1=salva('g_pes'); fecha('g_pes');
edita('g_pes','p5'); fmulti('g_pes','hab',['Irrigar','Operar trator','Aprovar O.S. (agrônomo)']); OUT.h2=fhelp('g_pes','hab'); cancela('g_pes'); fecha('g_pes');
edita('g_pes','p4'); fset('g_pes','sit','Inativa'); OUT.t3=salva('g_pes'); fecha('g_pes');
let x=mestre('e3'); OUT.dx4=[x.dx_sub,x.dx_p.proxT]; const f4=ficha('e3'); OUT.f4=f4&&f4.sub;
consGo('g_eq','Editar equipe'); OUT.lv=[fval('g_eq','lider'),selT('g_eq','lider')]; OUT.hl=fhelp('g_eq','lider');
fset('g_eq','cal','seg–sex · 07–17h'); salva('g_eq'); OUT.a6=errosT('g_eq'); OUT.o6=!!(painel('g_eq')&&!painel('g_eq').cons);
fset('g_eq','lider','Carlos'); OUT.t7=salva('g_eq'); OUT.o7=!!(painel('g_eq')&&!painel('g_eq').cons); fecha('g_eq'); x=mestre('e3'); OUT.dx7=x.dx_sub;
x=mestre(''); edita('g_pes','p2'); fset('g_pes','nome','Marcos Silva'); OUT.t8=salva('g_pes'); fecha('g_pes');
x=mestre('e2'); OUT.dx9=x.dx_sub; ficha('e2'); consGo('g_eq','Editar equipe'); OUT.lv9=[fval('g_eq','lider'),selT('g_eq','lider')]; cancela('g_eq'); fecha('g_eq');
x=v(); x.c4_neq(); v(); OUT.nt=[fval('g_eq','lider'),selT('g_eq','lider')]; fset('g_eq','nome','Campo 3'); salva('g_eq'); OUT.a10=errosT('g_eq');
fset('g_eq','lider','Paula'); OUT.t11=salva('g_eq'); fecha('g_eq'); x=v(); OUT.m11=x.mx_itens.map(i=>i.lab); const e3=RW(C,'g_eq').find(r=>r.v.nome==='Campo 3'); OUT.l11=e3&&e3.v.lider;
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 aviso "Salvo: Ana · alocável em O.S." sem ponto duplo', 'Salvo: Ana · alocável em O.S.' in (o.get('t1') or '') and 'O.S..' not in (o.get('t1') or ''), o.get('t1'))
chk('2 ajuda de Habilidades: "Exige NR-10, NR-31 e CREA com validade."', 'Exige NR-10, NR-31 e CREA com validade.' in (o.get('h2') or ''), o.get('h2'))
chk('3 inativar o Lucas grava e nomeia o próximo passo: escolher outro líder para Campo 2', 'Salvo: Lucas · inativa · escolha outro líder para Campo 2.' in (o.get('t3') or ''), o.get('t3'))
dx4 = o.get('dx4') or ['', '']
chk('4 a equipe Campo 2 mostra o líder Lucas inativa (cabeçalho do detalhe e ficha) e pede outro líder no Próximo passo',
    'Lucas' in dx4[0] and 'Lucas' in (o.get('f4') or '') and 'lucas está inativa' in dx4[1].lower() and 'líder ativo' in dx4[1].lower(), [dx4, o.get('f4')])
chk('5 "Editar equipe" da Campo 2 mostra o líder gravado "Lucas · inativa" (não Ana) com aviso', o.get('lv') == ['Lucas', 'Lucas · inativa'] and 'Lucas está inativa; escolha um líder ativo.' in (o.get('hl') or ''), [o.get('lv'), o.get('hl')])
chk('6 mudar só o calendário e salvar pede um líder ativo no campo Líder', o.get('o6') and 'Lucas está inativa; escolha um líder ativo.' in (o.get('a6') or ''), o.get('a6'))
chk('7 escolher Carlos grava: Campo 2 com líder Carlos e calendário seg–sex', not o.get('o7') and 'Carlos' in (o.get('dx7') or '') and 'seg–sex · 07–17h' in (o.get('dx7') or '') and 'inativa' not in (o.get('dx7') or ''), [o.get('dx7'), o.get('t7')])
chk('8 renomear Marcos avisa que o líder da Campo 1 foi atualizado', 'líder de Campo 1 atualizado' in (o.get('t8') or '') and 'O.S..' not in (o.get('t8') or ''), o.get('t8'))
chk('9 Campo 1: cabeçalho do detalhe e formulário mostram o líder "Marcos Silva"', 'Marcos Silva' in (o.get('dx9') or '') and o.get('lv9') == ['Marcos Silva', 'Marcos Silva'], [o.get('dx9'), o.get('lv9')])
chk('10 "+ Criar equipe": Líder começa em "Escolha…" e salvar sem ele pede o líder no campo', o.get('nt') == ['', 'Escolha…'] and 'Informe líder' in (o.get('a10') or ''), [o.get('nt'), o.get('a10')])
chk('11 com a Paula a equipe Campo 3 é criada e entra no mestre', o.get('l11') == 'Paula' and any(m.startswith('Campo 3') for m in o.get('m11', [])), [o.get('l11'), o.get('m11'), o.get('t11')])
chk('12 nenhum erro de JS', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
