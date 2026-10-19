import sys,json
from fractions import Fraction as F
sys.path.insert(0,sys.argv[1]); import dados2
E=json.load(open(sys.argv[2])); O=[]
def fr(v): return F(str(v)) if isinstance(v,(int,float)) and not isinstance(v,bool) else v
s=lambda v: None if v is None else str(v)
for x in E:
    cs=[{kk:(fr(vv) if kk in('rend','part','jan','custo_h','troca') else vv) for kk,vv in c.items()} for c in x['cfgs']]
    r=dados2.repartir(fr(x['Q']),cs,x.get('pools') or {})
    O.append(dict(q=[s(i['q']) for i in r['itens']],h=[s(i['h']) for i in r['itens']],alocado=s(r['alocado']),saldo=s(r['saldo']),conflito=r['conflito'],deficit=s(r['deficit']),motivos=r['motivos']))
json.dump(O,open(sys.argv[3],'w'),ensure_ascii=False)
