# bateria adversarial do teste de buraco (sintética, semente registrada): grafos de 20–32 configurações; cada aresta = um ativo compartilhado
import json,random,sys,itertools
W=sys.argv[1]; SEM=20261004; rnd=random.Random(SEM)
def de_arestas(nome,n,E,jan=lambda i:10,Q=None,part=False):
    at=[[] for _ in range(n)]
    for a,b in E: z=f'e{min(a,b)}_{max(a,b)}'; at[a].append(z); at[b].append(z)
    cf=[]
    for i in range(n):
        c={'id':f'K{i}','nome':f'K{i}','rend':1+(i%3),'jan':jan(i),'ativos':at[i],'custo_h':1}
        if part: c['part']=100/n
        cf.append(c)
    return {'nome':nome,'Q':Q or 100*n,'cfgs':cf,'pools':{}}
def grade_ti(a,b,jan=lambda t,p:10):
    cf=[{'id':f'T{t}P{p}','nome':f'T{t}+P{p}','rend':2,'jan':jan(t,p),'part':100/(a*b),'ativos':[f't{t}',f'p{p}'],'custo_h':1} for t in range(a) for p in range(b)]
    return cf
C=[]
for a,b in ((5,6),(6,5),(6,6),(5,7),(7,5),(4,8),(8,4)): C.append({'nome':f'trator×implemento {a}x{b} jan 10','Q':600,'cfgs':grade_ti(a,b),'pools':{}})
for a,b in ((5,6),(6,6)):
    js=[rnd.choice([2,3,5,8,10,15,20]) for _ in range(a*b)]
    C.append({'nome':f'trator×implemento {a}x{b} janelas variadas (todas finitas)','Q':600,'cfgs':grade_ti(a,b,lambda t,p,js=js,b=b:js[t*b+p]),'pools':{}})
for n in (20,24,30,21,25,29): C.append(de_arestas(f'anel C{n}',n,[(i,(i+1)%n) for i in range(n)]))
for n in (20,24,30,21,25): C.append(de_arestas(f'complemento do anel C{n}',n,[(i,j) for i in range(n) for j in range(i+1,n) if (j-i)%n not in (1,n-1)]))
for ps in ((5,)*6,(6,)*5,(3,)*10,(10,)*3,(2,)*15):
    idx=[k for k,s in enumerate(ps) for _ in range(s)]; n=len(idx)
    C.append(de_arestas('multipartido completo '+'×'.join(map(str,ps)),n,[(i,j) for i in range(n) for j in range(i+1,n) if idx[i]!=idx[j]]))
for n in (20,30): C.append(de_arestas(f'cadeia P{n}',n,[(i,i+1) for i in range(n-1)]))
for a,b in ((4,5),(5,5),(5,6)):
    v=lambda r,c:r*b+c; E=[(v(r,c),v(r,c+1)) for r in range(a) for c in range(b-1)]+[(v(r,c),v(r+1,c)) for r in range(a-1) for c in range(b)]
    C.append(de_arestas(f'malha {a}x{b}',a*b,E))
for n in (20,25,30):
    for p in (0.1,0.2,0.3,0.5,0.7,0.9):
        C.append(de_arestas(f'aleatório G({n},{p})',n,[(i,j) for i in range(n) for j in range(i+1,n) if rnd.random()<p]))
for p in (0.2,0.4):
    C.append(de_arestas(f'bipartido aleatório 15+15 p={p}',30,[(i,j) for i in range(15) for j in range(15,30) if rnd.random()<p]))
C.append(de_arestas('hipercubo Q5',32,[(i,i^(1<<k)) for i in range(32) for k in range(5) if i<i^(1<<k)]))
for c in json.load(open(W+'/entradas/perf_casos_prerev7.json')): c=dict(c); c['nome']='perf_casos: '+c['nome']; c['pools']=c.get('pools') or {}; C.append(c)
json.dump(C,open(W+'/entradas/adversariais.json','w'),ensure_ascii=False); print(len(C),'casos; semente',SEM)
