# Conferência independente das contas da ESPECIFICACAO.md v2 (Decimal e inteiro escalado 10^6, como o BigInt do JS); feita na conferência da v2 (DECISOES.md §11)
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_CEILING, getcontext
import datetime, re
getcontext().prec = 50
E6 = 10**6
def q(x, n=6): return x.quantize(D(1).scaleb(-n), rounding=ROUND_HALF_UP)
def big_div_half_up(num, den):  # inteiros, meio para cima (num, den > 0)
    qq, r = divmod(num, den)
    return qq + (1 if 2*r >= den else 0)
def big(x): return int(D(x)*E6)
falhas = []
def ok(nome, got, exp):
    norm=lambda v: [D(str(x)) for x in v] if isinstance(v,list) else (v if isinstance(v,(bool,str)) and not re.match(r'^-?[0-9.]+$',str(v)) else D(str(v)))
    if norm(got) != norm(exp):
        falhas.append(f'{nome}: obtido {got} esperado {exp}')

# --- água e massa estimada: forma única e paridade com inteiro escalado
def est(m, ui, uf): return q(D(m)*(100-D(ui))/(100-D(uf)))
def est_big(m, ui, uf):  # m em micro-kg; umidades em décimos de p.p. inteiros
    ui10, uf10 = int(D(ui)*10), int(D(uf)*10)
    return big_div_half_up(big(m)*(1000-ui10), (1000-uf10))
def agua(m, ui, uf): return D(m) - est(m, ui, uf)
for m, ui, uf in [('1000','20','10'), ('12.345676','30','20'), ('47750','17.2','14'), ('40900','17.2','14'), ('4120','55','12'), ('48000','17.2','14')]:
    ok(f'paridade big {m}', D(est_big(m, ui, uf))/E6, est(m, ui, uf))
    ok(f'est+agua=m {m}', est(m, ui, uf)+agua(m, ui, uf), D(m))
ok('K51 est', est(1000,20,10), D('888.888889')); ok('K51 agua', agua(1000,20,10), D('111.111111'))
ok('K51 q4', q(est(1000,20,10),4), D('888.8889')); ok('K51 q4 agua', q(agua(1000,20,10),4), D('111.1111'))
ok('K52 est', est('12.345676',30,20), D('10.802467')); ok('K52 agua', agua('12.345676',30,20), D('1.543209'))
ok('K52 direta', q(D('12.345676')*10/80), D('1.543210'))
ok('K53', q(D('0.0000005')), D('0.000001')); ok('K53b', q(q(D('0.0004995')),3), D('0.001')); ok('K53c', q(D('0.0004995'),3), D('0.000'))

# --- matéria seca com várias saídas
def ms(ents, sais):
    msp = sum(D(m)*(1-D(u)/100) for m,u in ents); mss = sum(D(m)*(1-D(u)/100) for m,u in sais); sm = sum(D(m) for m,_ in sais)
    e = q(msp*sm/mss); return e, sum(D(m) for m,_ in ents)-e, e-sm, msp-mss
e,a,d,_ = ms([(40900,'17.2')],[(39100,14)]); ok('K54 est',e,'39378.139535'); ok('K54 agua',a,'1521.860465'); ok('K54 dif',d,'278.139535')
e,a,d,_ = ms([(48000,'17.2')],[(39100,14),(6830,14)]); ok('K56 est',e,'46213.953488'); ok('K56 agua',a,'1786.046512'); ok('K56 dif',d,'283.953488'); ok('K56 %',q(d/48000*100,2),'0.59')
e,a,d,_ = ms([(47750,'17.2')],[(39100,14),(6830,14)]); ok('K57 est',e,'45973.255814'); ok('K57 agua',a,'1776.744186'); ok('K57 dif',d,'43.255814'); ok('K57 %',q(d/48000*100,2),'0.09')
ok('K57 recup', q(D(45930)/(D(48000)-a)*100,2), '99.37'); ok('K57 imp%', q(D(250)/48000*100,2), '0.52')
ok('K57 fechamento', q(D(45930)/(48000-a)*100,2)+q(D(250)/(48000-a)*100,2)+q(d/(48000-a)*100,2), '100.00')
e,a,d,_ = ms([(47900,'17.2')],[(39100,14),(6830,14)]); ok('K59 dif',d,'187.674419'); ok('K59 %',q(d/48000*100,2),'0.39')
e,a,d,dms = ms([(48000,'17.2')],[(39100,14),(6830,13)]); ok('K60 est',e,'46134.181828'); ok('K60 agua',a,'1865.818172'); ok('K60 dif',d,'204.181828'); ok('K60 MS',dms,'175.9')
e2,_,_,_ = ms([(48000,'17.2')],[(6830,13),(39100,14)]); ok('K60 ordem',e2,e)
uf = (D(39100)*14+D(6830)*13)/D(45930); ok('K60 uf q2', q(D(48000)*(100-D('17.2'))/(100-q(uf,2))), '46133.488102')
e,a,d,_ = ms([(47750,'17.2')],[(45930,'13.9')]); ok('K61 dif',d,'-10.139373'); ok('K61 %',q(d/48000*100,2),'-0.02')
e,a,d,_ = ms([(47750,'17.2')],[(45930,'13.4')]); ok('K62 dif',d,'-275.265589'); ok('K62 %',q(d/48000*100,2),'-0.57')
e,a,d,_ = ms([(47750,'17.7')],[(45930,14)]); ok('K63 dif',d,'-234.360465'); ok('K63 %',q(d/48000*100,2),'-0.49')
ok('K64 dif', est(1000,20,10)-889, '-0.111111')
def faixa(proc, base, ui, ufs, du=D('0.1'), tol=D('0.001')):
    return q(tol*D(proc) + du*D(base)/(100-D(ufs)) + du*D(base)*(100-D(ui))/(100-D(ufs))**2)
ok('K56 faixa', faixa(48000,48000,'17.2',14), '157.551109'); ok('K57 faixa', faixa(48000,47750,'17.2',14), '156.980530')
ok('K59 faixa', faixa(48000,47900,'17.2',14), '157.322877'); ok('K61 faixa', faixa(48000,47750,'17.2','13.9'), '156.791940')
ok('K62 faixa', faixa(48000,47750,'17.2','13.4'), '155.857661'); ok('K63 faixa', faixa(48000,47750,'17.7',14), '156.657720')
ok('K64 faixa', faixa(1000,1000,20,10), '3.098765')
# mistura
cg=[(9860,'15.9'),(8500,'18.6'),(10980,'16.4'),(8820,'18.3'),(9840,'17.2')]
ok('L38-120 soma', sum(m for m,_ in cg), 48000); ok('K50 Σmu', sum(D(m)*D(u) for m,u in cg), 825600)
ok('K50 mistura', sum(D(m)*D(u) for m,u in cg)/48000, '17.2'); ok('K50 simples', sum(D(u) for _,u in cg)/5, '17.28')
# sacas
for kg, sc in [(45930,'765.5'),(221400,3690),(2305200,38420),(2072700,34545),(191400,3190),(232500,3875),(240000,4000),(30000,500)]:
    ok(f'sc {kg}', D(kg)/60, sc)
ok('K65 vazios', [q(D(k)/60,2) for k in (48000,211900,4120,2098)], [D('800.00'),D('3531.67'),D('68.67'),D('34.97')])
ok('K66', 2305200-232500, 2072700)

# --- BEN-1 packing
ent=[3010,2980,2990,3020]; E=sum(ent); ok('OB-0110 entrada',E,12000)
tA=480*D('1.2'); tB=90*D('1.2'); lA=10176-tA; lB=1908-tB
ok('K01 tara A',tA,576); ok('K01 liq A',lA,9600); ok('K01 tara B',tB,108); ok('K01 liq B',lB,1800); ok('K01 dif',E-(lA+lB+600),0)
ok('K01 recup',q((lA+lB)/E*100,2),'95.00'); ok('K01 A',q(lA/E*100,2),'80.00'); ok('K01 B',q(lB/E*100,2),'15.00'); ok('K01 desc',q(D(600)/E*100,2),'5.00')
def rateio(S, ents):
    T=sum(ents); acc=0; prev=D(0); r=[]
    for x in ents:
        acc+=x; cur=q(D(S)*acc/T); r.append(cur-prev); prev=cur
    return r
ok('K02 A', rateio(9600,ent), [D(2408),D(2384),D(2392),D(2416)])
ok('K02 B', rateio(1800,ent), [D('451.5'),D(447),D('448.5'),D(453)])
ok('K02 desc', rateio(600,ent), [D('150.5'),D(149),D('149.5'),D(151)])
cx=lambda kg: (D(kg)*D('0.95')/20).to_integral_value(ROUND_CEILING)
ok('K03',cx(12000),570); ok('K06',cx(9270),441); ok('K07',cx(6140),292); ok('K06 exato',D(9270)*D('0.95')/20,'440.325'); ok('K07 exato',D(6140)*D('0.95')/20,'291.65')
ok('K03 REQ', 600-0, 570+30); ok('K04', 270+30, 300); ok('K08 disp', 300-292, 8)
ok('K08 h', q(D(6140)/2400), '2.558333'); ok('K08 h2', q(D(6140)/2400,2), '2.56'); ok('K08 HH', q(D(6140)*6/2400), '15.35')
ok('K09', lA+lB+600+100 > E+E*D('0.001'), True); ok('K09 lim', E+E*D('0.001'), 12012)
lA2=10177-tA; ok('K10 dif', E-(lA2+lB+600), -1); ok('K10 %', q((E-(lA2+lB+600))/E*100,2), '-0.01')
ok('K11 ep1', E-(lA+600), 1800); ok('K11 cust', 30+90, 120); ok('K11 ep2', E-(lA+600+(1008-tB)), 900)
ok('K12', E-(lA+lB), 600)
for b, dif, pct in [(1868,40,'0.33'),(1808,100,'0.83')]:
    l=b-tB; ok(f'K13/14 dif {b}', E-(lA+l+600), dif); ok(f'K13/14 % {b}', q((E-(lA+l+600))/E*100,2), pct)
ok('K13 limite Igor', min(E*D('0.005'), 100), 60)
ok('K16 faixa', D(40000)*D('0.001'), 40); ok('K16 %perm', D(40000)*D('0.005'), 200); ok('K16 %', q(D(150)/40000*100,3), '0.375')
ok('K18', D(1800)/80, '22.5'); ok('K18 desvio', (D(1800)/80/20-1)*100, '12.5')
ok('K19 tara', 480*D('1.2')+8*25, 776); ok('K19 liq', 10376-(480*D('1.2')+8*25), 9600); ok('K19 sem', 10376-480*D('1.2'), 9800)
ok('K19 kgcx', q((10376-480*D('1.2'))/480), '20.416667'); ok('K19 %', q(((10376-480*D('1.2'))/480/20-1)*100,2), '2.08')
ok('K21 falta', 10000-9600, 400)
ok('K28 semana', datetime.date(2026,9,23).isocalendar()[1], 39)
ok('K05 prazo', (datetime.date(2026,9,23)+datetime.timedelta(2)).isoformat(), '2026-09-25')
# BEN-2
custo = 5*120+30*32+570*D('4.80'); ok('K40', custo, '4296.00'); ok('K40 e', q(custo/12000,4), '0.3580'); ok('K40 v', q(custo/11400,4), '0.3768')
ok('K40 h', D(12000)/2400, 5); ok('K40 HH', D(12000)*6/2400, 30); ok('K40 kgHH', D(12000)/30, 400)
ok('K42 falta', 441-300, 141); ok('K42 PC', 141*D('4.80'), '676.80')
# BEN-4
ok('K70 est', est(4120,55,12), '2106.818182'); ok('K70 agua', agua(4120,55,12), '2013.181818'); ok('K70 dif', est(4120,55,12)-2098, '8.818182')
ok('K70 %', q((est(4120,55,12)-2098)/4120*100,2), '0.21'); ok('K70 recup', q(D(2098)/(4120-agua(4120,55,12))*100,2), '99.58')
T=231400+207200; ok('OB-0104', T, 438600); ok('OB-0104 saídas', 221400+211900+3100+2200, 438600)
ok('K71', q(D(221400)/T*100,2), '50.48'); ok('K71 seca', q(D(221400)*D('0.886')/(T*D('0.88'))*100,2), '50.82')
ok('L27-013 rateio', rateio(221400,[231400,207200]), [D('116807.934337'),D('104592.065663')])
ok('K72', 221400-30000, 191400); ok('K74 %', q(D(600)/T*100,2), '0.14'); ok('K74 faixa', T*D('0.001'), '438.6'); ok('K74 perm', T*D('0.005'), 2193)
ok('PV-030 falta', 240000-232500, 7500)
print('FALHAS:', len(falhas)); print('\n'.join(falhas))
