# Para as entradas que o verificador exato (tolerância 0) recusa: o maior excesso exato (h) sobre o prazo, por variante.
import json,sys,os,math
from fractions import Fraction as F
from itertools import combinations
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(W,'scripts'))
from verif import viavel, excl, janela
E=json.load(open(f'{W}/entradas/aleat.json'))
for v in ['P0','P1','P2']:
    rp=json.load(open(f'{W}/brutos/R_py_{v}_aleat.json'))['res']; mx=F(0); quem=None; n=0
    for i,e in enumerate(E):
        h=[F(x) for x in rp[str(i)]['h']]
        if viavel(e,h)[0]: continue
        n+=1; cs=e['cfgs']; H=[janela(c) for c in cs]; P=e.get('pools') or {}
        for m in range(2,len(cs)+1):
            for S in combinations(range(len(cs)),m):
                if not all(excl(cs[a],cs[b],P) for a,b in combinations(S,2)): continue
                for t in {H[i] for i in S if H[i]!=math.inf}:
                    d=sum((h[i] for i in S if H[i]<=t),F(0))-t
                    if d>mx: mx=d; quem=(i,[cs[j]['id'] for j in S],t)
    print(v,'recusadas com tolerância 0:',n,'· maior excesso exato =',float(mx),'h',quem)
