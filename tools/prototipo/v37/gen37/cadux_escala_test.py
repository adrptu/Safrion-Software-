# -*- coding: utf-8 -*-
"""CADUX · R17 / AC-26 (escala): com 300 itens no CD-06 (Fungicidas) e 40 talhões numa fazenda do CD-01 (Boa Vista), gerados só aqui
e nunca no cenário, o mestre, a grade, a busca, o "N de M", o "‹ ›" do painel e o painel funcionam sem erro de script.
Roda a lógica das páginas no node (cadux_node.py), com o mesmo runtime das telas (estado na hora, desenho em lote).
Uso: python3 cadux_escala_test.py  (lê project/; sai com 1 se alguma regra falhar)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
from cadux_node import roda, AUX
ok = []
def chk(nome, cond, extra=''):
    ok.append(bool(cond)); print(('OK  ' if cond else 'FALHOU ') + nome + (' · ' + str(extra)[:400] if extra and not cond else ''), flush=True)
# itens e talhões sintéticos, clonados de um registro do cenário (só nesta execução)
GERA = r"""function clona(o){ return JSON.parse(JSON.stringify(o)); }
function gera(gid,gidGrupo,base,n,nome,campo){ const g=GR(gid).rows.find(x=>x.id===gidGrupo); const b=g.kids.find(k=>k.id===base);
  for(let i=1;g.kids.length<n;i++){ const k=clona(b); k.id=base+'_e'+i; k.v[campo]=nome(i); k.s[campo]=nome(i); if(k.p&&k.p[campo]) k.p[campo]=[{k:'b',t:nome(i)}]; g.kids.push(k); } return g.kids.length; }
function folhas(gid){ return (v()[gid+'_rows']||[]).filter(r=>!/g2grp|grupo/.test(r.cls||'')&&r.cells.some(c=>c.isData)).length; }
function busca(q){ v().mx_setq({target:{value:q}}); return v(); }
"""
def parte(pag, gid, grupo, base, n, nome, campo, alvo, conta):
    """1440: grade, "N de M", busca que recorta a grade, painel e "‹ ›"; 390: a busca do mestre lista o registro e abre o painel."""
    larga = roda(pag, AUX + GERA + f"""
OUT.n=gera('{gid}','{grupo}','{base}',{n},{nome},'{campo}');
let x=mestre('{grupo[2:] if pag == 'CD-01' else grupo}'); const it=x.mx_itens.find(i=>i.id==='{grupo[2:] if pag == 'CD-01' else grupo}'); OUT.mn=it&&it.n; OUT.conta=x.{conta}; OUT.linhas=(x.{gid}_rows||[]).length;
x=busca('{alvo}'); OUT.lb=(x.{gid}_rows||[]).map(r=>r.cells.find(c=>c.isData).parts.map(p=>p.t).join(' ').trim()); OUT.contab=x.{conta}; x=busca('');
abre('{gid}','{base}_e20'); x=v(); let F=x.{gid}_F; OUT.p=F&&F.title; OUT.pos=F&&F.pos; if(F&&F.prox){{ F.prox(); __roda(); x=v(); OUT.p2=x.{gid}_F&&x.{gid}_F.title; OUT.pos2=x.{gid}_F&&x.{gid}_F.pos; }}
fecha('{gid}');""")
    est = roda(pag, AUX + GERA + f"""
gera('{gid}','{grupo}','{base}',{n},{nome},'{campo}');
let x=busca('{alvo}'); OUT.res=(x.mx_res||[]).map(r=>r.t); const r0=(x.mx_res||[]).find(r=>r.t.indexOf('{alvo}')===0); if(r0&&r0.go) r0.go(); __roda(); x=v(); OUT.p=x.{gid}_F&&x.{gid}_F.open?x.{gid}_F.title:null;""", larga=False)
    print(pag, json.dumps({'1440': {k: larga.get(k) for k in ('n', 'mn', 'conta', 'linhas', 'lb', 'contab', 'p', 'pos', 'p2', 'pos2')}, '390': {k: est.get(k) for k in ('res', 'p')}}, ensure_ascii=False)[:900])
    return larga, est

o, e = parte('CD-06', 'g_itm', 'GR6', 'i18', 300, "i=>'Fungicida E'+String(i).padStart(3,'0')", 'item', 'Fungicida E150', 'c6_conta')
chk('CD-06 com 300 fungicidas: sem erro de script (1440 e 390)', not o.get('__errs') and not e.get('__errs'), [o.get('__errs'), e.get('__errs')])
chk('CD-06: o mestre conta 300 em Fungicidas; a grade mostra as 300 linhas, sem paginar, e o "N de M" diz 300 de 300', o.get('n') == 300 and str(o.get('mn')) == '300' and (o.get('linhas') or 0) == 300 and o.get('conta') == '300 de 300', [o.get('mn'), o.get('linhas'), o.get('conta')])
chk('CD-06 1440: a busca do mestre recorta a grade no item 150 ("1 de 300")', o.get('lb') == ['Fungicida E150'] and o.get('contab') == '1 de 300', [o.get('lb'), o.get('contab')])
chk('CD-06: o painel abre em consulta e "‹ ›" percorre os 300 na ordem da grade ("n de 300")', str(o.get('pos') or '').endswith(' de 300') and str(o.get('pos2') or '').endswith(' de 300') and o.get('p2') and o.get('p2') != o.get('p'), [o.get('p'), o.get('pos'), o.get('p2'), o.get('pos2')])
chk('CD-06 390: a busca do mestre lista o item 150 e abre o painel dele', any(t.startswith('Fungicida E150') for t in (e.get('res') or [])) and 'Fungicida E150' in (e.get('p') or ''), [e.get('res'), e.get('p')])

o, e = parte('CD-01', 'g_tal', 'F_BV', 'B1', 40, "i=>'BX'+String(i).padStart(2,'0')", 't', 'BX20', 'cd_conta')
chk('CD-01 com 40 talhões na Boa Vista: sem erro de script (1440 e 390)', not o.get('__errs') and not e.get('__errs'), [o.get('__errs'), e.get('__errs')])
chk('CD-01: o mestre conta 40 na Boa Vista; a grade mostra os 40, sem paginar, e o "N de M" diz 40 de 40', o.get('n') == 40 and str(o.get('mn')) == '40' and (o.get('linhas') or 0) == 40 and o.get('conta') == '40 de 40', [o.get('mn'), o.get('linhas'), o.get('conta')])
chk('CD-01 1440: a busca do mestre recorta a grade no BX20 ("1 de 40")', o.get('lb') == ['BX20'] and o.get('contab') == '1 de 40', [o.get('lb'), o.get('contab')])
chk('CD-01: o painel abre em consulta e "‹ ›" percorre os 40 ("n de 40")', str(o.get('pos') or '').endswith(' de 40') and str(o.get('pos2') or '').endswith(' de 40') and o.get('p2') and o.get('p2') != o.get('p'), [o.get('p'), o.get('pos'), o.get('p2'), o.get('pos2')])
chk('CD-01 390: a busca do mestre lista o BX20 e abre o painel dele', any(t.startswith('BX20') for t in (e.get('res') or [])) and 'BX20' in (e.get('p') or ''), [e.get('res'), e.get('p')])
print('RESULTADO:', 'OK' if all(ok) else 'FALHOU', f'{sum(ok)}/{len(ok)}')
sys.exit(0 if all(ok) else 1)
