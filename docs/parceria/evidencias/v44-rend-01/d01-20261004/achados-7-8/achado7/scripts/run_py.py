# uso: python3 run_py.py <raiz_da_cópia> <entradas.json> [reps] [frac]  → uma linha JSON por caso (como run_js.js); frac=1 converte números em Fraction
import sys,json,time
from fractions import Fraction as Fr
sys.path.insert(0,sys.path[0]); import lib_py
raiz,arq=sys.argv[1],sys.argv[2]; reps=int(sys.argv[3]) if len(sys.argv)>3 else 2; frac=len(sys.argv)>4 and sys.argv[4]=='1'
mi=lib_py.carrega(raiz,True); mn=lib_py.carrega(raiz,False)
def fr(c):
    if not frac: return c['cfgs']
    out=[]
    for x in c['cfgs']:
        y=dict(x)
        for k in ('rend','part','jan','custo_h','troca'):
            if isinstance(y.get(k),(int,float)) and not isinstance(y.get(k),bool): y[k]=Fr(y[k]).limit_denominator(10**6)
        out.append(y)
    return out
def js(v):
    if isinstance(v,Fr): return float(v)
    if isinstance(v,float) and v==float('inf'): return None
    return v
for c in json.load(open(arq)):
    cf=fr(c); Q=Fr(c['Q']) if frac else c['Q']
    mi._BL.clear(); t0=time.perf_counter(); r=mi.repartir(Q,cf,c.get('pools') or {}); ti=round((time.perf_counter()-t0)*1000,2); bl=[dict(grafo=z[0],n=z[1],buraco=z[2],passos=z[3]) for z in mi._BL]
    ms=[] if reps>0 else [ti]   # reps=0: vale o tempo da execução instrumentada (só registro)
    for k in range(reps):
        t0=time.perf_counter(); r2=mn.repartir(Q,cf,c.get('pools') or {}); ms.append(round((time.perf_counter()-t0)*1000,2))
    a=lib_py.resumo(r)
    if reps>0: b=lib_py.resumo(r2); assert a==b,('instrumentado difere',c['nome'])
    o=dict(nome=c['nome'],n=len(c['cfgs'])); o.update({k:([js(z) for z in v] if isinstance(v,list) and k in('q','h') else js(v)) for k,v in a.items()})
    if frac: o['exato']={k:str(a[k]) for k in ('alocado','saldo','deficit')}; o['q_exato']=[str(z) for z in a['q']]
    o['buraco']=bl; o['ms']=ms; print(json.dumps(o,ensure_ascii=False),flush=True)
