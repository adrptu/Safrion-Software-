# -*- coding: utf-8 -*-
"""Pares reais de contraste da paleta proposta (avaliacao-claude.md §5, 6c03d7e), no uso do mapa.

Responde ao ponto 4 do retorno do Codex (PR #47, comentário 6227708290). Só leitura.
Uso: python3 -I -B contraste_pares.py <render>   (render de 05947ad; lê lagoa_rgb_20260925.png)

Mede, pela fórmula da WCAG 2.2 (1.4.3 texto 4,5:1; 1.4.11 não-texto 3:1):
  A. texto do rótulo (#15201A e branco) sobre o token opaco e sobre o preenchimento real da Santa Rita
     (opacidade 0,88 sobre o fundo #E3EADB, areas/inicio.py:1140);
  B. o mesmo texto sobre uma placa branca sólida a 90 % atrás do rótulo (correção verificável);
  C. contorno de seleção #15201A (inicio.py:1141, :630) e anel de foco do DS #1E7A4C (engine.py) contra o preenchimento;
  D. Lagoa Grande: texto branco (inicio.py:565) sobre o preenchimento a 0,55 (inicio.py:645) por cima da imagem RGB,
     no envelope P5/P50/P95 de luminância da imagem inteira (não só sob os pivôs);
  E. candidatos para o token "concluído" que passem 4,5:1 e mantenham a separação ΔE00 nas quatro visões.
Funções de cor copiadas de reproducao/cores.py (6c03d7e), sem mudança.
"""
import math, sys, os, zlib, struct, colorsys

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

def mix(fg,bg,a):  # composição alfa em sRGB, como o navegador faz em fill-opacity
    f=hx(fg); b=hx(bg); return '#'+''.join(f'{round((a*f[i]+(1-a)*b[i])*255):02X}' for i in range(3))
def rgbhex(t): return '#%02X%02X%02X'%t

FUNDO='#E3EADB'; TEXTO='#15201A'; BRANCO='#FFFFFF'; FOCO='#1E7A4C'; SEL='#15201A'
PROP={'impede':'#89291A','urgente':'#CD6F1D','atencao':'#EAC453','em-dia':'#4CA96B',
      'em-curso':'#275A86','programado':'#A0C4E3','concluido':'#73827A','neutro':'#C9CFCB','nao-se-aplica':'#E4E9DF'}
ok=lambda v,lim: 'ok' if v>=lim else 'FALHA'

print('A. Texto do rótulo sobre o preenchimento (WCAG 1.4.3: 4,5:1)')
print(f"{'token':14} {'hex':8} | {'escuro opaco':>12} {'branco opaco':>12} | {'SR 0,88 hex':>11} {'escuro SR':>9} {'branco SR':>9}")
falhas=[]
for k,h in PROP.items():
    sr=mix(h,FUNDO,0.88)
    e1,b1,e2,b2=cr(TEXTO,h),cr(BRANCO,h),cr(TEXTO,sr),cr(BRANCO,sr)
    melhor=max(e2,b2)
    print(f"{k:14} {h:8} | {e1:6.2f} {ok(e1,4.5):5} {b1:6.2f} {ok(b1,4.5):5} | {sr:>11} {e2:5.2f} {ok(e2,4.5):3} {b2:5.2f} {ok(b2,4.5):3}")
    if melhor<4.5: falhas.append((k,h,round(e2,2),round(b2,2)))
print('   tokens em que NENHUM dos dois textos passa 4,5:1 no uso da Santa Rita:', falhas or 'nenhum')

print('\nB. Correção verificável: placa branca sólida a 90 % atrás do rótulo (texto #15201A)')
pior=None
for k,h in PROP.items():
    placa=mix(BRANCO,mix(h,FUNDO,0.88),0.90); c=cr(TEXTO,placa)
    pior=c if pior is None or c<pior else pior
    print(f"   {k:14} placa {placa}  texto escuro {c:5.2f} {ok(c,4.5)}")
print(f"   pior caso com a placa: {pior:.2f}:1")
print('   Nota: o número do talhão já tem halo sólido (stroke 6 un, paint-order stroke, inicio.py:1426); o sub e o rótulo da camada')
print('   usam text-shadow difuso (inicio.py:1403-1406), que não dá superfície mensurável: por isso a placa.')

print('\nC. Não-texto (WCAG 1.4.11: 3:1) contra o preenchimento da Santa Rita (0,88 sobre o fundo)')
print(f"{'token':14} | {'seleção #15201A':>16} | {'foco #1E7A4C':>13} | {'contorno branco':>15}")
for k,h in PROP.items():
    sr=mix(h,FUNDO,0.88); s,f,w=cr(SEL,sr),cr(FOCO,sr),cr(BRANCO,sr)
    print(f"{k:14} | {s:8.2f} {ok(s,3):5}  | {f:6.2f} {ok(f,3):5} | {w:7.2f} {ok(w,3):5}")
print(f"   foco #1E7A4C × fundo {cr(FOCO,FUNDO):.2f}; seleção × fundo {cr(SEL,FUNDO):.2f}; foco × seleção {cr(FOCO,SEL):.2f}")
print('   Leitura: um anel só de #1E7A4C não chega a 3:1 sobre os preenchimentos escuros; o anel do foco precisa de duas')
print('   cores (ex.: #1E7A4C por dentro e branco por fora) ou de espessura/forma distinta da seleção.')

def png_rgb(path):
    d=open(path,'rb').read(); assert d[:8]==b'\x89PNG\r\n\x1a\n'; i=8; idat=b''; w=h=None
    while i<len(d):
        n=struct.unpack('>I',d[i:i+4])[0]; t=d[i+4:i+8]; c=d[i+8:i+8+n]; i+=12+n
        if t==b'IHDR': w,h,bd,ct,_,_,il=struct.unpack('>IIBBBBB',c); assert (bd,ct,il)==(8,2,0)
        elif t==b'IDAT': idat+=c
        elif t==b'IEND': break
    raw=zlib.decompress(idat); bpp=3; st=w*bpp; prev=bytearray(st); out=[]; p=0
    for _ in range(h):
        f=raw[p]; p+=1; cur=bytearray(raw[p:p+st]); p+=st
        for x in range(st):
            a=cur[x-bpp] if x>=bpp else 0; b=prev[x]; c=prev[x-bpp] if x>=bpp else 0
            if f==1: cur[x]=(cur[x]+a)&255
            elif f==2: cur[x]=(cur[x]+b)&255
            elif f==3: cur[x]=(cur[x]+((a+b)>>1))&255
            elif f==4:
                pa=abs(b-c); pb=abs(a-c); pc=abs(a+b-2*c)
                pr=a if (pa<=pb and pa<=pc) else (b if pb<=pc else c); cur[x]=(cur[x]+pr)&255
        out.append(bytes(cur)); prev=cur
    return w,h,out

print('\nD. Lagoa Grande: texto branco com sombra (inicio.py:565) sobre preenchimento a 0,55 por cima da imagem RGB')
R=sys.argv[1]; png=os.path.join(R,'lagoa_rgb_20260925.png')
w,h,rows=png_rgb(png)
amostra=[]
for y in range(0,h,4):
    r=rows[y]
    for x in range(0,w,4):
        t=(r[3*x],r[3*x+1],r[3*x+2]); amostra.append((L(rgbhex(t)),t))
amostra.sort()
env={q:amostra[int(q/100*(len(amostra)-1))][1] for q in (5,50,95)}
print(f"   imagem {os.path.basename(png)} {w}x{h}, {len(amostra)} pixels amostrados (passo 4); envelope de luminância:",
      ', '.join(f'P{q}={rgbhex(t)}' for q,t in env.items()))
print(f"{'token':14} | " + ' | '.join(f'branco P{q:<2} escuro P{q:<2}' for q in env))
for k,hh in PROP.items():
    cols=[]
    for q,t in env.items():
        comp=mix(hh,rgbhex(t),0.55); cols.append(f'{cr(BRANCO,comp):5.2f} {ok(cr(BRANCO,comp),4.5):5} {cr(TEXTO,comp):5.2f} {ok(cr(TEXTO,comp),4.5):5}')
    print(f"{k:14} | " + ' | '.join(cols))
print('   Leitura: com 0,55 sobre a imagem, nenhuma cor de texto passa em todos os tokens; o rótulo da Lagoa Grande precisa')
print('   da mesma placa sólida (B) ou de halo sólido medido, não de sombra difusa.')

print('\nE. Candidatos para "concluído" (matiz 150, saturação 0,06, como busca_paleta.py)')
outros={k:v for k,v in PROP.items() if k not in ('concluido','neutro','nao-se-aplica')}
for l in [x/100 for x in range(34,66,2)]:
    r,g,b=colorsys.hls_to_rgb(150/360,l,0.06); c='#%02X%02X%02X'%(round(r*255),round(g*255),round(b*255))
    sr=mix(c,FUNDO,0.88); e,bb=cr(TEXTO,sr),cr(BRANCO,sr)
    dmin={v:min(de00(sim(c,v),sim(o,v)) for o in outros.values()) for v in ('normal','deutan','protan','tritan')}
    texto='escuro' if e>=4.5 else ('branco' if bb>=4.5 else '—')
    eo,bo=cr(TEXTO,c),cr(BRANCO,c)
    print(f"   {c} L={l:.2f} | opaco escuro {eo:4.2f} branco {bo:4.2f} | SR escuro {e:5.2f} branco {bb:5.2f} → {texto:6} | ΔE00 mín: " + ' '.join(f'{v} {d:4.1f}' for v,d in dmin.items()))
print('   Leitura: o candidato serve se o texto passa 4,5:1 opaco e no uso (coluna →) e o ΔE00 mínimo fica ≥ 10 nas quatro visões.')
print('   PNG: 820 linhas, todas com filtro 0; bytes descomprimidos = 820 × (1 + 1080 × 3).')

print('\nF. Anel em duas cores (WCAG 1.4.11): passa se pelo menos uma das duas cores tem 3:1 contra o preenchimento real (SR 0,88)')
pares={'seleção #15201A + branco':(SEL,BRANCO),'foco #1E7A4C + branco':(FOCO,BRANCO),'foco #15201A + branco (tracejado)':(TEXTO,BRANCO)}
for nome,(c1,c2) in pares.items():
    ruins=[k for k,h in PROP.items() if max(cr(c1,mix(h,FUNDO,0.88)),cr(c2,mix(h,FUNDO,0.88)))<3]
    print(f"   {nome:36} tokens sem 3:1 em nenhuma das cores: {ruins or 'nenhum'}")
print('   Leitura: o par escuro + branco cobre os 9 tokens; o verde do DS + branco falha no "em dia". Foco e seleção ficam')
print('   distintos pela forma (seleção contínua; foco tracejado e afastado), não pela cor.')
