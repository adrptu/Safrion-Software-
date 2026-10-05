# quebra das violações do verificador nas 3 300 entradas aleatórias, por variante: tipo (V0–V3), categoria, motor, θ*, saldo 0 com violação,
# e se a entrada tem um só prazo finito entre as configurações com horas
import json,sys
from collections import Counter
W=sys.argv[1]; L=json.load(open(W+'/entradas/aleatorias_s20261004.json'))
for n in sys.argv[2:]:
    V={d['k']:d for d in map(json.loads,open(W+f'/brutos/verif_aleat_{n}.jsonl'))}; S={d['k']:d for d in map(json.loads,open(W+f'/brutos/aleat_js_{n}.jsonl'))}
    tipos=Counter(); cat=Counter(); motor=Counter(); th=[]; saldo0=[]; semconf=[]; unico=0; ex=[]
    for k,d in V.items():
        if not d['violacoes']: continue
        ts={x[:2] for x in d['violacoes']}; tipos[','.join(sorted(ts))]+=1; cat[d['cat']]+=1; motor[d['motor']]+=1
        if isinstance(d['theta'],float): th.append(d['theta'])
        s=S[k]
        if abs(s['saldo'])<1e-9: saldo0.append(k)
        if not s['conflito']: semconf.append(k)
        c=L[k]; hs={c['cfgs'][i].get('jan') for i,q in enumerate(s['q']) if (q or 0)>1e-9 and c['cfgs'][i].get('jan') not in ('',None)}
        if len(hs)<=1: unico+=1
        if d['cat'] in ('A','D'): ex.append((k,d['cat'],d['violacoes'][:2],d['motor']))
    th.sort()
    print(json.dumps(dict(variante=n,com_violacao=sum(cat.values()),tipos=dict(tipos),categoria=dict(cat),motor=dict(motor),theta_min=th[0] if th else None,theta_mediana=th[len(th)//2] if th else None,
        com_saldo_zero=len(saldo0),exemplos_saldo_zero=saldo0[:8],sem_conflito=len(semconf),com_um_so_prazo=unico,exemplos_A_D=ex),ensure_ascii=False))
