# -*- coding: utf-8 -*-
"""Verificador · mede o selo 'Chega depois da falta' da etapa 4 da Compra contra a célula, a linha e o contêiner que rola (1440 e 1280 px)."""
import time, json
from verif_cmpest_lib import V
v=V('CMP.dc.html'); J=v.J
M="""(()=>{const out=[]; [...document.querySelectorAll('span')].filter(s=>/^Chega depois da falta/.test(s.innerText.trim())&&s.offsetParent).slice(0,3).forEach(s=>{
  const chip=s.closest('span[style*="border-radius"]')||s; const cr=chip.getBoundingClientRect(); const cell=chip.closest('[role=cell]'); const ce=cell.getBoundingClientRect();
  let sc=cell.parentElement; while(sc&&!(getComputedStyle(sc).overflowX!=='visible'&&sc.clientWidth<sc.scrollWidth+1&&getComputedStyle(sc).overflowX!=='visible')) sc=sc.parentElement;
  let clip=cell; const chain=[]; while(clip&&clip!==document.body){ const cs=getComputedStyle(clip); if(cs.overflowX!=='visible') chain.push({tag:clip.tagName,cls:clip.className.slice?clip.className.slice(0,30):'',ox:cs.overflowX,right:Math.round(clip.getBoundingClientRect().right),sw:clip.scrollWidth,cw:clip.clientWidth}); clip=clip.parentElement; }
  out.push({chipRight:Math.round(cr.right),chipW:Math.round(cr.width),chipSW:chip.scrollWidth,chipCW:chip.clientWidth,cellRight:Math.round(ce.right),cellW:Math.round(ce.width),cellSW:cell.scrollWidth,cellCW:cell.clientWidth,chain}); }); return out;})()"""
try:
    for w in (1440,1280):
        v.c.size(w,1000); v.open(); v.clk('Abrir compra'); v.clk('3 Solicite cotações'); v.clk('Enviar convites (simulado)'); time.sleep(7)
        v.clk('Comparar propostas'); v.clk('Expandir tudo')
        r=J(M); print(w, json.dumps(r,ensure_ascii=False,indent=0)[:1500])
        clipped=[x for x in r if x['chipRight']>min([c['right'] for c in x['chain']]+[x['cellRight']])+0.5 or x['chipSW']>x['chipCW']+1]
        v.chk(f'{w}px: selo "Chega depois da falta" inteiro', not clipped, clipped[:1])
finally:
    v.close()
