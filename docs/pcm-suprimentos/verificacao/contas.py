from decimal import Decimal as D
from datetime import date, timedelta
CH=D(320)
P={'KIT-MF7719':D(690),'FIL-MF4292':D(160),'OL-1540':D(28),'KIT-U3030':D(520),'OL-HID68':D(24),'GR-EP2':D(32),
   'BOM-HID-6M':D(3600),'MANG-AP-6M':D(250),'ROL-ELEV-7250':D(640),'DSC-15':D(210),'VED-MB':D(380)}
def custo(pecas,h,serv=D(0)): return sum(q*p for q,p in pecas)+D(str(h))*CH+serv
out={}
# C1 OM-0234: realizado (kit 1, 12 L, 5 h) e previsto (kit 1, 16 L, 5 h)
out['C1 realizado']=custo([(1,P['KIT-MF7719']),(12,P['OL-1540'])],5)
out['C1 se 16 L']=custo([(1,P['KIT-MF7719']),(16,P['OL-1540'])],5)
out['C1 estimativa (autEcon)']=out['C1 se 16 L']
# lotes C1
out['C1 OF26-01 fisico apos entrega']=2-1
out['C1 OF26-07 fisico apos entrega']=120-16
out['C1 custodia apos concluir']=16-12
out['C1 OF26-07 apos devolucao']=120-16+4
# C2 OM-0235
f08=(D(160)*D('1.00')).quantize(D('0.01')); f09=(D(160)*D('0.97')).quantize(D('0.01'))
out['C2 preco F08']=f08; out['C2 preco F09']=f09
out['C2 F08']=custo([(1,f08),(12,P['OL-1540'])],4)
out['C2 F09']=custo([(1,f09),(12,P['OL-1540'])],4)
out['C2 diferenca F08-F09']=f08-f09
out['C2 estimativa (catalogo)']=custo([(1,P['FIL-MF4292']),(12,P['OL-1540'])],4)
hoje=date(2026,9,23); jan=hoje+timedelta(days=1)
out['C2 precisa (janela)']=jan.isoformat()
for f,pz in (('F08',1),('F09',6)):
    ch=hoje+timedelta(days=pz); out[f'C2 {f} chega']=ch.isoformat(); out[f'C2 {f} atrasa (chega>precisa)']=ch>jan
out['C2 OF26-07 apos entrega 12 L']=120-12
# C3 OM-0230
out['C3']=custo([(1,P['KIT-U3030']),(40,P['OL-HID68']),(1,P['GR-EP2'])],9)
out['C3 OF26-04 apos devolucao']=3+2
# C4 OM-0233 sem servico
out['C4']=custo([(1,P['BOM-HID-6M']),(2,P['MANG-AP-6M'])],D('6.5'))
# C8 OM-0221
pecas221=2*P['ROL-ELEV-7250']; out['C8 pecas']=pecas221; out['C8 servico (3800-pecas)']=D(3800)-pecas221
# C11 balcao
out['C11']=custo([(1,D(175)),(12,P['OL-1540'])],4)
# OM sintética acima da alçada
out['OM sintetica 15 bombas + 4 h']=custo([(15,P['BOM-HID-6M'])],4)
# I1 no teste unitário (SC 23/09, NF 24/09)
out['I1 U (dias)']=(date(2026,9,24)-date(2026,9,23)).days
# OTIF exemplo: prometido 24/09, reprogramado 28/09, recebido 27/09
out['OTIF atraso vs prevs[0] (dias)']=(date(2026,9,27)-date(2026,9,24)).days
# Diesel Bloco 6
out['Diesel 38% de 15000']=D(15000)*D('0.38'); out['Diesel apos 180 L']=D(15000)*D('0.38')-180
# lotes AC-03
lotes={'OF26-01':2,'OF26-03':3,'OF26-04':3,'OF26-05':1,'OF26-06':1,'OF26-07':120,'OF26-08':200,'OF26-09':18,'OF26-10':1,'OF26-11':24,'OF26-12':0,'OF26-13':0,'OF26-14':0}
out['AC-03 lotes']=len(lotes); out['AC-03 com saldo']=sum(1 for v in lotes.values() if v>0)
# reqs depois de restaurar
out['REQs apos restaurar']=11+3
for k,v in out.items(): print(f'{k}: {v}')
