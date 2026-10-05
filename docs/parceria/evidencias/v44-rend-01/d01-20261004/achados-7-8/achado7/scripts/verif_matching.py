# 2º verificador independente (não usa verif.py nem o código do protótipo), só para grades trator × implemento:
# enumera os emparelhamentos (conjuntos sem ativo em comum = quem pode trabalhar junto) entre as configurações com prazo finito e h > 0,
# e resolve o PL do cronograma por segmento entre prazos: max θ com θ·h_i ≤ Σ_{segmentos até H_i} Σ_{M ∋ i} y[M,k], Σ_M y[M,k] ≤ duração.
# uso: python3 verif_matching.py <entradas.json> <saida.txt>   (saída de run_js.js/run_py.py; q_exato se houver)
import json,sys,math
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
L=json.load(open(sys.argv[1])); S=[json.loads(l) for l in open(sys.argv[2]) if l.strip() and not l.startswith('#')]
def H(c): j=c.get('jan'); return math.inf if j in ('',None) else float(j)
for c,s in zip(L,S):
    assert c['nome']==s['nome']; cf=c['cfgs']
    q=[float(Fr(z)) for z in s['q_exato']] if 'q_exato' in s else [z or 0 for z in s['q']]
    h=[q[i]/float(cf[i]['rend']) for i in range(len(cf))]
    at=[i for i in range(len(cf)) if H(cf[i])!=math.inf and h[i]>1e-12]
    M=[]
    def dfs(k,cur,usados):
        if k==len(at): 
            if cur: M.append(tuple(cur))
            return
        dfs(k+1,cur,usados); i=at[k]; a=set(cf[i]['ativos'])
        if not (a&usados): dfs(k+1,cur+[i],usados|a)
    dfs(0,[],set())
    ts=sorted({H(cf[i]) for i in at}); segs=[]; a0=0.0
    for t in ts: segs.append((a0,t)); a0=t
    var=[(k,m) for k,(t0,t1) in enumerate(segs) for m in M if all(H(cf[i])>=t1 for i in m)]
    nv=len(var)+1; A=[]; b=[]
    for i in at:
        r=np.zeros(nv); r[-1]=h[i]
        for j,(k,m) in enumerate(var):
            if i in m: r[j]=-1
        A.append(r); b.append(0.0)
    for k,(t0,t1) in enumerate(segs):
        r=np.zeros(nv)
        for j,(kk,m) in enumerate(var):
            if kk==k: r[j]=1
        A.append(r); b.append(t1-t0)
    cvec=np.zeros(nv); cvec[-1]=-1
    res=linprog(cvec,A_ub=np.array(A),b_ub=np.array(b),bounds=[(0,None)]*len(var)+[(0,1e6)],method='highs')
    th=-res.fun if res.status==0 else None
    print(json.dumps(dict(nome=c['nome'],configs_com_prazo=len(at),emparelhamentos=len(M),segmentos=len(segs),theta=th,executavel=(th is not None and th>=1-1e-7)),ensure_ascii=False),flush=True)
