import sys,copy
sys.path.insert(0,sys.argv[1]); import raiox_gabarito as g
def ep(fator,safra='s1',sem=1,ruido=1):
    dias=[dict(wk=1.05,clima=1,falta=0.2,n14=8+d%3,k14=15,imigracao=.01,chuva=12 if d%9==0 else 0,ruido_obs=ruido,ruido_app=.5,eff=.6,clima_observado=None) for d in range(40)]
    return dict(cenario='c',safra=safra,semente=sem,talhao='T',alvo='A',fator=fator,x0=2,cap=1000,nc=5,fx={'def':.1,'n':.05,'k':.02,'lav':.8},
                dias=dias,observacoes=list(range(0,40,7)),politica=dict(delay=2,gatilho=1,resid=3))
out=g.gerar([ep('n'),ep('k'),ep('n','s2'),ep('k','s2')])
E=out['entrada']; print('R1 entradas:',len(E),'referências:',sorted({e.get('agenda_referencia') for e in E}))
# a entrada é o mundo factual (fator ligado): compara com o replay ligado
print('R1 obs = mundo ligado:', all(len(e['obs'])==6 for e in E))
try:
    g.gerar([ep('n'),dict(ep('k'),dias=[dict(d,ruido_obs=1.3) for d in ep('k')['dias']])]+[ep('n','s2'),ep('k','s2')]); print('R1 mundo divergente: ACEITO (defeito)')
except ValueError as e: print('R1 mundo divergente recusado:',e)
t=dict(id='T',antes=10,depois=4,antes_dia=9,depois_dia=17,unidade='u',protocolo='p')
c=dict(id='C',antes=10,depois=40,antes_dia=1,depois_dia=30,unidade='u',protocolo='p')
print('R2:',g.eficacia_referencia(t,[c],10,30))
c2=dict(c,antes_dia=9,depois_dia=17); print('R2 datas iguais:',g.eficacia_referencia(t,[c2],10,30)['estado'])
r=[dict(id='x',versao=2,fonte='f',tipo='fato',dia=1,disponivel_em=2,protocolo='p',unidade='u',valor=5),
   dict(id='x',versao=1,fonte='f',tipo='fato',dia=1,disponivel_em=3,protocolo='p',unidade='u',valor=9)]
try: print('R4:',g.selecionar_disponiveis(r,5,'p','u')['registros'])
except ValueError as e: print('R4 recusado:',e)
print('R4 corte 2 (versão 1 ainda indisponível):',[x['versao'] for x in g.selecionar_disponiveis(r,2,'p','u')['registros']])
# R3: populações diferentes entre agendas
rr=lambda d,ss: [dict(delta=d,identificavel=True,semente=i) for i in ss]
print('R3:',g.consolidar({'s1':{'ligado':rr(.3,range(20)),'desligado':rr(.3,range(1,21))},'s2':{'ligado':rr(.3,range(20)),'desligado':rr(.3,range(20))}})['classe'])
