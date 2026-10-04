import json, sys, os
from fractions import Fraction as F
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(W,'scripts'))
from verif import viavel, agenda_ok
E=json.load(open(f'{W}/entradas/casos_F.json')); AG=json.load(open(f'{W}/entradas/agendas_esperadas.json'))
VS=['ee4f954','04bf6f2','2e31588','P0nR23','P1','P2','P2nR23']
R={v:(json.load(open(f'{W}/brutos/F_js_{v}.json'))['res'],json.load(open(f'{W}/brutos/F_py_{v}.json'))['res']) for v in VS}
f4=lambda x: f'{float(x):.4f}'.rstrip('0').rstrip('.')
for k,e in E.items():
    ids=[c['id'] for c in e['cfgs']]
    print(f'### {k}  (fonte: {e["fonte"]})')
    q,err=agenda_ok(e,AG[k]); tot=sum(q.values(),F(0)); ok,why=viavel(e,[q[i]/F(str(c['rend'])) for i,c in zip(ids,e['cfgs'])])
    print(f'ESPERADO (agenda): {json.dumps(AG[k])} → q {", ".join(f"{i}={q[i]}" for i in ids)}; total {tot} ({f4(tot)} ha); erros_agenda={err}; verificador={ok} {why}')
    for v in VS:
        j,p=R[v][0][k],R[v][1][k]
        par=all(abs(float(a)-float(F(b)))<=1e-9*max(1,abs(float(F(b))) ) for a,b in zip(j['q']+[j['alocado'],j['saldo'],j['deficit']],p['q']+[p['alocado'],p['saldo'],p['deficit']])) and j['conflito']==p['conflito'] and j['motivos']==p['motivos']
        vj=viavel(e,j['h'],tol=1e-7); vp=viavel(e,[F(x) for x in p['h']])
        print(f'- {v}: q[{", ".join(f"{i}={f4(x)}" for i,x in zip(ids,j["q"]))}] (Py: {", ".join(p["q"])}) · alocado {f4(j["alocado"])} (Py {p["alocado"]}) · saldo {f4(j["saldo"])} · conflito {j["conflito"]} · déficit {f4(j["deficit"])} h · decorrido {f4(j["decorrido"]) if j["decorrido"] is not None else None} · viável JS={vj[0]}{(" "+vj[1]) if vj[1] else ""} Py={vp[0]}{(" "+vp[1]) if vp[1] else ""} · paridade JS×Py={par}')
        print('    motivos: '+' | '.join(j['motivos']))
    print()
