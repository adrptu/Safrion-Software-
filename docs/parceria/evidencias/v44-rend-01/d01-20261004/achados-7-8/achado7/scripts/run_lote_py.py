# uso: python3 run_lote_py.py <raiz> <entradas.json> [ini] [fim] [lista_de_indices.json] → JSONL compacto como run_lote.js
import sys,json,time
sys.path.insert(0,sys.path[0]); import lib_py
raiz,arq=sys.argv[1],sys.argv[2]; L=json.load(open(arq)); ini=int(sys.argv[3]) if len(sys.argv)>3 else 0; fim=int(sys.argv[4]) if len(sys.argv)>4 else len(L)
idx=json.load(open(sys.argv[5])) if len(sys.argv)>5 else range(ini,fim)
m=lib_py.carrega(raiz,True)
def js(v): return None if (isinstance(v,float) and v==float('inf')) else v
for k in idx:
    c=L[k]; m._BL.clear(); t0=time.perf_counter(); r=m.repartir(c['Q'],c['cfgs'],c.get('pools') or {}); ms=(time.perf_counter()-t0)*1000
    print(json.dumps(dict(k=k,nome=c['nome'],alocado=r['alocado'],saldo=r['saldo'],deficit=r['deficit'],conflito=r['conflito'],pendente=r['pendente'],q=[x['q'] for x in r['itens']],
        motivos=list(r['motivos']),caminho=lib_py.caminho(r['motivos']),bl=[list(z) for z in m._BL],ms=round(ms,2)),ensure_ascii=False),flush=True)
