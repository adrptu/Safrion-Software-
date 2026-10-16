# Conferência independente dos oráculos da ENTREGA-FAZ (Decimal + calendário). Dados sintéticos S1.
import datetime as dt
from decimal import Decimal as Dc, ROUND_CEILING
D=lambda s: dt.date(2026,int(s[3:5]),int(s[:2]))
f=lambda d: d.strftime('%d/%m')
WD=['seg','ter','qua','qui','sex','sáb','dom']
HOJE=D('23/09'); VIA=D('30/09'); MIN,MAX=7-2,30; EMB=Dc('20')
def pk(q): return (q/EMB).to_integral_value(ROUND_CEILING)
def janela(uso,floor,mn=MIN,mx=MAX): return max(uso-dt.timedelta(mx),floor), uso-dt.timedelta(mn)
def needs(lst,floor,mn=None):
    out=[]
    for it,u,q in lst:
        a,b=janela(D(u),floor,(mn or {}).get(it,MIN))
        out.append(dict(it=it,uso=D(u),q=Dc(str(q)),ini=a,fim=b))
    return out
def ordem(x): return (x['fim'],x['uso'],x['it'])            # desempate determinístico
def greedy(N):
    rest=sorted(N,key=ordem); out=[]
    while rest:
        p=rest[0]['fim']; g=[x for x in rest if x['ini']<=p]; rest=[x for x in rest if x['ini']>p]
        out.append(dict(ini=max(x['ini'] for x in g),fim=p,g=g))
    return out
def linhas(g,carry):
    tot={}
    for x in g: tot[x['it']]=tot.get(x['it'],Dc(0))+x['q']
    res={}
    for it,q in tot.items():
        need=max(Dc(0),q-carry.get(it,Dc(0))); n=pk(need); res[it]=(n*EMB,n); carry[it]=carry.get(it,Dc(0))+n*EMB-q
    return res
def show(nome,ents):
    carry={}; print(nome)
    for e in ents: print('  ',f(e['ini']),'-',f(e['fim']),{k:(str(v[0]),int(v[1])) for k,v in linhas(e['g'],carry).items()})
# ---------- S1 (sem capacidade) ----------
SR=[('Oleo','25/10',120),('Oleo','12/11',90),('Glif','05/11',20)]
LG=[('Oleo','30/10',400),('Oleo','20/11',230),('Glif','25/10','293.34')]
show('S1 SR',greedy(needs(SR,VIA))); show('S1 LG',greedy(needs(LG,VIA)))
s=greedy(needs(SR,VIA)); s2=greedy(needs(SR,VIA)); print('idempotente (mesma entrada, mesma saída):',[ (e['ini'],e['fim'],[x['q'] for x in e['g']]) for e in s]==[(e['ini'],e['fim'],[x['q'] for x in e['g']]) for e in s2])
# ---------- capacidade física no tempo ----------
# Simulação diária por item no local: estoque(t) = estoque(t-1) + chegadas(t); o pico do dia (soma dos itens, mesma grandeza)
# é medido ANTES dos usos do dia (chegada antes do uso, convenção do CAL-01); depois sai o uso EFETIVO planejado (q exato, não a
# quantidade arredondada à embalagem), sem passar de zero. A sobra de embalagem fica no local e passa ao uso seguinte do mesmo item.
# O horizonte vai até o dia seguinte ao último uso: o estoque final também é conferido.
# Chegada sem data prometida: o primeiro dia possível da janela (o caso mais cheio); conflito continua ocupando assim (conservador).
UM=dt.timedelta(1)
def picos(chegs,usos,fis,d0,d1):
    """chegs: [(dia,item,q)]; usos: [(dia,item,q)]; fis: {item: q}. Devolve {dia: pico} de d0 a d1."""
    est={k:Dc(v) for k,v in fis.items()}; ini=min([d0]+[c[0] for c in chegs]+[u[0] for u in usos]); out={}; d=ini
    while d<=d1:
        for c in chegs:
            if c[0]==d: est[c[1]]=est.get(c[1],Dc(0))+c[2]
        if d>=d0: out[d]=sum(est.values(),Dc(0))
        for u in usos:
            if u[0]==d: est[u[1]]=max(Dc(0),est.get(u[1],Dc(0))-u[2])
        d+=UM
    return out
def linhas_carry(g,carry):
    tot={}
    for x in g: tot[x['it']]=tot.get(x['it'],Dc(0))+x['q']
    lin={}; c2=dict(carry)
    for it,q in tot.items():
        need=max(Dc(0),q-c2.get(it,Dc(0))); ent=pk(need)*EMB
        c2[it]=c2.get(it,Dc(0))+ent-q
        if ent>0: lin[it]=ent
    return lin,c2
def com_capacidade(N,cap,fis=None):
    fis=fis or {}; usos=[(x['uso'],x['it'],x['q']) for x in N]; fim_h=max(x['uso'] for x in N)+UM
    pend=sorted(N,key=ordem); chegs=[]; carry={}
    def maxp(extra,d0): return max(picos(chegs+extra,usos,fis,d0,fim_h).values())
    while pend:
        p=pend[0]['fim']; g=[x for x in pend if x['ini']<=p]
        while True:
            ini=max(x['ini'] for x in g); lin,c2=linhas_carry(g,carry)
            ok=maxp([(ini,k,v) for k,v in lin.items()],ini)<=cap
            if ok or len(g)==1: break
            sai=sorted(g,key=ordem)[-1]; g=[x for x in g if x is not sai]   # sai a de fim mais tardio (desempate: uso, item)
        pend=[x for x in pend if x not in g]; fim=min(x['fim'] for x in g)
        if not ok:   # uma necessidade só: primeiro dia da janela em que cabe
            d=ini; achou=None
            while d<=fim:
                if maxp([(d,k,v) for k,v in lin.items()],d)<=cap: achou=d; break
                d+=UM
            if achou is None:
                pico=maxp([(fim,k,v) for k,v in lin.items()],fim)
                print('   CONFLITO',[(k,str(v)) for k,v in lin.items()],f(ini)+'-'+f(fim),'pico',str(pico),'>',str(cap))
                chegs+=[(ini,k,v) for k,v in lin.items()]; carry=c2; continue
            ini=achou
        chegs+=[(ini,k,v) for k,v in lin.items()]; carry=c2
        print('   entrega',f(ini),'-',f(fim),[(k,str(v)) for k,v in lin.items()])
    final=picos(chegs,usos,fis,fim_h,fim_h)[fim_h]
    print('   estoque final em',f(fim_h),'=',str(final),'(<=',str(cap),':',final<=cap,')')
print('E4  LG só Óleo, cap 500, físico 0'); com_capacidade(needs(LG[:2],VIA),Dc(500))
print('E4  LG só Óleo, cap 300'); com_capacidade(needs(LG[:2],VIA),Dc(300))
print('E4  LG só Óleo, cap 500, 150 L em quarentena no local'); com_capacidade(needs(LG[:2],VIA),Dc(500),fis={'Quarentena':150})
print('E4b S1 LG (Glifosato 300 + Óleo 400), cap 500'); com_capacidade(needs(LG,VIA),Dc(500))
print('E4c contraprova do Codex: cap 20, Óleo 11 L em 20/10 e 20 L em 20/11, galão 20 L, físico 0'); com_capacidade(needs([('Oleo','20/10',11),('Oleo','20/11',20)],VIA),Dc(20))
# ---------- regra regulatória NR-31 31.7.16 (critério conjunto L + kg, sem conversão) ----------
L,kg=Dc(60),Dc(50); print('E5b armário NR-31: 60 L + 50 kg =',L+kg,'> 100 ?',L+kg>100)
# ---------- reprogramação do saldo aberto (excluir só as previsões abertas desta programação) ----------
def reprog(saldo_aberto,nec_por_uso):
    # aloca o saldo aberto (em embalagens) às necessidades por data, na ordem; o que sobra continua aberto ("acima da demanda")
    rest=saldo_aberto; out=[]
    for uso,q in nec_por_uso:
        if rest<=0: break
        a=min(rest,pk(Dc(str(q)))*EMB); out.append((uso,str(a))); rest-=a
    return out,str(rest)
print('E12 SR Óleo saldo 220 (nada recebido), usos 12/10·120 e 12/11·90:',reprog(Dc(220),[('12/10',120),('12/11',90)]))
# pedido 300, recebido 200 -> aberto 100; CAL-01 LG sem as previsões abertas do PC-101: físico 200 real, uso 25/10 293,34 -> nec 93,34
nec=Dc('293.34')-Dc(200); print('E18 Glifosato LG: aberto 100, nec 25/10 =',nec,'->',reprog(Dc(100),[('25/10',nec)]))
print('E18 plano reduz uso LG a 150 L (nec 0): ->',reprog(Dc(100),[]),'(saldo continua aberto, não some)')
print('E18 repetir sem mudança:',reprog(Dc(100),[('25/10',nec)])==reprog(Dc(100),[('25/10',nec)]))
# ---------- cancelamento parcial (E11) ----------
ped,rec,canc=Dc(300),Dc(200),Dc(100); print('E11 LG Glifosato: programado',ped-canc,'recebido',rec,'saldo',ped-canc-rec,'| pedido total',Dc(320)-canc,'saldo total',Dc(320)-canc-rec)
print('E11 falta recalculada LG 25/10 =',Dc('293.34')-rec,'(não 100)')
# ---------- calendário: dia da semana das datas citadas ----------
for s in ['30/09','06/10','07/10','13/10','20/10','21/10','25/10','15/11']: print(s,WD[D(s).weekday()],end=' · ')
print()
# ---------- E8b: dias de recebimento da fazenda (Santa Rita recebe só seg e sex; dias corridos; data civil local) ----------
def receb_ok(d,dias): return d.weekday() in dias
def janela_rec(uso,floor,dias,mn=MIN,mx=MAX):
    a,b=janela(uso,floor,mn,mx)
    while a<=b and not receb_ok(a,dias): a+=dt.timedelta(1)
    while b>=a and not receb_ok(b,dias): b-=dt.timedelta(1)
    return a,b
def greedy_rec(lst,floor,dias):
    N=[]
    for it,u,q in lst:
        a,b=janela_rec(D(u),floor,dias); N.append(dict(it=it,uso=D(u),q=Dc(str(q)),ini=a,fim=b))
    vaz=[x for x in N if x['ini']>x['fim']]; N=[x for x in N if x['ini']<=x['fim']]
    return greedy(N),vaz
SEGSEX={0,4}
ents,vaz=greedy_rec([('Oleo','12/10',120),('Oleo','12/11',90),('Glif','05/11',20)],HOJE,SEGSEX)
show('E8b SR (E12 com recebimento seg e sex, piso = hoje 23/09)',ents); print('   janelas vazias:',[(x['it'],f(x['uso'])) for x in vaz])
print('dias:',[ (s,WD[D(s).weekday()]) for s in ['23/09','25/09','28/09','03/10','05/10','09/10','16/10','30/10','06/11']])
# ---------- E8b: janela vazia pelo prazo (Nitrato de cálcio da Santa Rita; mínima 5, máxima 60; pedido 23/09 + 7 dias) ----------
a,b=janela(D('01/10'),VIA,5,60); print('E8b Nitrato SR: entregar até',f(b),'· chegada viável',f(VIA),'· janela',f(a),'-',f(b),'· vazia =',a>b)
