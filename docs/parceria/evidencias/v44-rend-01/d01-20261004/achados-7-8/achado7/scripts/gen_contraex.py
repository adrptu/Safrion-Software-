# contraexemplo mínimo (sintético) do corte por prazo com prazos distintos em grafo perfeito (linhas de bipartido); rend 1 → q = h
import json,sys
W=sys.argv[1]
H=[('A','t2','p0',2,2),('B','t0','p0',10,4),('C','t0','p1',10,3),('D','t0','p2',10,3),('E','t1','p1',2,1),('F','t1','p2',2,1),('G','t4','p2',3,1.5)]
Q=sum(x[4] for x in H)   # 15,5 ha
cf=[{'id':n,'nome':f'{n} ({t}+{p})','rend':1,'jan':j,'part':h*100/Q,'ativos':[t,p],'custo_h':1} for n,t,p,j,h in H]
C=[{'nome':'contraexemplo 7 configurações, prazos 2/3/10, partes fixas (rend 1)','Q':Q,'cfgs':cf,'pools':{}}]
# o mesmo pelo rendimento (sem %): o código divide pelo rendimento até as janelas
C.append({'nome':'contraexemplo 7 configurações, sem %, Q=15,5','Q':Q,'cfgs':[{k:v for k,v in c.items() if k!='part'} for c in cf],'pools':{}})
json.dump(C,open(W+'/entradas/contraexemplo.json','w'),ensure_ascii=False,indent=0); print('Q',Q,[round(c['part'],6) for c in cf])
