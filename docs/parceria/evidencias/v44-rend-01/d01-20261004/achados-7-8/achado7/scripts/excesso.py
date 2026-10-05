# quanto da área atribuída às configurações COM prazo não cabe em nenhum cronograma (grade trator × implemento, V3b):
# max Σ r·x sujeito a 0 ≤ x ≤ h (horas da saída) e carga de cada ativo em cada segmento ≤ duração; excesso = Σ r·h − máximo (ha)
import sys,json,math
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0,sys.path[0]); import verif
def excesso(caso,saida):
    it,P=verif.prep(caso); q=saida['q']; h=[(q[i] or 0)/it[i]['r'] if it[i]['r'] else 0 for i in range(len(it))]
    at=[i for i,x in enumerate(it) if x['H']!=math.inf and h[i]>1e-9]; assert verif.linha_bip(it,at)
    segs=verif.segmentos([x['H'] for x in it],at); var=[(i,k) for i in at for k,(a,b) in enumerate(segs) if it[i]['H']>=b]
    A=[];b=[]
    for i in at:
        row=np.zeros(len(var)); 
        for j,(ii,k) in enumerate(var):
            if ii==i: row[j]=1
        A.append(row); b.append(h[i])
    for z in sorted({a for i in at for a in it[i]['at']}):
        for k,(t0,t1) in enumerate(segs):
            row=np.zeros(len(var))
            for j,(i,kk) in enumerate(var):
                if kk==k and z in it[i]['at']: row[j]=1
            A.append(row); b.append(t1-t0)
    c=np.array([-it[i]['r'] for (i,k) in var]); res=linprog(c,A_ub=np.array(A),b_ub=np.array(b),bounds=[(0,None)]*len(var),method='highs'); assert res.status==0
    tot=sum(it[i]['r']*h[i] for i in at); return tot,-res.fun,tot+res.fun
if __name__=='__main__':
    L=json.load(open(sys.argv[1])); S=[json.loads(l) for l in open(sys.argv[2]) if not l.startswith('#')]
    for c,s in zip(L,S):
        assert c['nome']==s['nome']
        try: t,m,e=excesso(c,s); print(json.dumps(dict(nome=c['nome'],ha_com_prazo=t,ha_executavel_max=m,excesso_ha=e),ensure_ascii=False))
        except AssertionError as ex: print(json.dumps(dict(nome=c['nome'],erro='fora da estrutura de bipartido'),ensure_ascii=False))
