import sys,json
from fractions import Fraction as F
sys.path.insert(0,sys.argv[1]); import dados2
E=json.load(open(sys.argv[2])); O={}
def fr(v): return F(str(v)) if isinstance(v,(int,float)) and not isinstance(v,bool) else v
for k,x in E.items():
    cs=[{kk:(fr(vv) if kk in('rend','part','jan','custo_h','troca') else vv) for kk,vv in c.items()} for c in x['cfgs']]
    r=dados2.repartir(fr(x['Q']),cs,x.get('pools') or {})
    s=lambda v: None if v is None else str(v)
    O[k]=dict(q=[s(i['q']) for i in r['itens']],h=[s(i['h']) for i in r['itens']],alocado=s(r['alocado']),saldo=s(r['saldo']),conflito=r['conflito'],deficit=s(r['deficit']),decorrido=s(r.get('decorrido')),motivos=r['motivos'])
print(json.dumps(O,ensure_ascii=False))
