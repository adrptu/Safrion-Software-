# Contas da especificação BEN v2 em Decimal (PRD 10.0: kg 6 casas, ROUND_HALF_UP; coeficiente 12 casas)
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_CEILING, getcontext
import datetime
getcontext().prec = 34
Q6 = D('0.000001'); Q12 = D('0.000000000001')
def q6(x): return x.quantize(Q6, rounding=ROUND_HALF_UP)
def q3(x): return x.quantize(D('0.001'), rounding=ROUND_HALF_UP)
def q4(x): return x.quantize(D('0.0001'), rounding=ROUND_HALF_UP)
def q2(x): return x.quantize(D('0.01'), rounding=ROUND_HALF_UP)
def pct(x): return q2(x*100)
def est_ms(ents, saidas):
    # ents: [(m_proc_base, u)] base já sem impureza; saidas: [(m, u)]
    ms_proc = sum(m*(1-u/100) for m,u in ents)
    ms_sai = sum(m*(1-u/100) for m,u in saidas)
    sm = sum(m for m,_ in saidas)
    return q6(ms_proc*sm/ms_sai), ms_proc, ms_sai, sm
def benEst(m, ui, uf): return q6(m*(100-ui)/(100-uf))
def benAgua(m, ui, uf): return m - benEst(m, ui, uf)
out=[]
def p(*a): out.append(' '.join(str(x) for x in a))

p('== BEN-03'); e=benEst(D(1000),D(20),D(10)); a=benAgua(D(1000),D(20),D(10)); p('est',e,'agua',a,'soma',e+a,'q4',q4(e),q4(a),'q3',q3(e),q3(a))
p('== empate (C-01 em 6 casas)'); m=D('12.345676'); e=benEst(m,D(30),D(20)); p('exato',m*D(70)/D(80),'est',e,'agua=m-est',m-e,'direta q6',q6(m*D(10)/D(80)),'soma direta',e+q6(m*D(10)/D(80)))
p('== quantizacao dupla'); x=D('0.0004995'); p('q6',q6(x),'q3(q6)',q3(q6(x)),'q3 direto',q3(x)); p('R-F04', q6(D('0.0000005')))

p('== BEN-1 OB-0110')
ent=[D(3010),D(2980),D(2990),D(3020)]; E=sum(ent); p('entrada',E)
tA=480*D('1.2'); lA=D(10176)-tA; tB=90*D('1.2'); lB=D(1908)-tB; p('A tara',tA,'liq',lA,'B tara',tB,'liq',lB,'desc',600,'soma',lA+lB+600,'dif',E-(lA+lB+600))
p('recup',pct((lA+lB)/E),'A',pct(lA/E),'B',pct(lB/E),'descarte',pct(D(600)/E))
def rateio(S, ents):
    T=sum(ents); acc=D(0); prev=D(0); r=[]
    for x in ents:
        acc+=x; cur=q6(S*acc/T); r.append(cur-prev); prev=cur
    return r
for S,n in ((lA,'L39-120'),(lB,'L39-121'),(D(600),'descarte')):
    r=rateio(S,ent); p('rateio',n,[str(x.normalize()) for x in r],'soma',sum(r))
p('caixas sugeridas 12000',(D(12000)*D('0.95')/20).to_integral_value(ROUND_CEILING),'9270',(D(9270)*D('0.95')/20),(D(9270)*D('0.95')/20).to_integral_value(ROUND_CEILING),'6140',(D(6140)*D('0.95')/20),(D(6140)*D('0.95')/20).to_integral_value(ROUND_CEILING))
p('h-linha 6140',q6(D(6140)/2400),'exib',q2(D(6140)/2400),'HH',q6(D(6140)*6/2400),'12000 h',D(12000)/2400,'HH',D(12000)*6/2400,'kg/HH',D(12000)/(D(12000)*6/2400))
p('tolerancia pesada 0,1% de 12000',D(12000)*D('0.001'),'alcada pct 0,5%',D(12000)*D('0.005'))
for b in (D(1868),D(1808)):
    l=b-tB; d=E-(lA+l+600); p('B bruto',b,'liq',l,'dif',d,'pct',q6(d/E*100))
l=D(10177)-tA; d=E-(l+lB+600); p('A bruto 10177 liq',l,'dif',d,'pct',q6(d/E*100))
p('A +100 soma pesada', lA+lB+600+100, 'limite', E+E*D('0.001'))
p('liq por caixa B 80 un', D(1800)/80, 'desvio %', q6((D(1800)/80/20-1)*100))
p('pallet: tara', 480*D('1.2')+8*25, 'liq', D(10376)-(480*D('1.2')+8*25), 'sem pallet liq', D(10376)-480*D('1.2'), 'kg/cx', q6((D(10376)-480*D('1.2'))/480), 'desvio %', q6(((D(10376)-480*D('1.2'))/480/20-1)*100))
p('teto sintetico: entrada 40000 pct', D(40000)*D('0.005'),'banda', D(40000)*D('0.001'),'dif 150 pct', q6(D(150)/40000*100))
p('caixas: CX26-01 270 +30 =',270+30,'- 292 =',300-292, '441>300')
p('custo BEN-2', 5*120+30*32+570*D('4.80'), 'R$/kg entrada', q6((5*120+30*32+570*D('4.80'))/12000), 'R$/kg vendavel', q6((5*120+30*32+570*D('4.80'))/11400), q4((5*120+30*32+570*D('4.80'))/11400))

p('== BEN-3 grão')
cg=[(9860,'15.9'),(8500,'18.6'),(10980,'16.4'),(8820,'18.3'),(9840,'17.2')]
sm=sum(D(m) for m,_ in cg); smu=sum(D(m)*D(u) for m,u in cg); p('L38-120',sm,'u mistura',(smu/sm).quantize(Q12),'media simples',sum(D(u) for _,u in cg)/5)
u0=D('17.2')
e,msp,mss,s=est_ms([(D(40900),u0)],[(D(39100),D(14))]); p('parcial est',e,'agua',D(40900)-e,'dif',e-39100)
for imp in (D(0),D(250),D(100)):
    base=D(48000)-imp
    e,msp,mss,s=est_ms([(base,u0)],[(D(39100),D(14)),(D(6830),D(14))]); ag=base-e; dif=e-s
    p('final imp',imp,'est',e,'agua',ag,'dif',dif,'dif%',q6(dif/48000*100),'recup',q6(s/(D(48000)-ag)*100))
# contraexemplo PRD-02
e,msp,mss,s=est_ms([(D(48000),u0)],[(D(39100),D(14)),(D(6830),D(13))]); p('PRD-02 contra est',e,'agua',D(48000)-e,'dif',e-s,'MS',msp-mss,'msp',msp,'mss',mss)
e2,_,_,_=est_ms([(D(48000),u0)],[(D(6830),D(13)),(D(39100),D(14))]); p('ordem invertida igual',e2==e)
# u_f ponderada quantizada 2 casas desloca
uf=(D(39100)*14+D(6830)*13)/D(45930); p('uf*',uf,'est com uf* q2', q6(D(48000)*(100-u0)/(100-q2(uf))), 'q4', q6(D(48000)*(100-u0)/(100-q4(uf))))
# banda
def banda(proc_peso, m, ui, uf, du_ent=D('0.1'), du_sai=D('0.1'), tol=D('0.001')):
    return q6(tol*proc_peso + du_ent*m/(100-uf) + du_sai*m*(100-ui)/((100-uf)**2))
for imp in (D(0),D(250),D(100)):
    p('banda imp',imp, banda(D(48000), D(48000)-imp, u0, D(14)))
# 13,9 e 13,4
for usai in (D('13.9'),D('13.4')):
    e,_,_,s=est_ms([(D(47750),u0)],[(D(45930),usai)]); dif=e-s; p('u_sai',usai,'est',e,'dif',dif,'pct',q6(dif/48000*100),'banda',banda(D(48000),D(47750),u0,usai))
# u entrada 17,7 com pesagem certa (impureza 250)
e,_,_,s=est_ms([(D(47750),D('17.7'))],[(D(45930),D(14))]); dif=e-s; p('ui 17,7 est',e,'dif',dif,'pct',q6(dif/48000*100),'banda',banda(D(48000),D(47750),D('17.7'),D(14)))
# BEN-03 com 889 pesados
p('BEN-03 889 dif', benEst(D(1000),D(20),D(10))-889, 'banda', banda(D(1000),D(1000),D(20),D(10)))
# sacas
for kg in (45930,221400,2305200,2072700,191400,4120,7100,48000,211900,2098): p('sc',kg,q6(D(kg)/60))
p('soja disp', 2305200-232500, (2305200-232500)/60, 'reserva sc', D(232500)/60)

p('== BEN-4 café')
e=benEst(D(4120),D(55),D(12)); p('OB-0114 est',e,'agua',D(4120)-e,'dif',e-2098,'pct',q6((e-2098)/4120*100),'recup',q6(D(2098)/(D(4120)-(D(4120)-e))*100),'banda pesada',D(4120)*D('0.001'))
c=[D(231400),D(207200)]; T=sum(c); p('OB-0104 entrada',T,'saidas',221400+211900+3100+2200,'rend',q6(D(221400)/T*100), (D(221400)/T).quantize(Q12))
r=rateio(D(221400),c); p('rateio L27-013',[str(x) for x in r],sum(r))
p('rend base seca coco 12 benef 11,4', q6(D(221400)*D('0.886')/(T*D('0.88'))*100))
p('alcada CAF-BEN pct', T*D('0.005'),'tol', T*D('0.001'),'600 pct', q6(D(600)/T*100))
p('disp L27-013 apos 30000', 221400-30000, D(191400)/60, 'PV-028 kg', 500*60)
p('bloqueado cafe 98,17?', q6(D(221400)/(221400+4120)*100))
p('C-02 fechamento', q6(D(250)/(D(48000)-D('1776.744186'))*100), q6(D('43.255814')/(D(48000)-D('1776.744186'))*100))
p('== semanas ISO', datetime.date(2026,9,23).isocalendar(), datetime.date(2026,9,18).isocalendar(), datetime.date(2026,9,15).isocalendar(), datetime.date(2026,9,20).isocalendar(),datetime.date(2026,9,22).isocalendar(),datetime.date(2026,9,24).isocalendar())

p('== extras')
p('K42 falta', 441-300, 'PC', (441-300)*D('4.80'))
p('K50 soma m*u', smu, 'soma m', sm)
p('K08 HH 6140', q6(D(6140)*6/D(2400)), 'q2 h', q2(D(6140)/2400))
p('PV-030 saldo kg', 4000*60, 'falta apos RS', 4000*60-232500, (4000*60-232500)/60)
p('OB-0104 soma saidas', 221400+211900+3100+2200)
print('\n'.join(out))
