# Verificador próprio do cético (não usa safra.js, dados2.py nem os scripts do pacote).
# Relaxação sem troca: cronograma preemptivo entre prazos; em cada instante só roda um conjunto compatível
# (sem ativo em comum, no máximo uma com seq, e Σ rec ≤ un em cada grupo). θ* = maior fator executável (θ*≥1 executável).
# Configurações sem janela não entram (rodam depois do último prazo). Dois motores: E (enumeração de conjuntos) e B (carga por ativo, Birkhoff; exato só para trator×implemento).
import json, sys, math
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
def num(x):
    if x is None or x=='' : return None
    try: return float(str(x).replace(',','.'))
    except: return float('nan')
def prep(caso, q):
    cf=caso['cfgs']; it=[]
    for i,c in enumerate(cf):
        r=num(c.get('rend')); H=num(c.get('jan'))
        H=math.inf if (H is None or H!=H or H<0) else H
        it.append(dict(i=i,r=r,H=H,q=q[i],at=[a for a in (c.get('ativos') or []) if a],seq=bool(c.get('seq')),rec={k:(num(v) or 0) for k,v in (c.get('rec') or {}).items()}))
    return it
def compat(x,y):
    if set(x['at'])&set(y['at']): return False
    if x['seq'] and y['seq']: return False
    return True
def okset(S,pools):
    for k,p in pools.items():
        un=num(p.get('un'))
        if un is None or un!=un or un<0: continue
        if sum(s['rec'].get(k,0) for s in S)>un+1e-9: return False
    return True
def base(caso,res):
    it=prep(caso,res['q']); v=[]
    Q=num(caso['Q']); s=sum(res['q'])+res['saldo']
    if abs(s-Q)>1e-6*max(1,Q): v.append('V0 conservação: Σq+saldo=%r, Q=%r'%(s,Q))
    for x in it:
        if x['q']>1e-9 and (x['r'] is None or x['q']>x['r']*x['H']+1e-7): v.append('V1 janela própria cfg %d'%x['i'])
    act=[x for x in it if x['q']>1e-12 and x['r'] and math.isfinite(x['H'])]
    for x in act: x['h']=x['q']/x['r']
    return it,act,v
def segs(act):
    ts=sorted(set(x['H'] for x in act)); out=[]; a=0
    for t in ts: out.append((a,t)); a=t
    return out
def lp(nv, A_rows, b, obj_idx):
    pass
def motorE(act,pools,cap=400000):
    n=len(act); comp=[[i!=j and compat(act[i],act[j]) for j in range(n)] for i in range(n)]
    sets=[]
    def dfs(start,cur):
        if len(sets)>cap: raise OverflowError
        sets.append(tuple(cur))
        for j in range(start,n):
            if all(comp[j][k] for k in cur) and okset([act[k] for k in cur+[j]],pools):
                cur.append(j); dfs(j+1,cur); cur.pop()
    dfs(0,[])
    sets=[s for s in sets if s]
    sg=segs(act); cols=[]
    for k,(a,t) in enumerate(sg):
        alive=set(i for i in range(n) if act[i]['H']>=t-1e-12)
        seen=set()
        for s in sets:
            ss=tuple(i for i in s if i in alive)
            if ss and ss not in seen: seen.add(ss)
        # só maximais (dentro do segmento)
        ls=sorted(seen,key=len,reverse=True); keep=[]; fs=[]
        for s in ls:
            S=set(s)
            if any(S<=F for F in fs): continue
            fs.append(S); keep.append(s)
        for s in keep: cols.append((k,s))
    m=len(cols); nv=1+m
    A=lil_matrix((len(sg)+n,nv)); b=np.zeros(len(sg)+n)
    for j,(k,s) in enumerate(cols):
        A[k,1+j]=1
        for i in s: A[len(sg)+i,1+j]=-1
    for k,(a,t) in enumerate(sg): b[k]=t-a
    for i in range(n): A[len(sg)+i,0]=act[i]['h']
    c=np.zeros(nv); c[0]=-1
    bd=[(0,1000)]+[(0,None)]*m
    r=linprog(c,A_ub=A.tocsr(),b_ub=b,bounds=bd,method='highs')
    return r.x[0], m
def bip_ok(act,pools):
    if any(x['seq'] for x in act) and sum(1 for x in act if x['seq'])>1: return False
    for k,p in pools.items():
        if sum(1 for x in act if x['rec'].get(k,0)>0)>1: return False
    if any(len(set(x['at']))>2 for x in act): return False
    adj={}
    for x in act:
        a=list(set(x['at']))
        if len(a)==2: adj.setdefault(a[0],[]).append(a[1]); adj.setdefault(a[1],[]).append(a[0])
    cor={}
    for z0 in adj:
        if z0 in cor: continue
        cor[z0]=0; st=[z0]
        while st:
            z=st.pop()
            for w in adj[z]:
                if w not in cor: cor[w]=1-cor[z]; st.append(w)
                elif cor[w]==cor[z]: return False
    return True
def motorB(act):
    n=len(act); sg=segs(act); var={}
    for k,(a,t) in enumerate(sg):
        for i in range(n):
            if act[i]['H']>=t-1e-12: var[(i,k)]=1+len(var)
    nv=1+len(var); rows=[]; b=[]
    ats=sorted(set(a for x in act for a in x['at']))
    for k,(a,t) in enumerate(sg):
        for z in ats:
            row={var[(i,k)]:1 for i in range(n) if (i,k) in var and z in act[i]['at']}
            if row: rows.append(row); b.append(t-a)
        for i in range(n):
            if (i,k) in var: rows.append({var[(i,k)]:1}); b.append(t-a)
    for i in range(n):
        row={0:act[i]['h']}
        for k in range(len(sg)):
            if (i,k) in var: row[var[(i,k)]]=-1
        rows.append(row); b.append(0)
    A=lil_matrix((len(rows),nv))
    for r_,row in enumerate(rows):
        for j,v in row.items(): A[r_,j]=v
    c=np.zeros(nv); c[0]=-1
    r=linprog(c,A_ub=A.tocsr(),b_ub=np.array(b),bounds=[(0,1000)]+[(0,None)]*(nv-1),method='highs')
    return r.x[0]
def verifica(caso,res,motores='EB',cap=400000):
    it,act,v=base(caso,res); out=dict(viol=v,n=len(act))
    if not act: out.update(theta=None,motor='vazio'); return out
    pools=caso.get('pools') or {}
    if 'B' in motores and bip_ok(act,pools): out['thetaB']=motorB(act)
    if 'E' in motores:
        try: out['thetaE'],out['colsE']=motorE(act,pools,cap)
        except OverflowError: out['thetaE']=None
    th=[t for t in (out.get('thetaB'),out.get('thetaE')) if t is not None]
    out['theta']=min(th) if th else None
    if out.get('thetaB') is not None and out.get('thetaE') is not None and abs(out['thetaB']-out['thetaE'])>1e-6: out['viol'].append('MOTORES DIVERGEM')
    out['inexec']=bool(out['theta'] is not None and out['theta']<1-1e-7)
    for k in ('theta','thetaB','thetaE'):
        if out.get(k) is not None: out[k]=float(out[k])
    return out
if __name__=='__main__':
    casos=json.load(open(sys.argv[1])); mot=sys.argv[3] if len(sys.argv)>3 else 'EB'
    for l in open(sys.argv[2]):
        res=json.loads(l); caso=casos[res['i']]
        o=verifica(caso,res,mot)
        print(json.dumps(dict(i=res['i'],nome=res['nome'],cat=caso.get('cat'),alocado=res['alocado'],saldo=res['saldo'],deficit=res['deficit'],conflito=res['conflito'],est=res['est'],**o),ensure_ascii=False))
