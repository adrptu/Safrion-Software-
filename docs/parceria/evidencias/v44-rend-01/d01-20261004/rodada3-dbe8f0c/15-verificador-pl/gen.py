import json, random, sys
rnd=random.Random(int(sys.argv[2]) if len(sys.argv)>2 else 7)
N=int(sys.argv[1]) if len(sys.argv)>1 else 3000
RV=[0.5,1,1.5,2,2.5,3,4]; JV=[1,2,3,4,5,6,8,10,12]; TV=[0.25,0.5,1,2]; PV=[5,10,20,25,30,40,50,60]
ATV=['T1','T2','T3','I1','I2','I3']
def jan():
    u=rnd.random()
    if u<0.28: return None
    if u<0.36: return 0
    return rnd.choice(JV)
def base(i,fam,notroca=False):
    c={'id':'c%d'%i,'nome':'K%d'%i,'custo_h':1}
    u=rnd.random(); c['rend']=rnd.choice(RV) if u>0.04 else rnd.choice([None,0])
    if rnd.random()<0.3: c['part']=rnd.choice(PV)
    j=jan()
    if j is not None: c['jan']=j
    if not notroca and rnd.random()<0.35: c['troca']=rnd.choice(TV)
    return c
cases=[]
for n_ in range(N):
    fam=rnd.choice(['geral','geral','anel','anel','rook','path','semtroca','semtroca','fixas'])
    notroca=fam in ('semtroca','path','rook') and rnd.random()<0.7
    pools={}
    if fam in ('geral','fixas') or rnd.random()<0.25:
        if rnd.random()<0.7: pools['g1']={'un':rnd.choice([1,2,2,3,4]),'nome':'Tratores'}
        if rnd.random()<0.5: pools['g2']={'un':rnd.choice([1,1,2]),'nome':'Plantadeiras'}
    if fam=='anel':
        L=rnd.choice([5,7]); n=L+rnd.choice([0,0,1,2])
        cs=[base(i,fam,notroca) for i in range(n)]
        for i in range(L): cs[i]['ativos']=['e%d'%i,'e%d'%((i+1)%L)]
        for i in range(L,n): cs[i]['ativos']=[rnd.choice(['e%d'%k for k in range(L)])] if rnd.random()<0.7 else []
        if rnd.random()<0.4:   # janelas todas finitas no anel
            for i in range(L): cs[i]['jan']=rnd.choice(JV)
        elif rnd.random()<0.5:  # um sem janela
            for i in range(L): cs[i]['jan']=rnd.choice(JV)
            cs[rnd.randrange(L)].pop('jan',None)
    elif fam=='rook':
        T=rnd.choice([2,3]); I=rnd.choice([2,3]); pairs=[(t,i) for t in range(T) for i in range(I)]; rnd.shuffle(pairs); n=rnd.randint(3,min(9,len(pairs)))
        cs=[base(k,fam,notroca) for k in range(n)]
        for k in range(n): cs[k]['ativos']=['T%d'%pairs[k][0],'I%d'%pairs[k][1]]
    elif fam=='path':
        n=rnd.randint(3,7); cs=[base(k,fam,notroca) for k in range(n)]
        for k in range(n): cs[k]['ativos']=['e%d'%k,'e%d'%(k+1)]
        for k in range(n):
            if rnd.random()<0.8: cs[k]['jan']=rnd.choice(JV)
    else:
        n=rnd.randint(2,9); cs=[base(k,fam,notroca) for k in range(n)]
        for c in cs:
            if rnd.random()<0.25: c['seq']=True
            k=rnd.choice([0,0,1,1,2]); a=rnd.sample(ATV,k)
            if a: c['ativos']=a
            if pools:
                rec={}
                for g in pools:
                    if rnd.random()<0.6: rec[g]=rnd.choice([1,1,2])
                if rec: c['rec']=rec
        if fam=='fixas':
            for c in cs:
                if rnd.random()<0.7: c['part']=rnd.choice(PV)
                if rnd.random()<0.7: c['jan']=rnd.choice(JV)
    if fam in ('anel','rook','path') and rnd.random()<0.3:
        for c in cs: c['seq']=rnd.random()<0.2
    Q=rnd.choice([1,2,4,5,8,10,20,30,50,100])
    cases.append({'tag':fam,'Q':Q,'cfgs':cs,'pools':pools or None})
json.dump(cases,open(sys.argv[3] if len(sys.argv)>3 else 'cases.json','w'))
print(len(cases))
