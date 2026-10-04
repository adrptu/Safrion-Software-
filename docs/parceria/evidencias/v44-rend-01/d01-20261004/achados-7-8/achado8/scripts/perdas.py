# Onde P1/P2 atendem menos que P0: há configurações sem %? qual a soma das horas por grupo? Exemplos de maior ganho e perda.
import json,sys,os
from fractions import Fraction as F
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E=json.load(open(f'{W}/entradas/aleat.json'))
R={v:json.load(open(f'{W}/brutos/R_py_{v}_aleat.json'))['res'] for v in ('P0','P1','P2')}
for v in ('P1','P2'):
    menos=[i for i in range(len(E)) if F(R[v][str(i)]['alocado'])<F(R['P0'][str(i)]['alocado'])]
    mais=[i for i in range(len(E)) if F(R[v][str(i)]['alocado'])>F(R['P0'][str(i)]['alocado'])]
    cl=sum(1 for i in menos if any(c['part']=='' for c in E[i]['cfgs']))
    cm=sum(1 for i in mais if any(c['part']=='' for c in E[i]['cfgs']))
    hp=sum(1 for i in menos if sum(F(x) for x in R[v][str(i)]['h'])>sum(F(x) for x in R['P0'][str(i)]['h']))
    hm=sum(1 for i in menos if sum(F(x) for x in R[v][str(i)]['h'])<sum(F(x) for x in R['P0'][str(i)]['h']))
    hpm=sum(1 for i in mais if sum(F(x) for x in R[v][str(i)]['h'])<sum(F(x) for x in R['P0'][str(i)]['h']))
    print(f'{v}: menos={len(menos)} (com configuração sem %: {cl}; horas-conjunto maiores que P0: {hp}; menores: {hm}) · mais={len(mais)} (com sem %: {cm}; com menos horas-conjunto: {hpm})')
for v,i in (('P1',449),('P1',4422),('P2',113),('P2',5549)):
    print(f'\n{v} idx {i}: entrada {json.dumps(E[i])}')
    for w in ('P0',v): r=R[w][str(i)]; print(f'  {w}: q={[str(F(x)) if "." not in x else x for x in r["q"]]} alocado={r["alocado"]} ({float(F(r["alocado"])):.4f}) conflito={r["conflito"]}')
