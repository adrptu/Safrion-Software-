# paridade JS × Python (float) nas entradas aleatórias: por k, alocado/saldo/déficit (rel 1e-9), conflito, q, motivos, caminho e buraco (resultado e passos)
import json,sys
sys.path.insert(0,sys.path[0]); import paridade
W=sys.argv[1]
for n in sys.argv[2:]:
    J={d['k']:d for d in map(json.loads,open(W+f'/brutos/aleat_js_{n}.jsonl'))}; P=[json.loads(l) for l in open(W+f'/brutos/aleat_py_{n}.jsonl')]
    dif=[]; 
    for p in P:
        j=J[p['k']]; j=dict(j,buraco=[{'grafo':b[0],'n':b[1],'buraco':b[2],'passos':b[3]} for b in j['bl']]); p=dict(p,buraco=[{'grafo':b[0],'n':b[1],'buraco':b[2],'passos':b[3]} for b in p['bl']])
        e=paridade.cmp(j,p)
        if e: dif.append((p['k'],e))
    print(json.dumps(dict(variante=n,entradas_python=len(P),com_diferenca=len(dif),exemplos=dif[:10],py_ms_max=max(x['ms'] for x in P),py_k_max=max(P,key=lambda x:x['ms'])['k']),ensure_ascii=False))
