# -*- coding: utf-8 -*-
"""CD-02 · culturas e operações cadastráveis (15 verificações): culturas → cultivares, ficha da cultura, 'Outra cultura…', item de
semente vinculado, operações → rendimentos, ficha da operação (processo e atividades), 'Outra operação…' e rendimento por cultura.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: C4, C5, D2, F1) sobre a seleção que abre detalhe (DEC-0910-01);
roda a lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  1, 9  as primárias são "+ Criar cultivar" e "+ Criar rendimento" no cabeçalho (BOT-02/03, C24); "Comparar com o realizado" é link
        no detalhe da aba Operações;
  2  tipo de ciclo e unidade de produtividade aparecem uma vez, no cabeçalho do detalhe da cultura (I21), não em cada linha;
  3, 10 a cultura e a operação abrem pela ficha ("Ver ficha da cultura" → "Editar cultura"; C26), não pela linha da árvore;
  4  a cultivar abre em consulta (SEL-01) e "Editar cultivar" mostra o formulário; o item de semente aparece na célula sem "›" (BOT-07);
  12 o "Conjunto ou equipe" é escolhido da lista do CD-03 ou do CD-04 (X-CAD-1); "Outro (descrever)" mantém o conjunto escrito à mão.
Uso: python3 cadc_cd02_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUX2 = r"""function lin(gid,nome){ const r=(v()[gid+'_rows']||[]).find(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim().indexOf(nome)===0); return r?r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '):null; }
function idDe(gid,f){ const r=(function w(l){ for(const x of l){ if(f(x)) return x; if(x.kids){ const k=w(x.kids); if(k) return k; } } return null; })(RW(C,gid)); return r?r.id:null; }
"""
o = roda('CD-02', AUX + AUX2 + r'''
let x=v(); OUT.e1=x.c2e; OUT.crt1=[x.cab_criar_on,x.cab_criarT];
x=mestre('CU1'); OUT.dx2=x.dx_sub; OUT.cols2=GR('g_cv').cols.map(c=>c.l);
x.dx_ficha(); v(); OUT.f3=cons('g_cult'); consGo('g_cult','Editar cultura'); OUT.l3=rotulos('g_cult'); OUT.d3=fdis('g_cult','tipo'); fecha('g_cult');
x=mestre('CU1'); abre('g_cv','cv3'); consGo('g_cv','Editar cultivar'); OUT.pre4=fval('g_cv','sem'); OUT.t4=salva('g_cv'); fecha('g_cv'); x=v(); OUT.r4=linhaTxt('g_cv','cv3'); OUT.e4=x.c2e;
edita('g_cv','cv2'); fset('g_cv','sem','Semente de milho AG 8700'); salva('g_cv'); OUT.a5=errosT('g_cv'); fset('g_cv','sem','Semente de soja 58 W'); salva('g_cv'); OUT.a5b=errosT('g_cv'); cancela('g_cv'); fecha('g_cv');
x=mestre(''); x.c2_criar(); v(); fset('g_cv','cult','Outra cultura…'); OUT.l6=rotulos('g_cv');
fset('g_cv','nome','BRS 373'); fset('g_cv','ncult','Sorgo'); fset('g_cv','tipo','Anual'); fset('g_cv','unid','sc de 60 kg/ha'); fset('g_cv','dias','120'); OUT.t6=salva('g_cv'); fecha('g_cv');
x=v(); const sg=RW(C,'g_cult').find(c=>c.v.nome==='Sorgo'); OUT.sg=sg&&[sg.v.tipo,sg.v.unid]; OUT.m6=x.mx_itens.map(i=>i.lab); OUT.r6=lin('g_cv','BRS 373');
x.c2_criar(); v(); fset('g_cv','cult','Café'); OUT.l7=rotulos('g_cv'); OUT.o7=fopts('g_cv','cult');
fset('g_cv','cult','Soja'); fset('g_cv','nome','58 W'); fset('g_cv','dias','118'); salva('g_cv'); OUT.a8=errosT('g_cv'); cancela('g_cv'); fecha('g_cv');
// ---- aba Operações ----
x=v(); x.c2t1_go(); x=v(); OUT.crt9=[x.cab_criarT,(x.dx_lks||[]).map(l=>l.t)];
x=mestre('OP1'); x.dx_ficha(); v(); consGo('g_op','Editar operação'); OUT.f10=[painel('g_op').title,fval('g_op','proc'),fval('g_op','atvs')];
fset('g_op','proc','Implantação'); OUT.t11=salva('g_op'); fecha('g_op'); x=mestre('OP1'); OUT.dx11=x.dx_sub;
x=v(); x.c2_criar(); v(); fset('g_rend','op','Outra operação…'); OUT.l12=rotulos('g_rend'); fset('g_rend','cjid','Outro (descrever)');
[['nop','Calagem'],['nproc','Implantação'],['conj','Trator 03 + Distribuidor de calcário'],['cult','Soja'],['larg','12'],['vel','8'],['efic','70'],['maq','150'],['impl','60'],['pess','1'],['pess_rs','38'],['fonte','Ensaio da fazenda'],['vig','2027-06-30']].forEach(([k,val])=>fset('g_rend',k,val));
OUT.t12=salva('g_rend'); OUT.e12=errosT('g_rend'); fecha('g_rend');
const cal=RW(C,'g_op').find(o=>o.v.nome==='Calagem'); OUT.cal=cal&&[cal.id,cal.v.proc]; if(cal){ x=mestre(cal.id); OUT.dx12=x.dx_sub; OUT.r12=lin('g_rend','Trator 03 + Distribuidor de calcário'); }
x=mestre('OP1'); x.c2_criar(); v(); fset('g_rend','cjid','k1'); fset('g_rend','cult','Todas');
[['vel','8'],['efic','75'],['pess','1'],['vig','2027-06-30']].forEach(([k,val])=>fset('g_rend',k,val)); salva('g_rend'); OUT.a13=errosT('g_rend');
fset('g_rend','cult','Milho'); OUT.t13=salva('g_rend'); OUT.o13=!!(painel('g_rend')&&!painel('g_rend').cons); fecha('g_rend'); x=mestre('OP1'); OUT.dx13=x.dx_sub;
OUT.ls=ls();
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 abre na aba Culturas com a primária "+ Criar cultivar" (cabeçalho) e o estado das pendências',
    o.get('crt1') == [True, '+ Criar cultivar'] and o.get('e1') == '1 cultivar sem semente · 1 premissa a validar', [o.get('crt1'), o.get('e1')])
chk('2 Soja: unidade de produtividade e ciclo anual no cabeçalho da cultura; coluna Registro fora da tabela',
    'Anual · produtividade em sc de 60 kg/ha' in (o.get('dx2') or '') and 'Registro' not in (o.get('cols2') or []), [o.get('dx2'), o.get('cols2')])
chk('3 a ficha da cultura abre "Editar cultura" (tipo de ciclo só consulta)', (o.get('f3') or {}).get('t') == 'Cultura · Soja' and o.get('l3') == ['Nome da cultura', 'Tipo de ciclo', 'Unidade de produtividade'] and o.get('d3') is True, [o.get('f3'), o.get('l3')])
chk('4 64 Z: salvar cria "Semente de soja 64 Z" (Produtos) e tira a pendência do cabeçalho',
    o.get('pre4') == 'Criar item ao salvar' and 'Semente de soja 64 Z' in (o.get('r4') or '') and 'criado em Produtos' in (o.get('t4') or '') and '1 cultivar sem semente' not in (o.get('e4') or ''), [o.get('pre4'), o.get('r4'), o.get('t4'), o.get('e4')])
chk('5 semente da cultura errada ou já vinculada a outra cultivar é barrada junto ao campo',
    'Escolha uma semente de soja' in (o.get('a5') or '') and 'Semente de soja 58 W já é a semente da cultivar 58 W' in (o.get('a5b') or ''), [o.get('a5'), o.get('a5b')])
chk('6 "Outra cultura…" cria Sorgo com a cultivar BRS 373 e a semente vinculada',
    'Nome da nova cultura' in (o.get('l6') or []) and 'Tipo de ciclo' in (o.get('l6') or []) and o.get('sg') == ['Anual', 'sc de 60 kg/ha'] and any(m.startswith('Sorgo · 1') for m in o.get('m6', []))
    and 'Semente de sorgo BRS 373' in (o.get('r6') or ''), [o.get('l6'), o.get('sg'), o.get('m6'), o.get('r6'), o.get('t6')])
chk('7 cultura perene esconde ciclo em dias e semente; a lista Cultura já tem Sorgo',
    'Ciclo até a colheita' not in (o.get('l7') or []) and 'Item de semente' not in (o.get('l7') or []) and 'Sorgo' in (o.get('o7') or []), [o.get('l7'), o.get('o7')])
chk('8 cultivar repetida na mesma cultura é barrada', '58 W já está cadastrada em Soja' in (o.get('a8') or ''), o.get('a8'))
chk('9 aba Operações: primária "+ Criar rendimento" e "Comparar com o realizado" no detalhe', (o.get('crt9') or [None, []])[0] == '+ Criar rendimento' and 'Comparar com o realizado' in (o.get('crt9') or [None, []])[1], o.get('crt9'))
f10 = o.get('f10') or [None, None, None]
chk('10 a ficha da operação abre processo (etapa de custo) e atividades usuais', f10[0] == 'Operação · Pulverização' and f10[1] == 'Tratos culturais' and 'Dessecação pré-plantio' in (f10[2] or ''), f10)
chk('11 processo salvo aparece no cabeçalho da operação', 'Processo Implantação' in (o.get('dx11') or '') and 'atividades usuais' in (o.get('t11') or ''), [o.get('dx11'), o.get('t11')])
r12 = o.get('r12') or ''
chk('12 "Outra operação…" cria Calagem com o rendimento só para Soja (12 × 8 ÷ 10 × 70% = 6,72 ha/h)',
    'Nome da nova operação' in (o.get('l12') or []) and (o.get('cal') or [None, None])[1] == 'Implantação' and 'Soja' in r12 and '6,72 ha/h' in r12 and 'Operação Calagem criada' in (o.get('t12') or ''),
    [o.get('l12'), o.get('cal'), r12, o.get('t12'), o.get('e12')])
chk('13 mesmo conjunto na mesma operação: repetido para Todas é barrado; para Milho é aceito',
    'já tem rendimento em Pulverização para todas as culturas' in (o.get('a13') or '') and not o.get('o13') and '2 rendimentos' in (o.get('dx13') or ''), [o.get('a13'), o.get('t13'), o.get('dx13')])
d = roda('CD-06', AUX + r'''let x=v(); const g=RW(C,'g_grp').find(g=>g.v.nome==='Sementes'); x=mestre(g.id); OUT.c=x.c6_conta; OUT.e=x.c6e;
  const it=(n)=>{ const r=(function w(l){ for(const q of l){ if(q.v&&q.v.item===n) return q; if(q.kids){ const k=w(q.kids); if(k) return k; } } return null; })(RW(C,'g_itm')); return r?linhaTxt('g_itm',r.id):null; };
  OUT.r=it('Semente de soja 64 Z'); OUT.r2=it('Semente de sorgo BRS 373');''',
         antes='(function(){ const o=' + (o.get('ls') or '{}') + '; for(const k in o) localStorage.setItem(k,o[k]); })();')
chk('14 os itens criados pelas cultivares (64 Z e BRS 373) aparecem em Produtos › Sementes, pendentes de preço e embalagem',
    d.get('r') and d.get('r2') and 'kg' in (d.get('r') or '') and (d.get('c') or '').startswith('6 de 6') and '3 itens sem preço · 2 itens sem embalagem' in (d.get('e') or ''), d)
chk('15 nenhum erro de JS na jornada', not o.get('__errs') and not d.get('__errs'), [o.get('__errs'), d.get('__errs')])
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
