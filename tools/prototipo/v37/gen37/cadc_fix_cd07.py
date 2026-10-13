# -*- coding: utf-8 -*-
"""CD-07 · defeitos do verificador (11 verificações): excluir um código entra no rascunho e só sai na publicação; excluir um código novo do
rascunho só o tira do rascunho; 'Importar do ERP' não duplica código que já está na dimensão; selo na cor de concluído quando não há
rascunho nem pendência.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: E1, E2) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  1, 5 publicar é o Próximo passo da tela no detalhe ("Publicar estrutura v6 (3 alterações)", ESPECIFICACAO §2.2), não a faixa;
  2, 7 excluir fica no formulário de edição ("Editar código" → "Excluir código" → "Confirmar exclusão"), com a causa à vista;
  3, 4 o código excluído abre em consulta (SEL-01) sem "Editar" nem "Excluir", dizendo quando sai;
  8  "+ Criar código" no cabeçalho, com a dimensão escolhida (em "Todas" ela vem vazia, X01) e o superior escolhido da lista.
Uso: python3 cadc_fix_cd07.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AMAR, VERDE = 'color:#8A5A00', 'color:#1E7A4C'
AUX7 = r"""function cid(cod){ const r=(function w(l){ for(const q of l){ if(q.v&&q.v.dim&&q.v.cod===cod) return q; if(q.kids){ const k=w(q.kids); if(k) return k; } } return null; })(RW(C,'g_dim')); return r&&r.id; }
function ncod(cod){ let n=0; (function w(l){ l.forEach(q=>{ if(q.v&&q.v.dim&&q.v.cod===cod) n++; if(q.kids) w(q.kids); }); })(RW(C,'g_dim')); return n; }
function excluir(cod){ edita('g_dim',cid(cod)); const a=(painel('g_dim').acts||[])[0]; if(!a) return 'sem ação'; a.go(); v(); const b=(painel('g_dim').acts||[])[0]; if(!b||!/Confirmar/.test(b.t)) return 'sem confirmação'; b.go(); const t=st().g2toast; v(); return t; }
"""
o = roda('CD-07', AUX + AUX7 + r'''
let x=v(); x.dx_p.prim(); x=v(); OUT.e1=x.c7e; OUT.s1=x.c7e_stst;
OUT.t2=excluir('PRJ-PIVO3'); fecha('g_dim'); x=v(); OUT.e2=x.c7e; OUT.r2=linhaTxt('g_dim',cid('PRJ-PIVO3'));
g2open(C,GR('g_dim'),cid('PRJ-PIVO3'),null); v(); OUT.p3=cons('g_dim'); fecha('g_dim');
x=v(); OUT.prim5=x.dx_p.primT; x.dx_p.prim(); OUT.t5=st().g2toast; x=v(); OUT.e5=x.c7e; OUT.s5=x.c7e_stst; OUT.r5=cid('PRJ-PIVO3');
x=mestre('projeto'); x.c7_criar(); v(); [['cod','PRJ-X'],['nome','Teste'],['ini','2026-10-01'],['conta','proj 9']].forEach(([k,val])=>fset('g_dim',k,val)); salva('g_dim'); fecha('g_dim'); x=v(); OUT.h7=x.c7e;
OUT.t7=excluir('PRJ-X'); fecha('g_dim'); x=v(); OUT.e7=x.c7e; OUT.r7=cid('PRJ-X');
''')
o2 = roda('CD-07', AUX + AUX7 + r'''
let x=v(); x.c7_criar(); v(); fset('g_dim','dim','Natureza'); [['cod','3.1.07'],['nome','Serviços de terceiros'],['sup','3.1'],['ini','2026-07-01'],['conta','4.1.1.07']].forEach(([k,val])=>fset('g_dim',k,val)); salva('g_dim'); fecha('g_dim');
x=v(); x.c7imp(); x=v(); OUT.nov=x.c7imp_novos.map(a=>a.t); x.c7imp_ok(); x=v(); OUT.n=ncod('3.1.07'); OUT.arm=!!cid('CC-ARM');
x.c7imp(); OUT.t10=st().g2toast;
''')
if o.get('__errs') or o2.get('__errs'): print('erros de script:', o.get('__errs'), o2.get('__errs'))
chk('1 publicada a v6: selo amarelo pela tradução pendente', o.get('e1') == 'v6 em vigor · 1 tradução pendente' and AMAR in (o.get('s1') or ''), [o.get('e1'), o.get('s1')])
r2 = o.get('r2') or ''
chk('2 excluir PRJ-PIVO3 entra no rascunho v7 e o código continua visível até publicar (Situação "Sai na v7" | No rascunho "Excluído")',
    'rascunho v7 com 1 alteração' in (o.get('e2') or '') and 'Sai na v7' in r2 and r2.endswith('Excluído') and r2.count('Excluído') == 1 and 'rascunho v7' in (o.get('t2') or ''), [o.get('t2'), o.get('e2'), r2])
p3 = o.get('p3') or {}
chk('3 código marcado para exclusão não oferece "Editar" nem "Excluir" de novo (painel em consulta)', p3.get('sec') == [] and 'Excluir' not in json.dumps(p3, ensure_ascii=False), p3)
chk('4 código excluído abre só em consulta, dizendo quando sai', 'Excluído no rascunho v7' in (p3.get('prox') or ''), p3.get('prox'))
t5 = o.get('t5') or ''
chk('5 publicar a v7 tira o código excluído e preserva a v6', o.get('prim5') == 'Publicar estrutura v7 (1 alteração)' and 'estrutura v7 publicada' in t5 and '1 código excluído' in t5 and 'v6 preservada' in t5
    and not o.get('r5') and o.get('e5') == 'v7 em vigor', [o.get('prim5'), t5, o.get('e5'), o.get('r5')])
chk('6 sem rascunho e sem pendência: selo verde', VERDE in (o.get('s5') or ''), [o.get('e5'), o.get('s5')])
chk('7 código novo excluído sai do rascunho na hora', 'rascunho v8 com 1 alteração' in (o.get('h7') or '') and not o.get('r7') and 'rascunho' not in (o.get('e7') or ''), [o.get('h7'), o.get('t7'), o.get('e7')])
nov = o2.get('nov') or []
chk('8 prévia não lista como novo o 3.1.07 já cadastrado', not any('3.1.07' in t for t in nov) and any('CC-ARM' in t for t in nov), nov)
chk('9 importação mantém um só 3.1.07 na Natureza e traz o CC-ARM', o2.get('n') == 1 and o2.get('arm'), [o2.get('n'), o2.get('arm')])
chk('10 segunda importação não repete as mudanças', 'não tem mudanças novas' in (o2.get('t10') or ''), o2.get('t10'))
chk('11 nenhum erro de JS', not o.get('__errs') and not o2.get('__errs'), [o.get('__errs'), o2.get('__errs')])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
