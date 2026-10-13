# -*- coding: utf-8 -*-
"""CD-06 · produtos, unidades e locais (15 verificações): grupo com natureza de custo, preço de referência com data, embalagem
estruturada, controle em um campo, situação Ativo/Inativo, unidade-base travada com motivo, locais com fazenda e capacidade só em
tanque e silo; o cabeçalho mostra pendência do cadastro (não do Estoque).
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: C1, C2, D2, E2) sobre a seleção que abre detalhe (DEC-0910-01);
roda a lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  1, 13 "+ Criar item" e "+ Criar local" no cabeçalho (BOT-02/03, C24), não "Cadastrar …" no bloco;
  2  o item abre em consulta: o saldo e os lotes vêm do Estoque no bloco "Locais", com "Abrir saldos e lotes" (SEL-01, I24);
  3  o grupo abre pela ficha ("Ver ficha do grupo" → "Editar grupo"; C26) e a natureza aparece uma vez, no cabeçalho do grupo (C19);
  9  o item inativo sai de "Todos" e aparece no filtro "Inativos" (R08);
  11 em "Todos os itens" o grupo vem vazio (X01/R14: sem padrão escondido) e é escolhido.
Uso: python3 cadc_cd06_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUX6 = r"""function idDe(n){ const r=(function w(l){ for(const q of l){ if(q.v&&q.v.item===n) return q; if(q.kids){ const k=w(q.kids); if(k) return k; } } return null; })(RW(C,'g_itm')); return r&&r.id; }
function grp(n){ const g=RW(C,'g_grp').find(g=>g.v.nome===n); return g&&g.id; }
function vtxt(){ const x=v(); return JSON.stringify(x,(k,val)=>typeof val==='function'?undefined:val); }
function lin(gid,n){ const r=(v()[gid+'_rows']||[]).find(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim().indexOf(n)===0); return r?r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | '):null; }
"""
o = roda('CD-06', AUX + AUX6 + r'''
let x=v(); OUT.e1=x.c6e; OUT.crt1=[x.cab_criar_on,x.cab_criarT]; const vt=vtxt(); OUT.q1=vt.indexOf('quarentena')>=0||vt.indexOf('PC-088')>=0;
OUT.r2=linhaTxt('g_itm',idDe('KCl 60%')); abre('g_itm',idDe('KCl 60%')); OUT.p2=cons('g_itm'); fecha('g_itm');
x=mestre(grp('Herbicidas')); x.dx_ficha(); v(); consGo('g_grp','Editar grupo'); OUT.ti3=painel('g_grp').title; OUT.nat3=fval('g_grp','nat');
fset('g_grp','nat','3.1.01 · Fertilizantes e corretivos'); salva('g_grp'); fecha('g_grp'); x=mestre(grp('Herbicidas')); OUT.dx3=x.dx_sub;
x=mestre(''); edita('g_itm',idDe('Glifosato 480')); OUT.f4=[fdis('g_itm','un'),fhelp('g_itm','un'),fval('g_itm','emb'),fval('g_itm','cont'),painel('g_itm').fields.find(f=>f.fid==='fx_g_itm_preco').u,fval('g_itm','ctrl')]; cancela('g_itm'); fecha('g_itm');
edita('g_itm',idDe('Ureia 45%')); OUT.f5=[fdis('g_itm','un'),fhelp('g_itm','un')]; cancela('g_itm'); fecha('g_itm');
const cal=idDe('Calcário dolomítico'); edita('g_itm',cal); OUT.l6=rotulos('g_itm'); fset('g_itm','preco','480'); salva('g_itm'); OUT.a6=errosT('g_itm');
fset('g_itm','pdata','2026-09-20'); salva('g_itm'); fecha('g_itm'); x=v(); OUT.r7=linhaTxt('g_itm',cal); OUT.e7=x.c6e;
edita('g_itm',cal); fset('g_itm','emb','Big bag'); OUT.l8=rotulos('g_itm'); salva('g_itm'); OUT.a8=errosT('g_itm'); cancela('g_itm'); fecha('g_itm');
const fc=idDe('Fungicida C'); edita('g_itm',fc); fset('g_itm','sit','Inativo'); OUT.t9=salva('g_itm'); fecha('g_itm'); x=v(); OUT.r9=linhaTxt('g_itm',fc);
const qi=(x.g_itm_cqf||[]).find(c=>c.t==='Inativos'); OUT.qf9=qi&&(qi.t+' '+qi.n); if(qi){ qi.go(); x=v(); OUT.r9b=linhaTxt('g_itm',fc); qi.go&&x.g_itm_cqf.find(c=>c.t==='Inativos').go(); x=v(); }
x=mestre(''); x.c6_criar(); v(); OUT.g10=fval('g_itm','grupo'); fset('g_itm','grupo','Outro grupo…'); OUT.l10=rotulos('g_itm');
[['item','Trichoderma WP'],['ngrupo','Biológicos'],['nnat','3.1.02 · Defensivos'],['un','kg'],['emb','Saco'],['cont','1'],['ctrl','Lote e validade'],['preco','85'],['pdata','2026-09-20'],['local','Câmara fria']].forEach(([k,val])=>fset('g_itm',k,val));
OUT.t10=salva('g_itm'); OUT.a10=errosT('g_itm'); fecha('g_itm'); x=v(); OUT.m10=x.mx_itens.map(i=>i.lab); OUT.r10=linhaTxt('g_itm',idDe('Trichoderma WP')); x=mestre(grp('Biológicos')||''); OUT.dx10=x.dx_sub;
x=mestre(''); x.c6_criar(); v(); fset('g_itm','grupo','Fertilizantes'); fset('g_itm','item','MAP 11-52'); fset('g_itm','cont','50'); salva('g_itm'); OUT.a11=errosT('g_itm'); cancela('g_itm'); fecha('g_itm');
x=mestre('locais'); OUT.lc=GR('g_loc').cols.map(c=>c.l); OUT.tq=lin('g_loc','Tanque Sede'); OUT.si=lin('g_loc','Silo 01'); OUT.g1=lin('g_loc','Galpão 1');
OUT.crt13=[x.cab_criar_on,x.cab_criarT]; OUT.novo13=vtxt().indexOf('Novo local')>=0; x.c6_criar(); v(); OUT.ti13=painel('g_loc')&&painel('g_loc').title;
fset('g_loc','nome','Galpão BV 2'); fset('g_loc','faz','Boa Vista'); fset('g_loc','tipo','Galpão'); OUT.t14=salva('g_loc'); fecha('g_loc'); OUT.r14=lin('g_loc','Galpão BV 2');
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 abre com a pendência do cadastro no cabeçalho, "+ Criar item" e sem fatos do Estoque (quarentena, pedido)', o.get('e1') == '1 item sem preço' and o.get('crt1') == [True, '+ Criar item'] and not o.get('q1'), [o.get('e1'), o.get('crt1'), o.get('q1')])
r2 = o.get('r2') or ''; p2 = json.dumps(o.get('p2') or {}, ensure_ascii=False)
chk('2 item mostra unidade, embalagem, controle e preço com data; o saldo (físico e disponível, do cenário do Estoque: A29) fica no painel com "Abrir saldos e lotes"',
    all(x in r2 for x in ['kg', 'big bag de 1.000 kg', 'Só lote', 'R$ 2,40/kg', '15/09/2026']) and 'Abrir saldos e lotes' in p2 and 'item com 60.000 kg no Estoque (50.000 kg disponíveis)' in p2 and 'EST.dc.html#sec=saldos' in p2, [r2, p2[:300]])
chk('3 a ficha do grupo abre nome e natureza; a natureza salva aparece no cabeçalho do grupo',
    o.get('ti3') == 'Grupo · Herbicidas' and o.get('nat3') == '3.1.02 · Defensivos' and '3.1.01 · Fertilizantes e corretivos' in (o.get('dx3') or ''), [o.get('ti3'), o.get('nat3'), o.get('dx3')])
f4 = o.get('f4') or [None] * 6
chk('4 Glifosato: unidade-base travada com o motivo (saldo); embalagem galão de 20 L; preço em R$/L; lote e validade',
    f4[0] is True and 'Travada: item com 1.200 L no Estoque (1.200 L disponíveis)' in (f4[1] or '') and f4[2] == 'Galão' and f4[3] == '20' and 'R$/L' in (f4[4] or '') and f4[5] == 'Lote e validade', f4)
f5 = o.get('f5') or [None, None]
chk('5 Ureia sem saldo mas em plano: unidade travada pelo plano', f5[0] is True and 'Travada: usado no plano Milho safrinha' in (f5[1] or ''), f5)
chk('6 Calcário (granel): sem campo de conteúdo; preço sem data é barrado junto ao campo', 'Conteúdo da embalagem' not in (o.get('l6') or []) and 'Informe a data do preço.' in (o.get('a6') or ''), [o.get('l6'), o.get('a6')])
chk('7 preço salvo com data e a pendência some do cabeçalho', 'R$ 480,00/t' in (o.get('r7') or '') and '20/09/2026' in (o.get('r7') or '') and o.get('e7') == 'Cadastro completo', [o.get('r7'), o.get('e7')])
chk('8 embalagem não granel pede o conteúdo na unidade-base (t)', 'Conteúdo da embalagem' in (o.get('l8') or []) and 'Informe quanto cabe em 1 big bag (em t).' in (o.get('a8') or ''), [o.get('l8'), o.get('a8')])
chk('9 inativar item em plano: aviso de que sai dos planos e das cotações; sai de "Todos" e aparece em "Inativos" com o chip (R08)',
    'sai dos planos e das cotações' in (o.get('t9') or '') and o.get('r9') is None and (o.get('qf9') or '').startswith('Inativos') and 'Inativo' in (o.get('r9b') or ''), [o.get('t9'), o.get('r9'), o.get('qf9'), o.get('r9b')])
chk('10 "Outro grupo…" cria Biológicos (natureza 3.1.02) com o item Trichoderma WP',
    o.get('g10') == '' and 'Nome do novo grupo' in (o.get('l10') or []) and 'Natureza de custo' in (o.get('l10') or []) and any(m.startswith('Biológicos · 1') for m in o.get('m10', []))
    and '3.1.02 · Defensivos' in (o.get('dx10') or '') and 'kg' in (o.get('r10') or '') and 'saco de 1 kg' in (o.get('r10') or ''), [o.get('g10'), o.get('l10'), o.get('m10'), o.get('dx10'), o.get('r10'), o.get('a10')])
chk('11 item repetido é barrado', 'Já existe o item MAP 11-52 em Fertilizantes.' in (o.get('a11') or ''), o.get('a11'))
lc = o.get('lc') or []
chk('12 locais: fazenda na tabela, sem coluna Controle; capacidade só no tanque e no silo (do ativo)',
    'Fazenda' in lc and 'Controle' not in lc and '15.000 L' in (o.get('tq') or '') and '60.000 sc' in (o.get('si') or '') and '—' in (o.get('g1') or ''), [lc, o.get('tq'), o.get('si'), o.get('g1')])
chk('13 "+ Criar local" é a primária com "Locais de estoque" escolhido (sem "+ Novo local")', o.get('crt13') == [True, '+ Criar local'] and not o.get('novo13') and o.get('ti13') == 'Criar local', [o.get('crt13'), o.get('ti13')])
chk('14 local novo na Boa Vista', 'Boa Vista' in (o.get('r14') or ''), [o.get('r14'), o.get('t14')])
chk('15 nenhum erro de JS na jornada', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
