import json
from fractions import Fraction as F
K='/tmp/claude-0/-home-user-Safrion-Software-/65558514-68d9-57f5-9da3-513cd6735cdc/scratchpad/r2_7_8/achado8/cetico'
E=json.load(open(K+'/ent/aleat.json'))
L=lambda v,l,f='aleat': json.load(open(f'{K}/brutos/A_{l}_{v}_{f}.json'))
p0=L('P0','py')
for v in ('P0','P1','P2'):
    p=L(v,'py'); j=L(v,'js')
    mais=[i for i in range(len(E)) if F(p[i]['alocado'])>F(p0[i]['alocado'])]
    menos=[i for i in range(len(E)) if F(p[i]['alocado'])<F(p0[i]['alocado'])]
    g=max(((float((F(p[i]['alocado'])-F(p0[i]['alocado']))/F(p[i]['alocado'])),i,float(F(p0[i]['alocado'])),float(F(p[i]['alocado']))) for i in mais),default=None)
    g2=max(((float((F(p[i]['alocado'])-F(p0[i]['alocado']))/F(p0[i]['alocado'])),i) for i in mais),default=None)
    pr=max(((float((F(p0[i]['alocado'])-F(p[i]['alocado']))/F(p0[i]['alocado'])),i,float(F(p0[i]['alocado'])),float(F(p[i]['alocado']))) for i in menos),default=None)
    prha=max(((float(F(p0[i]['alocado'])-F(p[i]['alocado'])),i) for i in menos),default=None)
    semc=sum(1 for i in mais+menos if not p0[i]['conflito'])
    msp=sum(1 for i in menos if any(c['part']=='' for c in E[i]['cfgs']))
    LJ=L(v,'py','aleat_janx2'); mj=sum(1 for i in range(len(E)) if F(LJ[i]['alocado'])<F(p[i]['alocado']))
    LQ=L(v,'py','aleat_Qx2'); mq=sum(1 for i in range(len(E)) if F(LQ[i]['alocado'])<F(p[i]['alocado']))
    near=lambda a,b: abs(float(F(a) if isinstance(a,str) else a)-float(F(b)))<=1e-9*max(1,abs(float(F(b))))
    par=[i for i in range(len(E)) if not (all(near(a,b) for a,b in zip(j[i]['q']+[j[i]['alocado'],j[i]['saldo']],p[i]['q']+[p[i]['alocado'],p[i]['saldo']])) and j[i]['conflito']==p[i]['conflito'] and j[i]['motivos']==p[i]['motivos'])]
    print(v,dict(mais=len(mais),ganho_rel_sobre_novo=g,ganho_rel_sobre_P0=g2,menos=len(menos),menos_com_sem_pct=msp,maior_perda_rel=pr,maior_perda_ha=prha,muda_sem_conflito_P0=semc,mono_jan_cai=mj,mono_Q_cai=mq,paridade_falhas=len(par),ex_par=par[:3]))
