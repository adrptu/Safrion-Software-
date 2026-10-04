import json,math,itertools
from fractions import Fraction as F
C='/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/r2_7_8/achado8/cetico'
E=json.load(open(C+'/casos_F.json'))
def ex(a,b,pools):
    if a.get('seq') and b.get('seq'): return True
    if set(a.get('ativos') or [])&set(b.get('ativos') or []): return True
    return any(pools[k]['un']<=1 and (a.get('rec')or{}).get(k) and (b.get('rec')or{}).get(k) for k in pools)
def viav(e,h):
    cs=e['cfgs']; n=len(cs); P=e.get('pools') or {}; H=[F(str(c['jan'])) if c.get('jan') not in (None,'') else None for c in cs]
    h=[F(x) for x in h]
    for i in range(n):
        if H[i] is not None and h[i]>H[i]: return 'h>jan %s'%cs[i]['id']
    X={(i,j) for i in range(n) for j in range(n) if i!=j and ex(cs[i],cs[j],P)}
    if all((i,j) in X for i in range(n) for j in range(n) if i!=j):  # completo: EDF exato
        o=sorted(range(n),key=lambda i:(H[i] is None, H[i] or 0)); t=F(0)
        for i in o:
            t+=h[i]
            if H[i] is not None and t>H[i]: return 'EDF falha em %s: fim %s > %s'%(cs[i]['id'],t,H[i])
        return 'viavel(EDF)'
    # M2: caminho B-A-C: A primeiro
    ids=[c['id'] for c in cs]; a,b,c=h
    return 'viavel(caminho)' if a+b<=H[0] and a+c<=H[2] else 'inviavel(caminho)'
fl=lambda v: float(F(v)) if isinstance(v,str) else float(v)
vs=['ee4f954','04bf6f2','2e31588','P1','P2','P0nR23','P2nR23']
R={v:(json.load(open(f'{C}/brutos/F_js_{v}.json')),json.load(open(f'{C}/brutos/F_py_{v}.json'))) for v in vs}
for k in E:
    print('==',k)
    for v in vs:
        j,p=R[v][0][k],R[v][1][k]
        par=all(abs(fl(x)-fl(y))<1e-6 for x,y in zip(j['q'],p['q'])) and abs(j['alocado']-fl(p['alocado']))<1e-6 and j['conflito']==p['conflito'] and j['motivos']==p['motivos'] and abs(fl(j["deficit"] or 0)-fl(p["deficit"] or 0))<1e-6
        print(f"{v:8} aloc={fl(p['alocado']):.4f} q={[round(fl(x),4) for x in p['q']]} saldo={fl(p['saldo']):.4f} confl={p['conflito']} def={p['deficit']} decor={p['decorrido']} viav={viav(E[k],p['h'])} parJSPy={par}")
