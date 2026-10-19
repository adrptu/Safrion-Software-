# Verificador INDEPENDENTE (não usa repartir): viabilidade por cortes por prazo com início comum.
# Exclusão (nunca ao mesmo tempo): as duas com seq; ativo do cadastro em comum; ou as duas usam um grupo de recursos de 1 unidade.
# Viável: cada h ≤ janela própria (vazio = sem limite; 0 = nada) e, para todo subconjunto que se exclui duas a duas e cada prazo t
# de um membro, Σ h dos membros com janela ≤ t ≤ t. (Sem troca: as entradas aleatórias têm troca 0.)
from fractions import Fraction as F
from itertools import combinations
import math
def num(v):
    if v is None or v=='': return None
    return F(str(v))
def janela(c):
    H=num(c.get('jan')); return math.inf if H is None or H<0 else H
def excl(a,b,pools):
    if a.get('seq') and b.get('seq'): return True
    if set(a.get('ativos') or [])&set(b.get('ativos') or []): return True
    for k,pv in (pools or {}).items():
        un=num((pv or {}).get('un'))
        if un is not None and un<=1 and (num((a.get('rec') or {}).get(k)) or 0)>0 and (num((b.get('rec') or {}).get(k)) or 0)>0: return True
    return False
def viavel(e,h,tol=F(0)):
    cs=e['cfgs']; n=len(cs); pools=e.get('pools') or {}; H=[janela(c) for c in cs]
    h=[F(x) if not isinstance(x,float) else x for x in h]
    for i in range(n):
        if h[i]>H[i]+tol: return False,f'{cs[i]["id"]}: h={float(h[i]):.6g} > janela {H[i]}'
    X=[[i!=j and excl(cs[i],cs[j],pools) for j in range(n)] for i in range(n)]
    for m in range(2,n+1):
        for S in combinations(range(n),m):
            if not all(X[a][b] for a,b in combinations(S,2)): continue
            for t in sorted({H[i] for i in S if H[i]!=math.inf}):
                s=sum((h[i] for i in S if H[i]<=t),F(0) if not any(isinstance(h[i],float) for i in S) else 0.0)
                if s>t+tol: return False,f'{[cs[i]["id"] for i in S]} @ {t}: soma {float(s):.6g} h'
    return True,''
def agenda_ok(e,ag):
    """ag = {id: [[ini,fim],...]} (frações em texto). Confere horas = q/r, fim ≤ janela, sem sobreposição entre quem se exclui, q ≤ teto da parte."""
    cs=e['cfgs']; pools=e.get('pools') or {}; Q=F(str(e['Q'])); ps=[num(c.get('part')) for c in cs]
    sp=sum((p for p in ps if p is not None),F(0)); esc=F(100)/sp if sp>100 else F(1)
    q={}; erros=[]
    for i,c in enumerate(cs):
        iv=[(F(a),F(b)) for a,b in ag.get(c['id'],[])]; hh=sum((b-a for a,b in iv),F(0)); q[c['id']]=hh*F(str(c['rend']))
        for a,b in iv:
            if a<0 or b<a or b>janela(c): erros.append(f'{c["id"]} intervalo {a}-{b} fora da janela')
        if ps[i] is not None and q[c['id']]>Q*ps[i]*esc/100: erros.append(f'{c["id"]} passa da parte')
    for i,j in combinations(range(len(cs)),2):
        if not excl(cs[i],cs[j],pools): continue
        for a,b in ag.get(cs[i]['id'],[]):
            for c_,d in ag.get(cs[j]['id'],[]):
                if max(F(a),F(c_))<min(F(b),F(d)): erros.append(f'{cs[i]["id"]}×{cs[j]["id"]} sobrepõem')
    return q,erros
