import sys,math,json
sys.path.insert(0,sys.argv[1]); import raiox_gabarito as g
def ep(fator,sem=1):
    dias=[dict(wk=1.05,clima=1,falta=0.2,n14=8+d%3,k14=15,imigracao=.01,chuva=12 if d%9==0 else 0,ruido_obs=1,ruido_app=.5,eff=.6,clima_observado=None) for d in range(40)]
    return dict(cenario='c',safra='s1',semente=sem,talhao='T',alvo='A',fator=fator,x0=2,cap=1000,nc=5,fx=dict(def_=0,n=.05,k=.02,lav=.8,**{'def':.1}),
                dias=dias,observacoes=list(range(0,40,7)),politica=dict(delay=2,gatilho=1,resid=3))
out=g.gerar([ep('n'),ep('k'),dict(ep('n'),safra='s2'),dict(ep('k'),safra='s2')])
E=out['entrada']; print('entradas',len(E),[ (e['agenda_referencia'],) for e in E])
lig=[e for e in E if e['agenda_referencia']=='ligado']; des=[e for e in E if e['agenda_referencia']=='desligado']
print('ligado: obs iguais entre fatores n e k =', lig[0]['obs']==lig[1]['obs'], 'series iguais =', lig[0]['series']==lig[1]['series'])
print('desligado(n) obs != ligado obs =', des[0]['obs']!=lig[0]['obs'], '; series iguais =', des[0]['series']==lig[0]['series'])
print('ligado v:', [round(o['v'],2) for o in lig[0]['obs']]); print('desl n v:', [round(o['v'],2) for o in des[0]['obs']])
# HT: controle com datas diferentes é aceito
t=dict(id='T',antes=10,depois=4,antes_dia=9,depois_dia=17,unidade='u',protocolo='p')
c=dict(id='C',antes=10,depois=40,antes_dia=1,depois_dia=30,unidade='u',protocolo='p')
print('HT datas diferentes:', g.eficacia_referencia(t,[c],10,30))
# versão não monótona
r=[dict(id='x',versao=2,fonte='f',tipo='fato',dia=1,disponivel_em=2,protocolo='p',unidade='u',valor=5),
   dict(id='x',versao=1,fonte='f',tipo='fato',dia=1,disponivel_em=3,protocolo='p',unidade='u',valor=9)]
print('versão:', g.selecionar_disponiveis(r,5,'p','u')['registros'])
