# autoteste do verificador (semente 7): (1) V3b e V3e dão o mesmo θ* em grades pequenas com horas e prazos aleatórios;
# (2) V2 é necessária: se θ* ≥ 1 nenhum corte V2 pode falhar; (3) um cronograma construído (EDF numa máquina só, em série) sempre passa
import random,math,sys,json
sys.path.insert(0,sys.path[0]); import verif
rnd=random.Random(7); dif=0; inc=0; ser=0; N=500
for k in range(N):
    a,b=rnd.randint(2,4),rnd.randint(2,4); cf=[]
    for t in range(a):
        for p in range(b):
            if rnd.random()<0.75: cf.append({'id':f'{t}{p}','rend':1,'jan':rnd.choice([1,2,3,4,5,6,8]),'ativos':[f't{t}',f'p{p}']})
    if len(cf)<2: continue
    h=[rnd.choice([0,0.5,1,1.5,2,3]) for _ in cf]
    caso={'Q':sum(h),'cfgs':cf,'pools':{}}; s={'q':h,'saldo':0}
    it,P=verif.prep(caso); at=[i for i in range(len(cf)) if h[i]>1e-7]
    if not at: continue
    tb=verif.v3b(it,h,at); te=verif.v3e(it,P,h,at)
    if abs(tb-te)>1e-6*max(1,abs(tb)): dif+=1; print('DIFERE',k,tb,te)
    v,th,mo=verif.verifica(caso,s)
    if th>=1-1e-7 and any(x.startswith('V2') for x in v): inc+=1; print('V2 falha com θ≥1',k,v)
    # cronograma em série (uma por vez, EDF): é executável por construção; escala h para caber
    order=sorted(range(len(cf)),key=lambda i:cf[i]['jan']); tt=0; hs=[0]*len(cf)
    for i in order:
        x=min(h[i],max(0,cf[i]['jan']-tt)); hs[i]=x; tt+=x
    v2,th2,_=verif.verifica({'Q':sum(hs),'cfgs':cf,'pools':{}},{'q':hs,'saldo':0})
    if v2: ser+=1; print('SÉRIE REPROVADA',k,v2)
print(json.dumps({'instancias':N,'V3b≠V3e':dif,'V2 falha com θ*≥1':inc,'cronograma em série reprovado':ser}))
