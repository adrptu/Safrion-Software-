# -*- coding: utf-8 -*-
"""Teste do CD-01 (Fazendas, áreas e talhões): cadastrar fazenda nova com validação, cadastrar talhão na nova fazenda,
"+ Criar fazenda…" a partir do talhão sem perder o preenchido, subtotal por fazenda, inativar e abrir o detalhe de outro talhão.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: B1, B5, B6, E2) sobre a seleção que abre detalhe
(DEC-0910-01, SEL-01): roda a lógica da página no node (cadux_node.py), sem navegador; o fluxo na tela é do cadux_cd01_test.py.
Expectativas que mudaram, com o motivo:
  5  a fazenda nova vira a seleção do mestre e o detalhe vazio diz o próximo passo; "+ Criar talhão" só no cabeçalho (R04, BOT-07: antes
     havia um 2º "Cadastrar talhão" dentro da linha do grupo);
  12 o B1 inativo sai de "Todos" e aparece no filtro "Inativos"; a área da fazenda passa a 0 ha (R08; antes ficava na lista com o chip);
  13 a fazenda se inativa pela ficha ("Ver ficha da fazenda" → "Editar fazenda"), não pelo cartão (as abas Fazendas saíram, C10), e sai do
     mestre até ligar "Inativas" (R08);
  14 o detalhe do talhão abre pelo link do painel em consulta, não pelo botão do formulário.
Uso: python3 cadf_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:300] if extra and not cond else ''))
LINHAS = r"""function todas(){ return (v().g_tal_rows||[]).map(r=>r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | ')); }
"""
o = roda('CD-01', AUX + LINHAS + r'''
let x=v(); OUT.sr=linhaTxt('g_tal','F_SR'); OUT.bv=linhaTxt('g_tal','F_BV'); OUT.tot=todas().some(t=>/2\.570|Total/.test(t));
// ---------- fazenda nova com validação ----------
x.cd_nfaz(); v(); salva('g_faz'); OUT.e2=errosT('g_faz');
fset('g_faz','nome','Nova Esperança'); fset('g_faz','mun','Lucas do Rio Verde'); fset('g_faz','uf','MT'); OUT.fuso=fval('g_faz','fuso');
fset('g_faz','area','600'); fset('g_faz','posse','Arrendada'); OUT.l4=rotulos('g_faz'); salva('g_faz'); OUT.e4=errosT('g_faz'); OUT.nome4=fval('g_faz','nome');
fset('g_faz','arrend','José Prado'); fset('g_faz','fim','2030-06-30'); fset('g_faz','custo','9'); OUT.t5=salva('g_faz');
x=v(); OUT.p5=!!painel('g_faz'); OUT.dx5=x.dx_t; OUT.vz5=x.cd_vt_t; OUT.m5=x.mx_itens.map(i=>i.lab); OUT.cab5=[x.cab_criar_on,x.cab_criarT];
// ---------- talhão na fazenda nova ----------
x.cd_criar(); v(); OUT.faz6=fval('g_tal','faz');
fset('g_tal','t','N1'); fset('g_tal','sis','Pivô central'); fset('g_tal','setor','Bomba do Pivô 1'); fset('g_tal','decl','700'); salva('g_tal'); OUT.e7=errosT('g_tal');
fset('g_tal','sis','Sequeiro'); fset('g_tal','decl','250'); OUT.t8=salva('g_tal'); fecha('g_tal'); x=mestre('');
OUT.ne=todas().find(t=>t.indexOf('Nova Esperança')===0); OUT.sr8=linhaTxt('g_tal','F_SR');
// ---------- "+ Criar fazenda…" a partir do talhão ----------
x.cd_criar(); v(); fset('g_tal','t','X9'); fset('g_tal','decl','50'); fset('g_tal','faz','+ Criar fazenda…');
const F9=painel('g_faz'); OUT.sub9=F9&&F9.sub; fset('g_faz','nome','Serra Azul'); fset('g_faz','mun','Jataí'); fset('g_faz','area','100'); salva('g_faz');
OUT.v9=[fval('g_tal','t'),fval('g_tal','decl'),fval('g_tal','faz')]; OUT.t10=salva('g_tal'); fecha('g_tal'); x=mestre('');
OUT.sa=todas().find(t=>t.indexOf('Serra Azul')===0);
// ---------- inativar sem excluir ----------
edita('g_tal','T1'); fset('g_tal','sit','Inativo'); salva('g_tal'); OUT.e11=errosT('g_tal'); cancela('g_tal'); fecha('g_tal');
edita('g_tal','B1'); fset('g_tal','sit','Inativo'); OUT.t12=salva('g_tal'); fecha('g_tal'); x=mestre('BV');
OUT.b1=linhaTxt('g_tal','B1'); OUT.qf12=(x.g_tal_cqf||[]).map(c=>c.t+' '+c.n); OUT.bv12=x.dx_sub; OUT.mbv=x.mx_itens.find(i=>i.id==='BV').lab;
x=mestre('BV'); x.dx_ficha(); v(); OUT.ficha=cons('g_faz'); consGo('g_faz','Editar fazenda'); fset('g_faz','sit','Inativa'); OUT.t13=salva('g_faz'); fecha('g_faz');
x=v(); OUT.m13=x.mx_itens.map(i=>i.lab); OUT.chip13=x.dx_chT; OUT.inat13=x.mx_inatT; x.mx_inat(); x=v(); OUT.m13b=x.mx_itens.map(i=>i.lab);
// ---------- detalhe de outro talhão ----------
x=mestre('SR'); abre('g_tal','T2'); OUT.p14=cons('g_tal');
OUT.ls=ls();
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 CD-01 sem erro, subtotal por fazenda e nenhum total somando fazendas',
    not o.get('__errs') and '1.165,0 ha' in (o.get('sr') or '') and '120,0 ha' in (o.get('bv') or '') and not o.get('tot'), [o.get('sr'), o.get('bv')])
e2 = o.get('e2') or ''
chk('2 fazenda vazia: erros junto aos campos', 'Informe nome da fazenda.' in e2 and 'Informe município.' in e2 and 'Informe área total do imóvel.' in e2, e2)
chk('3 fuso sugerido pela UF (MT → Cuiabá)', o.get('fuso') == 'América/Cuiabá (UTC−4)', o.get('fuso'))
L4, e4 = o.get('l4') or [], o.get('e4') or ''
chk('4 arrendada pede arrendador, fim do contrato e custo da terra', all(x in L4 for x in ['Arrendador ou parceiro', 'Fim do contrato', 'Custo da terra'])
    and 'Informe o arrendador ou parceiro.' in e4 and 'Informe o fim do contrato.' in e4 and o.get('nome4') == 'Nova Esperança', [L4, e4])
chk('5 fazenda salva: escolhida no mestre, detalhe vazio com o próximo passo e "+ Criar talhão" só no cabeçalho',
    not o.get('p5') and o.get('dx5') == 'Nova Esperança' and 'Crie o 1º em + Criar talhão' in (o.get('vz5') or '') and any(m.startswith('Nova Esperança · 0') for m in o.get('m5', []))
    and o.get('cab5') == [True, '+ Criar talhão'], [o.get('t5'), o.get('dx5'), o.get('vz5'), o.get('m5')])
chk('6 talhão nasce na fazenda escolhida', o.get('faz6') == 'Nova Esperança', o.get('faz6'))
e7 = o.get('e7') or ''
chk('7 regras do talhão: pivô já usado e área acima da fazenda', 'Bomba do Pivô 1 já irriga o P1' in e7 and 'somariam 700 ha; a fazenda tem 600 ha' in e7, e7)
chk('8 talhão salvo na nova fazenda com subtotal próprio (Santa Rita não muda)', '250,0 ha' in (o.get('ne') or '') and '1.165,0 ha' in (o.get('sr8') or ''), [o.get('ne'), o.get('t8')])
chk('9 volta ao talhão com a fazenda nova escolhida e o preenchido mantido', 'Ao salvar, você volta ao talhão X9' in (o.get('sub9') or '') and o.get('v9') == ['X9', '50', 'Serra Azul'], [o.get('sub9'), o.get('v9')])
chk('10 talhão X9 salvo na Serra Azul', '50,0 ha' in (o.get('sa') or ''), [o.get('sa'), o.get('t10')])
chk('11 T1 com parcelas na safra não inativa', 'T1 tem parcelas na Safra 2026/27 e na Safrinha 2027' in (o.get('e11') or ''), o.get('e11'))
chk('12 B1 inativo: sai de "Todos", aparece no filtro "Inativos" e sai do subtotal (R08)', o.get('b1') is None and 'Inativos 1' in (o.get('qf12') or [])
    and '0,0 ha cultivável · 0 talhões' in (o.get('bv12') or '') and (o.get('mbv') or '').startswith('Boa Vista · 0'), [o.get('t12'), o.get('b1'), o.get('qf12'), o.get('bv12'), o.get('mbv')])
chk('13 fazenda sem talhão ativo inativa sem excluir (pela ficha): sai do mestre e volta com "Inativas"', o.get('ficha') and o.get('chip13') == 'Inativa'
    and not any(m.startswith('Boa Vista') for m in o.get('m13', [])) and o.get('inat13') == 'Inativas · 1' and any(m.startswith('Boa Vista') for m in o.get('m13b', [])),
    [o.get('t13'), o.get('m13'), o.get('chip13'), o.get('inat13'), o.get('m13b')])
p14 = o.get('p14') or {}
chk('14 o painel do T2 em consulta leva ao detalhe do T2 (CD-01det#talhao=T2)', p14.get('t') == 'Talhão · T2' and 'CD-01det.dc.html#talhao=T2' in json.dumps(p14, ensure_ascii=False), p14)
# 15: o detalhe lê o cadastro salvo pela lista (mesmo armazenamento do navegador)
d = roda('CD-01det', AUX + r'''let x=v(); OUT.cab=JSON.stringify([x.det_sub,x.det_chT,x.dx_t,x.c1d_e,x.cdd_e]); OUT.ficha=(x.g_idt_rows||[]).map(r=>r.cells.filter(c=>c.isData).map(c=>c.parts.map(p=>p.t).join(' ')).join(' | ')).join(' || ');''',
         hash='#talhao=B1', antes='(function(){ const o=' + (o.get('ls') or '{}') + '; for(const k in o) localStorage.setItem(k,o[k]); })();')
txt = (d.get('cab') or '') + (d.get('ficha') or '')
chk('15 detalhe lê o cadastro salvo na lista: B1 inativo', 'Inativo' in txt and not d.get('__errs'), [d.get('cab'), (d.get('ficha') or '')[:200], d.get('__errs')])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
