# casos principais do achado 7 (sintéticos): grade trator × implemento, como no achado (rend 2, jan 10, partes 100/n %, Q=600)
import json,sys
W,PERF=sys.argv[1],sys.argv[2]
def grade(nt,npl,jan=10,rend=2,Q=600,semjan=(),part=True):
    n=nt*npl; cf=[]
    for t in range(nt):
        for p in range(npl):
            c={'id':f'T{t}P{p}','nome':f'T{t}+P{p}','rend':rend,'jan':'' if (t,p) in semjan else jan,'ativos':[f't{t}',f'p{p}'],'custo_h':1}
            if part: c['part']=100/n
            cf.append(c)
    return cf
C=[]
C.append({'nome':'5x6 partes fixas, todas 10 h','Q':600,'cfgs':grade(5,6),'pools':{}})
C.append({'nome':'6x5 partes fixas, todas 10 h','Q':600,'cfgs':grade(6,5),'pools':{}})
C.append({'nome':'5x6 T4+P5 sem janela (prestador)','Q':600,'cfgs':grade(5,6,semjan={(4,5)}),'pools':{}})
c9=json.load(open(PERF))[9]; assert c9['nome']=='trator×implemento 5×6 janelas variadas'
C.append({'nome':'caso 9: 5x6 janelas variadas (perf_casos #9)','Q':c9['Q'],'cfgs':c9['cfgs'],'pools':c9.get('pools') or {}})
for a,b in ((4,5),(4,6),(5,5)): C.append({'nome':f'controle {a}x{b} partes fixas, todas 10 h','Q':600,'cfgs':grade(a,b),'pools':{}})
json.dump(C,open(W+'/entradas/casos_principais.json','w'),ensure_ascii=False,indent=0)
# extras (só para as propostas): grades maiores
E=[]
for a,b in ((6,6),(5,7),(7,5),(6,7),(7,6),(7,7),(8,8),(10,10)): E.append({'nome':f'extra {a}x{b} partes fixas, todas 10 h','Q':600,'cfgs':grade(a,b),'pools':{}})
E.append({'nome':'extra 6x6 T5+P5 sem janela','Q':600,'cfgs':grade(6,6,semjan={(5,5)}),'pools':{}})
json.dump(E,open(W+'/entradas/casos_extras.json','w'),ensure_ascii=False,indent=0)
print(len(C),'principais;',len(E),'extras')
