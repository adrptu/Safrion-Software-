# -*- coding: utf-8 -*-
"""Contraste WCAG 2.2, simulação de daltonismo (Machado, Oliveira e Fernandes 2009, severidade 1,0)
e distância CIEDE2000 entre cores do mapa. Executar: python3 -I cores.py > cores.txt
Paleta "antes": inicio.py:430 (LCOR_OP), :345-346 (SATPAL), fundo :1556 (#E3EADB).
Paleta "proposta": tokens por significado da avaliacao-claude.md §5 (proposta, não aprovada)."""
import math, itertools
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def unl(c): c=max(0,min(1,c)); return 12.92*c if c<=0.0031308 else 1.055*c**(1/2.4)-0.055
def L(h): r,g,b=[lin(x) for x in hx(h)]; return 0.2126*r+0.7152*g+0.0722*b
def cr(a,b): la,lb=sorted([L(a),L(b)],reverse=True); return (la+0.05)/(lb+0.05)
MAT={'deutan':[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
     'protan':[[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
     'tritan':[[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]}
def sim(h,k):
    if k=='normal': return h
    r,g,b=[lin(x) for x in hx(h)]; m=MAT[k]
    o=[unl(m[i][0]*r+m[i][1]*g+m[i][2]*b) for i in range(3)]
    return '#'+''.join(f'{round(x*255):02X}' for x in o)
def lab(h):
    r,g,b=[lin(x) for x in hx(h)]
    X=(0.4124*r+0.3576*g+0.1805*b)/0.95047; Y=(0.2126*r+0.7152*g+0.0722*b); Z=(0.0193*r+0.1192*g+0.9505*b)/1.08883
    f=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    return 116*f(Y)-16, 500*(f(X)-f(Y)), 200*(f(Y)-f(Z))
def de00(a,b):
    L1,a1,b1=lab(a); L2,a2,b2=lab(b)
    C1=math.hypot(a1,b1); C2=math.hypot(a2,b2); Cm=(C1+C2)/2
    G=0.5*(1-math.sqrt(Cm**7/(Cm**7+25**7))); a1p=(1+G)*a1; a2p=(1+G)*a2
    C1p=math.hypot(a1p,b1); C2p=math.hypot(a2p,b2)
    h1=math.degrees(math.atan2(b1,a1p))%360; h2=math.degrees(math.atan2(b2,a2p))%360
    dL=L2-L1; dC=C2p-C1p
    dh=0 if C1p*C2p==0 else (h2-h1 if abs(h2-h1)<=180 else (h2-h1-360 if h2-h1>180 else h2-h1+360))
    dH=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dh/2))
    Lm=(L1+L2)/2; Cmp=(C1p+C2p)/2
    hm=(h1+h2) if C1p*C2p==0 else ((h1+h2)/2 if abs(h1-h2)<=180 else ((h1+h2+360)/2 if h1+h2<360 else (h1+h2-360)/2))
    T=1-0.17*math.cos(math.radians(hm-30))+0.24*math.cos(math.radians(2*hm))+0.32*math.cos(math.radians(3*hm+6))-0.20*math.cos(math.radians(4*hm-63))
    Sl=1+0.015*(Lm-50)**2/math.sqrt(20+(Lm-50)**2); Sc=1+0.045*Cmp; Sh=1+0.015*Cmp*T
    Rt=-2*math.sqrt(Cmp**7/(Cmp**7+25**7))*math.sin(math.radians(60*math.exp(-((hm-275)/25)**2)))
    return math.sqrt((dL/Sl)**2+(dC/Sc)**2+(dH/Sh)**2+Rt*(dC/Sc)*(dH/Sh))
FUNDO='#E3EADB'; TEXTO='#15201A'; BRANCO='#FFFFFF'; LEG='#FDFEFC'  # legenda: branco a 0,94 sobre o fundo (inicio.py:1562)
ANTES={'ok':'#7FAE68','good':'#5F8F55','lime':'#A9C06A','yellow':'#D4B25A','orange':'#D98A4E','red':'#C8553D','gray':'#C9CFCB','blue':'#6E9FC6','navy':'#44739A','none':'#E4E9DF','purple':'#9B8BC4'}
VIGOR={'v1 falha':'#E4002B','v2 fraco':'#FF6A00','v3 atenção':'#FFD500','v4 médio':'#B5E61D','v5 bom':'#3FBF2A','v6 vigor alto':'#0B7A1E'}
# proposta (tokens por significado; tons próximos dos da 74.7.3, separados por luminosidade para resistir ao daltonismo)
PROP={'estado.critico':'#89291A','estado.alerta':'#CD6F1D','estado.atencao':'#EAC453','estado.ok':'#4CA96B',
      'estado.em-curso':'#275A86','estado.programado':'#A0C4E3','estado.concluido':'#73827A'}   # saída de busca_paleta.py
ESTADIO={'fase.vegetativo':'#438F82','fase.reprodutivo':'#9C86CF','fase.producao-continua':'#2A4E75','fase.enchimento-maturacao':'#8C6638','fase.pre-plantio':'#C9CFCB'}   # categórica, sem vermelho/laranja/amarelo
NEUTRO={'nao-se-aplica (liso)':'#E4E9DF','contorno tracejado nao-se-aplica':'#6B776F','sem-leitura base':'#C9CFCB','sem-leitura listra':'#6B6B6B'}
def tabela(nome,P):
    print(f'\n## {nome}: contraste (razão WCAG) contra fundo {FUNDO}, contra branco do contorno, do texto {TEXTO} sobre a cor e do branco sobre a cor')
    print('| classe | hex | × fundo | × contorno branco | texto escuro sobre | texto branco sobre |')
    print('|---|---|---:|---:|---:|---:|')
    for k,h in P.items(): print(f'| {k} | {h} | {cr(h,FUNDO):.2f} | {cr(h,BRANCO):.2f} | {cr(TEXTO,h):.2f} | {cr(BRANCO,h):.2f} |')
def confusao(nome,P,pares=None,lim=10):
    print(f'\n## {nome}: menor distância CIEDE2000 entre classes, por visão (abaixo de {lim} = difícil de separar em área pequena)')
    ks=list(P); pares=pares or list(itertools.combinations(ks,2))
    for v in ('normal','deutan','protan','tritan'):
        ds=sorted(((de00(sim(P[a],v),sim(P[b],v)),a,b) for a,b in pares))
        ruins=[f'{a} × {b} {d:.1f}' for d,a,b in ds if d<lim]
        print(f'- {v}: mínimo {ds[0][0]:.1f} ({ds[0][1]} × {ds[0][2]}); pares < {lim}: {len(ruins)}'+(' → '+'; '.join(ruins[:8]) if ruins else ''))
if __name__=='__main__':
    tabela('Operacional antes (inicio.py:430)',ANTES)
    confusao('Operacional antes, pares de estado usados juntos numa legenda',ANTES,
      [('red','ok'),('red','yellow'),('red','orange'),('orange','yellow'),('yellow','ok'),('ok','good'),('ok','lime'),('lime','yellow'),('blue','navy'),('gray','none'),('blue','purple'),('red','good'),('lime','good'),('blue','ok')])
    print('\nSimulação deuteranopia dos estados antes:',{k:sim(h,'deutan') for k,h in ANTES.items() if k in ('red','ok','good','yellow','orange')})
    tabela('Rampa de vigor (inicio.py:345; PRD 74.7.2)',VIGOR)
    confusao('Rampa de vigor, classes vizinhas e extremos',VIGOR,[(a,b) for a,b in itertools.combinations(VIGOR,2)],lim=12)
    tabela('Proposta por significado (não aprovada)',PROP)
    confusao('Proposta por significado',PROP,lim=15)
    tabela('Estádio, categórica proposta',ESTADIO)
    confusao('Estádio, categórica proposta',ESTADIO,lim=15)
    tabela('Neutros e ausência de leitura',NEUTRO)
    print('\nNão se aplica × fundo:',f"{cr('#E4E9DF',FUNDO):.2f}",'· cinza × não se aplica:',f"{cr('#C9CFCB','#E4E9DF'):.2f}",'· contorno tracejado proposto × fundo:',f"{cr('#6B776F',FUNDO):.2f}",'· listra proposta × base:',f"{cr('#6B6B6B','#C9CFCB'):.2f}",'· listra atual × base:',f"{cr('#9E9E9E','#C9CFCB'):.2f}")
    print('Contorno de seleção #15201A × fundo:',f"{cr('#15201A',FUNDO):.2f}",'· foco tracejado #15201A (igual à seleção, só muda o traço)')
    print('Borda branca da amostra × legenda (Lc, inicio.py:854) para none:',f"{cr('#FFFFFF',LEG):.2f}")
