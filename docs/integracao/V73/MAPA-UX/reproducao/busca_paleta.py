# -*- coding: utf-8 -*-
"""Busca simples da paleta de estado por significado: varia a luminosidade de cada família de tom (HSL) e escolhe o
conjunto que maximiza a menor distância CIEDE2000 nas visões normal, deutan, protan e tritan, com restrições de contraste
(texto branco ≥ 4,5:1 sobre crítico e em curso; texto escuro ≥ 7:1 sobre atenção). Executar: python3 -I -B busca_paleta.py"""
import colorsys, itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cores import de00, sim, cr
def hsl(h,s,l): r,g,b=colorsys.hls_to_rgb(h/360,l,s); return '#%02X%02X%02X'%(round(r*255),round(g*255),round(b*255))
FAM={'critico':(8,.68),'alerta':(28,.75),'atencao':(45,.78),'ok':(140,.38),'em-curso':(208,.55),'programado':(208,.55),'concluido':(150,.06)}
L={'critico':[.32,.36,.40],'alerta':[.46,.50,.54],'atencao':[.62,.66,.70],'ok':[.36,.40,.44,.48],'em-curso':[.34,.38,.42],'programado':[.72,.76,.80],'concluido':[.48,.54,.60]}
best=None
for combo in itertools.product(*[L[k] for k in FAM]):
    P={k:hsl(FAM[k][0],FAM[k][1],l) for k,l in zip(FAM,combo)}
    if cr('#FFFFFF',P['critico'])<4.5 or cr('#FFFFFF',P['em-curso'])<4.5 or cr('#15201A',P['atencao'])<7: continue
    m=min(de00(sim(P[a],v),sim(P[b],v)) for v in ('normal','deutan','protan','tritan') for a,b in itertools.combinations(P,2))
    if not best or m>best[0]: best=(m,P)
print('menor ΔE00 entre estados nas 4 visões: %.1f'%best[0]); print(best[1])
for v in ('normal','deutan','protan','tritan'):
    ds=sorted((de00(sim(best[1][a],v),sim(best[1][b],v)),a,b) for a,b in itertools.combinations(best[1],2)); print(v,'mínimo %.1f (%s × %s)'%ds[0])
for k,h in best[1].items(): print(k,h,'× fundo %.2f · branco sobre %.2f · escuro sobre %.2f'%(cr(h,'#E3EADB'),cr('#FFFFFF',h),cr('#15201A',h)))
