# excesso (ha sem cronograma) nas entradas aleatórias com violação V3b, por variante: máximo absoluto e relativo à área com prazo e a Q
import json,sys
sys.path.insert(0,sys.path[0]); import excesso
W=sys.argv[1]; L=json.load(open(W+'/entradas/aleatorias_s20261004.json'))
for n in sys.argv[2:]:
    V={d['k']:d for d in map(json.loads,open(W+f'/brutos/verif_aleat_{n}.jsonl'))}; S={d['k']:d for d in map(json.loads,open(W+f'/brutos/aleat_js_{n}.jsonl'))}
    R=[]
    for k,d in V.items():
        if d['violacoes'] and d['motor']=='V3b':
            t,m,e=excesso.excesso(L[k],S[k]); R.append((e,e/t,e/L[k]['Q'],k))
    R.sort(reverse=True); rel=sorted(R,key=lambda x:-x[1])
    print(json.dumps(dict(variante=n,entradas=len(R),maior_excesso_ha=R[0][0],k=R[0][3],maior_rel_area_com_prazo=rel[0][1],k_rel=rel[0][3],maior_rel_Q=max(x[2] for x in R),mediana_ha=R[len(R)//2][0]),ensure_ascii=False))
