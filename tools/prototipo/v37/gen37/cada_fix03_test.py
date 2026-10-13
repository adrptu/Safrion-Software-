# -*- coding: utf-8 -*-
"""CD-03 · regressão dos defeitos do verificador (11 verificações): horímetro compara com a última leitura gravada, subtítulo da edição
sem 'escolha a classe', conjuntos da máquina identificam o conjunto e abrem o certo, plural em 'não alocáveis' e select do formulário
sempre mostra o valor gravado ('Escolha…' quando vazio).
CADUX P9 (09/10/2026): reescrito com as mesmas regras sobre a seleção que abre detalhe (DEC-0910-01); roda a lógica da página no node
(cadux_node.py). Expectativas que mudaram, com o motivo:
  4  "+ Criar ativo" no cabeçalho (BOT-03), não "Cadastrar máquina ou instalação";
  6, 8, 9 os conjuntos da máquina são filhos selecionáveis no painel dela (SEL-01: produto → filhos), com o nome do conjunto e a operação
     ("Trator 03 + Distribuidor 3 t · Adubação a lanço"), e abrem no mesmo painel com "‹ {máquina}" (C07);
  7  "+ Criar conjunto" no cabeçalho com "Conjuntos" escolhido no mestre, não "Montar conjunto" na aba.
Uso: python3 cada_fix03_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
FIL = r"""function filhos(gid,titulo){ const F=painel(gid); const b=F&&F.c.blocos.find(b=>b.t===titulo); return b?(b.fil||[]).map(f=>f.t+' · '+f.sub):null; }
function abreFilho(gid,titulo,t){ const F=painel(gid); const b=F.c.blocos.find(b=>b.t===titulo); const f=b.fil.find(f=>f.t===t); f.go(); v(); }
function abreNome(nome){ const r=RW(C,'g_atv').find(r=>r.v.nome===nome); abre('g_atv',r.id); }
"""
o = roda('CD-03', AUX + FIL + r'''
edita('g_atv','a02'); fset('g_atv','cont_tr','3100'); OUT.t1=salva('g_atv'); OUT.o1=!!(painel('g_atv')&&!painel('g_atv').cons); fecha('g_atv');
edita('g_atv','a02'); fset('g_atv','cont_tr','3000'); salva('g_atv'); OUT.a2=errosT('g_atv');
fset('g_atv','cont_tr','3150'); OUT.t3=salva('g_atv'); OUT.o3=!!(painel('g_atv')&&!painel('g_atv').cons); fecha('g_atv');
edita('g_atv','a01'); OUT.d4=painel('g_atv').sub; OUT.cl4=fdis('g_atv','classe'); cancela('g_atv'); fecha('g_atv');
let x=v(); x.c3_criar(); v(); OUT.d5=painel('g_atv').sub; fecha('g_atv');
const silo=RW(C,'g_atv').find(r=>r.v.nome==='Silo 01'); edita('g_atv',silo.id); OUT.sv=[fval('g_atv','custo_f'),(fopts('g_atv','custo_f')||[])[0]]; cancela('g_atv'); fecha('g_atv');
abreNome('Distribuidor 3 t'); OUT.di=filhos('g_atv','Conjuntos'); fecha('g_atv');
x=mestre('conjuntos'); x.c3_criar(); v(); OUT.mt=[fval('g_cj','maq'),(fopts('g_cj','maq')||[])[0]]; fset('g_cj','impl','Plantadeira 24 linhas'); fmulti('g_cj','ops',['Plantio']); salva('g_cj'); OUT.a7=errosT('g_cj');
fset('g_cj','maq','Trator 02'); salva('g_cj'); fecha('g_cj'); x=mestre('');
abreNome('Plantadeira 24 linhas'); OUT.pl=filhos('g_atv','Conjuntos'); fecha('g_atv'); abreNome('Trator T1'); OUT.t1f=filhos('g_atv','Conjuntos'); fecha('g_atv');
abreNome('Plantadeira 24 linhas'); abreFilho('g_atv','Conjuntos','Trator 02 + Plantadeira 24 linhas'); const P=painel('g_cj'); OUT.ti=P&&[P.title,P.temPai,P.paiT]; fecha('g_cj');
x=mestre('conjuntos'); OUT.k1=linhaTxt('g_cj','k3'); const k4=RW(C,'g_cj').find(r=>r.v.maq==='Trator 04'); OUT.k2=k4&&linhaTxt('g_cj',k4.id);
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 horímetro: 3.100 h grava; depois 3.000 h é barrado com "A última leitura foi 3.100 h"', not o.get('o1') and 'A última leitura foi 3.100 h' in (o.get('a2') or ''), [o.get('t1'), o.get('a2')])
chk('2 horímetro maior que a última leitura grava', not o.get('o3') and 'Salvo: Trator 02' in (o.get('t3') or ''), o.get('t3'))
chk('3 edição: subtítulo pede capacidade/custo/calibração e não pede a classe (fixa)', 'Altere capacidade, custo por hora e calibração' in (o.get('d4') or '') and 'Escolha a classe' not in (o.get('d4') or '') and o.get('cl4') is True, o.get('d4'))
chk('4 criação: subtítulo "Escolha a classe para abrir a capacidade dela."', 'Escolha a classe para abrir a capacidade dela.' in (o.get('d5') or '') and 'Altere capacidade' not in (o.get('d5') or ''), o.get('d5'))
chk('5 Silo 01 sem custo: "Fonte do custo" mostra "Escolha…" (valor vazio), não uma fonte que não foi gravada', o.get('sv') == ['', 'Escolha…'], o.get('sv'))
chk('6 Distribuidor 3 t: o conjunto aparece pelo trator e pela operação', o.get('di') == ['Trator 03 + Distribuidor 3 t · Adubação a lanço'], o.get('di'))
chk('7 criar conjunto: Máquina começa em "Escolha…" e salvar sem ela pede a máquina no campo', o.get('mt') == ['', 'Escolha…'] and 'Informe máquina' in (o.get('a7') or ''), [o.get('mt'), o.get('a7')])
chk('8 Plantadeira 24 linhas: conjuntos "Trator T1 + …" e "Trator 02 + …" (Plantio); Trator T1 mostra o dele',
    o.get('pl') == ['Trator T1 + Plantadeira 24 linhas · Plantio', 'Trator 02 + Plantadeira 24 linhas · Plantio'] and o.get('t1f') == ['Trator T1 + Plantadeira 24 linhas · Plantio'], [o.get('pl'), o.get('t1f')])
ti = o.get('ti') or ['', False, '']
chk('9 o conjunto "Trator 02 + Plantadeira 24 linhas" abre no mesmo painel, com "‹ Plantadeira 24 linhas"', 'Trator 02 + Plantadeira 24 linhas' in ti[0] and ti[1] and 'Plantadeira 24 linhas' in (ti[2] or ''), ti)
chk('10 operadores: "Lucas, Beto não alocáveis" no plural', 'Lucas, Beto não alocáveis' in (o.get('k1') or '') and 'Lucas, Beto não alocáveis' in (o.get('k2') or ''), [o.get('k1'), o.get('k2')])
chk('11 nenhum erro de JS', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
