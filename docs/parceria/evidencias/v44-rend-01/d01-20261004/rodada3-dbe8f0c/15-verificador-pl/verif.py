# Verificador INDEPENDENTE (não importa nada do repositório): física do arranjo + cortes por prazo + PL exato (preempção, sem troca)
import math, itertools
import numpy as np
from scipy.optimize import linprog
INF=math.inf
def num(x):
    if x is None or x=='': return None
    if isinstance(x,bool): return math.nan
    try: v=float(str(x).replace(',','.')) if not isinstance(x,(int,float)) else float(x)
    except Exception: return math.nan
    return v if math.isfinite(v) else math.nan
def parse(case):
    pools={}
    for k,pv in (case.get('pools') or {}).items():
        u=num((pv or {}).get('un'))
        if u is not None and not math.isnan(u) and u>=0: pools[k]=u
    cs=[]
    for i,c in enumerate(case['cfgs']):
        r=num(c.get('rend')); p=num(c.get('part')); H=num(c.get('jan')); tr=num(c.get('troca'))
        x=dict(i=i,r=r if (r is not None and not math.isnan(r) and r>0) else None,p=p if (p is not None and not math.isnan(p) and p>=0) else None,
               H=INF if (H is None or math.isnan(H) or H<0) else H,troca=tr if (tr is not None and not math.isnan(tr) and tr>0) else 0.0,
               seq=bool(c.get('seq')),at=set(a for a in (c.get('ativos') or []) if a),rec={k:(num(v) or 0) for k,v in (c.get('rec') or {}).items()})
        x['semRec']=any(x['rec'].get(k,0)>0 and x['rec'].get(k,0)>u+1e-9 for k,u in pools.items())
        if x['semRec']: x['H']=0.0
        cs.append(x)
    Q=num(case['Q']); Q=0.0 if (Q is None or math.isnan(Q) or Q<0) else Q
    return Q,cs,pools
def hard(x,y,pools,fora=None):   # nunca ao mesmo tempo, fato do cadastro: sequência declarada, ativo em comum, grupo de 1 unidade
    if x['seq'] and y['seq']: return True
    if x['at']&y['at']: return True
    return any(k!=fora and u<=1 and x['rec'].get(k,0)>0 and y['rec'].get(k,0)>0 for k,u in pools.items())
def mwis(us,k,pools):   # maior uso simultâneo do grupo k (força bruta)
    best=0; n=len(us)
    for m in range(1,1<<n):
        S=[us[j] for j in range(n) if m>>j&1]
        if any(hard(a,b,pools,k) for a,b in itertools.combinations(S,2)): continue
        best=max(best,sum(s['rec'].get(k,0) for s in S))
    return best
def excl_model(A,pools):   # modelo do algoritmo: + grupo de 2+ que serializa (decidido sobre A)
    ser=[k for k,u in pools.items() if u>1 and len([x for x in A if x['rec'].get(k,0)>0])>1 and mwis([x for x in A if x['rec'].get(k,0)>0],k,pools)>u+1e-9]
    def ex(x,y): return hard(x,y,pools) or any(x['rec'].get(k,0)>0 and y['rec'].get(k,0)>0 for k in ser)
    return ex,ser
def cortes_viol(A,h,pools,tol=1e-9):   # todo subconjunto que se exclui 2 a 2 e cada prazo t: Σh + trocas (as de todos menos a maior) ≤ t
    ex,ser=excl_model(A,pools); n=len(A); out=[]
    E=[[a!=b and ex(A[a],A[b]) for b in range(n)] for a in range(n)]
    for m in range(1,1<<n):
        S=[j for j in range(n) if m>>j&1]
        if len(S)<2 or any(not E[a][b] for a,b in itertools.combinations(S,2)): continue
        for t in sorted(set(A[j]['H'] for j in S if A[j]['H']<INF)):
            St=[j for j in S if A[j]['H']<=t]
            if len(St)<2: continue
            tr=[A[j]['troca'] for j in St]; need=sum(h[A[j]['i']] for j in St)+sum(tr)-max(tr)
            if need>t+tol*max(1,t): out.append(([A[j]['i'] for j in St],t,need))
    return out,ser
def lp_falta(jobs,pools):   # jobs: [(cfg,h)]; mínimo de horas que não cabem nos prazos (física exata, preempção, sem troca)
    jobs=[(x,h) for x,h in jobs if h>1e-12 and x['H']<INF]
    if not jobs: return 0.0
    n=len(jobs); fe=[]
    for m in range(1,1<<n):
        S=[j for j in range(n) if m>>j&1]; xs=[jobs[j][0] for j in S]
        if any((a['seq'] and b['seq']) or (a['at']&b['at']) for a,b in itertools.combinations(xs,2)): continue
        if any(sum(x['rec'].get(k,0) for x in xs)>u+1e-9 for k,u in pools.items()): continue
        fe.append(m)
    mx=[m for m in fe if not any((m2&m)==m and m2!=m for m2 in fe)]
    ts=sorted(set(x['H'] for x,_ in jobs)); L=[ts[0]]+[ts[k]-ts[k-1] for k in range(1,len(ts))]
    var=[(m,p) for m in mx for p in range(len(ts))]; nv=len(var)+n
    c=np.zeros(nv); c[len(var):]=1
    Aub=[]; bub=[]
    for p in range(len(ts)):
        row=np.zeros(nv)
        for vi,(m,pp) in enumerate(var):
            if pp==p: row[vi]=1
        Aub.append(row); bub.append(L[p])
    for j,(x,h) in enumerate(jobs):
        row=np.zeros(nv)
        for vi,(m,p) in enumerate(var):
            if m>>j&1 and ts[p]<=x['H']+1e-12: row[vi]=-1
        row[len(var)+j]=-1; Aub.append(row); bub.append(-h)
    r=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),bounds=[(0,None)]*nv,method='highs')
    return r.fun if r.status==0 else float('nan')
def plano(Q,cs):   # demanda inteira pela partilha (especificação: % fixos; resto pelo rendimento entre as sem % com horas)
    fx=[x for x in cs if x['p'] is not None]; sp=sum(x['p'] for x in fx); esc=100/sp if sp>100 else 1
    q1=[0.0]*len(cs); R=Q
    for x in fx:
        t=Q*x['p']*esc/100; R-=t
        if x['r'] is not None and t>1e-12: q1[x['i']]=t
    if R<=1e-9*max(1,Q): R=0
    liv=[x for x in cs if x['p'] is None]; ok=bool(liv) and all(x['r'] is not None for x in liv)
    lh=[x for x in liv if x['H']>0]; pl=lh or liv
    if R>0 and ok:
        sr=sum(x['r'] for x in pl)
        for x in pl: q1[x['i']]=x['r']*R/sr
    return q1
