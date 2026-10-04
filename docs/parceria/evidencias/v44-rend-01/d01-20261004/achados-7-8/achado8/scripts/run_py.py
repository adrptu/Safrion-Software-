# uso: python3 run_py.py <dir gen37> <entradas.json> [saida.json] — dados2.repartir com Fraction (entradas convertidas por F(str(x)))
import sys, json, time
from fractions import Fraction as F
d,ent=sys.argv[1],sys.argv[2]; sai=sys.argv[3] if len(sys.argv)>3 else None
sys.path.insert(0,d); import dados2 as D2
NUM=('rend','part','jan','custo_h','diesel','troca','pess')
def fr(v): return F(str(v)) if isinstance(v,(int,float)) and not isinstance(v,bool) else v
def cfg(c): return {k:(fr(v) if k in NUM else v) for k,v in c.items()}
E=json.load(open(ent)); ks=list(range(len(E))) if isinstance(E,list) else list(E)
OUT={}; tmax=0; tk=None
def s(x): return None if x is None else str(x)
for k in ks:
    e=E[k]; t0=time.perf_counter(); r=D2.repartir(fr(e['Q']),[cfg(c) for c in e['cfgs']],e.get('pools') or {}); ms=(time.perf_counter()-t0)*1000
    if ms>tmax: tmax=ms; tk=k
    OUT[str(k)]=dict(alocado=s(r['alocado']),saldo=s(r['saldo']),conflito=r['conflito'],deficit=s(r['deficit']),decorrido=s(r['decorrido']),motivos=r['motivos'],
        q=[s(x['q']) for x in r['itens']],h=[s(x['h']) for x in r['itens']],ms=ms)
o=json.dumps(dict(arquivo=d,tmax_ms=tmax,tmax_caso=tk,res=OUT),ensure_ascii=False)
if sai: open(sai,'w').write(o)
else: print(o)
