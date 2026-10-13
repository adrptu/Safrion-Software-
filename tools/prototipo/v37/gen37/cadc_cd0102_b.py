# -*- coding: utf-8 -*-
"""Parte CD-02 do cd0102test.py (2/2: salvar, modo Informado e mesmos campos no Planejar safra), com os mesmos valores esperados. 11 verificações.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: C5; O17 do Planejar safra) sobre a seleção que abre detalhe
(DEC-0910-01); roda a lógica das páginas no node (cadux_node.py). Expectativas que mudaram, com o motivo (X-CAD-1 da NAV):
  1, 2 a largura e o R$/h do conjunto vindo do CD-03 são só leitura no CD-02; a largura mínima é conferida num rendimento com
     "Outro (descrever)", o conjunto escrito à mão (sem vínculo), onde a largura continua digitada;
  4, 5 o R$/h novo do Trator 02 vem do CD-03 (200 em vez de 180), não do campo Máquina; as contas e os valores esperados são os mesmos;
  9-11 o Planejar safra é lido pela grade de rendimentos da safra aberta (g_rend_S2627), sem navegar pelas etapas.
Uso: python3 cadc_cd0102_b.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AJ = ["Largura × velocidade ÷ 10 × eficiência.", "Máquina + implemento + pessoas × custo por pessoa.", "Inclua combustível, manutenção e depreciação; o operador entra em Pessoas."]
o = roda('CD-02', AUX + r'''
let x=v(); x.c2t1_go(); x=mestre('OP1'); x.c2_criar(); v(); fset('g_rend','cjid','Outro (descrever)'); fset('g_rend','conj','Trator 05 + Pulverizador 2');
[['vel','10'],['efic','75'],['maq','100'],['pess','1'],['fonte','Medição local'],['vig','2027-06-30']].forEach(([k,val])=>fset('g_rend',k,val)); fset('g_rend','larg','0,2'); salva('g_rend'); OUT.a1=errosT('g_rend'); OUT.rc1=fval('g_rend','rend_c'); cancela('g_rend'); fecha('g_rend');
edita('g_rend','r1'); fset('g_rend','vel','10'); OUT.t4=salva('g_rend'); OUT.o3=!!(painel('g_rend')&&!painel('g_rend').cons); OUT.p5=JSON.stringify(cons('g_rend')); fecha('g_rend'); OUT.r5=linhaTxt('g_rend','r1');
x=mestre('OP2'); edita('g_rend','r2'); fset('g_rend','modo','Informado'); OUT.l6=rotulos('g_rend'); OUT.rd7=fval('g_rend','rend');
fset('g_rend','rend','7,5'); salva('g_rend'); OUT.p8=JSON.stringify(cons('g_rend')); fecha('g_rend'); OUT.r8=linhaTxt('g_rend','r2');
''', antes="localStorage.setItem('talhao-os-cadastros-v1',JSON.stringify({ativos:{a02:{nome:'Trator 02',custo_h:200}}}));")
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 largura abaixo do mínimo barrada', 'Mínimo 0,5 m' in (o.get('a1') or ''), o.get('a1'))
chk('2 rendimento ao vivo acompanha o digitado', o.get('rc1') == '0,15', o.get('rc1'))
chk('3 salvou e voltou à consulta', not o.get('o3'), o.get('o3'))
t4 = o.get('t4') or ''
chk('4 aviso de salvo com o novo rendimento', '27,00 ha/h' in t4 and 'R$ 333,00/h' in t4 and 'R$ 12,33/ha' in t4, t4)
p5 = o.get('p5') or ''
chk('5 linha e painel recalculados (27,00 ha/h · R$ 333,00 · R$ 12,33; 36 m × 10 km/h)', '27,00 ha/h' in (o.get('r5') or '') and 'R$ 333,00' in (o.get('r5') or '') and 'R$ 12,33/ha' in p5 and '36 m × 10 km/h ÷ 10 × 75 %' in p5, [o.get('r5'), p5[:300]])
L6 = o.get('l6') or []
chk('6 Informado esconde largura, velocidade e eficiência', 'Largura de trabalho' not in L6 and L6.count('Rendimento efetivo') == 1, L6)
chk('7 Informado parte do rendimento atual (6,8)', o.get('rd7') == '6,8', o.get('rd7'))
chk('8 linha em modo informado (7,50 ha/h · R$ 52,80/ha)', 'Informado' in (o.get('r8') or '') and '7,50 ha/h' in (o.get('r8') or '') and 'R$ 52,80/ha' in (o.get('p8') or ''), [o.get('r8'), (o.get('p8') or '')[:300]])
s = roda('SAF', AUX + r'''const g=GR('g_rend_S2627'); OUT.l=g.edit.fields.map(f=>f.l); OUT.h=g.edit.fields.map(f=>f.help||'').join(' ');
  const all=[]; (function w(l){ l.forEach(r=>{ all.push(r); if(r.kids) w(r.kids); }); })(g2rows(C,g)); const r=all.find(r=>/Trator 02/.test(r.v.nome||'')); if(r){ g2open(C,g,r.id,null); v(); OUT.rc=fval('g_rend_S2627','rend_c'); }''')
LC = ['Como obter o rendimento', 'Largura de trabalho', 'Velocidade de trabalho', 'Eficiência de campo', 'Rendimento efetivo', 'Rendimento efetivo', 'Máquina', 'Implemento', 'Pessoas na equipe', 'Custo por pessoa', 'Custo por hora']
ls = s.get('l') or []
sub = any(ls[i:i + len(LC)] == LC for i in range(len(ls)))
chk('9 Planejar safra usa os mesmos campos do rendimento (fora os próprios de cada tela)', sub and not s.get('__errs'), [ls, s.get('__errs')])
chk('10 Planejar safra tem as mesmas ajudas', all(a in (s.get('h') or '') for a in AJ), (s.get('h') or '')[:300])
chk('11 Planejar safra calcula o mesmo rendimento ao vivo (21,60)', s.get('rc') == '21,60', s.get('rc'))
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
