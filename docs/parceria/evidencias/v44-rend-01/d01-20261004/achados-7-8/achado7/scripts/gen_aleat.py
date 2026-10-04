# 3 300 entradas aleatórias sintéticas (semente registrada) para o verificador independente
#  A 1 500 gerais pequenas (2–10 configurações: ativos, sequência declarada, grupos de recursos, janelas vazias/0/finitas, partes, troca)
#  B 1 000 trator × implemento médios (subconjuntos de grades até 5×5, 6–20 configurações; janelas variadas, vazias e 0)
#  C   600 trator × implemento grandes (subconjuntos de grades 5×6 a 6×6 e 20 de 6×7/7×6, 26–42 configurações): C1 prazo único, C2 prazos variados
#  D   200 quase trator × implemento (grade 5×6/6×5 + um 3º ativo, uma sequência declarada ou um grupo de 1 unidade): P2 deve cair na busca
import json,random,sys
W=sys.argv[1]; SEM=int(sys.argv[2]) if len(sys.argv)>2 else 20261004; rnd=random.Random(SEM)
def jan_rand(p_vazio=0.15,p_zero=0.04,vals=(1,2,3,4,5,6,8,10,12,15,20)):
    u=rnd.random()
    return '' if u<p_vazio else (0 if u<p_vazio+p_zero else rnd.choice(vals))
def gerais(k):
    n=rnd.randint(2,10); pool=[f'a{j}' for j in range(rnd.randint(2,6))]; pools={}
    if rnd.random()<0.3:
        for g in range(rnd.randint(1,2)): pools[f'g{g}']={'un':rnd.choice([1,1,2,3]),'nome':f'Grupo {g}'}
    tr=rnd.random()<0.1; cf=[]
    for i in range(n):
        c={'id':f'C{i}','nome':f'C{i}','rend':rnd.choice([1,2,3,1.5]) if rnd.random()>0.03 else '','jan':jan_rand(),'ativos':rnd.sample(pool,rnd.randint(0,min(3,len(pool)))),'custo_h':1}
        if rnd.random()<0.2: c['seq']=True
        if rnd.random()<0.3: c['part']=rnd.choice([5,10,20,25,30,40,50])
        if tr and rnd.random()<0.5: c['troca']=rnd.choice([0.5,1,2])
        if pools: c['rec']={g:rnd.choice([0,1,1,2]) for g in pools}
        cf.append(c)
    return {'nome':f'A{k} gerais n={n}','Q':rnd.choice([5,10,20,50,100,200]),'cfgs':cf,'pools':pools,'cat':'A'}
def grade(a,b,keep,janf,partp):
    cf=[]
    for t in range(a):
        for p in range(b):
            if rnd.random()>keep: continue
            c={'id':f'T{t}P{p}','nome':f'T{t}+P{p}','rend':rnd.choice([1,2,3]),'jan':janf(),'ativos':[f't{t}',f'p{p}'],'custo_h':1}
            if rnd.random()<partp: c['part']=rnd.choice([1,2,3,4,5])
            cf.append(c)
    return cf
def medios(k):
    a,b=rnd.randint(2,5),rnd.randint(2,5); cf=grade(a,b,rnd.uniform(0.5,1),lambda:jan_rand(0.15,0.05),rnd.choice([0,0.3,1]))
    while len(cf)<2: cf=grade(a,b,1,lambda:jan_rand(),0)
    return {'nome':f'B{k} grade {a}x{b} n={len(cf)}','Q':rnd.choice([20,50,100,300]),'cfgs':cf,'pools':{},'cat':'B'}
def grandes(k):
    a,b=rnd.choice([(5,6),(6,5),(6,6),(5,6),(6,5)]) if k>=20 else rnd.choice([(6,7),(7,6)])
    unico=k%2==0; J=rnd.choice([5,8,10,12])
    janf=(lambda:('' if rnd.random()<0.08 else J)) if unico else (lambda:jan_rand(0.08,0.0,(2,3,5,8,10,15,20)))
    while True:
        cf=grade(a,b,rnd.uniform(0.8,1),janf,rnd.choice([0,0.5,1]))
        if len(cf)>=26: break
    return {'nome':f'C{k} grade {a}x{b} n={len(cf)} '+('prazo único' if unico else 'prazos variados'),'Q':rnd.choice([300,600,1000,3000]),'cfgs':cf,'pools':{},'cat':'C1' if unico else 'C2'}
def quase(k):
    a,b=rnd.choice([(5,6),(6,5)]); cf=grade(a,b,1,lambda:rnd.choice([10,10,8,'']),rnd.choice([0,1])); pools={}
    m=k%3; i,j=rnd.sample(range(len(cf)),2)
    if m==0: cf[i]['ativos']=cf[i]['ativos']+[cf[j]['ativos'][0] if cf[j]['ativos'][0]!=cf[i]['ativos'][0] else cf[j]['ativos'][1]]
    elif m==1: cf[i]['seq']=True; cf[j]['seq']=True
    else: pools={'op':{'un':1,'nome':'Operador'}}; cf[i]['rec']={'op':1}; cf[j]['rec']={'op':1}
    return {'nome':f'D{k} quase grade {a}x{b} tipo {m}','Q':600,'cfgs':cf,'pools':pools,'cat':'D'}
L=[gerais(k) for k in range(1500)]+[medios(k) for k in range(1000)]+[grandes(k) for k in range(600)]+[quase(k) for k in range(200)]
for k,c in enumerate(L): c['nome']=f'#{k} '+c['nome']
json.dump(L,open(W+'/entradas/aleatorias_s%d.json'%SEM,'w'),ensure_ascii=False); print(len(L),'entradas; semente',SEM)
from collections import Counter; print(Counter(c['cat'] for c in L))
