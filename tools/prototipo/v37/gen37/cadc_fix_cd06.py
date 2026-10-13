# -*- coding: utf-8 -*-
"""CD-06 · defeitos do verificador (12 verificações): item sem preço abre o campo vazio e salva sem preço (também a semente vinda do
CD-02); grupo renomeado continua sendo o da criação; selo 'Cadastro completo' na cor de concluído; Local padrão acompanha o cadastro de
locais (novo e renomeado); sem local válido a criação pede o local.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: C1, E2) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  6  o grupo se renomeia pela ficha ("Ver ficha do grupo" → "Editar grupo", C26); a criação herda o grupo do mestre (R03) e pede
     unidade, embalagem e local, que não vêm mais preenchidos (X01/R14); o aviso diz "Criado:" (BOT-03);
  3  a semente que vem do CD-02 pede a embalagem (tipo e conteúdo), que não nasce mais "Saco" (X01); continua sem pedir preço;
  10, 11 o item novo vem com Local padrão vazio (X01: antes "Galpão 2" escondido); o local é pedido no defensivo (NR-31, ESPECIFICACAO §1.6)
     e é opcional nos outros grupos;
  11 (folga no artboard) é layout: passou para o teste de navegador cadux_cd01_test.py.
Uso: python3 cadc_fix_cd06.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AMAR, VERDE = 'color:#8A5A00', 'color:#1E7A4C'
AUX6 = r"""function idDe(n){ const r=(function w(l){ for(const q of l){ if(q.v&&q.v.item===n) return q; if(q.kids){ const k=w(q.kids); if(k) return k; } } return null; })(RW(C,'g_itm')); return r&&r.id; }
function grp(n){ const g=RW(C,'g_grp').find(g=>g.v.nome===n); return g&&g.id; }
function loc(n){ const l=RW(C,'g_loc').find(l=>l.v.nome===n); return l&&l.id; }
function aberto(gid){ const F=painel(gid); return !!(F&&!F.cons); }
"""
o = roda('CD-06', AUX + AUX6 + r'''
let x=v(); OUT.e1=x.c6e; OUT.s1=x.c6e_stst;
edita('g_itm',idDe('Calcário dolomítico')); OUT.pv2=fval('g_itm','preco'); fset('g_itm','local','Galpão 2'); OUT.t2=salva('g_itm'); OUT.o2=aberto('g_itm'); fecha('g_itm'); OUT.r2=linhaTxt('g_itm',idDe('Calcário dolomítico'));
edita('g_itm',idDe('Semente de soja 64 Z')); OUT.pv3=fval('g_itm','preco'); salva('g_itm'); OUT.a3=errosT('g_itm');
fset('g_itm','emb','Saco'); fset('g_itm','cont','40'); fset('g_itm','preco','12,5'); fset('g_itm','pdata','2026-09-20'); salva('g_itm'); OUT.a4=errosT('g_itm'); OUT.o4=aberto('g_itm'); fecha('g_itm'); OUT.r4=linhaTxt('g_itm',idDe('Semente de soja 64 Z'));
edita('g_itm',idDe('Calcário dolomítico')); fset('g_itm','preco','480'); fset('g_itm','pdata','2026-09-20'); salva('g_itm'); fecha('g_itm'); x=v(); OUT.e5=x.c6e; OUT.s5=x.c6e_stst;
x=mestre(grp('Fertilizantes')); x.dx_ficha(); v(); consGo('g_grp','Editar grupo'); fset('g_grp','nome','Fertilizantes minerais'); salva('g_grp'); fecha('g_grp');
x=mestre(grp('Fertilizantes minerais')); x.c6_criar(); v(); OUT.g6=fval('g_itm','grupo'); OUT.ini6=['un','emb','local'].map(k=>fval('g_itm',k));
fset('g_itm','item','Sulfato de amônio'); fset('g_itm','un','kg'); fset('g_itm','emb','Saco'); fset('g_itm','cont','50'); fset('g_itm','local','Galpão 2'); OUT.t6=salva('g_itm'); OUT.o6=aberto('g_itm'); fecha('g_itm');
x=v(); OUT.m6=x.mx_itens.map(i=>i.lab);
x=mestre('locais'); x.c6_criar(); v(); fset('g_loc','nome','Galpão BV 2'); fset('g_loc','faz','Boa Vista'); salva('g_loc'); fecha('g_loc');
x=mestre(''); edita('g_itm',idDe('MAP 11-52')); OUT.ops7=fopts('g_itm','local'); cancela('g_itm'); fecha('g_itm');
x=mestre('locais'); OUT.n0=linhaTxt('g_loc',loc('Galpão 1')); const g1=loc('Galpão 1'); edita('g_loc',g1); fset('g_loc','nome','Galpão Norte'); salva('g_loc'); fecha('g_loc'); OUT.n1=linhaTxt('g_loc',g1);
edita('g_loc',g1); OUT.dn=(painel('g_loc').acts||[]).map(a=>a.h).join(' '); cancela('g_loc'); fecha('g_loc');
x=mestre(''); edita('g_itm',idDe('NPK 20-05-20')); OUT.lv9=fval('g_itm','local'); OUT.ops9=fopts('g_itm','local'); cancela('g_itm'); fecha('g_itm');
x.c6_criar(); v(); OUT.lv10=fval('g_itm','local'); fecha('g_itm');
const falhas=[]; ['KCl 60%','MAP 11-52','Nitrato de cálcio','Nitrato de potássio','Ureia 45%','Calcário dolomítico','Sulfato de amônio'].forEach(it=>{ const id=idDe(it); if(!id){ falhas.push(it+': sem item'); return; } edita('g_itm',id); fset('g_itm','local','Galpão Norte'); salva('g_itm'); if(aberto('g_itm')){ falhas.push(it+': '+errosT('g_itm')); cancela('g_itm'); } fecha('g_itm'); });
OUT.falhas=falhas; x=mestre('locais'); const g2=loc('Galpão 2'); edita('g_loc',g2); const a=painel('g_loc').acts||[]; OUT.del=a.map(q=>q.t+': '+q.h);
if(a[0]){ a[0].go(); v(); const b=painel('g_loc').acts||[]; if(b[0]&&/Confirmar/.test(b[0].t)){ b[0].go(); v(); } } fecha('g_loc'); OUT.g2x=!!loc('Galpão 2');
x=mestre(''); x.c6_criar(); v(); OUT.lv12=fval('g_itm','local'); OUT.o12=(fopts('g_itm','local')||[])[0]; fset('g_itm','grupo','Fungicidas'); fset('g_itm','item','Teste padrão'); fset('g_itm','un','L'); fset('g_itm','emb','Galão'); fset('g_itm','cont','5'); salva('g_itm'); OUT.a12=errosT('g_itm');
fset('g_itm','grupo','Fertilizantes minerais'); fset('g_itm','un','kg'); fset('g_itm','emb','Saco'); fset('g_itm','cont','1'); OUT.t12=salva('g_itm'); OUT.a12b=errosT('g_itm');
''', antes="localStorage.setItem('talhao-os-cadastros-v1',JSON.stringify({sementes:['Semente de soja 64 Z']}));")
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 abre com pendências no selo amarelo', o.get('e1') == '2 itens sem preço · 1 item sem embalagem' and AMAR in (o.get('s1') or ''), [o.get('e1'), o.get('s1')])
chk('2 Calcário: campo de preço abre vazio e o item salva sem preço, com Galpão 2', o.get('pv2') == '' and not o.get('o2') and 'sem preço de referência' in (o.get('t2') or '') and 'Sem preço' in (o.get('r2') or ''), [o.get('pv2'), o.get('t2'), o.get('r2')])
a3 = o.get('a3') or ''
chk('3 semente do CD-02: preço abre vazio; só a embalagem é pedida (sem padrão escondido, X01)', o.get('pv3') == '' and a3.startswith('emb:') and 'número' not in a3 and 'data do preço' not in a3, [o.get('pv3'), a3])
chk('4 semente salva com embalagem e preço', not o.get('o4') and 'R$ 12,50/kg' in (o.get('r4') or ''), [o.get('a4'), o.get('r4')])
chk('5 Cadastro completo no selo verde', o.get('e5') == 'Cadastro completo' and VERDE in (o.get('s5') or ''), [o.get('e5'), o.get('s5')])
chk('6 grupo renomeado: a criação herda Fertilizantes minerais (unidade, embalagem e local vazios) e o item é salvo nele',
    o.get('g6') == 'Fertilizantes minerais' and o.get('ini6') == ['', '', ''] and not o.get('o6') and 'Criado: Sulfato de amônio' in (o.get('t6') or '') and any(m.startswith('Fertilizantes minerais · 12') for m in o.get('m6', [])),
    [o.get('g6'), o.get('ini6'), o.get('t6'), o.get('m6')])
chk('7 local novo aparece em Local padrão do item', 'Galpão BV 2' in (o.get('ops7') or []), o.get('ops7'))
chk('8 renomear o local leva os itens junto e o local segue protegido contra exclusão (causa no painel)',
    (o.get('n0') or '').replace('Galpão 1', 'Galpão Norte') == o.get('n1') and 'tem itens com este local padrão' in (o.get('dn') or ''), [o.get('n0'), o.get('n1'), o.get('dn')])
chk('9 NPK 20-05-20 (em Galpão 1) passa a Galpão Norte e a lista não oferece mais Galpão 1', o.get('lv9') == 'Galpão Norte' and 'Galpão 1' not in (o.get('ops9') or []) and 'Galpão Norte' in (o.get('ops9') or []), [o.get('lv9'), o.get('ops9')])
chk('10 Local padrão do item novo vem vazio (sem padrão escondido, X01)', o.get('lv10') == '', o.get('lv10'))
chk('11 Galpão 2 esvaziado e excluído: a lista do item novo mostra "Escolha…"; defensivo pede o local (NR-31) e o item comum salva sem local',
    not o.get('falhas') and not o.get('g2x') and o.get('lv12') == '' and o.get('o12') == 'Escolha…' and 'local: Defensivo pede o local padrão' in (o.get('a12') or '')
    and not o.get('a12b') and 'Criado: Teste padrão' in (o.get('t12') or ''), [o.get('falhas'), o.get('del'), o.get('g2x'), o.get('lv12'), o.get('a12'), o.get('a12b'), o.get('t12')])
chk('12 nenhum erro de JS', not o.get('__errs'), o.get('__errs'))
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
