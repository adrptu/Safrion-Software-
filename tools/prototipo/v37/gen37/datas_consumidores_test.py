"""EX57 F0c: dados sintéticos, batch/cache e âncora ausente dos consumidores."""
import copy
import dados2 as D
import datas_atividade as DA

original=DA.calcular_lote
chamadas=[]
def medir(entradas):
    chamadas.append(len(entradas))
    return original(entradas)
DA.calcular_lote=medir
D._DATAS_ATIVIDADE.clear()
for cs in D.CULTIVOS.values():
    for c in cs:
        if not c['plano']: continue
        for a in D.PLANO[c['plano']]['atividades']: D.data_atividade(c,a)
assert len(chamadas)==1, chamadas
print('OK catálogo inteiro usa um lote; leituras seguintes usam recibo por conteúdo', chamadas)
p=dict(id='TESTE-SEM-COLHEITA',atividades=[dict(nome='Após',op='Adubar',g=dict(tipo='DAPC',dias=2))])
D.PLANO[p['id']]=p
c=dict(id='test',plano=p['id'],plantio='2026-10-01',colheita=None)
a=p['atividades'][0]
assert D.data_atividade(c,a) is None
c['colheita']='2026-11-01'
assert D.data_atividade(c,a).isoformat()=='2026-11-03'
c['colheita']='2026-12-01'
assert D.data_atividade(c,a).isoformat()=='2026-12-03'
assert D.classe_oc(None,-1,'2026-01-01','2026-12-31')=='fora'
assert D.falta_a_partir([(None,100),('2026-11-01',3)],5,[]) is None
assert D.falta_a_partir([(None,100),('2026-11-01',6)],5,[])=='2026-11-01'
print('OK ausência não vira plantio/data; edição invalida cache; falta datada exclui ausência')

import ocupacao as OC
pl=dict(id='P',cultura='Teste',atividades=[dict(nome='Após',op='Adubação',g=dict(tipo='DAPC',dias=2)),dict(nome='Antes',op='Adubação',g=dict(tipo='DANC',dias=3))])
ctx=OC.ctx_de({'Teste':'Anual'},[],[pl])
plantio=OC.dia('2026-10-01')
pend=[]
assert OC.datas_validas(ctx,plantio,'P',plantio,plantio+365,None,pend)==([],[])
assert pend==[('ancora_ausente','Após','DAPC'),('ancora_ausente','Antes','DANC')]
assert OC.fim_estimado(ctx,'Teste','',plantio) is None
assert [OC.iso(x[2]) for x in OC.atividades(ctx,plantio,'P',OC.dia('2026-11-01'))]==['2026-11-03','2026-10-29']
print('OK ocupação Python: pendências explícitas, ausência fora da ordenação, datas canônicas')

OC._datas_plano.cache_clear()
antes=len(chamadas)
for _ in range(20): OC.atividades(ctx,plantio,'P')
assert len(chamadas)==antes+1
pl['atividades'][0]['g']['dias']=4
assert OC.atividades(ctx,plantio,'P',OC.dia('2026-11-01'))[0][2]==OC.dia('2026-11-05')
assert len(chamadas)==antes+2
saida=OC.atividades(ctx,plantio,'P')
saida.clear()
assert len(OC.atividades(ctx,plantio,'P'))==2
assert OC._datas_plano.cache_info().maxsize==2048
print('OK cache ocupação: 20 consultas/1 lote, edição invalida, saída isolada, limite2048')

o=OC.mk(ctx,dict(id='c',saf='S',faz='F',faixa='T',tipo='Talhão inteiro',area=1,cult='Teste',plantio='2026-10-01',plano='P'),dict(id='S',ini='2026-01-01',fim='2026-12-31'))
assert o['fim'] is None and o['classe']=='semdata'
assert OC.P(ctx,o)==OC.INF
print('OK plano sem âncora não inventa fim nem liberação confirmada')
