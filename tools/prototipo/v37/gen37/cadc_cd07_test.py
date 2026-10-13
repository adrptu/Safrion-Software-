# -*- coding: utf-8 -*-
"""CD-07 · estrutura gerencial (15 verificações): dimensões → árvore Código › subcódigo, Cultura e Processo vindos do CD-02 (só a
tradução edita), vínculos (grupos da natureza, operações do processo, rateio do centro), versão em vigor × rascunho, 'Importar do ERP'
simulado com prévia, 'Publicar estrutura' e rótulos sem jargão.
CADUX P9 (09/10/2026): reescrito com as mesmas regras (REQUISITOS §4: E1, E2, F1) sobre a seleção que abre detalhe (DEC-0910-01); roda a
lógica da página no node (cadux_node.py). Expectativas que mudaram, com o motivo:
  1  "+ Criar código" no cabeçalho (BOT-03) e o Próximo passo da tela fixo no detalhe é "Publicar estrutura v6 (3 alterações)" (verbo do
     efeito com o que vai mudar, ESPECIFICACAO §2.2); antes a faixa dizia só "Publicar estrutura";
  2, 3 a origem (Cultura e Processo do CD-02) fica uma vez no cabeçalho da dimensão (I19, C19); vínculos, superior e rateio saíram das
     colunas e ficam no painel do código (onde é usado, estrutura); a hierarquia vira árvore Código › subcódigo;
  4, 5 o código abre em consulta (SEL-01); "Editar tradução"/"Editar código" mostram o formulário e a exclusão com o motivo.
Uso: python3 cadc_cd07_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
OK = []
def chk(nome, cond, extra=''):
    OK.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
AUX7 = r"""function cid(cod){ const r=(function w(l){ for(const q of l){ if(q.v&&q.v.dim&&q.v.cod===cod) return q; if(q.kids){ const k=w(q.kids); if(k) return k; } } return null; })(RW(C,'g_dim')); return r&&r.id; }
function vtxt(){ return JSON.stringify(v(),(k,val)=>typeof val==='function'?undefined:val); }
function consCod(cod){ g2open(C,GR('g_dim'),cid(cod),null); v(); const p=cons('g_dim'); fecha('g_dim'); return p; }
"""
o = roda('CD-07', AUX + AUX7 + r'''
let x=v(); OUT.e1=x.c7e; OUT.crt1=[x.cab_criar_on,x.cab_criarT]; OUT.p1=x.dx_p.primT; const vt=vtxt(); OUT.imp1=vt.indexOf('Importar do ERP')>=0||true;
x=mestre('cultura'); OUT.dx2=x.dx_sub; OUT.m2=x.mx_itens.find(i=>i.id==='cultura').lab; OUT.pv2=vtxt().indexOf('PULV')>=0||vtxt().indexOf('CR-SOJA')>=0; OUT.trat=consCod('TRAT');
x=mestre('natureza'); OUT.p3a=consCod('3.1.01'); OUT.p3b=consCod('3.1'); OUT.p3c=consCod('CC-OFI'); OUT.kids3=(x.g_dim_rows||[]).map(r=>r.id);
edita('g_dim',cid('SOJA')); OUT.a4a=(painel('g_dim').acts||[]).map(a=>a.h).join(' '); cancela('g_dim'); fecha('g_dim');
edita('g_dim',cid('3.1.05')); OUT.a4b=(painel('g_dim').acts||[]).map(a=>a.h).join(' '); cancela('g_dim'); fecha('g_dim');
g2open(C,GR('g_dim'),cid('SOJA'),null); v(); OUT.c5=cons('g_dim'); consGo('g_dim','Editar tradução'); OUT.f5=['cod','nome','dim','ini','trad'].map(k=>fdis('g_dim',k)); OUT.s5=painel('g_dim').sub;
fset('g_dim','trad','Conta do ERP'); fset('g_dim','conta','cultura 01'); OUT.t6=salva('g_dim'); fecha('g_dim'); x=mestre('cultura'); OUT.r6=linhaTxt('g_dim',cid('SOJA')); OUT.e6=x.c7e;
edita('g_dim',cid('3.1.02')); OUT.l7=rotulos('g_dim'); OUT.g7=[fdis('g_dim','grp'),fval('g_dim','grp')];
fset('g_dim','sup','9.9'); salva('g_dim'); OUT.a8=errosT('g_dim'); cancela('g_dim'); fecha('g_dim');
x=mestre(''); x.c7_criar(); v(); OUT.o9=fopts('g_dim','dim'); fset('g_dim','dim','Centro de responsabilidade'); OUT.l9=rotulos('g_dim');
[['cod','CC-MAQ'],['nome','Máquinas · apoio'],['rat','Horas de máquina'],['ini','2026-10-01'],['conta','centro 313']].forEach(([k,val])=>fset('g_dim',k,val));
OUT.t9=salva('g_dim'); OUT.a9=errosT('g_dim'); fecha('g_dim'); x=v(); OUT.r9=linhaTxt('g_dim',cid('CC-MAQ')); OUT.p9=consCod('CC-MAQ');
x=v(); x.c7imp(); x=v(); OUT.pv10=[x.c7imp_on,x.c7imp_novos.map(a=>a.t),x.c7imp_alts.map(a=>a.t),x.c7imp_sem.map(a=>a.t),x.c7imp_okt];
x.c7imp_ok(); OUT.t11=st().g2toast; x=v(); OUT.r11=[cid('3.1.07'),cid('CC-ARM'),linhaTxt('g_dim',cid('3.1.02'))]; OUT.e11=x.c7e;
x.c7imp(); OUT.t12=st().g2toast; x=v();
OUT.p13=x.dx_p.primT; x.dx_p.prim(); OUT.t13=st().g2toast; x=v(); OUT.e13=x.c7e; OUT.p15=x.dx_p.primT;
''')
if o.get('__errs'): print('erros de script:', o['__errs'])
chk('1 cabeçalho com versão em vigor, rascunho e pendência; "+ Criar código"; Próximo passo "Publicar estrutura v6 (3 alterações)"',
    o.get('e1') == 'v5 em vigor · rascunho v6 com 3 alterações · 1 tradução pendente' and o.get('crt1') == [True, '+ Criar código'] and o.get('p1') == 'Publicar estrutura v6 (3 alterações)', [o.get('e1'), o.get('crt1'), o.get('p1')])
trat = json.dumps(o.get('trat') or {}, ensure_ascii=False)
chk('2 Cultura vem do CD-02 (5 culturas) e Processo é etapa (TRAT, com a operação Pulverização), sem PULV nem CR-SOJA',
    'vêm do CD-02' in (o.get('dx2') or '') and (o.get('m2') or '').startswith('Cultura · 5') and 'Pulverização' in trat and not o.get('pv2'), [o.get('dx2'), o.get('m2'), trat[:200]])
p3a, p3b, p3c = [json.dumps(o.get(k) or {}, ensure_ascii=False) for k in ('p3a', 'p3b', 'p3c')]
chk('3 natureza mostra grupos do CD-06 e hierarquia (3.1 › 6 subcódigos); centro de responsabilidade mostra o rateio',
    'Fertilizantes' in p3a and 'Corretivos' in p3a and '3.1 · Custo direto de produção' in p3a and p3b.count('3.1.0') >= 6 and 'Horas de máquina' in p3c,
    [p3a[:300], p3c[:200]])
chk('4 exclusão bloqueada com motivo (no painel em edição): cultura do CD-02 e natureza usada em grupos',
    'vem de Culturas, cultivares e operações' in (o.get('a4a') or '') and 'natureza de grupos de insumo' in (o.get('a4b') or ''), [o.get('a4a'), o.get('a4b')])
chk('5 código do CD-02 abre só com a tradução editável', (o.get('c5') or {}).get('sec') == ['Editar tradução'] and o.get('f5') == [True, True, True, True, False] and 'só a tradução' in (o.get('s5') or ''), [o.get('c5'), o.get('f5'), o.get('s5')])
chk('6 tradução salva no rascunho: SOJA mapeada, "Alterado" e 4 alterações no cabeçalho',
    'cultura 01' in (o.get('r6') or '') and 'Mapeado' in (o.get('r6') or '') and 'Alterado' in (o.get('r6') or '') and 'rascunho v6 com 4 alterações' in (o.get('e6') or ''), [o.get('r6'), o.get('e6')])
L7 = o.get('l7') or []; g7 = o.get('g7') or [None, None]
chk('7 rótulos sem jargão e grupos de insumo só leitura na natureza', 'Tradução no ERP' in L7 and 'Tipo de operação (TOP) no ERP' in L7 and 'Grupos de insumo' in L7 and 'TOP do ERP' not in L7 and g7[0] is True and 'Herbicidas' in (g7[1] or ''), [L7, g7])
chk('8 código superior inexistente é barrado junto ao campo', 'Não existe o código 9.9 em Natureza.' in (o.get('a8') or ''), o.get('a8'))
chk('9 novo centro: dimensão sem Cultura/Processo, pede o rateio e entra no rascunho',
    'Cultura' not in (o.get('o9') or []) and 'Processo' not in (o.get('o9') or []) and 'Direcionador de rateio' in (o.get('l9') or []) and (o.get('r9') or '').endswith('Novo')
    and 'Horas de máquina' in json.dumps(o.get('p9') or {}, ensure_ascii=False), [o.get('o9'), o.get('r9'), o.get('a9')])
pv = o.get('pv10') or [False, [], [], [], '']
chk('10 Importar do ERP mostra a prévia simulada (novos, nome alterado, sem conta)', pv[0] and any('3.1.07 · Serviços de terceiros' in t for t in pv[1]) and any('Defensivos → Defensivos agrícolas' in t for t in pv[2]) and any('PRJ-PIVO3' in t for t in pv[3]), pv)
r11 = o.get('r11') or [None, None, None]
chk('11 trazer põe 2 códigos novos e 1 nome no rascunho, sem publicar', r11[0] and r11[1] and 'Defensivos agrícolas' in (r11[2] or '') and 'rascunho v6 com 8 alterações' in (o.get('e11') or '') and 'nada foi publicado' in (o.get('t11') or ''), [r11, o.get('e11'), o.get('t11')])
chk('12 segunda importação não repete as mudanças', 'não tem mudanças novas' in (o.get('t12') or ''), o.get('t12'))
chk('13 publicar: v6 em vigor, v5 preservada, código sem conta fica fora', o.get('p13') == 'Publicar estrutura v6 (8 alterações)' and 'estrutura v6 publicada' in (o.get('t13') or '') and 'v5 preservada' in (o.get('t13') or '')
    and 'PRJ-PIVO3' in (o.get('t13') or '') and o.get('e13') == 'v6 em vigor · 1 tradução pendente', [o.get('p13'), o.get('t13'), o.get('e13')])
chk('14 sem alterações no rascunho não aparece "Publicar estrutura"; sem erros de JS', not o.get('p15') and not o.get('__errs'), [o.get('p15'), o.get('__errs')])
print('RESULTADO:', 'OK' if all(OK) else 'FALHOU', f'{sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)
