# Entradas aleatórias sintéticas com partes fixas (pelo menos uma por entrada), troca 0. Semente fixa.
# Uso: python3 gera_aleatorias.py <semente> <n> <saida.json>; grava também as variantes de monotonicidade (janela ×2 numa configuração; Q ×2).
import random, json, sys
sem,n,sai=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]; R=random.Random(sem)
E=[]; MJ=[]; MQ=[]
while len(E)<n:
    k=R.randint(2,6); modo=R.choice(['at','seq','misto','misto'])
    cs=[]
    for i in range(k):
        c={'id':f'c{i}','nome':f'c{i}','rend':R.choice([0.5,1,2,3]),'custo_h':1,'jan':R.choice([0,5,10,10,20,20,50,100,100,'','']),'part':R.choice([5,10,20,30,50,'',''])}
        if modo=='at': c['ativos']=['a01']
        elif modo=='seq': c['seq']=True
        else:
            at=[a for a in ['a1','a2','a3'] if R.random()<0.4]
            if at: c['ativos']=at
            if R.random()<0.35: c['seq']=True
            if R.random()<0.3: c['rec']={'plant':1}
        cs.append(c)
    if all(c['part']=='' for c in cs): cs[R.randrange(k)]['part']=R.choice([10,20,30,50])
    e={'Q':R.choice([100,500,1000]),'cfgs':cs}
    if modo=='misto': e['pools']={'plant':{'un':1,'nome':'Plantadeiras'}}
    E.append(e)
    fin=[i for i,c in enumerate(cs) if c['jan'] not in ('',)]
    j=json.loads(json.dumps(e))
    if fin:
        i=R.choice(fin); j['cfgs'][i]['jan']=(cs[i]['jan']*2 if cs[i]['jan']>0 else 10); j['mono']=f"jan de {cs[i]['id']}: {cs[i]['jan']} → {j['cfgs'][i]['jan']}"
    else: j['mono']='sem janela finita (igual)'
    MJ.append(j)
    m=json.loads(json.dumps(e)); m['Q']=e['Q']*2; MQ.append(m)
json.dump(E,open(sai,'w')); json.dump(MJ,open(sai.replace('.json','_janx2.json'),'w')); json.dump(MQ,open(sai.replace('.json','_Qx2.json'),'w'))
print(len(E),'entradas; semente',sem)
