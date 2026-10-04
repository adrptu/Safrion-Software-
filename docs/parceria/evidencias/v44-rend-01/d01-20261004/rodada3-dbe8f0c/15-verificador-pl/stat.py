import json, sys
from verif import *
cases=json.load(open(sys.argv[1])); J=json.load(open(sys.argv[2]))
for v in ('new','old','pre'):
    acc=0; accnc=0; worst=(0,None); tot=0
    for i,c in enumerate(cases):
        r=J[v][i]; Q,cs,pools=parse(c); q=r['q']; h=[q[x['i']]/x['r'] if q[x['i']]>1e-12 else 0 for x in cs]
        A=[x for x in cs if q[x['i']]>1e-12]
        if len(A)<2: continue
        f=lp_falta([(x,h[x['i']]) for x in A],pools)
        if f>1e-7:
            acc+=1
            if not r['conflito'] and r['saldo']<=1e-9:
                accnc+=1; hs=sum(h[x['i']] for x in A if x['H']<INF); rel=f/hs
                if rel>worst[0]: worst=(rel,i)
    print(v,'casos',len(cases),'atendido inviável (PL):',acc,'· desses sem conflito e saldo 0:',accnc,'· pior falta/horas com prazo: %.1f%% caso %s'%(worst[0]*100,worst[1]))
