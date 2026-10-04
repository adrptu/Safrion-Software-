# resumo das 3 300 entradas aleatórias por variante: violações, novas em relação a P0, conflito/saldo, θ*, igualdade com P0 onde P0 conferiu
import json,sys
from collections import Counter
W=sys.argv[1]; VS=sys.argv[2:]
L=json.load(open(W+'/entradas/aleatorias_s20261004.json'))
def ld(p): return {d['k']:d for d in map(json.loads,open(p))}
S={n:ld(W+f'/brutos/aleat_js_{n}.jsonl') for n in VS}; V={n:ld(W+f'/brutos/verif_aleat_{n}.jsonl') for n in VS}
P0v={k for k,d in V['P0'].items() if d['violacoes']}
for n in VS:
    viol={k for k,d in V[n].items() if d['violacoes']}; novas=sorted(viol-P0v); sumiram=sorted(P0v-viol)
    semconf=[k for k in viol if not S[n][k]['conflito']]
    ths=[V[n][k]['theta'] for k in viol]
    cam=Counter(S[n][k]['caminho'] for k in S[n]); est=sum(1 for k in S[n] if any(z[2] is None for z in S[n][k]['bl']))
    lb=sum(1 for k in S[n] if any(z[2]=='linhaBip' for z in S[n][k]['bl']))
    # igualdade com P0 onde P0 conferiu (nenhuma busca estourou)
    conf=[k for k in S['P0'] if not any(z[2] is None for z in S['P0'][k]['bl'])]
    dif=[k for k in conf if max([abs((a or 0)-(b or 0)) for a,b in zip(S[n][k]['q'],S['P0'][k]['q'])]+[0])>1e-9 or S[n][k]['motivos']!=S['P0'][k]['motivos']]
    ms=sorted(S[n][k]['ms'] for k in S[n])
    print(json.dumps(dict(variante=n,entradas=len(S[n]),com_violacao=len(viol),por_categoria=dict(Counter(L[k]['cat'] for k in viol)),
      novas_vs_P0=len(novas),novas_por_categoria=dict(Counter(L[k]['cat'] for k in novas)),exemplos_novas=novas[:6],deixaram_de_violar=len(sumiram),
      violacao_sem_conflito=len(semconf),exemplos_sem_conflito=sorted(semconf)[:6],theta_min=min(ths) if ths else None,
      caminhos=dict(cam),entradas_com_estouro_do_buraco=est,entradas_com_linhaBip=lb,
      diferencas_vs_P0_onde_P0_conferiu=len(dif),exemplos_dif=dif[:5],ms_mediana=ms[len(ms)//2],ms_max=ms[-1],ms_max_k=max(S[n],key=lambda k:S[n][k]['ms'])),ensure_ascii=False))
