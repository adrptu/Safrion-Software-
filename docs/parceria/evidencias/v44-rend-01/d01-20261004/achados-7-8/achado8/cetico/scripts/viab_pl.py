# Cético: viabilidade das saídas nas 6000 aleatórias. Grafo completo: EDF exato (Fraction no Python, tolerância 1e-7 h no JS).
# Grafo não completo: PL de escalonamento preemptivo exato (conjuntos independentes por intervalo entre prazos), tolerância 1e-7 h.
import json,itertools,math,sys
from fractions import Fraction as F
from multiprocessing import Pool
import numpy as np
from scipy.optimize import linprog
K='/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/r2_7_8/achado8/cetico'
E=json.load(open(K+'/ent/aleat.json'))
def ex(a,b,P):
    if a.get('seq') and b.get('seq'): return True
    if set(a.get('ativos') or [])&set(b.get('ativos') or []): return True
    return any(P[k]['un']<=1 and (a.get('rec')or{}).get(k) and (b.get('rec')or{}).get(k) for k in P)
def jan(c): return None if c.get('jan') in (None,'') else F(str(c['jan']))
def check(args):
    i,h,exato=args; e=E[i]; cs=e['cfgs']; n=len(cs); P=e.get('pools') or {}; H=[jan(c) for c in cs]
    tol=F(0) if exato else F(1,10**7)
    h=[F(x) if isinstance(x,str) else F(x) for x in h]
    for k in range(n):
        if H[k] is not None and h[k]>H[k]+tol: return (i,False,float(h[k]-H[k]))
    X=[[k!=m and ex(cs[k],cs[m],P) for m in range(n)] for k in range(n)]
    if all(X[k][m] for k in range(n) for m in range(n) if k!=m):
        t=F(0); worst=F(0)
        for k in sorted(range(n),key=lambda k:(H[k] is None,H[k] or 0)):
            t+=h[k]
            if H[k] is not None and t-H[k]>worst: worst=t-H[k]
        return (i,worst<=tol,float(worst))
    Hf=[math.inf if x is None else float(x) for x in H]; hf=[float(x) for x in h]
    ind=[S for m in range(1,n+1) for S in itertools.combinations(range(n),m) if all(not X[a][b] for a,b in itertools.combinations(S,2))]
    bds=sorted({0.0}|{x for x in Hf if x!=math.inf}); bds.append(bds[-1]+sum(hf)+1); I=len(bds)-1; ns=len(ind)
    # minimizar a violação máxima s: sum_S y_kS <= len_k ; |sum y - h_i| <= s
    nv=I*ns+1; Aub=[];bub=[]
    for k in range(I):
        r=np.zeros(nv); r[k*ns:(k+1)*ns]=1; Aub.append(r); bub.append(bds[k+1]-bds[k])
    for a in range(n):
        r=np.zeros(nv)
        for k in range(I):
            if bds[k+1]<=Hf[a]+1e-12:
                for s,S in enumerate(ind):
                    if a in S: r[k*ns+s]=1
        r1=r.copy(); r1[-1]=-1; Aub.append(r1); bub.append(hf[a])
        r2=-r; r2[-1]=-1; Aub.append(r2); bub.append(-hf[a])
    c=np.zeros(nv); c[-1]=1
    res=linprog(c,A_ub=np.array(Aub),b_ub=np.array(bub),bounds=(0,None),method='highs')
    v=res.fun if res.status==0 else 1e9
    return (i,v<=1e-7,v)
if __name__=='__main__':
    out={}
    with Pool(16) as pool:
        for v in (sys.argv[1:] or ['P0','P1','P2']):
            for l in ('js','py'):
                R=json.load(open(f'{K}/brutos/A_{l}_{v}_aleat.json'))
                rs=pool.map(check,[(i,R[i]['h'],l=='py') for i in range(len(E))],chunksize=50)
                bad=[(i,w) for i,ok,w in rs if not ok]
                print(v,l,'inviaveis=',len(bad),'maior_excesso_h=',max([w for _,w in bad],default=0),'exemplos=',bad[:6],flush=True)
