# área máxima executável com q'_i ≤ q_i (só configurações com prazo), modelo de carga por ativo (exato para trator×implemento)
import json,sys,math,numpy as np
sys.path.insert(0,__file__.rsplit('/',1)[0]); import cx_verif as V
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
def maxarea(caso,res):
    it,act,v=V.base(caso,res); assert V.bip_ok(act,caso.get('pools') or {})
    n=len(act); sg=V.segs(act); var={}
    for k,(a,t) in enumerate(sg):
        for i in range(n):
            if act[i]['H']>=t-1e-12: var[(i,k)]=len(var)
    rows=[];b=[]; ats=sorted(set(z for x in act for z in x['at']))
    for k,(a,t) in enumerate(sg):
        for z in ats:
            row={var[(i,k)]:1 for i in range(n) if (i,k) in var and z in act[i]['at']}
            if row: rows.append(row); b.append(t-a)
        for i in range(n):
            if (i,k) in var: rows.append({var[(i,k)]:1}); b.append(t-a)
    for i in range(n):
        rows.append({var[(i,k)]:1 for k in range(len(sg)) if (i,k) in var}); b.append(act[i]['h'])
    A=lil_matrix((len(rows),len(var)))
    for r_,row in enumerate(rows):
        for j,vv in row.items(): A[r_,j]=vv
    c=np.zeros(len(var))
    for (i,k),j in var.items(): c[j]=-act[i]['r']
    r=linprog(c,A_ub=A.tocsr(),b_ub=np.array(b),bounds=[(0,None)]*len(var),method='highs')
    tot=sum(x['q'] for x in act); return tot,-r.fun
casos=json.load(open(sys.argv[1]))
for l in open(sys.argv[2]):
    res=json.loads(l); tot,mx=maxarea(casos[res['i']],res)
    print(res['i'],res['nome'][:50],'área com prazo',round(tot,6),'máx executável',round(mx,6),'excesso',round(tot-mx,6),'Q',casos[res['i']]['Q'])
