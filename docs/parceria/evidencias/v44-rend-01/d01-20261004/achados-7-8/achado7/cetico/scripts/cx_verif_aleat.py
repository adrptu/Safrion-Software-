# verifica as 3300 aleatórias de todas as variantes, uma vez por (entrada, q, saldo) distinto
import json,sys,os,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import cx_verif as V
from multiprocessing import Pool
C=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
casos=json.load(open(C+'/../entradas/aleatorias_s20261004.json'))
VS=['P0','P1_2e18','P1_2e20','P1_2e22','P2','P2u']
res={v:[json.loads(l) for l in open(C+'/brutos/aleat_js_%s.jsonl'%v)] for v in VS}
def chave(r): return (r['i'],tuple(round(x,9) for x in r['q']),round(r['saldo'],9))
todos={}
for v in VS:
    for r in res[v]: todos.setdefault(chave(r),r)
def f(item):
    k,r=item; t=time.time(); o=V.verifica(casos[r['i']],r,'EB',300000); o['seg']=time.time()-t; return k,o
if __name__=='__main__':
    with Pool(2) as p: out=dict(p.map(f,list(todos.items()),chunksize=20))
    with open(C+'/brutos/verif_aleat.jsonl','w') as fo:
        for v in VS:
            for r in res[v]:
                o=out[chave(r)]; fo.write(json.dumps(dict(var=v,i=r['i'],cat=casos[r['i']]['cat'],alocado=r['alocado'],saldo=r['saldo'],conflito=r['conflito'],est=r['est'],cic=r['cic'],ms=r['ms'][0],**o),ensure_ascii=False)+'\n')
    print('distintos',len(todos))
