# uso: python3 cx_run_py.py <gen37> <entrada.json> <frac 0|1> [i0 i1] -> JSONL
import sys,json,time,importlib
from fractions import Fraction as Fr
g,arq,frac=sys.argv[1],sys.argv[2],sys.argv[3]=='1'
sys.path.insert(0,g); import dados2
casos=json.load(open(arq)); i0=int(sys.argv[4]) if len(sys.argv)>4 else 0; i1=int(sys.argv[5]) if len(sys.argv)>5 else len(casos)
def F(v): return Fr(v).limit_denominator(10**6) if isinstance(v,(int,float)) and not isinstance(v,bool) else v
for i in range(i0,min(i1,len(casos))):
    c=casos[i]; cf=[dict(x) for x in c['cfgs']]
    if frac:
        for x in cf:
            for k in ('rend','part','jan','custo_h','troca'):
                if k in x: x[k]=F(x[k])
    Q=F(c['Q']) if frac else c['Q']
    t0=time.perf_counter(); r=dados2.repartir(Q,cf,c.get('pools') or {}); ms=(time.perf_counter()-t0)*1000
    mot=r['motivos']; it=r['itens']
    s=lambda v: str(v) if isinstance(v,Fr) else v
    print(json.dumps(dict(i=i,nome=c['nome'],alocado=float(r['alocado']),saldo=float(r['saldo']),deficit=float(r['deficit']),conflito=bool(r['conflito']),
        exato=[s(r['alocado']),s(r['saldo']),s(r['deficit'])],q=[float(x['q']) for x in it],q_exato=[s(x['q']) for x in it],
        est=any('combinações demais para conferir quem trabalha' in m for m in mot),cic=any('máquinas compartilhadas em ciclo' in m for m in mot),ms=[ms],motivos=mot,decorrido=float(r['decorrido']) if r['decorrido'] is not None else None),ensure_ascii=False),flush=True)
