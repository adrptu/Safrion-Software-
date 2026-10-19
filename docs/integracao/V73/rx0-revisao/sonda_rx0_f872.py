import sys, math, copy
sys.path.insert(0, sys.argv[1]); import raiox_gabarito as g
def ep(fator, safra='s1', sem=1):
    dias=[dict(wk=1.05,clima=1,falta=0.2,n14=8+d%3,k14=15,imigracao=.01,chuva=12 if d%9==0 else 0,ruido_obs=1,ruido_app=.5,eff=.6,clima_observado=None) for d in range(40)]
    return dict(cenario='c',safra=safra,semente=sem,talhao='T',alvo='A',fator=fator,x0=2,cap=1000,nc=5,fx={'def':.1,'n':.05,'k':.02,'lav':.8},
                dias=dias,observacoes=list(range(0,40,7)),politica=dict(delay=2,gatilho=1,resid=3))
pop=g.expandir_populacao([ep('n')],16)
def corr(a,b):
    ma=sum(a)/len(a); mb=sum(b)/len(b); va=sum((x-ma)**2 for x in a); vb=sum((y-mb)**2 for y in b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)
gat=[p['politica']['gatilho'] for p in pop]
mx=max(max(abs(corr(gat,[p['dias'][d]['n14'] for p in pop])),abs(corr(gat,[p['dias'][d]['k14'] for p in pop]))) for d in range(40))
print('A1 maior |corr(gatilho, n14 ou k14)| no mesmo dia, 16 talhões:', round(mx,2))
e=g.gerar([ep('n'),ep('k'),ep('n','s2'),ep('k','s2')])['entrada'][0]
bad=copy.deepcopy(e); bad['obs'][1]['v']=float('nan')
s0=g.medir_suporte([e])[0]; s1=g.medir_suporte([bad])[0]
print('A2 NaN numa observação: sem erro; excluídas', s0['excluidas'], '->', s1['excluidas'], '(dado malformado contado como exclusão por regra)')
print('A3 limites do ENSAIO (só proporções):', g.ENSAIO['limites'], '· denominador mínimo por limite:', [k for k in g.ENSAIO if k.startswith('denominador')] or 'nenhum')
