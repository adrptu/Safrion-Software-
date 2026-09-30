# -*- coding: utf-8 -*-
"""Verificador · capturas: Estoque etapa 2 e 5; Compra etapa 4 (2,4-D com Santa Rita), etapa 5 devolvida, etapa 6 com avisos."""
import time
from verif_cmpest_lib import V
v=V('EST.dc.html'); J=v.J
def scroll_to(t): J(f"(()=>{{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf({t!r})>=0); if(r) r.scrollIntoView({{block:'center'}});}})()"); time.sleep(.3)
def cut(): return J("""[...document.querySelectorAll('[role=row].g2r [role=cell]')].filter(c=>c.offsetParent&&c.scrollWidth>c.clientWidth+1).map(c=>c.innerText.replace(/\\s+/g,' ').slice(0,50))""")
try:
    v.open(); v.clk('2 Entregue por O.S.'); scroll_to('REQ-036'); v.shot('v_est_e2.png'); print('EST e2 cortadas:', cut())
    v.clk('5 Faça contagens'); v.shot('v_est_e5.png'); print('EST e5 cortadas:', cut())
    v.page='CMP.dc.html'; v.open(); v.clk('Abrir compra'); v.clk('3 Solicite cotações'); v.clk('Enviar convites (simulado)'); time.sleep(7)
    v.shot('v_cmp_e3.png'); print('CMP e3 cortadas:', cut())
    v.clk('Comparar propostas'); v.clk('Expandir tudo')
    J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2ed')]; const i=rows.findIndex(r=>/2,4-D 806/.test(r.innerText)); const k=rows.slice(i+1).find(r=>/Santa Rita Insumos/.test(r.innerText)); k.querySelector('[role=cell] span').click();})()"""); time.sleep(.5)
    v.shot('v_cmp_e4_form.png')
    v.setv('#'+v.fid('just'),'Agro Norte sem estoque para entrega imediata'); v.clk('Salvar','aside[role=dialog]')
    scroll_to('2,4-D 806'); v.shot('v_cmp_e4_24d.png'); print('CMP e4 cortadas:', cut())
    v.clk('Revisar aprovação'); v.clk('Enviar à Direção'); v.clk('Registrar devolução'); v.shot('v_cmp_e5_dev.png')
    v.clk('Voltar'); v.clk('Registrar aprovação da Direção'); v.clk('Acompanhar entrega')
    v.row('PC-090'); v.setv('#'+v.fid('prev'),'2026-10-20'); v.clk('Salvar','aside[role=dialog]')
    v.shot('v_cmp_e6.png'); print('CMP e6 cortadas:', cut())
finally:
    v.close()
