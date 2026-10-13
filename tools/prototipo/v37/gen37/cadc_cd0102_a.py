# -*- coding: utf-8 -*-
"""Parte CD-02 do cd0102test.py (1/2: lista e cálculo ao vivo), com os mesmos valores esperados. 12 verificações.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: C5) sobre a seleção que abre detalhe (DEC-0910-01); roda a lógica da
página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  2  (página sem rolagem lateral) é layout: passou para o teste de navegador cadux_cd01_test.py ("a página não rola", CD-01 a CD-07);
  3-5 a lista do rendimento tem as colunas da ESPECIFICACAO §2.2 (Conjunto | Situação | Cultura | Modo | Rendimento | Custo R$/h | Fonte);
     largura, velocidade, eficiência e custo R$/ha ficam no painel (bloco Rendimento e Custo), com a fórmula escrita;
  6, 7 o rendimento abre em consulta e "Editar rendimento" mostra o formulário; X-CAD-1 acrescenta "Conjunto ou equipe" (lista do
     CD-03/CD-04) e a "Descrição do conjunto ou da equipe" antes de Cultura; os campos do Planejar safra seguem iguais.
Uso: python3 cadc_cd0102_a.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
o = roda('CD-02', AUX + r'''
let x=v(); x.c2t1_go(); x=v(); OUT.cols=GR('g_rend').cols.map(c=>c.l); OUT.r1=linhaTxt('g_rend','r1');
const tsi=RW(C,'g_rend').map(g=>(g.kids||[])).flat().find(r=>/TSI/.test(r.v.conj||'')); OUT.r4=tsi&&linhaTxt('g_rend',tsi.id);
abre('g_rend','r1'); OUT.p1=JSON.stringify(cons('g_rend')); fecha('g_rend'); if(tsi){ abre('g_rend',tsi.id); OUT.p4=JSON.stringify(cons('g_rend')); fecha('g_rend'); }
edita('g_rend','r1'); OUT.l=rotulos('g_rend'); OUT.rc0=[fval('g_rend','rend_c'),fval('g_rend','custo_c')];
OUT.help=painel('g_rend').fields.map(f=>f.help||'').join(' ');
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 CD-02 sem erro JS', not o.get('__errs'), o.get('__errs'))
chk('2 colunas com uma variável cada (§2.2)', o.get('cols') == ['Operação › conjunto', 'Situação', 'Cultura', 'Modo', 'Rendimento', 'Custo R$/h', 'Fonte'], o.get('cols'))
p1 = o.get('p1') or ''
chk('3 painel mostra largura, velocidade e eficiência na fórmula (36 m × 8 km/h ÷ 10 × 75 %)', '36 m × 8 km/h ÷ 10 × 75 %' in p1, p1[:300])
chk('4 linha e painel mostram custo por hora e por hectare', 'R$ 313,00' in (o.get('r1') or '') and 'R$ 14,49/ha' in p1, [o.get('r1'), p1[:300]])
chk('5 rendimento informado sinalizado na coluna Modo (sem fórmula no painel)', 'Informado' in (o.get('r4') or '') and 'Fórmula' not in (o.get('p4') or ''), [o.get('r4'), (o.get('p4') or '')[:200]])
L = o.get('l') or []
chk('6 "Editar rendimento" abre o formulário', len(L) > 0, L)
chk('7 mesmos rótulos do Planejar safra (+ Conjunto ou equipe, Descrição e Cultura do cadastro)',
    L == ['Operação', 'Conjunto ou equipe', 'Descrição do conjunto ou da equipe', 'Cultura', 'Como obter o rendimento', 'Largura de trabalho', 'Velocidade de trabalho', 'Eficiência de campo',
          'Rendimento efetivo', 'Máquina', 'Implemento', 'Pessoas na equipe', 'Custo por pessoa', 'Custo por hora', 'Fonte do dado', 'Vigente até'], L)
chk('8 rendimento ao vivo inicial = 21,60', (o.get('rc0') or [None])[0] == '21,60', o.get('rc0'))
chk('9 custo/h ao vivo inicial = 313,00', (o.get('rc0') or [None, None])[1] == '313,00', o.get('rc0'))
# 10, 11: cálculo ao vivo. O conjunto do r1 vem do CD-03 (X-CAD-1): a máquina é só leitura, então o custo/h ao vivo é conferido com o
# R$/h do Trator 02 alterado no CD-03 (200), como a pessoa faria
o2 = roda('CD-02', AUX + r'''let x=v(); x.c2t1_go(); v(); edita('g_rend','r1'); fset('g_rend','vel','10'); OUT.rc=fval('g_rend','rend_c'); OUT.cc=fval('g_rend','custo_c'); OUT.md=fdis('g_rend','maq');''',
          antes="localStorage.setItem('talhao-os-cadastros-v1',JSON.stringify({ativos:{a02:{nome:'Trator 02',custo_h:200}}}));")
chk('10 L × V ÷ 10 × E ao vivo: 36 × 10 ÷ 10 × 75% = 27,00', o2.get('rc') == '27,00', o2.get('rc'))
chk('11 custo/h ao vivo com o R$/h do CD-03: 200 + 95 + 1 × 38 = 333,00 (máquina só leitura, X-CAD-1)', o2.get('cc') == '333,00' and o2.get('md') is True, [o2.get('cc'), o2.get('md')])
AJ = ["Largura × velocidade ÷ 10 × eficiência.", "Máquina + implemento + pessoas × custo por pessoa."]
chk('12 ajudas das fórmulas e da composição visíveis', all(a in (o.get('help') or '') for a in AJ), (o.get('help') or '')[:300])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
