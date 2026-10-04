# VERIFICADOR INDEPENDENTE (não usa nada de safra.js/dados2.py): recebe a entrada (Q, configurações, grupos) e a saída (q por configuração)
# e confere se o plano é executável no modelo físico:
#  V0 Σq + saldo = Q, q ≥ 0 · V1 h = q/rend ≤ janela própria; janela 0 ou sem recurso suficiente → q = 0
#  V2 cortes por prazo (D-01): para cada recurso (cada ativo; todas as de sequência declarada; cada grupo de 1 unidade) e cada prazo finito t,
#     Σ h das que usam o recurso com janela ≤ t ≤ t; grupo de 2+ unidades: Σ rec·h ≤ un·t (condição necessária)
#  V3 cronograma exato por PL (θ* = maior fator tal que θ·h cabe; executável ⇔ θ* ≥ 1): segmentos entre prazos finitos; quem não tem janela vai
#     depois do último prazo e não entra. V3e: enumera os conjuntos que podem trabalhar juntos (sem ativo em comum, no máximo uma de sequência
#     declarada, Σ rec ≤ un em cada grupo), exato, até 16 configurações ativas. V3b: só ativos, cada configuração com até 2 ativos
#     compartilhados 2-coloríveis (linhas de bipartido): por segmento, carga de cada ativo ≤ duração (Kőnig/Birkhoff), exato.
import json,sys,math
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import linprog
TOL=1e-7
def num(x):
    if x is None or x=='' : return None
    if isinstance(x,bool): return None
    try: v=float(str(x).strip().replace(',','.')) if not isinstance(x,(int,float,Fr)) else x
    except ValueError: return float('nan')
    return v
def prep(caso):
    cf=caso['cfgs']; pools=caso.get('pools') or {}; P={}
    for k,pv in pools.items():
        u=num((pv or {}).get('un'))
        if u is not None and not (isinstance(u,float) and math.isnan(u)) and u>=0: P[k]=u
    it=[]
    for c in cf:
        r=num(c.get('rend')); r=r if (r is not None and not (isinstance(r,float) and math.isnan(r)) and r>0) else None
        H=num(c.get('jan')); H=math.inf if (H is None or (isinstance(H,float) and math.isnan(H)) or H<0) else H
        at=[]; [at.append(a) for a in (c.get('ativos') or []) if a and a not in at]
        rec={k:(num((c.get('rec') or {}).get(k)) or 0) for k in P}
        semrec=any(rec[k]>0 and rec[k]>P[k]+1e-9 for k in P)
        it.append(dict(r=r,H=H,seq=bool(c.get('seq')),at=at,rec=rec,semrec=semrec))
    return it,P
def grupos(it,P):
    G=[]
    for z in sorted({a for x in it for a in x['at']},key=str): G.append(('at:'+str(z),[i for i,x in enumerate(it) if z in x['at']],None))
    G.append(('seq',[i for i,x in enumerate(it) if x['seq']],None))
    for k,u in P.items():
        us=[i for i,x in enumerate(it) if x['rec'][k]>0]
        G.append(('pl:'+k,us,None if u<=1 else u))   # un ≤ 1: uma máquina só; senão capacidade ponderada
    return [g for g in G if len(g[1])>1]
def lp_theta(h,ativos,segs,conj_por_seg):
    # variáveis y[S,k]; max θ: Σ_{k,S∋i} y ≥ θ h_i (só quem tem prazo finito e h>0) ; Σ_S y[S,k] ≤ L_k
    var=[(k,S) for k in range(len(segs)) for S in conj_por_seg[k]]
    nv=len(var)+1
    if not ativos: return math.inf
    A=[];b=[]
    for i in ativos:
        row=np.zeros(nv); row[-1]=h[i]
        for j,(k,S) in enumerate(var):
            if i in S: row[j]=-1
        A.append(row); b.append(0)
    for k,(t0,t1) in enumerate(segs):
        row=np.zeros(nv)
        for j,(kk,S) in enumerate(var):
            if kk==k: row[j]=1
        A.append(row); b.append(t1-t0)
    c=np.zeros(nv); c[-1]=-1
    res=linprog(c,A_ub=np.array(A),b_ub=np.array(b),bounds=[(0,None)]*len(var)+[(0,1e6)],method='highs')
    assert res.status==0,res.message
    return -res.fun
def segmentos(Hs,ativos):
    ts=sorted({Hs[i] for i in ativos}); segs=[]; a=0
    for t in ts: segs.append((a,t)); a=t
    return segs
def v3e(it,P,h,ativos):
    n=len(ativos)
    def ok(S):
        if sum(1 for i in S if it[i]['seq'])>1: return False
        for k,u in P.items():
            if sum(it[i]['rec'][k] for i in S)>u+1e-9: return False
        ats=[a for i in S for a in it[i]['at']]
        return len(ats)==len(set(ats))
    feas=[]
    def dfs(j,S):
        if j==n: feas.append(tuple(S)); return
        dfs(j+1,S)
        S2=S+[ativos[j]]
        if ok(S2): dfs(j+1,S2)
    dfs(0,[])
    Hs=[x['H'] for x in it]; segs=segmentos(Hs,ativos); cps=[]
    for (t0,t1) in segs:
        dis=set(i for i in ativos if Hs[i]>=t1); proj={tuple(sorted(set(S)&dis)) for S in feas}; proj.discard(())
        mx=[S for S in proj if not any(set(S)<set(T) for T in proj)]   # maximais
        cps.append([frozenset(S) for S in mx])
    return lp_theta(h,ativos,segs,cps)
def linha_bip(it,ativos):
    cnt={}
    for i in ativos:
        for a in it[i]['at']: cnt[a]=cnt.get(a,0)+1
    adj={}
    for i in ativos:
        s=[a for a in it[i]['at'] if cnt[a]>1]
        if len(s)>2: return False
        if len(s)==2: adj.setdefault(s[0],[]).append(s[1]); adj.setdefault(s[1],[]).append(s[0])
    cor={}
    for z0 in adj:
        if z0 in cor: continue
        cor[z0]=0; pl=[z0]
        while pl:
            z=pl.pop()
            for w in adj[z]:
                if w not in cor: cor[w]=1-cor[z]; pl.append(w)
                elif cor[w]==cor[z]: return False
    return True
def v3b(it,h,ativos):
    Hs=[x['H'] for x in it]; segs=segmentos(Hs,ativos)
    var=[(i,k) for i in ativos for k,(t0,t1) in enumerate(segs) if Hs[i]>=t1]; nv=len(var)+1; A=[];b=[]
    for i in ativos:
        row=np.zeros(nv); row[-1]=h[i]
        for j,(ii,k) in enumerate(var):
            if ii==i: row[j]=-1
        A.append(row); b.append(0)
    ats=sorted({a for i in ativos for a in it[i]['at']},key=str)
    for z in ats:
        for k,(t0,t1) in enumerate(segs):
            row=np.zeros(nv)
            for j,(i,kk) in enumerate(var):
                if kk==k and z in it[i]['at']: row[j]=1
            A.append(row); b.append(t1-t0)
    c=np.zeros(nv); c[-1]=-1
    res=linprog(c,A_ub=np.array(A),b_ub=np.array(b),bounds=[(0,None)]*len(var)+[(0,1e6)],method='highs'); assert res.status==0,res.message
    return -res.fun
def verifica(caso,saida,v3=True,max_enum=16):
    it,P=prep(caso); Q=float(caso['Q']); v=[]
    qx=saida.get('q_exato'); q=[Fr(z) for z in qx] if qx else [Fr(z) if z is not None else Fr(0) for z in saida['q']]
    exato=bool(qx); tol=Fr(0) if exato else Fr(TOL)
    h=[]
    for i,x in enumerate(it):
        if q[i]<-tol: v.append(f'V0 q[{i}]<0')
        if x['r'] is None:
            if q[i]>tol: v.append(f'V1 q[{i}] sem rendimento')
            h.append(Fr(0)); continue
        h.append(q[i]/Fr(x['r']))
    s=sum(q)+Fr(saida['saldo']); 
    if abs(float(s)-Q)>1e-6*max(1,Q): v.append(f'V0 Σq+saldo={float(s)} ≠ Q={Q}')
    for i,x in enumerate(it):
        if x['H']!=math.inf and h[i]>Fr(x['H'])+tol: v.append(f'V1 h[{i}]={float(h[i]):.6g} > janela {x["H"]}')
        if x['semrec'] and q[i]>tol: v.append(f'V1 q[{i}]>0 sem recurso suficiente')
    for nome,us,cap in grupos(it,P):
        for t in sorted({it[i]['H'] for i in us if it[i]['H']!=math.inf}):
            st=[i for i in us if it[i]['H']<=t]
            if cap is None:
                if len(st)<2: continue
                lhs=sum(h[i] for i in st); rhs=Fr(t)
            else:
                k=nome[3:]; lhs=sum(h[i]*Fr(it[i]['rec'][k]) for i in st); rhs=Fr(cap)*Fr(t)
            if lhs>rhs+tol*max(1,rhs): v.append(f'V2 {nome}@{t}: {float(lhs):.6g} > {float(rhs):.6g}')
    th=None; motor=None
    if v3:
        hf=[float(z) for z in h]; ativos=[i for i,x in enumerate(it) if x['H']!=math.inf and hf[i]>TOL]
        so_ativos=not any(it[i]['seq'] for i in ativos) or sum(1 for i in ativos if it[i]['seq'])<2
        so_ativos=so_ativos and all(sum(1 for i in ativos if it[i]['rec'][k]>0)<2 for k in P)
        if ativos and so_ativos and linha_bip(it,ativos): th=v3b(it,hf,ativos); motor='V3b'
        elif ativos and len(ativos)<=max_enum: th=v3e(it,P,hf,ativos); motor='V3e'
        elif not ativos: th=math.inf; motor='nada com prazo'
        else: motor='não aplicável (>%d sem estrutura de bipartido)'%max_enum
        if th is not None and th<1-1e-7: v.append(f'V3 cronograma inexistente: θ*={th:.9f} ({motor})')
    return v,th,motor
if __name__=='__main__':
    casos=json.load(open(sys.argv[1])); saidas=[json.loads(l) for l in open(sys.argv[2]) if l.strip() and not l.startswith('#')]
    assert len(casos)==len(saidas)
    for c,s in zip(casos,saidas):
        assert c['nome']==s['nome']
        v,th,m=verifica(c,s)
        print(json.dumps(dict(nome=c['nome'],violacoes=v,theta=(None if th is None else (th if th!=math.inf else 'inf')),motor=m),ensure_ascii=False))
