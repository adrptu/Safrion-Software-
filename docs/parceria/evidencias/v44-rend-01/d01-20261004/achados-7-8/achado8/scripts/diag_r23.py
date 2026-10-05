# Diagnóstico: quanto a ordem R2-3 muda os números nas 6 000 entradas (P0nR23 = 2e31588 sem a ordem; P2nR23 = P2 sem a ordem), Python exato + viabilidade.
import json,sys,os
from fractions import Fraction as F
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(W,'scripts'))
from verif import viavel
E=json.load(open(f'{W}/entradas/aleat.json'))
R={v:json.load(open(f'{W}/brutos/R_py_{v}_aleat.json'))['res'] for v in ('P0','P0nR23','P2nR23')}
for v in ('P0nR23','P2nR23'):
    mais=menos=difq=inv=0
    for i in range(len(E)):
        a,b=F(R[v][str(i)]['alocado']),F(R['P0'][str(i)]['alocado'])
        mais+=a>b; menos+=a<b; difq+=R[v][str(i)]['q']!=R['P0'][str(i)]['q']
        inv+=not viavel(E[i],[F(x) for x in R[v][str(i)]['h']],tol=F(1,10**9))[0]
    print(f'{v} × 2e31588 (Python exato, 6 000): q diferente em {difq}; atende mais {mais}; menos {menos}; inviáveis (tol 1e-9 h) {inv}')
