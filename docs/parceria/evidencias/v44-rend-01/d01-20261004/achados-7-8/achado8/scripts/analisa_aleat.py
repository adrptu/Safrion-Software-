# Análise das 6 000 entradas aleatórias: viabilidade (verificador independente, JS com tolerância 1e-7 e Python exato),
# atende mais/menos que P0 (2e31588), maior perda/ganho, monotonicidade (janela ×2 numa configuração; Q ×2), paridade JS×Python, tempo.
import json, sys, os
from fractions import Fraction as F
W=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(W,'scripts'))
from verif import viavel
E=json.load(open(f'{W}/entradas/aleat.json')); EJ=json.load(open(f'{W}/entradas/aleat_janx2.json')); EQ=json.load(open(f'{W}/entradas/aleat_Qx2.json'))
L=lambda v,f,l: json.load(open(f'{W}/brutos/R_{l}_{v}_{f}.json'))
D={v:{f:{l:L(v,f,l) for l in ('js','py')} for f in ('aleat','aleat_janx2','aleat_Qx2')} for v in ('P0','P1','P2')}
N=len(E); out={'n':N,'semente':20261004}
def near(a,b): return abs(float(a)-float(F(b)))<=1e-9*max(1.0,abs(float(F(b))))
ex={}
for v in ('P0','P1','P2'):
    s=dict(inviavel_js=0,inviavel_py=0,paridade_falha=0,mais_que_P0=0,menos_que_P0=0,maior_ganho_rel=0.0,maior_perda_rel=0.0,maior_perda_ha=0.0,
           mono_jan_cai=0,mono_Q_cai=0,muda_sem_conflito=0,tmax_js_ms=0,tmax_py_ms=0)
    for f in ('aleat','aleat_janx2','aleat_Qx2'):
        s['tmax_js_ms']=max(s['tmax_js_ms'],D[v][f]['js']['tmax_ms']); s['tmax_py_ms']=max(s['tmax_py_ms'],D[v][f]['py']['tmax_ms'])
    rj=D[v]['aleat']['js']['res']; rp=D[v]['aleat']['py']['res']; r0=D['P0']['aleat']['py']['res']
    for i in range(N):
        k=str(i); j,p=rj[k],rp[k]
        if not viavel(E[i],j['h'],tol=1e-7)[0]: s['inviavel_js']+=1; ex.setdefault(v+'_inviavel_js',i)
        if not viavel(E[i],[F(x) for x in p['h']])[0]: s['inviavel_py']+=1; ex.setdefault(v+'_inviavel_py',i)
        par=all(near(a,b) for a,b in zip(j['q']+[j['alocado'],j['saldo']],p['q']+[p['alocado'],p['saldo']])) and j['conflito']==p['conflito'] and j['motivos']==p['motivos']
        if not par: s['paridade_falha']+=1; ex.setdefault(v+'_paridade',i)
        a,a0=F(p['alocado']),F(r0[k]['alocado'])
        if a>a0: 
            s['mais_que_P0']+=1; g=float((a-a0)/a) if a else 0
            if g>s['maior_ganho_rel']: s['maior_ganho_rel']=g; ex[v+'_maior_ganho']=i
            if not r0[k]['conflito']: s['muda_sem_conflito']+=1
        if a<a0:
            s['menos_que_P0']+=1; g=float((a0-a)/a0)
            if g>s['maior_perda_rel']: s['maior_perda_rel']=g; s['maior_perda_ha']=float(a0-a); ex[v+'_maior_perda']=i
            if not r0[k]['conflito']: s['muda_sem_conflito']+=1
        for f,key in (('aleat_janx2','mono_jan_cai'),('aleat_Qx2','mono_Q_cai')):
            b=F(D[v][f]['py']['res'][k]['alocado'])
            if b<a: s[key]+=1; ex.setdefault(v+'_'+key,i)
    out[v]=s
out['exemplos_idx']=ex
print(json.dumps(out,indent=1,ensure_ascii=False))
