import sys, math, copy, json
sys.path.insert(0, sys.argv[1]); import raiox_gabarito as g
def ep(fator, safra='s1', sem=1):
    dias=[dict(wk=1.05,clima=1,falta=0.2,n14=8+d%3,k14=15,imigracao=.01,chuva=12 if d%9==0 else 0,ruido_obs=1,ruido_app=.5,eff=.6,clima_observado=None) for d in range(40)]
    return dict(cenario='c',safra=safra,semente=sem,talhao='T',alvo='A',fator=fator,x0=2,cap=1000,nc=5,fx={'def':.1,'n':.05,'k':.02,'lav':.8},
                dias=dias,observacoes=list(range(0,40,7)),politica=dict(delay=2,gatilho=1,resid=3))
def corr(a,b):
    ma=sum(a)/len(a); mb=sum(b)/len(b); va=sum((x-ma)**2 for x in a); vb=sum((y-mb)**2 for y in b)
    return 0.0 if va==0 or vb==0 else sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)
for n in (8,16,20):
    pop=g.expandir_populacao([ep('n')],n); gat=[p['politica']['gatilho'] for p in pop]
    mx=max(max(abs(corr(gat,[p['dias'][d]['n14'] for p in pop])),abs(corr(gat,[p['dias'][d]['k14'] for p in pop]))) for d in range(40))
    nk=sorted(set((round(p['dias'][0]['n14'],3),round(p['dias'][0]['k14'],3),p['politica']['gatilho']) for p in pop))
    print(f'A1 {n} talhões: maior |corr(gatilho, n14 ou k14)| = {mx:.3f}; combinações distintas (n14,k14,gatilho) no dia 0 = {len(nk)}')
try:
    g.expandir_populacao([ep('n')],6); print('A1b 6 talhões: aceito (esperado: recusa)')
except ValueError as e: print('A1b 6 talhões: recusa ·', str(e)[:120])
e=g.gerar([ep('n'),ep('k'),ep('n','s2'),ep('k','s2')])['entrada'][0]
for rot,val in (('NaN',float('nan')),('Infinity',float('inf')),('None',None),('negativo',-1.0),('texto','3')):
    bad=copy.deepcopy(e); bad['obs'][1]['v']=val
    try: s=g.medir_suporte([bad])[0]; print(f'A2 {rot}: sem erro · excluídas {s.get("excluidas")}')
    except (ValueError,TypeError) as x: print(f'A2 {rot}: recusa ·', str(x)[:100])
s0=g.medir_suporte([e])[0]; print('A2 entrada válida: excluídas', s0.get('excluidas'), '· motivos', {k:v for k,v in s0.items() if 'motivo' in k or 'exclu' in k})
print('A3 ENSAIO:', json.dumps({k:v for k,v in g.ENSAIO.items() if k!='hash'}, ensure_ascii=False)[:900])
# d1f6fa0 (A2, ajuste 2): motivos coexistentes contam a janela uma vez e cada motivo uma vez
base=copy.deepcopy(e); base['apps']=[]; base['nc']=5
def jan(obs, apps):
    x=copy.deepcopy(base); x['obs']=[dict(day=d,v=v) for d,v in obs]; x['apps']=[dict(day=d) for d in apps]; return g.medir_suporte([x])[0]
for rot,obs,apps in (('3 motivos numa janela',[(1,0.1),(3,1.0)],[2]),
                     ('2 motivos (abaixo NC + intervalo)',[(1,0.1),(30,1.0)],[]),
                     ('1 motivo (aplicação)',[(1,2.0),(8,3.0)],[5]),
                     ('nenhum motivo',[(1,2.0),(8,3.0)],[])):
    s=jan(obs,apps); print(f'A2b {rot}: excluídas {s["excluidas"]} · janelas {s["janelas"]} · motivos {s["exclusoes_por_motivo"]}')
