import json, random, sys
rnd=random.Random(int(sys.argv[2])); N=int(sys.argv[1]); cases=[]
for _ in range(N):
    fam=sys.argv[4]
    if fam=='rook':
        T=rnd.choice([2,3]); I=rnd.choice([2,3]); pairs=[(t,i) for t in range(T) for i in range(I)]; rnd.shuffle(pairs); n=rnd.randint(4,min(7,len(pairs)))
        cs=[{'id':'c%d'%k,'nome':'T%d+I%d'%pairs[k],'rend':rnd.choice([1,1.5,2,3]),'custo_h':1,'ativos':['T%d'%pairs[k][0],'I%d'%pairs[k][1]]} for k in range(n)]
    else:   # anel C5/C7 com 1 sem janela
        L=rnd.choice([5,7]); cs=[{'id':'c%d'%k,'nome':'K%d'%k,'rend':rnd.choice([1,1.5,2,3]),'custo_h':1,'ativos':['e%d'%k,'e%d'%((k+1)%L)]} for k in range(L)]
    for c in cs:
        if rnd.random()<0.85: c['jan']=rnd.choice([1,2,3,4,5,6])
    if fam!='rook':
        for c in cs: c['jan']=rnd.choice([1,2,3,4,5,6])
        cs[rnd.randrange(len(cs))].pop('jan')
    cases.append({'tag':fam,'Q':rnd.choice([1,2,3,4,5,6,8,10,12,15]),'cfgs':cs,'pools':None})
json.dump(cases,open(sys.argv[3],'w')); print(len(cases))
